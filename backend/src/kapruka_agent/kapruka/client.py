"""
Kapruka MCP client — the ONLY module that talks to mcp.kapruka.com.

What it does:
    - Keeps one long-lived MCP connection open (a call on an open connection
      takes ~0.3 s; opening a new connection per call costs ~1.5 s more).
    - Reconnects automatically if the connection breaks.
    - Always asks Kapruka for JSON and returns it as a Python dict.
    - Caches catalogue answers for a few minutes to stay under Kapruka's
      rate limit (60 requests/min per IP, shared by all our visitors).

When Kapruka answers with plain text instead of JSON — an error such as
"Error: ..." or "No products found for '...'" — ``call()`` raises
``KaprukaError`` with that text, so callers can show it to the model.
"""

import asyncio
import json
import time
from typing import Any

from loguru import logger
from mcp import Client

# Tools whose answers are the same for every customer, so they are safe to
# cache. ``kapruka_check_delivery`` is NOT here: its answer changes during the
# day (same-day cutoffs, slots filling up).
_CACHEABLE_TOOLS = frozenset(
    {
        "kapruka_search_products",
        "kapruka_get_product",
        "kapruka_list_delivery_cities",
        "kapruka_list_categories",
    }
)
_MAX_CACHE_ENTRIES = 1000
_RECONNECT_DELAY_SECONDS = 2.0

_UNREACHABLE_MESSAGE = "Kapruka is not reachable right now. Please try again in a moment."


class KaprukaError(Exception):
    """Kapruka returned an error or a 'no results' message instead of data."""


class KaprukaClient:
    """Async client for the Kapruka MCP server.

    Usage::

        kapruka = KaprukaClient("https://mcp.kapruka.com/mcp")
        await kapruka.start()
        data = await kapruka.call("kapruka_search_products", q="birthday cake")
        await kapruka.stop()
    """

    def __init__(self, url: str, cache_ttl_seconds: int = 600, timeout_seconds: float = 20.0):
        self._url = url
        self._cache_ttl = cache_ttl_seconds
        self._timeout = timeout_seconds

        self._session: Client | None = None
        self._connected = asyncio.Event()  # set while a connection is open
        self._reconnect = asyncio.Event()  # set by a failed call to request a fresh connection
        self._stopping = asyncio.Event()
        self._owner_task: asyncio.Task[None] | None = None

        # cache key -> (time stored, data)
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    @property
    def is_connected(self) -> bool:
        return self._connected.is_set()

    # ── Lifecycle ──────────────────────────────────────────────────

    async def start(self) -> None:
        """Open the connection in the background and wait briefly for it.

        If Kapruka is down at startup we log a warning instead of crashing;
        the background task keeps retrying until it connects.
        """
        self._owner_task = asyncio.create_task(self._keep_connected(), name="kapruka-mcp")
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=self._timeout)
        except TimeoutError:
            logger.warning("Kapruka MCP not connected yet — will keep retrying in the background")

    async def stop(self) -> None:
        """Close the connection and stop the background task."""
        self._stopping.set()
        self._reconnect.set()  # wakes the background task so it can exit
        if self._owner_task:
            await self._owner_task

    async def _keep_connected(self) -> None:
        """Own the MCP connection for the whole lifetime of the app.

        The MCP SDK requires a connection to be opened and closed by the
        same asyncio task. So this single background task does both, and
        reopens the connection whenever a call reports that it broke.
        """
        while not self._stopping.is_set():
            try:
                async with Client(self._url, read_timeout_seconds=self._timeout) as session:
                    self._session = session
                    self._connected.set()
                    logger.info("Connected to Kapruka MCP at {}", self._url)
                    # Wait here until a call asks for a reconnect, or the app stops.
                    await self._reconnect.wait()
            except Exception as exc:
                logger.warning("Kapruka MCP connection failed: {}", exc)
                await asyncio.sleep(_RECONNECT_DELAY_SECONDS)  # don't hammer the server
            finally:
                self._session = None
                self._connected.clear()
                self._reconnect.clear()

    # ── Calling tools ──────────────────────────────────────────────

    async def call(self, tool: str, **params: Any) -> dict[str, Any]:
        """Call a Kapruka MCP tool and return its JSON answer as a dict.

        Arguments left as ``None`` are not sent, so Kapruka applies its own
        defaults for them.

        Raises:
            KaprukaError: Kapruka is unreachable, or answered with an error
                or "no results" message. The message is safe to show.
        """
        params = {key: value for key, value in params.items() if value is not None}
        params["response_format"] = "json"

        cache_key = f"{tool}:{json.dumps(params, sort_keys=True)}"
        if (cached := self._cache_get(cache_key)) is not None:
            return cached

        text = await self._call_text(tool, params)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            raise KaprukaError(text.strip() or "Kapruka returned an empty answer.") from None

        if tool in _CACHEABLE_TOOLS:
            self._cache_put(cache_key, data)
        return data

    async def _call_text(self, tool: str, params: dict[str, Any]) -> str:
        """Send one tool call and return the raw text Kapruka answered with."""
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=self._timeout)
        except TimeoutError:
            raise KaprukaError(_UNREACHABLE_MESSAGE) from None

        session = self._session
        if session is None:
            raise KaprukaError(_UNREACHABLE_MESSAGE)

        started = time.perf_counter()
        try:
            # Every Kapruka tool takes its arguments wrapped in a "params" object.
            result = await session.call_tool(tool, {"params": params})
        except Exception as exc:
            logger.warning("Kapruka call {} failed: {} — reconnecting", tool, exc)
            self._reconnect.set()
            raise KaprukaError(_UNREACHABLE_MESSAGE) from exc

        logger.debug("Kapruka {} took {:.0f} ms", tool, (time.perf_counter() - started) * 1000)
        text = "".join(getattr(block, "text", "") for block in result.content)
        if result.is_error:
            raise KaprukaError(text.strip() or f"Kapruka could not run {tool}.")
        return text

    # ── Cache helpers ──────────────────────────────────────────────

    def _cache_get(self, key: str) -> dict[str, Any] | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        stored_at, data = entry
        if time.monotonic() - stored_at > self._cache_ttl:
            del self._cache[key]
            return None
        return data

    def _cache_put(self, key: str, data: dict[str, Any]) -> None:
        if len(self._cache) >= _MAX_CACHE_ENTRIES:
            # Drop expired entries first; if the cache is still full, start over.
            now = time.monotonic()
            self._cache = {k: v for k, v in self._cache.items() if now - v[0] <= self._cache_ttl}
            if len(self._cache) >= _MAX_CACHE_ENTRIES:
                self._cache.clear()
        self._cache[key] = (time.monotonic(), data)
