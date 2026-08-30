import random
import uuid
from datetime import timedelta, datetime
from faker import Faker
import psycopg2
from pymongo import MongoClient

fake = Faker()
random.seed(42)
Faker.seed(42)

PG_CONFIG = {
    "host": "127.0.0.1",
    "port": 5431,
    "dbname": "saas_oltp",
    "user": "oltp_user",
    "password": "oltp_password",
}

MONGO_URI = "mongodb://mongo_user:mongo_password@localhost:27017/"
MONGO_DB = "metricpulse_telemetry"

PAGES = ["/dashboard", "/billing", "/settings", "/reports", "/team", "/onboarding"]
FEATURES = ["export_csv", "invite_teammate", "create_report", "connect_integration", "set_alert"]

SESSIONS_PER_USER_WEIGHTS = [0.3, 0.3, 0.25, 0.15]  # 0-3 "bursts" of activity
EVENTS_PER_SESSION_RANGE = (2, 8)

def fetch_users():
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT user_id, signup_date FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows  # list of (user_id, signup_date)

def generate_session_events(user_id, signup_date):
    events = []
    n_sessions = random.choices([1, 2, 3, 4], weights=SESSIONS_PER_USER_WEIGHTS)[0]

    for _ in range(n_sessions):
        session_id = str(uuid.uuid4())
        days_after_signup = random.randint(0, 400)
        session_start = datetime.combine(signup_date, datetime.min.time()) + timedelta(
            days=days_after_signup,
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59),
        )

        if session_start > datetime.now():
            continue

        events.append({
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "event_type": "session_start",
            "page": "/dashboard",
            "feature_name": None,
            "timestamp": session_start,
        })

        n_events = random.randint(*EVENTS_PER_SESSION_RANGE)
        cursor_time = session_start

        for _ in range(n_events):
            cursor_time += timedelta(minutes=random.randint(1, 15))
            is_feature_click = random.random() < 0.4

            if is_feature_click:
                events.append({
                    "event_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "event_type": "feature_click",
                    "page": random.choice(PAGES),
                    "feature_name": random.choice(FEATURES),
                    "timestamp": cursor_time,
                })
            else:
                events.append({
                    "event_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "session_id": session_id,
                    "event_type": "page_view",
                    "page": random.choice(PAGES),
                    "feature_name": None,
                    "timestamp": cursor_time,
                })

    return events

def main():
    print("Fetching users from Postgres OLTP...")
    users = fetch_users()

    print(f"Generating clickstream for {len(users)} users...")
    all_events = []
    for user_id, signup_date in users:
        all_events.extend(generate_session_events(user_id, signup_date))

    print(f"Inserting {len(all_events)} events into MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    db.clickstream.drop()
    db.clickstream.insert_many(all_events)

    db.clickstream.create_index("user_id")
    db.clickstream.create_index("session_id")
    db.clickstream.create_index("timestamp")

    client.close()
    print("Done.")

if __name__ == "__main__":
    main()