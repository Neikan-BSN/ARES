"""Agent model for ARES."""

from typing import Optional

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Agent(Base, TimestampMixin):
    """Agent model for storing agent information."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="inactive")
    configuration: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    capabilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    reliability_metrics = relationship("ReliabilityMetric", back_populates="agent")
    enforcement_actions = relationship("EnforcementAction", back_populates="agent")
    mcp_connections = relationship("MCPConnection", back_populates="agent")

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}')>"
