"""
Cart, checkout and order placement.

The flow:
    1. Items go into a ``Cart`` (one per conversation).
    2. When the customer is ready, their details become ``CheckoutDetails``,
       and a delivery check with the whole cart gives the exact fee. Both
       are kept together as a ``CheckoutQuote`` and shown for confirmation.
    3. Only after the customer confirms, ``place_order`` asks Kapruka to
       create the order. Kapruka returns a pay link (an ``Order``) that the
       customer opens to pay. The link expires after 60 minutes.

Every model here is immutable in practice: methods return a NEW object
instead of changing the old one, which keeps conversation state safe.
"""

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from kapruka_agent.kapruka.client import KaprukaClient
from kapruka_agent.kapruka.models import Money

# Sri Lankan mobile numbers: 07XXXXXXXX or +947XXXXXXXX (spaces/dashes removed first).
_SL_MOBILE = re.compile(r"^(?:\+94|0)7\d{8}$")


# ── Cart ───────────────────────────────────────────────────────────


class CartItem(BaseModel):
    product_id: str
    name: str
    price: Money  # price of ONE item
    image_url: str | None = None
    url: str | None = None
    quantity: int = Field(default=1, ge=1, le=99)
    icing_text: str | None = Field(default=None, max_length=120)  # cakes only

    @property
    def line_total(self) -> float:
        return (self.price.amount or 0) * self.quantity


class Cart(BaseModel):
    items: list[CartItem] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.items

    @property
    def total(self) -> Money:
        return Money(amount=sum(item.line_total for item in self.items), currency="LKR")

    def with_item(self, new: CartItem) -> "Cart":
        """Add an item. If it is already in the cart, increase its quantity instead."""
        for index, item in enumerate(self.items):
            if item.product_id == new.product_id:
                merged = item.model_copy(
                    update={
                        "quantity": min(item.quantity + new.quantity, 99),
                        "icing_text": new.icing_text or item.icing_text,
                    }
                )
                return Cart(items=[*self.items[:index], merged, *self.items[index + 1 :]])
        return Cart(items=[*self.items, new])

    def without(self, product_id: str) -> "Cart":
        return Cart(items=[i for i in self.items if i.product_id.lower() != product_id.lower()])

    def find(self, product_id: str) -> CartItem | None:
        return next((i for i in self.items if i.product_id.lower() == product_id.lower()), None)

    def with_changes(
        self, product_id: str, quantity: int | None = None, icing_text: str | None = None
    ) -> "Cart":
        """Change the quantity and/or icing text of an item already in the cart.

        Arguments left as None stay as they are; an empty icing_text removes it.
        """
        changes: dict[str, Any] = {}
        if quantity is not None:
            changes["quantity"] = quantity
        if icing_text is not None:
            changes["icing_text"] = icing_text or None
        return Cart(
            items=[
                # model_validate re-checks the limits (quantity 1–99, icing ≤ 120 chars).
                CartItem.model_validate({**i.model_dump(), **changes})
                if i.product_id.lower() == product_id.lower()
                else i
                for i in self.items
            ]
        )

    def to_kapruka_lines(self) -> list[dict[str, Any]]:
        """Cart lines in the shape Kapruka's delivery check and create_order expect."""
        return [
            {"product_id": i.product_id, "quantity": i.quantity, "icing_text": i.icing_text}
            for i in self.items
        ]

    def for_llm(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    "product_id": i.product_id,
                    "name": i.name,
                    "quantity": i.quantity,
                    "line_total": Money(amount=i.line_total).label(),
                    **({"icing_text": i.icing_text} if i.icing_text else {}),
                }
                for i in self.items
            ],
            "total": self.total.label(),
        }


# ── Checkout ───────────────────────────────────────────────────────


class CheckoutDetails(BaseModel):
    """Everything Kapruka needs to deliver the order, collected in the chat."""

    recipient_name: str = Field(min_length=1, max_length=80)
    recipient_phone: str
    address: str = Field(min_length=3, max_length=250)
    city: str = Field(min_length=2, max_length=100)  # canonical Kapruka city name
    delivery_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    location_type: Literal["house", "apartment", "office", "other"] = "house"
    instructions: str | None = Field(default=None, max_length=250)
    sender_name: str = Field(min_length=1, max_length=80)
    anonymous: bool = False  # gift card shows "Anonymous" instead of the sender
    gift_message: str | None = Field(default=None, max_length=300)

    @field_validator("recipient_phone")
    @classmethod
    def _valid_mobile(cls, phone: str) -> str:
        cleaned = re.sub(r"[\s-]", "", phone)
        if not _SL_MOBILE.match(cleaned):
            raise ValueError("must be a Sri Lankan mobile number, e.g. 0771234567")
        return cleaned


class CheckoutQuote(BaseModel):
    """A checkout ready for the customer to confirm: cart + details + exact delivery fee."""

    cart: Cart
    details: CheckoutDetails
    delivery_fee: Money

    @property
    def grand_total(self) -> Money:
        return Money(amount=(self.cart.total.amount or 0) + (self.delivery_fee.amount or 0))

    def for_ui(self) -> dict[str, Any]:
        return {
            "cart": self.cart.model_dump(),
            "details": self.details.model_dump(),
            "items_total": self.cart.total.model_dump(),
            "delivery_fee": self.delivery_fee.model_dump(),
            "grand_total": self.grand_total.model_dump(),
        }


# ── Order ──────────────────────────────────────────────────────────


class Order(BaseModel):
    """An order Kapruka created. The customer pays by opening ``checkout_url``."""

    checkout_url: str
    order_ref: str
    items_total: Money
    delivery_fee: Money
    grand_total: Money  # includes any add-ons, e.g. icing text
    delivery_date: str
    expires_at: str  # ISO 8601; the pay link stops working after this

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Order":
        summary = data["summary"]
        currency = summary.get("currency", "LKR")
        return cls(
            checkout_url=data["checkout_url"],
            order_ref=data["order_ref"],
            items_total=Money(amount=summary["items_total"], currency=currency),
            delivery_fee=Money(amount=summary["delivery_fee"], currency=currency),
            grand_total=Money(amount=summary["grand_total"], currency=currency),
            delivery_date=summary["delivery_date"],
            expires_at=data["expires_at"],
        )


async def place_order(kapruka: KaprukaClient, quote: CheckoutQuote) -> Order:
    """Create a real Kapruka order from a confirmed quote and return its pay link.

    Only call this after the customer clicked "Confirm". Raises
    ``KaprukaError`` with Kapruka's message if the order is rejected.
    """
    details = quote.details
    data = await kapruka.call(
        "kapruka_create_order",
        cart=quote.cart.to_kapruka_lines(),
        recipient={"name": details.recipient_name, "phone": details.recipient_phone},
        delivery={
            "address": details.address,
            "city": details.city,
            "date": details.delivery_date,
            "location_type": details.location_type,
            "instructions": details.instructions,
            "type": "standard",
        },
        sender={"name": details.sender_name, "anonymous": details.anonymous},
        gift_message=details.gift_message,
        currency="LKR",
    )
    return Order.from_api(data)
