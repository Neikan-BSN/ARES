# CLAUDE.md - ARES (Agent Reliability Enforcement System)

This file provides comprehensive guidance to Claude Code when working with the ARES (Agent Reliability Enforcement System) project. ARES is an intelligent agent reliability monitoring and enforcement framework for AI-assisted development workflows.

**Critical File Preservation Note**: The `.claude/agents/*.md` files contain sub-agent definitions that must NEVER be moved or relocated - they are required to remain in place for the sub-agent system to function properly.

## MCP Server Configuration (14 Servers)

### Available Servers
- **Core Development**: filesystem, git, memory, context7
- **Code Quality**: eslint, ripgrep
- **Database Operations**: sqlite, sqlite-secondary, postgres
- **AI/ML Capabilities**: sequential-thinking, elevenlabs
- **Web Operations**: fetch, playwright
- **Local Services**: codanna-https (SSE)

### Server Descriptions
- **filesystem**: File system operations for ARES source code and agent definitions
- **git**: Git operations for version control of agent reliability system
- **memory**: Memory operations for agent state tracking and reliability metrics
- **sqlite**: Primary database operations for agent behavior data and reliability scores
- **sqlite-secondary**: Secondary database for proof-of-work validation and audit logs
- **context7**: Context research for agent reliability patterns and best practices
- **ripgrep**: Fast code search across ARES modules and agent behavior logic
- **eslint**: Code quality checking for ARES web interface components
- **fetch**: HTTP operations for external reliability validation and agent integrations
- **sequential-thinking**: AI planning for complex reliability enforcement workflows
- **playwright**: Web automation for testing agent interfaces and reliability dashboards
- **postgres**: PostgreSQL operations for production-scale agent reliability tracking
- **elevenlabs**: Text-to-speech for agent status notifications and alerts
- **codanna-https**: Local code analysis server via SSE protocol
  - URL: https://127.0.0.1:8443/mcp/sse
  - Protocol: Server-Sent Events (SSE)
  - Dependency: Requires local codanna service running

### MCP Operations
```bash
# Install and test all 14 MCP servers
make mcp-install && make mcp-test

# Quick health check for all servers
../workspace-infrastructure/tools/coordination/mcp-coordinator status

# Comprehensive validation
../workspace-infrastructure/tools/coordination/mcp-coordinator validate --level=standard

# Export health report
../workspace-infrastructure/tools/coordination/mcp-coordinator export
```

## Project Overview

ARES is a FastAPI-based microservice system designed to monitor, validate, and enforce reliability standards for AI agents. The system provides real-time reliability scoring, task completion verification, and proof-of-work validation for multi-agent AI systems.

### Core Components

1. **CompletionVerifier** - Validates task completion against requirements
2. **ToolCallValidator** - Ensures proper MCP server tool usage
3. **TaskRollbackManager** - Handles failed task recovery
4. **ProofOfWorkCollector** - Gathers evidence of agent work quality
5. **AgentBehaviorMonitor** - Tracks agent performance patterns

## Technology Stack

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Caching**: Redis for real-time data
- **Message Queue**: Celery for background tasks
- **WebSockets**: Real-time agent status updates
- **Container**: Docker with multi-stage builds
- **MCP Integration**: 14+ MCP servers for enhanced functionality

## Agent Orchestration System

ARES implements an intelligent agent routing system with 26 specialized agents organized into 4 categories:

### **Orchestration Layer (Always Start Here)**

#### 1. Tech-Lead-Orchestrator (Primary Coordinator)
**Usage**: `@tech-lead-orchestrator [task description]`
- **Purpose**: Primary coordinator for all complex multi-step tasks
- **ARES Integration**: Agent reliability coordination and task delegation
- **MCP Tools**: SQLite operations, code quality checks, documentation
- **Key Responsibilities**:
  - Cross-agent task coordination with reliability tracking
  - Resource allocation across reliability monitoring tasks
  - Integration planning with enforcement mechanisms
  - Team coordination for ARES-wide initiatives

**Example Tasks**:
```bash
@tech-lead-orchestrator "Implement agent reliability dashboard with real-time monitoring"
@tech-lead-orchestrator "Design proof-of-work validation system for task completion"
@tech-lead-orchestrator "Create comprehensive agent behavior analysis pipeline"
```

