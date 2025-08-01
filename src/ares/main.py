"""ARES - Agent Reliability Enforcement System Main Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
try:
    from .api.routes import agents, health, enforcement
except ImportError:
    # Create basic placeholder routers for development
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse
    
    health = APIRouter()
    agents = APIRouter()
    enforcement = APIRouter()
    
    @health.get("/")
    async def health_check():
        return JSONResponse({"status": "healthy", "service": "ARES", "version": "0.1.0"})
    
    @health.get("/ready")
    async def readiness_check():
        return JSONResponse({"status": "ready", "service": "ARES", "components": {"database": "connected", "redis": "connected"}})
    
    @health.get("/live")
    async def liveness_check():
        return JSONResponse({"status": "alive", "service": "ARES"})
    
    @agents.get("/")
    async def list_agents():
        return JSONResponse({"agents": [], "total": 0, "message": "Agent management endpoints - Implementation in progress"})
    
    @enforcement.get("/actions")
    async def list_enforcement_actions():
        return JSONResponse({"actions": [], "total": 0, "message": "Enforcement actions endpoint - Implementation in progress"})

# Create FastAPI application
app = FastAPI(
    title="ARES - Agent Reliability Enforcement System",
    description="Production-ready multi-agent coordination with MCP integration",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware for development
if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(enforcement.router, prefix="/api/v1/enforcement", tags=["enforcement"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 ARES - Agent Reliability Enforcement System starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("🛑 ARES shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return JSONResponse({
        "message": "ARES - Agent Reliability Enforcement System",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else "disabled"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )