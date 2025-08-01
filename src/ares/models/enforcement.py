"""Enforcement action model for ARES."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EnforcementAction(Base):
    """Enforcement action model for tracking agent interventions."""

    __tablename__ = "enforcement_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    action_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    result: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationship to agent
    agent = relationship("Agent", back_populates="enforcement_actions")

    def __repr__(self) -> str:
        return (
            f"<EnforcementAction(id={self.id}, agent_id={self.agent_id}, "
            f"type='{self.action_type}', result='{self.result}')>"
        )