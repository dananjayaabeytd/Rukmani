"""
Tools that change the cart and prepare the checkout.

Unlike the catalogue tools, these change the conversation state, so they
return a LangGraph ``Command``: "update these state fields, and add this
tool result message". The result message carries an artifact so the UI can
show the updated cart or the checkout summary.

Any change to the cart cancels a pending checkout, because the summary the
customer would confirm no longer matches the cart.

There is still no tool that PLACES an order. The checkout summary card
has a Confirm button that calls POST /api/checkout; only that creates it.
"""

import json
from typing import Annotated, Any

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from pydantic import ValidationError

from kapruka_agent.agent.state import get_cart
from kapruka_agent.kapruka import KaprukaClient, KaprukaError
from kapruka_agent.kapruka.models import DeliveryCheck, Money, ProductDetail
from kapruka_agent.kapruka.orders import Cart, CartItem, CheckoutDetails, CheckoutQuote

# Type hints that hide these arguments from the model; LangGraph fills them in.
State = Annotated[dict, InjectedState]
ToolCallId = Annotated[str, InjectedToolCallId]


def _reply(tool_call_id: str, text: str, artifact: dict[str, Any] | None = None) -> ToolMessage:
    return ToolMessage(content=text, tool_call_id=tool_call_id, artifact=artifact)


def _cart_changed(tool_call_id: str, cart: Cart, note: str) -> Command:
    """Save the new cart, cancel any pending checkout, and show the cart in the UI."""
    content = json.dumps({"note": note, "cart": cart.for_llm()}, ensure_ascii=False)
    artifact = {"kind": "cart", "cart": cart.model_dump(), "total": cart.total.model_dump()}
    return Command(
        update={
            "cart": cart,
            "checkout": None,
            "order": None,
            "messages": [_reply(tool_call_id, content, artifact)],
        }
    )


def _validation_message(error: ValidationError) -> str:
    """Turn Pydantic errors into one plain sentence the model can relay."""
    problems = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()]
    return "Some details need fixing — " + "; ".join(problems)


