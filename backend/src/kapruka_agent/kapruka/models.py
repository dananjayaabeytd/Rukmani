"""
Typed views of Kapruka's JSON answers.

Kapruka returns large JSON objects. These models keep only the fields we
use, so the rest of the app works with clean, predictable data. Unknown
fields are ignored, so new fields from Kapruka never break us.

Each model has two outputs:
    - ``model_dump()``  full data for the UI (product cards, delivery panel)
    - ``for_llm()``     a small summary for the model, to save tokens
"""

from typing import Any

from pydantic import BaseModel, Field


class Money(BaseModel):
    amount: float | None = None
    currency: str = "LKR"

    def label(self) -> str:
        """Human-readable price, e.g. 'LKR 5,950'."""
        if self.amount is None:
            return "price unavailable"
        return f"{self.currency} {self.amount:,.0f}"


class ProductCard(BaseModel):
    """A product as shown on a card in the chat (from search results)."""

    id: str
    name: str
    price: Money
    compare_at_price: Money | None = None  # the pre-discount price, when on sale
    in_stock: bool = True
    stock_level: str | None = None  # "low" | "medium" | "high"
    image_url: str | None = None
    url: str

    def for_llm(self) -> dict[str, Any]:
        summary: dict[str, Any] = {"id": self.id, "name": self.name, "price": self.price.label()}
        if self.compare_at_price:
            summary["was"] = self.compare_at_price.label()
        if self.stock_level == "low":
            summary["stock"] = "low"
        return summary


class DeliveryScope(BaseModel):
    """Where a product can be delivered."""

    island_wide: bool = True
    deliverable_city_count: int | None = None  # only when island_wide is false
    deliverable_cities: list[str] = Field(default_factory=list)  # capped at 60 by Kapruka


class ProductDetail(ProductCard):
    """Full product details (from kapruka_get_product)."""

    description: str = ""
    images: list[str] = Field(default_factory=list)
    delivery: DeliveryScope | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "ProductDetail":
        product = cls.model_validate(data)
        # The details endpoint has no ``image_url``; use the first photo instead.
        if product.image_url is None and product.images:
            product.image_url = product.images[0]
        return product

    def for_llm(self) -> dict[str, Any]:
        summary = super().for_llm()
        summary["in_stock"] = self.in_stock
        # Kapruka descriptions contain long runs of spaces; collapse them to save tokens.
        summary["description"] = " ".join(self.description.split())[:600]
        if self.delivery and not self.delivery.island_wide:
            summary["delivery"] = {
                "island_wide": False,
                "city_count": self.delivery.deliverable_city_count,
                "sample_cities": self.delivery.deliverable_cities[:10],
            }
        else:
            summary["delivery"] = {"island_wide": True}
        return summary


class City(BaseModel):
    """A city Kapruka delivers to. ``name`` is the canonical spelling to send back."""

    name: str
    aliases: list[str] = Field(default_factory=list)


class OrderProgressStep(BaseModel):
    step: str
    timestamp: str | None = None


class OrderStatusItem(BaseModel):
    name: str
    quantity: int = 1


class OrderStatus(BaseModel):
    """Where a paid order is now (from kapruka_track_order).

    Kapruka also returns the recipient's phone number and street address. We
    deliberately don't keep them: anyone who knows an order number could ask,
    so only the recipient's name and city are shown.
    """

    order_number: str
    status: str  # received | confirmed | shipped | delivered | cancelled | ...
    status_display: str
    order_date: str | None = None
    delivery_date: str | None = None
    shipped_date: str | None = None
    recipient_name: str | None = None
    recipient_city: str | None = None
    progress: list[OrderProgressStep] = Field(default_factory=list)
    items: list[OrderStatusItem] = Field(default_factory=list)
    has_delivery_photo: bool = False

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "OrderStatus":
        recipient = data.get("recipient") or {}
        return cls.model_validate(
            {
                **data,
                "recipient_name": recipient.get("name"),
                "recipient_city": recipient.get("city"),
            }
        )

    def for_llm(self) -> dict[str, Any]:
        return {
            "order_number": self.order_number,
            "status": self.status_display,
            "delivery_date": self.delivery_date,
            "latest_step": self.progress[-1].step if self.progress else None,
            "items": [f"{i.quantity} × {i.name}" for i in self.items],
            "delivery_photo_available": self.has_delivery_photo,
        }


class DeliveryCheck(BaseModel):
    """Whether Kapruka can deliver to a city on a date, and the fee."""

    city: str
    checked_date: str  # YYYY-MM-DD
    available: bool
    delivery_fee: float | None = None
    fee_currency: str = "LKR"
    # "cart" = exact fee, "max" = the most it can be, "fixed" = flat USD fee
    fee_basis: str | None = None
    reason: str | None = None  # Kapruka's own wording; may be imprecise
    next_available_date: str | None = None
    item_deliverable: bool | None = None  # only present when a product was checked
    deliverable_cities: list[str] = Field(default_factory=list)
    perishable_warning: str | None = None

    def for_llm(self) -> dict[str, Any]:
        summary = self.model_dump(
            exclude_none=True,
            exclude={"delivery_fee", "fee_currency", "fee_basis", "deliverable_cities"},
        )
        if self.delivery_fee is not None:
            # Without a cart, Kapruka only knows the maximum fee — say so.
            prefix = "up to " if self.fee_basis == "max" else ""
            summary["delivery_fee"] = f"{prefix}{self.fee_currency} {self.delivery_fee:,.0f}"
        if self.deliverable_cities:
            summary["deliverable_cities"] = self.deliverable_cities[:15]
        return summary
