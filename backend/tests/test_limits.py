"""Rate limits stop a single visitor or the whole day from going over budget."""

from kapruka_agent.api.limits import DailyLimit, SlidingWindowLimiter


def test_sliding_window_blocks_after_the_limit_per_visitor():
    limiter = SlidingWindowLimiter(limit=2, window_seconds=600)

    assert limiter.allow("1.1.1.1")
    assert limiter.allow("1.1.1.1")
    assert not limiter.allow("1.1.1.1")
    assert limiter.allow("2.2.2.2")  # other visitors are not affected


def test_sliding_window_forgets_old_hits(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr("kapruka_agent.api.limits.time.monotonic", lambda: clock[0])
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60)

    assert limiter.allow("ip")
    clock[0] += 61
    assert limiter.allow("ip")


def test_daily_limit_counts_everyone_together():
    daily = DailyLimit(limit=2)

    assert daily.allow()
    assert daily.allow()
    assert not daily.allow()
