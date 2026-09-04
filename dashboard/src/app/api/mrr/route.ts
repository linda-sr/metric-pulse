import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    const result = await pool.query(`
      SELECT
        mrr_month,
        movement_type,
        SUM(mrr_delta) AS total_delta
      FROM dbt_dev.fact_mrr_movements
      GROUP BY mrr_month, movement_type
      ORDER BY mrr_month, movement_type
    `);

    return NextResponse.json({ data: result.rows });
  } catch (error) {
    console.error('Error fetching MRR data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch MRR data' },
      { status: 500 }
    );
  }
}