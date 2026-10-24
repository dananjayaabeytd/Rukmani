# Terraform and provider versions, and where Terraform keeps its state.
#
# The state lives in a versioned Cloud Storage bucket (created once with
# gcloud — see infra/README.md), so laptops and GitHub Actions share it.

terraform {
  required_version = ">= 1.6"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 8.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = ">= 2.0, < 5.0"
    }
    supabase = {
      source  = "supabase/supabase"
      version = ">= 1.11, < 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.6, < 4.0"
    }
  }

  backend "gcs" {
    bucket = "rukmani-512609-tfstate"
    prefix = "rukmani"
  }
}
