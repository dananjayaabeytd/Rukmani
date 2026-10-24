# Google Cloud APIs the project needs.

locals {
  apis = [
    "run.googleapis.com",                  # Cloud Run (the backend)
    "artifactregistry.googleapis.com",     # container images
    "secretmanager.googleapis.com",        # API keys
    "iam.googleapis.com",                  # service accounts
    "iamcredentials.googleapis.com",       # short-lived tokens for GitHub Actions
    "sts.googleapis.com",                  # Workload Identity Federation
    "cloudresourcemanager.googleapis.com", # project-level IAM
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.apis)

  service            = each.value
  disable_on_destroy = false # never switch an API off by accident
}
