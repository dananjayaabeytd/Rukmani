"""The reply language is detected from the customer's message, including romanized Sinhala/Tamil."""

import pytest

from kapruka_agent.agent.language import detect_language
from kapruka_agent.agent.prompts import build_system_prompt


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("මගේ යාළුවාට රෝස මල් ටිකක් යවන්න ඕනේ", "Sinhala"),
        ("என் அம்மாவுக்கு பிறந்தநாள் கேக் வேண்டும்", "Tamil"),
        ("amma ta birthday cake ekak ona, budget 7000", "Singlish"),
        ("Kandy walata heta chocolate hamper ekak yawanna puluwanda?", "Singlish"),
        ("thambi ku birthday gift venum, chocolate hamper maathiri", "Tanglish"),
        ("amma ku naalai Colombo ku flowers anuppanum", "Tanglish"),
        ("A birthday cake for my mother", "English"),
    ],
)
def test_detect_language(message, expected):
    assert detect_language(message) == expected


def test_prompt_tells_the_model_which_language_to_reply_in():
    prompt = build_system_prompt(reply_language="Tanglish")

    assert "latest message is in Tanglish" in prompt
    assert "NEVER use Sinhala words" in prompt
