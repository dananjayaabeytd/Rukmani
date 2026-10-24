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

Conversations (messages, cart, checkout, order — see ``state.py``) are
saved per ``thread_id`` by the checkpointer, so each request only needs to
send the newest message.
"""

from collections.abc import Sequence

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from kapruka_agent.agent.llm import ChatModel
from kapruka_agent.agent.prompts import build_system_prompt
from kapruka_agent.agent.state import AgentState, get_cart, get_checkout, get_order

# Only the most recent messages are sent to the model, to keep each turn
# fast and cheap. The full conversation stays in the checkpointer.
_MAX_HISTORY_MESSAGES = 30


def build_agent(
    model: ChatModel,
    tools: Sequence[BaseTool],
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Compile the agent graph.

    Args:
        model: Chat model with the tools already bound (see ``llm.build_chat_model``).
        tools: The same tools, so the graph can run them.
        checkpointer: Where conversations are saved. Defaults to in-memory,
            which is lost on restart.
    """

    async def agent_node(state: AgentState, config: RunnableConfig) -> dict:
        # The prompt includes the current cart/checkout/order so Rukmani always
        # knows them, even after older messages are trimmed from the history.
        system = build_system_prompt(
            cart=get_cart(state), checkout=get_checkout(state), order=get_order(state)
        )
        history = _recent_history(state["messages"])
        response = await model.ainvoke([SystemMessage(system), *history], config)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)  # → "tools" or END
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=checkpointer or InMemorySaver())


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
