# ARES Quick Start Guide

Get up and running with ARES (Agent Reliability Enforcement System) in minutes. This guide covers installation, basic configuration, and your first verification tasks.

## 🚀 Overview

ARES provides comprehensive agent reliability monitoring through:
- **Task Completion Verification** - Validate agent task completion
- **Tool Call Validation** - Ensure proper MCP tool usage
- **Proof-of-Work Collection** - Analyze work quality and evidence
- **Real-time Monitoring** - Track agent performance and reliability
- **Web Dashboard** - Visual monitoring and management interface

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Git** for repository cloning
- **SQLite** (included with Python) or **PostgreSQL** for production
- **Redis** (optional, for caching and real-time features)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ares.git
cd ares
```

### 2. Install Dependencies

Using UV (recommended):
```bash
# Install UV if you don't have it
pip install uv

# Install all dependencies
uv sync --all-extras
```

Using pip:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[all]"
```

### 3. Initialize Database

```bash
# Initialize SQLite database (development)
uv run alembic upgrade head

# Or for PostgreSQL (production)
DATABASE_URL=postgresql://user:pass@localhost/ares uv run alembic upgrade head  # pragma: allowlist secret
```

### 4. Verify Installation

```bash
# Check ARES CLI
uv run ares version

# Test database connection
uv run ares config test-db

# Check system status
uv run ares status
```

Expected output:
```
🤖 ARES - Agent Reliability Enforcement System
Version: 1.0.0-alpha
Build: Development
Python: 3.11+

✅ Database connection successful

🚀 ARES System Status:
  Core Components:
    ✅ CompletionVerifier - Ready
    ✅ ToolCallValidator - Ready
    ✅ ProofOfWorkCollector - Ready
```

## ⚙️ Basic Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./ares.db
# DATABASE_URL=postgresql://user:pass@localhost/ares  # For PostgreSQL  # pragma: allowlist secret

# Debug Mode
DEBUG=true

# API Configuration
API_HOST=localhost
API_PORT=8000

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Evidence Storage
EVIDENCE_STORAGE_PATH=./evidence_storage

# Quality Thresholds
DEFAULT_QUALITY_THRESHOLD=0.8
SECURITY_THRESHOLD=0.85
PERFORMANCE_THRESHOLD_MS=1000
```

### 2. Configuration File

Create `config/ares.yaml`:

```yaml
# ARES Configuration
system:
  debug: true
  log_level: INFO

database:
  url: sqlite:///./ares.db
  echo_queries: false

verification:
  quality_thresholds:
    code_quality_min: 0.8
    test_coverage_min: 0.9
    performance_threshold: 1000
    security_score_min: 0.85

  strategies:
    enable_output_quality: true
    enable_requirements_matching: true
    enable_performance_verification: true
    enable_security_compliance: true

dashboard:
  refresh_interval_seconds: 30
  max_activity_records: 100
  enable_real_time_updates: true

mcp_server:
  host: localhost
  port: 8001
  enable_tools: true
```

## 🎯 Your First Verification

Let's verify a simple task completion:

### 1. Create Evidence File

Create `examples/evidence.json`:

```json
{
  "outputs": {
    "files_created": [
      {
        "path": "hello.py",
        "size": 156,
        "lines": 8,
        "complexity": 0.1,
        "has_docs": true,
        "follows_style": true,
        "has_tests": false
      }
    ],
    "completeness_score": 0.9,
    "accuracy_score": 0.95,
    "format_compliance": true,
    "error_handling_score": 0.8
  },
  "tool_calls": [
    {
      "tool_name": "write_file",
      "parameters": {
        "path": "hello.py",
        "content": "print('Hello, ARES!')"
      },
      "duration_ms": 50,
      "success": true,
      "appropriate": true,
      "efficient": true
    }
  ],
  "performance_metrics": {
    "execution_time_ms": 250,
    "memory_usage_mb": 12,
    "error_rate": 0.0,
    "cpu_usage_percent": 5
  }
}
```

### 2. Run Task Verification

```bash
uv run ares verify task \
  --agent-id "agent_001" \
  --task-id "task_hello_world" \
  --description "Create a simple Hello World Python script" \
  --evidence-file examples/evidence.json
