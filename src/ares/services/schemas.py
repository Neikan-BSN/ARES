"""Service schemas for ARES."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ..coordination.task_coordinator import TaskPriority


class AgentCapability(str, Enum):
    """Agent capabilities enumeration."""

    PLANNING = "planning"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    MONITORING = "monitoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY = "security"


class CoordinationRequest(BaseModel):
    """Request for agent coordination."""

    request_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Request title")
    description: str = Field(..., description="Request description")
    coordination_type: str = Field(default="task", description="Type of coordination")
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority"
    )
    required_capabilities: list[str] = Field(
        default_factory=list, description="Required capabilities"
    )
    preferred_agents: list[str] = Field(
        default_factory=list, description="Preferred agents"
    )
    timeout_minutes: int = Field(
        default=60, ge=1, le=480, description="Timeout in minutes"
    )
    max_retries: int = Field(default=2, ge=0, le=10, description="Maximum retries")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    workflow_id: str | None = Field(default=None, description="Existing workflow ID")
    custom_workflow: dict[str, Any] | None = Field(
        default=None, description="Custom workflow definition"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Request creation time"
    )
    estimated_duration_minutes: int | None = Field(
        default=None, ge=1, description="Estimated duration in minutes"
    )


class CoordinationResponse(BaseModel):
    """Response for agent coordination."""

    request_id: UUID = Field(..., description="Request ID")
    coordination_id: UUID | None = Field(
        default_factory=uuid4, description="Coordination ID"
    )
    status: str = Field(default="accepted", description="Response status")
    assigned_agents: list[str] = Field(
        default_factory=list, description="Assigned agents"
    )
    task_ids: list[UUID] = Field(default_factory=list, description="Created task IDs")
    workflow_id: str | None = Field(default=None, description="Workflow ID")
    execution_id: str | None = Field(default=None, description="Execution ID")
    estimated_completion_time: datetime | None = Field(
        default=None, description="Estimated completion"
    )
    confidence_score: float = Field(
        default=80.0, ge=0.0, le=100.0, description="Confidence score"
    )
    coordination_plan: dict[str, Any] = Field(
        default_factory=dict, description="Coordination plan"
    )
    response_time: datetime = Field(
        default_factory=datetime.utcnow, description="Response time"
    )


class AgentMetric(BaseModel):
    """Agent performance metrics."""

    agent_id: str
    tasks_completed: int
    tasks_failed: int
    success_rate: float
    average_completion_time_minutes: float
    load_factor: float  # 0.0 to 1.0
