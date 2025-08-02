"""Documentation Agent database models for ARES."""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class DocumentationType(str, Enum):
    """Types of documentation that can be generated."""

    API = "api"
    ARCHITECTURE = "architecture"
    USER_GUIDE = "user_guide"
    TECHNICAL_SPEC = "technical_spec"
    CODE_DOCUMENTATION = "code_documentation"


class DocumentationFormat(str, Enum):
    """Output formats for documentation."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    CONFLUENCE = "confluence"


class DocumentationTaskStatus(str, Enum):
    """Status of documentation generation tasks."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QualityScore(str, Enum):
    """Quality assessment scores."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class DocumentationTask(Base, TimestampMixin):
    """Documentation generation task tracking."""

    __tablename__ = "documentation_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)

    documentation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_paths: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    output_format: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[str] = mapped_column(
        String(50), default=DocumentationTaskStatus.PENDING.value
    )
    priority: Mapped[int] = mapped_column(Integer, default=3)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    generation_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="documentation_tasks")
    task = relationship("Task", back_populates="documentation_task")
    artifacts = relationship(
        "DocumentationArtifact", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DocumentationTask(id={self.id}, type={self.documentation_type}, title='{self.title}', status={self.status})>"


class DocumentationArtifact(Base, TimestampMixin):
    """Generated documentation artifacts and outputs."""

    __tablename__ = "documentation_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("documentation_tasks.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    format: Mapped[str] = mapped_column(String(50), nullable=False)

    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    version: Mapped[str] = mapped_column(String(20), default="1.0")
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)

    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    artifact_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    task = relationship("DocumentationTask", back_populates="artifacts")

    def __repr__(self):
        return f"<DocumentationArtifact(id={self.id}, name='{self.name}', version='{self.version}')>"


class QualityAssessment(Base, TimestampMixin):
    """Quality assessment results for documentation tasks."""

    __tablename__ = "quality_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("documentation_tasks.id"), nullable=False
    )
    artifact_id: Mapped[int | None] = mapped_column(
        ForeignKey("documentation_artifacts.id"), nullable=True
    )

    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    assessor_id: Mapped[int | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True
    )

    overall_score: Mapped[str] = mapped_column(String(50), nullable=False)
    completeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    clarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    usefulness_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    issues_found: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    strengths: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    requires_revision: Mapped[bool] = mapped_column(Boolean, default=False)

    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("DocumentationTask")
    artifact = relationship("DocumentationArtifact")
    assessor = relationship("Agent")

    def __repr__(self):
        return f"<QualityAssessment(id={self.id}, task_id={self.task_id}, overall_score={self.overall_score}, passed={self.passed})>"


class DocumentationTemplate(Base, TimestampMixin):
    """Reusable documentation templates."""

    __tablename__ = "documentation_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    documentation_type: Mapped[str] = mapped_column(String(50), nullable=False)

    template_content: Mapped[str] = mapped_column(Text, nullable=False)
    default_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    required_inputs: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    version: Mapped[str] = mapped_column(String(20), default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True
    )

    # Relationships
    creator = relationship("Agent")

    def __repr__(self):
        return f"<DocumentationTemplate(id={self.id}, name='{self.name}', type={self.documentation_type}, version='{self.version}')>"

    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
