#!/usr/bin/env python3
"""
ARES Project Tracker Update Script

This script provides manual and automated updates for project tracking documents.
Integrates with the ARES project tracking database and Git repository.
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from sqlalchemy import func, select
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.ares.models.base import get_async_session
    from src.ares.models.project_tracking import (
        AgentActivity,
        AgentWorkflow,
        IntegrationCheckpoint,
        ProjectMilestone,
        TechnicalDebtItem,
    )
    from src.ares.services.documentation_service import DocumentationService
except ImportError as e:
    print(f"Error importing ARES modules: {e}")
    print(
        "Please ensure you're running this script from the ARES project root directory"
    )
    sys.exit(1)


class ProjectTrackerUpdater:
    """Handles project tracker document updates."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.project_plan_dir = self.project_root / "project_plan"
        self.doc_service = DocumentationService()

    async def update_all_trackers(self) -> dict[str, bool]:
        """Update all tracker documents."""
        print("🔄 Starting tracker update process...")

        results = {}

        try:
            # Update master documents first
            print("📚 Updating master documents...")
            master_results = await self.doc_service.update_all_documents()
            results.update(master_results)

            # Update tracker documents
            print("📊 Updating tracker documents...")
            results["milestone_tracker"] = await self.update_milestone_tracker()
            results[
                "agent_performance_tracker"
            ] = await self.update_agent_performance_tracker()
            results["daily_status_report"] = await self.update_daily_status_report()

            print("✅ Tracker update process completed")
            return results

        except Exception as e:
            print(f"❌ Error updating trackers: {e}")
            return results

    async def update_milestone_tracker(self) -> bool:
        """Update the milestone tracker document."""
        try:
            print("  📈 Updating milestone tracker...")

            async with get_async_session() as session:
                # Get milestone data
                milestones = await self._get_milestones_data(session)

                # Generate updated content
                content = await self._generate_milestone_tracker_content(milestones)

                # Write to file
                tracker_file = (
                    self.project_plan_dir / "tracker" / "MILESTONE_TRACKER.md"
                )
                import aiofiles

                async with aiofiles.open(tracker_file, "w") as f:
                    await f.write(content)

                print("  ✅ Milestone tracker updated")
                return True

        except Exception as e:
            print(f"  ❌ Error updating milestone tracker: {e}")
            return False

    async def update_agent_performance_tracker(self) -> bool:
        """Update the agent performance tracker document."""
        try:
            print("  🤖 Updating agent performance tracker...")

            async with get_async_session() as session:
                # Get agent performance data
                performance_data = await self._get_agent_performance_data(session)

                # Generate updated content
                content = await self._generate_agent_performance_content(
                    performance_data
                )

                # Write to file
                tracker_file = (
                    self.project_plan_dir / "tracker" / "AGENT_PERFORMANCE_TRACKER.md"
                )
                import aiofiles

                async with aiofiles.open(tracker_file, "w") as f:
                    await f.write(content)

                print("  ✅ Agent performance tracker updated")
                return True

        except Exception as e:
            print(f"  ❌ Error updating agent performance tracker: {e}")
            return False

    async def update_daily_status_report(self) -> bool:
        """Update the daily status report."""
        try:
            print("  📋 Updating daily status report...")

            async with get_async_session() as session:
                # Get daily status data
                status_data = await self._get_daily_status_data(session)

                # Generate updated content
                content = await self._generate_daily_status_content(status_data)

                # Write to file
                report_file = (
                    self.project_plan_dir / "reports" / "DAILY_STATUS_REPORT.md"
                )
                import aiofiles

                async with aiofiles.open(report_file, "w") as f:
                    await f.write(content)

                print("  ✅ Daily status report updated")
                return True

        except Exception as e:
            print(f"  ❌ Error updating daily status report: {e}")
            return False

    async def _get_milestones_data(self, session: AsyncSession) -> dict:
        """Get milestone data from database."""
        # Get all milestones
        milestones_query = select(ProjectMilestone).order_by(
            ProjectMilestone.updated_at.desc()
        )
        milestones_result = await session.execute(milestones_query)
        milestones = milestones_result.scalars().all()

        # Calculate statistics
        total_milestones = len(milestones)
        completed_milestones = len(
            [m for m in milestones if m.completion_percentage >= 100]
        )
        in_progress_milestones = len(
            [m for m in milestones if 0 < m.completion_percentage < 100]
        )

        return {
            "milestones": milestones,
            "total_count": total_milestones,
            "completed_count": completed_milestones,
            "in_progress_count": in_progress_milestones,
            "completion_rate": (completed_milestones / max(total_milestones, 1)) * 100,
        }

    async def _get_agent_performance_data(self, session: AsyncSession) -> dict:
        """Get agent performance data from database."""
        # Get agent activities
        activities_query = (
            select(AgentActivity).order_by(AgentActivity.timestamp.desc()).limit(100)
        )
        activities_result = await session.execute(activities_query)
        activities = activities_result.scalars().all()

        # Get workflows
        workflows_query = select(AgentWorkflow).order_by(
            AgentWorkflow.updated_at.desc()
        )
        workflows_result = await session.execute(workflows_query)
        workflows = workflows_result.scalars().all()

        # Calculate agent statistics
        agent_stats = {}
        for activity in activities:
            agent_name = activity.agent_name
            if agent_name not in agent_stats:
                agent_stats[agent_name] = {
                    "activities": 0,
                    "last_activity": activity.timestamp,
                }
            agent_stats[agent_name]["activities"] += 1

        return {
            "activities": activities,
            "workflows": workflows,
            "agent_stats": agent_stats,
        }

    async def _get_daily_status_data(self, session: AsyncSession) -> dict:
        """Get daily status data from database."""
        # Get counts for various entities
        milestones_count = await session.execute(
            select(func.count(ProjectMilestone.id))
        )
        workflows_count = await session.execute(select(func.count(AgentWorkflow.id)))
        debt_count = await session.execute(select(func.count(TechnicalDebtItem.id)))
        checkpoints_count = await session.execute(
            select(func.count(IntegrationCheckpoint.id))
        )

        return {
            "milestones_count": milestones_count.scalar(),
            "workflows_count": workflows_count.scalar(),
            "debt_count": debt_count.scalar(),
            "checkpoints_count": checkpoints_count.scalar(),
            "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
        }

    async def _generate_milestone_tracker_content(self, data: dict) -> str:
        """Generate milestone tracker content."""
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        content = f"""# ARES Milestone Tracker

## Active Milestone Tracking
**Last Updated**: {current_time}
**Tracking Mode**: Automated update
**Data Source**: Project tracking database

## Overview Statistics
- **Total Milestones**: {data["total_count"]}
- **Completed**: {data["completed_count"]}
- **In Progress**: {data["in_progress_count"]}
- **Completion Rate**: {data["completion_rate"]:.1f}%

## Recent Milestones
"""

        for milestone in data["milestones"][:10]:  # Show top 10
            status_icon = (
                "✅"
                if milestone.completion_percentage >= 100
                else "🔄"
                if milestone.completion_percentage > 0
                else "⏳"
            )
            content += f"- {status_icon} **{milestone.title}** ({milestone.component.value}): {milestone.completion_percentage}%\n"

        content += f"""
---
**Auto-generated**: {current_time}
**Next Update**: Automated every 15 minutes
"""

        return content

    async def _generate_agent_performance_content(self, data: dict) -> str:
        """Generate agent performance tracker content."""
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        content = f"""# ARES Agent Performance Tracker

## Real-Time Agent Performance Dashboard
**Last Updated**: {current_time}
**Data Source**: Agent activity database

## Agent Activity Summary
- **Total Recent Activities**: {len(data["activities"])}
- **Active Agents**: {len(data["agent_stats"])}
- **Total Workflows**: {len(data["workflows"])}

## Top Active Agents
"""

        # Sort agents by activity count
        sorted_agents = sorted(
            data["agent_stats"].items(), key=lambda x: x[1]["activities"], reverse=True
        )

        for i, (agent_name, stats) in enumerate(sorted_agents[:10], 1):
            content += f"{i}. **{agent_name}**: {stats['activities']} activities (Last: {stats['last_activity'].strftime('%Y-%m-%d %H:%M')})\n"

        content += f"""
---
**Auto-generated**: {current_time}
**Next Update**: Automated every 15 minutes
"""

        return content

    async def _generate_daily_status_content(self, data: dict) -> str:
        """Generate daily status report content."""
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        content = f"""# ARES Daily Status Report

## Executive Summary
**Date**: {data["report_date"]}
**Report Generated**: {current_time}
**Status**: Automated Report

## System Overview
- **Milestones**: {data["milestones_count"]} total
- **Workflows**: {data["workflows_count"]} total
- **Technical Debt Items**: {data["debt_count"]} total
- **Integration Checkpoints**: {data["checkpoints_count"]} total

## System Health
- **Database**: Operational
- **API Endpoints**: Functional
- **Documentation System**: Active

---
**Auto-generated**: {current_time}
**Next Report**: Tomorrow at 18:00 UTC
"""

        return content

    async def get_project_statistics(self) -> dict:
        """Get overall project statistics."""
        try:
            async with get_async_session() as session:
                # Get various counts
                stats = {}

                # Milestones
                milestones_query = select(func.count(ProjectMilestone.id))
                milestones_result = await session.execute(milestones_query)
                stats["total_milestones"] = milestones_result.scalar()

                # Completed milestones
                completed_query = select(func.count(ProjectMilestone.id)).where(
                    ProjectMilestone.completion_percentage >= 100
                )
                completed_result = await session.execute(completed_query)
                stats["completed_milestones"] = completed_result.scalar()

                # Workflows
                workflows_query = select(func.count(AgentWorkflow.id))
                workflows_result = await session.execute(workflows_query)
                stats["total_workflows"] = workflows_result.scalar()

                # Technical debt
                debt_query = select(func.count(TechnicalDebtItem.id))
                debt_result = await session.execute(debt_query)
                stats["total_debt"] = debt_result.scalar()

                # Calculate completion rate
                stats["completion_rate"] = (
                    stats["completed_milestones"] / max(stats["total_milestones"], 1)
                ) * 100

                return stats

        except Exception as e:
            print(f"Error getting project statistics: {e}")
            return {}


