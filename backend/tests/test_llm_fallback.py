"""When the main model fails, the fallback answers AND the failure is logged."""

from langchain_core.runnables import RunnableLambda
from loguru import logger

from kapruka_agent.agent.llm import _log_failures


def _broken(_):
    raise RuntimeError("tools not supported")


def test_fallback_answers_and_failure_is_logged():
    logs: list[str] = []
    sink = logger.add(logs.append, level="WARNING")
    try:
        model = _log_failures(RunnableLambda(_broken), "openai/test-model").with_fallbacks(
            [RunnableLambda(lambda _: "fallback answer")]
        )

        assert model.invoke("hi") == "fallback answer"
    finally:
        logger.remove(sink)

    assert any("openai/test-model failed" in line for line in logs)
