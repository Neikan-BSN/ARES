"""FastAPI routes for project analytics and reporting."""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.base import get_async_session
from ...models.project_tracking import (
    AgentActivity,
    AgentWorkflow,
    IntegrationCheckpoint,
    ProjectMilestone,
    TechnicalDebtItem,
)
from .schemas.project_tracking import (
    AgentPerformanceMetrics,
    ProjectAnalytics,
    TimeSeriesData,
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/project/analytics", tags=["project-analytics"])


# ==============================================================================
# PROJECT ANALYTICS ENDPOINTS
# ==============================================================================


@router.get("/overview", response_model=ProjectAnalytics)
async def get_project_analytics(
    days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    session: AsyncSession = Depends(get_async_session),
):
    """Get comprehensive project analytics and trends."""
    try:
        analysis_start_date = datetime.utcnow() - timedelta(days=days)

        # Generate completion trend data
        completion_trend = await _generate_completion_trend(
            session, analysis_start_date, days
        )

        # Generate workflow activity trend
        workflow_trend = await _generate_workflow_trend(
            session, analysis_start_date, days
        )

        # Generate debt resolution trend
        debt_trend = await _generate_debt_resolution_trend(
            session, analysis_start_date, days
        )

        # Calculate performance metrics
        avg_completion_time = await _calculate_average_completion_time(
            session, analysis_start_date
        )
        workflow_success_rate = await _calculate_workflow_success_rate(
            session, analysis_start_date
        )
        debt_resolution_rate = await _calculate_debt_resolution_rate(
            session, analysis_start_date
        )

        # Get agent performance data
        top_agents = await _get_top_performing_agents(session, analysis_start_date)
        workload_distribution = await _get_agent_workload_distribution(
            session, analysis_start_date
        )

        # Calculate system health indicators
        integration_stability = await _calculate_integration_stability(session)
        code_quality_trend = await _generate_code_quality_trend(
            session, analysis_start_date, days
        )

        return ProjectAnalytics(
            completion_trend=completion_trend,
            workflow_activity_trend=workflow_trend,
            debt_resolution_trend=debt_trend,
            average_completion_time=avg_completion_time,
            workflow_success_rate=workflow_success_rate,
            debt_resolution_rate=debt_resolution_rate,
            top_performing_agents=top_agents,
            agent_workload_distribution=workload_distribution,
            integration_stability_score=integration_stability,
            code_quality_trend=code_quality_trend,
            report_generated_at=datetime.utcnow(),
            analysis_period_days=days,
        )

    except Exception as e:
        logger.error(f"Error generating project analytics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate project analytics"
        ) from e


@router.get("/agent-performance", response_model=list[AgentPerformanceMetrics])
async def get_agent_performance_metrics(
    days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    session: AsyncSession = Depends(get_async_session),
):
    """Get detailed performance metrics for all agents."""
    try:
        analysis_start_date = datetime.utcnow() - timedelta(days=days)

        # Get all agents with activities in the period
        agent_activities_query = (
            select(
                AgentActivity.agent_name,
                func.count(AgentActivity.id).label("total_activities"),
            )
            .where(AgentActivity.timestamp >= analysis_start_date)
            .group_by(AgentActivity.agent_name)
        )
        agent_activities_result = await session.execute(agent_activities_query)
        agent_activity_data = agent_activities_result.fetchall()

        performance_metrics = []

        for agent_name, total_activities in agent_activity_data:
            # Get completed workflows for this agent
            completed_workflows_query = select(func.count(AgentWorkflow.id)).where(
                AgentWorkflow.assigned_agent == agent_name,
                AgentWorkflow.status == "completed",
                AgentWorkflow.updated_at >= analysis_start_date,
            )
            completed_workflows_result = await session.execute(
                completed_workflows_query
            )
            completed_workflows = completed_workflows_result.scalar() or 0

            # Get total workflows for this agent
            total_workflows_query = select(func.count(AgentWorkflow.id)).where(
                AgentWorkflow.assigned_agent == agent_name,
                AgentWorkflow.created_at >= analysis_start_date,
            )
            total_workflows_result = await session.execute(total_workflows_query)
            total_workflows = total_workflows_result.scalar() or 0

            # Calculate success rate
            success_rate = (completed_workflows / max(total_workflows, 1)) * 100

            # Get average completion time
            avg_completion_query = select(
                func.avg(
                    func.extract("epoch", AgentWorkflow.updated_at)
                    - func.extract("epoch", AgentWorkflow.created_at)
                )
                / 3600  # Convert to hours
            ).where(
                AgentWorkflow.assigned_agent == agent_name,
                AgentWorkflow.status == "completed",
                AgentWorkflow.updated_at >= analysis_start_date,
            )
            avg_completion_result = await session.execute(avg_completion_query)
            avg_completion_time = avg_completion_result.scalar()

            # Get last activity timestamp
            last_activity_query = select(func.max(AgentActivity.timestamp)).where(
                AgentActivity.agent_name == agent_name
            )
            last_activity_result = await session.execute(last_activity_query)
            last_activity = last_activity_result.scalar() or datetime.utcnow()

            # Calculate reliability score (based on success rate and activity consistency)
            reliability_score = min(
                100, success_rate * 0.7 + (total_activities / max(days, 1)) * 0.3
            )

            performance_metrics.append(
                AgentPerformanceMetrics(
                    agent_name=agent_name,
                    total_activities=total_activities,
                    completed_workflows=completed_workflows,
                    success_rate=success_rate,
                    average_completion_time=avg_completion_time,
                    reliability_score=reliability_score,
                    last_activity=last_activity,
                )
            )

        # Sort by reliability score descending
        performance_metrics.sort(key=lambda x: x.reliability_score, reverse=True)

        return performance_metrics

    except Exception as e:
        logger.error(f"Error getting agent performance metrics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get agent performance metrics"
        ) from e


@router.get("/completion-trend", response_model=list[TimeSeriesData])
async def get_completion_trend(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    session: AsyncSession = Depends(get_async_session),
):
    """Get milestone completion trend over time."""
    try:
        analysis_start_date = datetime.utcnow() - timedelta(days=days)
        return await _generate_completion_trend(session, analysis_start_date, days)

    except Exception as e:
        logger.error(f"Error getting completion trend: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get completion trend"
        ) from e


@router.get("/debt-analysis")
async def get_debt_analysis(
    session: AsyncSession = Depends(get_async_session),
):
    """Get detailed technical debt analysis."""
    try:
        # Debt by priority
        debt_by_priority_query = select(
            TechnicalDebtItem.priority, func.count(TechnicalDebtItem.id).label("count")
        ).group_by(TechnicalDebtItem.priority)
        debt_by_priority_result = await session.execute(debt_by_priority_query)
        debt_by_priority = [
            {"priority": priority.value, "count": count}
            for priority, count in debt_by_priority_result.fetchall()
        ]

        # Debt by component
        debt_by_component_query = select(
            TechnicalDebtItem.component, func.count(TechnicalDebtItem.id).label("count")
        ).group_by(TechnicalDebtItem.component)
        debt_by_component_result = await session.execute(debt_by_component_query)
        debt_by_component = [
            {"component": component, "count": count}
            for component, count in debt_by_component_result.fetchall()
        ]

        # Debt resolution rate by month
        debt_resolution_query = (
            select(
                func.date_trunc("month", TechnicalDebtItem.updated_at).label("month"),
                TechnicalDebtItem.status,
                func.count(TechnicalDebtItem.id).label("count"),
            )
            .where(
                TechnicalDebtItem.updated_at >= datetime.utcnow() - timedelta(days=180)
            )
            .group_by(
                func.date_trunc("month", TechnicalDebtItem.updated_at),
                TechnicalDebtItem.status,
            )
            .order_by(func.date_trunc("month", TechnicalDebtItem.updated_at))
        )
        debt_resolution_result = await session.execute(debt_resolution_query)
        debt_resolution_trend = [
            {
                "month": month.isoformat() if month else None,
                "status": status.value if status else "unknown",
                "count": count,
            }
            for month, status, count in debt_resolution_result.fetchall()
        ]

        return {
            "debt_by_priority": debt_by_priority,
            "debt_by_component": debt_by_component,
            "resolution_trend": debt_resolution_trend,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting debt analysis: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get debt analysis"
        ) from e


# ==============================================================================
# HELPER FUNCTIONS FOR ANALYTICS
# ==============================================================================


async def _generate_completion_trend(
    session: AsyncSession, start_date: datetime, days: int
) -> list[dict]:
    """Generate milestone completion trend data."""
    trend_data = []

    # Generate daily data points
    for i in range(days):
        date_point = start_date + timedelta(days=i)

        # Get average completion percentage for milestones updated on this day
        completion_query = select(
            func.avg(ProjectMilestone.completion_percentage)
        ).where(func.date(ProjectMilestone.updated_at) == date_point.date())
        completion_result = await session.execute(completion_query)
        avg_completion = completion_result.scalar() or 0.0

        trend_data.append(
            {
                "timestamp": date_point.isoformat(),
                "value": float(avg_completion),
                "metadata": {"date": date_point.date().isoformat()},
            }
        )

    return trend_data


async def _generate_workflow_trend(
    session: AsyncSession, start_date: datetime, days: int
) -> list[dict]:
    """Generate workflow activity trend data."""
    trend_data = []

    for i in range(days):
        date_point = start_date + timedelta(days=i)

        # Count workflows created on this day
        workflow_count_query = select(func.count(AgentWorkflow.id)).where(
            func.date(AgentWorkflow.created_at) == date_point.date()
        )
        workflow_count_result = await session.execute(workflow_count_query)
        workflow_count = workflow_count_result.scalar() or 0

        trend_data.append(
            {
                "timestamp": date_point.isoformat(),
                "value": workflow_count,
                "metadata": {"date": date_point.date().isoformat()},
            }
        )

    return trend_data


async def _generate_debt_resolution_trend(
    session: AsyncSession, start_date: datetime, days: int
) -> list[dict]:
    """Generate debt resolution trend data."""
    trend_data = []

    for i in range(days):
        date_point = start_date + timedelta(days=i)

        # Count debt items resolved on this day
        resolved_count_query = select(func.count(TechnicalDebtItem.id)).where(
            func.date(TechnicalDebtItem.updated_at) == date_point.date(),
            TechnicalDebtItem.status == "resolved",
        )
        resolved_count_result = await session.execute(resolved_count_query)
        resolved_count = resolved_count_result.scalar() or 0

        trend_data.append(
            {
                "timestamp": date_point.isoformat(),
                "value": resolved_count,
                "metadata": {"date": date_point.date().isoformat()},
            }
        )

    return trend_data


async def _calculate_average_completion_time(
    session: AsyncSession, start_date: datetime
) -> float:
    """Calculate average milestone completion time."""
    avg_time_query = select(
        func.avg(
            func.extract("epoch", ProjectMilestone.updated_at)
            - func.extract("epoch", ProjectMilestone.created_at)
        )
        / 86400  # Convert to days
    ).where(
        ProjectMilestone.completion_percentage >= 100,
        ProjectMilestone.updated_at >= start_date,
    )

    result = await session.execute(avg_time_query)
    return float(result.scalar() or 0.0)


async def _calculate_workflow_success_rate(
    session: AsyncSession, start_date: datetime
) -> float:
    """Calculate workflow success rate."""
    total_query = select(func.count(AgentWorkflow.id)).where(
        AgentWorkflow.created_at >= start_date
    )
    total_result = await session.execute(total_query)
    total_workflows = total_result.scalar() or 0

    completed_query = select(func.count(AgentWorkflow.id)).where(
        AgentWorkflow.created_at >= start_date, AgentWorkflow.status == "completed"
    )
    completed_result = await session.execute(completed_query)
    completed_workflows = completed_result.scalar() or 0

    return (completed_workflows / max(total_workflows, 1)) * 100


async def _calculate_debt_resolution_rate(
    session: AsyncSession, start_date: datetime
) -> float:
    """Calculate debt resolution rate."""
    total_query = select(func.count(TechnicalDebtItem.id)).where(
        TechnicalDebtItem.created_at >= start_date
    )
    total_result = await session.execute(total_query)
    total_debt = total_result.scalar() or 0

    resolved_query = select(func.count(TechnicalDebtItem.id)).where(
        TechnicalDebtItem.created_at >= start_date,
        TechnicalDebtItem.status == "resolved",
    )
    resolved_result = await session.execute(resolved_query)
    resolved_debt = resolved_result.scalar() or 0

    return (resolved_debt / max(total_debt, 1)) * 100


async def _get_top_performing_agents(
    session: AsyncSession, start_date: datetime
) -> list[dict]:
    """Get top performing agents by activity count."""
    query = (
        select(
            AgentActivity.agent_name,
            func.count(AgentActivity.id).label("activity_count"),
        )
        .where(AgentActivity.timestamp >= start_date)
        .group_by(AgentActivity.agent_name)
        .order_by(func.count(AgentActivity.id).desc())
        .limit(10)
    )

    result = await session.execute(query)
    return [
        {"agent_name": agent_name, "activity_count": count}
        for agent_name, count in result.fetchall()
    ]


async def _get_agent_workload_distribution(
    session: AsyncSession, start_date: datetime
) -> list[dict]:
    """Get agent workload distribution."""
    query = (
        select(
            AgentWorkflow.assigned_agent,
            func.count(AgentWorkflow.id).label("total_workflows"),
            func.avg(AgentWorkflow.progress_percentage).label("avg_progress"),
        )
        .where(AgentWorkflow.created_at >= start_date)
        .group_by(AgentWorkflow.assigned_agent)
    )

    result = await session.execute(query)
    return [
        {
            "agent_name": agent_name,
            "total_workflows": total,
            "average_progress": float(avg_progress or 0.0),
        }
        for agent_name, total, avg_progress in result.fetchall()
    ]


async def _calculate_integration_stability(session: AsyncSession) -> float:
    """Calculate integration stability score."""
    total_query = select(func.count(IntegrationCheckpoint.id))
    total_result = await session.execute(total_query)
    total_checkpoints = total_result.scalar() or 0

    verified_query = select(func.count(IntegrationCheckpoint.id)).where(
        IntegrationCheckpoint.status == "verified"
    )
    verified_result = await session.execute(verified_query)
    verified_checkpoints = verified_result.scalar() or 0

    return (verified_checkpoints / max(total_checkpoints, 1)) * 100


async def _generate_code_quality_trend(
    session: AsyncSession, start_date: datetime, days: int
) -> list[dict]:
    """Generate code quality trend (placeholder - would integrate with actual quality metrics)."""
    # This is a placeholder that would integrate with actual code quality tools
    # For now, generate sample data
    trend_data = []

    for i in range(days):
        date_point = start_date + timedelta(days=i)

        # Placeholder quality score (would be from actual tools like SonarQube, etc.)
        quality_score = 85.0 + (i % 10) * 1.5  # Sample trend

        trend_data.append(
            {
                "timestamp": date_point.isoformat(),
                "value": quality_score,
                "metadata": {
                    "date": date_point.date().isoformat(),
                    "source": "placeholder",
                },
            }
        )

    return trend_data
