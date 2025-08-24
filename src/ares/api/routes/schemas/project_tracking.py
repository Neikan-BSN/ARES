"""Pydantic schemas for project tracking API endpoints."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ....models.project_tracking import (
    ActivityType,
    ComponentType,
    DebtPriority,
    DebtStatus,
    IntegrationStatus,
    WorkflowStatus,
)

# ==============================================================================
# PROJECT MILESTONE SCHEMAS
# ==============================================================================


class ProjectMilestoneBase(BaseModel):
    """Base project milestone schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Milestone title")
    description: str | None = Field(None, description="Detailed milestone description")
    component: ComponentType = Field(
        ..., description="System component this milestone belongs to"
    )
    target_completion_date: datetime | None = Field(
        None, description="Target completion date"
    )
    completion_percentage: Decimal = Field(
        default=Decimal("0.00"), ge=0, le=100, description="Completion percentage"
    )


class ProjectMilestoneCreate(ProjectMilestoneBase):
    """Schema for creating a new project milestone."""

    pass


class ProjectMilestoneResponse(ProjectMilestoneBase):
    """Schema for project milestone responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique milestone identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# ==============================================================================
# AGENT WORKFLOW SCHEMAS
# ==============================================================================


class AgentWorkflowBase(BaseModel):
    """Base agent workflow schema."""

    workflow_name: str = Field(
        ..., min_length=1, max_length=255, description="Workflow name"
    )
    description: str | None = Field(None, description="Workflow description")
    assigned_agent: str = Field(
        ..., min_length=1, max_length=100, description="Assigned agent name"
    )
    status: WorkflowStatus = Field(
        default=WorkflowStatus.PENDING, description="Workflow status"
    )
    priority: str = Field(default="medium", description="Workflow priority")
    estimated_duration_hours: int | None = Field(
        None, ge=0, description="Estimated duration in hours"
    )
    progress_percentage: Decimal = Field(
        default=Decimal("0.00"), ge=0, le=100, description="Progress percentage"
    )


class AgentWorkflowCreate(AgentWorkflowBase):
    """Schema for creating a new agent workflow."""

    milestone_ids: list[UUID] | None = Field(
        default=None, description="Associated milestone IDs"
    )


class AgentWorkflowResponse(AgentWorkflowBase):
    """Schema for agent workflow responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique workflow identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    associated_milestones: list[ProjectMilestoneResponse] | None = Field(
        default=None, description="Associated project milestones"
    )


# ==============================================================================
# TECHNICAL DEBT SCHEMAS
# ==============================================================================


class TechnicalDebtBase(BaseModel):
    """Base technical debt schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Debt item title")
    description: str = Field(
        ..., min_length=1, description="Detailed description of the technical debt"
    )
    priority: DebtPriority = Field(..., description="Priority level of the debt item")
    component: str = Field(
        ..., min_length=1, max_length=100, description="Affected component or module"
    )
    estimated_effort: str = Field(
        ..., min_length=1, max_length=50, description="Estimated effort to resolve"
    )
    assigned_agent: str | None = Field(
        None, max_length=100, description="Agent assigned to resolve this debt"
    )
    status: DebtStatus = Field(
        default=DebtStatus.PENDING, description="Current status of the debt item"
    )


class TechnicalDebtCreate(TechnicalDebtBase):
    """Schema for creating a new technical debt item."""

    pass


class TechnicalDebtResponse(TechnicalDebtBase):
    """Schema for technical debt responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique debt item identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# ==============================================================================
# INTEGRATION CHECKPOINT SCHEMAS
# ==============================================================================


