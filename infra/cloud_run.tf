# The backend: a Cloud Run service running the Docker image from backend/.
#
# Terraform owns the service's SETTINGS (scaling, env vars, secrets, size).
# GitHub Actions owns the IMAGE: each push to main builds and deploys a new
# one, so Terraform ignores image changes to avoid undoing a deploy.

# The identity the backend runs as. It can read the API keys and nothing else.
resource "google_service_account" "api" {
  account_id   = "rukmani-api"
  display_name = "Rukmani backend (Cloud Run runtime)"
}

resource "google_cloud_run_v2_service" "api" {
  name     = "rukmani-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account                  = google_service_account.api.email
    timeout                          = "300s" # long enough for a streamed reply
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = var.min_instances
      # One instance keeps rate limits exact and costs predictable.
      max_instance_count = 1
    }

    containers {
      image = var.initial_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
        cpu_idle          = true # only pay for CPU while handling requests
        startup_cpu_boost = true # faster wake-up from zero
      }

      env {
        name  = "MODEL_PROFILE"
        value = var.model_profile
      }
      env {
        name  = "LOG_LEVEL"
        value = "INFO"
      }
      env {
        name  = "CORS_ORIGINS"
        value = jsonencode(var.cors_origins)
      }

      # API keys come from Secret Manager, never from plain env values.
      dynamic "env" {
        for_each = local.secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.keys[env.key].secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image, # deployed by GitHub Actions
      client,
      client_version,
    ]
  }

  depends_on = [google_secret_manager_secret_iam_member.api_reads_keys]
}

# Anyone may call the API (the browser talks to it directly). Abuse is
# limited by the app's own rate limits.
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.api.name
  location = google_cloud_run_v2_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
