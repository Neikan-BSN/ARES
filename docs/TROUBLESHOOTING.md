# ARES Troubleshooting Guide

This guide provides solutions for common issues encountered when developing, deploying, and operating ARES (Agent Reliability Enforcement System).

## 🚨 Quick Diagnostics

### System Health Check
```bash
# Run comprehensive system health check
uv run ares healthcheck

# Check individual components
docker compose ps
docker compose logs ares-app --tail 50
curl http://localhost:8000/health
```

### Common Issues at a Glance

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| API returns 503 | Database connection failed | Check PostgreSQL container |
| WebSocket disconnects | Redis connection issues | Restart Redis container |
| Agent tasks timeout | MCP server unavailable | Test MCP server connections |
| High memory usage | Cache overflow | Clear Redis cache |
| Slow API responses | Database query inefficiency | Check query execution plans |

## 🔧 Installation and Setup Issues

### UV Package Manager Problems

#### Issue: `uv: command not found`
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Verify installation
uv --version
```

#### Issue: `uv sync` fails with dependency conflicts
```bash
# Clear UV cache
uv cache clean

# Reinstall with specific Python version
uv sync --python 3.11

# Install with all extras
uv sync --all-extras --verbose
```

### Docker Container Issues

#### Issue: Containers fail to start
```bash
# Check container logs
docker compose logs postgres
docker compose logs redis
docker compose logs ares-app

# Restart with fresh volumes
docker compose down -v
docker compose up -d
```

#### Issue: Port conflicts
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :5432

# Change ports in docker-compose.yml
# postgres: "5433:5432"
# ares-app: "8001:8000"
```

### Database Migration Problems

#### Issue: Alembic migration fails
```bash
# Check current migration status
uv run alembic current

# Reset to base and reapply
uv run alembic downgrade base
uv run alembic upgrade head

# Create new migration if schema changed
uv run alembic revision --autogenerate -m "Fix schema issues"
```

#### Issue: Database connection refused
```bash
# Check PostgreSQL container status
docker compose ps postgres

# Test direct connection
docker compose exec postgres psql -U postgres -d ares_dev -c "SELECT version();"

# Check connection string in environment
echo $DATABASE_URL
```

## 🤖 Agent Coordination Issues

### Agent Registration Problems

#### Issue: Agent fails to register
```bash
# Check agent registration endpoint
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "test-agent", "capabilities": ["testing"]}'

# Verify agent appears in database
docker compose exec postgres psql -U postgres -d ares_dev \
  -c "SELECT name, status FROM agents;"
```

#### Issue: Agent shows as inactive
**Symptoms**: Agent registered but status remains 'inactive'
**Diagnosis**:
```bash
# Check agent heartbeat
curl http://localhost:8000/api/v1/agents/{agent_id}/status

# Review agent logs
docker compose logs ares-app | grep "agent_heartbeat"

# Verify MCP server connections
uv run ares mcp test --server filesystem
```

**Solution**:
```python
# Ensure agent sends regular heartbeats
import asyncio
from ares.agents import AgentClient

async def maintain_heartbeat():
    client = AgentClient("your-agent-name")
    while True:
        await client.send_heartbeat()
        await asyncio.sleep(30)
```

### Task Delegation Issues

#### Issue: Tasks not reaching specialized agents
**Symptoms**: @tech-lead-orchestrator doesn't delegate to specialized agents
**Diagnosis**:
```bash
# Check agent routing configuration
curl http://localhost:8000/api/v1/agents | jq '.[] | {name, capabilities, status}'

# Verify agent capability mapping
docker compose exec postgres psql -U postgres -d ares_dev \
  -c "SELECT name, capabilities FROM agents WHERE status = 'active';"
```

**Solution**:
1. Ensure agents are registered with correct capabilities
2. Verify agent routing rules in `src/ares/coordination/router.py`
3. Check agent availability and load balancing

#### Issue: Agent handoff failures
**Symptoms**: Tasks fail during agent-to-agent handoff
**Diagnosis**:
```bash
# Check handoff logs
docker compose logs ares-app | grep "agent_handoff"

# Verify task state transitions
curl http://localhost:8000/api/v1/tasks/{task_id}/history
```

