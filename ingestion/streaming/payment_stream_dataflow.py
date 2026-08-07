import json
from datetime import datetime, timezone

import apache_beam as beam
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    SetupOptions,
    StandardOptions,
)


PROJECT_ID = "gaming-data-platform-dev"

SUBSCRIPTION = (
    "projects/gaming-data-platform-dev/"
    "subscriptions/payment-events-stream"
)

OUTPUT_TABLE = (
    "gaming-data-platform-dev:"
    "gaming_bronze.payment_transactions_stream"
)

BIGQUERY_SCHEMA = {
    "fields": [
        {"name": "transaction_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "player_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "transaction_type", "type": "STRING", "mode": "REQUIRED"},
        {"name": "amount", "type": "NUMERIC", "mode": "REQUIRED"},
        {"name": "currency", "type": "STRING", "mode": "REQUIRED"},
        {"name": "payment_method", "type": "STRING", "mode": "REQUIRED"},
        {"name": "transaction_status", "type": "STRING", "mode": "REQUIRED"},
        {"name": "event_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "ingestion_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "source_system", "type": "STRING", "mode": "REQUIRED"},
    ]
}


def parse_event(message):
    event = json.loads(message.decode("utf-8"))

    event["ingestion_timestamp"] = datetime.now(
        timezone.utc
    ).isoformat()

    return event


def valid_payment(event):
    required_fields = [
        "transaction_id",
        "player_id",
        "transaction_type",
        "amount",
        "currency",
        "payment_method",
        "transaction_status",
        "event_timestamp",
        "source_system",
    ]

    return all(
        event.get(field) is not None
        for field in required_fields
    )


def run():
    options = PipelineOptions()

    options.view_as(StandardOptions).streaming = True
    options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=options) as pipeline:

        (
            pipeline
            | "Read PubSub"
            >> beam.io.ReadFromPubSub(
                subscription=SUBSCRIPTION
            )
            | "Parse JSON"
            >> beam.Map(parse_event)
            | "Validate Payments"
            >> beam.Filter(valid_payment)
            | "Write BigQuery"
            >> beam.io.WriteToBigQuery(
                table=OUTPUT_TABLE,
                schema=BIGQUERY_SCHEMA,
                create_disposition=(
                    beam.io.BigQueryDisposition.CREATE_NEVER
                ),
                write_disposition=(
                    beam.io.BigQueryDisposition.WRITE_APPEND
                ),
                method=(
                    beam.io.WriteToBigQuery.Method.STREAMING_INSERTS
                ),
            )
        )


if __name__ == "__main__":
    run()