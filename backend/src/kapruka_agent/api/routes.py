"""
HTTP routes.

    POST /api/chat       Send a message; the reply streams back as Server-Sent Events.
    POST /api/checkout   The customer confirmed the checkout summary: place the order.
    GET  /api/health     Is the server up, and is Kapruka reachable?

Chat and checkout are rate-limited per visitor (see ``limits.py``).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from langgraph.graph.state import CompiledStateGraph
from sse_starlette import EventSourceResponse

from kapruka_agent.api.checkout import confirm_checkout
from kapruka_agent.api.deps import get_agent, get_kapruka
from kapruka_agent.api.events import stream_agent_events
from kapruka_agent.api.limits import limit_chat, limit_checkout
from kapruka_agent.api.schemas import ChatRequest, CheckoutRequest, HealthResponse
from kapruka_agent.kapruka import KaprukaClient
from kapruka_agent.kapruka.orders import Order

router = APIRouter(prefix="/api")

Agent = Annotated[CompiledStateGraph, Depends(get_agent)]
Kapruka = Annotated[KaprukaClient, Depends(get_kapruka)]


@router.post("/chat", dependencies=[Depends(limit_chat)])
async def chat(body: ChatRequest, agent: Agent, request: Request) -> EventSourceResponse:
    max_steps = request.app.state.max_agent_steps
    return EventSourceResponse(
        stream_agent_events(agent, body.thread_id, body.message, max_steps=max_steps)
    )


@router.post("/checkout", dependencies=[Depends(limit_checkout)])
async def checkout(body: CheckoutRequest, agent: Agent, kapruka: Kapruka) -> Order:
    return await confirm_checkout(agent, kapruka, body.thread_id)


@router.get("/health")
async def health(kapruka: Kapruka) -> HealthResponse:
    return HealthResponse(kapruka_connected=kapruka.is_connected)