**Solution**:
```python
# Implement proper handoff error handling
class AgentHandoffManager:
    async def handoff_task(self, from_agent: str, to_agent: str, task: Task):
        try:
            # Create handoff context
            context = await self.create_handoff_context(task)

            # Transfer task with retry logic
            result = await self.transfer_with_retry(to_agent, context)

            # Verify successful handoff
            await self.verify_handoff(result)

        except HandoffError as e:
            # Rollback to previous agent
            await self.rollback_handoff(from_agent, task)
            raise
```

## 🗄️ Database and Performance Issues

### Connection Pool Exhaustion

#### Issue: "Too many connections" error
**Symptoms**: Database queries fail with connection pool errors
**Diagnosis**:
```bash
# Check current connections
docker compose exec postgres psql -U postgres -d ares_dev \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool settings
docker compose exec postgres psql -U postgres -d ares_dev \
  -c "SHOW max_connections;"
```

**Solution**:
```python
# Adjust connection pool settings in config
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}

# Use connection pooling properly
async def get_db_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Slow Query Performance

#### Issue: API responses are slow (>1s)
**Diagnosis**:
```sql
-- Check slow queries in PostgreSQL
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check query execution plans
EXPLAIN ANALYZE SELECT * FROM reliability_metrics
WHERE agent_id = 'uuid'
ORDER BY recorded_at DESC
LIMIT 100;
```

**Solution**:
```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_reliability_metrics_agent_time
ON reliability_metrics(agent_id, recorded_at DESC);

CREATE INDEX CONCURRENTLY idx_tasks_status_created
ON tasks(status, created_at DESC)
WHERE status IN ('pending', 'in_progress');
```

### Memory Usage Issues

#### Issue: High memory consumption
**Diagnosis**:
```bash
# Check container memory usage
docker stats ares-app

# Check Python memory usage
docker compose exec ares-app python -m memory_profiler your_script.py

# Monitor Redis memory usage
docker compose exec redis redis-cli info memory
```

**Solution**:
```python
# Implement proper pagination
class PaginatedQuery:
    def __init__(self, page_size: int = 100):
        self.page_size = page_size

    async def get_paginated_results(
        self,
        query,
        page: int = 1
    ) -> PaginatedResult:
        offset = (page - 1) * self.page_size

        # Add pagination to query
        paginated_query = query.offset(offset).limit(self.page_size)

        results = await session.execute(paginated_query)
        total_count = await session.execute(
            select(func.count()).select_from(query.subquery())
        )

        return PaginatedResult(
            items=results.scalars().all(),
            total=total_count.scalar(),
            page=page,
            page_size=self.page_size
        )
```

## 🌐 MCP Server Integration Issues

### Connection Problems

#### Issue: MCP server connection failures
**Symptoms**: "MCP server unreachable" errors
**Diagnosis**:
```bash
# Test individual MCP servers
uv run ares mcp test --server postgresql
uv run ares mcp test --server sqlite
uv run ares mcp test --server filesystem

# Check MCP server configurations
cat .mcp.json

# Verify Docker network connectivity
docker compose exec ares-app ping postgres
docker compose exec ares-app curl http://localhost:8000/health
```

**Solution**:
1. **PostgreSQL MCP Server**:
```bash
# Ensure PostgreSQL is accessible
docker compose exec postgres psql -U postgres -d ares_dev -c "SELECT 1;"

# Update .mcp.json with correct connection string
{
  "postgresql": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": {
      "POSTGRES_CONNECTION_STRING": "postgresql://postgres:devpass@localhost:5433/ares_dev"  // pragma: allowlist secret
    }
  }
}
```

2. **SQLite MCP Server**:
```bash
# Verify SQLite database exists and is accessible
ls -la ares_dev.db
sqlite3 ares_dev.db ".tables"

# Update .mcp.json with correct path
{
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "./ares_dev.db"],
    "env": {}
  }
}
```

#### Issue: MCP tool execution timeouts
**Symptoms**: MCP operations timeout after 2 minutes
**Diagnosis**:
```bash
# Check MCP server responsiveness
time npx -y @modelcontextprotocol/server-sqlite ./ares_dev.db

