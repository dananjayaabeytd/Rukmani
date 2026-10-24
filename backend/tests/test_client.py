"""The Kapruka client reconnects after a dead connection, but never repeats an order."""

import json
from types import SimpleNamespace

import pytest

from kapruka_agent.kapruka import KaprukaClient, KaprukaError
from kapruka_agent.kapruka import client as client_module


class FakeConnection:
    """Stands in for the MCP Client. The first connection is 'dead' (every call fails)."""

    opened = 0

    def __init__(self, url, read_timeout_seconds=None):
        FakeConnection.opened += 1
        self.dead = FakeConnection.opened == 1
        self.calls: list[str] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def call_tool(self, tool, arguments):
        self.calls.append(tool)
        if self.dead:
            raise ConnectionError("connection reset")
        text = json.dumps({"cities": [{"name": "Kandy", "aliases": []}]})
        return SimpleNamespace(content=[SimpleNamespace(text=text)], is_error=False)


@pytest.fixture
def kapruka(monkeypatch):
    FakeConnection.opened = 0
    monkeypatch.setattr(client_module, "Client", FakeConnection)
    return KaprukaClient("https://example.test/mcp", timeout_seconds=2)


async def test_dead_connection_is_replaced_and_the_call_retried(kapruka):
    await kapruka.start()
    try:
        data = await kapruka.call("kapruka_list_delivery_cities", query="kandy")
    finally:
        await kapruka.stop()

    assert data["cities"][0]["name"] == "Kandy"
    assert FakeConnection.opened == 2  # reconnected once


async def test_orders_are_never_retried(kapruka):
    await kapruka.start()
    try:
        with pytest.raises(KaprukaError):
            await kapruka.call("kapruka_create_order", cart=[])
    finally:
        await kapruka.stop()