class IntegrationCheckpointBase(BaseModel):
    """Base integration checkpoint schema."""

    checkpoint_name: str = Field(
        ..., min_length=1, max_length=255, description="Checkpoint name"
    )
    description: str = Field(
        ..., min_length=1, description="Detailed checkpoint description"
    )
    component: str = Field(
        ..., min_length=1, max_length=100, description="System component being verified"
    )
    dependency_components: list[str] | None = Field(
        default=None, description="Dependent components"
    )
    verification_criteria: str = Field(
        ..., min_length=1, description="Criteria for successful verification"
    )
    status: IntegrationStatus = Field(
        default=IntegrationStatus.PENDING, description="Checkpoint status"
    )


class IntegrationCheckpointCreate(IntegrationCheckpointBase):
    """Schema for creating a new integration checkpoint."""

    pass


class IntegrationCheckpointResponse(IntegrationCheckpointBase):
    """Schema for integration checkpoint responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique checkpoint identifier")
    last_verified: datetime | None = Field(
        None, description="Last verification timestamp"
    )
    verification_notes: str | None = Field(
        None, description="Notes from last verification"
    )
    created_at: datetime = Field(..., description="Creation timestamp")


# ==============================================================================
# AGENT ACTIVITY SCHEMAS
# ==============================================================================


class AgentActivityBase(BaseModel):
    """Base agent activity schema."""

    agent_name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the agent"
    )
    activity_type: ActivityType = Field(..., description="Type of activity performed")
    description: str = Field(
        ..., min_length=1, description="Description of the activity"
    )
    metadata: dict | None = Field(
        default=None, description="Additional activity metadata"
    )


class AgentActivityCreate(AgentActivityBase):
    """Schema for creating a new agent activity log."""

    pass


class AgentActivityResponse(AgentActivityBase):
    """Schema for agent activity responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique activity identifier")
    timestamp: datetime = Field(..., description="Activity timestamp")


# ==============================================================================
# PROJECT OVERVIEW SCHEMAS
# ==============================================================================


class ProjectOverviewResponse(BaseModel):
    """Schema for comprehensive project overview."""

    # Milestone statistics
    total_milestones: int = Field(..., description="Total number of project milestones")
    completed_milestones: int = Field(..., description="Number of completed milestones")
    average_completion: float = Field(
        ..., description="Average completion percentage across all milestones"
    )

    # Workflow statistics
    active_workflows: int = Field(..., description="Number of active workflows")
    total_workflows: int = Field(..., description="Total number of workflows")

    # Technical debt statistics
    critical_debt_items: int = Field(
        ..., description="Number of critical priority debt items"
    )
    total_debt_items: int = Field(..., description="Total number of debt items")

    # Integration statistics
    verified_checkpoints: int = Field(
        ..., description="Number of verified integration checkpoints"
    )
    total_checkpoints: int = Field(
        ..., description="Total number of integration checkpoints"
    )

    # Overall health metrics
    health_score: float = Field(
        ..., ge=0, le=100, description="Overall project health score (0-100)"
    )
    last_updated: datetime = Field(..., description="Last update timestamp")


# ==============================================================================
# WEBSOCKET MESSAGE SCHEMAS
# ==============================================================================


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""

    type: str = Field(..., description="Message type")
    data: dict = Field(..., description="Message data")
    timestamp: str = Field(..., description="Message timestamp")


# ==============================================================================
# BULK OPERATION SCHEMAS
# ==============================================================================


class BulkMilestoneUpdate(BaseModel):
    """Schema for bulk milestone updates."""

    milestone_ids: list[UUID] = Field(
        ..., description="List of milestone IDs to update"
    )
    completion_percentage: float | None = Field(
        None, ge=0, le=100, description="New completion percentage"
    )
    target_completion_date: datetime | None = Field(
        None, description="New target completion date"
    )


class BulkWorkflowUpdate(BaseModel):
    """Schema for bulk workflow updates."""

    workflow_ids: list[UUID] = Field(..., description="List of workflow IDs to update")
    status: WorkflowStatus | None = Field(None, description="New workflow status")
    assigned_agent: str | None = Field(
        None, max_length=100, description="New assigned agent"
    )


