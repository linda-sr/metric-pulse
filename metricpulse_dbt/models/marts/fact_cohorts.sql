{{ config(materialized='table') }}

with users as (

    select
        user_id,
        date_trunc('month', signup_date)::date as cohort_month
    from {{ ref('stg_users') }}

),

sessions as (

    select
        user_id,
        date_trunc('month', session_date)::date as activity_month
    from {{ ref('int_user_sessions') }}
    group by user_id, date_trunc('month', session_date)::date  -- one row per user per active month, regardless of session count

),

cohort_size as (

    select
        cohort_month,
        count(distinct user_id) as cohort_users
    from users
    group by cohort_month

),

user_activity as (

    select
        u.user_id,
        u.cohort_month,
        s.activity_month,
        -- months_since_signup: integer count of calendar months between cohort and activity
        (extract(year from s.activity_month) - extract(year from u.cohort_month)) * 12
            + (extract(month from s.activity_month) - extract(month from u.cohort_month)) as months_since_signup

    from users u
    inner join sessions s on u.user_id = s.user_id
    where s.activity_month >= u.cohort_month  -- exclude any impossible pre-signup activity

),

retention as (

    select
        ua.cohort_month,
        ua.months_since_signup,
        count(distinct ua.user_id) as active_users,
        cs.cohort_users,
        round(100.0 * count(distinct ua.user_id) / cs.cohort_users, 1) as retention_pct

    from user_activity ua
    inner join cohort_size cs on ua.cohort_month = cs.cohort_month
    group by ua.cohort_month, ua.months_since_signup, cs.cohort_users

)

select * from retention
where months_since_signup between 0 and 12
order by cohort_month, months_since_signup