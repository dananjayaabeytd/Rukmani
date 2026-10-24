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
| `kapruka/` | The only code that talks to Kapruka. `client.py` keeps one MCP connection open, reconnects, and caches catalogue answers. `models.py` holds typed views of Kapruka's JSON. `orders.py` holds the cart, checkout and `place_order`. |
| `config/models.yaml` | Model profiles: which model Rukmani uses, with fallbacks. |
| `agent/` | `prompts.py` (Rukmani's persona), `tools.py` (catalogue tools), `cart_tools.py` (cart + checkout tools), `state.py` (cart/checkout/order saved per conversation), `llm.py` (builds the model from the active profile), `graph.py` (the LangGraph loop). |
| `api/` | `main.py` (app + startup), `routes.py` (HTTP endpoints), `checkout.py` (places the order after Confirm), `events.py` (agent run → UI events), `schemas.py` (request bodies). |

## How checkout works

1. Rukmani adds items with `add_to_cart` / `update_cart_item` / `remove_from_cart`. The cart is saved in the conversation state.
2. With the recipient, address, date and gift message, she calls `prepare_checkout`. It checks delivery **with the whole cart**, which gives the exact fee, and shows a summary card with a **Confirm** button.
3. Only that button calls `POST /api/checkout`, which creates the real Kapruka order and returns the pay link (valid 60 minutes).

## Design decisions

- **The model cannot place orders.** There is no order tool. Only the customer's Confirm click creates one, and the endpoint refuses duplicates.
- **Any cart change cancels a pending checkout**, so the customer never confirms a summary that no longer matches the cart.
- **One tool call at a time** (`parallel_tool_calls=False`), so two cart changes can't overwrite each other.
- **Each tool returns two things:** a small summary for the model and full data for the UI. That keeps model tokens low and the cards rich.
- **Catalogue answers are cached for 10 minutes.** Kapruka allows 60 requests/min per IP, and every visitor shares our server's IP.
- **Conversations are kept in memory** (`InMemorySaver`), so they are lost on restart. To keep them across restarts, switch to a SQLite or Postgres checkpointer in `graph.py`.
