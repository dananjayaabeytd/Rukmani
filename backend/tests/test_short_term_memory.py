"""Long chats are summarised (not forgotten), and remembered facts reach the prompt."""

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.store.memory import InMemoryStore

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.graph import AgentMemory, _summary_cut
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.memory import ConversationSummarizer, MemoryBook
from kapruka_agent.memory.models import ExtractedFact
from kapruka_agent.observability import Observability

from .test_events import ScriptedChatModel

VISITOR = "visitor-1234567890"


def test_cut_lands_on_a_customer_message():
    messages = [
        HumanMessage("a", id="1"),
        AIMessage("", tool_calls=[{"name": "search_products", "args": {}, "id": "c1"}], id="2"),
        HumanMessage("b", id="3"),
        AIMessage("reply", id="4"),
        HumanMessage("c", id="5"),
        AIMessage("reply", id="6"),
    ]

    cut = _summary_cut(messages, keep_recent=3)

    assert messages[cut].type == "human"
    assert len(messages) - cut >= 3


async def test_old_messages_are_folded_into_a_summary(fake_kapruka):
    summarizer = ConversationSummarizer(
        RunnableLambda(lambda _: AIMessage("Customer wants roses for wife in Kandy.")),
        Observability(),
    )
    agent = build_agent(
        ScriptedChatModel(replies=iter([AIMessage(f"reply {i}") for i in range(10)])),
        build_tools(fake_kapruka),
        memory=AgentMemory(summarizer=summarizer, summarize_after=6, keep_recent=2),
    )
    config = {"configurable": {"thread_id": "long-chat"}}

    for turn in range(5):
        await agent.ainvoke({"messages": [HumanMessage(f"message {turn}")]}, config)

    state = (await agent.aget_state(config)).values
    assert state["summary"] == "Customer wants roses for wife in Kandy."
    assert len(state["messages"]) < 10  # older messages were removed after summarising


async def test_remembered_facts_are_in_the_prompt(fake_kapruka):
    book = MemoryBook(InMemoryStore())
    await book.remember(
        VISITOR, [ExtractedFact(text="Mother lives in Kandy", category="recipient")]
    )
    prompts: list[str] = []

    def capture(messages):
        prompts.append(messages[0].content)
        return AIMessage("Hello again!")

    agent = build_agent(
        RunnableLambda(capture), build_tools(fake_kapruka), memory=AgentMemory(book=book)
    )
    config = {"configurable": {"thread_id": "t1", "visitor_id": VISITOR}}

    await agent.ainvoke({"messages": [HumanMessage("hi")]}, config)

    assert "Mother lives in Kandy" in prompts[0]
