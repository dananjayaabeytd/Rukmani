"""
The agent graph (LangGraph).

It is the standard tool-calling loop:

    START → agent ──(model asked for tools?)──► tools ─┐
              ▲              │ no                       │
              │              ▼                          │
              │             END                         │
              └─────────────────────────────────────────┘

    agent   Rukmani (the chat model) reads the conversation and either
            replies, or asks for one or more tools to be run.
    tools   Runs the requested tools and adds their results to the
            conversation, then hands back to the agent.

Memory, inside the agent step:
    short-term  once a chat is long, older messages are folded into a
                running summary (kept in state) and removed from the history
    long-term   the visitor's most useful remembered facts are added to the
                prompt (extracting new facts happens in service.py)

Conversations (messages, summary, cart, checkout, order — see ``state.py``)
are saved per chat id by the checkpointer, so each request only needs to
send the newest message.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from langchain_core.messages import BaseMessage, RemoveMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from kapruka_agent.agent.language import detect_language
from kapruka_agent.agent.llm import ChatModel
from kapruka_agent.agent.prompts import PERSONA, build_system_prompt
from kapruka_agent.agent.state import AgentState, get_cart, get_checkout, get_order
from kapruka_agent.memory import ConversationSummarizer, MemoryBook

# Safety cap on messages sent to the model (summaries normally keep it lower).
_MAX_HISTORY_MESSAGES = 50


@dataclass
class AgentMemory:
    """Memory settings and parts for the agent. Any part can be left out."""

    book: MemoryBook | None = None
    summarizer: ConversationSummarizer | None = None
    summarize_after: int = 40  # messages before older ones get summarised
    keep_recent: int = 16  # messages kept word for word after summarising
    recall_limit: int = 12  # remembered facts shown each turn


def build_agent(
    model: ChatModel,
    tools: Sequence[BaseTool],
    checkpointer: BaseCheckpointSaver | None = None,
    memory: AgentMemory | None = None,
    persona: Callable[[], str] = lambda: PERSONA,
) -> CompiledStateGraph:
    """Compile the agent graph.

    Args:
        model: Chat model with the tools already bound (see ``llm.build_chat_model``).
        tools: The same tools, so the graph can run them.
        checkpointer: Where conversations are saved. Defaults to in-memory.
        memory: Long-term recall and conversation summaries (optional).
        persona: Returns Rukmani's persona prompt (from Langfuse, or the code version).
    """
    memory = memory or AgentMemory()

    async def agent_node(state: AgentState, config: RunnableConfig) -> dict:
        messages = state["messages"]
        summary = state.get("summary")
        update: dict = {}

        # Short-term memory: fold older messages into the running summary.
        if memory.summarizer and len(messages) > memory.summarize_after:
            cut = _summary_cut(messages, memory.keep_recent)
            if cut:
                older, messages = messages[:cut], messages[cut:]
                summary = await memory.summarizer.summarize(summary, older, config)
                update["summary"] = summary
                update["messages"] = [RemoveMessage(id=m.id) for m in older]

        # Long-term memory: what we know about this visitor from earlier chats.
        visitor_id = config.get("configurable", {}).get("visitor_id")
        facts = (
            await memory.book.recall(visitor_id, memory.recall_limit)
            if memory.book and visitor_id
            else []
        )

        # The prompt includes the current cart/checkout/order so Rukmani always
        # knows them, even after older messages are summarised away.
        system = build_system_prompt(
            persona=persona(),
            cart=get_cart(state),
            checkout=get_checkout(state),
            order=get_order(state),
            summary=summary,
            remembered=[fact.text for fact in facts],
            reply_language=_latest_customer_language(messages),
        )
        response = await model.ainvoke([SystemMessage(system), *_recent_history(messages)], config)
        update["messages"] = [*update.get("messages", []), response]
        return update

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)  # → "tools" or END
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=checkpointer or InMemorySaver())


def _summary_cut(messages: list[BaseMessage], keep_recent: int) -> int | None:
    """Where to split old (summarised) from recent (kept) messages.

    The split is placed on a customer message, so a tool call and its result
    are never separated. Returns None if there's no good place to split.
    """
    for index in range(len(messages) - keep_recent, 0, -1):
        if messages[index].type == "human":
            return index
    return None


def _recent_history(messages: list) -> list:
    """The messages to send to the model: the last N, and only complete tool exchanges.

    The model API rejects a tool call without its result, and a result
    without its call. So:
      - a tool request that never got its result (a turn stopped by the step
        limit or an error) is dropped, and
      - if the cut lands on tool results, it moves back to their tool call.
    """
    answered = {m.tool_call_id for m in messages if m.type == "tool"}
    messages = [
        m
        for m in messages
        if not getattr(m, "tool_calls", None)
        or all(call["id"] in answered for call in m.tool_calls)
    ]

    if len(messages) <= _MAX_HISTORY_MESSAGES:
        return messages
    start = len(messages) - _MAX_HISTORY_MESSAGES
    while start > 0 and messages[start].type == "tool":
        start -= 1
    return messages[start:]


def _latest_customer_language(messages: list) -> str | None:
    """The language of the customer's most recent message, or None if there isn't one."""
    for message in reversed(messages):
        if message.type == "human":
            return detect_language(message.text)
    return None