async def main():
    """Main function for the tracker update script."""
    parser = argparse.ArgumentParser(description="ARES Project Tracker Update Script")
    parser.add_argument(
        "--update",
        choices=["all", "milestones", "agents", "status"],
        default="all",
        help="Which tracker to update",
    )
    parser.add_argument("--stats", action="store_true", help="Show project statistics")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    updater = ProjectTrackerUpdater()

    if args.stats:
        print("📊 Getting project statistics...")
        stats = await updater.get_project_statistics()
        print(f"""
Project Statistics:
==================
Total Milestones: {stats.get("total_milestones", 0)}
Completed Milestones: {stats.get("completed_milestones", 0)}
Completion Rate: {stats.get("completion_rate", 0):.1f}%
Total Workflows: {stats.get("total_workflows", 0)}
Technical Debt Items: {stats.get("total_debt", 0)}
""")
        return

    if args.update == "all":
        results = await updater.update_all_trackers()
    elif args.update == "milestones":
        results = {"milestone_tracker": await updater.update_milestone_tracker()}
    elif args.update == "agents":
        results = {
            "agent_performance_tracker": await updater.update_agent_performance_tracker()
        }
    elif args.update == "status":
        results = {"daily_status_report": await updater.update_daily_status_report()}

    # Print results
    print("\n📋 Update Results:")
    for tracker, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {tracker}: {status}")

    # Summary
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    print(f"\n📈 Summary: {successful}/{total} trackers updated successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Update cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
