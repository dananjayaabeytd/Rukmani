"""End-to-end through the graph with a scripted model: the UI gets tool, artifact, token, done."""

import json
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.service import ShoppingAgent
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.api.events import stream_agent_events
from kapruka_agent.observability import Observability


class ScriptedChatModel(BaseChatModel):
    """Returns pre-written replies in order, one per model call. No network."""

    replies: Iterator[AIMessage]

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=next(self.replies))])


async def test_stream_emits_tool_artifact_tokens_and_done(fake_kapruka):
    # Turn 1: the model asks for a search. Turn 2: it answers in text.
    model = ScriptedChatModel(
        replies=iter(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "search_products", "args": {"query": "cake"}, "id": "call_1"}
                    ],
                ),
                AIMessage(content="Here are three lovely cakes!"),
            ]
        )
    )
    agent = ShoppingAgent(build_agent(model, build_tools(fake_kapruka)), Observability())

    events = [
        json.loads(e["data"])
        async for e in stream_agent_events(agent, "thread-123", "visitor-1234567890", "cake ekak")
    ]
    types = [e["type"] for e in events]

    assert types[0] == "tool"
    assert events[1]["artifact"]["kind"] == "products"
    assert "".join(e["text"] for e in events if e["type"] == "token") == (
        "Here are three lovely cakes!"
    )
    assert types[-1] == "done"


async def test_an_empty_reply_becomes_a_friendly_error(fake_kapruka):
    agent = ShoppingAgent(
        build_agent(ScriptedChatModel(replies=iter([AIMessage("")])), build_tools(fake_kapruka)),
        Observability(),
    )

    events = [
        json.loads(e["data"])
        async for e in stream_agent_events(agent, "thread-456", "visitor-1234567890", "hi")
    ]

    assert [e["type"] for e in events] == ["error", "done"]
