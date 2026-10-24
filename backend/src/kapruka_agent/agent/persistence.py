"""
Where conversations are saved: a SQLite file on disk.

Each conversation (messages, cart, checkout, order) is stored under its
``thread_id``, so it survives server restarts and redeploys, as long as
the file is on persistent storage (see the deploy notes in the README).

Only our own cart/order types (plus LangGraph's built-in safe types) may
be loaded back from the file. That stops a tampered database from
creating arbitrary Python objects.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from loguru import logger

from kapruka_agent.kapruka.models import Money
from kapruka_agent.kapruka.orders import Cart, CartItem, CheckoutDetails, CheckoutQuote, Order

# The non-built-in types we keep in the conversation state.
_SAVED_TYPES = [Money, Cart, CartItem, CheckoutDetails, CheckoutQuote, Order]


@asynccontextmanager
async def open_checkpointer(db_path: Path) -> AsyncIterator[AsyncSqliteSaver]:
    """Open (and create if needed) the conversations database for the app's lifetime."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as conn:
        saver = AsyncSqliteSaver(
            conn, serde=JsonPlusSerializer(allowed_msgpack_modules=_SAVED_TYPES)
        )
        await saver.setup()  # creates the tables on first run
        logger.info("Conversations are saved in {}", db_path)
        yield saver
