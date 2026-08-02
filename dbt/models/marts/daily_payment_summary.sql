{{
    config(
        materialized='table',
        partition_by={
            "field": "event_date",
            "data_type": "date"
        },
        cluster_by=[
            "country_code",
            "transaction_type"
        ]
    )
}}

SELECT
    event_date,
    country_code,
    transaction_type,

    COUNT(*) AS transaction_count,
    COUNT(DISTINCT player_id) AS unique_players,

    SUM(amount) AS total_amount,

    COUNTIF(transaction_status = 'SUCCESS')
        AS successful_transactions,

    COUNTIF(transaction_status = 'FAILED')
        AS failed_transactions,

    SUM(
        CASE
            WHEN transaction_status = 'SUCCESS'
            THEN amount
            ELSE 0
        END
    ) AS successful_amount

FROM {{ ref('int_payment_transactions_enriched') }}

GROUP BY
    event_date,
    country_code,
    transaction_type