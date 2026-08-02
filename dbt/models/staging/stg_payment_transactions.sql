WITH source_data AS (

    SELECT
        transaction_id,
        player_id,
        UPPER(TRIM(transaction_type)) AS transaction_type,
        amount,
        UPPER(TRIM(currency)) AS currency,
        UPPER(TRIM(payment_method)) AS payment_method,
        UPPER(TRIM(transaction_status)) AS transaction_status,
        event_timestamp,
        ingestion_timestamp,
        source_system,
        batch_id
    FROM {{ source('gaming_bronze', 'payment_transactions') }}

),

validated_and_deduplicated AS (

    SELECT
        transaction_id,
        player_id,
        transaction_type,
        amount,
        currency,
        payment_method,
        transaction_status,
        event_timestamp,
        DATE(event_timestamp) AS event_date,
        ingestion_timestamp,
        source_system,
        batch_id
    FROM source_data
    WHERE transaction_id IS NOT NULL
      AND player_id IS NOT NULL
      AND amount > 0
      AND transaction_type IN ('DEPOSIT', 'WITHDRAWAL')
      AND transaction_status IN ('SUCCESS', 'FAILED', 'PENDING', 'REVERSED')

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY transaction_id
        ORDER BY ingestion_timestamp DESC
    ) = 1

)

SELECT *
FROM validated_and_deduplicated