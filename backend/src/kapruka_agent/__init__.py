"""Rukmani — an AI gift concierge for Kapruka.

Package layout (dependencies point one way only: api → agent → kapruka):

    config.py   Settings loaded from environment variables / .env
    log.py      Logging setup (loguru)
    kapruka/    Talks to the Kapruka MCP server. Knows nothing about the agent.
    agent/      The LangGraph agent: persona prompt, tools, graph.
    api/        FastAPI app: HTTP routes and the SSE event stream for the UI.
"""
