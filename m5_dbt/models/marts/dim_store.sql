-- Dimension: one row per store
-- Grain: store_id (10 stores)

with sales as (
    select * from {{ ref('stg_sales') }}
)

select distinct
    store_id        as store_key,
    state_id,
    case state_id
        when 'CA' then 'California'
        when 'TX' then 'Texas'
        when 'WI' then 'Wisconsin'
    end             as state_name
from sales