"""Project tracking models for ARES."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Numeric, String, Table, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

# Association table for workflow-milestone many-to-many relationship
workflow_milestone_association = Table(
    "workflow_milestone_association",
    Base.metadata,
    Column(
        "workflow_id",
        PGUUID(as_uuid=True),
        ForeignKey("agent_workflows.id"),
        primary_key=True,
    ),
    Column(
        "milestone_id",
        PGUUID(as_uuid=True),
        ForeignKey("project_milestones.id"),
        primary_key=True,
    ),
)


class ComponentType(Enum):
    """System component types."""

    API = "api"
    DATABASE = "database"
    FRONTEND = "frontend"
    BACKEND = "backend"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    MONITORING = "monitoring"


class DebtPriority(Enum):
    """Technical debt priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DebtStatus(Enum):
    """Technical debt status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class IntegrationStatus(Enum):
    """Integration checkpoint status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    FAILED = "failed"


class ActivityType(Enum):
    """Types of agent activities."""

    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    COORDINATION_EVENT = "coordination_event"
    SYSTEM_EVENT = "system_event"
    ERROR_EVENT = "error_event"
    PERFORMANCE_EVENT = "performance_event"


class WorkflowStatus(Enum):
    """Status of workflow executions."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class AgentActivity(Base, TimestampMixin):
    """Model for tracking agent activities."""

    __tablename__ = "agent_activities"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_type: Mapped[ActivityType] = mapped_column(
        SQLEnum(ActivityType), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # Performance metrics
    duration_seconds: Mapped[float | None] = mapped_column(nullable=True)
    success: Mapped[bool | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<AgentActivity(id={self.id}, agent='{self.agent_name}', type='{self.activity_type}')>"


class AgentWorkflow(Base, TimestampMixin):
    """Model for tracking agent workflows."""

    __tablename__ = "agent_workflows"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_agent: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(WorkflowStatus), default=WorkflowStatus.PENDING
    )
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    estimated_duration_hours: Mapped[int | None] = mapped_column(nullable=True)
    progress_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00")
    )

    # Relationships
    associated_milestones: Mapped[list["ProjectMilestone"]] = relationship(
        "ProjectMilestone",
        secondary="workflow_milestone_association",
        back_populates="workflows",
    )

    def __repr__(self) -> str:
        return f"<AgentWorkflow(id={self.id}, name='{self.workflow_name}', status='{self.status}')>"


class ProjectMilestone(Base, TimestampMixin):
    """Model for tracking project milestones."""

    __tablename__ = "project_milestones"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    component: Mapped[ComponentType] = mapped_column(
        SQLEnum(ComponentType), nullable=False
    )
    target_completion_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Progress tracking
    completion_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00")
    )

    # Relationships
    workflows: Mapped[list["AgentWorkflow"]] = relationship(
        "AgentWorkflow",
        secondary="workflow_milestone_association",
        back_populates="associated_milestones",
    )

    def __repr__(self) -> str:
        return f"<ProjectMilestone(id={self.id}, title='{self.title}', component='{self.component}')>"


class TechnicalDebtItem(Base, TimestampMixin):
    """Model for tracking technical debt items."""

    __tablename__ = "technical_debt_items"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[DebtPriority] = mapped_column(
        SQLEnum(DebtPriority), nullable=False
    )
    component: Mapped[str] = mapped_column(String(100), nullable=False)
    estimated_effort: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_agent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[DebtStatus] = mapped_column(
        SQLEnum(DebtStatus), default=DebtStatus.PENDING
    )

    def __repr__(self) -> str:
        return f"<TechnicalDebtItem(id={self.id}, title='{self.title}', priority='{self.priority}')>"


class IntegrationCheckpoint(Base, TimestampMixin):
    """Model for tracking integration checkpoints."""

    __tablename__ = "integration_checkpoints"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    checkpoint_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    component: Mapped[str] = mapped_column(String(100), nullable=False)
    dependency_components: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    verification_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IntegrationStatus] = mapped_column(
        SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING
    )
    last_verified: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<IntegrationCheckpoint(id={self.id}, name='{self.checkpoint_name}', status='{self.status}')>"
