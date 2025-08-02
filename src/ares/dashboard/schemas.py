"""Pydantic schemas for ARES dashboard data models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SystemHealth(str, Enum):
    """System health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"


class AgentStatusType(str, Enum):
    """Agent status types."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class VerificationActivityType(str, Enum):
    """Types of verification activities."""

    TASK_COMPLETION = "task_completion"
    TOOL_VALIDATION = "tool_validation"
    PROOF_OF_WORK = "proof_of_work"
    BEHAVIOR_MONITORING = "behavior_monitoring"
    ROLLBACK_OPERATION = "rollback_operation"


class VerificationStatus(str, Enum):
    """Verification activity status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


class DashboardStats(BaseModel):
    """Overall dashboard statistics."""

    total_agents: int = Field(..., description="Total number of agents in system")
    active_agents: int = Field(..., description="Number of currently active agents")
    total_verifications_today: int = Field(
        ..., description="Total verifications performed today"
    )
    successful_verifications: int = Field(
        ..., description="Successful verifications today"
    )
    failed_verifications: int = Field(..., description="Failed verifications today")
    pending_verifications: int = Field(
        ..., description="Currently pending verifications"
    )
    average_quality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Average quality score across all verifications",
    )
    system_health: SystemHealth = Field(..., description="Overall system health status")
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    last_updated: datetime = Field(..., description="When stats were last updated")

    class Config:
        json_schema_extra = {
            "example": {
                "total_agents": 25,
                "active_agents": 18,
                "total_verifications_today": 342,
                "successful_verifications": 298,
                "failed_verifications": 31,
                "pending_verifications": 13,
                "average_quality_score": 0.84,
                "system_health": "healthy",
                "uptime_seconds": 86400,
                "last_updated": "2024-01-15T10:30:00Z",
            }
        }


class AgentStatus(BaseModel):
    """Status and metrics for individual agent."""

    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    status: AgentStatusType = Field(..., description="Current agent status")
    last_seen: datetime = Field(..., description="Last activity timestamp")
    current_task: str | None = Field(
        default=None, description="Currently executing task ID"
    )
    reliability_score: float = Field(
        ..., ge=0.0, le=1.0, description="Agent reliability score (0-1)"
    )
    total_tasks_completed: int = Field(
        ..., description="Total tasks completed by agent"
    )
    success_rate: float = Field(
        ..., ge=0.0, le=1.0, description="Task success rate (0-1)"
    )
    average_quality_score: float = Field(
        ..., ge=0.0, le=1.0, description="Average quality score for agent's work (0-1)"
    )
    recent_activities: list[str] | None = Field(
        default=None, description="List of recent activities"
    )
    performance_metrics: dict[str, Any] | None = Field(
        default=None, description="Additional performance metrics"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_001",
                "name": "Development Agent Alpha",
                "status": "active",
                "last_seen": "2024-01-15T10:30:00Z",
                "current_task": "task_456",
                "reliability_score": 0.89,
                "total_tasks_completed": 156,
                "success_rate": 0.91,
                "average_quality_score": 0.84,
                "recent_activities": [
                    "Completed API implementation",
                    "Validated 5 tool calls",
                    "Generated documentation",
                ],
            }
        }


class VerificationActivity(BaseModel):
    """Individual verification activity record."""

    id: str = Field(..., description="Unique verification ID")
    type: VerificationActivityType = Field(..., description="Type of verification")
    agent_id: str = Field(..., description="Agent that performed the work")
    task_id: str | None = Field(default=None, description="Associated task ID")
    status: VerificationStatus = Field(..., description="Verification status")
    quality_score: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Quality score if applicable"
    )
    timestamp: datetime = Field(..., description="When verification was performed")
    duration_ms: int | None = Field(
        default=None, description="Verification duration in ms"
    )
    details: dict[str, Any] | None = Field(
        default=None, description="Additional verification details"
    )
    error_message: str | None = Field(
        default=None, description="Error message if verification failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "verify_789",
                "type": "task_completion",
                "agent_id": "agent_001",
                "task_id": "task_456",
                "status": "completed",
                "quality_score": 0.87,
                "timestamp": "2024-01-15T10:30:00Z",
                "duration_ms": 1250,
            }
        }


class RealtimeUpdate(BaseModel):
    """Real-time update message for WebSocket clients."""

    type: str = Field(..., description="Type of update message")
    data: dict[str, Any] = Field(..., description="Update data payload")
    timestamp: datetime = Field(..., description="When update was generated")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "agent_status_update",
                "data": {
                    "agent_id": "agent_001",
                    "status": "active",
                    "current_task": "task_789",
                },
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class QualityTrend(BaseModel):
    """Quality trend data point."""

    date: datetime = Field(..., description="Date of the data point")
    average_quality_score: float = Field(
        ..., ge=0.0, le=1.0, description="Average quality score for the period"
    )
    verification_count: int = Field(
        ..., description="Number of verifications in period"
    )
    success_rate: float = Field(
        ..., ge=0.0, le=1.0, description="Success rate for the period"
    )
    agent_count: int = Field(..., description="Number of active agents in period")


