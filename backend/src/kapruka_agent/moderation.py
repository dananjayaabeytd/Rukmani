"""
A safety check on every customer message, before Rukmani sees it.

Uses OpenAI's moderation endpoint (free, ~100 ms). A message that clearly
scores as harmful (threats, violence, hate, sexual, illegal requests) gets
a short fixed reply in the customer's language and
never reaches the agent, so it costs no model call either. If someone
mentions hurting themselves, the reply points to Sri Lanka's 1926 mental
health helpline instead.

If the check itself fails (timeout, outage), the message goes through: a
moderation outage must not close the shop. Without an OpenAI key the check
is off.
"""

from typing import Any

from loguru import logger
from openai import AsyncOpenAI

from kapruka_agent.agent.language import detect_language
from kapruka_agent.config import Settings

_MODEL = "omni-moderation-latest"

# A category scoring this much (0–1) blocks the message.
_BLOCK_SCORE = 0.5
# Plain rudeness ("you're a useless bot") isn't blocked: Rukmani answers it
# kindly, with the hotline. Threats are a separate category and are blocked.
_LEFT_TO_RUKMANI = {"harassment"}

_DECLINE = {
    "en": "I can't help with that. I'm here to help you find gifts and shop on Kapruka. "
    "What can I find for you?",
    "si": "මට ඒකට උදව් කරන්න බැහැ. මම ඉන්නේ Kapruka එකෙන් තෑගි හොයන්න උදව් කරන්න. මොනවද හොයන්න ඕනේ?",
    "ta": "அதற்கு என்னால் உதவ முடியாது. Kapruka-வில் பரிசுகள் தேட உதவவே நான் இருக்கிறேன். என்ன தேடலாம்?",
}

_SUPPORT = {
    "en": "I'm really sorry you're going through this. You don't have to face it alone: "
    "please call 1926, Sri Lanka's free mental health helpline, or talk to someone you trust.",
    "si": "ඔබ මේ අමාරු දේකට මුහුණ දෙන එක ගැන මට ඇත්තටම කනගාටුයි. ඔබ තනියම නෙවෙයි: "
    "කරුණාකර 1926 අමතන්න (ශ්‍රී ලංකාවේ නොමිලේ මානසික සෞඛ්‍ය උපකාරක අංකය), "
    "නැත්නම් ඔබ විශ්වාස කරන කෙනෙක් එක්ක කතා කරන්න.",
    "ta": "நீங்கள் இதை அனுபவிப்பது குறித்து மிகவும் வருந்துகிறேன். நீங்கள் தனியாக இல்லை: "
    "தயவுசெய்து 1926 ஐ அழைக்கவும் (இலங்கையின் இலவச மனநல உதவி எண்), "
    "அல்லது நீங்கள் நம்பும் ஒருவரிடம் பேசுங்கள்.",
}


def _reply_language(message: str) -> str:
    language = detect_language(message)
    if language == "Sinhala":
        return "si"
    if language in ("Tamil", "Tanglish"):
        return "ta"
    return "en"


class Moderator:
    """Checks customer messages. ``client`` is an AsyncOpenAI client, or None for no checks."""

    def __init__(self, client: Any | None = None):
        self._client = client

    async def check(self, message: str) -> str | None:
        """None if the message is fine; otherwise the reply to send instead of running the agent."""
        if self._client is None:
            return None
        try:
            response = await self._client.moderations.create(model=_MODEL, input=message)
        except Exception as error:
            logger.warning("Moderation check failed, letting the message through: {}", error)
            return None

        # Decide on scores, not OpenAI's own "flagged": it also flags plain
        # rudeness, and misreads some Singlish (a love letter scored as violence 0.35).
        scores = response.results[0].category_scores.model_dump()
        serious = sorted(
            name
            for name, score in scores.items()
            if score >= _BLOCK_SCORE and name not in _LEFT_TO_RUKMANI
        )
        if not serious:
            return None

        logger.info("Message blocked by moderation: {}", serious)
        self_harm = any(name.startswith("self") for name in serious)
        replies = _SUPPORT if self_harm else _DECLINE
        return replies[_reply_language(message)]


def build_moderator(settings: Settings) -> Moderator:
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not set — message moderation is off")
        return Moderator(None)
    client = AsyncOpenAI(
        api_key=settings.openai_api_key.get_secret_value(), timeout=5.0, max_retries=1
    )
    return Moderator(client)
