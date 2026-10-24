"""Confirming a checkout creates exactly one order, and only when a checkout exists."""

import pytest
from fastapi import HTTPException
from langchain_core.messages import AIMessage

from kapruka_agent.agent import build_agent
from kapruka_agent.agent.tools import build_tools
from kapruka_agent.api.checkout import confirm_checkout
from kapruka_agent.kapruka.models import Money
from kapruka_agent.kapruka.orders import Cart, CartItem, CheckoutDetails, CheckoutQuote

from .test_events import ScriptedChatModel
from .test_orders import DETAILS

THREAD = "thread-checkout-1"


def _agent(fake_kapruka):
    return build_agent(ScriptedChatModel(replies=iter([])), build_tools(fake_kapruka))


async def _with_pending_checkout(agent) -> None:
    quote = CheckoutQuote(
        cart=Cart().with_item(CartItem(product_id="CAKE1", name="Cake", price=Money(amount=5950))),
        details=CheckoutDetails(**DETAILS),
        delivery_fee=Money(amount=900),
    )
    config = {"configurable": {"thread_id": THREAD}}
    # As after a real turn: Rukmani's last message plus the pending checkout.
    await agent.aupdate_state(
        config,
        {"messages": [AIMessage("Please check and tap Confirm.")], "checkout": quote},
        as_node="agent",
    )


async def test_no_checkout_means_no_order(fake_kapruka):
    with pytest.raises(HTTPException) as error:
        await confirm_checkout(_agent(fake_kapruka), fake_kapruka, THREAD)

    assert error.value.status_code == 409
    assert not any(tool == "kapruka_create_order" for tool, _ in fake_kapruka.calls)


async def test_confirming_twice_creates_only_one_order(fake_kapruka):
    agent = _agent(fake_kapruka)
    await _with_pending_checkout(agent)

    first = await confirm_checkout(agent, fake_kapruka, THREAD)
    second = await confirm_checkout(agent, fake_kapruka, THREAD)

    assert first == second
    orders_created = [tool for tool, _ in fake_kapruka.calls if tool == "kapruka_create_order"]
    assert len(orders_created) == 1
