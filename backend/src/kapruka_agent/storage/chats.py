"""
The chat list: which conversations belong to which visitor, with titles.

A "visitor" is an anonymous, random ID the browser creates and keeps, so
customers get their own private chat list without signing in. The
conversation itself (messages, cart, ...) is stored by the LangGraph
checkpointer under the same chat ID; this table only holds the list.

Two implementations with the same interface:
    PostgresChatRepository   production (Supabase)
    InMemoryChatRepository   tests and local development without a database
"""

from datetime import UTC, datetime
from typing import Protocol

from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

_TITLE_MAX = 80


class Chat(BaseModel):
    id: str  # same as the LangGraph thread id
    visitor_id: str
    title: str
    created_at: datetime
    updated_at: datetime


def title_from_message(message: str) -> str:
    """A first title for a new chat: the opening message, shortened."""
    title = " ".join(message.split())
    return title if len(title) <= _TITLE_MAX else title[: _TITLE_MAX - 1].rstrip() + "…"


class ChatRepository(Protocol):
    async def get(self, chat_id: str) -> Chat | None: ...
    async def list_for(self, visitor_id: str, limit: int = 50) -> list[Chat]: ...
    async def create(self, chat_id: str, visitor_id: str, title: str) -> Chat: ...
    async def touch(self, chat_id: str) -> None: ...
    async def rename(self, chat_id: str, title: str) -> None: ...
    async def delete(self, chat_id: str) -> None: ...


# ── Postgres (Supabase) ────────────────────────────────────────────

_SCHEMA = """
create table if not exists chats (
    id          text primary key,
    visitor_id  text not null,
    title       text not null,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);
create index if not exists chats_visitor_recent on chats (visitor_id, updated_at desc);
"""


class PostgresChatRepository:
    def __init__(self, pool: AsyncConnectionPool):
        self._pool = pool

    async def setup(self) -> None:
        """Create the table on first run (safe to call every start)."""
        async with self._pool.connection() as conn:
            await conn.execute(_SCHEMA)

    async def get(self, chat_id: str) -> Chat | None:
        async with self._pool.connection() as conn:
            cur = await conn.execute("select * from chats where id = %s", (chat_id,))
            row = await cur.fetchone()
        return Chat.model_validate(row) if row else None

    async def list_for(self, visitor_id: str, limit: int = 50) -> list[Chat]:
        async with self._pool.connection() as conn:
            cur = await conn.execute(
                "select * from chats where visitor_id = %s order by updated_at desc limit %s",
                (visitor_id, limit),
            )
            rows = await cur.fetchall()
        return [Chat.model_validate(row) for row in rows]

    async def create(self, chat_id: str, visitor_id: str, title: str) -> Chat:
        async with self._pool.connection() as conn:
            cur = await conn.execute(
                "insert into chats (id, visitor_id, title) values (%s, %s, %s) returning *",
                (chat_id, visitor_id, title),
            )
            row = await cur.fetchone()
        return Chat.model_validate(row)

    async def touch(self, chat_id: str) -> None:
        async with self._pool.connection() as conn:
            await conn.execute("update chats set updated_at = now() where id = %s", (chat_id,))

    async def rename(self, chat_id: str, title: str) -> None:
        async with self._pool.connection() as conn:
            await conn.execute("update chats set title = %s where id = %s", (title, chat_id))

    async def delete(self, chat_id: str) -> None:
        async with self._pool.connection() as conn:
            await conn.execute("delete from chats where id = %s", (chat_id,))


# ── In memory (tests, local dev) ───────────────────────────────────


class InMemoryChatRepository:
    def __init__(self) -> None:
        self._chats: dict[str, Chat] = {}

    async def setup(self) -> None:
        return None

    async def get(self, chat_id: str) -> Chat | None:
        return self._chats.get(chat_id)

    async def list_for(self, visitor_id: str, limit: int = 50) -> list[Chat]:
        mine = [c for c in self._chats.values() if c.visitor_id == visitor_id]
        return sorted(mine, key=lambda c: c.updated_at, reverse=True)[:limit]

    async def create(self, chat_id: str, visitor_id: str, title: str) -> Chat:
        now = datetime.now(UTC)
        chat = Chat(id=chat_id, visitor_id=visitor_id, title=title, created_at=now, updated_at=now)
        self._chats[chat_id] = chat
        return chat

    async def touch(self, chat_id: str) -> None:
        if chat := self._chats.get(chat_id):
            self._chats[chat_id] = chat.model_copy(update={"updated_at": datetime.now(UTC)})

    async def rename(self, chat_id: str, title: str) -> None:
        if chat := self._chats.get(chat_id):
            self._chats[chat_id] = chat.model_copy(update={"title": title})

    async def delete(self, chat_id: str) -> None:
        self._chats.pop(chat_id, None)
