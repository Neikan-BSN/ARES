"""Pydantic schemas for MCP tool call validation."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """Tool call validation status."""

    VALID = "valid"
    INVALID = "invalid"
    UNAUTHORIZED = "unauthorized"
    PROTOCOL_VIOLATION = "protocol_violation"
    INVALID_PARAMETERS = "invalid_parameters"
    RATE_LIMITED = "rate_limited"
    SECURITY_VIOLATION = "security_violation"
    WARNING = "warning"
    ERROR = "error"


class MCPProtocolVersion(str, Enum):
    """Supported MCP protocol versions."""

    V1_0 = "1.0"
    V1_1 = "1.1"


class ToolCallValidationRequest(BaseModel):
    """Request model for MCP tool call validation."""

    tool_name: str = Field(..., description="Name of the MCP tool being called")
    parameters: dict[str, Any] | None = Field(
        default=None, description="Parameters passed to the tool call"
    )
    mcp_version: str = Field(..., description="MCP protocol version used")
    headers: dict[str, str] | None = Field(
        default=None, description="MCP request headers"
    )
    secure_transport: bool = Field(
        default=True, description="Whether secure transport (HTTPS/TLS) is used"
    )
    call_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the tool call was initiated"
    )
    request_id: str | None = Field(
        default=None, description="Unique identifier for the request"
    )
    context: dict[str, Any] | None = Field(
        default=None, description="Additional context for the tool call"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "read_file",
                "parameters": {"path": "/home/user/document.txt", "encoding": "utf-8"},
                "mcp_version": "1.1",
                "headers": {
                    "Content-Type": "application/json",
                    "MCP-Version": "1.1",
                    "Authorization": "Bearer token123",
                },
                "secure_transport": True,
                "call_timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
            }
        }


class ToolCallEvidence(BaseModel):
    """Evidence collected during tool call validation."""

    evidence_type: str = Field(..., description="Type of validation evidence")
    source: str = Field(..., description="Source system that generated the evidence")
    data: dict[str, Any] = Field(..., description="Evidence data and findings")
    timestamp: datetime = Field(..., description="When evidence was collected")
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in evidence accuracy (0-1)"
    )
    validation_rule: str | None = Field(
        default=None, description="Validation rule that generated this evidence"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata about the evidence"
    )


class ComplianceMetrics(BaseModel):
    """Compliance metrics for tool call validation."""

    overall_compliance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall compliance score (0-1)"
    )
    protocol_compliance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="MCP protocol compliance score (0-1)"
    )
    authorization_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Authorization compliance score (0-1)"
    )
    parameter_validation_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Parameter validation score (0-1)"
    )
    rate_limit_compliance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Rate limit compliance score (0-1)"
    )
    security_compliance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Security compliance score (0-1)"
    )
    dependency_compliance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Dependency compliance score (0-1)"
    )
    validation_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness of validation process (0-1)",
    )


class ToolCallValidationResult(BaseModel):
    """Result of MCP tool call validation."""

    agent_id: str = Field(..., description="Agent that initiated the tool call")
    tool_name: str = Field(..., description="Name of the validated tool")
    status: ValidationStatus = Field(..., description="Validation result status")
    message: str = Field(..., description="Human-readable validation message")
    compliance_metrics: ComplianceMetrics = Field(
        ..., description="Detailed compliance metrics"
    )
    evidence: list[ToolCallEvidence] = Field(
        default_factory=list, description="Evidence collected during validation"
    )
    validation_timestamp: datetime = Field(
        ..., description="When validation was completed"
    )
    validation_details: dict[str, Any] | None = Field(
        default=None, description="Detailed validation results by category"
    )
    recommendations: list[str] | None = Field(
        default=None, description="Recommendations for addressing validation issues"
    )
    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Risk score for the validated tool call (0-1)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_456",
                "tool_name": "read_file",
                "status": "valid",
                "message": "Tool call validation passed all compliance checks.",
                "compliance_metrics": {
                    "overall_compliance_score": 0.95,
                    "protocol_compliance_score": 1.0,
                    "authorization_score": 1.0,
                    "parameter_validation_score": 0.98,
                    "rate_limit_compliance_score": 1.0,
                    "security_compliance_score": 0.90,
                    "dependency_compliance_score": 1.0,
                    "validation_completeness": 1.0,
                },
                "evidence": [
                    {
                        "evidence_type": "protocol_compliance",
                        "source": "mcp_validator",
                        "data": {"version_check": "passed", "format_check": "passed"},
                        "timestamp": "2024-01-15T10:30:15Z",
                        "confidence_score": 0.95,
                    }
                ],
                "validation_timestamp": "2024-01-15T10:30:30Z",
            }
        }


class ValidationRule(BaseModel):
    """Configuration for validation rules."""

    rule_id: str = Field(..., description="Unique identifier for the rule")
    rule_name: str = Field(..., description="Human-readable rule name")
    rule_type: str = Field(..., description="Type of validation rule")
    enabled: bool = Field(default=True, description="Whether the rule is active")
    severity: str = Field(
        default="error", description="Rule severity (error, warning, info)"
    )
    conditions: dict[str, Any] = Field(
        ..., description="Rule conditions and parameters"
    )
    error_message: str = Field(..., description="Error message when rule fails")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "auth_001",
                "rule_name": "Tool Authorization Check",
                "rule_type": "authorization",
                "enabled": True,
                "severity": "error",
                "conditions": {
                    "required_permissions": ["tool_access"],
                    "check_context": True,
                },
                "error_message": "Agent not authorized to use this tool",
                "created_at": "2024-01-15T09:00:00Z",
            }
        }


class ToolSchema(BaseModel):
    """Schema definition for MCP tools."""

    tool_name: str = Field(..., description="Name of the tool")
    version: str = Field(default="1.0", description="Schema version")
    description: str = Field(..., description="Tool description")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parameter schema definition"
    )
    required_parameters: list[str] = Field(
        default_factory=list, description="List of required parameter names"
    )
    return_type: str | None = Field(default=None, description="Expected return type")
    permissions_required: list[str] = Field(
        default_factory=list, description="Required permissions to use this tool"
    )
    rate_limits: dict[str, int] | None = Field(
        default=None, description="Rate limiting configuration"
    )
    dependencies: dict[str, list[str]] | None = Field(
        default=None, description="Tool dependencies and conflicts"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "read_file",
                "version": "1.0",
                "description": "Read content from a file",
                "parameters": {
                    "path": {"type": "string", "description": "File path to read"},
                    "encoding": {"type": "string", "default": "utf-8"},
                },
                "required_parameters": ["path"],
                "return_type": "string",
                "permissions_required": ["file_read"],
                "rate_limits": {"calls_per_minute": 60, "calls_per_hour": 1000},
            }
        }


class AgentPermissions(BaseModel):
    """Agent permissions configuration."""

    agent_id: str = Field(..., description="Unique agent identifier")
    tool_permissions: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Tool-specific permissions and constraints"
    )
    global_permissions: list[str] = Field(
        default_factory=list, description="Global permissions applicable to all tools"
    )
    rate_limit_overrides: dict[str, dict[str, int]] | None = Field(
        default=None, description="Agent-specific rate limit overrides"
    )
    security_context: dict[str, Any] | None = Field(
        default=None, description="Security context and constraints"
    )
    expires_at: datetime | None = Field(
        default=None, description="When permissions expire"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_456",
                "tool_permissions": {
                    "read_file": {
                        "allowed_paths": ["/home/user/*"],
                        "max_file_size": 10485760,
                    },
                    "write_file": {
                        "allowed_paths": ["/home/user/workspace/*"],
                        "backup_required": True,
                    },
                },
                "global_permissions": ["basic_access", "file_operations"],
                "rate_limit_overrides": {"read_file": {"calls_per_minute": 120}},
                "expires_at": "2024-12-31T23:59:59Z",
                "created_at": "2024-01-15T09:00:00Z",
            }
        }


class ValidationSummary(BaseModel):
    """Summary of validation results over time."""

    agent_id: str = Field(..., description="Agent identifier")
    time_period: str = Field(..., description="Time period for summary")
    total_tool_calls: int = Field(..., description="Total tool calls validated")
    valid_calls: int = Field(..., description="Successfully validated calls")
    invalid_calls: int = Field(..., description="Invalid tool calls")
    unauthorized_calls: int = Field(..., description="Unauthorized tool calls")
    rate_limited_calls: int = Field(..., description="Rate limited calls")
    security_violations: int = Field(..., description="Security violation calls")
    average_compliance_score: float = Field(..., description="Average compliance score")
    most_used_tools: list[str] = Field(..., description="Most frequently used tools")
    violation_patterns: list[str] = Field(..., description="Common violation patterns")
    recommendations: list[str] = Field(..., description="Improvement recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_456",
                "time_period": "2024-01-15 to 2024-01-22",
                "total_tool_calls": 150,
                "valid_calls": 142,
                "invalid_calls": 3,
                "unauthorized_calls": 2,
                "rate_limited_calls": 2,
                "security_violations": 1,
                "average_compliance_score": 0.94,
                "most_used_tools": ["read_file", "write_file", "run_command"],
                "violation_patterns": ["missing_parameters", "rate_limit_exceeded"],
                "recommendations": [
                    "Review parameter validation",
                    "Implement better rate limiting",
                ],
            }
        }


class ToolCallLog(BaseModel):
    """Log entry for tool call validation."""

    log_id: str = Field(..., description="Unique log identifier")
    agent_id: str = Field(..., description="Agent that made the call")
    tool_name: str = Field(..., description="Tool that was called")
    validation_status: ValidationStatus = Field(..., description="Validation result")
    compliance_score: float = Field(..., description="Overall compliance score")
    parameters_hash: str | None = Field(
        default=None, description="Hash of parameters for deduplication"
    )
    execution_time_ms: int | None = Field(
        default=None, description="Validation execution time in milliseconds"
    )
    violations: list[str] = Field(
        default_factory=list, description="List of validation violations"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "log_id": "log_789",
                "agent_id": "agent_456",
                "tool_name": "read_file",
                "validation_status": "valid",
                "compliance_score": 0.95,
                "parameters_hash": "sha256:abc123...",
                "execution_time_ms": 45,
                "violations": [],
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
