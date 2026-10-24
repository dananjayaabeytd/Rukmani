"""The safety check on customer messages (no network: a fake moderation client)."""

from types import SimpleNamespace

from kapruka_agent.moderation import Moderator


class FakeCategories(SimpleNamespace):
    def model_dump(self) -> dict:
        return vars(self)


class FakeModerationClient:
    """Answers like OpenAI's moderation endpoint, flagging what it was told to."""

    def __init__(self, flagged: bool = False, self_harm: bool = False, fail: bool = False):
        categories = FakeCategories(
            harassment=flagged and not self_harm,
            self_harm=self_harm,
            self_harm_intent=self_harm,
            self_harm_instructions=False,
        )
        result = SimpleNamespace(flagged=flagged or self_harm, categories=categories)
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


async def test_moderation_outage_lets_messages_through():
    assert await Moderator(FakeModerationClient(fail=True)).check("Roses please") is None


async def test_no_key_means_no_check():
    assert await Moderator(None).check("anything") is None
