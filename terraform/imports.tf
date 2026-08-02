import {
  to = google_storage_bucket.raw
  id = "gaming-data-platform-dev/gaming-data-platform-dev-saeed-raw"
}

import {
  to = google_bigquery_dataset.bronze
  id = "projects/gaming-data-platform-dev/datasets/gaming_bronze"
}

import {
  to = google_bigquery_dataset.silver
  id = "projects/gaming-data-platform-dev/datasets/gaming_silver"
}

import {
  to = google_bigquery_dataset.gold
  id = "projects/gaming-data-platform-dev/datasets/gaming_gold"
}