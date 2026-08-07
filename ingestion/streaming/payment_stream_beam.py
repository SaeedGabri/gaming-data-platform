import json
from datetime import datetime, timezone

import apache_beam as beam
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    StandardOptions,
)


PROJECT_ID = "gaming-data-platform-dev"
SUBSCRIPTION_ID = "payment-events-stream"

SUBSCRIPTION_PATH = (
    f"projects/{PROJECT_ID}/subscriptions/{SUBSCRIPTION_ID}"
)


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
        "transaction_status",
        "event_timestamp",
    ]

    return all(
        field in event and event[field] is not None
        for field in required_fields
    )


def show_event(event):
    print(
        "BEAM RECEIVED:",
        json.dumps(event, indent=2),
        flush=True,
    )

    return event


options = PipelineOptions()

options.view_as(
    StandardOptions
).streaming = True


with beam.Pipeline(options=options) as pipeline:

    (
        pipeline
        |
        "Read payment events"
        >> beam.io.ReadFromPubSub(
            subscription=SUBSCRIPTION_PATH
        )
        |
        "Parse JSON"
        >> beam.Map(parse_event)
        |
        "Validate payment"
        >> beam.Filter(valid_payment)
        |
        "Print event"
        >> beam.Map(show_event)
    )