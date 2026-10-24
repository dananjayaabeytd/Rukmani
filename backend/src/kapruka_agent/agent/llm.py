"""
Chat model setup, driven by the profiles in ``backend/config/models.yaml``.

A profile names a primary model and fallbacks. If the primary call fails
(outage, rate limit, no credit), the same request is retried on each
fallback in order, so the customer still gets an answer.

Models whose provider has no API key in the environment are skipped, so a
profile also works with just one of the two keys.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import yaml
from langchain_core.language_models import BaseChatModel, LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from kapruka_agent.config import Settings

ChatModel = Runnable[LanguageModelInput, BaseMessage]


# ── What models.yaml looks like ────────────────────────────────────


class ModelSpec(BaseModel):
    """One model entry in a profile."""

    provider: Literal["openai", "groq"]
    model: str
    params: dict[str, Any] = Field(default_factory=dict)  # extra model settings

    def label(self) -> str:
        return f"{self.provider}/{self.model}"


class ModelProfile(BaseModel):
    primary: ModelSpec
    fallbacks: list[ModelSpec] = Field(default_factory=list)


class ModelsConfig(BaseModel):
    active_profile: str
    profiles: dict[str, ModelProfile]


def load_profile(path: Path, name: str | None = None) -> tuple[str, ModelProfile]:
    """Read models.yaml and return the chosen profile (``name``, or the active one)."""
    config = ModelsConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    name = name or config.active_profile
    if name not in config.profiles:
        available = ", ".join(config.profiles)
        raise ValueError(f"Model profile '{name}' not found in {path}. Available: {available}")
    return name, config.profiles[name]


# ── Building the model ─────────────────────────────────────────────


def _create_model(spec: ModelSpec, settings: Settings) -> BaseChatModel | None:
    """Create the chat model for one entry, or None if its API key is missing."""
    if spec.provider == "openai" and settings.openai_api_key:
        return ChatOpenAI(model=spec.model, api_key=settings.openai_api_key, **spec.params)
    if spec.provider == "groq" and settings.groq_api_key:
        return ChatGroq(model=spec.model, api_key=settings.groq_api_key, **spec.params)
    logger.warning("Skipping {} — no API key for {}", spec.label(), spec.provider)
    return None


def build_chat_model(settings: Settings, tools: Sequence[BaseTool]) -> ChatModel:
    """Build the tool-calling chat model for the configured profile."""
    profile_name, profile = load_profile(settings.models_config_path, settings.model_profile)

    models: list[ChatModel] = []
    labels: list[str] = []
    for spec in [profile.primary, *profile.fallbacks]:
        model = _create_model(spec, settings)
        if model is not None:
            models.append(model.bind_tools(tools))
            labels.append(spec.label())

    if not models:
        raise RuntimeError(
            f"No usable model in profile '{profile_name}'. "
            "Add the matching API key(s) to backend/.env."
        )

    logger.info("Model profile '{}': {}", profile_name, " → ".join(labels))
    primary, *fallbacks = models
    return primary.with_fallbacks(fallbacks) if fallbacks else primary
