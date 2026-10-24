"""
The agent's conversation state, saved per thread by the checkpointer.

    messages   The chat history (LangGraph appends new messages automatically).
    cart       What the customer has picked so far.
    checkout   A summary waiting for the customer's "Confirm" click, if any.
    order      The order Kapruka created after the customer confirmed, if any.

Only tools change cart/checkout/order, and the /api/checkout route sets
``order``. Fields may be missing on a new conversation, so read them with
the helpers below rather than ``state["cart"]``.
"""

from langgraph.graph import MessagesState

from kapruka_agent.kapruka.orders import Cart, CheckoutQuote, Order


class AgentState(MessagesState):
    cart: Cart
    checkout: CheckoutQuote | None
    order: Order | None


def get_cart(state: dict) -> Cart:
    return state.get("cart") or Cart()


def get_checkout(state: dict) -> CheckoutQuote | None:
    return state.get("checkout")


def get_order(state: dict) -> Order | None:
    return state.get("order")
