"""
Opens all storage the app needs, for the app's lifetime.

With DATABASE_URL set (Supabase Postgres), everything is durable:
    checkpointer  conversations: messages, cart, checkout, order, summary
    store         long-term memory about each visitor
    chats         the chat list (titles, owners)

Without it, everything lives in memory — handy for tests and local
development, but lost on restart (a warning is logged).

Supabase notes: use the *session pooler* connection string (IPv4,
port 5432) — Cloud Run has no IPv6 route to the direct database host.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres.aio import AsyncPostgresStore
from loguru import logger
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from kapruka_agent.kapruka.models import Money
from kapruka_agent.kapruka.orders import Cart, CartItem, CheckoutDetails, CheckoutQuote, Order
from kapruka_agent.storage.chats import (
    ChatRepository,
    InMemoryChatRepository,
    PostgresChatRepository,
)

# The non-built-in types kept in conversation state. Only these (plus
# LangGraph's own safe types) may be loaded back, so a tampered database
# can't create arbitrary Python objects.
_SAVED_TYPES = [Money, Cart, CartItem, CheckoutDetails, CheckoutQuote, Order]

# Small pool: one Cloud Run instance, and Supabase's free tier allows few connections.
_POOL_SIZE = 5


@dataclass
class Storage:
    checkpointer: BaseCheckpointSaver
    store: BaseStore
    chats: ChatRepository
    durable: bool  # False = in memory only


def _serializer() -> JsonPlusSerializer:
    return JsonPlusSerializer(allowed_msgpack_modules=_SAVED_TYPES)


@asynccontextmanager
async def open_storage(database_url: str | None) -> AsyncIterator[Storage]:
    """Open the database (or in-memory fallback) and create tables if needed."""
    if not database_url:
        logger.warning("DATABASE_URL not set — conversations and memory are kept in memory only")
        yield Storage(
            checkpointer=InMemorySaver(serde=_serializer()),
            store=InMemoryStore(),
            chats=InMemoryChatRepository(),
            durable=False,
        )
        return

    # Settings LangGraph's Postgres classes require (and that work with poolers).
    connection_kwargs = {"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row}
    async with AsyncConnectionPool(
        database_url,
        min_size=1,
        max_size=_POOL_SIZE,
        kwargs=connection_kwargs,
        # Supabase's pooler closes idle connections; test each one before use.
        check=AsyncConnectionPool.check_connection,
        open=False,
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool, serde=_serializer())
        store = AsyncPostgresStore(pool)
        chats = PostgresChatRepository(pool)

        # Create tables on first run; each call is safe to repeat.
        await checkpointer.setup()
        await store.setup()
        await chats.setup()

        logger.info("Connected to Postgres — conversations and memory are durable")
        yield Storage(checkpointer=checkpointer, store=store, chats=chats, durable=True)
