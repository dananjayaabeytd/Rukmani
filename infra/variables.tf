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

variable "initial_image" {
  description = <<-EOT
    Container image used when the service is first created. After that,
    GitHub Actions deploys new images and Terraform leaves the image alone.
  EOT
  type        = string
}
