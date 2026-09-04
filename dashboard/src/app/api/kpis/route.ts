import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    // Active MRR + Active Users: straightforward aggregates over the
    // customer base's CURRENT state.
    const currentStateQuery = pool.query(`
      SELECT
        COALESCE(SUM(monthly_price), 0) AS active_mrr,
        COUNT(*) AS active_users
      FROM dbt_dev.dim_customers
      WHERE is_current = true AND status = 'active'
    `);

    // NRR + Churn Rate: requires "starting MRR" per month, which is the
    // cumulative net MRR change up to (but not including) that month.
    const nrrQuery = pool.query(`
      with monthly_totals as (
          select
              mrr_month,
              sum(mrr_delta) as net_change,
              sum(case when movement_type not in ('new', 'resurrection') then mrr_delta else 0 end) as existing_customer_change,
              sum(case when movement_type = 'churn' then mrr_delta else 0 end) as churned_mrr
          from dbt_dev.fact_mrr_movements
          group by mrr_month
      ),

      cumulative as (
          select
              mrr_month,
              existing_customer_change,
              churned_mrr,
              -- Starting MRR = cumulative MRR through the END of the PRIOR month,
              -- i.e. running total minus this month's own net change.
              sum(net_change) over (order by mrr_month) - net_change as starting_mrr
          from monthly_totals
      )

      select
          mrr_month,
          starting_mrr,
          existing_customer_change,
          churned_mrr,
          case when starting_mrr > 0
               then round(100.0 * (starting_mrr + existing_customer_change) / starting_mrr, 1)
               else null
          end as nrr_pct,
          case when starting_mrr > 0
               then round(100.0 * abs(churned_mrr) / starting_mrr, 1)
               else null
          end as churn_rate_pct
      from cumulative
      order by mrr_month desc
      limit 1
    `);

    const [currentStateResult, nrrResult] = await Promise.all([currentStateQuery, nrrQuery]);

    const currentState = currentStateResult.rows[0];
    const nrrRow = nrrResult.rows[0];

    return NextResponse.json({
      data: {
        active_mrr: parseFloat(currentState.active_mrr),
        active_users: parseInt(currentState.active_users, 10),
        nrr_pct: nrrRow?.nrr_pct !== null ? parseFloat(nrrRow.nrr_pct) : null,
        churn_rate_pct: nrrRow?.churn_rate_pct !== null ? parseFloat(nrrRow.churn_rate_pct) : null,
        latest_month: nrrRow?.mrr_month ?? null,
      },
    });
  } catch (error) {
    console.error('Error fetching KPI data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch KPI data' },
      { status: 500 }
    );
  }
}