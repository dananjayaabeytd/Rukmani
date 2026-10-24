"""
HTTP routes. Everything except /health needs the X-Visitor-Id header, and a
visitor can only see and change their own chats and memories.

    POST   /api/chat               Send a message; the reply streams back (Server-Sent Events)
    POST   /api/checkout           The customer confirmed the checkout summary: place the order

    GET    /api/chats              The visitor's chats, newest first
    GET    /api/chats/{id}         One chat, rebuilt for the screen
    PATCH  /api/chats/{id}         Rename a chat
    DELETE /api/chats/{id}         Delete a chat and its conversation

    GET    /api/memory             What Rukmani remembers about the visitor
    DELETE /api/memory/{id}        Forget one fact
    DELETE /api/memory             Forget everything

    GET    /api/health             Is the server up, and is Kapruka reachable?

Chat and checkout are rate-limited per visitor IP (see ``limits.py``), and
chat messages pass a safety check first (see ``moderation.py``).
"""

from fastapi import APIRouter, Depends, Response
from sse_starlette import EventSourceResponse

from kapruka_agent.agent.state import get_cart
from kapruka_agent.api.checkout import confirm_checkout
from kapruka_agent.api.deps import (
    Agent,
    Kapruka,
    Memory,
    Moderation,
    Store,
    VisitorId,
    owned_chat,
)
from kapruka_agent.api.events import fixed_reply_events, stream_agent_events
from kapruka_agent.api.history import ui_messages
from kapruka_agent.api.limits import limit_chat, limit_checkout
from kapruka_agent.api.schemas import (
    ChatHistory,
    ChatRequest,
    ChatSummary,
    CheckoutRequest,
    HealthResponse,
    RememberedFact,
    RenameChat,
)
from kapruka_agent.kapruka.orders import Order
from kapruka_agent.storage.chats import title_from_message

router = APIRouter(prefix="/api")


# ── Conversation ───────────────────────────────────────────────────


@router.post("/chat", dependencies=[Depends(limit_chat)])
async def chat(
    body: ChatRequest, agent: Agent, storage: Store, moderator: Moderation, visitor_id: VisitorId
) -> EventSourceResponse:
    # Harmful messages get a fixed reply and never reach the agent (moderation.py).
    if blocked_reply := await moderator.check(body.message):
        return EventSourceResponse(fixed_reply_events(blocked_reply))

    existing = await storage.chats.get(body.thread_id)
    if existing is None:
        # First message of a new chat: list it, titled after the message.
        await storage.chats.create(body.thread_id, visitor_id, title_from_message(body.message))
    else:
        await owned_chat(body.thread_id, visitor_id, storage)
        await storage.chats.touch(body.thread_id)  # moves it to the top of the list

    return EventSourceResponse(stream_agent_events(agent, body.thread_id, visitor_id, body.message))


@router.post("/checkout", dependencies=[Depends(limit_checkout)])
async def checkout(
    body: CheckoutRequest, agent: Agent, kapruka: Kapruka, storage: Store, visitor_id: VisitorId
) -> Order:
    await owned_chat(body.thread_id, visitor_id, storage)
    return await confirm_checkout(agent.graph, kapruka, body.thread_id)


# ── Chat list ──────────────────────────────────────────────────────


@router.get("/chats")
async def list_chats(storage: Store, visitor_id: VisitorId) -> list[ChatSummary]:
    chats = await storage.chats.list_for(visitor_id)
    return [ChatSummary(id=c.id, title=c.title, updated_at=c.updated_at) for c in chats]


@router.get("/chats/{chat_id}")
async def get_chat(
    chat_id: str, agent: Agent, storage: Store, visitor_id: VisitorId
) -> ChatHistory:
    chat = await owned_chat(chat_id, visitor_id, storage)
    state = (await agent.graph.aget_state({"configurable": {"thread_id": chat_id}})).values
    messages = ui_messages(state.get("messages", []))

    # The cart lives in state; show it as the last card so the cart icon is right.
    cart = get_cart(state)
    if not cart.is_empty and messages:
        cart_card = {"kind": "cart", "cart": cart.model_dump(), "total": cart.total.model_dump()}
        messages[-1]["artifacts"] = [*messages[-1]["artifacts"], cart_card]

    return ChatHistory(
        id=chat.id, title=chat.title, summary=state.get("summary"), messages=messages
    )


@router.patch("/chats/{chat_id}", status_code=204)
async def rename_chat(
    chat_id: str, body: RenameChat, storage: Store, visitor_id: VisitorId
) -> Response:
    await owned_chat(chat_id, visitor_id, storage)
    await storage.chats.rename(chat_id, " ".join(body.title.split()))
    return Response(status_code=204)


@router.delete("/chats/{chat_id}", status_code=204)
async def delete_chat(chat_id: str, storage: Store, visitor_id: VisitorId) -> Response:
    await owned_chat(chat_id, visitor_id, storage)
    await storage.checkpointer.adelete_thread(chat_id)  # the conversation itself
    await storage.chats.delete(chat_id)  # and its entry in the list
    return Response(status_code=204)


# ── Long-term memory ───────────────────────────────────────────────


@router.get("/memory")
async def list_memory(memory: Memory, visitor_id: VisitorId) -> list[RememberedFact]:
    facts = await memory.all_facts(visitor_id)
    return [RememberedFact(id=f.id, text=f.text, category=f.category) for f in facts]


@router.delete("/memory/{fact_id}", status_code=204)
async def forget_fact(fact_id: str, memory: Memory, visitor_id: VisitorId) -> Response:
    await memory.forget(visitor_id, fact_id)  # only ever touches this visitor's memory
    return Response(status_code=204)


@router.delete("/memory", status_code=204)
async def forget_everything(memory: Memory, visitor_id: VisitorId) -> Response:
    await memory.forget_all(visitor_id)
    return Response(status_code=204)


# ── Health ─────────────────────────────────────────────────────────


@router.get("/health")
async def health(kapruka: Kapruka, storage: Store) -> HealthResponse:
    return HealthResponse(kapruka_connected=kapruka.is_connected, durable_storage=storage.durable)
