"""
config.py
Central configuration for m5-inventory-sim.
All environment variables are read here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ── Snowflake ──────────────────────────────────────────────────────────────
SF_ACCOUNT          = os.getenv("SF_ACCOUNT")
SF_USER             = os.getenv("SF_USER")
SF_PRIVATE_KEY_PATH = os.getenv("SF_PRIVATE_KEY_PATH")
SF_ROLE             = os.getenv("SF_ROLE", "SYSADMIN")
SF_WAREHOUSE        = os.getenv("SF_WAREHOUSE", "M5_WH")
SF_DATABASE         = os.getenv("SF_DATABASE", "M5")
SF_SCHEMA           = os.getenv("SF_SCHEMA", "RAW")

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# ── Source files (M5 Forecasting - Accuracy) ───────────────────────────────
# Maps each raw Snowflake table to its source CSV
SOURCE_FILES = {
    "raw_calendar": "calendar.csv",
    "raw_prices":   "sell_prices.csv",
    "raw_sales":    "sales_train_evaluation.csv",
}

# ── Snowflake objects used by load.py ──────────────────────────────────────
STAGE_NAME       = "m5_raw_stage"
FILE_FORMAT_NAME = "m5_csv_format"


def validate_config():
    """Fail fast if required settings are missing."""
    required = {
        "SF_ACCOUNT": SF_ACCOUNT,
        "SF_USER": SF_USER,
        "SF_PRIVATE_KEY_PATH": SF_PRIVATE_KEY_PATH,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise EnvironmentError(f"Missing required .env values: {', '.join(missing)}")