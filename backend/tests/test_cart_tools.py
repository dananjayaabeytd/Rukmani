"""Cart and checkout tools update the conversation state and show cards in the UI."""

from langchain_core.messages import AIMessage, HumanMessage

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.kapruka.models import Money
from kapruka_agent.kapruka.orders import Cart, CartItem

from .conftest import CART_DELIVERY_RESULT
from .test_events import ScriptedChatModel

CHECKOUT_ARGS = {
    "recipient_name": "Amma",
    "recipient_phone": "0771234567",
    "address": "12 Temple Road",
    "city": "Kandy",
    "delivery_date": "2026-10-25",
    "sender_name": "Nimal",
}


async def _run_tool(kapruka, name: str, args: dict, cart: Cart | None = None) -> dict:
    """Run one tool through the real graph and return the saved state afterwards.

    The scripted model asks for the tool, then says "ok". The returned dict has
    the state fields plus ``tool_message``: the tool's result message.
    """
    model = ScriptedChatModel(
        replies=iter(
            [
                AIMessage("", tool_calls=[{"name": name, "args": args, "id": "call_1"}]),
                AIMessage("ok"),
            ]
        )
    )
    agent = build_agent(model, build_tools(kapruka))
    config = {"configurable": {"thread_id": "thread-cart-test"}}
    await agent.ainvoke({"messages": [HumanMessage("hi")], "cart": cart or Cart()}, config)

    state = (await agent.aget_state(config)).values
    return {**state, "tool_message": state["messages"][-2]}


def _cart_with_cake() -> Cart:
    return Cart().with_item(
        CartItem(product_id="CAKE00KA001562", name="Cake", price=Money(amount=5950))
    )


async def test_add_to_cart_saves_item_and_shows_cart(fake_kapruka):
    state = await _run_tool(
        fake_kapruka, "add_to_cart", {"product_id": "CAKE00KA001562", "icing_text": "Happy 60th"}
    )

    item = state["cart"].items[0]
    assert item.name == "Floral Fantasy Happy Birthday Cake"
    assert item.icing_text == "Happy 60th"
    assert item.image_url.endswith("cake-large.jpg")  # first photo used as the card image
    assert state["tool_message"].artifact["kind"] == "cart"


async def test_prepare_checkout_with_empty_cart_is_refused(fake_kapruka):
    state = await _run_tool(fake_kapruka, "prepare_checkout", CHECKOUT_ARGS)

    assert "cart is empty" in state["tool_message"].content
    assert state.get("checkout") is None


async def test_prepare_checkout_rejects_bad_phone(fake_kapruka):
    args = {**CHECKOUT_ARGS, "recipient_phone": "123"}

    state = await _run_tool(fake_kapruka, "prepare_checkout", args, cart=_cart_with_cake())

    assert "Sri Lankan mobile" in state["tool_message"].content


async def test_prepare_checkout_shows_summary_with_exact_fee(fake_kapruka):
    fake_kapruka.answers["kapruka_check_delivery"] = CART_DELIVERY_RESULT

    state = await _run_tool(fake_kapruka, "prepare_checkout", CHECKOUT_ARGS, cart=_cart_with_cake())

    quote = state["checkout"]
    assert quote.delivery_fee.amount == 900
    assert quote.grand_total.amount == 5950 + 900
    assert state["tool_message"].artifact["kind"] == "checkout"
    # The delivery check was made with the whole cart, so the fee is exact.
    _, params = fake_kapruka.calls[-1]
    assert params["cart"][0]["product_id"] == "CAKE00KA001562"


async def test_prepare_checkout_offers_next_date_when_full(fake_kapruka):
    # The default fake answer says the date is full and offers the next one.
    state = await _run_tool(fake_kapruka, "prepare_checkout", CHECKOUT_ARGS, cart=_cart_with_cake())

    assert "Next available date: 2026-10-25" in state["tool_message"].content
    assert state.get("checkout") is None


async def test_changing_the_cart_cancels_a_pending_checkout(fake_kapruka):
    fake_kapruka.answers["kapruka_check_delivery"] = CART_DELIVERY_RESULT
    cart = _cart_with_cake()
    model = ScriptedChatModel(
        replies=iter(
            [
                AIMessage(
                    "", tool_calls=[{"name": "prepare_checkout", "args": CHECKOUT_ARGS, "id": "c1"}]
                ),
                AIMessage(
                    "",
                    tool_calls=[
                        {
                            "name": "remove_from_cart",
                            "args": {"product_id": "CAKE00KA001562"},
                            "id": "c2",
                        }
                    ],
                ),
                AIMessage("ok"),
            ]
        )
    )
    agent = build_agent(model, build_tools(fake_kapruka))
    config = {"configurable": {"thread_id": "thread-cancel-test"}}

    await agent.ainvoke({"messages": [HumanMessage("hi")], "cart": cart}, config)

    state = (await agent.aget_state(config)).values
    assert state["cart"].is_empty
    assert state["checkout"] is None


async def test_update_cart_item_changes_icing_without_adding_another(fake_kapruka):
    state = await _run_tool(
        fake_kapruka,
        "update_cart_item",
        {"product_id": "CAKE00KA001562", "icing_text": "Happy Birthday Amma"},
        cart=_cart_with_cake(),
    )

    assert len(state["cart"].items) == 1
    assert state["cart"].items[0].quantity == 1
    assert state["cart"].items[0].icing_text == "Happy Birthday Amma"
