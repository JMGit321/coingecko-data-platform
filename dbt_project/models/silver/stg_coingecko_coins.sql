{{ config(materialized='incremental', unique_key='silver_coin_key') }}

/*
    Staging Model: Silver Layer
    Cleans raw attributes, casts data types, renames columns to standard casing,
    and removes duplicate daily records.
*/

with source_raw as (
    select * from {{ source('bronze', 'raw_coingecko_coins') }}
),

transformed as (
    select
        md5(concat(lower(trim(id)), '_', current_date::text)) as silver_coin_key,
        lower(trim(id)) as coin_id,
        upper(trim(symbol)) as coin_symbol,
        trim(name) as coin_name,
        image as image_url,
        coalesce(current_price::numeric, 0) as current_price_usd,
        coalesce(market_cap::numeric, 0) as market_cap_usd,
        coalesce(market_cap_rank::integer, 99999) as market_cap_rank,
        coalesce(total_volume::numeric, 0) as total_volume_usd,
        coalesce(high_24h::numeric, 0) as high_24h_usd,
        coalesce(low_24h::numeric, 0) as low_24h_usd,
        price_change_percentage_24h::numeric as price_change_percentage_24h,
        market_cap_change_percentage_24h::numeric as market_cap_change_percentage_24h,
        circulating_supply::numeric as circulating_supply,
        max_supply::numeric as max_supply,
        ath::numeric as ath_usd,
        ath_date::timestamp as ath_date,
        last_updated::timestamp as coin_last_updated_at,
        current_date as ingested_date
    from source_raw
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by coin_id, ingested_date
            order by coin_last_updated_at desc
        ) as row_num
    from transformed
)

select
    silver_coin_key,
    coin_id,
    coin_symbol,
    coin_name,
    image_url,
    current_price_usd,
    market_cap_usd,
    market_cap_rank,
    total_volume_usd,
    high_24h_usd,
    low_24h_usd,
    price_change_percentage_24h,
    market_cap_change_percentage_24h,
    circulating_supply,
    max_supply,
    ath_usd,
    ath_date,
    coin_last_updated_at,
    ingested_date
from deduplicated
where row_num = 1