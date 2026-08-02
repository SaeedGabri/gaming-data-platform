# Source Systems and Data Contracts

## PLAYER_SERVICE

Produces one daily player extract.

Primary key:
- player_id

Important fields:
- registration_timestamp
- country_code
- account_status
- vip_tier
- risk_category
- updated_timestamp

## GAME_CATALOGUE

Produces the active and historical game catalogue.

Primary key:
- game_id

Important fields:
- provider_name
- game_category
- launch_date
- is_active
- updated_timestamp

## PAYMENT_SERVICE

Produces payment transactions.

Primary key:
- transaction_id

Foreign key:
- player_id

Important fields:
- transaction_type
- amount
- currency
- payment_method
- transaction_status
- event_timestamp
- ingestion_timestamp

## Data-quality expectations

- IDs must be present and unique within the extract.
- Monetary amounts must be greater than zero.
- Currency must use a controlled three-letter code.
- Status values must come from approved lists.
- Event timestamps cannot be unreasonably far in the future.
- Payment player IDs should resolve to a known player.