# Monitor MCP server logs
docker compose logs ares-app | grep "mcp_server"
```

**Solution**:
```python
# Implement proper timeout handling
class MCPClientWithTimeout:
    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    async def execute_with_timeout(self, operation: Callable):
        try:
            return await asyncio.wait_for(operation(), timeout=self.timeout)
        except asyncio.TimeoutError:
            logger.error(f"MCP operation timed out after {self.timeout}s")
            raise MCPTimeoutError("Operation timed out")
```

### Tool Usage Issues

#### Issue: MCP tools return unexpected results
**Symptoms**: Database queries return empty results or errors
**Diagnosis**:
```bash
# Test MCP tools directly
npx -y @modelcontextprotocol/server-sqlite ./ares_dev.db

# Check database content
sqlite3 ares_dev.db "SELECT name FROM sqlite_master WHERE type='table';"

# Verify table schemas
sqlite3 ares_dev.db ".schema agents"
```

**Solution**:
```python
# Implement proper error handling for MCP operations
class SafeMCPClient:
    async def execute_query(self, query: str, params: List = None):
        try:
            result = await self.mcp_client.execute(query, params or [])

            # Validate result format
            if not self.validate_result(result):
                raise MCPResultError("Invalid result format")

            return result

        except Exception as e:
            logger.error(f"MCP query failed: {query}, error: {e}")

            # Attempt fallback operation
            return await self.fallback_operation(query, params)
```

## 🔄 Real-Time Features Issues

### WebSocket Connection Problems

#### Issue: WebSocket connections frequently disconnect
**Symptoms**: Dashboard shows "Connection lost" frequently
**Diagnosis**:
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/ws/system/metrics

# Monitor WebSocket logs
docker compose logs ares-app | grep "websocket"

# Check Redis pub/sub functionality
docker compose exec redis redis-cli monitor
```

**Solution**:
```python
# Implement WebSocket connection resilience
class ResilientWebSocketManager:
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
        self.retry_count = 0

    async def maintain_connection(self):
        while self.retry_count < self.max_retries:
            try:
                await self.establish_connection()
                self.retry_count = 0  # Reset on successful connection
                await self.listen_for_messages()

            except websockets.ConnectionClosed:
                self.retry_count += 1
                wait_time = min(30, 2 ** self.retry_count)
                await asyncio.sleep(wait_time)

        logger.error("Max WebSocket reconnection attempts exceeded")
```

### Cache Synchronization Issues

#### Issue: Stale data in real-time updates
**Symptoms**: Dashboard shows outdated information
**Diagnosis**:
```bash
# Check Redis cache consistency
docker compose exec redis redis-cli keys "status:agent:*"
docker compose exec redis redis-cli get "status:agent:code-reviewer"

# Compare with database values
docker compose exec postgres psql -U postgres -d ares_dev \
  -c "SELECT name, status, updated_at FROM agents WHERE name = 'code-reviewer';"
```

**Solution**:
```python
# Implement cache invalidation strategy
class CacheManager:
    async def invalidate_agent_cache(self, agent_id: str):
        patterns = [
            f"status:agent:{agent_id}",
            f"metrics:agent:{agent_id}",
            f"tasks:agent:{agent_id}:*"
        ]

        for pattern in patterns:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)

        # Notify WebSocket clients of cache invalidation
        await self.notify_cache_invalidation(agent_id)
```

## 🛡️ Security Issues

### Authentication Problems

#### Issue: API key authentication fails
**Symptoms**: 401 Unauthorized errors for valid API keys
**Diagnosis**:
```bash
# Test API key authentication
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/agents

# Check API key in database
docker compose exec postgres psql -U postgres -d ares_dev \
  -c "SELECT * FROM api_keys WHERE key_hash = 'hash';"
```

**Solution**:
```python
# Implement proper API key validation
class APIKeyValidator:
    async def validate_api_key(self, api_key: str) -> bool:
        # Hash the provided key
        key_hash = self.hash_api_key(api_key)

        # Check against database
        db_key = await self.get_api_key_from_db(key_hash)

        if not db_key:
            return False

        # Check expiration
        if db_key.expires_at < datetime.utcnow():
            return False

        # Update last used timestamp
        await self.update_last_used(db_key.id)

        return True
```

### SSL/TLS Certificate Issues

