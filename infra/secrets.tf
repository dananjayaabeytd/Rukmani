# API keys for the model providers.
#
# Terraform creates the secret "boxes" and controls who may read them, but
# never the key values themselves — those would end up in Terraform's state.
# Add or rotate a value with:
#   printf '%s' "KEY" | gcloud secrets versions add openai-api-key --data-file=-

locals {
  secrets = {
    OPENAI_API_KEY = "openai-api-key"
    GROQ_API_KEY   = "groq-api-key"
  }
}

resource "google_secret_manager_secret" "keys" {
  for_each = local.secrets

  secret_id = each.value
  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

# Only the backend's own service account can read the keys.
resource "google_secret_manager_secret_iam_member" "api_reads_keys" {
  for_each = google_secret_manager_secret.keys

  secret_id = each.value.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}
