import random
import psycopg2
from datetime import date, timedelta
from faker import Faker
from models import Plan, User, SubscriptionEvent

fake = Faker()
random.seed(42)
Faker.seed(42)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5431,
    "dbname": "saas_oltp",
    "user": "oltp_user",
    "password": "oltp_password",
}

N_USERS = 500
PLANS = [
    Plan(plan_id=1, plan_name="Free", monthly_price=0),
    Plan(plan_id=2, plan_name="Starter", monthly_price=19),
    Plan(plan_id=3, plan_name="Pro", monthly_price=49),
    Plan(plan_id=4, plan_name="Enterprise", monthly_price=199),
]
EVENT_TYPES_AFTER_SIGNUP = ["upgrade", "downgrade", "churn", "reactivation"]

def create_schema(cur):
    cur.execute("""
        DROP TABLE IF EXISTS subscriptions, users, plans CASCADE;

        CREATE TABLE plans (
            plan_id INT PRIMARY KEY,
            plan_name TEXT NOT NULL,
            monthly_price NUMERIC NOT NULL
        );

        CREATE TABLE users (
            user_id INT PRIMARY KEY,
            email TEXT NOT NULL,
            signup_date DATE NOT NULL,
            country TEXT NOT NULL
        );

        CREATE TABLE subscriptions (
            subscription_id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(user_id),
            plan_id INT REFERENCES plans(plan_id),
            status TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            event_type TEXT NOT NULL,
            event_date DATE NOT NULL
        );
    """)

def generate_users():
    users = []
    today = date.today()
    eighteen_months_ago = today - timedelta(days=548)  # ~18 months

    for uid in range(1, N_USERS + 1):
        signup = fake.date_between(start_date=eighteen_months_ago, end_date=today)
        users.append(User(
            user_id=uid,
            email=fake.email(),
            signup_date=signup,
            country=fake.country(),
        ))
    return users

def generate_subscription_events(users):
    events = []
    sub_id_counter = 1
    today = date.today()

    for user in users:
        current_plan = random.choices([1, 2, 3], weights=[0.5, 0.35, 0.15])[0]
        event_date = user.signup_date
        events.append(SubscriptionEvent(
            subscription_id=sub_id_counter,
            user_id=user.user_id,
            plan_id=current_plan,
            status="active",
            start_date=event_date,
            end_date=None,
            event_type="new",
            event_date=event_date,
        ))
        sub_id_counter += 1

        n_followups = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
        last_date = event_date
        status = "active"

        for _ in range(n_followups):
            last_date = last_date + timedelta(days=random.randint(20, 200))
            if last_date > today:
                break

            etype = random.choice(EVENT_TYPES_AFTER_SIGNUP)

            if etype == "upgrade":
                current_plan = min(current_plan + 1, 4)
                status = "active"
            elif etype == "downgrade":
                current_plan = max(current_plan - 1, 1)
                status = "active"
            elif etype == "churn":
                status = "canceled"
            elif etype == "reactivation":
                if status != "canceled":
                    continue
                status = "active"

            events.append(SubscriptionEvent(
                subscription_id=sub_id_counter,
                user_id=user.user_id,
                plan_id=current_plan,
                status=status,
                start_date=last_date,
                end_date=last_date if etype == "churn" else None,
                event_type=etype,
                event_date=last_date,
            ))
            sub_id_counter += 1

    return events

def insert_data(cur, users, events):
    for p in PLANS:
        cur.execute(
            "INSERT INTO plans (plan_id, plan_name, monthly_price) VALUES (%s, %s, %s)",
            (p.plan_id, p.plan_name, p.monthly_price),
        )
    for u in users:
        cur.execute(
            "INSERT INTO users (user_id, email, signup_date, country) VALUES (%s, %s, %s, %s)",
            (u.user_id, u.email, u.signup_date, u.country),
        )
    for e in events:
        cur.execute(
            """INSERT INTO subscriptions
               (subscription_id, user_id, plan_id, status, start_date, end_date, event_type, event_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (e.subscription_id, e.user_id, e.plan_id, e.status,
             e.start_date, e.end_date, e.event_type, e.event_date),
        )

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    print("Creating schema...")
    create_schema(cur)

    print("Generating users...")
    users = generate_users()

    print("Generating subscription lifecycle events...")
    events = generate_subscription_events(users)

    print(f"Inserting {len(users)} users and {len(events)} subscription events...")
    insert_data(cur, users, events)

    cur.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()