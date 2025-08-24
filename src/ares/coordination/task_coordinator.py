"""Task Coordinator for intelligent task assignment and management."""

import logging
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ..models.base import get_async_session
from ..models.project_tracking import (
    ActivityType,
    AgentActivity,
    AgentWorkflow,
    WorkflowStatus,
)
from .agent_registry import AgentProfile, AgentRegistry

logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    """Task priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Task status states."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskDependency(BaseModel):
    """Task dependency relationship."""

    task_id: UUID
    dependency_type: str = Field(
        default="prerequisite"
    )  # prerequisite, optional, blocking
    status: str = Field(default="pending")


class TaskRequirement(BaseModel):
    """Task capability requirements."""

    capability: str = Field(..., description="Required capability name")
    minimum_proficiency: int = Field(default=1, ge=1, le=10)
    required: bool = Field(default=True)
    weight: float = Field(default=1.0, ge=0.1, le=10.0)


class TaskDefinition(BaseModel):
    """Complete task definition with requirements and constraints."""

    task_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Detailed task description")

    # Task metadata
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    estimated_duration_minutes: int | None = Field(default=None, ge=1)
    complexity_score: int = Field(default=5, ge=1, le=10)

    # Requirements and constraints
    requirements: list[TaskRequirement] = Field(default_factory=list)
    preferred_agents: list[str] = Field(default_factory=list)
    excluded_agents: list[str] = Field(default_factory=list)
    max_concurrent_agents: int = Field(default=1, ge=1, le=5)

    # Dependencies
    dependencies: list[TaskDependency] = Field(default_factory=list)
    blocking_tasks: list[UUID] = Field(default_factory=list)

    # Status and tracking
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    assigned_agents: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_at: datetime | None = Field(default=None)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    # Results and feedback
    result_data: dict | None = Field(default=None)
    feedback_score: float | None = Field(default=None, ge=0.0, le=10.0)
    error_message: str | None = Field(default=None)


class AgentAssignment(BaseModel):
    """Agent assignment for a task."""

    agent_name: str
    task_id: UUID
    assignment_score: float = Field(ge=0.0, le=100.0)
    assignment_reason: str
    estimated_completion_time: datetime | None = Field(default=None)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCoordinator:
    """Intelligent task coordinator for agent assignment and workflow management."""

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self.active_tasks: dict[UUID, TaskDefinition] = {}
        self.task_queue: list[TaskDefinition] = []
        self.agent_assignments: dict[str, list[UUID]] = {}  # agent_name -> task_ids
        self.task_history: list[TaskDefinition] = []

    async def create_task(
        self,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        requirements: list[TaskRequirement] | None = None,
        preferred_agents: list[str] | None = None,
        **kwargs,
    ) -> TaskDefinition:
        """Create a new task with specified requirements."""

        task = TaskDefinition(
            title=title,
            description=description,
            priority=priority,
            requirements=requirements or [],
            preferred_agents=preferred_agents or [],
            **kwargs,
        )

        # Add to task queue
        self.task_queue.append(task)

        logger.info(
            f"Created task: {task.title} (ID: {task.task_id}) with priority {priority}"
        )

        # Attempt immediate assignment if possible
        await self._attempt_immediate_assignment(task)

        return task

    async def _attempt_immediate_assignment(self, task: TaskDefinition):
        """Attempt to assign task immediately if suitable agents are available."""
        candidate_agents = await self.find_suitable_agents(task)

        if candidate_agents:
            # Get the best candidate
            best_candidate = candidate_agents[0]

            # Check if agent is available
            agent_profile = self.agent_registry.get_agent(best_candidate.agent_name)
            if agent_profile and agent_profile.status.status == "available":
                await self.assign_task(task.task_id, best_candidate.agent_name)

    async def find_suitable_agents(
        self, task: TaskDefinition, limit: int = 5
    ) -> list[AgentAssignment]:
        """Find agents suitable for a task based on capabilities and availability."""

        suitable_agents = []

        # Get all available agents
        available_agents = self.agent_registry.get_available_agents()

        for agent in available_agents:
            # Skip excluded agents
            if agent.name in task.excluded_agents:
                continue

            # Calculate assignment score
            score = await self._calculate_assignment_score(agent, task)

            # Only consider agents with minimum score
            if score >= 30.0:  # Minimum 30% match
                assignment = AgentAssignment(
                    agent_name=agent.name,
                    task_id=task.task_id,
                    assignment_score=score,
                    assignment_reason=await self._generate_assignment_reason(
                        agent, task, score
                    ),
                )
                suitable_agents.append(assignment)

        # Sort by score (highest first) and return top candidates
        suitable_agents.sort(key=lambda x: x.assignment_score, reverse=True)
        return suitable_agents[:limit]

    async def _calculate_assignment_score(
        self, agent: AgentProfile, task: TaskDefinition
    ) -> float:
        """Calculate how well an agent matches a task."""
        score = 0.0
        max_score = 0.0

        # Base score for availability
        if agent.status.status == "available":
            score += 20.0
        elif agent.status.workload_percentage < 50:
            score += 10.0
        max_score += 20.0

        # Priority matching bonus
        priority_bonus = {
            "critical": {"critical": 15, "high": 10, "medium": 5, "low": 0},
            "high": {"critical": 10, "high": 15, "medium": 10, "low": 5},
            "medium": {"critical": 5, "high": 10, "medium": 15, "low": 10},
            "low": {"critical": 0, "high": 5, "medium": 10, "low": 15},
        }
        score += priority_bonus.get(agent.priority_level, {}).get(
            task.priority.value, 0
        )
        max_score += 15.0

        # Capability matching
        if task.requirements:
            capability_score = 0.0
            capability_max = 0.0

            for requirement in task.requirements:
                # Find matching capability in agent
                matching_capability = None
                for capability in agent.capabilities:
                    if capability.name == requirement.capability:
                        matching_capability = capability
                        break

                requirement_weight = requirement.weight
                capability_max += requirement_weight * 10

                if matching_capability:
                    # Score based on proficiency vs requirement
                    proficiency_ratio = (
                        matching_capability.proficiency_level
                        / requirement.minimum_proficiency
                    )
                    capability_score += min(
                        requirement_weight * 10,
                        proficiency_ratio * requirement_weight * 10,
                    )
                elif not requirement.required:
                    # Partial credit for optional requirements
                    capability_score += requirement_weight * 2

            if capability_max > 0:
                score += (capability_score / capability_max) * 40.0
            max_score += 40.0
        else:
            # No specific requirements, give moderate score
            score += 20.0
            max_score += 40.0

        # Preferred agent bonus
        if agent.name in task.preferred_agents:
            score += 15.0
        max_score += 15.0

        # Reliability and performance bonus
        reliability_bonus = (agent.metrics.reliability_score / 100.0) * 10.0
        score += reliability_bonus
        max_score += 10.0

        # Workload penalty
        workload_penalty = (agent.status.workload_percentage / 100.0) * 5.0
        score -= workload_penalty

        # Normalize to 0-100 scale
        if max_score > 0:
            normalized_score = (score / max_score) * 100.0
            return max(0.0, min(100.0, normalized_score))

        return 0.0

    async def _generate_assignment_reason(
        self, agent: AgentProfile, task: TaskDefinition, score: float
    ) -> str:
        """Generate human-readable reason for agent assignment."""
        reasons = []

        # Capability matching
        if task.requirements:
            matched_capabilities = []
            for requirement in task.requirements:
                for capability in agent.capabilities:
                    if capability.name == requirement.capability:
                        matched_capabilities.append(capability.name)
                        break

            if matched_capabilities:
                reasons.append(f"Capabilities: {', '.join(matched_capabilities)}")

        # Priority matching
        if agent.priority_level == task.priority.value:
            reasons.append(f"Priority match: {task.priority.value}")

        # Availability
        if agent.status.status == "available":
            reasons.append("Available")
        elif agent.status.workload_percentage < 50:
            reasons.append(f"Low workload ({agent.status.workload_percentage}%)")

        # Reliability
        if agent.metrics.reliability_score > 80:
            reasons.append(f"High reliability ({agent.metrics.reliability_score:.1f}%)")

        # Preferred agent
        if agent.name in task.preferred_agents:
            reasons.append("Preferred agent")

        if not reasons:
            reasons.append("General capability match")

        return f"Score: {score:.1f}% - " + "; ".join(reasons)

    async def assign_task(self, task_id: UUID, agent_name: str) -> bool:
        """Assign a task to a specific agent."""
        # Find task in queue or active tasks
        task = None
        for t in self.task_queue:
            if t.task_id == task_id:
                task = t
                self.task_queue.remove(t)
                break

        if not task and task_id in self.active_tasks:
            task = self.active_tasks[task_id]

        if not task:
            logger.error(f"Task {task_id} not found for assignment")
            return False

        # Verify agent exists and is available
        agent = self.agent_registry.get_agent(agent_name)
        if not agent:
            logger.error(f"Agent {agent_name} not found")
            return False

        # Assign the task
        task.status = TaskStatus.ASSIGNED
        task.assigned_agents = [agent_name]
        task.assigned_at = datetime.utcnow()

        # Move to active tasks
        self.active_tasks[task_id] = task

        # Update agent assignments
        if agent_name not in self.agent_assignments:
            self.agent_assignments[agent_name] = []
        self.agent_assignments[agent_name].append(task_id)

        # Update agent status
        await self.agent_registry.update_agent_status(agent_name, "busy", task.title)

        # Log assignment in database
        await self._log_task_assignment(task, agent_name)

        logger.info(f"Assigned task '{task.title}' to agent {agent_name}")
        return True

    async def start_task(self, task_id: UUID, agent_name: str) -> bool:
        """Mark a task as started by an agent."""
        task = self.active_tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in active tasks")
            return False

        if agent_name not in task.assigned_agents:
            logger.error(f"Agent {agent_name} not assigned to task {task_id}")
            return False

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

        # Log task start
        await self._log_agent_activity(
            agent_name,
            ActivityType.TASK_STARTED,
            {"task_id": str(task_id), "task_title": task.title},
        )

        logger.info(f"Task '{task.title}' started by agent {agent_name}")
        return True

    async def complete_task(
        self,
        task_id: UUID,
        agent_name: str,
        result_data: dict | None = None,
        feedback_score: float | None = None,
    ) -> bool:
        """Mark a task as completed by an agent."""
        task = self.active_tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in active tasks")
            return False

        if agent_name not in task.assigned_agents:
            logger.error(f"Agent {agent_name} not assigned to task {task_id}")
            return False

        # Complete the task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result_data = result_data
        task.feedback_score = feedback_score

        # Move to history
        self.task_history.append(task)
        del self.active_tasks[task_id]

        # Update agent assignments
        if agent_name in self.agent_assignments:
            self.agent_assignments[agent_name].remove(task_id)

            # If no more tasks, mark agent as available
            if not self.agent_assignments[agent_name]:
                await self.agent_registry.update_agent_status(agent_name, "available")

        # Update agent metrics
        completion_time = None
        if task.started_at:
            completion_time = (
                task.completed_at - task.started_at
            ).total_seconds() / 60.0  # minutes

        await self.agent_registry.update_agent_metrics(
            agent_name,
            total_tasks_completed=self.agent_registry.get_agent(
                agent_name
            ).metrics.total_tasks_completed
            + 1,
            average_completion_time=completion_time,
            last_activity=datetime.utcnow(),
        )

        # Log completion
        await self._log_agent_activity(
            agent_name,
            ActivityType.TASK_COMPLETED,
            {
                "task_id": str(task_id),
                "task_title": task.title,
                "completion_time_minutes": completion_time,
                "feedback_score": feedback_score,
            },
        )

        logger.info(f"Task '{task.title}' completed by agent {agent_name}")

        # Check for dependent tasks that can now be started
        await self._check_dependent_tasks(task_id)

        return True

    async def fail_task(
        self, task_id: UUID, agent_name: str, error_message: str, retry: bool = True
    ) -> bool:
        """Mark a task as failed."""
        task = self.active_tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in active tasks")
            return False

        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.completed_at = datetime.utcnow()

        # Log failure
        await self._log_agent_activity(
            agent_name,
            ActivityType.TASK_FAILED,
            {
                "task_id": str(task_id),
                "task_title": task.title,
                "error_message": error_message,
            },
        )

        # Update agent status
        await self.agent_registry.update_agent_status(agent_name, "available")

        # Remove from agent assignments
        if agent_name in self.agent_assignments:
            self.agent_assignments[agent_name].remove(task_id)

        if retry:
            # Reset task for retry
            task.status = TaskStatus.PENDING
            task.assigned_agents = []
            task.assigned_at = None
            task.started_at = None
            task.completed_at = None
            task.error_message = None

            # Add back to queue
            self.task_queue.append(task)
            del self.active_tasks[task_id]

            logger.info(f"Task '{task.title}' failed, added back to queue for retry")
        else:
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]

            logger.info(f"Task '{task.title}' failed permanently")

        return True

    async def _check_dependent_tasks(self, completed_task_id: UUID):
        """Check if any queued tasks can now be started due to dependency completion."""
        for task in self.task_queue[
            :
        ]:  # Copy list to avoid modification during iteration
            dependencies_met = True

            for dependency in task.dependencies:
                if dependency.task_id == completed_task_id:
                    dependency.status = "completed"

                # Check if all prerequisites are met
                if (
                    dependency.dependency_type == "prerequisite"
                    and dependency.status != "completed"
                ):
                    dependencies_met = False
                    break

            if dependencies_met:
                await self._attempt_immediate_assignment(task)

    async def _log_task_assignment(self, task: TaskDefinition, agent_name: str):
        """Log task assignment to database."""
        try:
            async with get_async_session() as session:
                # Create workflow record
                workflow = AgentWorkflow(
                    workflow_name=task.title,
                    description=task.description,
                    assigned_agent=agent_name,
                    status=WorkflowStatus.IN_PROGRESS,
                    priority=task.priority.value,
                    progress_percentage=0,
                )
                session.add(workflow)
                await session.commit()

        except Exception as e:
            logger.error(f"Error logging task assignment: {e}")

    async def _log_agent_activity(
        self, agent_name: str, activity_type: ActivityType, metadata: dict
    ):
        """Log agent activity to database."""
        try:
            async with get_async_session() as session:
                activity = AgentActivity(
                    agent_name=agent_name,
                    activity_type=activity_type,
                    description=f"{activity_type.value}: {metadata.get('task_title', 'Unknown task')}",
                    metadata=metadata,
                )
                session.add(activity)
                await session.commit()

        except Exception as e:
            logger.error(f"Error logging agent activity: {e}")

    def get_task_queue_status(self) -> dict:
        """Get current task queue status."""
        return {
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(
                [t for t in self.task_history if t.status == TaskStatus.COMPLETED]
            ),
            "failed_tasks": len(
                [t for t in self.task_history if t.status == TaskStatus.FAILED]
            ),
            "queue_by_priority": {
                priority.value: len(
                    [t for t in self.task_queue if t.priority == priority]
                )
                for priority in TaskPriority
            },
        }

    def get_agent_workload(self, agent_name: str) -> dict:
        """Get current workload for a specific agent."""
        assigned_tasks = self.agent_assignments.get(agent_name, [])

        active_tasks = [
            self.active_tasks[task_id]
            for task_id in assigned_tasks
            if task_id in self.active_tasks
        ]

        return {
            "agent_name": agent_name,
            "assigned_tasks": len(assigned_tasks),
            "active_tasks": len(active_tasks),
            "current_workload": len(active_tasks),
            "tasks": [
                {
                    "task_id": str(task.task_id),
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "assigned_at": task.assigned_at.isoformat()
                    if task.assigned_at
                    else None,
                }
                for task in active_tasks
            ],
        }

    async def process_task_queue(self):
        """Process pending tasks in the queue and attempt assignments."""
        logger.info(f"Processing task queue with {len(self.task_queue)} pending tasks")

        for task in self.task_queue[:]:  # Copy to avoid modification during iteration
            # Check dependencies
            dependencies_met = True
            for dependency in task.dependencies:
                if (
                    dependency.dependency_type == "prerequisite"
                    and dependency.status != "completed"
                ):
                    dependencies_met = False
                    break

            if dependencies_met:
                candidate_agents = await self.find_suitable_agents(task)

                if candidate_agents:
                    best_candidate = candidate_agents[0]

                    # Assign if agent is available
                    agent = self.agent_registry.get_agent(best_candidate.agent_name)
                    if agent and agent.status.status == "available":
                        await self.assign_task(task.task_id, best_candidate.agent_name)


# Global task coordinator instance
task_coordinator = None


async def get_task_coordinator() -> TaskCoordinator:
    """Get the global task coordinator instance."""
    global task_coordinator
    if task_coordinator is None:
        from .agent_registry import agent_registry

        await agent_registry.initialize()
        task_coordinator = TaskCoordinator(agent_registry)
        logger.info("Task coordinator initialized")
    return task_coordinator
