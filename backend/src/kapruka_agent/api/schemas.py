"""
Request and response bodies for the HTTP API.

Validated by FastAPI at the boundary, so the rest of the code can trust
its inputs. The frontend mirrors these in ``frontend/lib/types.ts``.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """POST /api/chat — one new customer message."""

    # Created by the browser once per conversation; the agent uses it to
    # load earlier messages, so only the new message is sent each time.
    thread_id: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    message: str = Field(min_length=1, max_length=2000)


class CheckoutRequest(BaseModel):
    """POST /api/checkout — the customer tapped Confirm on the checkout summary."""

    thread_id: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")


class HealthResponse(BaseModel):
    """GET /api/health"""

    status: str = "ok"
    kapruka_connected: bool
