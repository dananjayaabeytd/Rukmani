"""
Finds facts worth remembering in the latest exchange, using the cheap
utility model with structured output (a list of facts, not free text).

It runs alongside Rukmani's reply, so it adds no waiting time. If it fails,
the chat carries on — memory is a bonus, never a blocker.
"""

from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig
from loguru import logger

from kapruka_agent.memory import policies
from kapruka_agent.memory.book import MemoryBook
from kapruka_agent.memory.models import ExtractionResult
from kapruka_agent.memory.prompts import MEMORY_EXTRACT
from kapruka_agent.observability import Observability

ChatModel = Runnable[Any, Any]


class MemoryExtractor:
    def __init__(self, model: ChatModel, book: MemoryBook, observability: Observability):
        # Must return ExtractionResult (see llm.build_structured_model).
        self._model = model.with_config(tags=["nostream"], run_name="memory-extraction")
        self._book = book
        self._observability = observability

    async def extract_and_remember(
        self,
        visitor_id: str,
        customer_message: str,
        previous_reply: str | None,
        config: RunnableConfig | None = None,
    ) -> int:
        """Look for new facts in this exchange and store them. Returns facts saved."""
        if not policies.worth_extracting(customer_message):
            return 0
        try:
            known = await self._book.recall(visitor_id, limit=30)
            exchange = (
                f"Rukmani: {previous_reply}\n" if previous_reply else ""
            ) + f"Customer: {customer_message}"
            prompt = self._observability.prompt(
                "memory_extract",
                MEMORY_EXTRACT,
                known_facts="\n".join(f"- {f.text}" for f in known) or "(nothing yet)",
                conversation=exchange,
            )
            result: ExtractionResult = await self._model.ainvoke([HumanMessage(prompt)], config)
            saved = await self._book.remember(visitor_id, result.facts)
            if saved:
                logger.info("Remembered {} fact(s) for a visitor", saved)
            return saved
        except Exception:
            logger.exception("Memory extraction failed (the chat is unaffected)")
            return 0
