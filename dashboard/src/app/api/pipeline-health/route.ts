import { NextResponse } from 'next/server';
import path from 'path';
import pool from '@/lib/db';

interface DbtTestResult {
  unique_id: string;
  status: string; // 'pass' | 'fail' | 'error' | 'skipped'
  execution_time: number;
  message: string | null;
}

async function getDbtTestResults() {
  const result = await pool.query(`
    SELECT run_at, total_tests, passed, failed
    FROM public.pipeline_health_log
    ORDER BY run_at DESC
    LIMIT 1
  `);
  const row = result.rows[0];
  if (!row) throw new Error("No pipeline health data logged yet");
  return {
    generated_at: row.run_at,
    total_tests: row.total_tests,
    passed: row.passed,
    failed: row.failed,
    failing_tests: [], // detailed per-test failures aren't stored in this summary table
  };
}

async function getRowCounts() {
  const tables = [
    { schema: 'raw_staging', name: 'plans' },
    { schema: 'raw_staging', name: 'users' },
    { schema: 'raw_staging', name: 'subscriptions' },
    { schema: 'raw_staging', name: 'clickstream' },
    { schema: 'dbt_dev', name: 'dim_customers' },
    { schema: 'dbt_dev', name: 'fact_mrr_movements' },
    { schema: 'dbt_dev', name: 'fact_cohorts' },
  ];

  const counts = await Promise.all(
    tables.map(async (t) => {
      const result = await pool.query(`SELECT COUNT(*) AS count FROM ${t.schema}.${t.name}`);
      return {
        table: `${t.schema}.${t.name}`,
        count: parseInt(result.rows[0].count, 10),
      };
    })
  );

  return counts;
}

export async function GET() {
  try {
    const [dbtHealth, rowCounts] = await Promise.all([
      getDbtTestResults(),
      getRowCounts(),
    ]);

    return NextResponse.json({ data: { dbtHealth, rowCounts } });
  } catch (error) {
    console.error('Error fetching pipeline health:', error);
    return NextResponse.json(
      { error: 'Failed to fetch pipeline health data. Have you run `dbt test` at least once?' },
      { status: 500 }
    );
  }
}