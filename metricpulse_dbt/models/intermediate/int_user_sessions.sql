with clickstream as (

    select * from {{ ref('stg_clickstream') }}

),

session_agg as (

    select
        session_id,
        user_id,
        min(event_timestamp)                                              as session_start,
        max(event_timestamp)                                              as session_end,
        extract(epoch from (max(event_timestamp) - min(event_timestamp))) as duration_seconds,
        count(*)                                                          as total_events,
        count(*) filter (where event_type = 'page_view')                  as page_view_count,
        count(*) filter (where event_type = 'feature_click')              as feature_click_count,
        count(distinct page)                                              as distinct_pages_viewed,
        count(distinct feature_name)                                      as distinct_features_used,
        min(event_date)                                                   as session_date

    from clickstream
    group by session_id, user_id

)

select * from session_agg