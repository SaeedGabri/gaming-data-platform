# Phase 1 Architecture

## Business flow

The source platform produces three daily batch domains:

1. Players
   - player identity
   - country
   - account status
   - VIP tier
   - risk category

2. Games
   - game catalogue
   - provider
   - category
   - active status

3. Payment transactions
   - deposits
   - withdrawals
   - status
   - amount
   - payment method
   - event and ingestion timestamps

## Layered platform

### Bronze

Purpose:
- preserve the source record
- add ingestion metadata
- allow replay and audit
- avoid business transformation

Key fields:
- source_file_name
- batch_id
- ingestion_timestamp
- record_hash
- source_system

### Silver

Purpose:
- standardise data types
- remove duplicates
- validate business rules
- quarantine invalid records
- resolve reference data
- prepare trusted entities

### Gold

Purpose:
- dimensional modelling
- business metrics
- reporting and analytics
- AI-approved data access

Initial Gold outputs:
- dim_player
- dim_game
- dim_date
- fact_payment_transaction
- daily_payment_summary
- player_activity_summary

## Reliability requirements

The pipeline must eventually support:

- safe reruns
- failed-record isolation
- source-to-target counts
- retries
- backfills
- late-arriving events
- freshness alerts
- schema validation
- cost-aware BigQuery queries
