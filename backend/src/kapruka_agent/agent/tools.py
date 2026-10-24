"""
Tools the agent can call.

Each tool wraps one Kapruka MCP call and returns TWO things
(LangChain's ``content_and_artifact`` format):

    content   A short JSON summary for the model to reason about.
    artifact  The full data for the UI (product cards, delivery panel).
              The model never sees it; the API streams it to the browser.

Tools never raise. If Kapruka fails or finds nothing, the tool returns the
reason as text so the model can explain it or try something else.

Cart and checkout tools live in ``cart_tools.py``. Placing orders is
deliberately NOT a tool: the customer confirms checkout in the UI, so the
model can never create an order by itself.
"""

import json
from typing import Any, Literal

from langchain_core.tools import BaseTool, tool

from kapruka_agent.agent.cart_tools import build_cart_tools
from kapruka_agent.kapruka import KaprukaClient, KaprukaError
from kapruka_agent.kapruka.models import City, DeliveryCheck, ProductCard, ProductDetail

# How many search results to show as cards in one reply.
_SEARCH_LIMIT = 8

# What a tool returns: (content for the model, artifact for the UI or None).
ToolResult = tuple[str, dict[str, Any] | None]


def _to_json(data: Any) -> str:
    # ensure_ascii=False keeps Sinhala text readable instead of \u escapes.
    return json.dumps(data, ensure_ascii=False)


def build_tools(kapruka: KaprukaClient) -> list[BaseTool]:
    """Create the agent's tools, all sharing one Kapruka client."""

    @tool(response_format="content_and_artifact")
    async def search_products(
        query: str,
        max_price: float | None = None,
        min_price: float | None = None,
        category: str | None = None,
        sort: Literal["relevance", "price_asc", "price_desc", "newest", "bestseller"] = "relevance",
    ) -> ToolResult:
        """Search the Kapruka catalogue. Results are shown to the customer as product cards.

        Args:
            query: Short ENGLISH keywords for the thing wanted, e.g. "birthday cake",
                "red roses", "chocolate hamper". Translate Sinhala or Singlish first.
                Kapruka matches ANY word, so keep it to the main noun plus one detail.
            max_price: Highest price in LKR, when the customer gave a budget.
            min_price: Lowest price in LKR.
            category: A facet name returned by an earlier search (category_facets),
                to narrow results. Leave empty on the first search.
            sort: Result order. Use "bestseller" for "popular" requests.
        """
        try:
            data = await kapruka.call(
                "kapruka_search_products",
                q=query,
                max_price=max_price,
                min_price=min_price,
                category=category,
                sort=sort,
                in_stock_only=True,
                limit=_SEARCH_LIMIT,
            )
        except KaprukaError as exc:
            return str(exc), None

        products = [ProductCard.model_validate(row) for row in data.get("results", [])]
        if not products:
            return f"No products found for '{query}'.", None

        facets = [facet["name"] for facet in data.get("facets", {}).get("categories", [])][:12]
        content = _to_json({"products": [p.for_llm() for p in products], "category_facets": facets})
        artifact = {
            "kind": "products",
            "query": query,
            "products": [p.model_dump() for p in products],
        }
        return content, artifact

    @tool(response_format="content_and_artifact")
    async def get_product_details(product_id: str) -> ToolResult:
        """Get full details of one product: description, photos, stock and WHERE it can be
        delivered. Use before recommending an item strongly or when the customer asks about it.

        Args:
            product_id: The product id from search results, e.g. "CAKE00KA001562".
        """
        try:
            data = await kapruka.call("kapruka_get_product", product_id=product_id)
        except KaprukaError as exc:
            return str(exc), None

        product = ProductDetail.from_api(data)
        artifact = {"kind": "product_detail", "product": product.model_dump()}
        return _to_json(product.for_llm()), artifact

    @tool
    async def find_delivery_city(name: str) -> str:
        """Find the exact Kapruka spelling of a Sri Lankan city or town. Always do this before
        check_delivery, because Kapruka only accepts its own city names.

        Args:
            name: The place the customer mentioned, e.g. "Kandy", "Nugegoda", "col 3".
        """
        try:
            data = await kapruka.call("kapruka_list_delivery_cities", query=name, limit=8)
        except KaprukaError as exc:
            return str(exc)

        cities = [City.model_validate(row) for row in data.get("cities", [])]
        if not cities:
            return f"No Kapruka delivery city matches '{name}'. Ask the customer for a nearby town."
        return _to_json([city.model_dump() for city in cities])

    @tool(response_format="content_and_artifact")
    async def check_delivery(
        city: str,
        delivery_date: str | None = None,
        product_id: str | None = None,
    ) -> ToolResult:
        """Check if Kapruka can deliver to a city on a date, and the delivery fee.

        Always pass product_id once the customer has picked an item: some items (restaurant
        food, hotel cakes) only reach certain cities, and same-day rules depend on the item.
        If the date is not available, offer next_available_date.

        Args:
            city: Exact city name from find_delivery_city.
            delivery_date: Date in YYYY-MM-DD (Sri Lanka time). Leave empty for today.
            product_id: The chosen product's id, if any.
        """
        try:
            data = await kapruka.call(
                "kapruka_check_delivery",
                city=city,
                delivery_date=delivery_date,
                product_id=product_id,
            )
        except KaprukaError as exc:
            return str(exc), None

        check = DeliveryCheck.model_validate(data)
        artifact = {"kind": "delivery", "product_id": product_id, "delivery": check.model_dump()}
        return _to_json(check.for_llm()), artifact

    catalogue_tools = [search_products, get_product_details, find_delivery_city, check_delivery]
    return [*catalogue_tools, *build_cart_tools(kapruka)]
