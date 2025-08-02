"""Pydantic schemas for proof-of-work collection and analysis."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """Types of work evidence that can be collected."""

    CODE_OUTPUT = "code_output"
    CODE_MODIFICATION = "code_modification"
    TOOL_USAGE = "tool_usage"
    PERFORMANCE_METRICS = "performance_metrics"
    FILE_CHANGES = "file_changes"
    TEST_RESULTS = "test_results"
    DOCUMENTATION = "documentation"
    USER_INTERACTION = "user_interaction"


class CollectionStatus(str, Enum):
    """Status of proof-of-work collection process."""

    HIGH_QUALITY = "high_quality"
    ACCEPTABLE_QUALITY = "acceptable_quality"
    LOW_QUALITY = "low_quality"
    POOR_QUALITY = "poor_quality"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    INVALID = "invalid"
    ERROR = "error"


class ProofOfWorkRequest(BaseModel):
    """Request model for proof-of-work collection."""

    task_id: str = Field(..., description="Unique task identifier")
    agent_id: str = Field(..., description="Agent that completed the work")
    work_description: str = Field(..., description="Description of work completed")
    evidence_sources: dict[str, Any] = Field(
        ..., description="Sources of evidence including code outputs, tool usage, etc."
    )
    expected_deliverables: list[str] | None = Field(
        default=None,
        description="List of expected deliverables for completeness assessment",
    )
    complexity_level: int | None = Field(
        default=None, ge=1, le=5, description="Task complexity level (1-5 scale)"
    )
    work_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the work was completed"
    )
    additional_context: dict[str, Any] | None = Field(
        default=None, description="Additional context for evidence analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_789",
                "agent_id": "agent_456",
                "work_description": "Implemented user authentication API with JWT tokens",
                "evidence_sources": {
                    "code_outputs": {
                        "files_created": [
                            {
                                "path": "auth.py",
                                "size": 2048,
                                "lines": 85,
                                "complexity": 0.7,
                                "has_docs": True,
                                "follows_style": True,
                                "has_tests": True,
                            }
                        ]
                    },
                    "tool_usage": {
                        "tool_calls": [
                            {
                                "tool": "write_file",
                                "params": {"path": "auth.py"},
                                "duration_ms": 150,
                                "success": True,
                                "appropriate": True,
                                "efficient": True,
                            }
                        ]
                    },
                    "performance_data": {
                        "total_time": 1200,
                        "memory_peak": 45,
                        "cpu_avg": 25,
                        "io_ops": 12,
                    },
                },
                "expected_deliverables": ["auth.py", "test_auth.py", "README.md"],
                "complexity_level": 3,
                "work_timestamp": "2024-01-15T10:30:00Z",
            }
        }


class WorkEvidence(BaseModel):
    """Individual piece of work evidence."""

    evidence_type: EvidenceType = Field(..., description="Type of evidence")
    source: str = Field(
        ..., description="Source system or process that generated this evidence"
    )
    data: dict[str, Any] = Field(..., description="Evidence data and metrics")
    timestamp: datetime = Field(..., description="When evidence was collected")
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in evidence reliability (0-1)",
    )
    quality_indicators: dict[str, Any] = Field(
        default_factory=dict,
        description="Quality indicators specific to this evidence type",
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata about the evidence"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "evidence_type": "code_output",
                "source": "file_creation",
                "data": {
                    "file_path": "auth.py",
                    "file_size": 2048,
                    "lines_of_code": 85,
                    "complexity_score": 0.7,
                    "file_hash": "a1b2c3d4e5f6",  # pragma: allowlist secret
                },
                "timestamp": "2024-01-15T10:30:15Z",
                "confidence_score": 0.95,
                "quality_indicators": {
                    "has_documentation": True,
                    "follows_conventions": True,
                    "has_tests": True,
                },
            }
        }


class QualityAssessment(BaseModel):
    """Comprehensive quality assessment of work evidence."""

    overall_quality_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall work quality score (0-1)"
    )
    code_quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Code quality and craftsmanship score (0-1)",
    )
    completeness_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Task completeness score (0-1)"
    )
    performance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Performance efficiency score (0-1)"
    )
    innovation_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Innovation and problem-solving score (0-1)",
    )
    documentation_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Documentation quality score (0-1)"
    )
    confidence_level: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in quality assessment (0-1)",
    )
    assessment_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness of quality assessment process (0-1)",
    )


class ProofOfWorkResult(BaseModel):
    """Result of proof-of-work collection and analysis."""

    task_id: str = Field(..., description="Task identifier")
    agent_id: str = Field(..., description="Agent identifier")
    status: CollectionStatus = Field(..., description="Collection and analysis status")
    message: str = Field(..., description="Human-readable result message")
    quality_assessment: QualityAssessment = Field(
        ..., description="Detailed quality assessment"
    )
    evidence: list[WorkEvidence] = Field(
        default_factory=list, description="Collected work evidence"
    )
    collection_timestamp: datetime = Field(
        ..., description="When collection was completed"
    )
    evidence_artifacts: dict[str, str] | None = Field(
        default=None, description="Paths to stored evidence artifacts"
    )
    analysis_details: dict[str, Any] | None = Field(
        default=None, description="Detailed analysis results by category"
    )
    recommendations: list[str] | None = Field(
        default=None, description="Recommendations for work quality improvement"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_789",
                "agent_id": "agent_456",
                "status": "high_quality",
                "message": "High-quality work evidence collected (score: 0.87)",
                "quality_assessment": {
                    "overall_quality_score": 0.87,
                    "code_quality_score": 0.90,
                    "completeness_score": 0.85,
                    "performance_score": 0.82,
                    "innovation_score": 0.88,
                    "documentation_score": 0.89,
                    "confidence_level": 0.93,
                    "assessment_completeness": 1.0,
                },
                "evidence": [
                    {
                        "evidence_type": "code_output",
                        "source": "file_creation",
                        "data": {"file_path": "auth.py", "lines_of_code": 85},
                        "timestamp": "2024-01-15T10:30:15Z",
                        "confidence_score": 0.95,
                    }
                ],
                "collection_timestamp": "2024-01-15T10:30:30Z",
            }
        }


class EvidenceAnalysisConfig(BaseModel):
    """Configuration for evidence analysis processes."""

    quality_weights: dict[str, float] = Field(
        default={
            "code_quality_weight": 0.25,
            "output_completeness_weight": 0.25,
            "performance_weight": 0.20,
            "innovation_weight": 0.15,
            "documentation_weight": 0.15,
        },
        description="Weights for different quality dimensions",
    )
    evidence_requirements: list[str] = Field(
        default=["code_outputs", "tool_usage", "performance_data"],
        description="Required evidence types for complete analysis",
    )
    quality_thresholds: dict[str, float] = Field(
        default={
            "high_quality_threshold": 0.8,
            "acceptable_threshold": 0.6,
            "low_quality_threshold": 0.4,
        },
        description="Thresholds for quality classification",
    )
    analysis_timeout_seconds: int = Field(
        default=300, description="Maximum time for evidence analysis"
    )


class WorkQualityMetrics(BaseModel):
    """Detailed work quality metrics."""

    lines_of_code: int = Field(default=0, description="Total lines of code produced")
    files_created: int = Field(default=0, description="Number of files created")
    files_modified: int = Field(default=0, description="Number of files modified")
    tests_created: int = Field(default=0, description="Number of tests created")
    documentation_coverage: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Documentation coverage ratio"
    )
    code_complexity_avg: float = Field(
        default=0.0, description="Average code complexity score"
    )
    performance_efficiency: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Performance efficiency score"
    )
    tool_usage_effectiveness: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Tool usage effectiveness score"
    )
    problem_solving_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Problem-solving approach score"
    )


class AgentWorkSummary(BaseModel):
    """Summary of agent work quality over time."""

    agent_id: str = Field(..., description="Agent identifier")
    time_period: str = Field(..., description="Time period for summary")
    total_tasks_completed: int = Field(..., description="Total tasks completed")
    average_quality_score: float = Field(..., description="Average quality score")
    quality_trend: str = Field(
        ..., description="Quality trend (improving/stable/declining)"
    )
    best_performing_areas: list[str] = Field(
        ..., description="Areas of highest quality"
    )
    improvement_areas: list[str] = Field(..., description="Areas needing improvement")
    total_lines_of_code: int = Field(..., description="Total lines of code produced")
    total_files_created: int = Field(..., description="Total files created")
    average_task_complexity: float = Field(
        ..., description="Average task complexity handled"
    )
    innovation_indicators: list[str] = Field(
        ..., description="Innovation indicators observed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_456",
                "time_period": "2024-01-15 to 2024-01-22",
                "total_tasks_completed": 12,
                "average_quality_score": 0.82,
                "quality_trend": "improving",
                "best_performing_areas": ["code_quality", "documentation"],
                "improvement_areas": ["performance_optimization", "test_coverage"],
                "total_lines_of_code": 1250,
                "total_files_created": 18,
                "average_task_complexity": 2.8,
                "innovation_indicators": [
                    "creative_tool_usage",
                    "performance_improvements",
                ],
            }
        }


class EvidenceSearchRequest(BaseModel):
    """Request for searching collected evidence."""

    agent_id: str | None = Field(default=None, description="Filter by agent ID")
    task_id: str | None = Field(default=None, description="Filter by task ID")
    evidence_types: list[EvidenceType] | None = Field(
        default=None, description="Filter by evidence types"
    )
    quality_score_min: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Minimum quality score filter"
    )
    date_from: datetime | None = Field(default=None, description="Start date filter")
    date_to: datetime | None = Field(default=None, description="End date filter")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum results to return"
    )
    include_analysis_details: bool = Field(
        default=False, description="Include detailed analysis information"
    )


class EvidenceSearchResult(BaseModel):
    """Result of evidence search."""

    total_found: int = Field(..., description="Total matching evidence records")
    results: list[ProofOfWorkResult] = Field(..., description="Search results")
    search_timestamp: datetime = Field(..., description="When search was performed")
    query_performance_ms: int = Field(..., description="Search execution time")
    facets: dict[str, Any] | None = Field(
        default=None, description="Search result facets and aggregations"
    )


class QualityBenchmark(BaseModel):
    """Quality benchmarks for comparison."""

    benchmark_name: str = Field(..., description="Name of the benchmark")
    benchmark_version: str = Field(default="1.0", description="Benchmark version")
    quality_thresholds: dict[str, float] = Field(..., description="Quality thresholds")
    performance_benchmarks: dict[str, float] = Field(
        ..., description="Performance benchmarks"
    )
    complexity_factors: dict[str, float] = Field(
        ..., description="Complexity adjustment factors"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "benchmark_name": "standard_development",
                "benchmark_version": "1.0",
                "quality_thresholds": {
                    "code_quality_min": 0.75,
                    "documentation_min": 0.70,
                    "test_coverage_min": 0.80,
                },
                "performance_benchmarks": {
                    "lines_per_hour": 50,
                    "files_per_task": 2.5,
                    "complexity_per_hour": 1.5,
                },
                "complexity_factors": {
                    "low_complexity": 1.0,
                    "medium_complexity": 1.2,
                    "high_complexity": 1.5,
                },
                "created_at": "2024-01-15T09:00:00Z",
            }
        }
