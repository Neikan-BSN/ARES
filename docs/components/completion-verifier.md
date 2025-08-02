# CompletionVerifier Component

The `CompletionVerifier` is the core component responsible for validating task completion in the ARES system. It ensures that agent tasks are properly completed according to defined requirements and quality standards.

## Overview

The CompletionVerifier implements a comprehensive verification pipeline that analyzes multiple dimensions of task completion:

- **Output Quality Analysis** - Evaluates the quality and correctness of task outputs
- **Requirements Matching** - Verifies that outputs meet the original task requirements
- **Performance Assessment** - Analyzes execution performance and resource usage
- **Security Compliance** - Ensures outputs meet security standards
- **Evidence Collection** - Gathers and validates completion evidence

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CompletionVerifier                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Request         │  │ Evidence        │  │ Quality         │  │
│  │ Validation      │  │ Collection      │  │ Analysis        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Strategy        │  │ Verification    │  │ Result          │  │
│  │ Selection       │  │ Execution       │  │ Generation      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Class Definition

```python
class CompletionVerifier:
    """Primary task completion verification engine.

    Validates that agent tasks are completed according to:
    - Defined success criteria
    - Quality standards and metrics
    - Evidence requirements
    - Performance benchmarks
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the completion verifier."""
        self.db_session = db_session
        self.verification_strategies: Dict[str, Any] = {}
        self._quality_thresholds = {
            "code_quality_min": 0.8,
            "test_coverage_min": 0.9,
            "performance_threshold": 1000,  # ms
            "security_score_min": 0.85,
        }
```

## Core Methods

### verify_task_completion()

The main verification method that orchestrates the entire verification process.

```python
async def verify_task_completion(
    self,
    agent_id: str,
    task_id: str,
    completion_request: TaskCompletionRequest,
) -> TaskCompletionResult:
    """Verify that a task has been completed successfully.

    Args:
        agent_id: Unique identifier for the agent
        task_id: Unique identifier for the task
        completion_request: Details of the completion claim

    Returns:
        TaskCompletionResult with verification status and evidence
    """
```

#### Verification Pipeline

1. **Input Validation** - Validates the completion request format and content
2. **Evidence Collection** - Gathers evidence from multiple sources
3. **Strategy Execution** - Runs verification strategies based on task type
4. **Quality Assessment** - Calculates comprehensive quality metrics
5. **Status Determination** - Determines final completion status
6. **Result Generation** - Creates detailed verification result

### Verification Strategies

The CompletionVerifier uses pluggable verification strategies:

#### Output Quality Verification

```python
async def _verify_output_quality(
    self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
) -> Dict[str, Any]:
    """Verify the quality of task outputs."""
```

**Quality Factors:**
- **Completeness Score** (≥0.8) - How complete the outputs are
- **Accuracy Score** (≥0.85) - How accurate the outputs are
- **Format Compliance** - Whether outputs follow required formats
- **Error Handling Score** (≥0.8) - Quality of error handling

#### Requirements Matching

```python
async def _verify_requirements_match(
    self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
) -> Dict[str, Any]:
    """Verify that outputs match the original task requirements."""
```

**Matching Process:**
1. Extract requirements from task description
2. Analyze outputs against each requirement
3. Calculate match percentage
4. Identify missing requirements

#### Performance Standards

```python
async def _verify_performance_standards(
    self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
) -> Dict[str, Any]:
    """Verify that task performance meets standards."""
```

**Performance Metrics:**
- **Execution Time** (<1000ms threshold)
- **Memory Usage** (<500MB threshold)
- **Error Rate** (<5% threshold)
- **Resource Efficiency**

#### Security Compliance

```python
async def _verify_security_compliance(
    self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
) -> Dict[str, Any]:
    """Verify that task execution meets security standards."""
```

**Security Checks:**
- **Sensitive Data Detection** - Scans for exposed sensitive information
- **Input Sanitization** - Validates proper input handling
- **Injection Pattern Detection** - Checks for security vulnerabilities
- **Transport Security** - Ensures secure communication

