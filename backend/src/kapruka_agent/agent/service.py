"""
One customer turn, end to end — the orchestrator around the graph.

For each message it:
    1. builds the run config: which chat and visitor, the step limit, and
       Langfuse tracing (the trace is grouped by chat and by visitor),
    2. starts long-term memory extraction IN PARALLEL with Rukmani's reply,
       so it adds no waiting time,
    3. streams the graph's output to the caller (api/events.py turns it into
       UI events),
    4. waits for memory extraction to finish before the request ends (on
       Cloud Run, work left running after a response may be starved of CPU).
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from loguru import logger

from kapruka_agent.memory import MemoryExtractor
from kapruka_agent.observability import Observability

# Memory extraction normally finishes long before the reply; this is a backstop.
_MEMORY_TIMEOUT_SECONDS = 20


class ShoppingAgent:
    def __init__(
        self,
        graph: CompiledStateGraph,
        observability: Observability,
        extractor: MemoryExtractor | None = None,
        max_steps: int = 16,
    ):
        self.graph = graph
        self._observability = observability
        self._extractor = extractor
        self._max_steps = max_steps

    def config(
        self, chat_id: str, visitor_id: str, run_name: str = "rukmani-turn"
    ) -> RunnableConfig:
        """Run settings: which conversation, step limit, and tracing."""
        return {
            "configurable": {"thread_id": chat_id, "visitor_id": visitor_id},
            "recursion_limit": self._max_steps,
            "callbacks": self._observability.callbacks(),
            "metadata": self._observability.trace_metadata(chat_id, visitor_id, [run_name]),
            "run_name": run_name,
        }

    async def stream(
        self, chat_id: str, visitor_id: str, message: str
    ) -> AsyncIterator[tuple[str, Any]]:
        """Run one turn, yielding LangGraph stream items: (mode, payload)."""
        config = self.config(chat_id, visitor_id)
        memory_task = await self._start_memory_extraction(chat_id, visitor_id, message)
        try:
            # "messages" mode gives the reply token by token; "updates" mode gives
            # each finished step (tool calls requested, tool results returned).
            async for item in self.graph.astream(
                {"messages": [HumanMessage(message)]}, config, stream_mode=["messages", "updates"]
            ):
                yield item
        finally:
            if memory_task:
                await self._finish(memory_task)

    async def record_turn(self, chat_id: str, message: str, reply: str) -> None:
        """Save a turn answered without the model (e.g. from the FAQ).

        It goes into the chat like any other turn, so the chat reopens with it
        and Rukmani sees it as context on the next message.
        """
        await self.graph.aupdate_state(
            {"configurable": {"thread_id": chat_id}},
            {"messages": [HumanMessage(message), AIMessage(reply)]},
            as_node="agent",
        )

    async def _start_memory_extraction(
        self, chat_id: str, visitor_id: str, message: str
    ) -> asyncio.Task | None:
        if not self._extractor:
            return None
        previous_reply = await self._last_reply(chat_id)
        memory_config = self.config(chat_id, visitor_id, run_name="memory-extraction")
        return asyncio.create_task(
            self._extractor.extract_and_remember(visitor_id, message, previous_reply, memory_config)
        )

    async def _last_reply(self, chat_id: str) -> str | None:
        """Rukmani's previous message in this chat (context for memory extraction)."""
        state = await self.graph.aget_state({"configurable": {"thread_id": chat_id}})
        for message in reversed(state.values.get("messages", [])):
            if message.type == "ai" and message.text:
                return message.text
        return None

    @staticmethod
    async def _finish(task: asyncio.Task) -> None:
        try:
            await asyncio.wait_for(task, timeout=_MEMORY_TIMEOUT_SECONDS)
        except TimeoutError:
            logger.warning("Memory extraction took too long and was skipped")
