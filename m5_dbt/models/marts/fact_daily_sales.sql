-- Fact: daily unit sales with price and revenue
-- Grain: item_key + store_key + date_key  (~59.2M rows)

with sales as (
    select * from {{ ref('stg_sales') }}
),

calendar as (
    select * from {{ ref('stg_calendar') }}
),

prices as (
    select * from {{ ref('stg_prices') }}
)

select
    s.item_id                               as item_key,
    s.store_id                              as store_key,
    c.calendar_date                         as date_key,
    c.walmart_week_id,
    s.units_sold,
    p.sell_price,
    s.units_sold * p.sell_price             as revenue,
    p.sell_price is not null                as is_listed
from sales s
inner join calendar c
    on s.day_id = c.day_id
left join prices p
    on  s.store_id = p.store_id
    and s.item_id = p.item_id
    and c.walmart_week_id = p.walmart_week_id