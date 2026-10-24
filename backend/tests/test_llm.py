"""The shipped models.yaml is valid, and profile selection works."""

import pytest

from kapruka_agent.agent.llm import load_profile
from kapruka_agent.config import BACKEND_DIR

MODELS_YAML = BACKEND_DIR / "config" / "models.yaml"


@pytest.mark.parametrize("name", ["budget", "balanced", "best"])
def test_every_shipped_profile_loads(name):
    loaded_name, profile = load_profile(MODELS_YAML, name)

    assert loaded_name == name
    assert profile.chat.primary.model
    assert profile.utility.primary.model


def test_active_profile_is_used_when_none_given():
    name, _ = load_profile(MODELS_YAML)

    assert name == "budget"


def test_unknown_profile_lists_the_available_ones():
    with pytest.raises(ValueError, match="Available: budget, balanced, best"):
        load_profile(MODELS_YAML, "premium")