## Data Models

### TaskCompletionRequest

```python
class TaskCompletionRequest(BaseModel):
    task_id: str
    agent_id: str
    task_description: str
    completion_evidence: Dict[str, Any]
    completion_timestamp: datetime
    additional_context: Optional[Dict[str, Any]] = None
```

### TaskCompletionResult

```python
class TaskCompletionResult(BaseModel):
    task_id: str
    agent_id: str
    status: CompletionStatus
    message: str
    quality_metrics: QualityMetrics
    evidence: List[VerificationEvidence]
    verification_timestamp: datetime
    verification_details: Optional[Dict[str, Any]] = None
```

### QualityMetrics

```python
class QualityMetrics(BaseModel):
    overall_score: float  # 0-1
    output_quality_score: float  # 0-1
    requirements_match_score: float  # 0-1
    performance_score: float  # 0-1
    security_score: float  # 0-1
    evidence_confidence: float  # 0-1
    verification_completeness: float  # 0-1
```

## Usage Examples

### Basic Verification

```python
from ares.verification.completion import CompletionVerifier
from ares.verification.completion.schemas import TaskCompletionRequest

# Initialize verifier
async with AsyncSession() as session:
    verifier = CompletionVerifier(session)

    # Create completion request
    completion_request = TaskCompletionRequest(
        task_id="task_123",
        agent_id="agent_456",
        task_description="Create user authentication API",
        completion_evidence={
            "outputs": {
                "files_created": ["auth.py", "test_auth.py"],
                "api_endpoints": ["/login", "/logout"],
                "completeness_score": 0.95,
                "accuracy_score": 0.88
            },
            "tool_calls": [
                {"tool_name": "write_file", "success": True},
                {"tool_name": "run_tests", "success": True}
            ],
            "performance_metrics": {
                "execution_time_ms": 1200,
                "memory_usage_mb": 45,
                "error_rate": 0.02
            }
        }
    )

    # Perform verification
    result = await verifier.verify_task_completion(
        "agent_456", "task_123", completion_request
    )

    # Check results
    print(f"Status: {result.status}")
    print(f"Overall Score: {result.quality_metrics.overall_score}")
    print(f"Message: {result.message}")
```

### Custom Quality Thresholds

```python
# Update quality thresholds
await verifier.update_quality_thresholds({
    "code_quality_min": 0.85,
    "test_coverage_min": 0.95,
    "performance_threshold": 800,  # ms
    "security_score_min": 0.90
})

# Verification will now use updated thresholds
result = await verifier.verify_task_completion(
    agent_id, task_id, completion_request
)
```

### Verification History

```python
# Get verification history for analysis
history = await verifier.get_verification_history(
    agent_id="agent_456",
    limit=100
)

for record in history:
    print(f"Task: {record['task_id']}, Score: {record['overall_score']}")
```

## Configuration

### Quality Thresholds

Configure minimum quality thresholds for different verification aspects:

```python
quality_thresholds = {
    "code_quality_min": 0.8,        # Minimum code quality score
    "test_coverage_min": 0.9,       # Minimum test coverage
    "performance_threshold": 1000,   # Max execution time (ms)
    "security_score_min": 0.85,     # Minimum security score
}
```

### Verification Strategies

Enable/disable specific verification strategies:

```python
verification_config = {
    "enable_output_quality": True,
    "enable_requirements_matching": True,
    "enable_performance_verification": True,
    "enable_security_compliance": True,
    "require_all_strategies": False,  # If False, partial verification allowed
}
```

## Error Handling

The CompletionVerifier implements comprehensive error handling:

### Common Errors

```python
try:
    result = await verifier.verify_task_completion(
        agent_id, task_id, completion_request
    )
except ValidationError as e:
    # Invalid completion request format
    logger.error(f"Validation error: {e}")

except InsufficientEvidenceError as e:
    # Not enough evidence for verification
    logger.error(f"Insufficient evidence: {e}")

except VerificationTimeoutError as e:
    # Verification took too long
    logger.error(f"Verification timeout: {e}")

except DatabaseError as e:
    # Database operation failed
    logger.error(f"Database error: {e}")
```

