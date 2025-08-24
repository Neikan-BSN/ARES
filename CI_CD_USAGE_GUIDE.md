# ARES CI/CD Usage Guide

## Quick Start

ARES includes a comprehensive CI/CD suite optimized for agent reliability enforcement systems with real-time monitoring, proof-of-work validation, and MCP ecosystem integration.

### Essential Commands

```bash
# Environment Setup
make install           # Install all dependencies with quality gates
make env-check         # Validate canonical UV environment
make clean-env         # Remove non-canonical environments

# Quality Gates (run all or individual)
make quality-gates     # Run all 4 quality gates
make quality-gate-1    # Environment validation
make quality-gate-2    # Code quality & standards
make quality-gate-3    # Security compliance
make quality-gate-4    # Testing & coverage

# CI/CD Operations
make ci-check          # Pragmatic CI validation (5-8 minutes)
make ci-check-full     # Comprehensive CI with quality gates (15-20 minutes)
```

## ARES Specific Features

### Agent Reliability Testing

**Agent Monitoring System:**
```bash
# Agent reliability management
make agents-status     # Check agent monitoring status
make agents-health     # Health check for reliability system
make run-agent         # Start the agent reliability system

# Agent reliability testing
make test-reliability  # Reliability scoring and metrics
make test-proof-work   # Proof-of-work validation testing
make test-agents       # Agent behavior validation tests
```

**Performance Benchmarks:**
- Agent coordination APIs: <200ms response times
- WebSocket updates: <50ms latency
- Database queries: <10ms execution
- Reliability calculations: <100ms completion
- Concurrent task handling: 1000+ tasks simultaneously

### Real-Time Monitoring System

**WebSocket Performance Testing:**
```bash
# Real-time monitoring validation
make test-websocket-latency      # WebSocket performance testing
make test-status-broadcasting    # Agent status update testing
make test-metrics-collection     # Reliability metrics testing
make test-enforcement-triggers   # Enforcement action testing
```

**Monitoring Commands:**
```bash
# Start ARES server
uv run python -m src.ARES.main

# Start API server
make run-api
# Access at http://localhost:8000

# Alternative: Start specific components
uv run uvicorn src.ARES.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Proof-of-Work Validation

**Evidence Collection Testing:**
```bash
# Proof-of-work validation
make test-completion-verifier    # Task completion verification
make test-tool-validator        # MCP tool usage validation
make test-rollback-manager      # Failure recovery testing
make test-proof-collector       # Evidence collection validation
```

**Validation Components:**
- **CompletionVerifier**: Validates task completion against requirements
- **ToolCallValidator**: Ensures proper MCP server tool usage
- **TaskRollbackManager**: Handles failed task recovery
- **ProofOfWorkCollector**: Gathers evidence of agent work quality
- **AgentBehaviorMonitor**: Tracks agent performance patterns

## Quality Gates Deep Dive

### Gate 1: Environment Validation

**What it checks:**
- Canonical `.venv` environment setup
- Python 3.12 version compliance
- FastAPI and SQLAlchemy setup
- Redis and Celery connectivity
- MCP ecosystem integration (14 servers)

**Troubleshooting:**
```bash
# Fix environment issues
make clean-env && make install

# Check specific components
uv --version              # Should be 0.8.3+
python --version          # Should be 3.12+
redis-cli ping           # Should return PONG
```

### Gate 2: Code Quality & Standards

**Standards Applied:**
- Ruff formatting with 88-character line limit
- Critical linting (E9, F, B, S error classes only)
- FastAPI endpoint standards validation
- SQLAlchemy model quality analysis
- WebSocket implementation code quality

**Common Issues & Fixes:**
```bash
# Fix formatting issues
make format

# Check specific code quality issues
uv run ruff check src/ tests/ --select="E9,F,B,S"
uv run ruff format --check src/ tests/

# Fix import sorting
uv run ruff check --select I src/ tests/ --fix
```

### Gate 3: Security Compliance

**Security Checks:**
- Bandit security scanning for agent operations
- Input validation for agent task data
- Database access control verification
- WebSocket security implementation testing

**Security Issues Resolution:**
```bash
# Run security scans
make security

# Check specific security issues
uv run bandit -r src/ tests/ -f json -o reports/bandit-report.json
uv run safety check

