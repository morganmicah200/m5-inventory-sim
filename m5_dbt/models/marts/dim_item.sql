-- Dimension: one row per product
-- Grain: item_id (~3,049 items)

with sales as (
    select * from {{ ref('stg_sales') }}
)

select distinct
    item_id         as item_key,
    dept_id,
    cat_id
from sales