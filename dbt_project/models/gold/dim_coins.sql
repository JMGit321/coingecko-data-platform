/*
    Dimension Table: Gold Layer
    Contains descriptive attributes and static information for cryptocurrencies.
*/

with stg_coins as (
    select * from {{ ref('stg_coingecko_coins') }}
),

latest_records as (
    select
        coin_id,
        coin_symbol,
        coin_name,
        image_url,
        ath_usd,
        ath_date,
        max_supply,
        row_number() over (
            partition by coin_id 
            order by coin_last_updated_at desc
        ) as rank_idx
    from stg_coins
)

select
    coin_id,
    coin_symbol,
    coin_name,
    image_url,
    ath_usd,
    ath_date,
    max_supply
from latest_records
where rank_idx = 1