"""
HTTP routes.

    POST /api/chat     Send a message; the reply streams back as Server-Sent Events.
    GET  /api/health   Is the server up, and is Kapruka reachable?
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from langgraph.graph.state import CompiledStateGraph
from sse_starlette import EventSourceResponse

from kapruka_agent.api.deps import get_agent, get_kapruka
from kapruka_agent.api.events import stream_agent_events
from kapruka_agent.api.schemas import ChatRequest, HealthResponse
from kapruka_agent.kapruka import KaprukaClient

router = APIRouter(prefix="/api")

Agent = Annotated[CompiledStateGraph, Depends(get_agent)]
Kapruka = Annotated[KaprukaClient, Depends(get_kapruka)]


@router.post("/chat")
async def chat(body: ChatRequest, agent: Agent) -> EventSourceResponse:
    return EventSourceResponse(stream_agent_events(agent, body.thread_id, body.message))


@router.get("/health")
async def health(kapruka: Kapruka) -> HealthResponse:
    return HealthResponse(kapruka_connected=kapruka.is_connected)
