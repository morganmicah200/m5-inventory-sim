-- Staging: weekly sell price per item and store
-- Grain: store_id + item_id + walmart_week_id

with source as (
    select * from {{ source('raw', 'raw_prices') }}
)

select
    store_id,
    item_id,
    wm_yr_wk        as walmart_week_id,
    sell_price
from source