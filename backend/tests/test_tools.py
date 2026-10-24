"""Tools turn Kapruka answers into (model summary, UI artifact) pairs and never raise."""

import json

from kapruka_agent.agent.tools import build_tools
from kapruka_agent.kapruka.models import DeliveryCheck


def _tools_by_name(kapruka):
    return {t.name: t for t in build_tools(kapruka)}


def _call(tool_name: str, args: dict) -> dict:
    """A tool call in the shape the model produces (needed to get the artifact back)."""
    return {"name": tool_name, "args": args, "id": "call_1", "type": "tool_call"}


async def test_search_returns_summary_and_product_cards(fake_kapruka):
    tool = _tools_by_name(fake_kapruka)["search_products"]

    message = await tool.ainvoke(_call("search_products", {"query": "birthday cake"}))

    summary = json.loads(message.content)
    assert summary["products"][0]["price"] == "LKR 5,950"
    assert summary["category_facets"] == ["Kapruka Cakes"]
    assert message.artifact["kind"] == "products"
    assert message.artifact["products"][0]["image_url"].endswith("cake.jpg")
    # Out-of-stock items are filtered out by Kapruka for us.
    assert fake_kapruka.calls[0][1]["in_stock_only"] is True


async def test_delivery_check_says_fee_is_a_maximum(fake_kapruka):
    tool = _tools_by_name(fake_kapruka)["check_delivery"]

    message = await tool.ainvoke(
        _call("check_delivery", {"city": "Kandy", "product_id": "CAKE00KA001562"})
    )

    summary = json.loads(message.content)
    assert summary["delivery_fee"] == "up to LKR 1,075"
    assert summary["next_available_date"] == "2026-10-25"
    assert message.artifact["kind"] == "delivery"


async def test_kapruka_error_is_returned_as_text(fake_kapruka):
    tool = _tools_by_name(fake_kapruka)["find_delivery_city"]

    result = await tool.ainvoke({"name": "Kandy"})

    assert result == "Error: service busy"


def test_perishable_warning_hides_the_product_code():
    check = DeliveryCheck(
        city="Kandy",
        checked_date="2026-10-29",
        available=True,
        perishable_warning=(
            "Note: Product `CAKE00KA001562` looks like a perishable item (cake/flower/combo). "
            "Same-day or next-day delivery is recommended; freshness on 2026-10-29 is not "
            "guaranteed."
        ),
    )

    assert check.perishable_warning.startswith("This is a fresh item. Same-day or next-day")
    assert "CAKE00KA001562" not in check.perishable_warning
