{{ config(materialized='view') }}

SELECT
    p.transaction_id,
    p.player_id,
    pl.country_code,
    pl.account_status,
    pl.vip_tier,
    pl.risk_category,
    p.transaction_type,
    p.amount,
    p.currency,
    p.payment_method,
    p.transaction_status,
    p.event_timestamp,
    p.event_date,
    p.ingestion_timestamp,
    p.source_system,
    p.batch_id
FROM {{ ref('stg_payment_transactions') }} AS p
LEFT JOIN {{ ref('stg_players') }} AS pl
    ON p.player_id = pl.player_id