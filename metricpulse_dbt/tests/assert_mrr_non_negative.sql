select
    subscription_id,
    user_id,
    monthly_price
from {{ ref('int_subscription_history') }}
where monthly_price < 0