#### 2. Project-Analyst
**Usage**: When deep project understanding is needed
- **ARES Integration**: Reliability metrics analysis and architectural assessment
- **Specialized Tasks**: ARES component dependency mapping, performance bottleneck identification

#### 3. Team-Configurator
**Usage**: For agent team setup and optimization
- **ARES Integration**: Agent reliability team configuration and routing optimization

### **Core Development Agents**

#### 4. Code-Archaeologist
**Usage**: `@code-archaeologist` for codebase exploration
- **ARES Integration**: Agent reliability pattern discovery and architectural documentation
- **MCP Tools**: Ripgrep search, filesystem operations, Git analysis
- **Key Capabilities**:
  - ARES component relationship mapping
  - Reliability metric extraction from existing code
  - Agent behavior pattern identification

#### 5. Code-Reviewer
**Usage**: For quality assurance and security validation
- **ARES Integration**: Task completion verification and agent behavior validation
- **Key Functions**:
  - Proof-of-work validation with `validate_task_completion()`
  - Agent reliability scoring and quality metrics
  - Security compliance for agent operations

#### 6. Documentation-Specialist
**Usage**: For technical documentation and knowledge synthesis
- **ARES Integration**: Agent reliability documentation and architectural guides
- **Deliverables**: API documentation, reliability scorecards, agent behavior guides

#### 7. Performance-Optimizer
**Usage**: `@performance-optimizer` for system-wide optimization
- **ARES Integration**: Agent reliability performance analysis and optimization
- **Focus Areas**: Database query optimization, Redis caching strategies, WebSocket performance

### **Universal Development Agents**

#### 8. API-Architect
**Usage**: For RESTful API design and microservice coordination
- **ARES Integration**: Agent reliability API endpoints and coordination services
- **Key Features**:
  - Agent coordination API design
  - Reliability monitoring endpoints
  - WebSocket real-time communication patterns

#### 9. Backend-Developer
**Usage**: For service implementation and business logic
- **ARES Integration**: Complete `AgentCoordinationService` with async coordination
- **Key Components**:
  - TaskRollbackManager implementation
  - Agent reliability monitoring services
  - Proof-of-work collection systems

#### 10. Frontend-Developer
**Usage**: For web interface development
- **ARES Integration**: Agent reliability dashboard with real-time updates
- **Technologies**: React/Vue with WebSocket integration

### **Specialized Framework Agents**

#### Django Framework (3 agents)
- **django-api-developer**: ARES agent reliability API endpoints
- **django-backend-expert**: Agent coordination services
- **django-orm-expert**: Reliability metrics database optimization

#### Laravel Framework (2 agents)
- **laravel-backend-expert**: Laravel-based agent reliability systems
- **laravel-eloquent-expert**: Database modeling for agent metrics

#### Rails Framework (3 agents)
- **rails-backend-expert**: Rails agent reliability implementation
- **rails-api-developer**: Agent coordination APIs
- **rails-activerecord-expert**: Performance optimization for reliability metrics

#### React Framework (3 agents)
- **react-component-architect**: Agent reliability dashboard components
- **react-nextjs-expert**: Full-stack agent monitoring applications
- **react-state-manager**: Real-time state management for agent status

#### Vue Framework (3 agents)
- **vue-component-architect**: Vue-based reliability dashboards
- **vue-nuxt-expert**: Full-stack Vue applications for agent monitoring
- **vue-state-manager**: Reactive state management for agent metrics

## ARES-Specific Agent Routing Maps

### **Agent Reliability Monitoring Tasks**

```bash
# Start with tech-lead-orchestrator for coordination
"Build comprehensive agent reliability monitoring system"
→ @tech-lead-orchestrator → analyzes requirements → routes to:
   → @api-architect (reliability API design)
   → @backend-developer (monitoring services)
   → @performance-optimizer (real-time optimization)
   → @frontend-developer (dashboard creation)
```

### **Task Completion Verification**

```bash
# Verification and validation workflows
"Implement proof-of-work validation for agent tasks"
→ @tech-lead-orchestrator → @code-reviewer → @backend-developer
   → Enhanced with task completion verification
   → Integrated with SQLite MCP tools
   → Real-time WebSocket updates
```

### **Agent Behavior Analysis**

```bash
# Deep analysis and pattern recognition
"Analyze agent behavior patterns for reliability scoring"
→ @tech-lead-orchestrator → @code-archaeologist → @performance-optimizer
   → Pattern discovery in agent operations
   → Performance bottleneck identification
   → Reliability metric optimization
```

