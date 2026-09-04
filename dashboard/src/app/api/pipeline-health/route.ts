import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import path from 'path';
import pool from '@/lib/db';

interface DbtTestResult {
  unique_id: string;
  status: string; // 'pass' | 'fail' | 'error' | 'skipped'
  execution_time: number;
  message: string | null;
}

async function getDbtTestResults() {
  const dbtProjectPath = process.env.DBT_PROJECT_PATH;
  if (!dbtProjectPath) {
    throw new Error('DBT_PROJECT_PATH environment variable is not set');
  }

  const runResultsPath = path.join(dbtProjectPath, 'target', 'run_results.json');
  const raw = await readFile(runResultsPath, 'utf-8');
  const parsed = JSON.parse(raw);

  // run_results.json contains an entry for every node dbt executed —
  // both models (materializations) and tests. We only care about tests here.
  const testResults: DbtTestResult[] = parsed.results
    .filter((r: any) => r.unique_id.startsWith('test.'))
    .map((r: any) => ({
      unique_id: r.unique_id,
      status: r.status,
      execution_time: r.execution_time,
      message: r.message ?? null,
    }));

  const passed = testResults.filter((t) => t.status === 'pass').length;
  const failed = testResults.filter((t) => t.status !== 'pass').length;

  return {
    generated_at: parsed.metadata?.generated_at ?? null,
    total_tests: testResults.length,
    passed,
    failed,
    failing_tests: testResults.filter((t) => t.status !== 'pass'),
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