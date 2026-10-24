"""
Model setup, driven by the profiles in ``backend/config/models.yaml``.

A profile has two roles, each a primary model plus fallbacks:

    chat     Rukmani herself: talks to the customer and calls tools.
    utility  Cheap background work: memory extraction, conversation summaries.

If a model call fails (outage, rate limit, no credit), the same request is
retried on the next fallback, and the failure is logged. Models whose
provider has no API key in the environment are skipped.
"""

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Literal

import yaml
from langchain_core.language_models import BaseChatModel, LanguageModelInput
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.tracers.schemas import Run
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from kapruka_agent.config import Settings

# Anything that takes chat messages and returns a reply (or structured output).
ChatModel = Runnable[LanguageModelInput, Any]


# ── What models.yaml looks like ────────────────────────────────────


class ModelSpec(BaseModel):
    """One model entry."""

    provider: Literal["openai", "groq"]
    model: str
    params: dict[str, Any] = Field(default_factory=dict)  # extra model settings

    def label(self) -> str:
        return f"{self.provider}/{self.model}"


class ModelChain(BaseModel):
    """A primary model and the fallbacks tried after it, in order."""

    primary: ModelSpec
    fallbacks: list[ModelSpec] = Field(default_factory=list)


class ModelProfile(BaseModel):
    chat: ModelChain
    utility: ModelChain


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


# ── Building models ────────────────────────────────────────────────


def _create_model(spec: ModelSpec, settings: Settings) -> BaseChatModel | None:
    """Create the model for one entry, or None if its API key is missing."""
    if spec.provider == "openai" and settings.openai_api_key:
        return ChatOpenAI(model=spec.model, api_key=settings.openai_api_key, **spec.params)
    if spec.provider == "groq" and settings.groq_api_key:
        return ChatGroq(model=spec.model, api_key=settings.groq_api_key, **spec.params)
    logger.warning("Skipping {} — no API key for {}", spec.label(), spec.provider)
    return None


def _log_failures(model: ChatModel, label: str) -> ChatModel:
    """Log a warning whenever this model fails, so a silent fallback can't hide a problem."""

    def on_error(run: Run) -> None:
        logger.warning("Model {} failed, trying the next one: {}", label, run.error)

    return model.with_listeners(on_error=on_error)


def _build_chain(
    chain: ModelChain,
    settings: Settings,
    role: str,
    prepare: Callable[[BaseChatModel], ChatModel],
) -> ChatModel:
    """Primary + fallbacks, each prepared the same way (tools bound, structured output...)."""
    models: list[ChatModel] = []
    labels: list[str] = []
    for spec in [chain.primary, *chain.fallbacks]:
        model = _create_model(spec, settings)
        if model is not None:
            models.append(_log_failures(prepare(model), spec.label()))
            labels.append(spec.label())

    if not models:
        raise RuntimeError(f"No usable {role} model. Add the matching API key(s) to backend/.env.")
    logger.info("{} model: {}", role.capitalize(), " → ".join(labels))
    primary, *fallbacks = models
    return primary.with_fallbacks(fallbacks) if fallbacks else primary


def build_chat_model(settings: Settings, tools: Sequence[BaseTool]) -> ChatModel:
    """Rukmani's tool-calling model for the configured profile."""
    name, profile = load_profile(settings.models_config_path, settings.model_profile)
    logger.info("Model profile '{}'", name)
    # One tool call at a time: two cart tools running in parallel would both
    # edit the same cart and one change would be lost.
    return _build_chain(
        profile.chat,
        settings,
        "chat",
        lambda model: model.bind_tools(tools, parallel_tool_calls=False),
    )


def build_utility_model(settings: Settings) -> ChatModel:
    """The cheap model for background work, returning plain text."""
    _, profile = load_profile(settings.models_config_path, settings.model_profile)
    return _build_chain(profile.utility, settings, "utility", lambda model: model)


def build_structured_model(settings: Settings, schema: type[BaseModel]) -> ChatModel:
    """The cheap model, returning an instance of ``schema`` instead of text."""
    _, profile = load_profile(settings.models_config_path, settings.model_profile)
    return _build_chain(
        profile.utility,
        settings,
        "structured utility",
        lambda model: model.with_structured_output(schema),
    )