### Error Recovery

```python
# Retry verification with relaxed thresholds
if result.status == CompletionStatus.ERROR:
    # Lower thresholds temporarily
    await verifier.update_quality_thresholds({
        "code_quality_min": 0.7,
        "performance_threshold": 2000
    })

    # Retry verification
    retry_result = await verifier.verify_task_completion(
        agent_id, task_id, completion_request
    )
```

## Performance Considerations

### Optimization Strategies

1. **Evidence Caching** - Cache frequently accessed evidence
2. **Async Processing** - All verification steps are async
3. **Strategy Parallelization** - Run verification strategies in parallel
4. **Result Caching** - Cache verification results for duplicate requests

### Performance Metrics

```python
# Monitor verification performance
async def monitor_performance():
    stats = await verifier.get_performance_stats()

    print(f"Average verification time: {stats['avg_time_ms']}ms")
    print(f"95th percentile: {stats['p95_time_ms']}ms")
    print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
```

## Integration Points

### Database Integration

The CompletionVerifier integrates with the ARES database models:

```python
# Update agent reliability metrics
await self._update_reliability_metrics(
    agent_id, final_status, quality_metrics
)

# Store verification history
await self._store_verification_record(
    task_id, agent_id, result
)
```

### MCP Server Integration

Works seamlessly with the MCP server for external integrations:

```python
# MCP server exposes verification endpoints
@mcp_server.tool("verify_task_completion")
async def verify_task_completion_tool(
    agent_id: str, task_id: str, evidence: Dict[str, Any]
) -> Dict[str, Any]:
    completion_request = TaskCompletionRequest(
        task_id=task_id,
        agent_id=agent_id,
        completion_evidence=evidence
    )

    result = await completion_verifier.verify_task_completion(
        agent_id, task_id, completion_request
    )

    return result.dict()
```

### Event System Integration

Publishes verification events for real-time monitoring:

```python
# Publish verification completed event
await event_publisher.publish("verification.completed", {
    "task_id": task_id,
    "agent_id": agent_id,
    "status": result.status,
    "quality_score": result.quality_metrics.overall_score
})
```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
async def completion_verifier():
    mock_session = AsyncMock()
    return CompletionVerifier(mock_session)

@pytest.mark.asyncio
async def test_task_completion_success(completion_verifier):
    # Test successful task completion verification
    completion_request = TaskCompletionRequest(...)

    result = await completion_verifier.verify_task_completion(
        "agent_001", "task_123", completion_request
    )

    assert result.status == CompletionStatus.COMPLETED
    assert result.quality_metrics.overall_score > 0.8
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_end_to_end_verification():
    # Test complete verification pipeline
    async with test_database_session() as session:
        verifier = CompletionVerifier(session)

        # Create realistic completion request
        request = create_test_completion_request()

        # Perform verification
        result = await verifier.verify_task_completion(
            "test_agent", "test_task", request
        )

        # Verify database updates
        agent_metrics = await get_agent_reliability_metrics("test_agent")
        assert agent_metrics is not None
```

## Monitoring and Observability

### Metrics Collection

```python
# Key metrics to monitor
verification_metrics = {
    "verification_duration_ms": histogram,
    "verification_success_rate": counter,
    "quality_score_distribution": histogram,
    "evidence_collection_errors": counter,
    "strategy_execution_failures": counter
}
```

### Logging

```python
import structlog

logger = structlog.get_logger(__name__)

# Structured logging for verification events
logger.info(
    "verification_completed",
    task_id=task_id,
    agent_id=agent_id,
    status=result.status,
    quality_score=result.quality_metrics.overall_score,
    duration_ms=verification_duration
)
```

---

*Component Version: 1.0.0*
*Last Updated: January 15, 2024*
