{{ config(materialized='table') }}

with subscription_history as (

    select * from {{ ref('int_subscription_history') }}

),

users as (

    select * from {{ ref('stg_users') }}

),

with_valid_to as (

    select
        sh.*,
        u.email,
        u.country,
        u.signup_date,
        -- Sample - Git pull requiest trial
        -- valid_to = the date the NEXT event for this user occurred.
        -- If there is no next event, this row represents their current state (valid_to = NULL).
        lead(sh.event_date) over (
            partition by sh.user_id
            order by sh.event_date, sh.subscription_id
        ) as valid_to

    from subscription_history sh
    left join users u on sh.user_id = u.user_id

),

final as (

    select
        {{ dbt_utils.generate_surrogate_key(['user_id', 'event_date', 'subscription_id']) }} as customer_key,
        user_id,
        email,
        country,
        signup_date,
        plan_id,
        plan_name,
        monthly_price,
        status,
        event_type                        as change_reason,
        event_date                        as valid_from,
        valid_to,
        case when valid_to is null then true else false end as is_current

    from with_valid_to

)

select * from final