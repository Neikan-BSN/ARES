"""Reliability metric model for ARES."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ReliabilityMetric(Base):
    """Reliability metric model for tracking agent performance."""

    __tablename__ = "reliability_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(nullable=False)
    metric_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship to agent
    agent = relationship("Agent", back_populates="reliability_metrics")

    def __repr__(self) -> str:
        return (
            f"<ReliabilityMetric(id={self.id}, agent_id={self.agent_id}, "
            f"type='{self.metric_type}', value={self.metric_value})>"
        )