#### Issue: SSL certificate errors in production
**Symptoms**: HTTPS connections fail with certificate errors
**Diagnosis**:
```bash
# Check certificate validity
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Verify certificate in container
docker compose exec ares-app openssl x509 -in /etc/ssl/cert.pem -text -noout
```

**Solution**:
```yaml
# docker-compose.production.yml
services:
  ares-app:
    environment:
      - SSL_CERT_PATH=/etc/ssl/certs/server.crt
      - SSL_KEY_PATH=/etc/ssl/private/server.key
    volumes:
      - ./certs:/etc/ssl/certs:ro
      - ./private:/etc/ssl/private:ro
```

## 📊 Monitoring and Alerting Issues

### Metrics Collection Problems

#### Issue: Prometheus metrics not being exported
**Symptoms**: Grafana dashboards show no data
**Diagnosis**:
```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Verify Prometheus configuration
docker compose exec prometheus cat /etc/prometheus/prometheus.yml

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

**Solution**:
```python
# Ensure metrics are properly initialized
from prometheus_client import start_http_server, Counter, Histogram

# Initialize metrics at application startup
def initialize_metrics():
    TASK_COUNTER = Counter(
        'ares_tasks_total',
        'Total number of tasks',
        ['agent_name', 'status']
    )

    RESPONSE_TIME = Histogram(
        'ares_response_time_seconds',
        'API response time'
    )

    # Start metrics server
    start_http_server(9090)
```

### Log Analysis Issues

#### Issue: Logs are not structured or searchable
**Symptoms**: Difficult to troubleshoot issues from logs
**Solution**:
```python
# Implement structured logging
import structlog

logger = structlog.get_logger()

# Log with structured data
logger.info(
    "Agent task completed",
    agent_id="code-reviewer",
    task_id="task-123",
    duration=1.5,
    success=True,
    evidence_count=3
)
```

## 🔧 Environment-Specific Issues

### Development Environment

#### Issue: Hot reload not working
**Solution**:
```bash
# Ensure proper volume mounting
docker-compose.override.yml:
services:
  ares-app:
    volumes:
      - .:/app
      - /app/.venv  # Exclude virtual environment
    environment:
      - RELOAD=true
```

### Production Environment

#### Issue: High latency in production
**Diagnosis**:
```bash
# Check system resources
top
iostat -x 1
netstat -i

# Analyze application performance
docker stats
docker compose exec ares-app py-spy top --pid 1
```

**Solution**:
```python
# Implement production optimizations
import uvloop

# Use faster event loop
uvloop.install()

# Configure production settings
PRODUCTION_CONFIG = {
    "workers": min(32, (os.cpu_count() * 2) + 1),
    "worker_class": "uvicorn.workers.UvicornWorker",
    "max_requests": 1000,
    "max_requests_jitter": 100,
    "preload_app": True,
    "timeout": 120
}
```

## 📞 Getting Additional Help

### Enable Debug Mode
```bash
# Set debug environment variables
export ARES_DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose logging
uv run python -m ares.main --log-level debug
```

### Collect Diagnostic Information
```bash
#!/bin/bash
# diagnostic-collection.sh

echo "=== ARES Diagnostic Information ==="
echo "Date: $(date)"
echo "System: $(uname -a)"
echo ""

echo "=== Docker Information ==="
docker --version
docker compose --version
docker compose ps

echo "=== Container Logs ==="
docker compose logs --tail 50 ares-app
docker compose logs --tail 20 postgres
docker compose logs --tail 20 redis

echo "=== System Resources ==="
df -h
free -h
ps aux | head -20

echo "=== Network Connectivity ==="
curl -s http://localhost:8000/health | jq '.'
```

### Contact Support
If you're still experiencing issues:

1. **GitHub Issues**: [Create an issue](https://github.com/Neikan-BSN/ARES/issues) with:
   - Detailed problem description
   - Steps to reproduce
   - Error messages and logs
   - System information

2. **GitHub Discussions**: [Ask questions](https://github.com/Neikan-BSN/ARES/discussions) for:
   - Usage questions
   - Feature requests
   - General guidance

3. **Community Support**:
   - Include diagnostic information
   - Provide minimal reproducible examples
   - Be specific about your environment and use case

---

Remember: Most issues can be resolved by carefully checking logs, verifying configurations, and ensuring all dependencies are properly installed and running.
