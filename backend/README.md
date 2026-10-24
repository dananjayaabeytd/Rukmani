# Rukmani backend

FastAPI + LangGraph agent that shops the live Kapruka catalogue through the
[Kapruka MCP](https://mcp.kapruka.com). It streams replies, product cards and delivery checks to the frontend as Server-Sent Events.

## Run it

```bash
cd backend
cp .env.example .env          # then add OPENAI_API_KEY and/or GROQ_API_KEY
uv sync
uv run uvicorn kapruka_agent.api.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs · Health: http://localhost:8000/api/health

## Choose the models

Models are set in [`config/models.yaml`](config/models.yaml) as profiles:

| Profile | Primary → fallbacks | Use it for |
|---|---|---|
| `budget` (default) | Groq `gpt-oss-20b` → OpenAI `gpt-4.1-nano` | Development while credits are low. Weak Sinhala. |
| `balanced` | OpenAI `gpt-5.4-mini` → Groq `gpt-oss-120b` | Real testing and demos. Good Sinhala. |
| `best` | OpenAI `gpt-5.5` → `gpt-5.4-mini` → Groq `gpt-oss-120b` | Judging day. |

Switch with `active_profile` in the YAML, or `MODEL_PROFILE=balanced` in `.env`.

## Check it

```bash
uv run pytest                         # unit tests (no network, no API keys)
uv run python scripts/smoke_kapruka.py   # live read-only calls to Kapruka
uv run ruff check . && uv run ruff format --check .
```

## How the code is organised

Dependencies point one way only: `api → agent → kapruka`.

| Folder | Job |
|---|---|
| `kapruka/` | The only code that talks to Kapruka. `client.py` keeps one MCP connection open, reconnects, and caches catalogue answers. `models.py` holds typed views of Kapruka's JSON. |
| `config/models.yaml` | Model profiles: which model Rukmani uses, with fallbacks. |
| `agent/` | `prompts.py` (Rukmani's persona), `tools.py` (what she can do), `llm.py` (builds the model from the active profile), `graph.py` (the LangGraph loop). |
| `api/` | `main.py` (app + startup), `routes.py` (HTTP endpoints), `events.py` (agent run → UI events), `schemas.py` (request bodies). |

## Design decisions

- **The model cannot place orders.** There is no order tool. Checkout will be a separate endpoint the customer confirms in the UI.
- **Each tool returns two things:** a small summary for the model and full data for the UI. That keeps model tokens low and the cards rich.
- **Catalogue answers are cached for 10 minutes.** Kapruka allows 60 requests/min per IP, and every visitor shares our server's IP.
- **Conversations are kept in memory** (`InMemorySaver`), so they are lost on restart. To keep them across restarts, switch to a SQLite or Postgres checkpointer in `graph.py`.
