# The database: a Supabase Postgres project that keeps every chat, its cart
# and checkout (LangGraph checkpoints), the chat list, and long-term memory.
#
# Terraform creates the project with a random password and writes the
# connection string into Secret Manager ("database-url"), where Cloud Run
# reads it. Note: the password is therefore in Terraform's state, which is
# why the state bucket is private.

resource "random_password" "database" {
  length  = 32
  special = false # keeps the connection string free of characters to escape
}

resource "supabase_project" "db" {
  organization_id   = var.supabase_organization_id
  name              = "rukmani"
  database_password = random_password.database.result
  region            = var.supabase_region
}

# Supabase's connection pooler. Cloud Run has no IPv6, and the direct
# database host is IPv6-only, so the backend connects through the pooler.
data "supabase_pooler" "db" {
  project_ref = supabase_project.db.id
}

locals {
  # The pooler gives a URL like postgresql://postgres.<ref>@<host>:6543/postgres
  # (possibly with a password placeholder). Take its user, host and database,
  # and build the session-mode URL (port 5432) with the real password —
  # LangGraph's checkpointer needs session mode.
  pooler_parts = regex(
    "^postgres(?:ql)?://([^:@/]+)(?::[^@]*)?@([^:/]+)(?::[0-9]+)?/([^?]+)",
    values(data.supabase_pooler.db.url)[0],
  )
  database_url = format(
    "postgresql://%s:%s@%s:5432/%s",
    local.pooler_parts[0],
    random_password.database.result,
    local.pooler_parts[1],
    local.pooler_parts[2],
  )
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.keys["DATABASE_URL"].id
  secret_data = local.database_url
}
