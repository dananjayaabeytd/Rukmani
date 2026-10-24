"""Overseas gift orders and the cheaper economy delivery option."""

from langchain_core.messages import AIMessage, HumanMessage

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.kapruka.models import Money
from kapruka_agent.kapruka.orders import Cart, CartItem, CheckoutDetails, CheckoutQuote, place_order

from .test_events import ScriptedChatModel

ABROAD_PRODUCT = {
    "id": "intGift00931",
    "name": "Birthday Rocher Bouquet",
    "price": {"amount": 36890, "currency": "LKR"},
    "in_stock": True,
    "images": ["https://www.kapruka.com/international_gifts/productImages/intgift00931.jpg"],
    "url": "https://www.kapruka.com/international_gifts/x",
    "international_gift": {"country": "UAE", "orderable": True},
    # Kapruka really sends this for overseas items (no Sri Lanka delivery area).
    "delivery": {"island_wide": None},
}

ABROAD_CHECK = {
    "city": None,
    "checked_date": "2026-10-28",
    "available": True,
    "delivery_fee": 13020,
    "fee_currency": "LKR",
    "fee_basis": "fixed",
}

ABROAD_CHECKOUT = {
    "recipient_name": "Sister",
    "recipient_phone": "+971 50 123 4567",
    "address": "Villa 12, Al Wasl Road",
    "city": "Dubai",
    "delivery_date": "2026-10-28",
    "sender_name": "Nimal",
    "postcode": "00000",
    "zone": "Dubai",
    "sender_email": "nimal@example.com",
}

LOCAL_CHECKOUT = {
    "recipient_name": "Amma",
    "recipient_phone": "0771234567",
    "address": "12 Temple Road",
    "city": "Jaffna",
    "delivery_date": "2026-10-25",
    "sender_name": "Nimal",
}


async def _run(kapruka, calls: list[tuple[str, dict]], cart: Cart | None = None) -> dict:
    """Run tool calls one after another through the real graph; return the final state."""
    replies = [
        AIMessage("", tool_calls=[{"name": name, "args": args, "id": f"c{i}"}])
        for i, (name, args) in enumerate(calls)
    ]
    agent = build_agent(
        ScriptedChatModel(replies=iter([*replies, AIMessage("ok")])), build_tools(kapruka)
    )
    config = {"configurable": {"thread_id": "thread-abroad"}}
    await agent.ainvoke({"messages": [HumanMessage("hi")], "cart": cart or Cart()}, config)
    state = (await agent.aget_state(config)).values
    return {**state, "tool_message": state["messages"][-2]}


async def test_overseas_item_is_marked_with_its_country(fake_kapruka):
    fake_kapruka.answers["kapruka_get_product"] = ABROAD_PRODUCT

    state = await _run(fake_kapruka, [("add_to_cart", {"product_id": "intGift00931"})])

    assert state["cart"].abroad_country == "UAE"


async def test_sri_lanka_and_overseas_items_cannot_be_mixed(fake_kapruka):
    local_cart = Cart().with_item(
        CartItem(product_id="CAKE1", name="Cake", price=Money(amount=5950))
    )
    fake_kapruka.answers["kapruka_get_product"] = ABROAD_PRODUCT

    state = await _run(fake_kapruka, [("add_to_cart", {"product_id": "intGift00931"})], local_cart)

    assert "can't mix countries" in state["tool_message"].content
    assert len(state["cart"].items) == 1


async def test_overseas_checkout_checks_the_zone_not_a_city(fake_kapruka):
    abroad_cart = Cart().with_item(
        CartItem(
            product_id="intGift00931",
            name="Birthday Rocher Bouquet",
            price=Money(amount=36890),
            abroad_country="UAE",
        )
    )
    fake_kapruka.answers["kapruka_check_delivery"] = ABROAD_CHECK

    state = await _run(fake_kapruka, [("prepare_checkout", ABROAD_CHECKOUT)], abroad_cart)

    quote = state["checkout"]
    assert quote.details.delivery_type == "international_gift"
    assert quote.details.country == "UAE"
    assert quote.details.recipient_phone == "+971501234567"
    _, params = fake_kapruka.calls[-1]
    assert params["zone"] == "Dubai" and "city" not in params


async def test_overseas_checkout_needs_a_postcode(fake_kapruka):
    abroad_cart = Cart().with_item(
        CartItem(product_id="intGift1", name="Gift", price=Money(amount=1), abroad_country="UAE")
    )
    args = {k: v for k, v in ABROAD_CHECKOUT.items() if k != "postcode"}

    state = await _run(fake_kapruka, [("prepare_checkout", args)], abroad_cart)

    assert "postcode" in state["tool_message"].content
    assert state.get("checkout") is None


async def test_economy_only_items_go_by_economy(fake_kapruka):
    cart = Cart().with_item(CartItem(product_id="BOOK1", name="Book", price=Money(amount=3000)))
    fake_kapruka.answers["kapruka_check_delivery"] = {
        "city": "Jaffna",
        "checked_date": "2026-10-25",
        "available": False,  # the chosen date doesn't matter for economy-only items
        "delivery_fee": 900,
        "fee_basis": "cart",
        "economy": {
            "available": True,
            "forced": True,
            "fee": 450,
            "promise": "Delivered in 3–5 working days",
            "delivery_date": "2026-10-29",
        },
    }

    state = await _run(fake_kapruka, [("prepare_checkout", LOCAL_CHECKOUT)], cart)

    quote = state["checkout"]
    assert quote.details.delivery_type == "economy"
    assert quote.details.delivery_date == "2026-10-29"
    assert quote.delivery_fee.amount == 450
    assert quote.delivery_promise == "Delivered in 3–5 working days"


async def test_economy_is_offered_but_not_chosen_automatically(fake_kapruka):
    cart = Cart().with_item(CartItem(product_id="BOOK1", name="Book", price=Money(amount=3000)))
    fake_kapruka.answers["kapruka_check_delivery"] = {
        "city": "Jaffna",
        "checked_date": "2026-10-25",
        "available": True,
        "delivery_fee": 900,
        "fee_basis": "cart",
        "economy": {"available": True, "forced": False, "fee": 450, "promise": "3–5 days"},
    }

    state = await _run(fake_kapruka, [("prepare_checkout", LOCAL_CHECKOUT)], cart)

    assert state["checkout"].details.delivery_type == "standard"
    assert "cheaper economy delivery is possible" in state["tool_message"].content


async def test_place_order_sends_overseas_delivery_fields(fake_kapruka):
    quote = CheckoutQuote(
        cart=Cart().with_item(
            CartItem(
                product_id="intGift1", name="Gift", price=Money(amount=1), abroad_country="UAE"
            )
        ),
        details=CheckoutDetails(
            **ABROAD_CHECKOUT,
            delivery_type="international_gift",
            country="UAE",
        ),
        delivery_fee=Money(amount=13020),
    )

    await place_order(fake_kapruka, quote)

    _, params = fake_kapruka.calls[-1]
    assert params["delivery"]["type"] == "international_gift"
    assert params["delivery"]["country"] == "UAE"
    assert params["delivery"]["zip"] == "00000"
    assert params["sender"]["email"] == "nimal@example.com"
