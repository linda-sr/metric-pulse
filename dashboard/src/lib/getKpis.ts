import pool from '@/lib/db';

export interface KPIData {
  active_mrr: number;
  active_users: number;
  nrr_pct: number | null;
  churn_rate_pct: number | null;
  latest_month: string | null;
}

export async function getKPIs(): Promise<{ data: KPIData | null; error: string | null }> {
  try {
    const currentStateQuery = pool.query(`
      SELECT COALESCE(SUM(monthly_price), 0) AS active_mrr, COUNT(*) AS active_users
      FROM dbt_dev.dim_customers
      WHERE is_current = true AND status = 'active'
    `);

    const nrrQuery = pool.query(`
      with monthly_totals as (
          select mrr_month,
              sum(mrr_delta) as net_change,
              sum(case when movement_type not in ('new', 'resurrection') then mrr_delta else 0 end) as existing_customer_change,
              sum(case when movement_type = 'churn' then mrr_delta else 0 end) as churned_mrr
          from dbt_dev.fact_mrr_movements
          group by mrr_month
      ),
      cumulative as (
          select mrr_month, existing_customer_change, churned_mrr,
              sum(net_change) over (order by mrr_month) - net_change as starting_mrr
          from monthly_totals
      )
      select mrr_month, starting_mrr,
          case when starting_mrr > 0 then round(100.0 * (starting_mrr + existing_customer_change) / starting_mrr, 1) else null end as nrr_pct,
          case when starting_mrr > 0 then round(100.0 * abs(churned_mrr) / starting_mrr, 1) else null end as churn_rate_pct
      from cumulative
      order by mrr_month desc
      limit 1
    `);

    const [currentStateResult, nrrResult] = await Promise.all([currentStateQuery, nrrQuery]);
    const currentState = currentStateResult.rows[0];
    const nrrRow = nrrResult.rows[0];

    return {
      data: {
        active_mrr: parseFloat(currentState.active_mrr),
        active_users: parseInt(currentState.active_users, 10),
        nrr_pct: nrrRow?.nrr_pct !== null ? parseFloat(nrrRow.nrr_pct) : null,
        churn_rate_pct: nrrRow?.churn_rate_pct !== null ? parseFloat(nrrRow.churn_rate_pct) : null,
        latest_month: nrrRow?.mrr_month ?? null,
      },
      error: null,
    };
  } catch (e) {
    console.error('getKPIs error:', e);
    return { data: null, error: 'Failed to load KPI data' };
  }
}