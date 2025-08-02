# Verification API Reference

The Verification API provides endpoints for task completion verification, quality assessment, and evidence analysis. This API is the core of the ARES system's reliability enforcement capabilities.

## Base URL

```
http://localhost:8000/api/v1/verification
```

## Authentication

All API endpoints require authentication via API key or JWT token:

```http
Authorization: Bearer <your-token>
# or
X-API-Key: <your-api-key>
```

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks/verify` | Verify task completion |
| `GET` | `/tasks/{task_id}/status` | Get verification status |
| `GET` | `/tasks/{task_id}/evidence` | Get verification evidence |
| `POST` | `/quality/assess` | Assess work quality |
| `GET` | `/history/{agent_id}` | Get agent verification history |
| `GET` | `/metrics/summary` | Get verification metrics |

---

## Task Completion Verification

### Verify Task Completion

Verify that an agent has successfully completed a task according to defined requirements and quality standards.

```http
POST /api/v1/verification/tasks/verify
```

#### Request Body

```json
{
  "task_id": "task_12345",
  "agent_id": "agent_001",
  "task_description": "Create user authentication API with JWT tokens",
  "completion_evidence": {
    "outputs": {
      "files_created": [
        {
          "path": "auth.py",
          "size": 2048,
          "lines": 85,
          "complexity": 0.7,
          "has_docs": true,
          "follows_style": true,
          "has_tests": true
        }
      ],
      "completeness_score": 0.95,
      "accuracy_score": 0.88,
      "format_compliance": true,
      "error_handling_score": 0.85
    },
    "tool_calls": [
      {
        "tool_name": "write_file",
        "parameters": {
          "path": "auth.py",
          "content": "..."
        },
        "duration_ms": 150,
        "success": true,
        "appropriate": true,
        "efficient": true
      }
    ],
    "performance_metrics": {
      "execution_time_ms": 1200,
      "memory_usage_mb": 45,
      "error_rate": 0.02,
      "cpu_usage_percent": 25
    }
  },
  "completion_timestamp": "2024-01-15T10:30:00Z",
  "additional_context": {
    "complexity_level": 3,
    "priority": "high"
  }
}
```

#### Response

```json
{
  "task_id": "task_12345",
  "agent_id": "agent_001",
  "status": "completed",
  "message": "Task completed successfully with all quality standards met.",
  "quality_metrics": {
    "overall_score": 0.89,
    "output_quality_score": 0.92,
    "requirements_match_score": 0.88,
    "performance_score": 0.85,
    "security_score": 0.91,
    "evidence_confidence": 0.94,
    "verification_completeness": 1.0
  },
  "evidence": [
    {
      "evidence_type": "output_analysis",
      "source": "agent_outputs",
      "data": {
        "files_created": 1,
        "lines_of_code": 85,
        "complexity_average": 0.7
      },
      "timestamp": "2024-01-15T10:30:15Z",
      "confidence_score": 0.95
    }
  ],
  "verification_timestamp": "2024-01-15T10:30:30Z",
  "verification_details": {
    "output_quality": {
      "passed": true,
      "score": 0.92,
      "factors": ["completeness_good", "accuracy_good", "format_compliant"]
    },
    "requirements_match": {
      "passed": true,
      "score": 0.88,
      "matched_requirements": ["authentication", "jwt_tokens", "api_endpoints"],
      "total_requirements": 3
    },
    "performance": {
      "passed": true,
      "score": 0.85,
      "execution_time_ms": 1200,
      "memory_usage_mb": 45
    },
    "security": {
      "passed": true,
      "score": 0.91,
      "issues": []
    }
  }
}
```

#### Response Codes

| Code | Description |
|------|-------------|
| `200` | Verification completed successfully |
| `400` | Invalid request data or missing evidence |
| `401` | Authentication required |
| `403` | Insufficient permissions |
| `404` | Task or agent not found |
| `422` | Validation error in request data |
| `500` | Internal server error |

---

### Get Verification Status

Retrieve the current verification status for a specific task.

```http
GET /api/v1/verification/tasks/{task_id}/status
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | string | Unique task identifier |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_details` | boolean | `false` | Include detailed verification results |
| `include_evidence` | boolean | `false` | Include collected evidence |

#### Response

```json
{
  "task_id": "task_12345",
  "agent_id": "agent_001",
  "status": "completed",
  "overall_score": 0.89,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:30Z",
  "duration_ms": 30000,
  "summary": {
    "requirements_met": 3,
    "total_requirements": 3,
    "quality_issues": 0,
    "security_issues": 0
  }
}
```

---

### Get Verification Evidence

Retrieve detailed evidence collected during task verification.

```http
GET /api/v1/verification/tasks/{task_id}/evidence
```

#### Response

```json
{
  "task_id": "task_12345",
  "evidence_count": 4,
  "evidence": [
    {
      "evidence_type": "output_analysis",
      "source": "agent_outputs",
      "data": {
        "files_created": ["auth.py", "test_auth.py"],
        "total_lines": 125,
        "documentation_coverage": 0.95
      },
      "timestamp": "2024-01-15T10:30:15Z",
      "confidence_score": 0.95,
      "metadata": {
        "analyzer_version": "1.0.0",
        "analysis_duration_ms": 250
      }
    },
    {
      "evidence_type": "tool_usage",
      "source": "mcp_logs",
      "data": {
        "tools_used": ["write_file", "run_tests"],
        "total_calls": 5,
        "success_rate": 1.0
      },
      "timestamp": "2024-01-15T10:30:20Z",
      "confidence_score": 0.98
    }
  ],
  "collection_summary": {
    "collection_started": "2024-01-15T10:30:00Z",
    "collection_completed": "2024-01-15T10:30:25Z",
    "evidence_types": ["output_analysis", "tool_usage", "performance_metrics", "security_scan"],
    "collection_completeness": 1.0
  }
}
```

---

## Quality Assessment

### Assess Work Quality

Perform comprehensive quality assessment of agent work based on collected evidence.

```http
POST /api/v1/verification/quality/assess
```

#### Request Body

```json
{
  "agent_id": "agent_001",
  "task_id": "task_12345",
  "work_description": "Implemented user authentication API with JWT tokens",
  "evidence_sources": {
    "code_outputs": {
      "files_created": [
        {
          "path": "auth.py",
          "size": 2048,
          "complexity": 0.7,
          "has_docs": true,
          "has_tests": true
        }
      ]
    },
    "tool_usage": {
      "tool_calls": [
        {
          "tool": "write_file",
          "success": true,
          "duration_ms": 150
        }
      ]
    },
    "performance_data": {
      "total_time": 1200,
      "memory_peak": 45,
      "cpu_avg": 25
    }
  },
  "expected_deliverables": ["auth.py", "test_auth.py", "README.md"],
  "complexity_level": 3
}
```

#### Response

```json
{
  "task_id": "task_12345",
  "agent_id": "agent_001",
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
    "assessment_completeness": 1.0
  },
  "evidence": [
    {
      "evidence_type": "code_output",
      "source": "file_creation",
      "data": {
        "file_path": "auth.py",
        "lines_of_code": 85,
        "complexity_score": 0.7
      },
      "quality_indicators": {
        "has_documentation": true,
        "follows_conventions": true,
        "has_tests": true
      }
    }
  ],
  "analysis_details": {
    "code_analysis": {
      "score": 0.90,
      "documentation_coverage": 0.95,
      "style_compliance": 0.92,
      "test_coverage": 0.85
    },
    "completeness_analysis": {
      "score": 0.85,
      "completeness_ratio": 0.85,
      "output_diversity": 0.75
    },
    "performance_analysis": {
      "score": 0.82,
      "execution_time_ms": 1200,
      "memory_usage_mb": 45
    }
  }
}
```

---

## Agent History and Metrics

### Get Agent Verification History

Retrieve historical verification data for a specific agent.

```http
GET /api/v1/verification/history/{agent_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | string | Unique agent identifier |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | `50` | Maximum number of records to return |
| `offset` | integer | `0` | Number of records to skip |
| `start_date` | string | | Start date filter (ISO 8601) |
| `end_date` | string | | End date filter (ISO 8601) |
| `status` | string | | Filter by verification status |
| `include_details` | boolean | `false` | Include detailed verification results |

#### Response

```json
{
  "agent_id": "agent_001",
  "total_records": 156,
  "returned_records": 50,
  "summary": {
    "total_verifications": 156,
    "successful_verifications": 142,
    "failed_verifications": 14,
    "average_quality_score": 0.84,
    "success_rate": 0.91,
    "average_duration_ms": 1350
  },
  "verifications": [
    {
      "task_id": "task_12345",
      "status": "completed",
      "overall_score": 0.89,
      "verification_timestamp": "2024-01-15T10:30:30Z",
      "duration_ms": 30000,
      "quality_breakdown": {
        "code_quality": 0.92,
        "completeness": 0.88,
        "performance": 0.85,
        "security": 0.91
      }
    }
  ],
  "trends": {
    "quality_trend": "improving",
    "recent_average": 0.87,
    "previous_average": 0.81,
    "improvement": 0.06
  }
}
```

### Get Verification Metrics Summary

Get system-wide verification metrics and statistics.

```http
GET /api/v1/verification/metrics/summary
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `day` | Time period: `hour`, `day`, `week`, `month` |
| `agent_id` | string | | Filter by specific agent |
| `include_trends` | boolean | `false` | Include trend analysis |

#### Response

```json
{
  "period": "day",
  "period_start": "2024-01-15T00:00:00Z",
  "period_end": "2024-01-15T23:59:59Z",
  "summary": {
    "total_verifications": 342,
    "successful_verifications": 298,
    "failed_verifications": 44,
    "success_rate": 0.87,
    "average_quality_score": 0.84,
    "average_duration_ms": 1250
  },
  "by_status": {
    "completed": 268,
    "partial": 30,
    "failed": 37,
    "error": 7
  },
  "by_type": {
    "task_completion": 198,
    "tool_validation": 89,
    "proof_of_work": 55
  },
  "quality_distribution": {
    "high_quality": 156,
    "acceptable_quality": 112,
    "low_quality": 58,
    "poor_quality": 16
  },
  "performance_metrics": {
    "p50_duration_ms": 980,
    "p95_duration_ms": 2340,
    "p99_duration_ms": 4120,
    "total_processing_time_ms": 427500
  }
}
```

---

## Error Handling

The API uses standard HTTP status codes and returns detailed error information:

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "completion_evidence",
      "issue": "Missing required field 'outputs'"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | Valid authentication required |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard tier**: 1000 requests per hour per API key
- **Premium tier**: 10000 requests per hour per API key
- **Burst limit**: 100 requests per minute

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 842
X-RateLimit-Reset: 1642267200
X-RateLimit-Window: 3600
```

---

## SDKs and Libraries

### Python SDK

```python
from ares_client import AresClient

client = AresClient(api_key="your-api-key")

# Verify task completion
result = await client.verification.verify_task(
    task_id="task_12345",
    agent_id="agent_001",
    evidence=evidence_data
)

print(f"Status: {result.status}")
print(f"Quality Score: {result.quality_metrics.overall_score}")
```

### JavaScript SDK

```javascript
import { AresClient } from '@ares/client';

const client = new AresClient({ apiKey: 'your-api-key' });  // pragma: allowlist secret

// Verify task completion
const result = await client.verification.verifyTask({
  taskId: 'task_12345',
  agentId: 'agent_001',
  evidence: evidenceData
});

console.log(`Status: ${result.status}`);
console.log(`Quality Score: ${result.qualityMetrics.overallScore}`);
```

---

## Webhooks

Configure webhooks to receive real-time notifications about verification events:

### Webhook Events

| Event | Description |
|-------|-------------|
| `verification.completed` | Task verification completed |
| `verification.failed` | Task verification failed |
| `quality.threshold_breach` | Quality score below threshold |
| `agent.reliability_change` | Agent reliability score changed |

### Webhook Payload

```json
{
  "event": "verification.completed",
  "timestamp": "2024-01-15T10:30:30Z",
  "data": {
    "task_id": "task_12345",
    "agent_id": "agent_001",
    "status": "completed",
    "quality_score": 0.89
  },
  "metadata": {
    "webhook_id": "wh_abc123",
    "delivery_attempt": 1
  }
}
```

---

*Last updated: January 15, 2024*
