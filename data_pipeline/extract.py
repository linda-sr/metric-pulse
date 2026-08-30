import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from pydantic import ValidationError

from config import PG_OLTP_CONFIG, MONGO_URI, MONGO_DB
from models import (
    ExtractedSubscriptionEvent,
    ExtractedUser,
    ExtractedPlan,
    ExtractedClickstreamEvent,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("extract")


def extract_postgres_table(table_name: str, model_cls):
    """Generic extractor: pulls all rows from a Postgres table and validates each via pydantic."""
    conn = psycopg2.connect(**PG_OLTP_CONFIG, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    validated, errors = [], []
    for row in rows:
        try:
            validated.append(model_cls(**row))
        except ValidationError as e:
            errors.append({"row": dict(row), "error": str(e)})

    logger.info(f"[{table_name}] extracted {len(rows)} rows, {len(validated)} valid, {len(errors)} invalid")
    if errors:
        logger.warning(f"[{table_name}] sample error: {errors[0]}")

    return validated, errors


def extract_clickstream():
    """Pulls all documents from the Mongo clickstream collection and validates each."""
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    docs = list(db.clickstream.find({}))
    client.close()

    validated, errors = [], []
    for doc in docs:
        doc.pop("_id", None)  # Mongo's ObjectId isn't part of our schema
        try:
            validated.append(ExtractedClickstreamEvent(**doc))
        except ValidationError as e:
            errors.append({"row": doc, "error": str(e)})

    logger.info(f"[clickstream] extracted {len(docs)} docs, {len(validated)} valid, {len(errors)} invalid")
    if errors:
        logger.warning(f"[clickstream] sample error: {errors[0]}")

    return validated, errors


def run_extraction():
    plans, plan_errors = extract_postgres_table("plans", ExtractedPlan)
    users, user_errors = extract_postgres_table("users", ExtractedUser)
    subscriptions, sub_errors = extract_postgres_table("subscriptions", ExtractedSubscriptionEvent)
    clickstream, click_errors = extract_clickstream()

    return {
        "plans": plans,
        "users": users,
        "subscriptions": subscriptions,
        "clickstream": clickstream,
        "errors": {
            "plans": plan_errors,
            "users": user_errors,
            "subscriptions": sub_errors,
            "clickstream": click_errors,
        },
    }


if __name__ == "__main__":
    result = run_extraction()
    for key in ["plans", "users", "subscriptions", "clickstream"]:
        print(f"{key}: {len(result[key])} valid records")
    total_errors = sum(len(v) for v in result["errors"].values())
    print(f"Total validation errors: {total_errors}")