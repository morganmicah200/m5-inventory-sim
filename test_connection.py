import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SF_ACCOUNT"),
    user=os.getenv("SF_USER"),
    private_key_file=os.getenv("SF_PRIVATE_KEY_PATH"),
    role=os.getenv("SF_ROLE"),
    warehouse=os.getenv("SF_WAREHOUSE"),
    database=os.getenv("SF_DATABASE"),
    schema=os.getenv("SF_SCHEMA"),
)

cur = conn.cursor()
cur.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
print(cur.fetchone())
conn.close()