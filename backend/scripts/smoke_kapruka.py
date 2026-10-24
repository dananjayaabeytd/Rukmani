"""
Smoke test against the LIVE Kapruka MCP (read-only calls, no orders).

Checks that the connection works and that Kapruka's answers still fit our
models. Run it after upgrading dependencies or if Kapruka changes its API:

    uv run python scripts/smoke_kapruka.py
"""

import asyncio

from kapruka_agent.agent.tools import build_tools
from kapruka_agent.config import get_settings
from kapruka_agent.kapruka import KaprukaClient


async def main() -> None:
    kapruka = KaprukaClient(get_settings().kapruka_mcp_url)
    await kapruka.start()
    tools = {t.name: t for t in build_tools(kapruka)}

    def call(name: str, args: dict) -> dict:
        return {"name": name, "args": args, "id": "smoke", "type": "tool_call"}

    try:
        search = await tools["search_products"].ainvoke(
            call("search_products", {"query": "birthday cake", "max_price": 8000})
        )
        print("search_products  ->", search.content[:300], "\n")
        product_id = search.artifact["products"][0]["id"]

        details = await tools["get_product_details"].ainvoke(
            call("get_product_details", {"product_id": product_id})
        )
        print("get_product      ->", details.content[:300], "\n")

        cities = await tools["find_delivery_city"].ainvoke({"name": "kandy"})
        print("find_city        ->", cities, "\n")

        delivery = await tools["check_delivery"].ainvoke(
            call("check_delivery", {"city": "Kandy", "product_id": product_id})
        )
        print("check_delivery   ->", delivery.content)
    finally:
        await kapruka.stop()


if __name__ == "__main__":
    asyncio.run(main())