### **Cross-Framework Integration**

```bash
# Multi-framework agent coordination
"Create agent reliability APIs across Django, Laravel, Rails"
→ @tech-lead-orchestrator → determines optimal framework agents:
   → @django-api-developer (Django implementation)
   → @laravel-backend-expert (Laravel implementation)
   → @rails-api-developer (Rails implementation)
   → All enhanced with ARES reliability features
```

## MCP Server Integration Strategy

ARES leverages 14+ MCP servers for enhanced development capabilities:

### **Database Operations (Core)**
- **SQLite**: Primary development database for agent reliability metrics
- **PostgreSQL**: Production-scale reliability data storage
- **Usage Pattern**: `mcp__sqlite__read_query`, `mcp__sqlite__write_query`

### **Code Quality Assurance**
- **ESLint**: Frontend code quality for agent dashboards
- **Python Code Checker**: Backend reliability service validation
- **Usage**: Integrated into all agent workflows for quality gates

### **Browser Automation & Testing**
- **Playwright**: End-to-end testing for agent reliability interfaces
- **Usage**: Automated testing of agent coordination workflows

### **Infrastructure & DevOps**
- **Docker**: Containerized agent reliability services
- **GitHub Actions**: CI/CD for agent reliability deployments

### **Search & Analysis**
- **Ripgrep**: Fast codebase search for agent patterns
- **AST Analysis**: Code structure analysis for reliability metrics

## Essential Development Commands

### **Environment Setup**
```bash
# FastAPI development with UV package management
uv sync --all-extras
uv run python -m ares.main

# Docker development environment
docker-compose up -d              # Start all ARES services
docker-compose logs -f ares-api   # Monitor API logs
```

### **Database Operations**
```bash
# SQLite operations for development
uv run alembic upgrade head       # Apply database migrations
uv run python -m ares.cli db-init # Initialize ARES database

# PostgreSQL for production
DATABASE_URL=postgresql://... alembic upgrade head
```

### **Agent Reliability Testing**
```bash
# Run comprehensive agent reliability tests
uv run pytest tests/agents/       # Agent-specific tests
uv run pytest tests/reliability/  # Reliability framework tests
uv run pytest tests/integration/  # Cross-agent integration tests
```

### **Code Quality & Standards**
```bash
# Code quality pipeline
uv run ruff check src/            # Fast Python linting
uv run ruff format src/           # Code formatting
# Type checking handled by Pylance in VS Code
uv run pytest --cov=src          # Test coverage
```

## Agent Coordination Patterns

### **Intelligent Task Routing**

1. **Always start with @tech-lead-orchestrator** for tasks spanning multiple components
2. **Use @project-analyst** for deep architectural analysis of ARES components
3. **Apply @code-archaeologist** for discovering agent reliability patterns
4. **Leverage @performance-optimizer** for system-wide reliability optimization

### **Quality & Reliability Workflows**

1. **Development**: Use appropriate framework agents (@django-*, @laravel-*, @rails-*)
2. **Review**: Always involve @code-reviewer for reliability validation
3. **Performance**: Apply @performance-optimizer for bottleneck identification
4. **Documentation**: Engage @documentation-specialist for technical specifications

### **Multi-Agent Coordination Examples**

#### **Complete Reliability Dashboard Development**
```bash
"Build complete agent reliability monitoring dashboard with real-time updates"
→ @tech-lead-orchestrator coordinates:
   1. @api-architect: Design reliability monitoring APIs
   2. @backend-developer: Implement agent coordination services
   3. @frontend-developer: Create real-time dashboard with WebSockets
   4. @code-reviewer: Validate implementation quality
   5. @performance-optimizer: Optimize real-time performance
   6. @documentation-specialist: Create comprehensive documentation
```

#### **Agent Behavior Analysis Pipeline**
```bash
"Implement comprehensive agent behavior analysis and scoring system"
→ @tech-lead-orchestrator routes to:
   1. @code-archaeologist: Discover existing agent patterns
   2. @backend-developer: Implement behavior tracking services
   3. @performance-optimizer: Optimize pattern recognition algorithms
   4. @code-reviewer: Validate scoring algorithm accuracy
```

#### **Cross-Framework Agent Implementation**
```bash
"Create agent reliability APIs for Django, Laravel, and Rails frameworks"
→ @tech-lead-orchestrator coordinates parallel development:
   1. @django-api-developer: Django implementation with ARES integration
   2. @laravel-backend-expert: Laravel implementation with reliability features
   3. @rails-api-developer: Rails implementation with monitoring capabilities
   4. @api-architect: Ensure consistent API design across frameworks
   5. @code-reviewer: Validate implementation quality across all frameworks
```

## ARES-Specific Quality Standards

### **Agent Reliability Requirements**

1. **Task Completion Verification**: All agents must provide proof-of-work evidence
2. **MCP Tool Usage Tracking**: Monitor and validate proper tool utilization
3. **Quality Scoring**: Maintain >80% reliability scores for all agent operations
4. **Real-time Monitoring**: WebSocket updates for all agent status changes
5. **Error Recovery**: Implement TaskRollbackManager for failed operations

### **Code Quality Framework**

- **Language Standards**: Python 3.11+ with type hints (enforced by Pylance) and SQLAlchemy 2.0
- **API Standards**: FastAPI with Pydantic models and dependency injection
- **Testing**: pytest with >90% coverage for agent reliability components
- **Documentation**: Comprehensive API documentation with reliability metrics
- **Security**: Input validation and agent operation sanitization

### **Performance Standards**

- **Response Time**: Agent coordination APIs <200ms average response
- **Real-time Updates**: WebSocket latency <50ms for agent status changes
- **Database Performance**: SQLite queries optimized for <10ms execution
- **Caching Strategy**: Redis caching for frequently accessed agent metrics

## Project Structure

```
ARES/
├── src/ares/              # Main application code
│   ├── api/              # FastAPI endpoints and routers
│   ├── core/             # Core reliability enforcement components
│   ├── models/           # SQLAlchemy models for agent data
│   ├── services/         # Business logic and agent coordination
│   ├── schemas/          # Pydantic models for API validation
│   └── utils/            # Utility functions and helpers
├── tests/                # Comprehensive test suites
│   ├── agents/          # Agent-specific reliability tests
│   ├── integration/     # Cross-component integration tests
│   └── reliability/     # Reliability framework validation tests
├── .claude/agents/       # 26 specialized AI agents for development
│   ├── orchestrators/   # Primary coordination agents
│   ├── core/           # Core development agents
│   ├── universal/      # Framework-agnostic agents
│   └── specialized/    # Framework-specific agents
├── scripts/             # Deployment and maintenance scripts
├── docker/              # Docker configuration and compose files
├── docs/               # Technical documentation and guides
└── alembic/            # Database migration scripts
```

## Development Workflow

### **Feature Development with Agent Coordination**

1. **Planning**: @tech-lead-orchestrator breaks down requirements and assigns specialists
2. **Analysis**: @project-analyst or @code-archaeologist provides architectural context
3. **Implementation**: Domain-appropriate specialists (@api-architect, @backend-developer)
4. **Quality**: @code-reviewer ensures reliability standards compliance
5. **Performance**: @performance-optimizer validates system performance
6. **Documentation**: @documentation-specialist creates technical specifications
7. **Testing**: MCP-powered comprehensive testing with reliability validation

### **Agent Reliability Monitoring Workflow**

1. **Architecture**: @tech-lead-orchestrator + @api-architect design monitoring systems
2. **Implementation**: @backend-developer implements reliability services
3. **Dashboard**: @frontend-developer creates real-time monitoring interfaces
4. **Optimization**: @performance-optimizer ensures efficient real-time operations
5. **Validation**: @code-reviewer validates reliability measurement accuracy
6. **Documentation**: Complete reliability monitoring documentation

## Key Features

### **Real-time Agent Monitoring**
- WebSocket-based agent status updates
- Live reliability scoring and metrics display
- Real-time task completion tracking
- Agent behavior pattern visualization

### **Proof-of-Work Validation**
- Task completion evidence collection
- Quality scoring based on implementation standards
- MCP tool usage verification and tracking
- Comprehensive audit trails for agent operations

### **Agent Coordination Services**
- Multi-agent task delegation and coordination
- Intelligent agent routing based on capabilities
- Cross-agent communication and handoff protocols
- Failure recovery and task rollback mechanisms

