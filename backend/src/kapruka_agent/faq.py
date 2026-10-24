"""
Instant answers to common questions, with no model call.

The questions and answers live in ``config/faq.yaml``, so they can be
edited without touching code. A message is answered from the FAQ only when
it is SHORT and closely matches one of an entry's example phrasings. Anything
longer or different ("hi, I need a cake for tomorrow") goes to Rukmani as
usual, so the FAQ never gets in the way of real shopping.

Answers are given in the customer's language (detected like everywhere
else). If an entry has no answer in that language, Rukmani answers instead.
"""

import re
from difflib import SequenceMatcher
from pathlib import Path

import yaml
from loguru import logger
from pydantic import BaseModel

from kapruka_agent.agent.language import detect_language

# Only messages this short are looked up; longer ones carry real requests.
_MAX_WORDS = 10
# How close (0–1) a message must be to an example phrasing to count as a match.
_MIN_SIMILARITY = 0.85

# detect_language() names → answer keys in faq.yaml
_LANGUAGE_KEYS = {
    "English": "en",
    "Sinhala": "si",
    "Tamil": "ta",
    "Singlish": "singlish",
    "Tanglish": "tanglish",
}


class FaqEntry(BaseModel):
    id: str
    examples: list[str]
    answers: dict[str, str]  # language key → answer (markdown)


def _normalise(text: str) -> str:
    """Lowercase, no punctuation or emoji, single spaces (keeps Sinhala/Tamil letters)."""
    return " ".join(re.sub(r"[^\w\s]", " ", text.lower()).split())


class Faq:
    def __init__(self, entries: list[FaqEntry]):
        self._entries = entries
        # Normalise the examples once, not on every message.
        self._examples = [(entry, _normalise(ex)) for entry in entries for ex in entry.examples]

    @classmethod
    def load(cls, path: Path) -> "Faq":
        if not path.exists():
            logger.warning("No FAQ file at {} — every message goes to the model", path)
            return cls([])
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        entries = [FaqEntry.model_validate(item) for item in data.get("faq", [])]
        logger.info("Loaded {} FAQ answers", len(entries))
        return cls(entries)

    def answer(self, message: str) -> tuple[str, str] | None:
        """(entry id, answer) if the message is a known common question, else None."""
        text = _normalise(message)
        if not text or len(text.split()) > _MAX_WORDS:
            return None

        best, best_score = None, 0.0
        for entry, example in self._examples:
            score = 1.0 if text == example else SequenceMatcher(None, text, example).ratio()
            if score > best_score:
                best, best_score = entry, score
        if best is None or best_score < _MIN_SIMILARITY:
            return None

        reply = best.answers.get(_LANGUAGE_KEYS[detect_language(message)])
        return (best.id, reply) if reply else None
