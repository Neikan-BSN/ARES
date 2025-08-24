"""Documentation Service for automatic master document updates."""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import aiofiles
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.agent import Agent
from ..models.base import get_async_session
from ..models.project_tracking import (
    AgentActivity,
    AgentWorkflow,
    IntegrationCheckpoint,
    ProjectMilestone,
    TechnicalDebtItem,
)
from ..models.task import Task

logger = logging.getLogger(__name__)


class DocumentationService:
    """Service for managing and updating master documentation."""

    def __init__(self):
        """Initialize the documentation service."""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.master_doc_path = (
            self.project_root / "project_plan" / "DEVELOPMENT_STATUS.md"
        )

    async def update_master_documentation(self) -> None:
        """Update master documentation with current project status."""
        try:
            logger.info("Starting master documentation update...")

            # Gather data from various sources
            agent_status = await self._get_agent_status()
            task_summary = await self._get_task_summary()
            project_metrics = await self._get_project_metrics()
            git_stats = await self._get_git_statistics()

            # Generate the documentation content
            content = await self._generate_documentation_content(
                agent_status, task_summary, project_metrics, git_stats
            )

            # Write to master document
            await self._write_master_document(content)

            logger.info("Master documentation updated successfully")

        except Exception as e:
            logger.error(f"Failed to update master documentation: {e}")
            raise

    async def _get_project_metrics(self) -> dict[str, Any]:
        """Get project metrics from database."""
        session_gen = get_async_session()
        session = await session_gen.__anext__()
        try:
            try:
                # Project milestones
                milestones_query = select(ProjectMilestone).order_by(
                    desc(ProjectMilestone.updated_at)
                )
                milestones_result = await session.execute(milestones_query)
                milestones = milestones_result.scalars().all()

                # Agent workflows
                workflows_query = select(AgentWorkflow).order_by(
                    desc(AgentWorkflow.updated_at)
                )
                workflows_result = await session.execute(workflows_query)
                workflows = workflows_result.scalars().all()

                # Technical debt items
                debt_query = select(TechnicalDebtItem).order_by(
                    TechnicalDebtItem.priority.desc()
                )
                debt_result = await session.execute(debt_query)
                debt_items = debt_result.scalars().all()

                # Integration checkpoints
                checkpoints_query = select(IntegrationCheckpoint).order_by(
                    desc(IntegrationCheckpoint.last_verified)
                )
                checkpoints_result = await session.execute(checkpoints_query)
                checkpoints = checkpoints_result.scalars().all()

                # Agent activities (recent)
                activities_query = (
                    select(AgentActivity)
                    .where(
                        AgentActivity.timestamp >= datetime.utcnow() - timedelta(days=7)
                    )
                    .order_by(desc(AgentActivity.timestamp))
                    .limit(50)
                )
                activities_result = await session.execute(activities_query)
                activities = activities_result.scalars().all()

                return {
                    "milestones": milestones,
                    "workflows": workflows,
                    "debt_items": debt_items,
                    "checkpoints": checkpoints,
                    "recent_activities": activities,
                }

            except Exception as e:
                logger.error(f"Error getting project metrics: {e}")
                return {}
        finally:
            await session_gen.aclose()

    async def _get_agent_status(self) -> dict[str, Any]:
        """Get current agent status from database."""
        session_gen = get_async_session()
        session = await session_gen.__anext__()
        try:
            try:
                agents_query = select(Agent).order_by(desc(Agent.updated_at))
                result = await session.execute(agents_query)
                agents = result.scalars().all()

                return {
                    "total_agents": len(agents),
                    "active_agents": len([a for a in agents if a.status == "active"]),
                    "agents": agents,
                }

            except Exception as e:
                logger.error(f"Error getting agent status: {e}")
                return {"total_agents": 0, "active_agents": 0, "agents": []}
        finally:
            await session_gen.aclose()

    async def _get_task_summary(self) -> dict[str, Any]:
        """Get current task summary from database."""
        session_gen = get_async_session()
        session = await session_gen.__anext__()
        try:
            try:
                tasks_query = select(Task).order_by(desc(Task.updated_at))
                result = await session.execute(tasks_query)
                tasks = result.scalars().all()

                return {
                    "total_tasks": len(tasks),
                    "completed_tasks": len(
                        [t for t in tasks if t.status == "completed"]
                    ),
                    "pending_tasks": len([t for t in tasks if t.status == "pending"]),
                    "failed_tasks": len([t for t in tasks if t.status == "failed"]),
                    "recent_tasks": tasks[:10],  # Most recent 10 tasks
                }

            except Exception as e:
                logger.error(f"Error getting task summary: {e}")
                return {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "pending_tasks": 0,
                    "failed_tasks": 0,
                    "recent_tasks": [],
                }
        finally:
            await session_gen.aclose()

    async def _calculate_completion_percentage(self, session: AsyncSession) -> float:
        """Calculate overall project completion percentage."""
        try:
            # Get completion percentage from all milestones
            completion_query = select(func.avg(ProjectMilestone.completion_percentage))
            result = await session.execute(completion_query)
            avg_completion = result.scalar()

            return float(avg_completion) if avg_completion else 0.0

        except Exception as e:
            logger.error(f"Error calculating completion: {e}")
            return 0.0

    async def _get_git_statistics(self) -> dict[str, Any]:
        """Get git repository statistics."""
        try:
            # Get recent commit count
            recent_commits = await asyncio.create_subprocess_exec(
                "git",
                "rev-list",
                "--count",
                "--since=1.week.ago",
                "HEAD",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root,
            )
            stdout, stderr = await recent_commits.communicate()

            # Get modified files count
            modified_files = await asyncio.create_subprocess_exec(
                "git",
                "status",
                "--porcelain",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root,
            )
            mod_stdout, mod_stderr = await modified_files.communicate()

            # Get branch info
            current_branch = await asyncio.create_subprocess_exec(
                "git",
                "branch",
                "--show-current",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root,
            )
            branch_stdout, branch_stderr = await current_branch.communicate()

            return {
                "recent_commits": int(stdout.decode().strip()) if stdout else 0,
                "modified_files": len(mod_stdout.decode().strip().split("\n"))
                if mod_stdout
                else 0,
                "current_branch": branch_stdout.decode().strip()
                if branch_stdout
                else "unknown",
            }

        except Exception as e:
            logger.error(f"Error getting git statistics: {e}")
            return {
                "recent_commits": 0,
                "modified_files": 0,
                "current_branch": "unknown",
            }

    async def _generate_documentation_content(
        self,
        agent_status: dict[str, Any],
        task_summary: dict[str, Any],
        project_metrics: dict[str, Any],
        git_stats: dict[str, Any],
    ) -> str:
        """Generate the master documentation content."""
        timestamp = datetime.utcnow().isoformat()

        content = f"""# ARES Development Status

**Last Updated:** {timestamp}
**Generated by:** ARES Documentation Service

## 📊 Project Overview

### Agent Status
- **Total Agents:** {agent_status.get("total_agents", 0)}
- **Active Agents:** {agent_status.get("active_agents", 0)}

### Task Summary
- **Total Tasks:** {task_summary.get("total_tasks", 0)}
- **Completed:** {task_summary.get("completed_tasks", 0)}
- **Pending:** {task_summary.get("pending_tasks", 0)}
- **Failed:** {task_summary.get("failed_tasks", 0)}

### Repository Activity
- **Current Branch:** {git_stats.get("current_branch", "unknown")}
- **Recent Commits (7 days):** {git_stats.get("recent_commits", 0)}
- **Modified Files:** {git_stats.get("modified_files", 0)}

## 🎯 Current Milestones

"""

        # Add milestone details if available
        milestones = project_metrics.get("milestones", [])
        if milestones:
            for milestone in milestones[:5]:  # Show top 5 milestones
                content += f"- **{milestone.title}**: {milestone.completion_percentage}% complete\n"
        else:
            content += "- No active milestones found\n"

        content += """
## 🔧 Technical Debt

"""

        # Add technical debt items
        debt_items = project_metrics.get("debt_items", [])
        if debt_items:
            for item in debt_items[:5]:  # Show top 5 debt items
                content += f"- **{item.title}** (Priority: {item.priority})\n"
        else:
            content += "- No technical debt items tracked\n"

        content += """
## 🚀 Recent Activities

"""

        # Add recent activities
        activities = project_metrics.get("recent_activities", [])
        if activities:
            for activity in activities[:10]:  # Show recent 10 activities
                content += f"- **{activity.agent_name}**: {activity.description}\n"
        else:
            content += "- No recent activities found\n"

        content += """

---
*This document is automatically generated and updated by the ARES Documentation Service.*
"""

        return content

    async def _write_master_document(self, content: str) -> None:
        """Write content to the master documentation file."""
        try:
            # Ensure directory exists
            self.master_doc_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the content
            async with aiofiles.open(self.master_doc_path, "w", encoding="utf-8") as f:
                await f.write(content)

            logger.info(f"Master document written to {self.master_doc_path}")

        except Exception as e:
            logger.error(f"Error writing master document: {e}")
            raise
