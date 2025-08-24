"""Agent Registry for managing and tracking all ARES agents."""

import logging
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import select

from ..models.base import get_async_session
from ..models.project_tracking import AgentActivity

logger = logging.getLogger(__name__)


class AgentCapability(BaseModel):
    """Represents an agent capability."""

    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    proficiency_level: int = Field(
        ..., ge=1, le=10, description="Proficiency level 1-10"
    )
    category: str = Field(..., description="Capability category")


class AgentMetrics(BaseModel):
    """Agent performance metrics."""

    reliability_score: float = Field(default=0.0, ge=0.0, le=100.0)
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_completion_time: float | None = Field(default=None)
    total_tasks_completed: int = Field(default=0, ge=0)
    current_workload: int = Field(default=0, ge=0)
    last_activity: datetime | None = Field(default=None)


class AgentStatus(BaseModel):
    """Agent status information."""

    status: str = Field(default="available")  # available, busy, offline, maintenance
    current_task: str | None = Field(default=None)
    workload_percentage: int = Field(default=0, ge=0, le=100)
    estimated_available_time: datetime | None = Field(default=None)


class AgentProfile(BaseModel):
    """Complete agent profile with capabilities and metrics."""

    agent_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Agent name (e.g., @tech-lead-orchestrator)")
    display_name: str = Field(..., description="Human-readable display name")
    category: str = Field(..., description="Agent category")
    role: str = Field(..., description="Primary role description")

    capabilities: list[AgentCapability] = Field(default_factory=list)
    metrics: AgentMetrics = Field(default_factory=AgentMetrics)
    status: AgentStatus = Field(default_factory=AgentStatus)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Agent coordination settings
    max_concurrent_tasks: int = Field(default=3, ge=1, le=10)
    priority_level: str = Field(default="medium")  # critical, high, medium, low
    collaboration_preferences: list[str] = Field(default_factory=list)
    specialization_tags: list[str] = Field(default_factory=list)