### **Reliability Enforcement**
- Automated quality gate enforcement
- Real-time reliability threshold monitoring
- Proactive intervention for failing agents
- Comprehensive reliability reporting and analytics

---

## Complete Command Reference

### Environment Management

```bash
# Development setup
uv sync --all-extras              # Install all dependencies including dev tools
docker compose up -d postgres redis  # Start core services
uv run alembic upgrade head       # Apply database migrations
uv run python -m ares.main       # Start ARES server

# Production setup
docker compose up -d              # Start all services including monitoring
docker compose logs -f ares-app  # View application logs
docker compose exec ares-app uv run alembic upgrade head  # Run migrations in container
```

### Database Operations

```bash
# Migration management
uv run alembic revision --autogenerate -m "Description"  # Create new migration
uv run alembic upgrade head       # Apply migrations
uv run alembic downgrade -1       # Rollback one migration
uv run alembic history            # View migration history

# Database inspection
uv run python -c "from src.ares.models.base import Base; print([t.name for t in Base.metadata.tables.values()])"
```

### Testing and Quality

```bash
# Test execution
uv run pytest                     # Run all tests
uv run pytest tests/unit/         # Unit tests only
uv run pytest tests/integration/  # Integration tests only
uv run pytest --cov=src/ares --cov-report=html  # Coverage report
uv run pytest -k "test_agent"     # Run specific test patterns

# Code quality
uv run ruff check                 # Lint code
uv run ruff format                # Format code
# Type checking handled by Pylance in VS Code
uv run bandit -r src/             # Security scan
```

### Agent Operations

```bash
# Agent monitoring
uv run ares status                           # System status
uv run ares agents list                      # List all monitored agents
uv run ares agents metrics --agent code-reviewer  # Agent-specific metrics
uv run ares tasks active                     # View active tasks
uv run ares reliability report               # Generate reliability report

# MCP server management
uv run ares mcp list                         # List available MCP servers
uv run ares mcp test --server postgresql     # Test MCP server connection
uv run ares mcp reload                       # Reload MCP server configurations
```

### Debugging and Troubleshooting

```bash
# Log analysis
docker compose logs -f ares-app              # Application logs
docker compose logs -f ares-postgres         # Database logs
docker compose logs -f ares-redis           # Cache logs

# Health checks
curl http://localhost:8000/health            # API health check
curl http://localhost:8000/metrics           # Prometheus metrics
uv run ares healthcheck                      # Comprehensive system check

# Database troubleshooting
docker compose exec ares-postgres psql -U postgres -d ares_dev -c "SELECT * FROM agents LIMIT 5;"
docker compose exec ares-redis redis-cli ping
```

## Architecture Deep Dive

### Database Schema

```sql
-- Core agent tracking
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    capabilities JSONB,
    status agent_status_enum,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reliability metrics
CREATE TABLE reliability_metrics (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    success_rate FLOAT,
    response_time_avg FLOAT,
    task_completion_rate FLOAT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enforcement actions
CREATE TABLE enforcement_actions (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    action_type enforcement_action_enum,
    reason TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- MCP connections
CREATE TABLE mcp_connections (
    id UUID PRIMARY KEY,
    server_name VARCHAR(255) NOT NULL,
    connection_status connection_status_enum,
    last_ping TIMESTAMP WITH TIME ZONE
);
```

### API Endpoints

#### Agent Management
- `GET /agents` - List all agents with status
- `GET /agents/{agent_id}` - Get specific agent details
- `POST /agents/{agent_id}/tasks` - Create new agent task
- `GET /agents/{agent_id}/metrics` - Get agent reliability metrics
- `POST /agents/{agent_id}/verify` - Verify task completion

#### Reliability Monitoring
- `GET /metrics` - System-wide reliability metrics
- `GET /metrics/agents/{agent_id}` - Agent-specific metrics
- `POST /enforcement/trigger` - Manual enforcement action
- `GET /reports/reliability` - Generate reliability report

#### MCP Integration
- `GET /mcp/servers` - List available MCP servers
- `POST /mcp/servers/{server}/test` - Test MCP server connection
- `GET /mcp/tools` - List available tools across servers

### File Structure & Entry Points

