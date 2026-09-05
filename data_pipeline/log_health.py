import json
import os
import psycopg2

CLOUD_WAREHOUSE_URL = os.getenv("CLOUD_WAREHOUSE_URL")

def main():
    with open("../metricpulse_dbt/target/run_results.json") as f:
        results = json.load(f)

    tests = [r for r in results["results"] if r["unique_id"].startswith("test.")]
    passed = sum(1 for t in tests if t["status"] == "pass")
    failed = len(tests) - passed

    conn = psycopg2.connect(CLOUD_WAREHOUSE_URL)
    cur = conn.cursor()

    row_counts = {}
    for schema, table in [
        ("raw_staging", "plans"), ("raw_staging", "users"),
        ("raw_staging", "subscriptions"), ("raw_staging", "clickstream"),
        ("dbt_dev", "dim_customers"), ("dbt_dev", "fact_mrr_movements"),
        ("dbt_dev", "fact_cohorts"),
    ]:
        cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
        row_counts[f"{schema}.{table}"] = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO public.pipeline_health_log (total_tests, passed, failed, row_counts) VALUES (%s, %s, %s, %s)",
        (len(tests), passed, failed, json.dumps(row_counts)),
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Logged health snapshot: {passed}/{len(tests)} passed")

if __name__ == "__main__":
    main()