select *
from {{ ref('fact_cohorts') }}
where retention_pct > 100 or retention_pct < 0