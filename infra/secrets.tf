# API keys for the model providers.
#
# Terraform creates the secret "boxes" and controls who may read them, but
# never the key values themselves — those would end up in Terraform's state.
# Add or rotate a value with:
#   printf '%s' "KEY" | gcloud secrets versions add openai-api-key --data-file=-

#
# The one exception is "database-url": Terraform creates the database too,
# so it writes that value itself (see supabase.tf).

locals {
  model_keys = {
    OPENAI_API_KEY = "openai-api-key"
    GROQ_API_KEY   = "groq-api-key"
  }
  langfuse_keys = {
    LANGFUSE_PUBLIC_KEY = "langfuse-public-key"
    LANGFUSE_SECRET_KEY = "langfuse-secret-key"
  }

  # Every secret box (env var name => secret name).
  secrets = merge(local.model_keys, local.langfuse_keys, { DATABASE_URL = "database-url" })

  # The ones the backend reads. Langfuse joins once its keys have been added
  # (langfuse_enabled), because Cloud Run refuses a secret with no value yet.
  service_secrets = merge(
    local.model_keys,
    { DATABASE_URL = "database-url" },
    var.langfuse_enabled ? local.langfuse_keys : {},
  )
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
