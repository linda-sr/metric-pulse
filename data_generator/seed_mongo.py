import random
import uuid
from datetime import datetime, timedelta, timezone
import psycopg2
from pymongo import MongoClient
from pydantic import BaseModel, Field

# --- Pydantic Data Model for Clickstream Events ---
class ClickstreamEventModel(BaseModel):
    event_id: str
    user_id: str
    session_id: str
    event_type: str  # 'page_view', 'feature_click', 'session_start'
    page_url: str
    feature_name: str | None = None
    device_type: str
    ip_address: str
    timestamp: datetime

# --- Database Configurations ---
PG_CONFIG = {
    "host": "127.0.0.1",
    "port": 5431,
    "dbname": "saas_oltp",
    "user": "oltp_user",
    "password": "oltp_password",
}

MONGO_URI = "mongodb://mongo_user:mongo_password@127.0.0.1:27017/admin?authSource=admin"

# --- Telemetry Metadata Pools ---
PAGES = [
    "/dashboard",
    "/settings/billing",
    "/analytics/reports",
    "/projects/new",
    "/team/members",
]

FEATURES = [
    "export_csv",
    "trigger_webhook",
    "filter_date_range",
    "invite_user",
    "upgrade_modal_click",
]

DEVICES = ["desktop_mac", "desktop_windows", "mobile_ios", "mobile_android"]

def fetch_existing_users():
    # Fetch real user_ids and creation dates from PostgreSQL to maintain cross-db integrity.
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, created_at FROM users;")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records

def generate_clickstream_events(users, total_events=5000):
    events = []
    now = datetime.now(timezone.utc)

    for _ in range(total_events):
        user_id, user_created_at = random.choice(users)
        
        # Ensure telemetry events occur AFTER the user signed up
        event_time = user_created_at + timedelta(
            seconds=random.randint(0, int((now - user_created_at).total_seconds()))
        )
        
        # Group events into sessions
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        device = random.choice(DEVICES)
        ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        event_type = random.choice(["page_view", "feature_click", "session_start"])
        page = random.choice(PAGES)
        feature = random.choice(FEATURES) if event_type == "feature_click" else None

        event = ClickstreamEventModel(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            page_url=page,
            feature_name=feature,
            device_type=device,
            ip_address=ip,
            timestamp=event_time
        )
        events.append(event.model_dump())  # Convert Pydantic model to dict for Mongo

    return events

def seed_mongo():
    print("1. Fetching valid user IDs from PostgreSQL OLTP...")
    users = fetch_existing_users()
    if not users:
        print("No users found in PostgreSQL. Please run seed_oltp.py first!")
        return

    print(f"Found {len(users)} users in PostgreSQL.")

    print("2. Generating 5,000 synthetic clickstream events...")
    events = generate_clickstream_events(users, total_events=5000)

    print("3. Connecting to MongoDB...")
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["saas_telemetry"]
    collection = db["clickstream_events"]

    # Clear previous runs and insert bulk documents
    collection.delete_many({})
    result = collection.insert_many(events)

    print(f"Successfully inserted {len(result.inserted_ids)} telemetry documents into MongoDB ('saas_telemetry.clickstream_events')!")

if __name__ == "__main__":
    seed_mongo()