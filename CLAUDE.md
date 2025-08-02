# CLAUDE.md - ARES (Agent Reliability Enforcement System)

This file provides guidance to Claude Code when working with the ARES (Agent Reliability Enforcement System) project - an intelligent agent reliability monitoring and enforcement framework.

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
uv run mypy src/                  # Type checking
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

- **Language Standards**: Python 3.11+ with type hints and SQLAlchemy 2.0
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

**Remember**: ARES is designed to ensure AI agent reliability through comprehensive monitoring, validation, and enforcement. Always start with @tech-lead-orchestrator for complex tasks, leverage MCP server tools for enhanced functionality, and maintain high reliability standards throughout development.