```

Expected output:
```
✅ Task Verification Result
Status: COMPLETED
Agent: agent_001
Task: task_hello_world
Message: Task completed successfully with all quality standards met.

📊 Quality Metrics:
  Overall Score: 0.87
  Output Quality: 0.92
  Requirements Match: 0.90
  Performance: 0.95
  Security: 0.85

🔍 Evidence: 3 pieces collected
  • output_analysis: 0.95 confidence
  • tool_usage: 0.98 confidence
  • performance_metrics: 0.92 confidence
```

### 3. Validate Tool Call

```bash
uv run ares validate tool-call \
  --agent-id "agent_001" \
  --tool-name "write_file" \
  --parameters '{"path": "hello.py", "content": "print(\"Hello!\")"}' \
  --mcp-version "1.1"
```

Expected output:
```
✅ Tool Call Validation Result
Status: VALID
Tool: write_file
Agent: agent_001
Message: Tool call validation passed all compliance checks.

📋 Compliance Metrics:
  Overall Score: 0.95
  Protocol: 1.00
  Authorization: 1.00
  Parameters: 0.98
  Security: 0.90
```

## 🌐 Web Dashboard

### 1. Start the Web Server

```bash
# Start FastAPI server with dashboard
uv run uvicorn ares.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access Dashboard

Open your browser and navigate to:
- **Main Dashboard**: http://localhost:8000/dashboard
- **Agent Monitoring**: http://localhost:8000/dashboard/agents
- **Verification Activity**: http://localhost:8000/dashboard/verification
- **Analytics**: http://localhost:8000/dashboard/analytics
- **API Documentation**: http://localhost:8000/docs

### 3. Monitor Real-time Activity

The dashboard provides real-time monitoring with:
- Live agent status updates
- Verification activity feed
- Quality score trends
- Performance metrics
- System health indicators

## 🔧 MCP Server Integration

### 1. Start MCP Server

```bash
# Start the MCP server
uv run python -m ares.mcp_server.main --host localhost --port 8001
```

### 2. Test MCP Tools

```python
import asyncio
from ares.mcp_server.client import MCPClient

async def test_mcp_tools():
    client = MCPClient("http://localhost:8001")

    # Test task completion verification
    result = await client.call_tool("verify_task_completion", {
        "agent_id": "agent_001",
        "task_id": "test_task",
        "evidence": {
            "outputs": {"status": "completed"},
            "tool_calls": [],
            "performance_metrics": {"duration": 100}
        }
    })

    print(f"Verification result: {result}")

# Run the test
asyncio.run(test_mcp_tools())
```

## 📈 Monitoring Agent Performance

### 1. Monitor Specific Agent

```bash
# Start real-time monitoring
uv run ares monitor agent --agent-id "agent_001" --duration 300 --interval 30
```

### 2. Collect Proof of Work

Create `examples/work_evidence.json`:

```json
{
  "code_outputs": {
    "files_created": [
      {
        "path": "calculator.py",
        "size": 1024,
        "lines": 45,
        "complexity": 0.6,
        "has_docs": true,
        "follows_style": true,
        "has_tests": true
      }
    ]
  },
  "tool_usage": {
    "tool_calls": [
      {
        "tool": "write_file",
        "success": true,
        "duration_ms": 120,
        "appropriate": true,
        "efficient": true
      },
      {
        "tool": "run_tests",
        "success": true,
        "duration_ms": 350,
        "appropriate": true,
        "efficient": true
      }
    ]
  },
  "performance_data": {
    "total_time": 2400,
    "memory_peak": 32,
    "cpu_avg": 15,
    "io_ops": 8
  }
}
```

```bash
uv run ares proof collect \
  --agent-id "agent_001" \
  --task-id "task_calculator" \
  --description "Implement calculator with tests" \
  --evidence-file examples/work_evidence.json \
  --complexity 3
```

