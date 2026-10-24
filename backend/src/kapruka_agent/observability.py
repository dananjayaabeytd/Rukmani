"""
Langfuse: tracing and prompt management.

Tracing
    Every customer turn is one trace in Langfuse, grouped by chat
    ("session") and customer ("user"): each model call, tool call and memory
    step with its inputs, outputs, latency, tokens and cost.

Prompt management
    Prompts (Rukmani's persona, memory extraction, conversation summary) can
    be edited and versioned in Langfuse — no redeploy needed. The prompts in
    the code are the fallback, used when Langfuse is off, unreachable, or the
    prompt hasn't been created there yet. Create them in Langfuse with the
    names in PROMPT_NAMES and the label "production".

Everything here is a no-op when LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY
aren't set, so the app runs fine without Langfuse.
"""

from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langfuse.model import TemplateParser
from loguru import logger

from kapruka_agent.config import Settings

# Langfuse prompt names (create these in Langfuse to override the code versions).
PROMPT_NAMES = {
    "persona": "rukmani-persona",
    "memory_extract": "rukmani-memory-extract",
    "summary": "rukmani-conversation-summary",
}

# Prompts are cached in the app for this long, so Langfuse isn't called every turn.
_PROMPT_CACHE_SECONDS = 300


class Observability:
    """Tracing callbacks, trace attributes and prompts — or no-ops when Langfuse is off."""

    def __init__(self, settings: Settings | None = None):
        """Without settings (tests, scripts), tracing is off and prompts come from code."""
        self._public_key = settings.langfuse_public_key if settings else None
        self._client: Langfuse | None = None
        if settings and settings.langfuse_public_key and settings.langfuse_secret_key:
            self._client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key.get_secret_value(),
                base_url=settings.langfuse_base_url,
                environment=settings.environment,
            )
            logger.info("Langfuse tracing on ({})", settings.langfuse_base_url)
        else:
            logger.info("Langfuse not configured — tracing off, prompts from code")

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def callbacks(self) -> list[BaseCallbackHandler]:
        """LangChain callbacks that send this run to Langfuse (empty when off)."""
        if not self._client:
            return []
        return [CallbackHandler(public_key=self._public_key)]

    @staticmethod
    def trace_metadata(chat_id: str, visitor_id: str, tags: list[str]) -> dict[str, Any]:
        """Run metadata that Langfuse turns into the trace's session, user and tags."""
        return {
            "langfuse_session_id": chat_id,
            "langfuse_user_id": visitor_id,
            "langfuse_tags": tags,
        }

    def prompt(self, key: str, fallback: str, **variables: Any) -> str:
        """The prompt from Langfuse (or the code fallback), with {{variables}} filled in."""
        if self._client:
            try:
                prompt = self._client.get_prompt(
                    PROMPT_NAMES[key], fallback=fallback, cache_ttl_seconds=_PROMPT_CACHE_SECONDS
                )
                return prompt.compile(**variables)
            except Exception as exc:  # Langfuse down → never break the chat
                logger.warning("Langfuse prompt {} unavailable, using code version: {}", key, exc)
        return TemplateParser.compile_template(fallback, variables)

    def shutdown(self) -> None:
        """Send any traces still buffered (call when the app stops)."""
        if self._client:
            self._client.shutdown()
