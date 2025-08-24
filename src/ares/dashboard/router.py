"""FastAPI router for ARES web dashboard."""

import asyncio
import json
import logging
from datetime import datetime, timedelta

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .schemas import (
    AgentStatus,
    DashboardStats,
    RealtimeUpdate,
    VerificationActivity,
)

logger = logging.getLogger(__name__)

# Initialize router and templates
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="src/ares/dashboard/templates")


class ConnectionManager:
    """WebSocket connection manager for real-time updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.agent_monitors: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.remove(websocket)
        # Remove from agent monitors
        for _agent_id, connections in self.agent_monitors.items():
            if websocket in connections:
                connections.remove(websocket)
                break

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Connection is broken, remove it
                self.active_connections.remove(connection)

    async def send_agent_update(self, agent_id: str, update: dict):
        """Send update to clients monitoring specific agent."""
        if agent_id in self.agent_monitors:
            message = json.dumps(update)
            for connection in self.agent_monitors[agent_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    # Connection is broken, remove it
                    self.agent_monitors[agent_id].remove(connection)

    def monitor_agent(self, agent_id: str, websocket: WebSocket):
        """Add WebSocket to agent monitoring list."""
        if agent_id not in self.agent_monitors:
            self.agent_monitors[agent_id] = []
        self.agent_monitors[agent_id].append(websocket)


# Global connection manager
manager = ConnectionManager()


# ==============================================================================
# HTML DASHBOARD ROUTES
# ==============================================================================


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard home page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "ARES Dashboard", "active_page": "dashboard"},
    )


@router.get("/agents", response_class=HTMLResponse)
async def agents_dashboard(request: Request):
    """Agents monitoring dashboard."""
    return templates.TemplateResponse(
        "agents.html",
        {"request": request, "title": "Agent Monitoring", "active_page": "agents"},
    )


@router.get("/verification", response_class=HTMLResponse)
async def verification_dashboard(request: Request):
    """Verification activity dashboard."""
    return templates.TemplateResponse(
        "verification.html",
        {
            "request": request,
            "title": "Verification Activity",
            "active_page": "verification",
        },
    )


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Analytics and trends dashboard."""
    return templates.TemplateResponse(
        "analytics.html",
        {"request": request, "title": "Analytics & Trends", "active_page": "analytics"},
    )


# ==============================================================================
# API ENDPOINTS FOR DASHBOARD DATA
# ==============================================================================


