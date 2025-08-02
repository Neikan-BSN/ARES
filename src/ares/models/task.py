"""Task model for ARES."""

from enum import Enum

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    """Task priority enumeration."""

    LOW = 1
    MEDIUM = 3
    HIGH = 5


class Task(Base, TimestampMixin):
    """Task model for storing task information."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=TaskStatus.PENDING.value)
    priority: Mapped[int] = mapped_column(Integer, default=TaskPriority.MEDIUM.value)
    requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    documentation_task = relationship(
        "DocumentationTask", back_populates="task", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