Expected output:
```
🏆 Proof-of-Work Collection Result
Status: HIGH_QUALITY
Agent: agent_001
Task: task_calculator
Message: High-quality work evidence collected (score: 0.92)

🎯 Quality Assessment:
  Overall Score: 0.92
  Code Quality: 0.95
  Completeness: 0.90
  Performance: 0.88
  Innovation: 0.91
  Documentation: 0.94

📋 Evidence: 3 pieces analyzed
  • code_output: 2 items
  • tool_usage: 2 items
  • performance_metrics: 1 items
```

## 🔍 Advanced Usage

### 1. Custom Configuration

```bash
# Use custom config file
uv run ares --config config/production.yaml status

# Override specific settings
DATABASE_URL=postgresql://prod:pass@db:5432/ares uv run ares status  # pragma: allowlist secret
```

### 2. Batch Verification

Create `examples/batch_tasks.json`:

```json
[
  {
    "task_id": "task_001",
    "agent_id": "agent_001",
    "description": "Create user model",
    "evidence_file": "evidence_001.json"
  },
  {
    "task_id": "task_002",
    "agent_id": "agent_002",
    "description": "Implement API endpoints",
    "evidence_file": "evidence_002.json"
  }
]
```

```bash
# Process multiple tasks
for task in $(cat examples/batch_tasks.json | jq -r '.[] | @base64'); do
  data=$(echo $task | base64 -d)
  task_id=$(echo $data | jq -r '.task_id')
  agent_id=$(echo $data | jq -r '.agent_id')
  description=$(echo $data | jq -r '.description')
  evidence_file=$(echo $data | jq -r '.evidence_file')

  uv run ares verify task \
    --agent-id "$agent_id" \
    --task-id "$task_id" \
    --description "$description" \
    --evidence-file "examples/$evidence_file"
done
```

### 3. API Integration

```python
import httpx
import asyncio

async def verify_via_api():
    async with httpx.AsyncClient() as client:
        # Verify task completion via REST API
        response = await client.post(
            "http://localhost:8000/api/v1/verification/tasks/verify",
            json={
                "task_id": "api_task_001",
                "agent_id": "api_agent_001",
                "task_description": "API integration test",
                "completion_evidence": {
                    "outputs": {"status": "completed"},
                    "tool_calls": [],
                    "performance_metrics": {"duration": 150}
                }
            }
        )

        result = response.json()
        print(f"API Verification: {result['status']}")
        print(f"Quality Score: {result['quality_metrics']['overall_score']}")

asyncio.run(verify_via_api())
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database status
uv run ares config test-db

# Reset database
uv run alembic downgrade base
uv run alembic upgrade head
```

#### Permission Errors
```bash
# Fix file permissions
chmod +x scripts/*.sh
chmod -R 755 evidence_storage/
```

#### Missing Dependencies
```bash
# Reinstall all dependencies
uv sync --all-extras --force

# Check for missing system dependencies
uv run python -c "import sys; print(sys.version)"
```

#### Port Conflicts
```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
uv run uvicorn ares.main:app --port 8080
```

### Getting Help

- **CLI Help**: `uv run ares --help`
- **Command Help**: `uv run ares verify --help`
- **Configuration**: Check `config/ares.yaml`
- **Logs**: Check `logs/ares.log`
- **Issues**: [GitHub Issues](https://github.com/your-org/ares/issues)

## 🎉 Next Steps

Now that you have ARES running:

1. **[Explore the Dashboard](dashboard.md)** - Learn about web interface features
2. **[CLI Reference](cli-usage.md)** - Complete command-line guide
3. **[API Documentation](../api/)** - Integrate with your applications
4. **[Configuration Guide](configuration.md)** - Customize for your needs
5. **[Architecture Overview](../development/architecture.md)** - Understand the system design

## 📚 Additional Resources

- **[API Reference](../api/verification.md)** - Complete API documentation
- **[Component Guide](../components/)** - Detailed component documentation
- **[Development Setup](../development/setup.md)** - Set up development environment
- **[Deployment Guide](../development/deployment.md)** - Production deployment
- **[Testing Guide](../development/testing.md)** - Testing strategies and tools

---

*Quick Start Guide - Version 1.0.0*
*Last Updated: January 15, 2024*

Need help? Check our [troubleshooting guide](troubleshooting.md) or [open an issue](https://github.com/your-org/ares/issues).
