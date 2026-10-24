"""
Request and response bodies for the HTTP API.

Validated by FastAPI at the boundary, so the rest of the code can trust
its inputs. The frontend mirrors these in ``frontend/lib/types.ts``.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# Chat ids are created by the browser (UUIDs).
ChatId = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")


class ChatRequest(BaseModel):
    """POST /api/chat — one new customer message."""

    # Created by the browser once per conversation; the agent uses it to
    # load earlier messages, so only the new message is sent each time.
    thread_id: str = ChatId
    message: str = Field(min_length=1, max_length=2000)


class CheckoutRequest(BaseModel):
    """POST /api/checkout — the customer tapped Confirm on the checkout summary."""

    thread_id: str = ChatId


class ChatSummary(BaseModel):
    """One row in the chat list."""

    id: str
    title: str
    updated_at: datetime


class ChatHistory(BaseModel):
    """GET /api/chats/{id} — a saved chat, ready to show."""

    id: str
    title: str
    summary: str | None  # older messages, condensed, when the chat was long
    messages: list[dict[str, Any]]  # same shape as the UI's ChatMessage


class RenameChat(BaseModel):
    """PATCH /api/chats/{id}"""

    title: str = Field(min_length=1, max_length=80)


class RememberedFact(BaseModel):
    """One thing Rukmani remembers about the visitor."""

    id: str
    text: str
    category: str


class HealthResponse(BaseModel):
    """GET /api/health"""

    status: str = "ok"
    kapruka_connected: bool
    durable_storage: bool  # False = conversations are only kept in memory
