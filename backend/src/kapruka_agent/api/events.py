"""
Turns the agent's run into a stream of simple events for the UI.

The browser receives Server-Sent Events. Each event's data is JSON with a
``type`` field:

    {"type": "token",     "text": "..."}                     part of Rukmani's reply
    {"type": "tool",      "tool": "search_products",
                          "label": "Searching Kapruka..."}   a tool started
    {"type": "artifact",  "artifact": {"kind": "products", ...}}   data for a card
    {"type": "done"}                                         reply finished
    {"type": "error",     "message": "..."}                  something went wrong

The frontend mirrors these in ``frontend/lib/types.ts``.
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from loguru import logger

from kapruka_agent.agent.service import ShoppingAgent

# Friendly text the UI shows while a tool runs.
_TOOL_LABELS = {
    "search_products": "Searching Kapruka for gifts",
    "get_product_details": "Looking at the product details",
    "find_delivery_city": "Finding the delivery city",
    "check_delivery": "Checking delivery date and fee",
    "add_to_cart": "Adding to your cart",
    "update_cart_item": "Updating your cart",
    "remove_from_cart": "Updating your cart",
    "prepare_checkout": "Preparing your checkout",
    "track_order": "Tracking your order",
    "list_gift_countries": "Checking overseas gift stores",
    "browse_gift_store": "Browsing the overseas gift store",
}

_ERROR_MESSAGE = "Sorry, something went wrong on my side. Please try again."
_EMPTY_REPLY_MESSAGE = "Sorry, I lost my words there. Could you ask that again?"


def _event(event_type: str, **data: Any) -> dict[str, str]:
    """Package one event in the shape sse-starlette sends to the browser."""
    return {"data": json.dumps({"type": event_type, **data}, ensure_ascii=False)}


async def stream_agent_events(
    agent: ShoppingAgent, chat_id: str, visitor_id: str, message: str
) -> AsyncIterator[dict[str, str]]:
    """Run one customer turn and yield UI events as they happen."""
    shown_anything = False  # did the customer get any text or card?

    try:
        async for mode, payload in agent.stream(chat_id, visitor_id, message):
            if mode == "messages":
                chunk, metadata = payload
                # Only stream the agent's own words, not raw tool output.
                # Usually these are small chunks; a model that can't stream
                # sends its whole reply as one AIMessage, which works the same.
                if (
                    metadata.get("langgraph_node") == "agent"
                    and isinstance(chunk, AIMessage)
                    and chunk.text
                ):
                    shown_anything = True
                    yield _event("token", text=chunk.text)
            else:
                for event in _events_from_update(payload):
                    shown_anything = True
                    yield event

        if not shown_anything:
            # Never leave the customer looking at an empty reply.
            logger.warning("Empty reply in chat {}", chat_id)
            yield _event("error", message=_EMPTY_REPLY_MESSAGE)
        yield _event("done")
    except Exception:
        logger.exception("Agent run failed in chat {}", chat_id)
        yield _event("error", message=_ERROR_MESSAGE)


async def fixed_reply_events(text: str) -> AsyncIterator[dict[str, str]]:
    """A reply that doesn't come from the agent (e.g. a message blocked by moderation)."""
    yield _event("token", text=text)
    yield _event("done")


def _events_from_update(update: dict[str, Any]) -> list[dict[str, str]]:
    """Map one finished graph step to UI events."""
    events = []
    for node_output in update.values():
        # A node usually returns one dict; tools returning Commands may give a list.
        outputs = node_output if isinstance(node_output, list) else [node_output]
        messages = [m for out in outputs if isinstance(out, dict) for m in out.get("messages", [])]
        for msg in messages:
            if isinstance(msg, AIMessage):
                for call in msg.tool_calls:
                    label = _TOOL_LABELS.get(call["name"], "Working on it")
                    events.append(_event("tool", tool=call["name"], label=label))
            elif isinstance(msg, ToolMessage) and msg.artifact:
                events.append(_event("artifact", artifact=msg.artifact))
    return events