# Update security baseline if needed
make secrets-update
```

### Gate 4: Testing & Coverage

**Testing Requirements:**
- Unit tests: >90% coverage for reliability components
- Integration tests: Full ARES component validation
- Performance tests: Agent reliability under load
- End-to-end tests: Complete reliability enforcement validation

**Testing Commands:**
```bash
# Run all tests with coverage
make test

# Run specific test categories
make test-unit         # Unit tests only
make test-integration  # Integration tests

# ARES-specific testing
pytest tests/agents/       # Agent-specific tests
pytest tests/reliability/  # Reliability framework tests
pytest tests/integration/  # Cross-agent integration tests
```

## Development Workflow

### Daily Development

**Morning Setup:**
```bash
# Start fresh development session
make env-check         # Verify environment
redis-server &         # Start Redis if not running
make agents-status     # Check agent reliability system health
```

**Before Committing:**
```bash
# Quick validation (5-8 minutes)
make ci-check

# Comprehensive validation (15-20 minutes)
make ci-check-full
```

**Feature Development:**
```bash
# Start feature development
git checkout -b feature/enhanced-reliability-scoring

# Regular testing during development
make test-unit         # Fast unit tests
make test-reliability  # Reliability system validation

# Before merge
make quality-gates     # Full quality validation
make test-integration  # Integration testing
```

### Agent Reliability Development Workflow

**Implementing New Reliability Features:**
1. Implement feature in appropriate ARES component
2. Add comprehensive tests in `tests/reliability/`
3. Update API endpoints if needed
4. Test real-time monitoring: `make test-websocket-latency`
5. Validate performance: `make test-performance`

**Modifying Enforcement Logic:**
1. Update enforcement components in `src/verification/`
2. Test proof-of-work validation: `make test-proof-work`
3. Validate rollback mechanisms: `make test-rollback-manager`
4. Check agent behavior monitoring: `make test-agents`

## Troubleshooting Common Issues

### Environment Issues

**"Canonical .venv not found":**
```bash
make clean-env && make install
```

**Redis Connection Issues:**
```bash
# Check Redis status
redis-cli ping

# Start Redis if not running
redis-server &

# Test Redis connection from ARES
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

**Database Connection Issues:**
```bash
# Check database connectivity
python -c "from src.ares.models.base import engine; print('DB OK')"

# Run database migrations
uv run alembic upgrade head

# Initialize ARES database
uv run python -m ares.cli db-init
```

### Agent Reliability System Issues

**Reliability Monitoring Problems:**
```bash
# Check agent reliability system health
make agents-status
make agents-health

# Restart reliability monitoring
make run-agent

# Check reliability logs
tail -f logs/reliability-*.log
```

**WebSocket Performance Issues:**
```bash
# Test WebSocket connectivity
make test-websocket-latency

# Check WebSocket server status
curl http://localhost:8000/health

# Monitor WebSocket connections
make monitor-websocket-connections
```

### Performance Issues

**Slow Agent APIs:**
```bash
# Analyze performance bottlenecks
make analyze-bottlenecks

# Test specific performance areas
make test-performance

# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/agents
```

**High Memory Usage:**
```bash
# Check memory usage
ps aux | grep python | grep ares

# Monitor Redis memory usage
redis-cli info memory

# Optimize database connection pooling
# Review src/ares/core/config.py database settings
```

### Testing Issues

**Test Failures:**
```bash
# Run tests with verbose output
pytest tests/ -v -s

# Run specific failing test
pytest tests/test_specific.py::TestClass::test_method -v -s

# Check test dependencies
make env-check
redis-cli ping  # Ensure Redis is running
```

**WebSocket Testing Issues:**
```bash
# Test WebSocket connectivity directly
python -c "
import asyncio
import websockets
async def test():
    uri = 'ws://localhost:8000/ws'
    async with websockets.connect(uri) as websocket:
        await websocket.send('test')
        response = await websocket.recv()
        print(f'Response: {response}')
asyncio.run(test())
"
```

## Performance Optimization

### Agent Reliability Optimization