```
src/ares/
├── main.py                  # FastAPI application entry point
├── api/                     # REST API routes and handlers
│   ├── routes/
│   │   ├── agents.py        # Agent management endpoints
│   │   ├── enforcement.py   # Enforcement action endpoints
│   │   └── health.py        # Health check endpoints
├── core/                    # Core business logic
│   └── config.py            # Configuration management
├── models/                  # SQLAlchemy database models
│   ├── agent.py             # Agent model and schemas
│   ├── reliability.py       # Reliability metrics model
│   └── enforcement.py       # Enforcement action model
├── verification/            # Task verification components
│   ├── completion/          # Task completion verification
│   ├── proof_of_work/      # Evidence collection and validation
│   ├── tool_validation/    # MCP tool usage validation
│   └── rollback/           # Task rollback management
├── mcp_server/             # MCP integration layer
│   ├── client.py           # MCP client implementation
│   └── server.py           # MCP server implementation
└── dashboard/              # Web dashboard components
    ├── router.py           # Dashboard routes
    └── templates/          # HTML templates
```

### Integration Patterns

#### MCP Server Usage
```python
# Typical MCP integration pattern
from ares.mcp_server.client import MCPClient

async def verify_with_mcp(task_data: dict) -> bool:
    async with MCPClient("postgresql") as client:
        # Store task evidence
        await client.execute_query(
            "INSERT INTO task_evidence (task_id, evidence) VALUES ($1, $2)",
            [task_data["id"], task_data["evidence"]]
        )

        # Validate with SQLite for caching
        async with MCPClient("sqlite") as cache_client:
            result = await cache_client.read_query(
                "SELECT * FROM validation_cache WHERE task_id = ?",
                [task_data["id"]]
            )
            return result is not None
```

#### Agent Monitoring Pattern
```python
# Real-time agent tracking
from ares.verification.completion.verifier import CompletionVerifier

verifier = CompletionVerifier()

@agent_task_handler
async def track_agent_task(agent_name: str, task_description: str):
    async with verifier.track_task(agent_name, task_description) as tracker:
        # Agent executes task
        result = await agent.execute_task()

        # Verify completion
        verification = await tracker.verify_completion(result)

        if not verification.success:
            # Trigger enforcement action
            await enforcement_manager.trigger_action(
                agent_name,
                "task_failure",
                verification.failure_reason
            )
```

## Development Best Practices

### ARES-Specific Patterns

1. **Always use agent coordination**: Start with @tech-lead-orchestrator for complex tasks
2. **Reliability-first approach**: Every feature should include reliability monitoring
3. **MCP integration**: Leverage MCP servers for data operations and external integrations
4. **Evidence-based validation**: All agent tasks must provide verifiable proof-of-work
5. **Real-time monitoring**: Implement WebSocket updates for live system visibility

### Code Quality Standards

- **Type hints required**: All functions must have proper type annotations
- **Async by default**: Use async/await for all I/O operations
- **Error handling**: Comprehensive exception handling with proper logging
- **Testing coverage**: Minimum 90% test coverage for core reliability components
- **Documentation**: All public APIs must have comprehensive docstrings

### Performance Requirements

- **Response time**: API endpoints must respond within 200ms
- **Throughput**: System must handle 1000+ concurrent agent tasks
- **Real-time updates**: WebSocket updates within 100ms of state changes
- **Database queries**: All queries must be optimized with proper indexing

### Security Considerations

- **Input validation**: All user inputs validated with Pydantic schemas
- **SQL injection prevention**: Use parameterized queries exclusively
- **Authentication**: API key or JWT-based authentication for all endpoints
- **Rate limiting**: Implement rate limiting for public endpoints
- **Audit logging**: All agent actions must be logged for compliance

## Troubleshooting Guide

### Common Issues

#### Agent Connection Problems
```bash
# Check agent registration
curl http://localhost:8000/agents | jq '.[] | select(.name=="problematic-agent")'

# Verify MCP server connectivity
uv run ares mcp test --server sqlite

# Check database connectivity
docker compose exec ares-postgres psql -U postgres -d ares_dev -c "SELECT COUNT(*) FROM agents;"
```

#### Performance Issues
```bash
# Check system resources
docker compose exec ares-app htop

# Analyze database performance
docker compose exec ares-postgres psql -U postgres -d ares_dev -c "SELECT * FROM pg_stat_activity;"

# Monitor Redis cache
docker compose exec ares-redis redis-cli info memory
```

