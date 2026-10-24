"""Instant FAQ answers: strict matching, the customer's language, and the real faq.yaml."""

import pytest

from kapruka_agent.config import BACKEND_DIR
from kapruka_agent.faq import Faq, FaqEntry

FAQ = Faq(
    [
        FaqEntry(
            id="greeting",
            examples=["hi", "hello", "ආයුබෝවන්"],
            answers={"en": "Hi! What gift are you looking for?", "si": "ආයුබෝවන්!"},
        ),
        FaqEntry(
            id="contact",
            examples=["how can I contact customer service"],
            answers={"en": "Call +94 117 551 111."},
        ),
    ]
)


def test_exact_and_close_phrasings_match():
    assert FAQ.answer("Hi!") == ("greeting", "Hi! What gift are you looking for?")
    assert FAQ.answer("How can I contact customer service?")[0] == "contact"
    assert FAQ.answer("how can i contact customer servise")[0] == "contact"  # typo


def test_answer_is_in_the_customers_language():
    assert FAQ.answer("ආයුබෝවන්") == ("greeting", "ආයුබෝවන්!")


def test_no_answer_in_that_language_goes_to_the_model():
    assert FAQ.answer("vanakkam") is None


@pytest.mark.parametrize(
    "message",
    [
        "hi, I need a birthday cake delivered to Kandy tomorrow",  # real request after a greeting
        "Red roses for my mother",
        "how can I contact the delivery person for my order",
        "",
    ],
)
def test_real_requests_are_never_caught(message):
    assert FAQ.answer(message) is None


# The real file: loads, and shopping messages still reach Rukmani.

REAL = Faq.load(BACKEND_DIR / "config" / "faq.yaml")


def test_real_faq_loads_and_answers_a_greeting():
    assert REAL.answer("hello") is not None


@pytest.mark.parametrize(
    "message",
    [
        "Show me chocolate cakes under 5000",
        "Do you deliver to Kandy tomorrow?",
        "I want to send flowers to my wife",
        "track my order 123456789012",
        "What can I send to my mother in the UK?",
        "hi Rukmani, need a gift",
    ],
)
def test_real_faq_leaves_shopping_to_rukmani(message):
    assert REAL.answer(message) is None
