import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    const result = await pool.query(`
      SELECT
        cohort_month,
        months_since_signup,
        active_users,
        cohort_users,
        retention_pct
      FROM dbt_dev.fact_cohorts
      ORDER BY cohort_month, months_since_signup
    `);

    return NextResponse.json({ data: result.rows });
  } catch (error) {
    console.error('Error fetching cohort data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch cohort data' },
      { status: 500 }
    );
  }
}