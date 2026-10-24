# Deploying Rukmani

| Part | Host | Live URL |
|---|---|---|
| `frontend/` (Next.js) | **Vercel** | https://rukmani.vercel.app |
| `backend/` (FastAPI) | **Google Cloud Run** (`asia-south1`, Mumbai — closest to Sri Lanka) | https://rukmani-api-240930203956.asia-south1.run.app |

## How it's managed

- **Infrastructure is Terraform** — see [`infra/README.md`](infra/README.md) (first-time setup, everyday changes).
- **Deploys are GitHub Actions** — see [`.github/workflows/`](.github/workflows/):

| Workflow | When | What |
|---|---|---|
| `ci.yml` | Every pull request (and before every deploy) | Backend lint + tests, frontend lint + types + build, Terraform format + validate |
| `deploy.yml` | Push to `main` | Backend: build image → Artifact Registry → Cloud Run → health check. Frontend: Vercel build → production. Only the parts that changed. |
| `terraform.yml` | Changes under `infra/` | Pull request: `terraform plan` in the run summary. `main`: `terraform apply` (in the `production` environment). |

GitHub logs in to Google Cloud with **Workload Identity Federation** — no Google keys are stored anywhere. The only GitHub secrets are `VERCEL_TOKEN` and `SUPABASE_ACCESS_TOKEN`.

## How the backend runs

- **Scales to zero** (free when idle; the first message after a quiet spell takes a few extra seconds). Set `min_instances = 1` in `infra/terraform.tfvars` to keep it warm.
- **At most 1 instance**, so rate limits are exact and costs predictable.
- **API keys and the database URL live in Secret Manager**; the backend's own service account is the only one that can read them.
- **Chats, carts and memory live in Supabase Postgres** (`ap-south-1`, Mumbai, next to Cloud Run), created by Terraform. Nothing is lost when the instance scales to zero.
- **Traces go to Langfuse** once `langfuse_enabled = true` (see `infra/README.md`).

## Logs

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="rukmani-api"' \
  --project rukmani-512609 --limit 50 --freshness=1h
```

A line saying `Model ... failed, trying the next one` means the main model is failing and the fallback is answering — investigate it.

For what the agent did in a turn (prompt, tool calls, tokens, cost), open the trace in Langfuse: filter by session (chat id) or user (visitor id).

## Before judging

- Set `model_profile = "best"` (or `"balanced"`) in `infra/terraform.tfvars` — the budget model's Sinhala/Tamil is weaker.
- Make sure the OpenAI account has credit and a monthly spending limit.
- Optional: `min_instances = 1` so judges never wait for a wake-up.
- Open https://rukmani.vercel.app on a phone over mobile data and run one full chat.