def build_cart_tools(kapruka: KaprukaClient) -> list[BaseTool]:
    """Create the cart and checkout tools, sharing one Kapruka client."""

    @tool
    async def add_to_cart(
        product_id: str,
        state: State,
        tool_call_id: ToolCallId,
        quantity: int = 1,
        icing_text: str | None = None,
    ) -> Command | ToolMessage:
        """Add a NEW product to the customer's cart. To change an item that is already in
        the cart (quantity or icing text), use update_cart_item instead.

        Args:
            product_id: Product id from search results, e.g. "CAKE00KA001562".
            quantity: How many, 1–99.
            icing_text: Words to write on a CAKE, up to 120 characters — only what the
                customer actually said. Never make it up; leave empty if not given.
        """
        try:
            product = ProductDetail.from_api(
                await kapruka.call("kapruka_get_product", product_id=product_id)
            )
        except KaprukaError as exc:
            return _reply(tool_call_id, str(exc))
        if not product.in_stock:
            return _reply(tool_call_id, f"{product.name} is out of stock. Suggest another.")
        abroad = product.international_gift
        if abroad and not abroad.orderable:
            return _reply(tool_call_id, f"{product.name} can't be ordered right now.")

        try:
            item = CartItem(
                product_id=product_id,
                name=product.name,
                price=product.price,
                image_url=product.image_url,
                url=product.url,
                quantity=quantity,
                icing_text=icing_text,
                abroad_country=abroad.country if abroad else None,
            )
        except ValidationError as exc:
            return _reply(tool_call_id, _validation_message(exc))

        cart = get_cart(state)
        if not cart.can_add(item):
            where = cart.abroad_country or "Sri Lanka"
            return _reply(
                tool_call_id,
                f"The cart is for delivery in {where}, and one order can't mix countries. "
                "Offer to finish this order first, or empty the cart and start a new one.",
            )
        return _cart_changed(
            tool_call_id, cart.with_item(item), f"Added {quantity} × {product.name}."
        )

    @tool
    async def update_cart_item(
        product_id: str,
        state: State,
        tool_call_id: ToolCallId,
        quantity: int | None = None,
        icing_text: str | None = None,
    ) -> Command | ToolMessage:
        """Change an item that is already in the cart: its quantity and/or icing text.

        Args:
            product_id: The product id of the cart item.
            quantity: The new total quantity, 1–99. Leave empty to keep it.
            icing_text: The new words for the cake. Empty string "" removes the icing text.
                Leave out to keep it.
        """
        cart = get_cart(state)
        item = cart.find(product_id)
        if item is None:
            return _reply(tool_call_id, f"{product_id} is not in the cart. Use add_to_cart.")
        try:
            updated = cart.with_changes(product_id, quantity=quantity, icing_text=icing_text)
        except ValidationError as exc:
            return _reply(tool_call_id, _validation_message(exc))
        return _cart_changed(tool_call_id, updated, f"Updated {item.name}.")

    @tool
    async def remove_from_cart(
        product_id: str, state: State, tool_call_id: ToolCallId
    ) -> Command | ToolMessage:
        """Remove a product from the customer's cart.

        Args:
            product_id: The product id of the cart item to remove.
        """
        cart = get_cart(state)
        updated = cart.without(product_id)
        if len(updated.items) == len(cart.items):
            return _reply(tool_call_id, f"{product_id} is not in the cart.")
        return _cart_changed(tool_call_id, updated, f"Removed {product_id}.")

    @tool
    async def prepare_checkout(
        recipient_name: str,
        recipient_phone: str,
        address: str,
        city: str,
        delivery_date: str,
        sender_name: str,
        state: State,
        tool_call_id: ToolCallId,
        gift_message: str | None = None,
        anonymous: bool = False,
        location_type: str = "house",
        instructions: str | None = None,
        economy: bool = False,
        postcode: str | None = None,
        zone: str | None = None,
        sender_email: str | None = None,
    ) -> Command | ToolMessage:
        """Check delivery for the whole cart and show the customer a checkout summary
        with a Confirm button. Call this once you have every required detail.

        You cannot place the order yourself: the customer taps Confirm on the summary.

        Args:
            recipient_name: Who receives the gift.
            recipient_phone: Recipient's phone. Sri Lanka: a mobile like 0771234567.
                Overseas: their number in that country.
            address: Street address for delivery.
            city: Sri Lanka: exact Kapruka city name from find_delivery_city.
                Overseas: the recipient's town, as written.
            delivery_date: YYYY-MM-DD (Sri Lanka time). Overseas: at least 3 days ahead.
            sender_name: Who the gift is from (shown on the gift card).
            gift_message: Message for the gift card, up to 300 characters, in any language.
            anonymous: True to show "Anonymous" instead of the sender's name.
            location_type: house, apartment, office or other.
            instructions: Optional notes for the delivery rider.
            economy: True if the customer chose the cheaper economy delivery you offered.
            postcode: OVERSEAS ONLY (required): the recipient's postcode / ZIP.
            zone: OVERSEAS ONLY: required for Australia and the UAE — one of the store's zones.
            sender_email: OVERSEAS: the sender's email, so Kapruka can send updates.
        """
        cart = get_cart(state)
        if cart.is_empty:
            return _reply(tool_call_id, "The cart is empty. Add items before checking out.")

        abroad = cart.abroad_country  # None = delivery within Sri Lanka
        try:
            details = CheckoutDetails(
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                address=address,
                city=city,
                delivery_date=delivery_date,
                sender_name=sender_name,
                sender_email=sender_email,
                gift_message=gift_message,
                anonymous=anonymous,
                location_type=location_type,
                instructions=instructions,
                delivery_type="international_gift" if abroad else "standard",
                country=abroad,
                postcode=postcode,
                zone=zone,
            )
        except ValidationError as exc:
            return _reply(tool_call_id, _validation_message(exc))

        # Checking with the whole cart gives the EXACT fee the order will charge.
        try:
            check = DeliveryCheck.model_validate(
                await kapruka.call("kapruka_check_delivery", **_delivery_check_args(cart, details))
            )
        except KaprukaError as exc:
            return _reply(tool_call_id, str(exc))

        if problem := _delivery_problem(check, details):
            return _reply(tool_call_id, problem)

        quote = _quote(cart, details, check, wants_economy=economy)
        content = (
            f"Checkout summary card shown with a Confirm button. Grand total "
            f"{quote.grand_total.label()} (delivery {quote.delivery_fee.label()}). "
            "The card already lists every detail, so do NOT repeat them. In one short "
            "sentence, ask the customer to check the card and tap Confirm to get the "
            "payment link."
        )
        offer = check.economy
        if quote.details.delivery_type == "economy":
            content += f" It goes by economy delivery: {quote.delivery_promise}."
            if offer and offer.forced:
                content += " (These items go by economy only.)"
        elif offer and offer.available:
            content += (
                f" A cheaper economy delivery is possible: {offer.for_llm()}. Offer it briefly; "
                "if they want it, call prepare_checkout again with economy=true."
            )
        elif economy:
            content += " Economy delivery isn't available for this order, so it's standard."
        if check.perishable_warning:
            content += f" Freshness note to mention: {check.perishable_warning}"

        artifact = {"kind": "checkout", "quote": quote.for_ui()}
        return Command(
            update={
                "checkout": quote,
                "order": None,
                "messages": [_reply(tool_call_id, content, artifact)],
            }
        )

    return [add_to_cart, update_cart_item, remove_from_cart, prepare_checkout]