class PerformanceMetrics(BaseModel):
    """Performance metrics for dashboard display."""

    average_response_time_ms: float = Field(..., description="Average response time")
    peak_response_time_ms: float = Field(..., description="Peak response time")
    throughput_per_minute: float = Field(..., description="Verifications per minute")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate (0-1)")
    cpu_usage_percent: float = Field(
        ..., ge=0.0, le=100.0, description="CPU usage percentage"
    )
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    active_connections: int = Field(..., description="Number of active connections")


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemAlert(BaseModel):
    """System alert for dashboard notifications."""

    id: str = Field(..., description="Unique alert identifier")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    source: str = Field(..., description="Source component that generated alert")
    timestamp: datetime = Field(..., description="When alert was generated")
    acknowledged: bool = Field(
        default=False, description="Whether alert has been acknowledged"
    )
    resolved: bool = Field(default=False, description="Whether alert has been resolved")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional alert metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert_001",
                "severity": "warning",
                "title": "High Error Rate",
                "message": "Agent agent_005 has error rate above 10% in last hour",
                "source": "agent_monitor",
                "timestamp": "2024-01-15T10:30:00Z",
                "acknowledged": False,
                "resolved": False,
            }
        }


class DashboardConfig(BaseModel):
    """Dashboard configuration settings."""

    refresh_interval_seconds: int = Field(
        default=30, description="Auto-refresh interval"
    )
    max_activity_records: int = Field(
        default=100, description="Max activity records to display"
    )
    alert_retention_hours: int = Field(
        default=24, description="How long to keep alerts"
    )
    enable_real_time_updates: bool = Field(
        default=True, description="Enable WebSocket updates"
    )
    quality_threshold_warning: float = Field(
        default=0.7, description="Quality score threshold for warnings"
    )
    quality_threshold_critical: float = Field(
        default=0.5, description="Quality score threshold for critical alerts"
    )
    performance_monitoring_enabled: bool = Field(
        default=True, description="Enable performance monitoring"
    )


class ChartData(BaseModel):
    """Data structure for dashboard charts."""

    labels: list[str] = Field(..., description="Chart labels (x-axis)")
    datasets: list[dict[str, Any]] = Field(..., description="Chart datasets")
    title: str = Field(..., description="Chart title")
    chart_type: str = Field(..., description="Chart type (line, bar, pie, etc.)")
    options: dict[str, Any] | None = Field(
        default=None, description="Chart configuration options"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "datasets": [
                    {
                        "label": "Quality Score",
                        "data": [0.85, 0.82, 0.88, 0.84, 0.89],
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    }
                ],
                "title": "Weekly Quality Trends",
                "chart_type": "line",
            }
        }


class AgentDetails(BaseModel):
    """Detailed agent information for agent-specific dashboard."""

    agent_status: AgentStatus = Field(..., description="Basic agent status")
    task_history: list[dict[str, Any]] = Field(..., description="Recent task history")
    quality_trends: list[QualityTrend] = Field(..., description="Quality trend data")
    performance_metrics: PerformanceMetrics = Field(
        ..., description="Performance metrics"
    )
    recent_verifications: list[VerificationActivity] = Field(
        ..., description="Recent verification activities"
    )
    alerts: list[SystemAlert] = Field(..., description="Agent-specific alerts")
    capabilities: list[str] = Field(..., description="Agent capabilities and tools")


class DashboardSummary(BaseModel):
    """Complete dashboard summary for main page."""

    stats: DashboardStats = Field(..., description="Overall statistics")
    top_performing_agents: list[AgentStatus] = Field(
        ..., description="Top performing agents"
    )
    recent_activities: list[VerificationActivity] = Field(
        ..., description="Recent activities"
    )
    system_alerts: list[SystemAlert] = Field(..., description="Active system alerts")
    quality_trends: list[QualityTrend] = Field(..., description="Quality trends")
    performance_metrics: PerformanceMetrics = Field(
        ..., description="System performance"
    )
    chart_data: dict[str, ChartData] = Field(
        ..., description="Chart data for visualization"
    )


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: str = Field(..., description="Message type")
    data: dict[str, Any] | None = Field(default=None, description="Message data")
    request_id: str | None = Field(default=None, description="Request identifier")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "subscribe_agent",
                "data": {"agent_id": "agent_001"},
                "request_id": "req_123",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
