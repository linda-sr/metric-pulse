import json
import os
import psycopg2
from psycopg2.extras import execute_values

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data/raw")

# Connect to target Postgres Warehouse (Port 5433 from docker-compose.yml)
WAREHOUSE_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "dbname": "saas_warehouse",
    "user": "warehouse_user",
    "password": "warehouse_password",
}

def load_raw_staging():
    print("Loading Raw Staging Data into Postgres Warehouse (raw_staging schema)...")
    
    conn = psycopg2.connect(**WAREHOUSE_CONFIG)
    cursor = conn.cursor()

    # Create target schema
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw_staging;")

    sources = {
        "raw_users": os.path.join(RAW_DATA_DIR, "pg_users.json"),
        "raw_plans": os.path.join(RAW_DATA_DIR, "pg_plans.json"),
        "raw_subscriptions": os.path.join(RAW_DATA_DIR, "pg_subscriptions.json"),
        "raw_clickstream": os.path.join(RAW_DATA_DIR, "mongo_clickstream.json"),
    }

    for table_name, json_path in sources.items():
        if not os.path.exists(json_path):
            print(f"File not found: {json_path}. Run extract_raw.py first!")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        if not records:
            print(f"Skipping empty dataset: {table_name}")
            continue

        # Extract column names dynamically from JSON keys
        columns = list(records[0].keys())
        full_table = f"raw_staging.{table_name}"

        # Drop and create staging tables storing data as text/JSONB for dbt downstream
        create_table_sql = f"DROP TABLE IF EXISTS {full_table}; CREATE TABLE {full_table} ("
        create_table_sql += ", ".join([f"{col} TEXT" for col in columns])
        create_table_sql += ");"
        cursor.execute(create_table_sql)

        # Batch insert raw records
        insert_sql = f"INSERT INTO {full_table} ({', '.join(columns)}) VALUES %s"
        values = [[str(rec.get(col)) if rec.get(col) is not None else None for col in columns] for rec in records]
        execute_values(cursor, insert_sql, values)

        # Verify row counts
        cursor.execute(f"SELECT COUNT(*) FROM {full_table};")
        count = cursor.fetchone()[0]
        print(f"Staged {count} rows into '{full_table}'")

    conn.commit()
    cursor.close()
    conn.close()
    print("Raw Staging load complete! Postgres Warehouse populated on port 5433.\n")

if __name__ == "__main__":
    load_raw_staging()