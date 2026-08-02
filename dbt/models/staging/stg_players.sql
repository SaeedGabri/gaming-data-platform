WITH source_data AS (

    SELECT
        player_id,
        registration_timestamp,
        UPPER(TRIM(country_code)) AS country_code,
        UPPER(TRIM(account_status)) AS account_status,
        UPPER(TRIM(vip_tier)) AS vip_tier,
        UPPER(TRIM(risk_category)) AS risk_category,
        updated_timestamp,
        source_system,
        batch_id
    FROM {{ source('gaming_bronze', 'players') }}

),

deduplicated AS (

    SELECT *
    FROM source_data
    WHERE player_id IS NOT NULL

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY player_id
        ORDER BY updated_timestamp DESC
    ) = 1

)

SELECT *
FROM deduplicated