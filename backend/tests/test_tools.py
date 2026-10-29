"""Tools turn Kapruka answers into (model summary, UI artifact) pairs and never raise."""

import json

from kapruka_agent.agent.tools import build_tools
from kapruka_agent.kapruka.models import DeliveryCheck

from .conftest import PRODUCT_RESULT, FakeKapruka

GIFT_COUNTRIES_RESULT = {
    "countries": [
        {
            "country": "UK",
            "products_in_stock": 42,
            "delivery_fee": {"amount": 9140, "currency": "LKR"},
            "earliest_date": "2026-10-28",
        },
        {
            "country": "UAE",
            "products_in_stock": 18,
            "delivery_fee": {"amount": 0, "currency": "LKR"},
            "zone_required": True,
            "zones": [{"name": "Dubai", "delivery_fee": {"amount": 2500, "currency": "LKR"}}],
            "earliest_date": "2026-10-27",
        },
    ]
}

UK_STORE_RESULT = {
    "country": "UK",
    "earliest_date": "2026-10-28",
    "delivery": {"country": "UK", "delivery_fee": {"amount": 9140, "currency": "LKR"}},
    "products": [
        {
            "id": "UK-CAKE-01",
            "name": "Strawberries And Cream Cake",
            "price": {"amount": 26650, "currency": "LKR"},
            "url": "https://www.kapruka.com/uk/cake",
        }
    ],
}


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


async def test_product_details_use_the_first_photo_and_say_where_it_goes(fake_kapruka):
    tool = _tools_by_name(fake_kapruka)["get_product_details"]

    message = await tool.ainvoke(_call("get_product_details", {"product_id": "CAKE00KA001562"}))

    summary = json.loads(message.content)
    assert summary["description"] == "A floral birthday cake."
    assert summary["delivery"] == {"island_wide": True}
    assert message.artifact["kind"] == "product_detail"
    # The details endpoint has no image_url, so the first photo becomes the card image.
    assert message.artifact["product"]["image_url"].endswith("cake-large.jpg")


async def test_overseas_store_product_is_delivered_in_its_country():
    overseas = PRODUCT_RESULT | {
        "delivery": {"island_wide": None},
        "international_gift": {"country": "UK"},
    }
    tool = _tools_by_name(FakeKapruka({"kapruka_get_product": overseas}))["get_product_details"]

    message = await tool.ainvoke(_call("get_product_details", {"product_id": "UK-CAKE-01"}))

    assert json.loads(message.content)["delivery"] == {"delivered_in_country": "UK"}


async def test_gift_countries_show_one_fee_or_zone_fees():
    kapruka = FakeKapruka({"kapruka_gift_countries": GIFT_COUNTRIES_RESULT})
    tool = _tools_by_name(kapruka)["list_gift_countries"]

    countries = json.loads(await tool.ainvoke({}))

    uk, uae = countries
    assert uk["delivery_fee"] == "LKR 9,140"
    assert uk["gifts_in_stock"] == 42
    # Zone-based countries list each zone's fee instead of one fee.
    assert uae["zones"] == {"Dubai": "LKR 2,500"}
    assert "delivery_fee" not in uae


async def test_browse_gift_store_returns_cards_and_delivery():
    kapruka = FakeKapruka({"kapruka_gift_country_products": UK_STORE_RESULT})
    tool = _tools_by_name(kapruka)["browse_gift_store"]

    message = await tool.ainvoke(
        _call("browse_gift_store", {"country": "UK", "gift_type": "Cakes"})
    )

    summary = json.loads(message.content)
    assert summary["delivery"]["delivery_fee"] == "LKR 9,140"
    assert summary["gifts"][0]["name"] == "Strawberries And Cream Cake"
    assert message.artifact["kind"] == "products"
    assert kapruka.calls[0] == ("kapruka_gift_country_products", {"country": "UK", "type": "Cakes"})


async def test_empty_gift_store_says_so_without_cards():
    kapruka = FakeKapruka({"kapruka_gift_country_products": {"country": "UK", "products": []}})
    tool = _tools_by_name(kapruka)["browse_gift_store"]

    message = await tool.ainvoke(_call("browse_gift_store", {"country": "UK"}))

    assert message.content == "No gifts in stock in the UK store right now."
    assert message.artifact is None


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
