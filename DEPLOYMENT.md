# Deploying Rukmani

| Part | Host | Live URL |
|---|---|---|
| `frontend/` (Next.js) | **Vercel** | https://rukmani.vercel.app |
| `backend/` (FastAPI) | **Google Cloud Run** (`asia-south1`, Mumbai — closest to Sri Lanka) | https://rukmani-api-240930203956.asia-south1.run.app |

Google Cloud project: `rukmani-512609`. Vercel project: `rukmani`.

## How the backend runs

- **Scales to zero:** it costs nothing while idle. The first message after a quiet spell takes a few extra seconds while it wakes up.
- **At most 1 instance**, so the rate limits are exact and costs stay predictable.
- **API keys live in Secret Manager** (`openai-api-key`, `groq-api-key`), never in the code or the upload.
- **Saved conversations reset when the instance shuts down** (its disk is temporary). The browser still shows the chat. To keep conversations, move them to a database (e.g. Cloud SQL Postgres with LangGraph's Postgres checkpointer).

## Redeploy the backend

From `backend/` (uploads only the files allowed by `.gcloudignore` — never `.env`):

```bash
gcloud run deploy rukmani-api --source . --project rukmani-512609 --region asia-south1
```

Settings such as secrets, limits and CORS are kept between deploys.

### Change settings without redeploying

```bash
# Switch models, e.g. before judging (budget → balanced → best)
gcloud run services update rukmani-api --project rukmani-512609 --region asia-south1 \
  --update-env-vars MODEL_PROFILE=best

# Allow another frontend address (the list contains commas, so use the ^@^ delimiter)
gcloud run services update rukmani-api --project rukmani-512609 --region asia-south1 \
  --update-env-vars '^@^CORS_ORIGINS=["https://rukmani.vercel.app","https://your-domain.lk"]'
```

### Rotate an API key

```bash
printf '%s' "NEW_KEY" | gcloud secrets versions add openai-api-key --project rukmani-512609 --data-file=-
gcloud run services update rukmani-api --project rukmani-512609 --region asia-south1   # picks up "latest"
```

### Logs

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="rukmani-api"' \
  --project rukmani-512609 --limit 50 --freshness=1h
```

A line saying `Model ... failed, trying the next one` means the main model is failing and the fallback is answering — investigate it.

## Redeploy the frontend

From `frontend/`:

```bash
vercel --prod
```

The API address is the Vercel environment variable `NEXT_PUBLIC_API_URL` (Production). Change it with `vercel env rm` / `vercel env add`, then redeploy.

## Before judging

- Set `MODEL_PROFILE=best` (or `balanced`) — the `budget` model's Sinhala/Tamil is weaker.
- Make sure the OpenAI account has credit and a monthly spending limit.
- Optional: keep one instance warm so judges never wait for a wake-up (costs roughly USD 10–15/month):
  `gcloud run services update rukmani-api --project rukmani-512609 --region asia-south1 --min-instances 1`
- Open https://rukmani.vercel.app on a phone over mobile data and run one full chat.
