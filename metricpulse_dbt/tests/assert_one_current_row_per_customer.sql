select
    user_id,
    count(*) as current_row_count
from {{ ref('dim_customers') }}
where is_current = true
group by user_id
having count(*) != 1