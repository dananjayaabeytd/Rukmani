"""
Placing the order after the customer taps "Confirm".

This is the ONLY code path that creates a Kapruka order, and it is only
reachable from the Confirm button on the checkout summary card. It:

    1. reads the conversation's pending checkout from the agent state,
    2. asks Kapruka to create the order (a real order with a pay link),
    3. saves the order in the state, so Rukmani knows it was placed.

Safeguards against duplicate orders (Kapruka allows 30 per hour per IP):
    - If the checkout was already confirmed, the existing order is returned.
    - Two clicks at the same time for one conversation are rejected.
"""

from fastapi import HTTPException
from langgraph.graph.state import CompiledStateGraph
from loguru import logger

from kapruka_agent.agent.state import get_checkout, get_order
from kapruka_agent.kapruka import KaprukaClient, KaprukaError
from kapruka_agent.kapruka.orders import Order, place_order

# Conversations with an order being placed right now.
_in_progress: set[str] = set()


async def confirm_checkout(
    agent: CompiledStateGraph, kapruka: KaprukaClient, thread_id: str
) -> Order:
    """Create the Kapruka order for this conversation's confirmed checkout."""
    config = {"configurable": {"thread_id": thread_id}}
    state = (await agent.aget_state(config)).values

    if existing := get_order(state):
        return existing  # already confirmed — don't create a second order
    quote = get_checkout(state)
    if quote is None:
        raise HTTPException(status_code=409, detail="There is no checkout to confirm.")
    if thread_id in _in_progress:
        raise HTTPException(status_code=409, detail="Your order is already being placed.")

    _in_progress.add(thread_id)
    try:
        order = await place_order(kapruka, quote)
    except KaprukaError as exc:
        logger.warning("Order rejected for thread {}: {}", thread_id, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        _in_progress.discard(thread_id)

    logger.info("Order {} created for thread {}", order.order_ref, thread_id)
    # Record it as if the agent node wrote it, so the next turn's prompt shows it.
    await agent.aupdate_state(config, {"order": order}, as_node="agent")
    return order
