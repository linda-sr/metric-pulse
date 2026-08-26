import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient

# Import data generators/models to reuse Pydantic schemas
from seed_oltp import UserModel, SubscriptionModel
from seed_mongo import ClickstreamEventModel

RAW_DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
os.makedirs(RAW_DATA_DIR, exist_ok=True)

PG_CONFIG = {
    "host": "127.0.0.1",
    "port": 5431,
    "dbname": "saas_oltp",
    "user": "oltp_user",
    "password": "oltp_password",
}

MONGO_URI = "mongodb://mongo_user:mongo_password@127.0.0.1:27017/admin?authSource=admin"

def extract_postgres_tables():
    print("Extracting PostgreSQL relational tables with Pydantic validation")
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    table_model_map = {
        "users": UserModel,
        "subscriptions": SubscriptionModel,
    }

    # Extract static 'plans' table directly
    cursor.execute("SELECT * FROM plans;")
    plans_records = [dict(row) for row in cursor.fetchall()]
    with open(os.path.join(RAW_DATA_DIR, "pg_plans.json"), "w", encoding="utf-8") as f:
        json.dump(plans_records, f, indent=2, default=str)

    # Extract & validate users + subscriptions
    for table, model_cls in table_model_map.items():
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        
        validated_records = []
        for row in rows:
            try:
                # Pydantic validates types and handles nulls
                validated_obj = model_cls(**dict(row))
                validated_records.append(validated_obj.model_dump())
            except Exception as e:
                print(f"Validation skipped invalid record in '{table}': {e}")

        output_file = os.path.join(RAW_DATA_DIR, f"pg_{table}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(validated_records, f, indent=2, default=str)
            
        print(f"Validated & extracted {len(validated_records)} records from '{table}' -> {output_file}")

    cursor.close()
    conn.close()

def extract_mongo_collections():
    print("Extracting MongoDB telemetry collections with Pydantic validation")
    client = MongoClient(MONGO_URI)
    db = client["saas_telemetry"]
    collection = db["clickstream_events"]

    cursor = collection.find({}, {"_id": 0})
    raw_docs = list(cursor)

    validated_events = []
    for doc in raw_docs:
        try:
            validated_obj = ClickstreamEventModel(**doc)
            validated_events.append(validated_obj.model_dump())
        except Exception as e:
            print(f"Validation skipped invalid Mongo document: {e}")

    output_file = os.path.join(RAW_DATA_DIR, "mongo_clickstream.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(validated_events, f, indent=2, default=str)

    print(f"Validated & extracted {len(validated_events)} documents from Mongo -> {output_file}")
    client.close()

def run_extraction():
    print("Running ELT Extraction Pipeline...")
    extract_postgres_tables()
    extract_mongo_collections()
    print("Extraction Complete! All validated landing files generated in data/raw/\n")

if __name__ == "__main__":
    run_extraction()