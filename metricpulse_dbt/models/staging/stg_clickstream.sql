with source as (

    select * from {{ source('raw_staging', 'clickstream') }}

),

cleaned as (

    select
        event_id                                        as event_id,
        user_id::integer                                as user_id,
        session_id                                       as session_id,
        lower(trim(event_type))                          as event_type,
        page                                              as page,
        feature_name                                     as feature_name,
        event_timestamp::timestamp                       as event_timestamp,
        event_timestamp::date                            as event_date

    from source

)

select * from cleaned