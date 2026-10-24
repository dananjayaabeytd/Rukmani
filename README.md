<p align="center">
  <img src="logo.webp" alt="Kapruka" width="420">
</p>

<h1 align="center">Rukmani (රුක්මණී) — AI gift concierge for Kapruka</h1>

<p align="center">
  An entry for the <a href="https://www.kapruka.com/contactUs/agentChallenge.html">Kapruka Agent Challenge 2026</a>,
  built on the public <a href="https://mcp.kapruka.com">Kapruka MCP</a>.
</p>

---

## What it is

Rukmani is a chat shopping assistant for [Kapruka.com](https://www.kapruka.com), Sri Lanka's largest online gift shop. She helps customers go from "I'm not sure what to send" to a gift that fits:

- Talks in **Sinhala, Singlish/Tanglish or English**, matching the customer.
- Searches the **live Kapruka catalogue** and shows products as cards.
- Suggests **3 picks** with a reason for each: a safe pick, a "wow" pick and a budget pick.
- Checks **delivery to the customer's city and date**, including the fee and the next available date.

Everything comes from Kapruka's real data through the Kapruka MCP server (`https://mcp.kapruka.com/mcp`). Rukmani never invents products, prices or delivery dates.

## Project structure

| Folder | What's inside | Status |
|---|---|---|
| [`backend/`](backend/) | Python API: FastAPI + LangGraph agent + Kapruka MCP client | Working |
| `frontend/` | Next.js full-screen chat UI | Next |

## How it works

```
Browser (chat UI)
   │  POST /api/chat  ← one message
   ▼                  → Server-Sent Events: reply text, product cards, delivery checks
FastAPI
   ▼
LangGraph agent (Rukmani)  ⇄  tools: search, product details, city lookup, delivery check
   ▼
Kapruka MCP client  →  mcp.kapruka.com/mcp
```

- **The agent cannot place orders by itself.** Checkout will be a step the customer confirms in the UI.
- **Models are swappable profiles** (`budget`, `balanced`, `best`) in [`backend/config/models.yaml`](backend/config/models.yaml), using OpenAI and Groq.

## Quick start

See [`backend/README.md`](backend/README.md). In short:

```bash
cd backend
cp .env.example .env      # add OPENAI_API_KEY and/or GROQ_API_KEY
uv sync
uv run uvicorn kapruka_agent.api.main:app --reload --port 8000
```

## Tech stack

Python 3.11 · FastAPI · LangGraph · LangChain (OpenAI, Groq) · MCP Python SDK · Pydantic · loguru · uv · pytest · ruff

## Author

**dananjayaabeytd** · dananjayaabeytd@gmail.com

---

<sub>Kapruka, the Kapruka logo and the Kapruka catalogue belong to Kapruka Holdings PLC. This is an independent challenge entry built on Kapruka's public MCP.</sub>
