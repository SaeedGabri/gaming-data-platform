resource "google_pubsub_topic" "payment_events" {
  name = "payment-events"

  labels = {
    environment = "dev"
    domain      = "payments"
    platform    = "gaming"
  }
}

resource "google_pubsub_subscription" "payment_events_stream" {
  name  = "payment-events-stream"
  topic = google_pubsub_topic.payment_events.id

  ack_deadline_seconds       = 30
  message_retention_duration = "604800s"

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "60s"
  }

  labels = {
    environment = "dev"
    domain      = "payments"
    platform    = "gaming"
  }
}