#### Reliability Metric Anomalies
```bash
# Check recent enforcement actions
uv run ares enforcement history --limit 10

# Analyze reliability trends
uv run ares metrics trend --agent code-reviewer --days 7

# Validate proof-of-work integrity
uv run ares validation check --task-id <task_id>
```

---

**Remember**: ARES is designed to ensure AI agent reliability through comprehensive monitoring, validation, and enforcement. Always start with @tech-lead-orchestrator for complex tasks, leverage MCP server tools for enhanced functionality, and maintain high reliability standards throughout development.

## CI/CD Implementation & Testing

### Deployed CI/CD Workflows
ARES now includes a complete standardized CI/CD suite following Phase 2 deployment patterns:

**Core CI/CD Features:**
- Agent behavior testing with proof-of-work validation
- Real-time reliability monitoring pipeline
- MCP server integration testing (14-server ecosystem)
- Agent coordination performance benchmarks
- Quality gates with agent-specific metrics

### Workflow Structure
```bash
# Environment Management
make env-check          # Validate canonical UV environment
make install           # Install all dependencies with quality gates
make clean-env         # Remove non-canonical environments

# Quality Gates (4-tier validation)
make quality-gates     # Run all 4 quality gates
make quality-gate-1    # Environment & setup validation
make quality-gate-2    # Code quality & standards
make quality-gate-3    # Security validation & compliance
make quality-gate-4    # Testing & coverage validation

# Agent Reliability Testing
make test-agents       # Agent behavior validation tests
make test-reliability  # Reliability scoring and metrics
make test-proof-work   # Proof-of-work validation testing
```

### Project-Specific CI/CD Customizations

**Agent Behavior Testing:**
- CompletionVerifier validation with task evidence collection
- ToolCallValidator testing for MCP server usage verification
- TaskRollbackManager testing for failure recovery scenarios
- ProofOfWorkCollector validation for agent work quality
- AgentBehaviorMonitor performance pattern analysis

**Reliability Enforcement Testing:**
- Real-time reliability threshold monitoring
- Automated quality gate enforcement validation
- Agent coordination failure recovery testing
- WebSocket performance under agent load
- Multi-agent task delegation stress testing

**MCP Integration Validation:**
- 14-server ecosystem connectivity testing
- Database operations validation (SQLite, PostgreSQL)
- Web automation testing with Playwright
- Search and analysis tool integration (Ripgrep)
- Real-time communication performance testing

### Quality Gates Implementation

**Gate 1: Environment Validation**
- Python 3.12 standardization compliance
- UV canonical environment verification
- FastAPI and SQLAlchemy setup validation
- Redis and Celery connectivity testing

**Gate 2: Code Quality & Standards**
- Agent reliability code pattern compliance
- FastAPI endpoint standards validation
- SQLAlchemy model quality analysis
- WebSocket implementation code quality

**Gate 3: Security & Compliance**
- Agent operation security scanning
- Input validation for agent task data
- Database access control verification
- WebSocket security implementation testing

**Gate 4: Testing & Coverage**
- Agent reliability testing with >90% coverage
- Integration testing for all ARES components
- Performance testing under realistic agent loads
- End-to-end reliability enforcement validation

### Agent-Specific Testing Patterns

**Proof-of-Work Validation Testing:**
```bash
# Test task completion verification
make test-completion-verifier

# Test tool usage validation
make test-tool-validator

# Test rollback mechanisms
make test-rollback-manager

# Test evidence collection
make test-proof-collector
```

**Real-Time Monitoring Testing:**
```bash
# Test WebSocket performance
make test-websocket-latency

# Test agent status updates
make test-status-broadcasting

# Test reliability metrics
make test-metrics-collection

# Test enforcement actions
make test-enforcement-triggers
```

### Troubleshooting CI/CD Issues

**Common Agent Testing Issues:**
```bash
# Database connectivity issues
make db-init           # Initialize ARES database
make db-reset          # Reset and reinitialize

# Agent monitoring failures
make agents-status     # Check agent monitoring status
make agents-health     # Health check for reliability system

# Performance issues
make test-performance  # Run reliability performance tests
make analyze-bottlenecks # Identify monitoring bottlenecks
```

**Agent Reliability Debugging:**
- Use agent reliability logs in `/logs/reliability-*.log`
- Check WebSocket connection stability for real-time updates
- Monitor database performance for reliability metrics storage
- Validate proof-of-work evidence collection accuracy

### Performance Standards Validation

