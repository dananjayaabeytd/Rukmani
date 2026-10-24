"""
Rebuilds a saved conversation for the screen when a chat is reopened.

The checkpointer stores the raw conversation: customer messages, Rukmani's
replies and tool calls, and tool results (whose artifacts are the cards).
The UI wants what it showed live: one bubble per customer message and, for
each turn, one Rukmani reply with its cards and text. This module turns the
first into the second, matching ``frontend/lib/types.ts`` (ChatMessage).
"""

from typing import Any

from langchain_core.messages import BaseMessage


def ui_messages(messages: list[BaseMessage]) -> list[dict[str, Any]]:
    """Group the stored messages into the chat bubbles the UI shows."""
    bubbles: list[dict[str, Any]] = []
    reply: dict[str, Any] | None = None  # Rukmani's bubble for the current turn

    for message in messages:
        if message.type == "human":
            reply = None
            bubbles.append(_bubble(message.id, "user", message.text))
            continue

        if message.type not in ("ai", "tool"):
            continue
        if reply is None:
            reply = _bubble(message.id, "assistant", "")
            bubbles.append(reply)

        if message.type == "ai" and message.text:
            reply["text"] = f"{reply['text']}\n\n{message.text}" if reply["text"] else message.text
        elif message.type == "tool" and getattr(message, "artifact", None):
            reply["artifacts"].append(message.artifact)

    # A turn that was cut off may have left an empty reply bubble.
    return [b for b in bubbles if b["role"] == "user" or b["text"] or b["artifacts"]]


def _bubble(message_id: str | None, role: str, text: str) -> dict[str, Any]:
    return {
        "id": message_id or "",
        "role": role,
        "text": text,
        "artifacts": [],
        "status": None,
        "failed": False,
    }
