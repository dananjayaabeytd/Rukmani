# Provider settings.
#
# Google: uses your gcloud application-default login locally, and Workload
# Identity Federation (no keys) in GitHub Actions.
# Vercel: reads the API token from the VERCEL_API_TOKEN environment variable.

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "vercel" {
  team = var.vercel_team_id
}
