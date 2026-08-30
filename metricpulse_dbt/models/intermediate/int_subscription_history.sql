with subscriptions as (

    select * from {{ ref('stg_subscriptions') }}

),

plans as (

    select * from {{ ref('stg_plans') }}

),

joined as (

    select
        s.subscription_id,
        s.user_id,
        s.plan_id,
        p.plan_name,
        p.monthly_price,
        s.status,
        s.event_type,
        s.event_date,
        s.start_date,
        s.end_date

    from subscriptions s
    left join plans p on s.plan_id = p.plan_id

),

with_lag as (

    select
        *,
        lag(plan_id)        over (partition by user_id order by event_date, subscription_id) as prev_plan_id,
        lag(monthly_price)  over (partition by user_id order by event_date, subscription_id) as prev_monthly_price,
        lag(status)         over (partition by user_id order by event_date, subscription_id) as prev_status,
        lag(event_date)     over (partition by user_id order by event_date, subscription_id) as prev_event_date

    from joined

)

select * from with_lag