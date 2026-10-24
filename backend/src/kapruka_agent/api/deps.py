"""
Dependency helpers for routes.

Long-lived objects (the agent, storage, Kapruka client, memory) are built
once at startup in ``main.lifespan`` and kept on ``app.state``. Routes get
them with these helpers via FastAPI's ``Depends``.

The visitor id identifies whose chats and memories these are. The browser
creates it once (a random UUID, kept in local storage) and sends it on every
request in the ``X-Visitor-Id`` header. There's no sign-in: the id itself is
the key to a visitor's chats, so it's long and random.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from kapruka_agent.agent.service import ShoppingAgent
from kapruka_agent.faq import Faq
from kapruka_agent.kapruka import KaprukaClient
from kapruka_agent.memory import MemoryBook
from kapruka_agent.moderation import Moderator
from kapruka_agent.storage import Chat, Storage


def _from_state(request: Request, name: str):
    value = getattr(request.app.state, name, None)
    if value is None:
        raise HTTPException(status_code=503, detail="Server is still starting up")
    return value


def get_agent(request: Request) -> ShoppingAgent:
    return _from_state(request, "agent")


def get_kapruka(request: Request) -> KaprukaClient:
    return _from_state(request, "kapruka")


def get_storage(request: Request) -> Storage:
    return _from_state(request, "storage")


def get_memory(request: Request) -> MemoryBook:
    return _from_state(request, "memory")


def get_moderator(request: Request) -> Moderator:
    return _from_state(request, "moderator")


def get_faq(request: Request) -> Faq:
    return _from_state(request, "faq")


def get_visitor_id(
    x_visitor_id: Annotated[str, Header(min_length=16, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")],
) -> str:
    return x_visitor_id


async def owned_chat(chat_id: str, visitor_id: str, storage: Storage) -> Chat:
    """The chat, if it belongs to this visitor. Otherwise 404 (never reveal others' chats)."""
    chat = await storage.chats.get(chat_id)
    if chat is None or chat.visitor_id != visitor_id:
        raise HTTPException(status_code=404, detail="Chat not found.")
    return chat


Agent = Annotated[ShoppingAgent, Depends(get_agent)]
Kapruka = Annotated[KaprukaClient, Depends(get_kapruka)]
Store = Annotated[Storage, Depends(get_storage)]
Memory = Annotated[MemoryBook, Depends(get_memory)]
Moderation = Annotated[Moderator, Depends(get_moderator)]
FaqAnswers = Annotated[Faq, Depends(get_faq)]
VisitorId = Annotated[str, Depends(get_visitor_id)]
