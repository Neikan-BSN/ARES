# Contributing to ARES

Thank you for your interest in contributing to ARES (Agent Reliability Enforcement System)! This guide will help you get started with contributing to our project.

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git
- UV package manager

### Development Environment Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/ARES.git
cd ARES
git remote add upstream https://github.com/Neikan-BSN/ARES.git

# 2. Set up development environment
uv sync --all-extras
docker compose up -d postgres redis

# 3. Run database migrations
uv run alembic upgrade head

# 4. Verify setup
uv run pytest
uv run python -m ares.main --help
```

## 🛠️ Development Workflow

### 1. Choose Your Contribution
- **🐛 Bug fixes**: Check [GitHub Issues](https://github.com/Neikan-BSN/ARES/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
- **✨ Features**: Look for [feature requests](https://github.com/Neikan-BSN/ARES/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
- **📚 Documentation**: Find [documentation issues](https://github.com/Neikan-BSN/ARES/issues?q=is%3Aissue+is%3Aopen+label%3Adocumentation)
- **🧪 Testing**: Help improve test coverage

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### 3. Make Your Changes

#### Code Quality Standards
```bash
# Format code before committing
uv run ruff format

# Check linting
uv run ruff check

# Run type checking
uv run mypy src/

# Run tests
uv run pytest
```

#### Agent System Integration
If working with the agent coordination system:

```python
# Always use agent coordination for complex tasks
from ares.agents import get_agent_coordinator

@task_handler
async def implement_feature():
    coordinator = get_agent_coordinator()

    # Start with tech-lead-orchestrator
    result = await coordinator.delegate_task(
        agent="tech-lead-orchestrator",
        task="Implement reliability monitoring feature",
        context={"requirements": requirements}
    )

    return result
```

### 4. Testing Requirements

#### Unit Tests
```bash
# Run specific test modules
uv run pytest tests/unit/test_verification.py

# Test with coverage
uv run pytest --cov=src/ares --cov-report=html
```

#### Integration Tests
```bash
# Start test environment
docker compose -f docker-compose.test.yml up -d

# Run integration tests
uv run pytest tests/integration/

# Cleanup
docker compose -f docker-compose.test.yml down
```

#### Add Tests for New Features
```python
# tests/unit/test_your_feature.py
import pytest
from ares.your_module import YourFeature

@pytest.fixture
async def feature_instance():
    return YourFeature()

async def test_your_feature_functionality(feature_instance):
    result = await feature_instance.do_something()
    assert result.success is True
    assert result.data["key"] == "expected_value"
```

### 5. Documentation
Update documentation for any new features:

```bash
# Update API documentation
# Edit docs/api/ files as needed

# Update CLAUDE.md for AI assistant guidance
# Add new command references and patterns

# Update README.md if user-facing changes
# Keep it concise - details go in docs/
```

### 6. Submit Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request via GitHub UI
# Include:
# - Clear description of changes
# - Link to related issues
# - Screenshots for UI changes
# - Test results
```

## 🏗️ Project Architecture

### Core Components

#### Verification System
- **CompletionVerifier** (`src/ares/verification/completion/`)
- **ProofOfWorkCollector** (`src/ares/verification/proof_of_work/`)
- **ToolCallValidator** (`src/ares/verification/tool_validation/`)
- **TaskRollbackManager** (`src/ares/verification/rollback/`)

#### Agent Coordination
- **Tech-Lead-Orchestrator**: Primary task coordinator
- **Project-Analyst**: Deep architectural analysis
- **Code-Reviewer**: Quality assurance and security
- **Performance-Optimizer**: System optimization

#### Data Layer
- **Models** (`src/ares/models/`): SQLAlchemy database models
- **Migrations** (`migrations/`): Alembic database migrations
- **MCP Integration** (`src/ares/mcp_server/`): Model Context Protocol

### Coding Conventions

#### Python Style
```python
# Use type hints for all functions
async def verify_task_completion(
    task_id: str,
    evidence: Dict[str, Any]
) -> CompletionResult:
    """Verify task completion with evidence validation.

    Args:
        task_id: Unique task identifier
        evidence: Task completion evidence dictionary

    Returns:
        CompletionResult with success status and metrics

    Raises:
        ValidationError: If evidence is invalid
        DatabaseError: If database operation fails
    """
    pass

# Use descriptive variable names
agent_reliability_score = calculate_reliability(metrics)
task_completion_rate = successful_tasks / total_tasks

# Prefer composition over inheritance
class ReliabilityMonitor:
    def __init__(self, verifier: CompletionVerifier, collector: ProofOfWorkCollector):
        self.verifier = verifier
        self.collector = collector
```

