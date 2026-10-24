"""
Work out which language the customer wrote in, so Rukmani answers in it.

Models handle Sinhala and Tamil script well, but often confuse Singlish
(Sinhala in English letters) with Tanglish (Tamil in English letters).
Telling the model the language explicitly fixes that.

How it decides:
    - Sinhala or Tamil script characters → "Sinhala" / "Tamil".
    - Otherwise, count common words of each romanized language; the one
      with more matches wins. No matches → "English".
"""

import re

# Unicode code point ranges of the two scripts.
_SINHALA_RANGE = range(0x0D80, 0x0E00)
_TAMIL_RANGE = range(0x0B80, 0x0C00)

# Everyday words that appear in only one of the two romanized languages.
_SINGLISH_WORDS = set(
    """
    ona oney eka ekak ekata walata mata oyata puluwanda puluwan kiyala hondai
    honda hondama heta anidda yawanna ganna monawada kohomada thiyenawa
    thiyenawada nadda nehe aney lassana lassanai dawasa mokakda kawda kiyada wage
    ayubowan isthuthi sthuthi bohoma
    """.split()
)
_TANGLISH_WORDS = set(
    """
    venum vendum irukku iruku anuppanum anupanum anuppa anupa maathiri mathiri
    enna eppadi naalai nalai nalla thambi thangachi illai illa romba panna
    pannunga kudunga vaanga sollunga endha evvalavu ooru ku kku
    vanakkam nandri
    """.split()
)
_WORD = re.compile(r"[a-z]+")


def _has_script(text: str, script: range) -> bool:
    return any(ord(char) in script for char in text)


def detect_language(text: str) -> str:
    """Return "Sinhala", "Tamil", "Singlish", "Tanglish" or "English"."""
    if _has_script(text, _SINHALA_RANGE):
        return "Sinhala"
    if _has_script(text, _TAMIL_RANGE):
        return "Tamil"

    words = _WORD.findall(text.lower())
    singlish = sum(word in _SINGLISH_WORDS for word in words)
    tanglish = sum(word in _TANGLISH_WORDS for word in words)
    if tanglish > singlish:
        return "Tanglish"
    if singlish > tanglish:
        return "Singlish"
    return "English"


# Extra guidance for the two languages models tend to mix up.
_REMINDERS = {
    "Tanglish": (
        " Tanglish is TAMIL in English letters. Use Tamil words such as super, nalla,"
        " irukku, venum, anuppalam, endha ooru, sollunga. NEVER use Sinhala words such as"
        " aney, lassanai, ona, ekata, yawanna, hondama, mehemai."
    ),
    "Singlish": (
        " Singlish is SINHALA in English letters. Use Sinhala words such as aney, lassanai,"
        " ona, yawanna, hondama. NEVER use Tamil words such as venum, irukku, anuppalam."
    ),
}


def reply_language_instruction(language: str) -> str:
    """One line for the system prompt telling the model which language to answer in."""
    return (
        f"The customer's latest message is in {language}. Write your whole reply in "
        f"{language}.{_REMINDERS.get(language, '')}"
    )
