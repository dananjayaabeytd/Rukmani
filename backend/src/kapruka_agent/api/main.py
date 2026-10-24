"""
FastAPI application entrypoint.

Run locally (from the backend/ folder):

    uv run uvicorn kapruka_agent.api.main:app --reload --port 8000

API docs: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.llm import build_chat_model
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.api.routes import router
from kapruka_agent.config import get_settings
from kapruka_agent.kapruka import KaprukaClient
from kapruka_agent.log import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build long-lived objects once at startup and close them at shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)

    kapruka = KaprukaClient(
        settings.kapruka_mcp_url,
        cache_ttl_seconds=settings.kapruka_cache_ttl_seconds,
        timeout_seconds=settings.kapruka_timeout_seconds,
    )
    await kapruka.start()

    tools = build_tools(kapruka)
    app.state.kapruka = kapruka
    app.state.agent = build_agent(build_chat_model(settings, tools), tools)

    yield

    await kapruka.stop()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Rukmani — Kapruka gift concierge", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    app.include_router(router)
    return app


app = create_app()
