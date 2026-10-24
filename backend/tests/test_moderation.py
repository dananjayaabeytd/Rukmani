"""The safety check on customer messages (no network: a fake moderation client)."""

from types import SimpleNamespace

from kapruka_agent.moderation import Moderator


class FakeScores(SimpleNamespace):
    def model_dump(self) -> dict:
        return vars(self)


class FakeModerationClient:
    """Answers like OpenAI's moderation endpoint, with the scores it was given."""

    def __init__(
        self,
        flagged: bool = False,
        self_harm: bool = False,
        fail: bool = False,
        **scores: float,
    ):
        all_scores = {
            "harassment": 0.0,
            "harassment_threatening": 0.9 if flagged else 0.0,
            "violence": 0.0,
            "self_harm": 0.9 if self_harm else 0.0,
            "self_harm_intent": 0.9 if self_harm else 0.0,
        } | scores
        result = SimpleNamespace(category_scores=FakeScores(**all_scores))
        self._response = SimpleNamespace(results=[result])
        self._fail = fail
        self.moderations = self

    async def create(self, **_kwargs):
        if self._fail:
            raise TimeoutError("moderation is down")
        return self._response


async def test_safe_message_passes():
    assert await Moderator(FakeModerationClient()).check("Roses for my mother") is None


async def test_harmful_message_gets_a_polite_decline():
    reply = await Moderator(FakeModerationClient(flagged=True)).check("something abusive")

    assert reply is not None and "Kapruka" in reply


async def test_decline_is_in_the_customers_language():
    reply = await Moderator(FakeModerationClient(flagged=True)).check("මට ඕනේ ...")

    assert reply is not None and "උදව්" in reply


async def test_self_harm_points_to_the_helpline():
    reply = await Moderator(FakeModerationClient(self_harm=True)).check("...")

    assert reply is not None and "1926" in reply


async def test_plain_rudeness_is_left_to_rukmani():
    moderator = Moderator(FakeModerationClient(harassment=0.89))

    assert await moderator.check("you are a useless bot") is None


async def test_low_scores_pass():
    # Singlish love letter request, misread by moderation as violence 0.35.
    moderator = Moderator(FakeModerationClient(violence=0.35))

    assert await moderator.check("mata girlfriend ta love letter ekak liyala denna") is None


async def test_moderation_outage_lets_messages_through():
    assert await Moderator(FakeModerationClient(fail=True)).check("Roses please") is None


async def test_no_key_means_no_check():
    assert await Moderator(None).check("anything") is None
