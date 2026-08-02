resource "google_bigquery_dataset" "bronze" {
  project     = "gaming-data-platform-dev"
  dataset_id  = "gaming_bronze"
  location    = "me-central1"
  description = "Raw ingested source data"

  delete_contents_on_destroy = false

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_bigquery_dataset" "silver" {
  project    = "gaming-data-platform-dev"
  dataset_id = "gaming_silver"
  location   = "me-central1"

  delete_contents_on_destroy = false

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_bigquery_dataset" "gold" {
  project     = "gaming-data-platform-dev"
  dataset_id  = "gaming_gold"
  location    = "me-central1"
  description = "Curated analytics and reporting data"

  delete_contents_on_destroy = false

  lifecycle {
    prevent_destroy = true
  }
}