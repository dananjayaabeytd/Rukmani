"""
Dependency helpers for routes.

Long-lived objects (the agent, the Kapruka client) are built once at
startup in ``main.lifespan`` and stored on ``app.state``. Routes fetch them
with these helpers via FastAPI's ``Depends``.
"""

from fastapi import HTTPException, Request
from langgraph.graph.state import CompiledStateGraph

from kapruka_agent.kapruka import KaprukaClient


def _from_state(request: Request, name: str):
    value = getattr(request.app.state, name, None)
    if value is None:
        raise HTTPException(status_code=503, detail="Server is still starting up")
    return value


def get_agent(request: Request) -> CompiledStateGraph:
    return _from_state(request, "agent")


def get_kapruka(request: Request) -> KaprukaClient:
    return _from_state(request, "kapruka")
