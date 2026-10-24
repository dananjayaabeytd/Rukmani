"""
Condenses the older part of a long conversation into a short summary.

Instead of simply dropping old messages (and with them, details like the
recipient or the budget), they're folded into a running summary that stays
in Rukmani's prompt.
"""

from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig

from kapruka_agent.memory.prompts import CONVERSATION_SUMMARY
from kapruka_agent.observability import Observability

ChatModel = Runnable[Any, Any]


def transcript(messages: list[BaseMessage]) -> str:
    """Plain-text view of messages for the summary prompt (tool results shortened)."""
    lines = []
    for message in messages:
        if message.type == "human":
            lines.append(f"Customer: {message.text}")
        elif message.type == "ai" and message.text:
            lines.append(f"Rukmani: {message.text}")
        elif message.type == "tool":
            lines.append(f"[{message.name} result: {str(message.content)[:300]}]")
    return "\n".join(lines)


class ConversationSummarizer:
    def __init__(self, model: ChatModel, observability: Observability):
        # "nostream" keeps the summary out of the customer's live reply stream.
        self._model = model.with_config(tags=["nostream"], run_name="conversation-summary")
        self._observability = observability

    async def summarize(
        self,
        previous_summary: str | None,
        messages: list[BaseMessage],
        config: RunnableConfig | None = None,
    ) -> str:
        prompt = self._observability.prompt(
            "summary",
            CONVERSATION_SUMMARY,
            previous_summary=previous_summary or "(none)",
            conversation=transcript(messages),
        )
        reply = await self._model.ainvoke([HumanMessage(prompt)], config)
        return reply.text.strip()
