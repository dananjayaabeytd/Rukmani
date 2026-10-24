# Non-secret settings for the live deployment. API keys are NOT here:
# they live in Secret Manager (see secrets.tf).

project_id        = "rukmani-512609"
region            = "asia-south1"
github_repository = "dananjayaabeytd/Rukmani"
vercel_team_id    = "team_L6FFBTSkQf3NqpU4zETr3yKh"

supabase_organization_id = "ulfyhlbxcswlhlgcteex"

# Set to true after adding values to the langfuse-* secrets.
langfuse_enabled = false

model_profile = "budget"
min_instances = 0

cors_origins = [
  "https://rukmani.vercel.app",
  "https://rukmani-dananjayaabeytd-gmailcoms-projects.vercel.app",
]

initial_image = "asia-south1-docker.pkg.dev/rukmani-512609/cloud-run-source-deploy/rukmani-api@sha256:5ac4e29f78de71c920a5cd88a66fece3e43c577e821adeafea31ba6e8032e903"
