"""History trimming never separates a tool result from the call that asked for it."""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from kapruka_agent.agent import graph


def test_trim_moves_back_to_include_the_tool_call(monkeypatch):
    monkeypatch.setattr(graph, "_MAX_HISTORY_MESSAGES", 2)
    messages = [
        HumanMessage("hi"),
        AIMessage("", tool_calls=[{"name": "search_products", "args": {}, "id": "c1"}]),
        ToolMessage("results", tool_call_id="c1"),
        AIMessage("done"),
    ]

    trimmed = graph._recent_history(messages)

    # A cut at 2 would start on the ToolMessage; it must start on the AI call instead.
    assert trimmed[0] is messages[1]


def test_unanswered_tool_call_is_dropped():
    # A turn stopped by the step limit can leave a tool request with no result.
    messages = [
        HumanMessage("hi"),
        AIMessage("", tool_calls=[{"name": "search_products", "args": {}, "id": "lost"}]),
        HumanMessage("hello?"),
    ]

    history = graph._recent_history(messages)

    assert [m.type for m in history] == ["human", "human"]
