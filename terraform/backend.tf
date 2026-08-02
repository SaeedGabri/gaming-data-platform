terraform {
  backend "gcs" {
    bucket = "gaming-data-platform-dev-saeed-tfstate"
    prefix = "gaming-data-platform/dev"
  }
}