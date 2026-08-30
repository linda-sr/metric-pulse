{{ config(materialized='table') }}

with history as (

    select * from {{ ref('int_subscription_history') }}

),

classified as (

    select
        subscription_id,
        user_id,
        plan_id,
        plan_name,
        monthly_price,
        prev_monthly_price,
        status,
        prev_status,
        event_date,
        prev_event_date,

        case
            when prev_event_date is null then 'new'
            when prev_status = 'canceled' and status = 'active' then 'resurrection'
            when status = 'canceled' then 'churn'
            when monthly_price > prev_monthly_price then 'expansion'
            when monthly_price < prev_monthly_price then 'contraction'
            else 'no_change'
        end as movement_type,

        -- The actual dollar impact of this event on MRR.
        -- New/Resurrection/Expansion: positive delta.
        -- Churn/Contraction: negative delta (note the sign flip).
        case
            when prev_event_date is null then monthly_price
            when prev_status = 'canceled' and status = 'active' then monthly_price
            when status = 'canceled' then -coalesce(prev_monthly_price, 0)
            when monthly_price > prev_monthly_price then monthly_price - prev_monthly_price
            when monthly_price < prev_monthly_price then monthly_price - prev_monthly_price  -- already negative
            else 0
        end as mrr_delta,

        date_trunc('month', event_date)::date as mrr_month

    from history

),

final as (

    select *
    from classified
    where movement_type != 'no_change'

)

select * from final