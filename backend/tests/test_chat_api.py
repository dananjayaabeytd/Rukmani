"""The chat list API: list, reopen, rename, delete — and visitors can't touch others' chats."""

import json

import httpx
import pytest
from fastapi import FastAPI
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.service import ShoppingAgent
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.api.history import ui_messages
from kapruka_agent.api.limits import DailyLimit, Limits, SlidingWindowLimiter
from kapruka_agent.api.routes import router
from kapruka_agent.memory import MemoryBook
from kapruka_agent.observability import Observability
from kapruka_agent.storage import Storage
from kapruka_agent.storage.chats import InMemoryChatRepository

from .test_events import ScriptedChatModel

ALICE = {"X-Visitor-Id": "alice-visitor-0001"}
BOB = {"X-Visitor-Id": "bob-visitor-000002"}


@pytest.fixture
def client(fake_kapruka):
    """The real routes, with in-memory storage and a scripted model (no network)."""
    storage = Storage(
        checkpointer=InMemorySaver(),
        store=InMemoryStore(),
        chats=InMemoryChatRepository(),
        durable=False,
    )
    model = ScriptedChatModel(replies=iter([AIMessage(f"Reply {i}") for i in range(20)]))
    graph = build_agent(model, build_tools(fake_kapruka), storage.checkpointer)

    app = FastAPI()
    app.include_router(router)
    app.state.storage = storage
    app.state.memory = MemoryBook(storage.store)
    app.state.agent = ShoppingAgent(graph, Observability())
    app.state.kapruka = fake_kapruka
    app.state.limits = Limits(
        chat=SlidingWindowLimiter(100, 600),
        checkout=SlidingWindowLimiter(100, 3600),
        daily_chat=DailyLimit(1000),
        trust_proxy_headers=False,
    )
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def _say(client, chat_id: str, text: str, headers=ALICE) -> list[dict]:
    response = await client.post(
        "/api/chat", json={"thread_id": chat_id, "message": text}, headers=headers
    )
    return [json.loads(line[5:]) for line in response.text.splitlines() if line.startswith("data:")]


async def test_first_message_creates_a_titled_chat(client):
    await _say(client, "chat-0001", "A birthday cake for my mother")

    chats = (await client.get("/api/chats", headers=ALICE)).json()

    assert [c["title"] for c in chats] == ["A birthday cake for my mother"]


async def test_reopening_a_chat_shows_its_messages(client):
    await _say(client, "chat-0001", "Hello there")

    history = (await client.get("/api/chats/chat-0001", headers=ALICE)).json()

    assert [m["role"] for m in history["messages"]] == ["user", "assistant"]
    assert history["messages"][1]["text"] == "Reply 0"


async def test_rename_and_delete(client):
    await _say(client, "chat-0001", "Hello there")

    await client.patch("/api/chats/chat-0001", json={"title": "Amma's birthday"}, headers=ALICE)
    assert (await client.get("/api/chats", headers=ALICE)).json()[0]["title"] == "Amma's birthday"

    assert (await client.delete("/api/chats/chat-0001", headers=ALICE)).status_code == 204
    assert (await client.get("/api/chats", headers=ALICE)).json() == []
    assert (await client.get("/api/chats/chat-0001", headers=ALICE)).status_code == 404


async def test_visitors_cannot_see_or_change_each_others_chats(client):
    await _say(client, "chat-0001", "Hello there")

    assert (await client.get("/api/chats", headers=BOB)).json() == []
    assert (await client.get("/api/chats/chat-0001", headers=BOB)).status_code == 404
    assert (await client.delete("/api/chats/chat-0001", headers=BOB)).status_code == 404
    rename = await client.patch("/api/chats/chat-0001", json={"title": "x"}, headers=BOB)
    assert rename.status_code == 404
    hijack = await client.post(
        "/api/chat", json={"thread_id": "chat-0001", "message": "hi"}, headers=BOB
    )
    assert hijack.status_code == 404


async def test_requests_without_a_visitor_id_are_refused(client):
    response = await client.get("/api/chats")

    assert response.status_code == 422


def test_history_groups_tool_cards_into_one_reply():
    messages = [
        HumanMessage("cake for amma", id="h1"),
        AIMessage("", tool_calls=[{"name": "search_products", "args": {}, "id": "c1"}], id="a1"),
        ToolMessage("...", tool_call_id="c1", artifact={"kind": "products", "products": []}),
        AIMessage("Here are 3 picks", id="a2"),
    ]

    bubbles = ui_messages(messages)

    assert [b["role"] for b in bubbles] == ["user", "assistant"]
    assert bubbles[1]["artifacts"][0]["kind"] == "products"
    assert bubbles[1]["text"] == "Here are 3 picks"
