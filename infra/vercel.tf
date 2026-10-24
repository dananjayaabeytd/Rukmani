# The frontend on Vercel. GitHub Actions builds and deploys it; Terraform
# owns the project and its settings, including where the backend API is —
# taken straight from the Cloud Run service, so the two never drift apart.

resource "vercel_project" "frontend" {
  name      = "rukmani"
  framework = "nextjs"
}

resource "vercel_project_environment_variable" "api_url" {
  project_id = vercel_project.frontend.id
  key        = "NEXT_PUBLIC_API_URL"
  value      = google_cloud_run_v2_service.api.uri
  target     = ["production", "preview"]
  sensitive  = false # a public URL, also visible in the browser
}
