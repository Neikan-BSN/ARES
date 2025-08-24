"""Workflow Engine for coordinating complex agent workflows and task orchestration."""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import select

from ..models.base import get_async_session
from ..models.project_tracking import (
    ActivityType,
    AgentActivity,
    AgentWorkflow,
    WorkflowStatus,
)
from .agent_registry import AgentProfile, AgentRegistry
from .task_coordinator import TaskCoordinator, TaskDefinition, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    """Types of workflows supported by the engine."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"
    REACTIVE = "reactive"


class WorkflowStep(BaseModel):
    """Individual step in a workflow."""

    step_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Step name")
    description: str = Field(..., description="Step description")

    # Agent assignment
    required_capabilities: list[str] = Field(default_factory=list)
    preferred_agents: list[str] = Field(default_factory=list)
    assigned_agent: str | None = Field(default=None)

    # Dependencies and conditions
    depends_on: list[UUID] = Field(default_factory=list)
    conditions: dict[str, Any] = Field(default_factory=dict)

    # Execution details
    task_definition: TaskDefinition | None = Field(default=None)
    estimated_duration_minutes: int | None = Field(default=None)
    max_retries: int = Field(default=2, ge=0, le=10)

    # Status tracking
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    result_data: dict | None = Field(default=None)
    error_message: str | None = Field(default=None)
    retry_count: int = Field(default=0, ge=0)


class WorkflowDefinition(BaseModel):
    """Complete workflow definition."""

    workflow_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")

    # Workflow metadata
    workflow_type: WorkflowType = Field(default=WorkflowType.SEQUENTIAL)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    category: str = Field(default="general")
    tags: list[str] = Field(default_factory=list)

    # Workflow steps
    steps: list[WorkflowStep] = Field(default_factory=list)

    # Execution settings
    max_concurrent_steps: int = Field(default=3, ge=1, le=10)
    timeout_minutes: int | None = Field(default=None, ge=1)
    auto_retry_failed_steps: bool = Field(default=True)

    # Status and tracking
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    # Results and metrics
    overall_progress: float = Field(default=0.0, ge=0.0, le=100.0)
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    execution_metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowExecution(BaseModel):
    """Runtime workflow execution state."""

    execution_id: UUID = Field(default_factory=uuid4)
    workflow_definition: WorkflowDefinition

    # Execution state
    current_step_ids: set[UUID] = Field(default_factory=set)
    completed_step_ids: set[UUID] = Field(default_factory=set)
    failed_step_ids: set[UUID] = Field(default_factory=set)

    # Agent assignments
    step_agent_assignments: dict[UUID, str] = Field(default_factory=dict)
    agent_workloads: dict[str, int] = Field(default_factory=dict)

    # Execution metrics
    execution_start_time: datetime | None = Field(default=None)
    step_execution_times: dict[UUID, float] = Field(default_factory=dict)
    agent_performance_data: dict[str, dict] = Field(default_factory=dict)


class WorkflowEngine:
    """Advanced workflow engine for coordinating complex agent workflows."""

    def __init__(
        self, agent_registry: AgentRegistry, task_coordinator: TaskCoordinator
    ):
        self.agent_registry = agent_registry
        self.task_coordinator = task_coordinator

        # Active workflows
        self.active_workflows: dict[UUID, WorkflowExecution] = {}
        self.workflow_definitions: dict[UUID, WorkflowDefinition] = {}

        # Workflow templates
        self.workflow_templates: dict[str, WorkflowDefinition] = {}

        # Event handlers
        self.step_completion_handlers: list = []
        self.workflow_completion_handlers: list = []

    async def initialize(self):
        """Initialize the workflow engine with predefined workflows."""
        logger.info("Initializing ARES Workflow Engine...")

        # Register common workflow templates
        await self._register_common_workflows()

        # Load active workflows from database
        await self._load_active_workflows()

        logger.info(
            f"Workflow Engine initialized with {len(self.workflow_templates)} templates"
        )

    async def _register_common_workflows(self):
        """Register common ARES workflow templates."""

        # Documentation Update Workflow
        doc_workflow = WorkflowDefinition(
            name="Documentation Update Workflow",
            description="Comprehensive documentation update and validation workflow",
            workflow_type=WorkflowType.SEQUENTIAL,
            priority=TaskPriority.HIGH,
            category="documentation",
            tags=["documentation", "validation", "automation"],
            steps=[
                WorkflowStep(
                    name="Gather Project Data",
                    description="Collect current project metrics and status information",
                    required_capabilities=["data_collection", "database_operations"],
                    preferred_agents=["@backend-developer"],
                    estimated_duration_minutes=10,
                ),
                WorkflowStep(
                    name="Update Master Documents",
                    description="Update all master tracking documents",
                    required_capabilities=["documentation", "template_processing"],
                    preferred_agents=["@documentation-specialist"],
                    estimated_duration_minutes=15,
                ),
                WorkflowStep(
                    name="Validate Documentation",
                    description="Validate updated documentation for completeness and accuracy",
                    required_capabilities=["quality_assessment", "validation"],
                    preferred_agents=["@code-reviewer"],
                    estimated_duration_minutes=8,
                ),
            ],
            max_concurrent_steps=1,
            timeout_minutes=45,
        )
        self.workflow_templates["documentation_update"] = doc_workflow

        # Agent Reliability Assessment Workflow
        reliability_workflow = WorkflowDefinition(
            name="Agent Reliability Assessment",
            description="Comprehensive agent performance analysis and reliability scoring",
            workflow_type=WorkflowType.PIPELINE,
            priority=TaskPriority.HIGH,
            category="reliability",
            tags=["agent_monitoring", "performance", "assessment"],
            steps=[
                WorkflowStep(
                    name="Collect Agent Metrics",
                    description="Gather performance data from all active agents",
                    required_capabilities=["data_collection", "agent_monitoring"],
                    preferred_agents=["@performance-optimizer"],
                    estimated_duration_minutes=5,
                ),
                WorkflowStep(
                    name="Analyze Performance Patterns",
                    description="Analyze agent behavior patterns and identify trends",
                    required_capabilities=["pattern_discovery", "performance_analysis"],
                    preferred_agents=["@code-archaeologist"],
                    estimated_duration_minutes=12,
                ),
                WorkflowStep(
                    name="Generate Reliability Scores",
                    description="Calculate reliability scores and performance ratings",
                    required_capabilities=["performance_analysis", "scoring"],
                    preferred_agents=["@performance-optimizer"],
                    estimated_duration_minutes=8,
                ),
                WorkflowStep(
                    name="Update Agent Registry",
                    description="Update agent profiles with new reliability data",
                    required_capabilities=["database_operations", "agent_management"],
                    preferred_agents=["@backend-developer"],
                    estimated_duration_minutes=5,
                ),
            ],
            max_concurrent_steps=2,
            timeout_minutes=35,
        )
        self.workflow_templates["agent_reliability_assessment"] = reliability_workflow

        # System Integration Verification Workflow
        integration_workflow = WorkflowDefinition(
            name="System Integration Verification",
            description="Comprehensive system integration testing and validation",
            workflow_type=WorkflowType.PARALLEL,
            priority=TaskPriority.CRITICAL,
            category="integration",
            tags=["integration", "testing", "validation", "system_health"],
            steps=[
                WorkflowStep(
                    name="API Endpoint Testing",
                    description="Test all FastAPI endpoints for functionality",
                    required_capabilities=["api_testing", "integration_testing"],
                    preferred_agents=["@api-architect"],
                    estimated_duration_minutes=15,
                ),
                WorkflowStep(
                    name="Database Integration Testing",
                    description="Verify database connections and operations",
                    required_capabilities=["database_testing", "integration_testing"],
                    preferred_agents=["@backend-developer"],
                    estimated_duration_minutes=12,
                ),
                WorkflowStep(
                    name="MCP Server Validation",
                    description="Validate all MCP server connections and functionality",
                    required_capabilities=["mcp_integration", "validation"],
                    preferred_agents=["@backend-developer"],
                    estimated_duration_minutes=10,
                ),
                WorkflowStep(
                    name="WebSocket Communication Testing",
                    description="Test real-time WebSocket communication",
                    required_capabilities=["websocket_testing", "real_time_systems"],
                    preferred_agents=["@frontend-developer"],
                    estimated_duration_minutes=8,
                ),
            ],
            max_concurrent_steps=4,
            timeout_minutes=25,
        )
        self.workflow_templates["system_integration_verification"] = (
            integration_workflow
        )

    async def create_workflow_from_template(
        self, template_name: str, custom_parameters: dict[str, Any] | None = None
    ) -> WorkflowDefinition:
        """Create a workflow instance from a template."""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")

        template = self.workflow_templates[template_name]

        # Create a new workflow instance
        workflow = WorkflowDefinition(
            name=template.name,
            description=template.description,
            workflow_type=template.workflow_type,
            priority=template.priority,
            category=template.category,
            tags=template.tags.copy(),
            steps=[
                WorkflowStep(
                    name=step.name,
                    description=step.description,
                    required_capabilities=step.required_capabilities.copy(),
                    preferred_agents=step.preferred_agents.copy(),
                    depends_on=step.depends_on.copy(),
                    conditions=step.conditions.copy(),
                    estimated_duration_minutes=step.estimated_duration_minutes,
                    max_retries=step.max_retries,
                )
                for step in template.steps
            ],
            max_concurrent_steps=template.max_concurrent_steps,
            timeout_minutes=template.timeout_minutes,
            auto_retry_failed_steps=template.auto_retry_failed_steps,
        )

        # Apply custom parameters if provided
        if custom_parameters:
            await self._apply_workflow_parameters(workflow, custom_parameters)

        # Store workflow definition
        self.workflow_definitions[workflow.workflow_id] = workflow

        logger.info(
            f"Created workflow '{workflow.name}' from template '{template_name}'"
        )
        return workflow

    async def _apply_workflow_parameters(
        self, workflow: WorkflowDefinition, parameters: dict[str, Any]
    ):
        """Apply custom parameters to a workflow."""
        # Apply workflow-level parameters
        if "priority" in parameters:
            workflow.priority = TaskPriority(parameters["priority"])

        if "timeout_minutes" in parameters:
            workflow.timeout_minutes = parameters["timeout_minutes"]

        if "max_concurrent_steps" in parameters:
            workflow.max_concurrent_steps = parameters["max_concurrent_steps"]

        # Apply step-level parameters
        if "step_parameters" in parameters:
            step_params = parameters["step_parameters"]
            for step in workflow.steps:
                if step.name in step_params:
                    step_param = step_params[step.name]

                    if "preferred_agents" in step_param:
                        step.preferred_agents = step_param["preferred_agents"]

                    if "estimated_duration_minutes" in step_param:
                        step.estimated_duration_minutes = step_param[
                            "estimated_duration_minutes"
                        ]

    async def execute_workflow(self, workflow_id: UUID) -> WorkflowExecution:
        """Execute a workflow with full orchestration."""
        workflow_def = self.workflow_definitions.get(workflow_id)
        if not workflow_def:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Create workflow execution
        execution = WorkflowExecution(
            workflow_definition=workflow_def, execution_start_time=datetime.utcnow()
        )

        # Store active execution
        self.active_workflows[execution.execution_id] = execution

        # Update workflow status
        workflow_def.status = WorkflowStatus.IN_PROGRESS
        workflow_def.started_at = datetime.utcnow()

        # Log workflow start
        await self._log_workflow_event(
            workflow_def,
            "workflow_started",
            {
                "execution_id": str(execution.execution_id),
                "workflow_type": workflow_def.workflow_type.value,
                "total_steps": len(workflow_def.steps),
            },
        )

        logger.info(
            f"Started workflow execution: {workflow_def.name} (ID: {execution.execution_id})"
        )

        # Start workflow execution
        asyncio.create_task(self._execute_workflow_steps(execution))

        return execution

    async def _execute_workflow_steps(self, execution: WorkflowExecution):
        """Execute workflow steps based on workflow type."""
        workflow = execution.workflow_definition

        try:
            if workflow.workflow_type == WorkflowType.SEQUENTIAL:
                await self._execute_sequential_workflow(execution)
            elif workflow.workflow_type == WorkflowType.PARALLEL:
                await self._execute_parallel_workflow(execution)
            elif workflow.workflow_type == WorkflowType.PIPELINE:
                await self._execute_pipeline_workflow(execution)
            elif workflow.workflow_type == WorkflowType.CONDITIONAL:
                await self._execute_conditional_workflow(execution)
            elif workflow.workflow_type == WorkflowType.REACTIVE:
                await self._execute_reactive_workflow(execution)

            # Complete workflow
            await self._complete_workflow(execution)

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            await self._fail_workflow(execution, str(e))

    async def _execute_sequential_workflow(self, execution: WorkflowExecution):
        """Execute workflow steps sequentially."""
        workflow = execution.workflow_definition

        for step in workflow.steps:
            # Check if dependencies are met
            if not await self._check_step_dependencies(step, execution):
                continue

            # Execute step
            step_start_time = datetime.utcnow()
            success = await self._execute_workflow_step(step, execution)

            # Record execution time
            execution_time = (
                datetime.utcnow() - step_start_time
            ).total_seconds() / 60.0
            execution.step_execution_times[step.step_id] = execution_time

            if success:
                execution.completed_step_ids.add(step.step_id)
                step.status = TaskStatus.COMPLETED
                step.completed_at = datetime.utcnow()
            else:
                execution.failed_step_ids.add(step.step_id)
                step.status = TaskStatus.FAILED

                if (
                    not workflow.auto_retry_failed_steps
                    or step.retry_count >= step.max_retries
                ):
                    raise Exception(f"Step '{step.name}' failed and cannot be retried")

                # Retry step
                step.retry_count += 1
                step.status = TaskStatus.PENDING

                # Re-execute step
                success = await self._execute_workflow_step(step, execution)
                if success:
                    execution.completed_step_ids.add(step.step_id)
                    step.status = TaskStatus.COMPLETED
                    step.completed_at = datetime.utcnow()
                else:
                    execution.failed_step_ids.add(step.step_id)
                    step.status = TaskStatus.FAILED
                    raise Exception(
                        f"Step '{step.name}' failed after {step.retry_count} retries"
                    )

    async def _execute_parallel_workflow(self, execution: WorkflowExecution):
        """Execute workflow steps in parallel."""
        workflow = execution.workflow_definition

        # Create tasks for all eligible steps
        step_tasks = []
        for step in workflow.steps:
            if await self._check_step_dependencies(step, execution):
                task = asyncio.create_task(
                    self._execute_step_with_tracking(step, execution)
                )
                step_tasks.append(task)

        # Wait for all steps to complete
        results = await asyncio.gather(*step_tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            step = workflow.steps[i]
            if isinstance(result, Exception):
                execution.failed_step_ids.add(step.step_id)
                step.status = TaskStatus.FAILED
                step.error_message = str(result)
            else:
                execution.completed_step_ids.add(step.step_id)
                step.status = TaskStatus.COMPLETED
                step.completed_at = datetime.utcnow()

    async def _execute_pipeline_workflow(self, execution: WorkflowExecution):
        """Execute workflow steps in pipeline fashion."""
        workflow = execution.workflow_definition

        # Execute steps with pipeline coordination
        active_steps = []
        completed_steps = set()

        for step in workflow.steps:
            # Wait for dependencies efficiently
            if step.depends_on and not all(
                dep_id in completed_steps for dep_id in step.depends_on
            ):
                # Use a brief sleep instead of busy loop
                await asyncio.sleep(0.1)

            # Start step execution
            step_task = asyncio.create_task(
                self._execute_step_with_tracking(step, execution)
            )
            active_steps.append((step, step_task))

            # Manage concurrency
            if len(active_steps) >= workflow.max_concurrent_steps:
                # Wait for oldest step to complete
                step, task = active_steps.pop(0)
                await task
                completed_steps.add(step.step_id)

        # Wait for remaining steps
        for step, task in active_steps:
            await task
            completed_steps.add(step.step_id)

    async def _execute_conditional_workflow(self, execution: WorkflowExecution):
        """Execute workflow with conditional branching."""
        workflow = execution.workflow_definition

        for step in workflow.steps:
            # Check conditions
            if not await self._evaluate_step_conditions(step, execution):
                logger.info(f"Skipping step '{step.name}' - conditions not met")
                continue

            # Execute step
            success = await self._execute_workflow_step(step, execution)

            if success:
                execution.completed_step_ids.add(step.step_id)
                step.status = TaskStatus.COMPLETED
            else:
                execution.failed_step_ids.add(step.step_id)
                step.status = TaskStatus.FAILED

    async def _execute_reactive_workflow(self, execution: WorkflowExecution):
        """Execute workflow with event-driven reactive patterns."""
        # Reactive workflows respond to system events
        # This is a placeholder for future reactive workflow implementation
        await self._execute_sequential_workflow(execution)

    async def _execute_step_with_tracking(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> bool:
        """Execute a step with full tracking and error handling."""
        step_start_time = datetime.utcnow()

        try:
            success = await self._execute_workflow_step(step, execution)

            # Record execution time
            execution_time = (
                datetime.utcnow() - step_start_time
            ).total_seconds() / 60.0
            execution.step_execution_times[step.step_id] = execution_time

            return success

        except Exception as e:
            logger.error(f"Step execution failed: {step.name} - {e}")
            step.error_message = str(e)
            return False

    async def _execute_workflow_step(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> bool:
        """Execute a single workflow step."""
        # Find best agent for step
        if not step.assigned_agent:
            agent = await self._assign_agent_to_step(step, execution)
            if not agent:
                logger.error(f"No suitable agent found for step: {step.name}")
                return False
            step.assigned_agent = agent.name

        # Create task definition
        if not step.task_definition:
            step.task_definition = TaskDefinition(
                title=step.name,
                description=step.description,
                priority=execution.workflow_definition.priority,
                estimated_duration_minutes=step.estimated_duration_minutes,
                preferred_agents=[step.assigned_agent] if step.assigned_agent else [],
            )

        # Execute task through task coordinator
        step.status = TaskStatus.IN_PROGRESS
        step.started_at = datetime.utcnow()

        # Assign and execute task
        task_assigned = await self.task_coordinator.assign_task(
            step.task_definition.task_id, step.assigned_agent
        )

        if not task_assigned:
            logger.error(f"Failed to assign task for step: {step.name}")
            return False

        # Start task
        task_started = await self.task_coordinator.start_task(
            step.task_definition.task_id, step.assigned_agent
        )

        if not task_started:
            logger.error(f"Failed to start task for step: {step.name}")
            return False

        # Monitor task completion (simplified - in real implementation would use callbacks)
        # For now, simulate task completion
        await asyncio.sleep(1)  # Simulate work

        # Complete task
        task_completed = await self.task_coordinator.complete_task(
            step.task_definition.task_id,
            step.assigned_agent,
            result_data={"step_completed": True, "step_name": step.name},
        )

        return task_completed

    async def _assign_agent_to_step(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> AgentProfile | None:
        """Assign the best available agent to a workflow step."""
        # Check preferred agents first
        for agent_name in step.preferred_agents:
            agent = self.agent_registry.get_agent(agent_name)
            if agent and agent.status.status == "available":
                # Check if agent has required capabilities
                agent_capabilities = {cap.name for cap in agent.capabilities}
                if all(
                    req_cap in agent_capabilities
                    for req_cap in step.required_capabilities
                ):
                    return agent

        # Find agents with required capabilities
        suitable_agents = []
        for capability in step.required_capabilities:
            agents_with_capability = self.agent_registry.get_agents_by_capability(
                capability
            )
            suitable_agents.extend(agents_with_capability)

        # Remove duplicates and filter available agents
        unique_agents = list({agent.name: agent for agent in suitable_agents}.values())
        available_agents = [
            agent for agent in unique_agents if agent.status.status == "available"
        ]

        if available_agents:
            # Return agent with highest reliability score
            return max(available_agents, key=lambda a: a.metrics.reliability_score)

        return None

    async def _check_step_dependencies(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> bool:
        """Check if step dependencies are satisfied."""
        for dep_id in step.depends_on:
            if dep_id not in execution.completed_step_ids:
                return False
        return True

    async def _evaluate_step_conditions(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> bool:
        """Evaluate step conditions for conditional workflows."""
        if not step.conditions:
            return True

        # Simple condition evaluation (can be extended)
        for condition_key, condition_value in step.conditions.items():
            if condition_key == "previous_step_success":
                if condition_value and execution.failed_step_ids:
                    return False
            elif condition_key == "agent_available":
                agent = self.agent_registry.get_agent(condition_value)
                if not agent or agent.status.status != "available":
                    return False

        return True

    async def _complete_workflow(self, execution: WorkflowExecution):
        """Complete workflow execution."""
        workflow = execution.workflow_definition

        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.utcnow()

        # Calculate success metrics
        total_steps = len(workflow.steps)
        completed_steps = len(execution.completed_step_ids)
        workflow.success_rate = (
            (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        )
        workflow.overall_progress = 100.0

        # Log completion
        await self._log_workflow_event(
            workflow,
            "workflow_completed",
            {
                "execution_id": str(execution.execution_id),
                "success_rate": workflow.success_rate,
                "total_execution_time": (
                    workflow.completed_at - workflow.started_at
                ).total_seconds()
                / 60.0,
            },
        )

        # Remove from active workflows
        if execution.execution_id in self.active_workflows:
            del self.active_workflows[execution.execution_id]

        logger.info(
            f"Workflow completed: {workflow.name} (Success rate: {workflow.success_rate:.1f}%)"
        )

    async def _fail_workflow(self, execution: WorkflowExecution, error_message: str):
        """Handle workflow failure."""
        workflow = execution.workflow_definition

        workflow.status = WorkflowStatus.FAILED
        workflow.completed_at = datetime.utcnow()

        # Log failure
        await self._log_workflow_event(
            workflow,
            "workflow_failed",
            {
                "execution_id": str(execution.execution_id),
                "error_message": error_message,
                "failed_steps": len(execution.failed_step_ids),
            },
        )

        # Remove from active workflows
        if execution.execution_id in self.active_workflows:
            del self.active_workflows[execution.execution_id]

        logger.error(f"Workflow failed: {workflow.name} - {error_message}")

    async def _log_workflow_event(
        self, workflow: WorkflowDefinition, event_type: str, metadata: dict
    ):
        """Log workflow events to database."""
        try:
            async with get_async_session() as session:
                activity = AgentActivity(
                    agent_name="@workflow-engine",
                    activity_type=ActivityType.WORKFLOW_EVENT,
                    description=f"{event_type}: {workflow.name}",
                    metadata=metadata,
                )
                session.add(activity)
                await session.commit()

        except Exception as e:
            logger.error(f"Error logging workflow event: {e}")

    async def _load_active_workflows(self):
        """Load active workflows from database."""
        try:
            async with get_async_session() as session:
                # Query for active workflows
                query = select(AgentWorkflow).where(
                    AgentWorkflow.status.in_(
                        [WorkflowStatus.IN_PROGRESS, WorkflowStatus.PENDING]
                    )
                )
                result = await session.execute(query)
                active_db_workflows = result.scalars().all()

                logger.info(
                    f"Loaded {len(active_db_workflows)} active workflows from database"
                )

        except Exception as e:
            logger.warning(f"Could not load active workflows from database: {e}")

    def get_workflow_status(self, workflow_id: UUID) -> dict | None:
        """Get workflow execution status."""
        if workflow_id not in self.workflow_definitions:
            return None

        workflow = self.workflow_definitions[workflow_id]
        execution = None

        # Find active execution
        for _exec_id, exec_obj in self.active_workflows.items():
            if exec_obj.workflow_definition.workflow_id == workflow_id:
                execution = exec_obj
                break

        status = {
            "workflow_id": str(workflow_id),
            "name": workflow.name,
            "status": workflow.status.value,
            "overall_progress": workflow.overall_progress,
            "total_steps": len(workflow.steps),
            "completed_steps": len(execution.completed_step_ids) if execution else 0,
            "failed_steps": len(execution.failed_step_ids) if execution else 0,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat()
            if workflow.started_at
            else None,
            "completed_at": workflow.completed_at.isoformat()
            if workflow.completed_at
            else None,
        }

        if execution:
            status["execution_id"] = str(execution.execution_id)
            status["current_steps"] = len(execution.current_step_ids)
            status["step_execution_times"] = {
                str(step_id): time_minutes
                for step_id, time_minutes in execution.step_execution_times.items()
            }

        return status

    def get_engine_statistics(self) -> dict:
        """Get workflow engine statistics."""
        total_workflows = len(self.workflow_definitions)
        active_workflows = len(self.active_workflows)
        completed_workflows = len(
            [
                w
                for w in self.workflow_definitions.values()
                if w.status == WorkflowStatus.COMPLETED
            ]
        )
        failed_workflows = len(
            [
                w
                for w in self.workflow_definitions.values()
                if w.status == WorkflowStatus.FAILED
            ]
        )

        return {
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "success_rate": (completed_workflows / max(total_workflows, 1)) * 100,
            "workflow_templates": len(self.workflow_templates),
            "last_updated": datetime.utcnow().isoformat(),
        }


# Global workflow engine instance
workflow_engine = None


async def get_workflow_engine() -> WorkflowEngine:
    """Get the global workflow engine instance."""
    global workflow_engine
    if workflow_engine is None:
        from .agent_registry import agent_registry
        from .task_coordinator import get_task_coordinator

        await agent_registry.initialize()
        task_coordinator = await get_task_coordinator()

        workflow_engine = WorkflowEngine(agent_registry, task_coordinator)
        await workflow_engine.initialize()

        logger.info("Workflow engine initialized")
    return workflow_engine
