"""
load.py
Loads the raw M5 CSVs into Snowflake (M5.RAW).

Flow: file format + internal stage -> PUT local CSVs -> COPY INTO raw tables.
Each run is a full reload: tables are recreated, so it is safe to re-run.
"""

import logging
from pathlib import Path

import snowflake.connector

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ── Table definitions ──────────────────────────────────────────────────────
# raw_sales is not listed here: it has 1,947 columns (6 IDs + d_1...d_1941),
# so its columns are generated from the CSV header instead.
TABLE_COLUMNS = {
    "raw_calendar": """
        date          DATE,
        wm_yr_wk      INTEGER,
        weekday       VARCHAR,
        wday          INTEGER,
        month         INTEGER,
        year          INTEGER,
        d             VARCHAR,
        event_name_1  VARCHAR,
        event_type_1  VARCHAR,
        event_name_2  VARCHAR,
        event_type_2  VARCHAR,
        snap_ca       INTEGER,
        snap_tx       INTEGER,
        snap_wi       INTEGER
    """,
    "raw_prices": """
        store_id    VARCHAR,
        item_id     VARCHAR,
        wm_yr_wk    INTEGER,
        sell_price  NUMBER(12, 4)
    """,
}

SALES_ID_COLUMNS = {"id", "item_id", "dept_id", "cat_id", "store_id", "state_id"}


# ── Helpers ────────────────────────────────────────────────────────────────
def get_connection():
    """Connect to Snowflake using key-pair auth from config."""
    config.validate_config()
    return snowflake.connector.connect(
        account=config.SF_ACCOUNT,
        user=config.SF_USER,
        private_key_file=config.SF_PRIVATE_KEY_PATH,
        role=config.SF_ROLE,
        warehouse=config.SF_WAREHOUSE,
        database=config.SF_DATABASE,
        schema=config.SF_SCHEMA,
    )


def fetch_dicts(cursor):
    """Return query results as a list of dicts keyed by lowercase column name."""
    columns = [col[0].lower() for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def build_sales_columns(csv_path: Path) -> str:
    """Generate column definitions for the wide sales file from its header."""
    with open(csv_path, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")

    columns = [
        f"{name} {'VARCHAR' if name in SALES_ID_COLUMNS else 'INTEGER'}"
        for name in header
    ]
    day_columns = sum(1 for name in header if name.startswith("d_"))
    logger.info(f"raw_sales: {len(header)} columns ({day_columns} day columns)")
    return ",\n".join(columns)


# ── Snowflake setup ────────────────────────────────────────────────────────
def create_file_format(cursor):
    cursor.execute(f"""
        CREATE OR REPLACE FILE FORMAT {config.FILE_FORMAT_NAME}
            TYPE = CSV
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            EMPTY_FIELD_AS_NULL = TRUE
            NULL_IF = ('', 'NULL')
    """)
    logger.info(f"File format {config.FILE_FORMAT_NAME} ready")


def create_stage(cursor):
    cursor.execute(f"""
        CREATE OR REPLACE STAGE {config.STAGE_NAME}
            FILE_FORMAT = (FORMAT_NAME = '{config.FILE_FORMAT_NAME}')
    """)
    logger.info(f"Internal stage {config.STAGE_NAME} ready")


def create_table(cursor, table: str, columns: str):
    cursor.execute(f"CREATE OR REPLACE TABLE {table} ({columns})")
    logger.info(f"Table {table} created")


# ── Load steps ─────────────────────────────────────────────────────────────
def put_file(cursor, csv_path: Path) -> str:
    """Upload a local CSV to the internal stage. Returns the staged file name."""
    file_uri = csv_path.resolve().as_posix()
    logger.info(f"Uploading {csv_path.name} to @{config.STAGE_NAME}...")
    cursor.execute(
        f"PUT 'file://{file_uri}' @{config.STAGE_NAME} "
        f"AUTO_COMPRESS = TRUE OVERWRITE = TRUE PARALLEL = 4"
    )
    result = fetch_dicts(cursor)[0]
    if result["status"] != "UPLOADED":
        raise RuntimeError(f"PUT failed for {csv_path.name}: {result}")
    logger.info(f"Uploaded {result['source']} -> {result['target']}")
    return result["target"]


def copy_into(cursor, table: str, staged_file: str):
    """Bulk load a staged file into its raw table; fail on any bad row."""
    cursor.execute(f"""
        COPY INTO {table}
        FROM @{config.STAGE_NAME}
        FILES = ('{staged_file}')
        FILE_FORMAT = (FORMAT_NAME = '{config.FILE_FORMAT_NAME}')
        ON_ERROR = 'ABORT_STATEMENT'
    """)
    for result in fetch_dicts(cursor):
        if result["status"] != "LOADED":
            raise RuntimeError(f"COPY INTO {table} failed: {result}")
        logger.info(f"{table}: loaded {result['rows_loaded']:,} rows from {result['file']}")


def count_rows(cursor, table: str) -> int:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        create_file_format(cursor)
        create_stage(cursor)

        for table, filename in config.SOURCE_FILES.items():
            csv_path = config.RAW_DATA_DIR / filename
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing source file: {csv_path}")

            columns = (
                build_sales_columns(csv_path)
                if table == "raw_sales"
                else TABLE_COLUMNS[table]
            )
            create_table(cursor, table, columns)
            staged_file = put_file(cursor, csv_path)
            copy_into(cursor, table, staged_file)
            logger.info(f"{table}: {count_rows(cursor, table):,} rows in Snowflake")

        logger.info("All raw tables loaded")
    finally:
        conn.close()


if __name__ == "__main__":
    main()