resource "google_storage_bucket" "dataflow_temp" {
  name     = "gaming-data-platform-dev-saeed-dataflow-temp"
  project  = "gaming-data-platform-dev"
  location = "ME-CENTRAL1"

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = true

  labels = {
    environment = "dev"
    component   = "dataflow"
    platform    = "gaming"
  }
}

resource "google_service_account" "dataflow_payment_worker" {
  project      = "gaming-data-platform-dev"
  account_id   = "dataflow-payment-worker"
  display_name = "Dataflow Payment Worker"

  description = (
    "Worker identity for the payment streaming Dataflow pipeline"
  )
}

resource "google_project_iam_member" "dataflow_worker_role" {
  project = "gaming-data-platform-dev"
  role    = "roles/dataflow.worker"

  member = (
    "serviceAccount:${google_service_account.dataflow_payment_worker.email}"
  )
}

resource "google_project_iam_member" "dataflow_pubsub_subscriber" {
  project = "gaming-data-platform-dev"
  role    = "roles/pubsub.subscriber"

  member = (
    "serviceAccount:${google_service_account.dataflow_payment_worker.email}"
  )
}

resource "google_project_iam_member" "dataflow_bigquery_editor" {
  project = "gaming-data-platform-dev"
  role    = "roles/bigquery.dataEditor"

  member = (
    "serviceAccount:${google_service_account.dataflow_payment_worker.email}"
  )
}

resource "google_storage_bucket_iam_member" "dataflow_temp_access" {
  bucket = google_storage_bucket.dataflow_temp.name
  role   = "roles/storage.objectAdmin"

  member = (
    "serviceAccount:${google_service_account.dataflow_payment_worker.email}"
  )
}

resource "google_bigquery_table" "payment_transactions_stream" {
  project    = "gaming-data-platform-dev"
  dataset_id = google_bigquery_dataset.bronze.dataset_id
  table_id   = "payment_transactions_stream"

  deletion_protection = true

  time_partitioning {
    type  = "DAY"
    field = "event_timestamp"
  }

  clustering = [
    "transaction_type",
    "transaction_status"
  ]

  schema = jsonencode([
    {
      name = "transaction_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "player_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "transaction_type"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "amount"
      type = "NUMERIC"
      mode = "REQUIRED"
    },
    {
      name = "currency"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "payment_method"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "transaction_status"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "event_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "ingestion_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "source_system"
      type = "STRING"
      mode = "REQUIRED"
    }
  ])
}
resource "google_project_iam_member" "dataflow_pubsub_viewer" {
  project = "gaming-data-platform-dev"
  role    = "roles/pubsub.viewer"

  member = (
    "serviceAccount:${google_service_account.dataflow_payment_worker.email}"
  )
}
