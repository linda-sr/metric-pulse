import os
from dotenv import load_dotenv

load_dotenv()

PG_OLTP_CONFIG = {
    "host": "127.0.0.1",
    "port": 5431,
    "dbname": "saas_oltp",
    "user": "oltp_user",
    "password": "oltp_password",
}

PG_WAREHOUSE_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "dbname": "saas_warehouse",
    "user": "warehouse_user",
    "password": "warehouse_password",
}

CLOUD_WAREHOUSE_URL = os.getenv("CLOUD_WAREHOUSE_URL")
TARGET = os.getenv("TARGET", "local")

MONGO_URI = "mongodb://mongo_user:mongo_password@localhost:27017/"
MONGO_DB = "metricpulse_telemetry"
CI_WAREHOUSE_URL = os.getenv("CI_WAREHOUSE_URL")