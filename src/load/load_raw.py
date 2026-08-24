import os
import duckdb

# --- Paths & Directory Configs ---
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data/raw")
DB_PATH = os.path.join(BASE_DIR, "data/warehouse.duckdb")

def load_bronze_layer():
    print("Loading Raw Staging Data into DuckDB (Bronze Layer)")
    
    # Connect to local DuckDB file
    conn = duckdb.connect(DB_PATH)

    # Create 'bronze' schema for raw staged tables
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze;")

    # List of tables to ingest directly from JSON using DuckDB's auto-json reader
    sources = {
        "bronze.raw_users": os.path.join(RAW_DATA_DIR, "pg_users.json"),
        "bronze.raw_plans": os.path.join(RAW_DATA_DIR, "pg_plans.json"),
        "bronze.raw_subscriptions": os.path.join(RAW_DATA_DIR, "pg_subscriptions.json"),
        "bronze.raw_clickstream": os.path.join(RAW_DATA_DIR, "mongo_clickstream.json"),
    }

    for table_name, json_path in sources.items():
        if not os.path.exists(json_path):
            print(f"File not found: {json_path}. Run extract_raw.py first!")
            continue

        # 1. Convert backslashes to forward slashes BEFORE the f-string
        clean_path = json_path.replace("\\", "/")

        # 2. Pass the clean variable into the f-string
        query = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_json_auto('{clean_path}');
        """
        conn.execute(query)
        
        # Verify row counts
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
        print(f" Staged {count} rows into DuckDB table '{table_name}'")

    conn.close()
    print("Bronze Layer complete. DuckDB database created at data/warehouse.duckdb\n")

if __name__ == "__main__":
    load_bronze_layer()