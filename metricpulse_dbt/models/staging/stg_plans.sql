with source as (

    select * from {{ source('raw_staging', 'plans') }}

),

cleaned as (

    select
        plan_id::integer                as plan_id,
        lower(trim(plan_name))          as plan_name,
        monthly_price::numeric          as monthly_price

    from source

)

select * from cleaned