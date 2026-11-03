-- Dimension: one row per calendar day
-- Grain: calendar_date

with calendar as (
    select * from {{ ref('stg_calendar') }}
)

select
    calendar_date                                   as date_key,
    day_id,
    day_number,
    walmart_week_id,
    weekday_name,
    walmart_weekday_number,
    weekday_name in ('Saturday', 'Sunday')          as is_weekend,
    calendar_month,
    calendar_year,
    event_name_1,
    event_type_1,
    event_name_2,
    event_type_2,
    is_event_day,
    is_snap_ca,
    is_snap_tx,
    is_snap_wi
from calendar