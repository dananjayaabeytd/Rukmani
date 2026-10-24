# Values the GitHub Actions workflows need (also handy to print).

output "api_url" {
  description = "Public URL of the backend."
  value       = google_cloud_run_v2_service.api.uri
}

output "image_repository" {
  description = "Where to push backend images."
  value       = local.image_repository
}

output "workload_identity_provider" {
  description = "For google-github-actions/auth (workload_identity_provider)."
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "deployer_service_account" {
  description = "Service account the deploy workflow uses."
  value       = google_service_account.deployer.email
}

output "terraform_service_account" {
  description = "Service account the Terraform workflow uses."
  value       = google_service_account.terraform.email
}

output "vercel_project_id" {
  description = "For the frontend deploy workflow (VERCEL_PROJECT_ID)."
  value       = vercel_project.frontend.id
}
