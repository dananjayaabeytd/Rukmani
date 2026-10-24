"""Shared test helpers: a fake Kapruka client with canned answers."""

from typing import Any

import pytest

from kapruka_agent.kapruka import KaprukaError

SEARCH_RESULT = {
    "results": [
        {
            "id": "CAKE00KA001562",
            "name": "Floral Fantasy Happy Birthday Cake",
            "price": {"amount": 5950, "currency": "LKR"},
            "compare_at_price": None,
            "in_stock": True,
            "stock_level": "low",
            "image_url": "https://static2.kapruka.com/cake.jpg",
            "url": "https://www.kapruka.com/buyonline/cake",
            "summary": "ignored by our models",
        }
    ],
    "facets": {"categories": [{"name": "Kapruka Cakes", "count": 12}]},
}

DELIVERY_RESULT = {
    "city": "Kandy",
    "checked_date": "2026-10-24",
    "available": False,
    "reason": "Today's slots for Kandy are full",
    "next_available_date": "2026-10-25",
    "item_deliverable": True,
    "delivery_fee": 1075,
    "fee_currency": "LKR",
    "fee_basis": "max",
}


class FakeKapruka:
    """Stands in for KaprukaClient: returns a canned answer per tool, or raises."""

    def __init__(self, answers: dict[str, Any]):
        self.answers = answers
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call(self, tool: str, **params: Any) -> dict[str, Any]:
        self.calls.append((tool, params))
        answer = self.answers[tool]
        if isinstance(answer, Exception):
            raise answer
        return answer


@pytest.fixture
def fake_kapruka() -> FakeKapruka:
    return FakeKapruka(
        {
            "kapruka_search_products": SEARCH_RESULT,
            "kapruka_check_delivery": DELIVERY_RESULT,
            "kapruka_list_delivery_cities": KaprukaError("Error: service busy"),
        }
    )
