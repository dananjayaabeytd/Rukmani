# Resources that already existed before Terraform (created by hand during the
# first deploy). Terraform adopts them instead of trying to create duplicates.
# These blocks are harmless after the first apply and document the history.

import {
  to = google_cloud_run_v2_service.api
  id = "projects/${var.project_id}/locations/${var.region}/services/rukmani-api"
}

import {
  for_each = local.secrets
  to       = google_secret_manager_secret.keys[each.key]
  id       = "projects/${var.project_id}/secrets/${each.value}"
}

import {
  to = vercel_project.frontend
  id = "${var.vercel_team_id}/prj_70s0wcTps5dzpjgKalLVsSohOTsj"
}