**Database Performance:**
```bash
# Analyze slow queries
# Review database logs for slow query patterns

# Optimize reliability metrics storage
# Check src/ares/models/reliability.py for indexing

# Monitor database performance
uv run python -c "
from src.ares.models.base import engine
with engine.connect() as conn:
    result = conn.execute('SELECT COUNT(*) FROM agents')
    print(f'Agents: {result.scalar()}')
"
```

**WebSocket Performance:**
```bash
# Test WebSocket performance under load
make test-websocket-load

# Optimize WebSocket connection handling
# Review src/ares/api/websocket.py

# Monitor concurrent connections
make monitor-websocket-performance
```

### Real-Time Monitoring Optimization

**Metrics Collection Optimization:**
```bash
# Analyze metrics collection performance
make analyze-metrics-performance

# Optimize metrics storage
# Review Redis usage patterns

# Test metrics collection under load
make test-metrics-load
```

**Enforcement Action Optimization:**
```bash
# Test enforcement action performance
make test-enforcement-performance

# Optimize rollback mechanisms
# Review src/verification/rollback/

# Monitor enforcement action latency
make monitor-enforcement-latency
```

## Advanced Usage

### Custom Reliability Metrics

**Implementing Custom Metrics:**
```python
# Add to src/ares/verification/
class CustomReliabilityMetric:
    def calculate_score(self, agent_data):
        # Custom scoring logic
        pass
```

**Testing Custom Metrics:**
```bash
# Create custom tests
# tests/reliability/test_custom_metrics.py

pytest tests/reliability/test_custom_metrics.py -v
```

### Advanced Agent Monitoring

**Custom Agent Behavior Patterns:**
```python
# src/ares/verification/agent_behavior_monitor.py
class CustomBehaviorPattern:
    def analyze_pattern(self, agent_history):
        # Custom pattern analysis
        pass
```

**Real-Time Alert Configuration:**
```python
# src/ares/verification/alert_manager.py
class CustomAlertRule:
    def should_alert(self, reliability_score):
        # Custom alert logic
        return reliability_score < 0.8
```

### CI/CD Customization

**Custom CI Commands:**
```makefile
# Add to Makefile
ci-check-ares: env-check
	@echo "🔍 Running ARES specific CI checks"
	$(MAKE) quality-gates
	$(MAKE) test-reliability
	$(MAKE) agents-health
	$(MAKE) test-proof-work
```

**Performance Monitoring:**
```bash
# Continuous performance monitoring
make monitor-reliability-performance &

# Alert on performance degradation
make setup-reliability-alerts
```

## Integration with MCP Ecosystem

### MCP Server Testing

**14-Server Ecosystem Validation:**
```bash
# Test MCP server connectivity
make mcp-test
make mcp-status

# Test specific MCP servers
uv run ares mcp test --server postgresql
uv run ares mcp test --server sqlite
uv run ares mcp test --server playwright
```

**MCP Integration Patterns:**
```bash
# Test database operations via MCP
make test-mcp-database

# Test web automation via MCP
make test-mcp-playwright

# Test search operations via MCP
make test-mcp-ripgrep
```

## Best Practices

### Development Best Practices

1. **Always start with environment validation**: `make env-check`
2. **Test reliability features regularly**: `make test-reliability`
3. **Monitor WebSocket performance**: `make test-websocket-latency`
4. **Validate proof-of-work systems**: `make test-proof-work`
5. **Check agent health continuously**: `make agents-health`

### CI/CD Best Practices

1. **Use pragmatic CI for regular development**: `make ci-check`
2. **Full CI for releases and merges**: `make ci-check-full`
3. **Test reliability under load**: Regular performance validation
4. **Monitor real-time systems**: WebSocket and metrics performance
5. **Validate enforcement mechanisms**: Rollback and recovery testing

### Agent Reliability Best Practices

1. **Test reliability metrics in isolation**: Unit tests for scoring algorithms
2. **Validate real-time monitoring**: WebSocket performance under load
3. **Test enforcement actions**: Rollback and recovery mechanisms
4. **Monitor system health**: Continuous health checks and alerts
5. **Document reliability criteria**: Clear reliability standards and thresholds

---

*For additional help, see the [Cross-Project CI/CD Best Practices Guide](../workspace-infrastructure/docs/CROSS_PROJECT_CICD_BEST_PRACTICES_GUIDE.md)*
