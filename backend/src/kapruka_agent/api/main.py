"""
FastAPI application entrypoint.

Run locally (from the backend/ folder):

    uv run uvicorn kapruka_agent.api.main:app --reload --port 8000

API docs: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.graph import AgentMemory
from kapruka_agent.agent.llm import build_chat_model, build_structured_model, build_utility_model
from kapruka_agent.agent.prompts import PERSONA
from kapruka_agent.agent.service import ShoppingAgent
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.api.limits import DailyLimit, Limits, SlidingWindowLimiter
from kapruka_agent.api.routes import router
from kapruka_agent.config import Settings, get_settings
from kapruka_agent.kapruka import KaprukaClient
from kapruka_agent.log import setup_logging
from kapruka_agent.memory import ConversationSummarizer, MemoryBook, MemoryExtractor
from kapruka_agent.memory.models import ExtractionResult
from kapruka_agent.observability import Observability
from kapruka_agent.storage import open_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build long-lived objects once at startup and close them at shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)
    observability = Observability(settings)

    kapruka = KaprukaClient(
        settings.kapruka_mcp_url,
        cache_ttl_seconds=settings.kapruka_cache_ttl_seconds,
        timeout_seconds=settings.kapruka_timeout_seconds,
    )
    await kapruka.start()

    database_url = settings.database_url.get_secret_value() if settings.database_url else None
    async with open_storage(database_url) as storage:
        memory = MemoryBook(storage.store, max_facts=settings.max_memory_facts)
        tools = build_tools(kapruka)
        graph = build_agent(
            build_chat_model(settings, tools),
            tools,
            storage.checkpointer,
            memory=AgentMemory(
                book=memory,
                summarizer=ConversationSummarizer(build_utility_model(settings), observability),
                summarize_after=settings.summarize_after_messages,
                keep_recent=settings.keep_recent_messages,
                recall_limit=settings.recalled_memory_facts,
            ),
            persona=lambda: observability.prompt("persona", PERSONA),
        )
        extractor = MemoryExtractor(
            build_structured_model(settings, ExtractionResult), memory, observability
        )

        app.state.kapruka = kapruka
        app.state.storage = storage
        app.state.memory = memory
        app.state.agent = ShoppingAgent(graph, observability, extractor, settings.max_agent_steps)
        app.state.limits = _build_limits(settings)

        yield

    await kapruka.stop()
    observability.shutdown()  # send any traces still buffered


def _build_limits(settings: Settings) -> Limits:
    return Limits(
        chat=SlidingWindowLimiter(settings.chat_messages_per_10_minutes, window_seconds=600),
        checkout=SlidingWindowLimiter(settings.checkouts_per_hour, window_seconds=3600),
        daily_chat=DailyLimit(settings.chat_messages_per_day),
        trust_proxy_headers=settings.trust_proxy_headers,
    )


def _start_error_monitoring(settings: Settings) -> None:
    """Report unexpected errors to Sentry, if a DSN is configured.

    Customers' messages and details are personal, so Sentry is told not to
    collect personal data, and no performance tracing is sent.
    """
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn.get_secret_value(),
            send_default_pii=False,
            traces_sample_rate=0.0,
        )


def create_app() -> FastAPI:
    settings = get_settings()
    _start_error_monitoring(settings)
    app = FastAPI(title="Rukmani — Kapruka gift concierge", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-Visitor-Id"],
    )
    app.include_router(router)
    return app


app = create_app()