@router.get("/api/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get overall dashboard statistics."""
    # Placeholder implementation - would query database
    return DashboardStats(
        total_agents=15,
        active_agents=12,
        total_verifications_today=127,
        successful_verifications=98,
        failed_verifications=18,
        pending_verifications=11,
        average_quality_score=0.84,
        system_health="healthy",
        uptime_seconds=86400,
        last_updated=datetime.utcnow(),
    )


@router.get("/api/agents", response_model=list[AgentStatus])
async def get_agent_statuses():
    """Get status of all agents."""
    # Placeholder implementation - would query database
    agents = []
    for i in range(1, 16):
        agent = AgentStatus(
            agent_id=f"agent_{i:03d}",
            name=f"Agent {i}",
            status="active" if i <= 12 else "inactive",
            last_seen=datetime.utcnow() - timedelta(minutes=i * 2),
            current_task=f"task_{i + 100}" if i <= 8 else None,
            reliability_score=0.75 + (i % 5) * 0.05,
            total_tasks_completed=50 + i * 10,
            success_rate=0.80 + (i % 10) * 0.02,
            average_quality_score=0.70 + (i % 8) * 0.03,
        )
        agents.append(agent)

    return agents


@router.get("/api/agents/{agent_id}", response_model=AgentStatus)
async def get_agent_status(agent_id: str):
    """Get detailed status of specific agent."""
    # Placeholder implementation - would query database
    return AgentStatus(
        agent_id=agent_id,
        name=f"Agent {agent_id.split('_')[-1]}",
        status="active",
        last_seen=datetime.utcnow(),
        current_task="task_analysis_456",
        reliability_score=0.87,
        total_tasks_completed=156,
        success_rate=0.89,
        average_quality_score=0.82,
        recent_activities=[
            "Completed task verification",
            "Validated 3 tool calls",
            "Generated quality report",
        ],
    )


@router.get("/api/verification/activity", response_model=list[VerificationActivity])
async def get_verification_activity(limit: int = 50):
    """Get recent verification activity."""
    # Placeholder implementation - would query database
    activities = []
    for i in range(limit):
        activity = VerificationActivity(
            id=f"verify_{i:03d}",
            type=(
                "task_completion"
                if i % 3 == 0
                else "tool_validation"
                if i % 3 == 1
                else "proof_of_work"
            ),
            agent_id=f"agent_{(i % 10) + 1:03d}",
            task_id=f"task_{i + 200}",
            status="completed" if i % 4 != 3 else "failed",
            quality_score=0.60 + (i % 10) * 0.04,
            timestamp=datetime.utcnow() - timedelta(minutes=i * 5),
            duration_ms=500 + i * 20,
        )
        activities.append(activity)

    return activities


@router.get("/api/metrics/trends")
async def get_metrics_trends(days: int = 7):
    """Get quality and performance trends."""
    # Placeholder implementation - would calculate from database
    trends = []
    base_date = datetime.utcnow() - timedelta(days=days)

    for i in range(days):
        date = base_date + timedelta(days=i)
        trend_data = {
            "date": date.isoformat(),
            "quality_score": 0.75 + (i % 3) * 0.05,
            "verification_count": 80 + i * 10,
            "success_rate": 0.85 + (i % 4) * 0.03,
            "average_duration_ms": 800 - i * 20,
        }
        trends.append(trend_data)

    return {"trends": trends, "period_days": days}


# ==============================================================================
# WEBSOCKET ENDPOINTS FOR REAL-TIME UPDATES
# ==============================================================================


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time dashboard updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message_data.get("type") == "subscribe_stats":
                # Start sending periodic stats updates
                await _send_stats_update(websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/agent/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for monitoring specific agent."""
    await manager.connect(websocket)
    manager.monitor_agent(agent_id, websocket)

    try:
        # Send initial agent status
        await _send_agent_update(websocket, agent_id)

        while True:
            # Wait for messages
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "get_status":
                await _send_agent_update(websocket, agent_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def _send_stats_update(websocket: WebSocket):
    """Send periodic statistics updates."""
    try:
        stats = await get_dashboard_stats()
        update = RealtimeUpdate(
            type="stats_update",
            data=stats.dict(),
            timestamp=datetime.utcnow(),
        )
        await websocket.send_text(update.json())
    except Exception as e:
        # Connection might be closed, log error if needed
        logger.debug(f"WebSocket connection error: {e}")


async def _send_agent_update(websocket: WebSocket, agent_id: str):
    """Send agent status update."""
    try:
        agent_status = await get_agent_status(agent_id)
        update = RealtimeUpdate(
            type="agent_update",
            data=agent_status.dict(),
            timestamp=datetime.utcnow(),
        )
        await websocket.send_text(update.json())
    except Exception as e:
        # Connection might be closed, log error if needed
        logger.debug(f"WebSocket connection error: {e}")


# ==============================================================================
# BACKGROUND TASKS FOR REAL-TIME MONITORING
# ==============================================================================


async def start_background_monitoring():
    """Start background tasks for real-time monitoring."""
    asyncio.create_task(periodic_stats_broadcast())
    asyncio.create_task(monitor_agent_activities())


async def periodic_stats_broadcast():
    """Periodically broadcast system statistics."""
    while True:
        try:
            stats = await get_dashboard_stats()
            update = RealtimeUpdate(
                type="stats_broadcast",
                data=stats.dict(),
                timestamp=datetime.utcnow(),
            )
            await manager.broadcast(update.json())
            await asyncio.sleep(30)  # Broadcast every 30 seconds
        except Exception as e:
            print(f"Error in stats broadcast: {e}")
            await asyncio.sleep(60)  # Wait longer on error


async def monitor_agent_activities():
    """Monitor and broadcast agent activity updates."""
    while True:
        try:
            # Check for agent activity changes
            agents = await get_agent_statuses()
            for agent in agents:
                if agent.status == "active":
                    update_data = {
                        "type": "agent_activity",
                        "agent_id": agent.agent_id,
                        "activity": "status_check",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await manager.send_agent_update(agent.agent_id, update_data)

            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            print(f"Error in agent monitoring: {e}")
            await asyncio.sleep(120)  # Wait longer on error


# ==============================================================================
# VERIFICATION INTEGRATION ENDPOINTS
# ==============================================================================


@router.post("/api/verification/task")
async def trigger_task_verification(
    agent_id: str,
    task_id: str,
    completion_data: dict,
):
    """Trigger task completion verification and broadcast results."""
    try:
        # This would integrate with the actual verification system
        # For now, simulate verification
        await asyncio.sleep(2)  # Simulate processing time

        # Broadcast verification result
        result_data = {
            "type": "verification_completed",
            "agent_id": agent_id,
            "task_id": task_id,
            "status": "completed",
            "quality_score": 0.85,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await manager.broadcast(json.dumps(result_data))

        return {"status": "success", "message": "Verification completed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/health")
async def dashboard_health():
    """Dashboard health check endpoint."""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "monitored_agents": len(manager.agent_monitors),
        "timestamp": datetime.utcnow().isoformat(),
    }