**Response Time Testing:**
- Agent coordination APIs must respond within 200ms
- WebSocket updates must deliver within 50ms
- Database queries must execute within 10ms
- Reliability calculations must complete within 100ms

**Throughput Testing:**
- System must handle 1000+ concurrent agent tasks
- Real-time monitoring for 100+ active agents
- Database must support 10,000+ reliability metric entries
- WebSocket connections must support 500+ concurrent clients

### Deployment Validation

**Pre-Deployment Checks:**
```bash
make ci-check          # Pragmatic CI validation
make ci-check-full     # Comprehensive CI with quality gates
make deployment-check  # Agent reliability deployment readiness
```

**Post-Deployment Verification:**
- Agent reliability monitoring activation
- Real-time metrics collection validation
- WebSocket performance baseline establishment
- Proof-of-work validation system testing

---

## AI ASSISTANT STRICT PROHIBITIONS

**NEVER CREATE WITHOUT EXPLICIT REQUEST:**
- Monitoring dashboards, analytics dashboards, or reporting interfaces
- Metrics collection systems or performance monitoring tools
- Features, components, or functionality not specifically requested
- "Comprehensive" error prevention frameworks or validation systems
- Complex security frameworks beyond basic input validation
- Fake user feedback, testimonials, or usage statistics
- Completion reports claiming achievements without actual implementation
- Files with inflated capabilities or non-existent functionality

**REQUIRED BEHAVIOR:**
- Only implement what is explicitly asked for
- If unsure about scope, ask before creating anything
- Focus on simple, working solutions over complex frameworks
- Admit when something hasn't been actually implemented
- Provide honest assessment of current state vs. claims

**VIOLATION EXAMPLES TO AVOID:**
- Creating quality_dashboard.html without being asked for a dashboard
- Generating fake performance metrics (e.g., "7600+ files/minute improvement")
- Building monitoring systems when asked for basic file operations
- Adding complex validation when simple checks were requested
- Creating completion reports with false achievement claims

This prohibition applies to ALL AI assistants working on this project. Focus on the specific task requested, nothing more.


---

## MCP Server Configuration

This project is configured with **Agent Orchestration Systems** MCP integration.
AI agent orchestration and routing systems with hierarchical management

### Essential MCP Servers

These servers are required for core functionality:

- **filesystem**: Essential file system operations and management
- **git**: Git version control operations and repository management
- **memory**: Core functionality
- **sequentialthinking**: Core functionality

### Recommended MCP Servers

These servers enhance project capabilities:

- **github**: github server functionality
- **redis**: Enhanced functionality
- **context7**: context7 server functionality

### Optional MCP Servers

These servers provide additional features:

- **postgresql**: postgresql server functionality
- **docker**: docker server functionality
- **code-checker**: code-checker server functionality

### Configuration Examples

```bash
# Install and configure MCP servers for this project
cd /home/user01/projects/workspace-tools
./configure-mcp.sh

# Select this project and choose recommended servers
# Project type: Agent Orchestration Systems
```

```bash
# Required environment variables:
export MEMORY_STORE_PATH="your_project_root/data/orchestration_memory"
export MEMORY_MAX_SIZE="5000000"
export MEMORY_PERSIST="true"
export HIERARCHICAL="true"
export THINKING_DEPTH="10"
export CONTEXT_RETENTION="true"
export BRANCH_TRACKING="true"
export REDIS_URL="your_redis_url"
export REDIS_DB="your_redis_db"
export KEY_PREFIX="your_project_name_orchestration:"
```

### Usage Patterns

```bash
# General Operations
"Perform file system operations safely"
"Manage Git repository with version control"
"Execute development workflows and testing"
```

### Troubleshooting

#### Common Issues

**MCP Server Connection Issues:**
```bash
# Check server status
cd /home/user01/projects/workspace-tools
./configure-mcp.sh --test-connection

# Restart problematic servers
./configure-mcp.sh --restart-servers
```

**Environment Variable Issues:**
```bash
# Verify environment setup
echo $CLAUDE_CONFIG_PATH
cat ~/.claude.json | jq '.mcpServers'

# Reload configuration
source ~/.bashrc
./configure-mcp.sh --reload-config
```

**WSL-Specific Issues:**
```bash
# Check WSL interoperability
wsl.exe --version

# Verify Node.js access
which node && node --version
which npm && npm --version
```
