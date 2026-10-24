"""Long-term memory: scoring, duplicates, privacy, pruning and the extractor."""

import time

from langchain_core.runnables import RunnableLambda
from langgraph.store.memory import InMemoryStore

from kapruka_agent.memory import MemoryBook, MemoryExtractor, policies
from kapruka_agent.memory.models import ExtractedFact, ExtractionResult, MemoryFact
from kapruka_agent.observability import Observability

VISITOR = "visitor-1234567890"


def _fact(**overrides) -> MemoryFact:
    now = time.time()
    values = {"id": "f1", "text": "x", "created_at": now, "last_seen_at": now, **overrides}
    return MemoryFact(**values)


# ── Policies (pure rules) ──────────────────────────────────────────


def test_repeated_and_explicit_facts_score_higher():
    now = time.time()
    once = _fact()
    repeated = _fact(mentions=5)
    asked_to_remember = _fact(explicit=True)

    assert policies.score(repeated, now) > policies.score(once, now)
    assert policies.score(asked_to_remember, now) > policies.score(once, now)


def test_old_facts_fade():
    now = time.time()
    fresh = _fact()
    stale = _fact(last_seen_at=now - 90 * 86_400)

    assert policies.score(fresh, now) > policies.score(stale, now)


def test_same_fact_in_different_words_is_a_duplicate():
    assert policies.is_duplicate(
        "Customer's mother Kamala lives in Kandy", "Customer's mother, Kamala, lives in Kandy."
    )
    assert not policies.is_duplicate("Wife loves chocolate", "Mother lives in Kandy")


def test_contact_details_are_never_kept():
    assert policies.is_too_sensitive("Mother's number is 077 123 4567")
    assert policies.is_too_sensitive("Email is nimal@example.com")
    assert not policies.is_too_sensitive("Wife's birthday is on 12 March")


def test_button_messages_and_short_replies_are_skipped():
    assert not policies.worth_extracting("ok thanks")
    assert not policies.worth_extracting('Add "Rose Bouquet" (FLOWER1) to my cart')
    assert not policies.worth_extracting('"Rose Bouquet" (FLOWER1) කරත්තයට දාන්න')
    assert not policies.worth_extracting("Can you deliver to Kandy on 2026-10-25 (CAKE1)?")
    assert not policies.worth_extracting("I'm ready to check out")
    assert policies.worth_extracting("It's for my wife, she is 25 and loves chocolate")


# ── MemoryBook (storage) ───────────────────────────────────────────


async def test_repeated_fact_is_reinforced_not_duplicated():
    book = MemoryBook(InMemoryStore())

    await book.remember(VISITOR, [ExtractedFact(text="Wife loves chocolate", category="recipient")])
    await book.remember(
        VISITOR, [ExtractedFact(text="Wife loves chocolate.", category="recipient")]
    )

    facts = await book.all_facts(VISITOR)
    assert len(facts) == 1
    assert facts[0].mentions == 2


async def test_sensitive_facts_are_dropped():
    book = MemoryBook(InMemoryStore())

    saved = await book.remember(
        VISITOR, [ExtractedFact(text="Wife's phone is 0771234567", category="recipient")]
    )

    assert saved == 0
    assert await book.all_facts(VISITOR) == []


async def test_only_the_most_important_facts_are_kept():
    book = MemoryBook(InMemoryStore(), max_facts=2)

    await book.remember(
        VISITOR,
        [
            ExtractedFact(text="Prefers flowers over cakes", category="preference"),
            ExtractedFact(text="Mother lives in Kandy", category="recipient"),
            ExtractedFact(
                text="Remember: wife is allergic to nuts", category="recipient", explicit=True
            ),
        ],
    )

    texts = [f.text for f in await book.all_facts(VISITOR)]
    assert len(texts) == 2
    assert "Remember: wife is allergic to nuts" in texts  # explicit facts are kept first


async def test_visitors_never_see_each_others_memories():
    book = MemoryBook(InMemoryStore())
    await book.remember(VISITOR, [ExtractedFact(text="Wife loves chocolate", category="recipient")])

    assert await book.all_facts("another-visitor-0987654321") == []


async def test_forget_all():
    book = MemoryBook(InMemoryStore())
    await book.remember(VISITOR, [ExtractedFact(text="Wife loves chocolate", category="recipient")])

    await book.forget_all(VISITOR)

    assert await book.all_facts(VISITOR) == []


# ── Extractor ──────────────────────────────────────────────────────


async def test_extractor_saves_what_the_model_found():
    book = MemoryBook(InMemoryStore())
    model = RunnableLambda(
        lambda _: ExtractionResult(
            facts=[ExtractedFact(text="Wife is 25 and loves chocolate", category="recipient")]
        )
    )
    extractor = MemoryExtractor(model, book, Observability())

    saved = await extractor.extract_and_remember(
        VISITOR, "It's for my wife, she's 25 and loves chocolate", previous_reply="Who is it for?"
    )

    assert saved == 1
    assert (await book.all_facts(VISITOR))[0].text == "Wife is 25 and loves chocolate"


async def test_extractor_failure_never_breaks_the_chat():
    def broken(_):
        raise RuntimeError("model down")

    extractor = MemoryExtractor(
        RunnableLambda(broken), MemoryBook(InMemoryStore()), Observability()
    )

    assert (
        await extractor.extract_and_remember(VISITOR, "It's for my wife who loves roses", None) == 0
    )
