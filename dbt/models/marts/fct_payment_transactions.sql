{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='transaction_id',
        partition_by={
            "field": "event_date",
            "data_type": "date"
        },
        cluster_by=[
            "country_code",
            "transaction_type"
        ],
        on_schema_change='fail'
    )
}}

SELECT
    transaction_id,
    player_id,
    country_code,
    account_status,
    vip_tier,
    risk_category,
    transaction_type,
    amount,
    currency,
    payment_method,
    transaction_status,
    event_timestamp,
    event_date,
    ingestion_timestamp,
    source_system,
    batch_id

FROM {{ ref('int_payment_transactions_enriched') }}

{% if is_incremental() %}

WHERE ingestion_timestamp >= (
    SELECT COALESCE(
        MAX(ingestion_timestamp),
        TIMESTAMP('1900-01-01 00:00:00+00')
    )
    FROM {{ this }}
)

{% endif %}