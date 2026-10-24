"""
Long-term memory for each visitor, kept in the LangGraph store
(Supabase Postgres in production) under ("memory", <visitor id>).

    recall     the most useful facts right now, for the prompt
    remember   add new facts — merging repeats instead of duplicating
    all_facts/forget/forget_all   for the "what Rukmani remembers" screen
"""

import time
import uuid

from langgraph.store.base import BaseStore
from loguru import logger

from kapruka_agent.memory import policies
from kapruka_agent.memory.models import ExtractedFact, MemoryFact

_NAMESPACE = "memory"
_LIST_LIMIT = 200  # far above max_facts; just a safety bound


class MemoryBook:
    def __init__(self, store: BaseStore, max_facts: int = 30):
        self._store = store
        self._max_facts = max_facts

    @staticmethod
    def _namespace(visitor_id: str) -> tuple[str, ...]:
        return (_NAMESPACE, visitor_id)

    async def all_facts(self, visitor_id: str) -> list[MemoryFact]:
        """All facts for a visitor, most important first."""
        items = await self._store.asearch(self._namespace(visitor_id), limit=_LIST_LIMIT)
        facts = [MemoryFact.model_validate({**item.value, "id": item.key}) for item in items]
        now = time.time()
        return sorted(facts, key=lambda f: policies.score(f, now), reverse=True)

    async def recall(self, visitor_id: str, limit: int) -> list[MemoryFact]:
        """The facts worth showing Rukmani this turn."""
        return (await self.all_facts(visitor_id))[:limit]

    async def remember(self, visitor_id: str, new_facts: list[ExtractedFact]) -> int:
        """Store new facts. A fact already known is reinforced, not duplicated.

        Returns how many facts were added or reinforced.
        """
        existing = await self.all_facts(visitor_id)
        now = time.time()
        changed = 0

        for new in new_facts:
            if policies.is_too_sensitive(new.text):
                logger.debug("Not remembering a sensitive fact")
                continue
            match = next((f for f in existing if policies.is_duplicate(f.text, new.text)), None)
            if match:
                # Same fact again: it matters more now. Keep the newer wording.
                match.text = new.text
                match.mentions += 1
                match.explicit = match.explicit or new.explicit
                match.last_seen_at = now
                await self._save(visitor_id, match)
            else:
                fact = MemoryFact(
                    id=uuid.uuid4().hex,
                    text=new.text,
                    category=new.category,
                    explicit=new.explicit,
                    created_at=now,
                    last_seen_at=now,
                )
                existing.append(fact)
                await self._save(visitor_id, fact)
            changed += 1

        await self._prune(visitor_id, existing, now)
        return changed

    async def forget(self, visitor_id: str, fact_id: str) -> None:
        await self._store.adelete(self._namespace(visitor_id), fact_id)

    async def forget_all(self, visitor_id: str) -> None:
        for fact in await self.all_facts(visitor_id):
            await self.forget(visitor_id, fact.id)

    async def _save(self, visitor_id: str, fact: MemoryFact) -> None:
        await self._store.aput(
            self._namespace(visitor_id), fact.id, fact.model_dump(exclude={"id"})
        )

    async def _prune(self, visitor_id: str, facts: list[MemoryFact], now: float) -> None:
        """Keep only the most important facts (explicit "remember" ones are kept first)."""
        if len(facts) <= self._max_facts:
            return
        ranked = sorted(facts, key=lambda f: (f.explicit, policies.score(f, now)), reverse=True)
        for fact in ranked[self._max_facts :]:
            await self.forget(visitor_id, fact.id)
