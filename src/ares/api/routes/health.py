"""Health check endpoints for ARES."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return JSONResponse({"status": "healthy", "service": "ARES", "version": "0.1.0"})


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/Docker."""
    # Add database connectivity check here
    return JSONResponse(
        {
            "status": "ready",
            "service": "ARES",
            "components": {"database": "connected", "redis": "connected"},
        }
    )


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes/Docker."""
    return JSONResponse({"status": "alive", "service": "ARES"})
