-- Staging: daily unit sales, unpivoted from wide (1,941 day columns) to long
-- Grain: item_id + store_id + day_id  (~59.2M rows)

{{ config(materialized='table') }}

with source as (
    select * from {{ source('raw', 'raw_sales') }}
),

unpivoted as (
    select
        item_id,
        dept_id,
        cat_id,
        store_id,
        state_id,
        day_id,
        units_sold
    from source
    unpivot (
        units_sold for day_id in (
            {% for i in range(1, 1942) -%}
                d_{{ i }}{% if not loop.last %}, {% endif %}
            {%- endfor %}
        )
    )
)

select
    item_id,
    dept_id,
    cat_id,
    store_id,
    state_id,
    lower(day_id)                                   as day_id,
    cast(replace(lower(day_id), 'd_', '') as integer) as day_number,
    units_sold
from unpivoted