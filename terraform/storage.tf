resource "google_storage_bucket" "raw" {
  name     = "gaming-data-platform-dev-saeed-raw"
  project  = "gaming-data-platform-dev"
  location = "ME-CENTRAL1"

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false

  encryption {
    google_managed_encryption_enforcement_config {
      restriction_mode = "NotRestricted"
    }

    customer_managed_encryption_enforcement_config {
      restriction_mode = "NotRestricted"
    }

    customer_supplied_encryption_enforcement_config {
      restriction_mode = "FullyRestricted"
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}