-- Staging: one row per day, renamed and typed for analysis
-- Grain: calendar_date (d_1 to d_1969)

with source as (
    select * from {{ source('raw', 'raw_calendar') }}
)

select
    date                                    as calendar_date,
    d                                       as day_id,
    cast(replace(d, 'd_', '') as integer)   as day_number,
    wm_yr_wk                                as walmart_week_id,
    weekday                                 as weekday_name,
    wday                                    as walmart_weekday_number,  -- 1 = Saturday (Walmart week starts Sat)
    month                                   as calendar_month,
    year                                    as calendar_year,

    event_name_1,
    event_type_1,
    event_name_2,
    event_type_2,
    event_name_1 is not null                as is_event_day,

    snap_ca::boolean                        as is_snap_ca,
    snap_tx::boolean                        as is_snap_tx,
    snap_wi::boolean                        as is_snap_wi

from source