# Infrastructure (Terraform)

Everything Rukmani runs on, as code:

| File | What it manages |
|---|---|
| `apis.tf` | Google Cloud APIs the project needs |
| `artifact_registry.tf` | Docker image repository (keeps the 10 newest images) |
| `secrets.tf` | Secret Manager entries for the API keys, and who may read them (never the key values) |
| `cloud_run.tf` | The backend service: scaling, size, env vars, secrets, public access, its own service account |
| `github_actions.tf` | Keyless login for GitHub Actions (Workload Identity Federation) + the `deployer` and `terraform` accounts |
| `vercel.tf` | The Vercel project and its `NEXT_PUBLIC_API_URL`, taken straight from Cloud Run |
| `imports.tf` | Adopts the resources that were created by hand before Terraform |

Settings (no secrets) are in `terraform.tfvars`. State is kept in the versioned bucket `gs://rukmani-512609-tfstate`.

## Who changes what

- **Terraform** owns the settings: scaling, env vars, secrets, permissions, the Vercel project.
- **GitHub Actions** (`.github/workflows/deploy.yml`) owns the code that runs: each push to `main` deploys a new backend image and a new frontend build. Terraform ignores image changes, so the two never fight.

## First-time setup (once)

1. **Vercel token:** in Vercel go to *Account Settings → Tokens → Create*, with scope = your team. Copy it.
2. **Local token:** create `infra/.env` (it's gitignored) with one line:
   `VERCEL_API_TOKEN=<the token>`
3. **Let Terraform own the API URL:** remove the variable that was added by hand, so Terraform can create it (the live site keeps working; it's only read at build time):

   | Windows PowerShell | bash / macOS / Linux |
   |---|---|
   | `cd frontend; vercel env rm NEXT_PUBLIC_API_URL production --yes; cd ..` | `cd frontend && vercel env rm NEXT_PUBLIC_API_URL production --yes && cd ..` |

4. **Apply** (review the plan first: it should import 4 — Cloud Run, 2 secrets, the Vercel project — create ~31, change 1 — the service account — and destroy 0):

   Windows PowerShell:
   ```powershell
   cd infra
   # Load VERCEL_API_TOKEN from .env into this terminal only (nothing is printed)
   Get-Content .env | ForEach-Object { $name, $value = $_ -split '=', 2; if ($name) { Set-Item "env:$name" $value } }
   terraform init
   terraform plan
   terraform apply
   ```

   bash / macOS / Linux:
   ```bash
   cd infra
   set -a; . ./.env; set +a      # loads VERCEL_API_TOKEN into this terminal
   terraform init
   terraform plan
   terraform apply
   ```
5. **GitHub:** in the repo go to *Settings → Secrets and variables → Actions → New repository secret*, name `VERCEL_TOKEN`, value = the same token. Optionally, under *Settings → Environments*, create `production` with required reviewers, so infrastructure changes wait for your approval.
6. Push to `main`. The **Deploy** workflow builds and deploys both apps.

## Everyday changes

- **Switch models** (e.g. before judging): set `model_profile = "best"` in `terraform.tfvars`, open a PR (the plan shows in the Terraform run), merge → applied.
- **Keep one instance warm:** `min_instances = 1` (≈ USD 10–15/month).
- **Add a domain:** add it to `cors_origins`.
- **Rotate an API key:** `printf '%s' "NEW_KEY" | gcloud secrets versions add openai-api-key --project rukmani-512609 --data-file=-`. The service reads `latest` on its next start; redeploy to switch now.

## Notes

- The images from the very first manual deploy live in the `cloud-run-source-deploy` repository, which Terraform doesn't manage. Delete it once a GitHub deploy has succeeded.
- After the first apply, the service runs as `rukmani-api@…` instead of the default compute account. That account can only read the two API key secrets.
