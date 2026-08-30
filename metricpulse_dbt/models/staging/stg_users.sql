with source as (

    select * from {{ source('raw_staging', 'users') }}

),

cleaned as (

    select
        user_id::integer                as user_id,
        lower(trim(email))              as email,
        signup_date::date               as signup_date,
        trim(country)                   as country

    from source

)

select * from cleaned