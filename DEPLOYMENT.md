# Deploying Rukmani

Two parts, two hosts:

| Part | Host | Why |
|---|---|---|
| `backend/` (FastAPI) | **Railway** | Always-on container (no slow "cold start" when a judge opens the link), persistent volume for conversations |
| `frontend/` (Next.js) | **Vercel** | Made for Next.js, global CDN, free tier |

## 1. Backend on Railway

One-time login (opens your browser):

```bash
railway login
```

Create the service and deploy (from the `backend/` folder):

```bash
cd backend
railway init --name rukmani            # creates the project
railway up --detach                    # builds the Dockerfile and deploys
```

In the Railway dashboard for the service:

1. **Variables** — add:
   | Name | Value |
   |---|---|
   | `OPENAI_API_KEY` | your key |
   | `GROQ_API_KEY` | your key |
   | `MODEL_PROFILE` | `budget` now, `balanced` or `best` for judging |
   | `CORS_ORIGINS` | `["https://<your-vercel-domain>"]` (fill in after step 2) |
2. **Volumes** — add a volume mounted at **`/data`**. Conversations live there and survive redeploys.
3. **Networking** — *Generate Domain*. This is your API URL, e.g. `https://rukmani-production.up.railway.app`.

Check it: open `https://<api-domain>/api/health` → `{"status":"ok","kapruka_connected":true}`.

## 2. Frontend on Vercel

```bash
vercel login
cd frontend
vercel link                              # create/link the project
vercel env add NEXT_PUBLIC_API_URL production   # paste the Railway API URL
vercel --prod
```

Then put the Vercel URL into the backend's `CORS_ORIGINS` (step 1.1) and redeploy the backend (`railway up --detach`).

Optional: add a custom domain in Vercel (e.g. `rukmani.yourdomain.lk`) and include it in `CORS_ORIGINS` too.

## 3. Before judging

- Set `MODEL_PROFILE=best` (or `balanced`) on Railway — the budget model's Sinhala/Tamil is weak.
- Make sure the OpenAI account has credit, and set a monthly spending limit in the OpenAI dashboard.
- Rate limits (per visitor and per day) are in `backend/src/kapruka_agent/config.py` and can be overridden with variables, e.g. `CHAT_MESSAGES_PER_DAY=3000`.
- Open the site on a phone over mobile data and run one full chat.