class BulkDebtUpdate(BaseModel):
    """Schema for bulk technical debt updates."""

    debt_ids: list[UUID] = Field(..., description="List of debt item IDs to update")
    status: DebtStatus | None = Field(None, description="New debt status")
    assigned_agent: str | None = Field(
        None, max_length=100, description="New assigned agent"
    )


# ==============================================================================
# SEARCH AND FILTER SCHEMAS
# ==============================================================================


class ProjectSearchFilters(BaseModel):
    """Schema for project search and filtering."""

    component: ComponentType | None = Field(None, description="Filter by component")
    status: str | None = Field(None, description="Filter by status")
    assigned_agent: str | None = Field(None, description="Filter by assigned agent")
    priority: str | None = Field(None, description="Filter by priority")
    date_from: datetime | None = Field(None, description="Filter from date")
    date_to: datetime | None = Field(None, description="Filter to date")
    search_query: str | None = Field(
        None, min_length=1, description="Text search query"
    )


class ProjectSearchResponse(BaseModel):
    """Schema for project search results."""

    milestones: list[ProjectMilestoneResponse] = Field(
        default=[], description="Matching milestones"
    )
    workflows: list[AgentWorkflowResponse] = Field(
        default=[], description="Matching workflows"
    )
    debt_items: list[TechnicalDebtResponse] = Field(
        default=[], description="Matching debt items"
    )
    checkpoints: list[IntegrationCheckpointResponse] = Field(
        default=[], description="Matching checkpoints"
    )
    total_results: int = Field(
        ..., description="Total number of results across all categories"
    )


# ==============================================================================
# ANALYTICS AND REPORTING SCHEMAS
# ==============================================================================


class ProjectAnalytics(BaseModel):
    """Schema for project analytics data."""

    # Trend data
    completion_trend: list[dict] = Field(
        ..., description="Completion percentage trend over time"
    )
    workflow_activity_trend: list[dict] = Field(
        ..., description="Workflow activity trend"
    )
    debt_resolution_trend: list[dict] = Field(
        ..., description="Technical debt resolution trend"
    )

    # Performance metrics
    average_completion_time: float | None = Field(
        None, description="Average milestone completion time in days"
    )
    workflow_success_rate: float = Field(
        ..., ge=0, le=100, description="Workflow success rate percentage"
    )
    debt_resolution_rate: float = Field(
        ..., ge=0, le=100, description="Debt resolution rate percentage"
    )

    # Agent performance
    top_performing_agents: list[dict] = Field(
        ..., description="Top performing agents by activity"
    )
    agent_workload_distribution: list[dict] = Field(
        ..., description="Workload distribution across agents"
    )

    # System health indicators
    integration_stability_score: float = Field(
        ..., ge=0, le=100, description="Integration stability score"
    )
    code_quality_trend: list[dict] = Field(
        ..., description="Code quality metrics over time"
    )

    # Generated metadata
    report_generated_at: datetime = Field(
        ..., description="Report generation timestamp"
    )
    analysis_period_days: int = Field(..., description="Analysis period in days")


class TimeSeriesData(BaseModel):
    """Schema for time series data points."""

    timestamp: datetime = Field(..., description="Data point timestamp")
    value: float = Field(..., description="Data point value")
    metadata: dict | None = Field(
        default=None, description="Additional metadata for the data point"
    )


class AgentPerformanceMetrics(BaseModel):
    """Schema for agent performance metrics."""

    agent_name: str = Field(..., description="Agent name")
    total_activities: int = Field(..., description="Total number of activities")
    completed_workflows: int = Field(..., description="Number of completed workflows")
    success_rate: float = Field(
        ..., ge=0, le=100, description="Success rate percentage"
    )
    average_completion_time: float | None = Field(
        None, description="Average completion time in hours"
    )
    reliability_score: float = Field(
        ..., ge=0, le=100, description="Overall reliability score"
    )
    last_activity: datetime = Field(..., description="Timestamp of last activity")
