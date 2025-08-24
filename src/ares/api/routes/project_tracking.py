"""FastAPI routes for project tracking and documentation management."""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.base import get_async_session
from ...models.project_tracking import (
    AgentActivity,
    AgentWorkflow,
    IntegrationCheckpoint,
    ProjectMilestone,
    TechnicalDebtItem,
)
from ...services.documentation_service import DocumentationService
from .schemas.project_tracking import (
    AgentActivityCreate,
    AgentActivityResponse,
    AgentWorkflowCreate,
    AgentWorkflowResponse,
    IntegrationCheckpointCreate,
    IntegrationCheckpointResponse,
    ProjectMilestoneCreate,
    ProjectMilestoneResponse,
    ProjectOverviewResponse,
    TechnicalDebtCreate,
    TechnicalDebtResponse,
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/project", tags=["project-tracking"])

# Documentation service instance
doc_service = DocumentationService()


# WebSocket connection manager for real-time updates
class ProjectWebSocketManager:
    """WebSocket manager for real-time project updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
            )

    async def broadcast_update(self, update_type: str, data: dict):
        """Broadcast update to all connected clients."""
        message = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Send to all connections, remove failed ones
        failed_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                failed_connections.append(connection)

        # Clean up failed connections
        for failed in failed_connections:
            self.disconnect(failed)


# Global WebSocket manager
ws_manager = ProjectWebSocketManager()


# ==============================================================================
# PROJECT MILESTONES ENDPOINTS
# ==============================================================================


@router.get("/milestones", response_model=list[ProjectMilestoneResponse])
async def get_project_milestones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    component: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    """Get project milestones with optional filtering."""
    try:
        query = select(ProjectMilestone).order_by(desc(ProjectMilestone.updated_at))

        if component:
            query = query.where(ProjectMilestone.component == component)

        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        milestones = result.scalars().all()

        return [
            ProjectMilestoneResponse.model_validate(milestone)
            for milestone in milestones
        ]

    except Exception as e:
        logger.error(f"Error retrieving milestones: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve milestones"
        ) from e


@router.post("/milestones", response_model=ProjectMilestoneResponse)
async def create_milestone(
    milestone_data: ProjectMilestoneCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new project milestone."""
    try:
        milestone = ProjectMilestone(**milestone_data.model_dump())
        session.add(milestone)
        await session.commit()
        await session.refresh(milestone)

        # Broadcast update
        await ws_manager.broadcast_update(
            "milestone_created",
            {
                "id": str(milestone.id),
                "title": milestone.title,
                "component": milestone.component.value,
                "completion_percentage": float(milestone.completion_percentage),
            },
        )

        # Trigger document update
        await doc_service.update_all_documents()

        return ProjectMilestoneResponse.model_validate(milestone)

    except Exception as e:
        logger.error(f"Error creating milestone: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create milestone") from e


@router.get("/milestones/{milestone_id}", response_model=ProjectMilestoneResponse)
async def get_milestone(
    milestone_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Get specific milestone by ID."""
    try:
        query = select(ProjectMilestone).where(ProjectMilestone.id == milestone_id)
        result = await session.execute(query)
        milestone = result.scalar_one_or_none()

        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone not found")

        return ProjectMilestoneResponse.model_validate(milestone)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving milestone {milestone_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve milestone"
        ) from e


@router.put("/milestones/{milestone_id}/progress")
async def update_milestone_progress(
    milestone_id: UUID,
    completion_percentage: float = Query(..., ge=0, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    """Update milestone completion percentage."""
    try:
        query = select(ProjectMilestone).where(ProjectMilestone.id == milestone_id)
        result = await session.execute(query)
        milestone = result.scalar_one_or_none()

        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone not found")

        milestone.completion_percentage = completion_percentage
        milestone.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(milestone)

        # Broadcast update
        await ws_manager.broadcast_update(
            "milestone_updated",
            {
                "id": str(milestone.id),
                "title": milestone.title,
                "completion_percentage": float(completion_percentage),
            },
        )

        # Trigger document update
        await doc_service.update_all_documents()

        return {
            "message": "Milestone progress updated",
            "completion_percentage": completion_percentage,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating milestone progress: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to update milestone progress"
        ) from e


# ==============================================================================
# AGENT WORKFLOWS ENDPOINTS
# ==============================================================================


@router.get("/workflows", response_model=list[AgentWorkflowResponse])
async def get_agent_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str | None = Query(None),
    assigned_agent: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    """Get agent workflows with optional filtering."""
    try:
        query = (
            select(AgentWorkflow)
            .options(selectinload(AgentWorkflow.associated_milestones))
            .order_by(desc(AgentWorkflow.updated_at))
        )

        if status:
            query = query.where(AgentWorkflow.status == status)
        if assigned_agent:
            query = query.where(AgentWorkflow.assigned_agent == assigned_agent)

        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        workflows = result.scalars().all()

        return [
            AgentWorkflowResponse.model_validate(workflow) for workflow in workflows
        ]

    except Exception as e:
        logger.error(f"Error retrieving workflows: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve workflows"
        ) from e


@router.post("/workflows", response_model=AgentWorkflowResponse)
async def create_workflow(
    workflow_data: AgentWorkflowCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new agent workflow."""
    try:
        workflow = AgentWorkflow(**workflow_data.model_dump(exclude={"milestone_ids"}))

        # Associate with milestones if provided
        if workflow_data.milestone_ids:
            milestone_query = select(ProjectMilestone).where(
                ProjectMilestone.id.in_(workflow_data.milestone_ids)
            )
            milestone_result = await session.execute(milestone_query)
            milestones = milestone_result.scalars().all()
            workflow.associated_milestones = milestones

        session.add(workflow)
        await session.commit()
        await session.refresh(workflow, ["associated_milestones"])

        # Broadcast update
        await ws_manager.broadcast_update(
            "workflow_created",
            {
                "id": str(workflow.id),
                "workflow_name": workflow.workflow_name,
                "assigned_agent": workflow.assigned_agent,
                "status": workflow.status.value,
            },
        )

        return AgentWorkflowResponse.model_validate(workflow)

    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create workflow") from e


@router.put("/workflows/{workflow_id}/status")
async def update_workflow_status(
    workflow_id: UUID,
    status: str,
    progress_percentage: float | None = Query(None, ge=0, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    """Update workflow status and progress."""
    try:
        query = select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
        result = await session.execute(query)
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        workflow.status = status
        if progress_percentage is not None:
            workflow.progress_percentage = progress_percentage
        workflow.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(workflow)

        # Broadcast update
        await ws_manager.broadcast_update(
            "workflow_updated",
            {
                "id": str(workflow.id),
                "workflow_name": workflow.workflow_name,
                "status": status,
                "progress_percentage": float(workflow.progress_percentage),
            },
        )

        # Trigger document update for active workflows
        await doc_service.update_all_documents()

        return {"message": "Workflow status updated", "status": status}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow status: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to update workflow status"
        ) from e


# ==============================================================================
# TECHNICAL DEBT ENDPOINTS
# ==============================================================================


@router.get("/technical-debt", response_model=list[TechnicalDebtResponse])
async def get_technical_debt(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    priority: str | None = Query(None),
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    """Get technical debt items with optional filtering."""
    try:
        query = select(TechnicalDebtItem).order_by(
            TechnicalDebtItem.priority.desc(), desc(TechnicalDebtItem.created_at)
        )

        if priority:
            query = query.where(TechnicalDebtItem.priority == priority)
        if status:
            query = query.where(TechnicalDebtItem.status == status)

        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        debt_items = result.scalars().all()

        return [TechnicalDebtResponse.model_validate(item) for item in debt_items]

    except Exception as e:
        logger.error(f"Error retrieving technical debt: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve technical debt"
        ) from e


@router.post("/technical-debt", response_model=TechnicalDebtResponse)
async def create_technical_debt(
    debt_data: TechnicalDebtCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new technical debt item."""
    try:
        debt_item = TechnicalDebtItem(**debt_data.model_dump())
        session.add(debt_item)
        await session.commit()
        await session.refresh(debt_item)

        # Broadcast update
        await ws_manager.broadcast_update(
            "debt_created",
            {
                "id": str(debt_item.id),
                "title": debt_item.title,
                "priority": debt_item.priority.value,
                "status": debt_item.status.value,
            },
        )

        # Trigger document update
        await doc_service.update_all_documents()

        return TechnicalDebtResponse.model_validate(debt_item)

    except Exception as e:
        logger.error(f"Error creating technical debt: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create technical debt"
        ) from e


@router.put("/technical-debt/{debt_id}/status")
async def update_debt_status(
    debt_id: UUID,
    status: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Update technical debt item status."""
    try:
        query = select(TechnicalDebtItem).where(TechnicalDebtItem.id == debt_id)
        result = await session.execute(query)
        debt_item = result.scalar_one_or_none()

        if not debt_item:
            raise HTTPException(status_code=404, detail="Technical debt item not found")

        debt_item.status = status
        debt_item.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(debt_item)

        # Broadcast update
        await ws_manager.broadcast_update(
            "debt_updated",
            {"id": str(debt_item.id), "title": debt_item.title, "status": status},
        )

        # Trigger document update
        await doc_service.update_all_documents()

        return {"message": "Technical debt status updated", "status": status}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating debt status: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to update debt status"
        ) from e


# ==============================================================================
# INTEGRATION CHECKPOINTS ENDPOINTS
# ==============================================================================


@router.get(
    "/integration-checkpoints", response_model=list[IntegrationCheckpointResponse]
)
async def get_integration_checkpoints(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    """Get integration checkpoints with optional filtering."""
    try:
        query = select(IntegrationCheckpoint).order_by(
            desc(IntegrationCheckpoint.last_verified)
        )

        if status:
            query = query.where(IntegrationCheckpoint.status == status)

        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        checkpoints = result.scalars().all()

        return [IntegrationCheckpointResponse.model_validate(cp) for cp in checkpoints]

    except Exception as e:
        logger.error(f"Error retrieving integration checkpoints: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve integration checkpoints"
        ) from e


@router.post("/integration-checkpoints", response_model=IntegrationCheckpointResponse)
async def create_integration_checkpoint(
    checkpoint_data: IntegrationCheckpointCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new integration checkpoint."""
    try:
        checkpoint = IntegrationCheckpoint(**checkpoint_data.model_dump())
        session.add(checkpoint)
        await session.commit()
        await session.refresh(checkpoint)

        # Broadcast update
        await ws_manager.broadcast_update(
            "checkpoint_created",
            {
                "id": str(checkpoint.id),
                "checkpoint_name": checkpoint.checkpoint_name,
                "status": checkpoint.status.value,
            },
        )

        return IntegrationCheckpointResponse.model_validate(checkpoint)

    except Exception as e:
        logger.error(f"Error creating integration checkpoint: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create integration checkpoint"
        ) from e


@router.put("/integration-checkpoints/{checkpoint_id}/verify")
async def verify_integration_checkpoint(
    checkpoint_id: UUID,
    verification_notes: str | None = None,
    session: AsyncSession = Depends(get_async_session),
):
    """Verify an integration checkpoint."""
    try:
        query = select(IntegrationCheckpoint).where(
            IntegrationCheckpoint.id == checkpoint_id
        )
        result = await session.execute(query)
        checkpoint = result.scalar_one_or_none()

        if not checkpoint:
            raise HTTPException(
                status_code=404, detail="Integration checkpoint not found"
            )

        checkpoint.status = "verified"
        checkpoint.last_verified = datetime.utcnow()
        if verification_notes:
            checkpoint.verification_notes = verification_notes

        await session.commit()
        await session.refresh(checkpoint)

        # Broadcast update
        await ws_manager.broadcast_update(
            "checkpoint_verified",
            {
                "id": str(checkpoint.id),
                "checkpoint_name": checkpoint.checkpoint_name,
                "status": "verified",
                "last_verified": checkpoint.last_verified.isoformat(),
            },
        )

        # Trigger document update
        await doc_service.update_all_documents()

        return {"message": "Integration checkpoint verified", "status": "verified"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying checkpoint: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to verify checkpoint"
        ) from e


# ==============================================================================
# AGENT ACTIVITIES ENDPOINTS
# ==============================================================================


@router.get("/agent-activities", response_model=list[AgentActivityResponse])
async def get_agent_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    agent_name: str | None = Query(None),
    activity_type: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    """Get agent activities with optional filtering."""
    try:
        query = select(AgentActivity).order_by(desc(AgentActivity.timestamp))

        if agent_name:
            query = query.where(AgentActivity.agent_name == agent_name)
        if activity_type:
            query = query.where(AgentActivity.activity_type == activity_type)

        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        activities = result.scalars().all()

        return [
            AgentActivityResponse.model_validate(activity) for activity in activities
        ]

    except Exception as e:
        logger.error(f"Error retrieving agent activities: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve agent activities"
        ) from e


@router.post("/agent-activities", response_model=AgentActivityResponse)
async def log_agent_activity(
    activity_data: AgentActivityCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Log a new agent activity."""
    try:
        activity = AgentActivity(**activity_data.model_dump())
        session.add(activity)
        await session.commit()
        await session.refresh(activity)

        # Broadcast update
        await ws_manager.broadcast_update(
            "activity_logged",
            {
                "id": str(activity.id),
                "agent_name": activity.agent_name,
                "activity_type": activity.activity_type.value,
                "timestamp": activity.timestamp.isoformat(),
            },
        )

        return AgentActivityResponse.model_validate(activity)

    except Exception as e:
        logger.error(f"Error logging agent activity: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to log agent activity"
        ) from e


# ==============================================================================
# PROJECT OVERVIEW AND STATISTICS
# ==============================================================================


@router.get("/overview", response_model=ProjectOverviewResponse)
async def get_project_overview(
    session: AsyncSession = Depends(get_async_session),
):
    """Get comprehensive project overview and statistics."""
    try:
        # Get milestone statistics
        milestone_count_query = select(func.count(ProjectMilestone.id))
        milestone_count_result = await session.execute(milestone_count_query)
        total_milestones = milestone_count_result.scalar()

        completed_milestones_query = select(func.count(ProjectMilestone.id)).where(
            ProjectMilestone.completion_percentage >= 100
        )
        completed_milestones_result = await session.execute(completed_milestones_query)
        completed_milestones = completed_milestones_result.scalar()

        avg_completion_query = select(func.avg(ProjectMilestone.completion_percentage))
        avg_completion_result = await session.execute(avg_completion_query)
        avg_completion = avg_completion_result.scalar() or 0.0

        # Get workflow statistics
        active_workflows_query = select(func.count(AgentWorkflow.id)).where(
            AgentWorkflow.status == "in_progress"
        )
        active_workflows_result = await session.execute(active_workflows_query)
        active_workflows = active_workflows_result.scalar()

        total_workflows_query = select(func.count(AgentWorkflow.id))
        total_workflows_result = await session.execute(total_workflows_query)
        total_workflows = total_workflows_result.scalar()

        # Get technical debt statistics
        critical_debt_query = select(func.count(TechnicalDebtItem.id)).where(
            TechnicalDebtItem.priority == "critical"
        )
        critical_debt_result = await session.execute(critical_debt_query)
        critical_debt = critical_debt_result.scalar()

        total_debt_query = select(func.count(TechnicalDebtItem.id))
        total_debt_result = await session.execute(total_debt_query)
        total_debt = total_debt_result.scalar()

        # Get integration checkpoint statistics
        verified_checkpoints_query = select(func.count(IntegrationCheckpoint.id)).where(
            IntegrationCheckpoint.status == "verified"
        )
        verified_checkpoints_result = await session.execute(verified_checkpoints_query)
        verified_checkpoints = verified_checkpoints_result.scalar()

        total_checkpoints_query = select(func.count(IntegrationCheckpoint.id))
        total_checkpoints_result = await session.execute(total_checkpoints_query)
        total_checkpoints = total_checkpoints_result.scalar()

        # Calculate health score
        milestone_health = (completed_milestones / max(total_milestones, 1)) * 100
        debt_health = max(
            0, 100 - (critical_debt * 25)
        )  # Each critical debt item reduces by 25%
        integration_health = (verified_checkpoints / max(total_checkpoints, 1)) * 100
        overall_health = (milestone_health + debt_health + integration_health) / 3

        return ProjectOverviewResponse(
            total_milestones=total_milestones,
            completed_milestones=completed_milestones,
            average_completion=float(avg_completion),
            active_workflows=active_workflows,
            total_workflows=total_workflows,
            critical_debt_items=critical_debt,
            total_debt_items=total_debt,
            verified_checkpoints=verified_checkpoints,
            total_checkpoints=total_checkpoints,
            health_score=float(overall_health),
            last_updated=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting project overview: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get project overview"
        ) from e


# ==============================================================================
# DOCUMENTATION MANAGEMENT ENDPOINTS
# ==============================================================================


@router.post("/documentation/update")
async def trigger_documentation_update():
    """Manually trigger documentation update."""
    try:
        results = await doc_service.update_all_documents()

        # Broadcast update
        await ws_manager.broadcast_update(
            "documentation_updated",
            {"results": results, "updated_at": datetime.utcnow().isoformat()},
        )

        return {
            "message": "Documentation update triggered",
            "results": results,
            "updated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error triggering documentation update: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to update documentation"
        ) from e


@router.get("/documentation/status")
async def get_documentation_status():
    """Get documentation service status."""
    return {
        "service_active": True,
        "last_update": doc_service.last_update.isoformat()
        if doc_service.last_update
        else None,
        "documents": [
            "PROJECT_ROADMAP.md",
            "DEVELOPMENT_STATUS.md",
            "AGENT_COORDINATION_LOG.md",
            "TECHNICAL_DEBT_REGISTRY.md",
            "INTEGRATION_CHECKPOINTS.md",
        ],
        "websocket_connections": len(ws_manager.active_connections),
    }


# ==============================================================================
# WEBSOCKET ENDPOINT FOR REAL-TIME UPDATES
# ==============================================================================


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time project tracking updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
