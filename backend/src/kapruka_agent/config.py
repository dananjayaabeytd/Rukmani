"""
Application settings.

Every setting can be overridden with an environment variable of the same
name (case-insensitive) or a line in ``backend/.env``. Secrets such as API
keys live ONLY in the environment — never hard-code them.

Which chat models to use is NOT set here: it lives in
``backend/config/models.yaml`` as named profiles (see ``agent/llm.py``).

Example ``.env``::

    OPENAI_API_KEY=sk-...
    GROQ_API_KEY=gsk_...
    MODEL_PROFILE=budget
"""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ folder (this file is backend/src/kapruka_agent/config.py)
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ── LLM providers ──────────────────────────────────────────────
    # Only the keys needed by the active model profile are required.
    openai_api_key: SecretStr | None = None
    groq_api_key: SecretStr | None = None

    # ── Model profiles ─────────────────────────────────────────────
    models_config_path: Path = BACKEND_DIR / "config" / "models.yaml"
    # Overrides `active_profile` in models.yaml when set, e.g. MODEL_PROFILE=best
    model_profile: str | None = None

    # ── Kapruka MCP ────────────────────────────────────────────────
    kapruka_mcp_url: str = "https://mcp.kapruka.com/mcp"
    # Catalogue answers (search, product details, cities) are cached this
    # long. Kapruka allows 60 requests/min per IP, and every visitor shares
    # our server's IP, so caching keeps us well under that limit.
    kapruka_cache_ttl_seconds: int = 600
    kapruka_timeout_seconds: float = 20.0

    # ── Conversations ──────────────────────────────────────────────
    # SQLite file holding every conversation. On a host, put it on a
    # persistent volume so conversations survive redeploys.
    conversations_db: Path = BACKEND_DIR / "data" / "conversations.sqlite"

    # ── Protection against abuse and runaway cost ──────────────────
    chat_messages_per_10_minutes: int = 30  # per visitor IP
    checkouts_per_hour: int = 5  # per visitor IP (Kapruka allows 30/hour for us in total)
    chat_messages_per_day: int = 2000  # for all visitors together — protects LLM credits
    # Most steps (model calls + tool runs) one message may take, so a confused
    # model can't loop and burn credits.
    max_agent_steps: int = 16
    # Behind a hosting proxy (Railway, Fly, Render), the visitor's IP is in
    # X-Forwarded-For. Set to false if the API is exposed directly.
    trust_proxy_headers: bool = True

    # ── API server ─────────────────────────────────────────────────
    # Browser origins allowed to call the API (the frontend's URL).
    # In .env, write it as JSON: CORS_ORIGINS=["https://rukmani.example.com"]
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Load settings once and reuse them everywhere."""
    return Settings()
