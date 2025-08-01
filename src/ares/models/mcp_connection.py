"""MCP connection model for ARES."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class MCPConnection(Base, TimestampMixin):
    """MCP connection model for tracking agent-MCP server connections."""

    __tablename__ = "mcp_connections"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    mcp_server_name: Mapped[str] = mapped_column(String(255), nullable=False)
    connection_status: Mapped[str] = mapped_column(String(50), default="disconnected")
    last_ping: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    connection_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationship to agent
    agent = relationship("Agent", back_populates="mcp_connections")

    def __repr__(self) -> str:
        return (
            f"<MCPConnection(id={self.id}, agent_id={self.agent_id}, "
            f"server='{self.mcp_server_name}', status='{self.connection_status}')>"
        )
