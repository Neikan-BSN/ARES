"""FastAPI routes for bulk operations on project tracking data."""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.base import get_async_session
from ...models.project_tracking import (
    AgentWorkflow,
    ProjectMilestone,
    TechnicalDebtItem,
)
from .schemas.project_tracking import (
    BulkDebtUpdate,
    BulkMilestoneUpdate,
    BulkWorkflowUpdate,
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/project/bulk", tags=["project-bulk-operations"])


# ==============================================================================
# BULK MILESTONE OPERATIONS
# ==============================================================================


@router.put("/milestones/update")
async def bulk_update_milestones(
    bulk_update: BulkMilestoneUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Bulk update multiple milestones."""
    try:
        update_values = {}

        if bulk_update.completion_percentage is not None:
            update_values["completion_percentage"] = bulk_update.completion_percentage

        if bulk_update.target_completion_date is not None:
            update_values["target_completion_date"] = bulk_update.target_completion_date

        if not update_values:
            raise HTTPException(status_code=400, detail="No update values provided")

        # Perform bulk update
        update_query = (
            update(ProjectMilestone)
            .where(ProjectMilestone.id.in_(bulk_update.milestone_ids))
            .values(**update_values)
        )

        result = await session.execute(update_query)
        await session.commit()

        updated_count = result.rowcount

        return {
            "message": f"Successfully updated {updated_count} milestones",
            "updated_count": updated_count,
            "milestone_ids": [str(id) for id in bulk_update.milestone_ids],
            "updates_applied": update_values,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk milestone update: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to perform bulk milestone update"
        ) from e


@router.delete("/milestones")
async def bulk_delete_milestones(
    milestone_ids: list[UUID],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Bulk delete multiple milestones."""
    try:
        # First, get the milestones to be deleted for logging
        select_query = select(ProjectMilestone).where(
            ProjectMilestone.id.in_(milestone_ids)
        )
        select_result = await session.execute(select_query)
        milestones_to_delete = select_result.scalars().all()

        if not milestones_to_delete:
            raise HTTPException(
                status_code=404, detail="No milestones found with provided IDs"
            )

        # Delete the milestones
        for milestone in milestones_to_delete:
            await session.delete(milestone)

        await session.commit()

        return {
            "message": f"Successfully deleted {len(milestones_to_delete)} milestones",
            "deleted_count": len(milestones_to_delete),
            "deleted_milestones": [
                {"id": str(m.id), "title": m.title} for m in milestones_to_delete
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk milestone deletion: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to perform bulk milestone deletion"
        ) from e


# ==============================================================================
# BULK WORKFLOW OPERATIONS
# ==============================================================================


@router.put("/workflows/update")
async def bulk_update_workflows(
    bulk_update: BulkWorkflowUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Bulk update multiple workflows."""
    try:
        update_values = {}

        if bulk_update.status is not None:
            update_values["status"] = bulk_update.status

        if bulk_update.assigned_agent is not None:
            update_values["assigned_agent"] = bulk_update.assigned_agent

        if not update_values:
            raise HTTPException(status_code=400, detail="No update values provided")

        # Perform bulk update
        update_query = (
            update(AgentWorkflow)
            .where(AgentWorkflow.id.in_(bulk_update.workflow_ids))
            .values(**update_values)
        )

        result = await session.execute(update_query)
        await session.commit()

        updated_count = result.rowcount

        return {
            "message": f"Successfully updated {updated_count} workflows",
            "updated_count": updated_count,
            "workflow_ids": [str(id) for id in bulk_update.workflow_ids],
            "updates_applied": update_values,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk workflow update: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to perform bulk workflow update"
        ) from e


@router.post("/workflows/reassign")
async def bulk_reassign_workflows(
    workflow_ids: list[UUID],
    new_agent: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Bulk reassign workflows to a different agent."""
    try:
        # Update workflows with new agent assignment
        update_query = (
            update(AgentWorkflow)
            .where(AgentWorkflow.id.in_(workflow_ids))
            .values(assigned_agent=new_agent)
        )

        result = await session.execute(update_query)
        await session.commit()

        updated_count = result.rowcount

        return {
            "message": f"Successfully reassigned {updated_count} workflows to {new_agent}",
            "updated_count": updated_count,
            "new_agent": new_agent,
            "workflow_ids": [str(id) for id in workflow_ids],
        }

    except Exception as e:
        logger.error(f"Error in bulk workflow reassignment: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to perform bulk workflow reassignment"
        ) from e


# ==============================================================================
# BULK TECHNICAL DEBT OPERATIONS
# ==============================================================================


@router.put("/technical-debt/update")
async def bulk_update_technical_debt(
    bulk_update: BulkDebtUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Bulk update multiple technical debt items."""
    try:
        update_values = {}

        if bulk_update.status is not None:
            update_values["status"] = bulk_update.status

        if bulk_update.assigned_agent is not None:
            update_values["assigned_agent"] = bulk_update.assigned_agent

        if not update_values:
            raise HTTPException(status_code=400, detail="No update values provided")

        # Perform bulk update
        update_query = (
            update(TechnicalDebtItem)
            .where(TechnicalDebtItem.id.in_(bulk_update.debt_ids))
            .values(**update_values)
        )

        result = await session.execute(update_query)
        await session.commit()

        updated_count = result.rowcount

        return {
            "message": f"Successfully updated {updated_count} technical debt items",
            "updated_count": updated_count,
            "debt_ids": [str(id) for id in bulk_update.debt_ids],
            "updates_applied": update_values,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk debt update: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to perform bulk debt update"
        ) from e


@router.post("/technical-debt/resolve")
async def bulk_resolve_technical_debt(
    debt_ids: list[UUID],
    resolution_notes: str = "Bulk resolved",
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Bulk resolve multiple technical debt items."""
    try:
        # Update debt items to resolved status
        update_query = (
            update(TechnicalDebtItem)
            .where(TechnicalDebtItem.id.in_(debt_ids))
            .values(
                status="resolved",
                # Note: Would need to add resolution_notes field to model if needed
            )
        )

        result = await session.execute(update_query)
        await session.commit()

        updated_count = result.rowcount

        return {
            "message": f"Successfully resolved {updated_count} technical debt items",
            "resolved_count": updated_count,
            "debt_ids": [str(id) for id in debt_ids],
            "resolution_notes": resolution_notes,
        }

    except Exception as e:
        logger.error(f"Error in bulk debt resolution: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to perform bulk debt resolution"
        ) from e


# ==============================================================================
# BULK DATA VALIDATION AND STATISTICS
# ==============================================================================


@router.get("/validation/milestones")
async def validate_milestone_data(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Validate milestone data integrity and provide statistics."""
    try:
        # Get basic statistics
        total_query = select(ProjectMilestone)
        total_result = await session.execute(total_query)
        all_milestones = total_result.scalars().all()

        total_count = len(all_milestones)
        completed_count = len(
            [m for m in all_milestones if m.completion_percentage >= 100]
        )
        in_progress_count = len(
            [m for m in all_milestones if 0 < m.completion_percentage < 100]
        )
        not_started_count = len(
            [m for m in all_milestones if m.completion_percentage == 0]
        )

        # Check for data inconsistencies
        issues = []

        for milestone in all_milestones:
            # Check for invalid completion percentages
            if (
                milestone.completion_percentage < 0
                or milestone.completion_percentage > 100
            ):
                issues.append(
                    {
                        "type": "invalid_completion_percentage",
                        "milestone_id": str(milestone.id),
                        "milestone_title": milestone.title,
                        "value": float(milestone.completion_percentage),
                    }
                )

            # Check for missing target dates on high-priority items
            if (
                not milestone.target_completion_date
                and milestone.completion_percentage < 100
            ):
                issues.append(
                    {
                        "type": "missing_target_date",
                        "milestone_id": str(milestone.id),
                        "milestone_title": milestone.title,
                    }
                )

        return {
            "validation_summary": {
                "total_milestones": total_count,
                "completed": completed_count,
                "in_progress": in_progress_count,
                "not_started": not_started_count,
                "issues_found": len(issues),
            },
            "data_issues": issues,
            "validation_timestamp": "2025-08-02T00:00:00Z",
        }

    except Exception as e:
        logger.error(f"Error in milestone data validation: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to validate milestone data"
        ) from e


@router.get("/validation/workflows")
async def validate_workflow_data(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Validate workflow data integrity and provide statistics."""
    try:
        # Get all workflows
        workflows_query = select(AgentWorkflow)
        workflows_result = await session.execute(workflows_query)
        all_workflows = workflows_result.scalars().all()

        # Calculate statistics
        total_count = len(all_workflows)
        status_counts = {}
        agent_workloads = {}

        issues = []

        for workflow in all_workflows:
            # Count by status
            status = workflow.status.value if workflow.status else "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

            # Count by agent
            agent = workflow.assigned_agent or "unassigned"
            agent_workloads[agent] = agent_workloads.get(agent, 0) + 1

            # Check for data issues
            if not workflow.assigned_agent:
                issues.append(
                    {
                        "type": "unassigned_workflow",
                        "workflow_id": str(workflow.id),
                        "workflow_name": workflow.workflow_name,
                    }
                )

            if workflow.progress_percentage < 0 or workflow.progress_percentage > 100:
                issues.append(
                    {
                        "type": "invalid_progress_percentage",
                        "workflow_id": str(workflow.id),
                        "workflow_name": workflow.workflow_name,
                        "value": float(workflow.progress_percentage),
                    }
                )

        return {
            "validation_summary": {
                "total_workflows": total_count,
                "status_distribution": status_counts,
                "agent_workload_distribution": agent_workloads,
                "issues_found": len(issues),
            },
            "data_issues": issues,
            "validation_timestamp": "2025-08-02T00:00:00Z",
        }

    except Exception as e:
        logger.error(f"Error in workflow data validation: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to validate workflow data"
        ) from e


# ==============================================================================
# BULK IMPORT/EXPORT OPERATIONS
# ==============================================================================


@router.post("/import/milestones")
async def bulk_import_milestones(
    milestones_data: list[dict[str, Any]],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Bulk import milestones from structured data."""
    try:
        imported_milestones = []
        errors = []

        for i, milestone_data in enumerate(milestones_data):
            try:
                # Validate required fields
                if "title" not in milestone_data or "component" not in milestone_data:
                    errors.append(
                        {
                            "index": i,
                            "error": "Missing required fields: title, component",
                        }
                    )
                    continue

                # Create milestone
                milestone = ProjectMilestone(
                    title=milestone_data["title"],
                    description=milestone_data.get("description"),
                    component=milestone_data["component"],
                    completion_percentage=milestone_data.get(
                        "completion_percentage", 0
                    ),
                    target_completion_date=milestone_data.get("target_completion_date"),
                )

                session.add(milestone)
                imported_milestones.append(milestone)

            except Exception as e:
                errors.append({"index": i, "error": str(e)})

        await session.commit()

        return {
            "message": f"Successfully imported {len(imported_milestones)} milestones",
            "imported_count": len(imported_milestones),
            "error_count": len(errors),
            "errors": errors,
            "imported_milestone_ids": [str(m.id) for m in imported_milestones],
        }

    except Exception as e:
        logger.error(f"Error in bulk milestone import: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to perform bulk milestone import"
        ) from e


@router.get("/export/project-data")
async def export_project_data(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Export all project tracking data for backup or analysis."""
    try:
        # Get all milestones
        milestones_query = select(ProjectMilestone)
        milestones_result = await session.execute(milestones_query)
        milestones = milestones_result.scalars().all()

        # Get all workflows
        workflows_query = select(AgentWorkflow)
        workflows_result = await session.execute(workflows_query)
        workflows = workflows_result.scalars().all()

        # Get all technical debt
        debt_query = select(TechnicalDebtItem)
        debt_result = await session.execute(debt_query)
        debt_items = debt_result.scalars().all()

        # Convert to exportable format
        export_data = {
            "export_metadata": {
                "export_timestamp": "2025-08-02T00:00:00Z",
                "total_records": len(milestones) + len(workflows) + len(debt_items),
            },
            "milestones": [
                {
                    "id": str(m.id),
                    "title": m.title,
                    "description": m.description,
                    "component": m.component.value,
                    "completion_percentage": float(m.completion_percentage),
                    "target_completion_date": m.target_completion_date.isoformat()
                    if m.target_completion_date
                    else None,
                    "created_at": m.created_at.isoformat(),
                    "updated_at": m.updated_at.isoformat(),
                }
                for m in milestones
            ],
            "workflows": [
                {
                    "id": str(w.id),
                    "workflow_name": w.workflow_name,
                    "description": w.description,
                    "assigned_agent": w.assigned_agent,
                    "status": w.status.value,
                    "priority": w.priority,
                    "progress_percentage": float(w.progress_percentage),
                    "estimated_duration_hours": w.estimated_duration_hours,
                    "created_at": w.created_at.isoformat(),
                    "updated_at": w.updated_at.isoformat(),
                }
                for w in workflows
            ],
            "technical_debt": [
                {
                    "id": str(d.id),
                    "title": d.title,
                    "description": d.description,
                    "priority": d.priority.value,
                    "component": d.component,
                    "estimated_effort": d.estimated_effort,
                    "assigned_agent": d.assigned_agent,
                    "status": d.status.value,
                    "created_at": d.created_at.isoformat(),
                    "updated_at": d.updated_at.isoformat(),
                }
                for d in debt_items
            ],
        }

        return export_data

    except Exception as e:
        logger.error(f"Error in project data export: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to export project data"
        ) from e
