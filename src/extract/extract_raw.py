import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient

# --- Paths & Directory Configs ---
RAW_DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# --- Database Configurations ---
PG_CONFIG = {
    "host": "127.0.0.1",
    "port": 5431,
    "dbname": "saas_oltp",
    "user": "oltp_user",
    "password": "oltp_password",
}

MONGO_URI = "mongodb://mongo_user:mongo_password@127.0.0.1:27017/admin?authSource=admin"

def extract_postgres_tables():
    """Extracts raw tables from PostgreSQL OLTP and dumps to JSON staging files."""
    print("1. Extracting PostgreSQL relational tables...")
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    tables = ["users", "plans", "subscriptions"]
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        
        records = [dict(row) for row in rows]
        
        output_file = os.path.join(RAW_DATA_DIR, f"pg_{table}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            # default=str handles Decimal, datetime, and date automatically
            json.dump(records, f, indent=2, default=str)
            
        print(f"   ✓ Extracted {len(records)} records from Postgres '{table}' -> {output_file}")

    cursor.close()
    conn.close()

def extract_mongo_collections():
    """Extracts raw collections from MongoDB Telemetry and dumps to JSON staging files."""
    print("2. Extracting MongoDB NoSQL telemetry collections...")
    client = MongoClient(MONGO_URI)
    db = client["saas_telemetry"]
    collection = db["clickstream_events"]

    cursor = collection.find({}, {"_id": 0})
    records = list(cursor)

    output_file = os.path.join(RAW_DATA_DIR, "mongo_clickstream.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)

    print(f"   ✓ Extracted {len(records)} documents from Mongo 'clickstream_events' -> {output_file}")
    client.close()

def run_extraction():
    print("Starting Day 4 Raw Extraction Pipeline...")
    extract_postgres_tables()
    extract_mongo_collections()
    print("✓ Extraction pipeline complete! All raw landing files generated in data/raw/\n")

if __name__ == "__main__":
    run_extraction()