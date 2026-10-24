"""
Memory rules — pure functions, no storage or model calls (easy to test).

    score            how important a fact is now: recency + repetition + "remember"
    is_duplicate     the same fact said in different words
    is_too_sensitive phone numbers, emails, card numbers: never stored
    worth_extracting skip messages too short to contain a useful fact
"""

import math
import re
from difflib import SequenceMatcher

from kapruka_agent.memory.models import MemoryFact

# A fact unused for this many days is worth half as much.
_HALF_LIFE_DAYS = 30
# Two facts this similar (0–1) are treated as the same fact.
_DUPLICATE_SIMILARITY = 0.82

_PHONE = re.compile(r"(?:\+?\d[\s-]?){7,}")
_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_BUTTON_MESSAGES = re.compile(r'^(Add ".+" \(.+\) to my cart|Remove ".+" \(.+\) from my cart)$')


def score(fact: MemoryFact, now: float) -> float:
    """0–1: 50% recency, 30% repetition, 20% "the customer asked to remember"."""
    age_days = max(0.0, now - fact.last_seen_at) / 86_400
    recency = math.exp(-age_days * math.log(2) / _HALF_LIFE_DAYS)
    repetition = min(1.0, math.log(1 + fact.mentions) / math.log(6))  # 5+ mentions = 1.0
    explicit = 1.0 if fact.explicit else 0.0
    return round(0.5 * recency + 0.3 * repetition + 0.2 * explicit, 3)


def _normalise(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", text.lower()).split())


def is_duplicate(a: str, b: str) -> bool:
    """True if two facts say the same thing (ignoring case, punctuation, small wording changes)."""
    return SequenceMatcher(None, _normalise(a), _normalise(b)).ratio() >= _DUPLICATE_SIMILARITY


def is_too_sensitive(text: str) -> bool:
    """Contact and payment details are never kept in long-term memory."""
    return bool(_PHONE.search(text) or _EMAIL.search(text))


def worth_extracting(message: str) -> bool:
    """Only look for facts in real sentences, not 'ok' or button messages."""
    message = message.strip()
    return len(message.split()) >= 4 and not _BUTTON_MESSAGES.match(message)
