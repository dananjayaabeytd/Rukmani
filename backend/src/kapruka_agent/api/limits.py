"""
Protection against abuse and runaway cost.

The demo is public, and every message costs LLM credits and Kapruka
requests. These simple in-memory limits keep both under control:

    - per visitor (IP):  a few dozen messages per 10 minutes,
                         a handful of checkout confirmations per hour
    - for everyone:      a daily cap on chat messages

They live in memory, so they reset when the server restarts. That is fine
for one server; with several, move them to Redis.
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException, Request

_SRI_LANKA_TZ = ZoneInfo("Asia/Colombo")
_MAX_TRACKED_VISITORS = 10_000


class SlidingWindowLimiter:
    """Allow at most ``limit`` hits per ``window_seconds`` for each key (e.g. an IP)."""

    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()  # forget hits older than the window
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        if len(self._hits) > _MAX_TRACKED_VISITORS:
            self._forget_idle(now)
        return True

    def _forget_idle(self, now: float) -> None:
        """Drop visitors with no recent hits, so memory stays small."""
        self._hits = defaultdict(
            deque, {k: v for k, v in self._hits.items() if v and now - v[-1] <= self.window}
        )


@dataclass
class DailyLimit:
    """Allow at most ``limit`` hits per day (Sri Lanka date) across all visitors."""

    limit: int
    _day: str = ""
    _count: int = field(default=0)

    def allow(self) -> bool:
        today = datetime.now(_SRI_LANKA_TZ).date().isoformat()
        if today != self._day:
            self._day, self._count = today, 0
        if self._count >= self.limit:
            return False
        self._count += 1
        return True


@dataclass
class Limits:
    """All limits, created once at startup and kept on ``app.state.limits``."""

    chat: SlidingWindowLimiter
    checkout: SlidingWindowLimiter
    daily_chat: DailyLimit
    trust_proxy_headers: bool

    def client_ip(self, request: Request) -> str:
        """The visitor's IP. Behind a hosting proxy, the real IP is in X-Forwarded-For."""
        forwarded = request.headers.get("x-forwarded-for")
        if self.trust_proxy_headers and forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


def _limits(request: Request) -> Limits:
    return request.app.state.limits


def limit_chat(request: Request) -> None:
    """FastAPI dependency for POST /api/chat."""
    limits = _limits(request)
    if not limits.chat.allow(limits.client_ip(request)):
        raise HTTPException(
            status_code=429,
            detail="You're sending messages very quickly. Please wait a few minutes.",
        )
    if not limits.daily_chat.allow():
        raise HTTPException(
            status_code=503,
            detail="Rukmani has helped a lot of people today and is resting. "
            "Please come back tomorrow!",
        )


def limit_checkout(request: Request) -> None:
    """FastAPI dependency for POST /api/checkout."""
    limits = _limits(request)
    if not limits.checkout.allow(limits.client_ip(request)):
        raise HTTPException(
            status_code=429,
            detail="Too many orders from your connection. Please try again in an hour.",
        )
