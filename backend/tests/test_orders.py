"""Cart rules, checkout validation and the create_order request we send to Kapruka."""

import pytest
from pydantic import ValidationError

from kapruka_agent.kapruka.models import Money
from kapruka_agent.kapruka.orders import (
    Cart,
    CartItem,
    CheckoutDetails,
    CheckoutQuote,
    place_order,
)

DETAILS = {
    "recipient_name": "Amma",
    "recipient_phone": "077 123 4567",
    "address": "12 Temple Road",
    "city": "Kandy",
    "delivery_date": "2026-10-25",
    "sender_name": "Nimal",
    "gift_message": "Happy birthday Amma!",
}


def _item(product_id: str = "CAKE1", quantity: int = 1, price: float = 5950) -> CartItem:
    return CartItem(
        product_id=product_id, name="Cake", price=Money(amount=price), quantity=quantity
    )


def test_adding_the_same_product_increases_quantity():
    cart = Cart().with_item(_item(quantity=1)).with_item(_item(quantity=2))

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 3
    assert cart.total.amount == 3 * 5950


def test_cart_changes_return_a_new_cart():
    original = Cart().with_item(_item())

    original.without("CAKE1")

    assert len(original.items) == 1  # unchanged


def test_phone_is_cleaned_and_validated():
    assert CheckoutDetails(**DETAILS).recipient_phone == "0771234567"
    with pytest.raises(ValidationError, match="Sri Lankan mobile"):
        CheckoutDetails(**{**DETAILS, "recipient_phone": "12345"})


def test_gift_message_is_limited_to_300_characters():
    with pytest.raises(ValidationError):
        CheckoutDetails(**{**DETAILS, "gift_message": "x" * 301})


async def test_place_order_sends_cart_and_details_and_returns_pay_link(fake_kapruka):
    quote = CheckoutQuote(
        cart=Cart().with_item(_item("CAKE00KA001562")),
        details=CheckoutDetails(**DETAILS),
        delivery_fee=Money(amount=900),
    )

    order = await place_order(fake_kapruka, quote)

    tool, params = fake_kapruka.calls[-1]
    assert tool == "kapruka_create_order"
    assert params["cart"] == [{"product_id": "CAKE00KA001562", "quantity": 1, "icing_text": None}]
    assert params["recipient"] == {"name": "Amma", "phone": "0771234567"}
    assert params["delivery"]["city"] == "Kandy"
    assert params["gift_message"] == "Happy birthday Amma!"
    assert order.checkout_url.endswith("abc123")
    assert order.grand_total.amount == 6850


def test_changing_an_item_keeps_one_line_and_validates_limits():
    cart = Cart().with_item(_item(quantity=1))

    changed = cart.with_changes("CAKE1", quantity=1, icing_text="Happy Birthday Amma")

    assert len(changed.items) == 1
    assert changed.items[0].quantity == 1
    assert changed.items[0].icing_text == "Happy Birthday Amma"
    assert cart.with_changes("CAKE1", icing_text="").items[0].icing_text is None
    with pytest.raises(ValidationError):
        cart.with_changes("CAKE1", quantity=100)
