import uuid
import random
from datetime import datetime, timedelta, timezone
import psycopg2
from faker import Faker
from pydantic import BaseModel, EmailStr, Field

fake = Faker()
Faker.seed(42)
random.seed(42)

# --- Pydantic Data Models (Type Safety & Validation) ---
class UserModel(BaseModel):
    user_id: str
    email: EmailStr
    company_name: str
    created_at: datetime

class SubscriptionModel(BaseModel):
    subscription_id: str
    user_id: str
    plan_id: str
    status: str
    mrr: float
    start_date: datetime
    end_date: datetime | None = None
    updated_at: datetime

# --- Database Connection Config ---
DB_CONFIG = {
    # "host": "localhost",
    "host": "127.0.0.1",
    "port": 5431,
    "dbname": "saas_oltp",
    "user": "oltp_user",
    "password": "oltp_password",
}

PLANS = [
    {"plan_id": "plan_starter", "price": 29.00},
    {"plan_id": "plan_pro", "price": 99.00},
    {"plan_id": "plan_enterprise", "price": 299.00},
]

def generate_saas_lifecycle(num_users=200):
    users = []
    subscriptions = []
    
    # Generate data spanning the last 365 days
    now = datetime.now(timezone.utc)
    start_window = now - timedelta(days=365)

    for _ in range(num_users):
        user_id = f"usr_{uuid.uuid4().hex[:10]}"
        created_at = fake.date_time_between(start_date=start_window, end_date=now, tzinfo=timezone.utc)
        
        user = UserModel(
            user_id=user_id,
            email=fake.email(),
            company_name=fake.company(),
            created_at=created_at
        )
        users.append(user)

        # Generate subscription behavior
        initial_plan = random.choice(PLANS)
        sub_id = f"sub_{uuid.uuid4().hex[:10]}"
        
        # Simulate Churn / Upgrades
        event_dice = random.random()
        
        if event_dice < 0.20:  # 20% Churned users
            churn_date = created_at + timedelta(days=random.randint(30, 180))
            if churn_date > now:
                churn_date = None
                status = "active"
            else:
                status = "canceled"
            
            sub = SubscriptionModel(
                subscription_id=sub_id,
                user_id=user_id,
                plan_id=initial_plan["plan_id"],
                status=status,
                mrr=initial_plan["price"] if status == "active" else 0.0,
                start_date=created_at,
                end_date=churn_date,
                updated_at=churn_date if churn_date else created_at
            )
        elif event_dice < 0.35:  # 15% Upgraded users
            upgrade_plan = PLANS[2] if initial_plan["plan_id"] == "plan_pro" else PLANS[1]
            upgrade_date = created_at + timedelta(days=random.randint(45, 120))
            
            sub = SubscriptionModel(
                subscription_id=sub_id,
                user_id=user_id,
                plan_id=upgrade_plan["plan_id"],
                status="active",
                mrr=upgrade_plan["price"],
                start_date=created_at,
                end_date=None,
                updated_at=upgrade_date if upgrade_date <= now else created_at
            )
        else:  # 65% Steady Active Users
            sub = SubscriptionModel(
                subscription_id=sub_id,
                user_id=user_id,
                plan_id=initial_plan["plan_id"],
                status="active",
                mrr=initial_plan["price"],
                start_date=created_at,
                end_date=None,
                updated_at=created_at
            )
            
        subscriptions.append(sub)

    return users, subscriptions

def seed_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. Execute DDL Schema
    with open("schema.sql", "r") as f:
        cursor.execute(f.read())
    
    print("✓ OLTP Schema created successfully.")

    # 2. Generate Data
    users, subscriptions = generate_saas_lifecycle(num_users=250)

    # 3. Insert Users
    user_records = [(u.user_id, u.email, u.company_name, u.created_at) for u in users]
    cursor.executemany(
        "INSERT INTO users (user_id, email, company_name, created_at) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING;",
        user_records
    )

    # 4. Insert Subscriptions
    sub_records = [
        (s.subscription_id, s.user_id, s.plan_id, s.status, s.mrr, s.start_date, s.end_date, s.updated_at)
        for s in subscriptions
    ]
    cursor.executemany(
        """INSERT INTO subscriptions 
           (subscription_id, user_id, plan_id, status, mrr, start_date, end_date, updated_at) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
           ON CONFLICT (subscription_id) DO NOTHING;""",
        sub_records
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✓ Successfully seeded {len(users)} users and {len(subscriptions)} subscription records into saas_oltp!")

if __name__ == "__main__":
    seed_database()