# ── Checkout helpers ───────────────────────────────────────────────


def _delivery_check_args(cart: Cart, details: CheckoutDetails) -> dict[str, Any]:
    """Arguments for kapruka_check_delivery that match the order we're about to place."""
    args: dict[str, Any] = {
        "delivery_date": details.delivery_date,
        "cart": cart.to_kapruka_lines(),
        "gift_message": details.gift_message,
        "currency": "LKR",
    }
    if details.delivery_type == "international_gift":
        args["zone"] = details.zone  # overseas: the country comes from the items
    else:
        args["city"] = details.city
        # With a single item, Kapruka also checks that item's delivery area and
        # same-day rules.
        if len(cart.items) == 1:
            args["product_id"] = cart.items[0].product_id
    return args


def _delivery_problem(check: DeliveryCheck, details: CheckoutDetails) -> str | None:
    """Why this order can't be delivered as asked, or None if it can."""
    if check.item_deliverable is False:
        cities = ", ".join(check.deliverable_cities[:15])
        return f"This cart can't be delivered to {details.city}. It can go to: {cities}."
    economy_only = check.economy is not None and check.economy.forced
    if not check.available and not economy_only:
        next_date = check.next_available_date or "a later date"
        return (
            f"{details.delivery_date} is not available. Next available date: {next_date}. "
            "Ask the customer."
        )
    return None


def _quote(
    cart: Cart, details: CheckoutDetails, check: DeliveryCheck, wants_economy: bool
) -> CheckoutQuote:
    """Build the summary to confirm, using economy delivery when chosen or required."""
    offer = check.economy
    if offer and offer.available and (offer.forced or wants_economy):
        economy_details = details.model_copy(
            update={
                "delivery_type": "economy",
                # Kapruka sets the date for economy orders itself.
                "delivery_date": offer.delivery_date or details.delivery_date,
            }
        )
        return CheckoutQuote(
            cart=cart,
            details=economy_details,
            delivery_fee=Money(amount=offer.fee, currency=offer.currency),
            delivery_promise=offer.promise,
        )
    return CheckoutQuote(
        cart=cart,
        details=details,
        delivery_fee=Money(amount=check.delivery_fee, currency=check.fee_currency),
    )
