# Where GitHub Actions pushes the backend's container images.

resource "google_artifact_registry_repository" "images" {
  repository_id = "rukmani"
  location      = var.region
  format        = "DOCKER"
  description   = "Rukmani backend images, pushed by GitHub Actions"

  # Keep storage small: only the 10 newest images are kept.
  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }
  cleanup_policies {
    id     = "delete-older"
    action = "DELETE"
    condition {
      tag_state = "ANY"
    }
  }

  depends_on = [google_project_service.apis]
}

locals {
  image_repository = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}
