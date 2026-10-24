# Inputs. Values are in terraform.tfvars (nothing secret lives there).

variable "project_id" {
  description = "Google Cloud project that hosts the backend."
  type        = string
}

variable "region" {
  description = "Google Cloud region. asia-south1 (Mumbai) is the closest to Sri Lanka."
  type        = string
}

variable "github_repository" {
  description = "GitHub repo (owner/name) allowed to deploy through Workload Identity Federation."
  type        = string
}

variable "vercel_team_id" {
  description = "Vercel team (scope) that owns the frontend project."
  type        = string
}

variable "model_profile" {
  description = "Model profile from backend/config/models.yaml: budget, balanced or best."
  type        = string
  default     = "budget"

  validation {
    condition     = contains(["budget", "balanced", "best"], var.model_profile)
    error_message = "model_profile must be budget, balanced or best."
  }
}

variable "min_instances" {
  description = "Instances kept warm. 0 = scale to zero (cheapest); 1 = no wake-up delay."
  type        = number
  default     = 0
}

variable "cors_origins" {
  description = "Browser origins allowed to call the API (the frontend's URLs)."
  type        = list(string)
}

variable "supabase_organization_id" {
  description = "Supabase organization slug (in the dashboard URL: supabase.com/dashboard/org/<slug>)."
  type        = string

  validation {
    condition     = var.supabase_organization_id != "CHANGE_ME"
    error_message = "Set supabase_organization_id in terraform.tfvars to your Supabase organization slug."
  }
}

variable "supabase_region" {
  description = "Supabase region. ap-south-1 (Mumbai) sits next to the Cloud Run region."
  type        = string
  default     = "ap-south-1"
}

variable "langfuse_enabled" {
  description = "Turn on Langfuse tracing. Add values to the two langfuse-* secrets first."
  type        = bool
  default     = false
}

variable "langfuse_base_url" {
  description = "Langfuse host (EU cloud by default; https://us.cloud.langfuse.com for US)."
  type        = string
  default     = "https://cloud.langfuse.com"
}

variable "initial_image" {
  description = <<-EOT
    Container image used when the service is first created. After that,
    GitHub Actions deploys new images and Terraform leaves the image alone.
  EOT
  type        = string
}
