with source as (

    select * from {{ source('raw_staging', 'subscriptions') }}

),

cleaned as (

    select
        subscription_id::integer                       as subscription_id,
        user_id::integer                                as user_id,
        plan_id::integer                                as plan_id,
        lower(trim(status))                             as status,
        lower(trim(event_type))                         as event_type,
        start_date::date                                as start_date,
        end_date::date                                  as end_date,
        event_date::date                                as event_date

    from source

)

select * from cleaned