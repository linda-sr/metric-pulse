import logging
import json
import psycopg2
from psycopg2.extras import execute_values

from config import PG_WAREHOUSE_CONFIG
from extract import run_extraction

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load")


def create_raw_schema(cur):
    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS raw_staging;

        DROP TABLE IF EXISTS raw_staging.plans CASCADE;
        CREATE TABLE raw_staging.plans (
            plan_id INT,
            plan_name TEXT,
            monthly_price NUMERIC
        );

        DROP TABLE IF EXISTS raw_staging.users CASCADE;
        CREATE TABLE raw_staging.users (
            user_id INT,
            email TEXT,
            signup_date DATE,
            country TEXT
        );

        DROP TABLE IF EXISTS raw_staging.subscriptions CASCADE;
        CREATE TABLE raw_staging.subscriptions (
            subscription_id INT,
            user_id INT,
            plan_id INT,
            status TEXT,
            start_date DATE,
            end_date DATE,
            event_type TEXT,
            event_date DATE
        );

        DROP TABLE IF EXISTS raw_staging.clickstream CASCADE;
        CREATE TABLE raw_staging.clickstream (
            event_id TEXT,
            user_id INT,
            session_id TEXT,
            event_type TEXT,
            page TEXT,
            feature_name TEXT,
            event_timestamp TIMESTAMP
        );
    """)

def load_plans(cur, plans):
    rows = [(p.plan_id, p.plan_name, p.monthly_price) for p in plans]
    execute_values(
        cur,
        "INSERT INTO raw_staging.plans (plan_id, plan_name, monthly_price) VALUES %s",
        rows,
    )


def load_users(cur, users):
    rows = [(u.user_id, u.email, u.signup_date, u.country) for u in users]
    execute_values(
        cur,
        "INSERT INTO raw_staging.users (user_id, email, signup_date, country) VALUES %s",
        rows,
    )


def load_subscriptions(cur, subscriptions):
    rows = [
        (s.subscription_id, s.user_id, s.plan_id, s.status,
         s.start_date, s.end_date, s.event_type, s.event_date)
        for s in subscriptions
    ]
    execute_values(
        cur,
        """INSERT INTO raw_staging.subscriptions
           (subscription_id, user_id, plan_id, status, start_date, end_date, event_type, event_date)
           VALUES %s""",
        rows,
    )


def load_clickstream(cur, clickstream):
    rows = [
        (c.event_id, c.user_id, c.session_id, c.event_type, c.page, c.feature_name, c.timestamp)
        for c in clickstream
    ]
    execute_values(
        cur,
        """INSERT INTO raw_staging.clickstream
           (event_id, user_id, session_id, event_type, page, feature_name, event_timestamp)
           VALUES %s""",
        rows,
    )


def verify_counts(cur):
    tables = ["plans", "users", "subscriptions", "clickstream"]
    counts = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM raw_staging.{t}")
        counts[t] = cur.fetchone()[0]
    return counts

def run_load():
    logger.info("Running extraction...")
    extracted = run_extraction()

    if not extracted["users"] or not extracted["plans"]:
        raise RuntimeError("Extraction returned empty users or plans — aborting load to avoid corrupting raw_staging")

    conn = None
    try:
        conn = psycopg2.connect(**PG_WAREHOUSE_CONFIG)
        conn.autocommit = False  # switch to explicit transaction control
        cur = conn.cursor()

        logger.info("Creating raw_staging schema...")
        create_raw_schema(cur)

        logger.info("Loading plans...")
        load_plans(cur, extracted["plans"])

        logger.info("Loading users...")
        load_users(cur, extracted["users"])

        logger.info("Loading subscriptions...")
        load_subscriptions(cur, extracted["subscriptions"])

        logger.info("Loading clickstream...")
        load_clickstream(cur, extracted["clickstream"])

        conn.commit()

        counts = verify_counts(cur)
        logger.info(f"Row counts in raw_staging: {counts}")
        return counts

    except Exception:
        if conn:
            conn.rollback()
            logger.error("Load failed — transaction rolled back, raw_staging left in previous state")
        raise
    finally:
        if conn:
            conn.close()
def run_load1():
    logger.info("Running extraction...")
    extracted = run_extraction()

    conn = psycopg2.connect(**PG_WAREHOUSE_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    logger.info("Creating raw_staging schema...")
    create_raw_schema(cur)

    logger.info("Loading plans...")
    load_plans(cur, extracted["plans"])

    logger.info("Loading users...")
    load_users(cur, extracted["users"])

    logger.info("Loading subscriptions...")
    load_subscriptions(cur, extracted["subscriptions"])

    logger.info("Loading clickstream...")
    load_clickstream(cur, extracted["clickstream"])

    counts = verify_counts(cur)
    logger.info(f"Row counts in raw_staging: {json.dumps(counts, indent=2)}")

    cur.close()
    conn.close()
    return counts


if __name__ == "__main__":
    run_load()