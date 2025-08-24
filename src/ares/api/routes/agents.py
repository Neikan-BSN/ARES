"""Agent management endpoints for ARES."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...coordination import agent_registry, get_task_coordinator

router = APIRouter()


def get_agent_registry():
    """Get the global agent registry instance."""
    return agent_registry


async def get_task_coordinator_instance():
    """Get the global task coordinator instance."""
    return await get_task_coordinator()


@router.get("/")
async def list_agents():
    """List all registered agents."""
    return JSONResponse(
        {
            "agents": [],
            "total": 0,
            "message": "Agent management endpoints - Implementation in progress",
        }
    )


@router.post("/")
async def create_agent():
    """Register a new agent."""
    return JSONResponse(
        {"message": "Agent creation endpoint - Implementation in progress"}
    )


@router.get("/{agent_id}")
async def get_agent(agent_id: int):
    """Get agent by ID."""
    return JSONResponse(
        {
            "agent_id": agent_id,
            "message": "Agent details endpoint - Implementation in progress",
        }
    )
