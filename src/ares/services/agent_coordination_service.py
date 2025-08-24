"""Agent coordination service for ARES."""

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ..coordination.agent_registry import AgentRegistry
from ..coordination.routing_manager import RoutingManager
from ..coordination.task_coordinator import TaskCoordinator, TaskRequirement
from ..coordination.workflow_engine import WorkflowEngine
from ..models.agent import Agent
from ..models.base import get_async_session
from .schemas import (
    AgentCapability,
    AgentMetric,
    CoordinationRequest,
    CoordinationResponse,
)

logger = logging.getLogger(__name__)


class AgentCoordinationService:
    """Service for coordinating agent tasks and workflows."""

    def __init__(
        self,
        agent_registry: AgentRegistry | None = None,
        task_coordinator: TaskCoordinator | None = None,
        workflow_engine: WorkflowEngine | None = None,
        routing_manager: RoutingManager | None = None,
    ):
        """Initialize the coordination service."""
        self.agent_registry = agent_registry
        self.task_coordinator = task_coordinator
        self.workflow_engine = workflow_engine
        self.routing_manager = routing_manager

        # Initialize state tracking
        self.active_coordinations = {}
        self.coordination_history = []
        self.service_stats = {}
        self.background_tasks = []
        self.is_running = False

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status."""
        components_initialized = (
            self.agent_registry is not None
            and self.task_coordinator is not None
            and self.workflow_engine is not None
            and self.routing_manager is not None
        )

        return {
            "service_running": self.is_running,
            "components_initialized": components_initialized,
            "active_coordinations": len(self.active_coordinations),
            "background_tasks": len(self.background_tasks),
            "statistics": self.service_stats,
            "last_health_check": datetime.utcnow().isoformat(),
        }

    async def shutdown(self):
        """Shutdown the coordination service gracefully."""
        logger.info("Shutting down coordination service...")

        # Cancel background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self.background_tasks.clear()
        self.is_running = False
        logger.info("Coordination service shutdown complete")

    async def get_coordination_status(
        self, coordination_id: UUID
    ) -> dict[str, Any] | None:
        """Get status of a coordination request."""
        if coordination_id not in self.active_coordinations:
            return None

        coordination = self.active_coordinations[coordination_id]
        return {
            "coordination_id": str(coordination_id),
            "status": coordination.get("status", "unknown"),
            "progress": coordination.get("progress", 0),
            "created_at": coordination.get("created_at", datetime.utcnow()).isoformat(),
        }

    async def cancel_coordination(self, coordination_id: UUID) -> bool:
        """Cancel a coordination request."""
        if coordination_id not in self.active_coordinations:
            return False

        try:
            # Cancel the coordination
            coordination = self.active_coordinations[coordination_id]
            coordination["status"] = "cancelled"

            # Move to history
            self.coordination_history.append(coordination)
            del self.active_coordinations[coordination_id]

            return True
        except Exception as e:
            logger.error(f"Failed to cancel coordination {coordination_id}: {e}")
            return False

    async def coordinate_agents(
        self, request: CoordinationRequest
    ) -> CoordinationResponse:
        """Coordinate multiple agents for a complex task."""
        logger.info(f"Coordinating agents for request: {request.request_id}")

        # If service is not properly initialized, return error response
        if not all(
            [
                self.agent_registry,
                self.task_coordinator,
                self.workflow_engine,
                self.routing_manager,
            ]
        ):
            logger.error("Coordination service not fully initialized")
            return CoordinationResponse(
                request_id=request.request_id,
                status="failed",
                confidence_score=0.0,
                coordination_plan={"error": "Service not fully initialized"},
            )

        try:
            # Delegate to appropriate coordination method based on type
            if request.coordination_type == "task":
                return await self._coordinate_task(request)
            elif request.coordination_type == "multi_agent":
                return await self._coordinate_multi_agent(request)
            elif request.coordination_type == "reactive":
                return await self._coordinate_reactive(request)
            else:
                # Default to task coordination
                return await self._coordinate_task(request)

        except Exception as e:
            logger.error(f"Failed to coordinate agents: {e}")
            return CoordinationResponse(
                request_id=request.request_id,
                status="failed",
                confidence_score=0.0,
                coordination_plan={"error": str(e)},
            )

    async def _coordinate_task(
        self, request: CoordinationRequest
    ) -> CoordinationResponse:
        """Coordinate a single task."""
        # Use routing manager to find best agent
        routing_decision = await self.routing_manager.route_task(request)

        if not routing_decision or not routing_decision.selected_agent:
            return CoordinationResponse(
                request_id=request.request_id,
                status="failed",
                confidence_score=0.0,
                coordination_plan={"error": "No suitable agent found"},
            )

        # Create task using task coordinator
        task_requirements = [
            TaskRequirement(capability=cap) for cap in request.required_capabilities
        ]

        task = await self.task_coordinator.create_task(
            title=request.title,
            description=request.description,
            priority=request.priority,
            requirements=task_requirements,
            preferred_agents=[routing_decision.selected_agent],
        )

        # Log coordination activity
        await self._log_coordination_activity(
            request, routing_decision.selected_agent, task.task_id
        )

        return CoordinationResponse(
            request_id=request.request_id,
            status="accepted",
            assigned_agents=[routing_decision.selected_agent],
            task_ids=[task.task_id],
            confidence_score=routing_decision.confidence_score,
            coordination_plan={
                "type": "task",
                "strategy": routing_decision.routing_strategy.value
                if routing_decision.routing_strategy
                else "default",
                "agent": routing_decision.selected_agent,
                "task_id": str(task.task_id),
            },
        )

    async def _coordinate_multi_agent(
        self, request: CoordinationRequest
    ) -> CoordinationResponse:
        """Coordinate multiple agents for complex tasks."""
        # Decompose request into subtasks
        subtasks = await self._decompose_multi_agent_request(request)

        assigned_agents = []
        task_ids = []
        total_confidence = 0.0

        for subtask in subtasks:
            # Route each subtask
            routing_decision = await self.routing_manager.route_task(subtask)

            if routing_decision and routing_decision.selected_agent:
                # Create the task
                task = await self.task_coordinator.create_task(
                    title=subtask.title,
                    description=subtask.description,
                    priority=subtask.priority,
                    requirements=[
                        TaskRequirement(capability=cap)
                        for cap in subtask.required_capabilities
                    ],
                    preferred_agents=[routing_decision.selected_agent],
                )

                assigned_agents.append(routing_decision.selected_agent)
                task_ids.append(task.task_id)
                total_confidence += routing_decision.confidence_score

        avg_confidence = total_confidence / len(subtasks) if subtasks else 0.0

        return CoordinationResponse(
            request_id=request.request_id,
            status="accepted",
            assigned_agents=assigned_agents,
            task_ids=task_ids,
            confidence_score=avg_confidence,
            coordination_plan={
                "type": "multi_agent",
                "subtasks": len(subtasks),
                "agents": len(set(assigned_agents)),
            },
        )

    async def _coordinate_reactive(
        self, request: CoordinationRequest
    ) -> CoordinationResponse:
        """Set up reactive coordination that responds to events."""
        # Set up monitoring for reactive coordination
        coordination_id = uuid4()

        coordination_data = {
            "coordination_id": coordination_id,
            "status": "monitoring",
            "request": request,
            "created_at": datetime.utcnow(),
            "triggers": request.metadata.get("triggers", []),
        }

        self.active_coordinations[coordination_id] = coordination_data

        return CoordinationResponse(
            request_id=request.request_id,
            coordination_id=coordination_id,
            status="monitoring",
            confidence_score=80.0,
            coordination_plan={
                "type": "reactive",
                "monitoring_enabled": True,
                "trigger_conditions": request.metadata.get("triggers", []),
            },
        )

    async def _decompose_multi_agent_request(
        self, request: CoordinationRequest
    ) -> list[CoordinationRequest]:
        """Decompose a multi-agent request into subtasks."""
        if not request.required_capabilities:
            # If no specific capabilities, return single task with estimated duration set
            single_task = CoordinationRequest(
                title=request.title,
                description=request.description,
                coordination_type=request.coordination_type,
                priority=request.priority,
                required_capabilities=request.required_capabilities,
                preferred_agents=request.preferred_agents,
                timeout_minutes=request.timeout_minutes,
                estimated_duration_minutes=request.timeout_minutes,  # Set to timeout for single task
                max_retries=request.max_retries,
                metadata=request.metadata,
                workflow_id=request.workflow_id,
                custom_workflow=request.custom_workflow,
            )
            return [single_task]

        # Create subtask for each capability
        subtasks = []
        estimated_time_per_task = request.timeout_minutes // len(
            request.required_capabilities
        )

        for i, capability in enumerate(request.required_capabilities):
            subtask = CoordinationRequest(
                title=f"{request.title} - Part {i + 1}",
                description=f"Subtask for {capability}: {request.description}",
                coordination_type="task",
                priority=request.priority,
                required_capabilities=[capability],
                timeout_minutes=estimated_time_per_task,
                estimated_duration_minutes=estimated_time_per_task,  # Set the field the test expects
                metadata=request.metadata,
            )
            subtasks.append(subtask)

        return subtasks

    async def _log_coordination_activity(
        self, request: CoordinationRequest, agent: str, task_id: UUID
    ):
        """Log coordination activity."""
        activity = {
            "timestamp": datetime.utcnow(),
            "request_id": str(request.request_id),
            "agent": agent,
            "task_id": str(task_id),
            "action": "task_assigned",
        }

        # In a real implementation, this would log to database
        logger.info(f"Coordination activity: {activity}")

    async def get_coordination_status_detailed(
        self, coordination_id: str
    ) -> dict[str, Any]:
        """Get detailed status of a coordination request."""
        try:
            # Get workflow execution status directly from workflow engine
            if self.workflow_engine:
                execution = await self.workflow_engine.get_execution_status(
                    coordination_id
                )

                if not execution:
                    return {"status": "not_found", "message": "Coordination not found"}

                return {
                    "status": execution.status.value,
                    "progress": execution.progress_percentage,
                    "current_step": execution.current_step,
                    "started_at": execution.started_at.isoformat()
                    if execution.started_at
                    else None,
                    "completed_at": execution.completed_at.isoformat()
                    if execution.completed_at
                    else None,
                    "error_message": execution.error_message,
                }
            else:
                return {"status": "error", "message": "Workflow engine not available"}

        except Exception as e:
            logger.error(f"Failed to get coordination status: {e}")
            return {"status": "error", "message": str(e)}

    async def _find_available_agents(
        self, required_capabilities: list[AgentCapability]
    ) -> list[Agent]:
        """Find agents with required capabilities."""
        async with get_async_session() as session:
            try:
                # For now, return all active agents
                # In future, filter by capabilities
                agents_result = await session.execute(
                    "SELECT * FROM agents WHERE status = 'active'"
                )
                return agents_result.fetchall()

            except Exception as e:
                logger.error(f"Error finding available agents: {e}")
                return []

    async def _create_default_workflow(self, request: CoordinationRequest):
        """Create a default workflow based on the coordination request."""
        if self.workflow_engine:
            # This would create a workflow with standard steps
            # Implementation depends on the workflow engine
            return await self.workflow_engine.create_workflow(
                name=f"Default workflow for {request.request_id}",
                description="Auto-generated default workflow",
                steps=[],  # Add default steps based on request
            )
        else:
            raise ValueError("Workflow engine not available")

    async def _create_custom_workflow(self, request: CoordinationRequest):
        """Create a custom workflow from the request specification."""
        if self.workflow_engine:
            # This would parse the custom workflow definition
            # Implementation depends on the workflow specification format
            return await self.workflow_engine.create_workflow(
                name=f"Custom workflow for {request.request_id}",
                description="Custom workflow from request",
                steps=request.custom_workflow.get("steps", []),
            )
        else:
            raise ValueError("Workflow engine not available")

    async def get_agent_metrics(self, agent_id: str) -> AgentMetric | None:
        """Get performance metrics for an agent."""
        async with get_async_session() as session:
            try:
                # Get agent tasks and calculate metrics
                tasks_query = """
                    SELECT * FROM tasks
                    WHERE assigned_agent = :agent_id
                    AND created_at >= datetime('now', '-7 days')
                """
                result = await session.execute(tasks_query, {"agent_id": agent_id})
                recent_tasks = result.fetchall()

                if not recent_tasks:
                    return None

                completed_tasks = [
                    t for t in recent_tasks if t["status"] == "completed"
                ]
                failed_tasks = [t for t in recent_tasks if t["status"] == "failed"]

                success_rate = (
                    len(completed_tasks) / len(recent_tasks) * 100
                    if recent_tasks
                    else 0
                )

                # Calculate average completion time
                avg_completion_time = 0
                if completed_tasks:
                    completion_times = [
                        (
                            datetime.fromisoformat(t["completed_at"])
                            - datetime.fromisoformat(t["created_at"])
                        ).total_seconds()
                        / 60  # Convert to minutes
                        for t in completed_tasks
                        if t["completed_at"]
                    ]
                    if completion_times:
                        avg_completion_time = sum(completion_times) / len(
                            completion_times
                        )

                return AgentMetric(
                    agent_id=agent_id,
                    tasks_completed=len(completed_tasks),
                    tasks_failed=len(failed_tasks),
                    success_rate=success_rate,
                    average_completion_time_minutes=avg_completion_time,
                    load_factor=min(len(recent_tasks) / 10.0, 1.0),  # Normalize to 0-1
                )

            except Exception as e:
                logger.error(f"Error getting agent metrics: {e}")
                return None

    async def optimize_agent_assignments(self) -> dict[str, Any]:
        """Optimize agent assignments based on current load and capabilities."""
        try:
            async with get_async_session() as session:
                # Get all active agents
                agents_result = await session.execute(
                    "SELECT * FROM agents WHERE status = 'active'"
                )
                agents = agents_result.fetchall()

                # Get pending tasks
                tasks_result = await session.execute(
                    "SELECT * FROM tasks WHERE status = 'pending'"
                )
                pending_tasks = tasks_result.fetchall()

                optimization_results = {
                    "total_agents": len(agents),
                    "pending_tasks": len(pending_tasks),
                    "recommendations": [],
                }

                # Simple load balancing logic
                if agents and pending_tasks:
                    tasks_per_agent = len(pending_tasks) // len(agents)
                    for i, agent in enumerate(agents):
                        start_idx = i * tasks_per_agent
                        end_idx = (
                            start_idx + tasks_per_agent
                            if i < len(agents) - 1
                            else len(pending_tasks)
                        )
                        assigned_tasks = pending_tasks[start_idx:end_idx]

                        optimization_results["recommendations"].append(
                            {
                                "agent_id": agent["agent_id"],
                                "recommended_tasks": [
                                    t["task_id"] for t in assigned_tasks
                                ],
                                "task_count": len(assigned_tasks),
                            }
                        )

                return optimization_results

        except Exception as e:
            logger.error(f"Error optimizing agent assignments: {e}")
            return {"error": str(e)}


# Create singleton instance
coordination_service = AgentCoordinationService()