class AgentRegistry:
    """Central registry for managing all ARES agents."""

    def __init__(self):
        self.agents: dict[str, AgentProfile] = {}
        self.capabilities_index: dict[str, set[str]] = {}
        self.category_index: dict[str, set[str]] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize the agent registry with all ARES agents."""
        if self._initialized:
            return

        logger.info("Initializing ARES Agent Registry...")

        # Initialize all 26 ARES agents
        await self._register_orchestration_agents()
        await self._register_core_development_agents()
        await self._register_universal_agents()
        await self._register_framework_specialists()

        # Build capability and category indexes
        await self._build_indexes()

        # Load metrics from database
        await self._load_agent_metrics()

        self._initialized = True
        logger.info(f"Agent Registry initialized with {len(self.agents)} agents")

    async def _register_orchestration_agents(self):
        """Register orchestration layer agents."""

        # Tech Lead Orchestrator
        tech_lead = AgentProfile(
            name="@tech-lead-orchestrator",
            display_name="Tech Lead Orchestrator",
            category="orchestration",
            role="Primary coordinator for complex multi-step tasks",
            capabilities=[
                AgentCapability(
                    name="task_breakdown",
                    description="Break down complex tasks into manageable subtasks",
                    proficiency_level=10,
                    category="coordination",
                ),
                AgentCapability(
                    name="agent_routing",
                    description="Route tasks to optimal agents based on capabilities",
                    proficiency_level=10,
                    category="coordination",
                ),
                AgentCapability(
                    name="dependency_management",
                    description="Manage task dependencies and execution order",
                    proficiency_level=9,
                    category="coordination",
                ),
                AgentCapability(
                    name="resource_allocation",
                    description="Allocate resources across reliability monitoring tasks",
                    proficiency_level=8,
                    category="management",
                ),
            ],
            max_concurrent_tasks=5,
            priority_level="critical",
            specialization_tags=["coordination", "orchestration", "task_management"],
        )
        await self.register_agent(tech_lead)

        # Project Analyst
        project_analyst = AgentProfile(
            name="@project-analyst",
            display_name="Project Analyst",
            category="orchestration",
            role="Deep codebase analysis and project assessment",
            capabilities=[
                AgentCapability(
                    name="architectural_analysis",
                    description="Analyze system architecture and dependencies",
                    proficiency_level=9,
                    category="analysis",
                ),
                AgentCapability(
                    name="dependency_mapping",
                    description="Map and analyze project dependencies",
                    proficiency_level=8,
                    category="analysis",
                ),
                AgentCapability(
                    name="risk_assessment",
                    description="Assess project risks and mitigation strategies",
                    proficiency_level=7,
                    category="analysis",
                ),
            ],
            max_concurrent_tasks=3,
            priority_level="high",
            specialization_tags=["analysis", "architecture", "planning"],
        )
        await self.register_agent(project_analyst)

        # Team Configurator
        team_configurator = AgentProfile(
            name="@team-configurator",
            display_name="Team Configurator",
            category="orchestration",
            role="Agent team setup and optimization",
            capabilities=[
                AgentCapability(
                    name="team_optimization",
                    description="Optimize agent team configurations",
                    proficiency_level=8,
                    category="coordination",
                ),
                AgentCapability(
                    name="workflow_design",
                    description="Design efficient workflow patterns",
                    proficiency_level=7,
                    category="coordination",
                ),
            ],
            max_concurrent_tasks=2,
            priority_level="medium",
            specialization_tags=["team_management", "optimization", "workflow"],
        )
        await self.register_agent(team_configurator)

    async def _register_core_development_agents(self):
        """Register core development agents."""

        # Code Archaeologist
        code_archaeologist = AgentProfile(
            name="@code-archaeologist",
            display_name="Code Archaeologist",
            category="core_development",
            role="Codebase exploration and architectural discovery",
            capabilities=[
                AgentCapability(
                    name="pattern_discovery",
                    description="Discover patterns in existing codebase",
                    proficiency_level=9,
                    category="analysis",
                ),
                AgentCapability(
                    name="architectural_documentation",
                    description="Document system architecture and relationships",
                    proficiency_level=8,
                    category="documentation",
                ),
                AgentCapability(
                    name="legacy_analysis",
                    description="Analyze and understand legacy code systems",
                    proficiency_level=9,
                    category="analysis",
                ),
            ],
            max_concurrent_tasks=3,
            priority_level="high",
            specialization_tags=["exploration", "documentation", "analysis"],
        )
        await self.register_agent(code_archaeologist)

        # Code Reviewer
        code_reviewer = AgentProfile(
            name="@code-reviewer",
            display_name="Code Reviewer",
            category="core_development",
            role="Quality assurance and security validation",
            capabilities=[
                AgentCapability(
                    name="security_validation",
                    description="Validate code security and identify vulnerabilities",
                    proficiency_level=9,
                    category="security",
                ),
                AgentCapability(
                    name="quality_assessment",
                    description="Assess code quality and maintainability",
                    proficiency_level=9,
                    category="quality",
                ),
                AgentCapability(
                    name="standards_compliance",
                    description="Ensure compliance with coding standards",
                    proficiency_level=8,
                    category="quality",
                ),
            ],
            max_concurrent_tasks=4,
            priority_level="high",
            specialization_tags=["review", "security", "quality"],
        )
        await self.register_agent(code_reviewer)

        # Documentation Specialist
        documentation_specialist = AgentProfile(
            name="@documentation-specialist",
            display_name="Documentation Specialist",
            category="core_development",
            role="Technical documentation and knowledge synthesis",
            capabilities=[
                AgentCapability(
                    name="technical_writing",
                    description="Create comprehensive technical documentation",
                    proficiency_level=9,
                    category="documentation",
                ),
                AgentCapability(
                    name="knowledge_synthesis",
                    description="Synthesize complex information into clear documents",
                    proficiency_level=8,
                    category="documentation",
                ),
            ],
            max_concurrent_tasks=3,
            priority_level="medium",
            specialization_tags=["documentation", "writing", "synthesis"],
        )
        await self.register_agent(documentation_specialist)

        # Performance Optimizer
        performance_optimizer = AgentProfile(
            name="@performance-optimizer",
            display_name="Performance Optimizer",
            category="core_development",
            role="System-wide performance analysis and optimization",
            capabilities=[
                AgentCapability(
                    name="performance_analysis",
                    description="Analyze system performance bottlenecks",
                    proficiency_level=9,
                    category="optimization",
                ),
                AgentCapability(
                    name="database_optimization",
                    description="Optimize database queries and performance",
                    proficiency_level=8,
                    category="optimization",
                ),
                AgentCapability(
                    name="caching_strategies",
                    description="Design and implement caching strategies",
                    proficiency_level=8,
                    category="optimization",
                ),
            ],
            max_concurrent_tasks=3,
            priority_level="high",
            specialization_tags=["performance", "optimization", "analysis"],
        )
        await self.register_agent(performance_optimizer)

    async def _register_universal_agents(self):
        """Register universal development agents."""

        # API Architect
        api_architect = AgentProfile(
            name="@api-architect",
            display_name="API Architect",
            category="universal_development",
            role="RESTful API design and microservice coordination",
            capabilities=[
                AgentCapability(
                    name="api_design",
                    description="Design RESTful APIs and endpoints",
                    proficiency_level=9,
                    category="architecture",
                ),
                AgentCapability(
                    name="microservice_coordination",
                    description="Coordinate microservice architectures",
                    proficiency_level=8,
                    category="architecture",
                ),
                AgentCapability(
                    name="documentation_generation",
                    description="Generate comprehensive API documentation",
                    proficiency_level=8,
                    category="documentation",
                ),
            ],
            max_concurrent_tasks=4,
            priority_level="high",
            specialization_tags=["api", "architecture", "design"],
        )
        await self.register_agent(api_architect)

        # Backend Developer
        backend_developer = AgentProfile(
            name="@backend-developer",
            display_name="Backend Developer",
            category="universal_development",
            role="Service implementation and business logic",
            capabilities=[
                AgentCapability(
                    name="async_programming",
                    description="Implement async/await patterns and concurrency",
                    proficiency_level=9,
                    category="implementation",
                ),
                AgentCapability(
                    name="database_operations",
                    description="Design and implement database operations",
                    proficiency_level=9,
                    category="implementation",
                ),
                AgentCapability(
                    name="service_architecture",
                    description="Design and implement service architectures",
                    proficiency_level=8,
                    category="architecture",
                ),
            ],
            max_concurrent_tasks=4,
            priority_level="critical",
            specialization_tags=["backend", "implementation", "services"],
        )
        await self.register_agent(backend_developer)

        # Frontend Developer
        frontend_developer = AgentProfile(
            name="@frontend-developer",
            display_name="Frontend Developer",
            category="universal_development",
            role="Web interface and dashboard development",
            capabilities=[
                AgentCapability(
                    name="dashboard_development",
                    description="Create interactive dashboards and interfaces",
                    proficiency_level=8,
                    category="ui",
                ),
                AgentCapability(
                    name="websocket_integration",
                    description="Integrate real-time WebSocket functionality",
                    proficiency_level=7,
                    category="implementation",
                ),
                AgentCapability(
                    name="responsive_design",
                    description="Create responsive and accessible designs",
                    proficiency_level=8,
                    category="ui",
                ),
            ],
            max_concurrent_tasks=3,
            priority_level="high",
            specialization_tags=["frontend", "ui", "dashboard"],
        )
        await self.register_agent(frontend_developer)

    async def _register_framework_specialists(self):
        """Register framework specialist agents."""

        # Django Specialists
        for specialist in [
            "@django-api-developer",
            "@django-backend-expert",
            "@django-orm-expert",
        ]:
            django_agent = AgentProfile(
                name=specialist,
                display_name=specialist.replace("@", "").replace("-", " ").title(),
                category="framework_specialists",
                role=f"Django framework specialist - {specialist.split('-')[-1]}",
                capabilities=[
                    AgentCapability(
                        name="django_framework",
                        description="Django framework expertise",
                        proficiency_level=9,
                        category="framework",
                    )
                ],
                max_concurrent_tasks=2,
                priority_level="medium",
                specialization_tags=["django", "python", "framework"],
            )
            await self.register_agent(django_agent)

        # Laravel Specialists
        for specialist in ["@laravel-backend-expert", "@laravel-eloquent-expert"]:
            laravel_agent = AgentProfile(
                name=specialist,
                display_name=specialist.replace("@", "").replace("-", " ").title(),
                category="framework_specialists",
                role=f"Laravel framework specialist - {specialist.split('-')[-1]}",
                capabilities=[
                    AgentCapability(
                        name="laravel_framework",
                        description="Laravel framework expertise",
                        proficiency_level=8,
                        category="framework",
                    )
                ],
                max_concurrent_tasks=2,
                priority_level="medium",
                specialization_tags=["laravel", "php", "framework"],
            )
            await self.register_agent(laravel_agent)

        # Rails Specialists
        for specialist in [
            "@rails-backend-expert",
            "@rails-api-developer",
            "@rails-activerecord-expert",
        ]:
            rails_agent = AgentProfile(
                name=specialist,
                display_name=specialist.replace("@", "").replace("-", " ").title(),
                category="framework_specialists",
                role=f"Rails framework specialist - {specialist.split('-')[-1]}",
                capabilities=[
                    AgentCapability(
                        name="rails_framework",
                        description="Ruby on Rails framework expertise",
                        proficiency_level=8,
                        category="framework",
                    )
                ],
                max_concurrent_tasks=2,
                priority_level="medium",
                specialization_tags=["rails", "ruby", "framework"],
            )
            await self.register_agent(rails_agent)

        # React Specialists
        for specialist in [
            "@react-component-architect",
            "@react-nextjs-expert",
            "@react-state-manager",
        ]:
            react_agent = AgentProfile(
                name=specialist,
                display_name=specialist.replace("@", "").replace("-", " ").title(),
                category="framework_specialists",
                role=f"React framework specialist - {specialist.split('-')[-1]}",
                capabilities=[
                    AgentCapability(
                        name="react_framework",
                        description="React framework expertise",
                        proficiency_level=8,
                        category="framework",
                    )
                ],
                max_concurrent_tasks=2,
                priority_level="medium",
                specialization_tags=["react", "javascript", "frontend"],
            )
            await self.register_agent(react_agent)

        # Vue Specialists
        for specialist in [
            "@vue-component-architect",
            "@vue-nuxt-expert",
            "@vue-state-manager",
        ]:
            vue_agent = AgentProfile(
                name=specialist,
                display_name=specialist.replace("@", "").replace("-", " ").title(),
                category="framework_specialists",
                role=f"Vue framework specialist - {specialist.split('-')[-1]}",
                capabilities=[
                    AgentCapability(
                        name="vue_framework",
                        description="Vue.js framework expertise",
                        proficiency_level=8,
                        category="framework",
                    )
                ],
                max_concurrent_tasks=2,
                priority_level="medium",
                specialization_tags=["vue", "javascript", "frontend"],
            )
            await self.register_agent(vue_agent)

    async def register_agent(self, agent: AgentProfile):
        """Register a new agent in the registry."""
        self.agents[agent.name] = agent
        logger.debug(f"Registered agent: {agent.name} ({agent.category})")

    async def _build_indexes(self):
        """Build capability and category indexes for fast lookups."""
        self.capabilities_index.clear()
        self.category_index.clear()

        for agent_name, agent in self.agents.items():
            # Build category index
            if agent.category not in self.category_index:
                self.category_index[agent.category] = set()
            self.category_index[agent.category].add(agent_name)

            # Build capabilities index
            for capability in agent.capabilities:
                if capability.name not in self.capabilities_index:
                    self.capabilities_index[capability.name] = set()
                self.capabilities_index[capability.name].add(agent_name)

    async def _load_agent_metrics(self):
        """Load agent metrics from database."""
        try:
            async with get_async_session() as session:
                # Get recent agent activities for metrics calculation
                activities_query = (
                    select(AgentActivity)
                    .where(
                        AgentActivity.timestamp >= datetime.utcnow() - timedelta(days=7)
                    )
                    .order_by(AgentActivity.timestamp.desc())
                )
                activities_result = await session.execute(activities_query)
                activities = activities_result.scalars().all()

                # Calculate metrics for each agent
                agent_activity_counts = {}
                for activity in activities:
                    agent_name = activity.agent_name
                    if agent_name not in agent_activity_counts:
                        agent_activity_counts[agent_name] = {
                            "total_activities": 0,
                            "last_activity": activity.timestamp,
                        }
                    agent_activity_counts[agent_name]["total_activities"] += 1

                # Update agent metrics
                for agent_name, activity_data in agent_activity_counts.items():
                    if agent_name in self.agents:
                        agent = self.agents[agent_name]
                        agent.metrics.total_tasks_completed = activity_data[
                            "total_activities"
                        ]
                        agent.metrics.last_activity = activity_data["last_activity"]
                        agent.metrics.reliability_score = min(
                            100.0, activity_data["total_activities"] * 10
                        )
                        agent.updated_at = datetime.utcnow()

        except Exception as e:
            logger.warning(f"Could not load agent metrics from database: {e}")

    def get_agent(self, agent_name: str) -> AgentProfile | None:
        """Get agent profile by name."""
        return self.agents.get(agent_name)

    def get_agents_by_category(self, category: str) -> list[AgentProfile]:
        """Get all agents in a specific category."""
        agent_names = self.category_index.get(category, set())
        return [self.agents[name] for name in agent_names]

    def get_agents_by_capability(self, capability: str) -> list[AgentProfile]:
        """Get all agents with a specific capability."""
        agent_names = self.capabilities_index.get(capability, set())
        return [self.agents[name] for name in agent_names]

    def get_available_agents(self) -> list[AgentProfile]:
        """Get all available agents."""
        return [
            agent
            for agent in self.agents.values()
            if agent.status.status == "available"
        ]

    def get_agents_by_priority(self, priority: str) -> list[AgentProfile]:
        """Get agents by priority level."""
        return [
            agent for agent in self.agents.values() if agent.priority_level == priority
        ]

    async def update_agent_status(
        self, agent_name: str, status: str, current_task: str | None = None
    ):
        """Update agent status."""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            agent.status.status = status
            agent.status.current_task = current_task
            agent.updated_at = datetime.utcnow()

            # Update workload based on status
            if status == "busy":
                agent.status.workload_percentage = min(
                    100, agent.status.workload_percentage + 25
                )
            elif status == "available":
                agent.status.workload_percentage = 0
                agent.status.current_task = None

    async def update_agent_metrics(self, agent_name: str, **metrics):
        """Update agent performance metrics."""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            for key, value in metrics.items():
                if hasattr(agent.metrics, key):
                    setattr(agent.metrics, key, value)
            agent.updated_at = datetime.utcnow()

    def get_registry_stats(self) -> dict:
        """Get overall registry statistics."""
        total_agents = len(self.agents)
        available_agents = len(self.get_available_agents())

        category_counts = {}
        for category, agent_names in self.category_index.items():
            category_counts[category] = len(agent_names)

        avg_reliability = sum(
            agent.metrics.reliability_score for agent in self.agents.values()
        ) / max(total_agents, 1)

        return {
            "total_agents": total_agents,
            "available_agents": available_agents,
            "busy_agents": total_agents - available_agents,
            "category_distribution": category_counts,
            "average_reliability_score": avg_reliability,
            "last_updated": datetime.utcnow(),
        }

    def search_agents(self, query: str) -> list[AgentProfile]:
        """Search agents by name, capabilities, or tags."""
        query_lower = query.lower()
        matching_agents = []

        for agent in self.agents.values():
            # Search in name and display name
            if (
                query_lower in agent.name.lower()
                or query_lower in agent.display_name.lower()
            ):
                matching_agents.append(agent)
                continue

            # Search in capabilities
            for capability in agent.capabilities:
                if (
                    query_lower in capability.name.lower()
                    or query_lower in capability.description.lower()
                ):
                    matching_agents.append(agent)
                    break

            # Search in specialization tags
            if any(query_lower in tag.lower() for tag in agent.specialization_tags):
                matching_agents.append(agent)

        return matching_agents


# Global agent registry instance
agent_registry = AgentRegistry()
