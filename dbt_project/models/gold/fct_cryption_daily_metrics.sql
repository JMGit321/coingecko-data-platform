/*
    Fact Table: Gold Layer
    Contains daily snapshot metrics, prices, and financial indicators for modeling in Metabase.
*/

with stg_coins as (
    select * from {{ ref('stg_coingecko_coins') }}
)

select
    silver_coin_key as fact_crypto_daily_key,
    coin_id,
    ingested_date as date_key,
    current_price_usd,
    market_cap_usd,
    market_cap_rank,
    total_volume_usd,
    high_24h_usd,
    low_24h_usd,
    price_change_percentage_24h,
    market_cap_change_percentage_24h,
    case 
        when current_price_usd >= ath_usd then true 
        else false 
    end as is_at_ath_flag,
    coin_last_updated_at
from stg_coins