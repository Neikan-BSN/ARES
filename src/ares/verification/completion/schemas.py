"""Pydantic schemas for task completion verification."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CompletionStatus(str, Enum):
    """Task completion verification status."""

    PENDING = "pending"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    INVALID = "invalid"
    ERROR = "error"


class TaskCompletionRequest(BaseModel):
    """Request model for task completion verification."""

    task_id: str = Field(..., description="Unique task identifier")
    agent_id: str = Field(..., description="Agent that completed the task")
    task_description: str = Field(
        ..., description="Original task description and requirements"
    )
    completion_evidence: dict[str, Any] = Field(
        ...,
        description="Evidence of task completion including outputs, tool calls, metrics",
    )
    completion_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was marked as completed",
    )
    additional_context: dict[str, Any] | None = Field(
        default=None, description="Additional context for verification"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123",
                "agent_id": "agent_456",
                "task_description": "Create a user authentication API endpoint",
                "completion_evidence": {
                    "outputs": {
                        "files_created": ["auth.py", "test_auth.py"],
                        "api_endpoints": ["/login", "/logout"],
                        "completeness_score": 0.95,
                        "accuracy_score": 0.88,
                        "format_compliance": True,
                    },
                    "tool_calls": [
                        {"tool_name": "write_file", "parameters": {"path": "auth.py"}},
                        {
                            "tool_name": "run_tests",
                            "parameters": {"test_path": "test_auth.py"},
                        },
                    ],
                    "performance_metrics": {
                        "execution_time_ms": 1200,
                        "memory_usage_mb": 45,
                        "error_rate": 0.02,
                    },
                },
                "completion_timestamp": "2024-01-15T10:30:00Z",
            }
        }


class VerificationEvidence(BaseModel):
    """Evidence collected during verification process."""

    evidence_type: str = Field(
        ..., description="Type of evidence (output_analysis, tool_usage, etc.)"
    )
    source: str = Field(..., description="Source of the evidence")
    data: dict[str, Any] = Field(..., description="Evidence data")
    timestamp: datetime = Field(..., description="When evidence was collected")
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in evidence reliability (0-1)",
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata about the evidence"
    )


class QualityMetrics(BaseModel):
    """Quality metrics calculated during verification."""

    overall_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall quality score (0-1)"
    )
    output_quality_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Quality of task outputs (0-1)"
    )
    requirements_match_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How well outputs match requirements (0-1)",
    )
    performance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Performance metrics score (0-1)"
    )
    security_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Security compliance score (0-1)"
    )
    evidence_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average confidence in collected evidence (0-1)",
    )
    verification_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness of verification process (0-1)",
    )


class TaskCompletionResult(BaseModel):
    """Result of task completion verification."""

    task_id: str = Field(..., description="Task identifier")
    agent_id: str = Field(..., description="Agent identifier")
    status: CompletionStatus = Field(..., description="Verification status")
    message: str = Field(..., description="Human-readable verification message")
    quality_metrics: QualityMetrics = Field(..., description="Quality metrics")
    evidence: list[VerificationEvidence] = Field(
        default_factory=list, description="Evidence collected during verification"
    )
    verification_timestamp: datetime = Field(
        ..., description="When verification was completed"
    )
    verification_details: dict[str, Any] | None = Field(
        default=None, description="Detailed verification results"
    )
    recommendations: list[str] | None = Field(
        default=None, description="Recommendations for improvement"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123",
                "agent_id": "agent_456",
                "status": "completed",
                "message": "Task completed successfully with all quality standards met.",
                "quality_metrics": {
                    "overall_score": 0.92,
                    "output_quality_score": 0.95,
                    "requirements_match_score": 0.90,
                    "performance_score": 0.88,
                    "security_score": 0.95,
                    "evidence_confidence": 0.93,
                    "verification_completeness": 1.0,
                },
                "evidence": [
                    {
                        "evidence_type": "output_analysis",
                        "source": "agent_outputs",
                        "data": {"files_created": 2, "tests_passed": 15},
                        "timestamp": "2024-01-15T10:30:15Z",
                        "confidence_score": 0.95,
                    }
                ],
                "verification_timestamp": "2024-01-15T10:30:30Z",
            }
        }


class VerificationConfig(BaseModel):
    """Configuration for verification process."""

    quality_thresholds: dict[str, float] = Field(
        default={
            "code_quality_min": 0.8,
            "test_coverage_min": 0.9,
            "performance_threshold": 1000,
            "security_score_min": 0.85,
        },
        description="Quality thresholds for verification",
    )
    verification_strategies: list[str] = Field(
        default=["output_quality", "requirements_match", "performance", "security"],
        description="Verification strategies to execute",
    )
    evidence_requirements: list[str] = Field(
        default=["outputs", "tool_calls", "performance_metrics"],
        description="Required evidence types for verification",
    )
    timeout_seconds: int = Field(
        default=300, description="Maximum time for verification process"
    )


class VerificationSummary(BaseModel):
    """Summary of verification results for reporting."""

    agent_id: str = Field(..., description="Agent identifier")
    time_period: str = Field(..., description="Time period for summary")
    total_tasks: int = Field(..., description="Total tasks verified")
    completed_tasks: int = Field(..., description="Successfully completed tasks")
    failed_tasks: int = Field(..., description="Failed tasks")
    partial_tasks: int = Field(..., description="Partially completed tasks")
    average_quality_score: float = Field(..., description="Average quality score")
    completion_rate: float = Field(..., description="Task completion rate")
    reliability_trend: str = Field(
        ..., description="Reliability trend (improving/declining/stable)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_456",
                "time_period": "2024-01-15 to 2024-01-22",
                "total_tasks": 25,
                "completed_tasks": 20,
                "failed_tasks": 2,
                "partial_tasks": 3,
                "average_quality_score": 0.87,
                "completion_rate": 0.80,
                "reliability_trend": "improving",
            }
        }