#### Database Operations
```python
# Always use async database operations
async def get_agent_metrics(agent_id: str) -> AgentMetrics:
    async with get_db_session() as session:
        result = await session.execute(
            select(ReliabilityMetric)
            .where(ReliabilityMetric.agent_id == agent_id)
            .order_by(ReliabilityMetric.recorded_at.desc())
        )
        return result.scalars().first()

# Use proper error handling
try:
    await database_operation()
except SQLAlchemyError as e:
    logger.error(f"Database operation failed: {e}")
    raise DatabaseError("Failed to complete operation")
```

#### API Development
```python
# Use FastAPI with proper validation
@router.post("/agents/{agent_id}/verify", response_model=VerificationResponse)
async def verify_agent_task(
    agent_id: str,
    verification_data: VerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> VerificationResponse:
    """Verify agent task completion."""
    try:
        result = await verification_service.verify_task(
            agent_id=agent_id,
            data=verification_data.dict(),
            db=db
        )
        return VerificationResponse(**result)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for component interaction
├── performance/            # Performance and load tests
├── fixtures/               # Shared test data and fixtures
└── conftest.py            # Pytest configuration
```

### Writing Effective Tests

#### Unit Tests
```python
# Test individual functions and methods
@pytest.mark.asyncio
async def test_completion_verifier_success():
    verifier = CompletionVerifier()
    evidence = {"task_id": "123", "status": "completed", "artifacts": ["file.py"]}

    result = await verifier.verify_completion(evidence)

    assert result.success is True
    assert result.completion_score > 0.8
    assert "file.py" in result.artifacts
```

#### Integration Tests
```python
# Test component interactions
@pytest.mark.asyncio
async def test_agent_task_full_workflow():
    async with TestClient() as client:
        # Create agent
        agent_response = await client.post("/agents", json={"name": "test-agent"})
        agent_id = agent_response.json()["id"]

        # Submit task
        task_response = await client.post(
            f"/agents/{agent_id}/tasks",
            json={"description": "Test task", "requirements": []}
        )

        # Verify completion
        verify_response = await client.post(
            f"/agents/{agent_id}/verify",
            json={"evidence": {"status": "completed"}}
        )

        assert verify_response.status_code == 200
        assert verify_response.json()["success"] is True
```

### Test Data Management
```python
# Use factories for test data
@pytest.fixture
def agent_factory():
    def _create_agent(**kwargs):
        defaults = {
            "name": "test-agent",
            "capabilities": ["code-review", "testing"],
            "status": "active"
        }
        defaults.update(kwargs)
        return Agent(**defaults)
    return _create_agent

# Clean up test data
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    yield
    # Cleanup logic here
    await cleanup_test_database()
```

## 📋 Code Review Process

### Pull Request Checklist
- [ ] **Functionality**: Code works as intended
- [ ] **Tests**: Adequate test coverage (>90% for new code)
- [ ] **Documentation**: Updated docs for user-facing changes
- [ ] **Code Quality**: Passes all linting and type checks
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security vulnerabilities introduced
- [ ] **Agent Integration**: Proper agent coordination patterns used

### Review Focus Areas

#### Security Review
- Input validation for all user data
- SQL injection prevention
- Authentication and authorization
- Sensitive data handling

#### Performance Review
- Database query efficiency
- Async/await usage
- Memory usage patterns
- API response times

#### Architecture Review
- Component boundaries and responsibilities
- Error handling and recovery
- Integration patterns
- Scalability considerations

## 🎯 Specialized Contribution Areas

### Agent System Development
If contributing to the agent coordination system:
- Follow agent routing patterns in CLAUDE.md
- Use @tech-lead-orchestrator for complex tasks
- Implement proper agent handoff protocols
- Ensure reliability monitoring integration

### MCP Server Integration
For Model Context Protocol development:
- Test MCP server connections thoroughly
- Implement proper error handling for external services
- Document MCP tool usage patterns
- Ensure proper resource cleanup

### Web Dashboard Development
For dashboard and UI contributions:
- Use responsive design principles
- Implement real-time updates with WebSockets
- Follow accessibility guidelines
- Test across different browsers and devices

## 🐛 Bug Reports

### Effective Bug Reports Include:
1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected vs actual behavior**
4. **Environment details** (OS, Python version, etc.)
5. **Log output** or error messages
6. **Screenshots** for UI issues

### Bug Report Template:
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- ARES Version: [e.g., 0.1.0]
- Docker Version: [e.g., 24.0.0]

## Additional Context
Any other relevant information
```

## 🚀 Getting Help

### Communication Channels
- **GitHub Discussions**: General questions and feature discussions
- **GitHub Issues**: Bug reports and feature requests
- **Code Review**: Pull request discussions

### Resources
- **CLAUDE.md**: Comprehensive technical guidance for AI assistants
- **docs/**: Detailed documentation and guides
- **tests/**: Examples of proper testing patterns
- **src/ares/**: Source code with inline documentation

---

Thank you for contributing to ARES! Your contributions help make AI agent reliability monitoring better for everyone. 🎉
