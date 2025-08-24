"""Routing Manager for intelligent agent task routing and load balancing."""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ..models.base import get_async_session
from ..models.project_tracking import ActivityType, AgentActivity
from .agent_registry import AgentRegistry
from .task_coordinator import (
    TaskCoordinator,
    TaskDefinition,
)

logger = logging.getLogger(__name__)


class RoutingStrategy(str, Enum):
    """Agent routing strategies."""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    BEST_FIT = "best_fit"
    PRIORITY_BASED = "priority_based"
    CAPABILITY_WEIGHTED = "capability_weighted"
    LEARNING_OPTIMIZED = "learning_optimized"


class LoadBalancingMode(str, Enum):
    """Load balancing modes."""

    STRICT = "strict"  # Strict load distribution
    ADAPTIVE = "adaptive"  # Adaptive based on agent performance
    CAPACITY_AWARE = "capacity_aware"  # Based on agent capacity limits
    DYNAMIC = "dynamic"  # Dynamic adjustment based on real-time metrics


class RoutingRule(BaseModel):
    """Individual routing rule definition."""

    rule_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")

    # Rule conditions
    task_patterns: list[str] = Field(default_factory=list)  # Task matching patterns
    capability_requirements: list[str] = Field(default_factory=list)
    priority_levels: list[str] = Field(default_factory=list)

    # Routing preferences
    preferred_agents: list[str] = Field(default_factory=list)
    excluded_agents: list[str] = Field(default_factory=list)
    agent_categories: list[str] = Field(default_factory=list)

    # Rule metadata
    weight: float = Field(default=1.0, ge=0.1, le=10.0)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentLoad(BaseModel):
    """Agent load tracking information."""

    agent_name: str
    current_tasks: int = Field(default=0, ge=0)
    max_capacity: int = Field(default=3, ge=1)
    utilization_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

    # Performance metrics
    avg_completion_time: float = Field(default=0.0, ge=0.0)
    success_rate: float = Field(default=100.0, ge=0.0, le=100.0)
    reliability_score: float = Field(default=100.0, ge=0.0, le=100.0)

    # Load history
    load_history: list[float] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class RoutingDecision(BaseModel):
    """Agent routing decision with reasoning."""

    task_id: UUID
    selected_agent: str
    routing_strategy: RoutingStrategy
    confidence_score: float = Field(ge=0.0, le=100.0)

    # Decision reasoning
    decision_factors: dict[str, float] = Field(default_factory=dict)
    applied_rules: list[str] = Field(default_factory=list)
    alternative_agents: list[str] = Field(default_factory=list)

    # Timing and metadata
    decision_time: datetime = Field(default_factory=datetime.utcnow)
    expected_completion_time: datetime | None = Field(default=None)
    routing_metadata: dict[str, Any] = Field(default_factory=dict)


class RoutingManager:
    """Intelligent agent routing and load balancing manager."""

    def __init__(
        self, agent_registry: AgentRegistry, task_coordinator: TaskCoordinator
    ):
        self.agent_registry = agent_registry
        self.task_coordinator = task_coordinator

        # Routing configuration
        self.default_strategy = RoutingStrategy.BEST_FIT
        self.load_balancing_mode = LoadBalancingMode.ADAPTIVE

        # Routing rules and patterns
        self.routing_rules: dict[UUID, RoutingRule] = {}
        self.agent_loads: dict[str, AgentLoad] = {}

        # Performance tracking
        self.routing_decisions: list[RoutingDecision] = []
        self.routing_performance: dict[str, dict] = {}

        # Load balancing state
        self.round_robin_counters: dict[str, int] = {}  # Per category counters
        self.last_assignments: dict[str, datetime] = {}

        # Adaptive learning
        self.routing_success_rates: dict[
            tuple[str, str], float
        ] = {}  # (agent, task_type) -> success_rate
        self.performance_history: dict[str, list[float]] = {}

    async def initialize(self):
        """Initialize the routing manager."""
        logger.info("Initializing ARES Routing Manager...")

        # Initialize agent loads
        await self._initialize_agent_loads()

        # Register default routing rules
        await self._register_default_routing_rules()

        # Start load monitoring
        asyncio.create_task(self._monitor_agent_loads())

        logger.info(f"Routing Manager initialized with {len(self.routing_rules)} rules")

    async def _initialize_agent_loads(self):
        """Initialize agent load tracking."""
        for agent_name, agent in self.agent_registry.agents.items():
            self.agent_loads[agent_name] = AgentLoad(
                agent_name=agent_name,
                max_capacity=agent.max_concurrent_tasks,
                current_tasks=0,
                utilization_percentage=0.0,
                avg_completion_time=agent.metrics.average_completion_time or 0.0,
                success_rate=agent.metrics.success_rate,
                reliability_score=agent.metrics.reliability_score,
            )

    async def _register_default_routing_rules(self):
        """Register default routing rules for ARES agents."""

        # High-priority orchestration rule
        orchestration_rule = RoutingRule(
            name="Orchestration Priority",
            description="Route complex coordination tasks to orchestration agents",
            task_patterns=["coordination", "orchestration", "management", "breakdown"],
            capability_requirements=[
                "task_breakdown",
                "agent_routing",
                "dependency_management",
            ],
            priority_levels=["critical", "high"],
            preferred_agents=["@tech-lead-orchestrator", "@project-analyst"],
            weight=5.0,
        )
        await self.register_routing_rule(orchestration_rule)

        # Code quality and review rule
        quality_rule = RoutingRule(
            name="Code Quality Routing",
            description="Route quality assurance tasks to review specialists",
            task_patterns=["review", "quality", "security", "validation", "compliance"],
            capability_requirements=[
                "security_validation",
                "quality_assessment",
                "standards_compliance",
            ],
            preferred_agents=["@code-reviewer", "@performance-optimizer"],
            agent_categories=["core_development"],
            weight=4.0,
        )
        await self.register_routing_rule(quality_rule)

        # API and backend development rule
        backend_rule = RoutingRule(
            name="Backend Development Routing",
            description="Route backend and API tasks to appropriate developers",
            task_patterns=["api", "backend", "database", "service", "async"],
            capability_requirements=[
                "api_design",
                "database_operations",
                "async_programming",
            ],
            preferred_agents=["@api-architect", "@backend-developer"],
            agent_categories=["universal_development"],
            weight=3.5,
        )
        await self.register_routing_rule(backend_rule)

        # Framework-specific routing rule
        framework_rule = RoutingRule(
            name="Framework Specialist Routing",
            description="Route framework-specific tasks to appropriate specialists",
            task_patterns=["django", "laravel", "rails", "react", "vue"],
            preferred_agents=[],  # Will be populated dynamically based on task content
            agent_categories=["framework_specialists"],
            weight=3.0,
        )
        await self.register_routing_rule(framework_rule)

        # Load balancing rule
        load_balancing_rule = RoutingRule(
            name="Load Balancing",
            description="Distribute tasks based on current agent workload",
            task_patterns=["*"],  # Apply to all tasks
            weight=2.0,
        )
        await self.register_routing_rule(load_balancing_rule)

        # Documentation and analysis rule
        documentation_rule = RoutingRule(
            name="Documentation and Analysis",
            description="Route documentation and analysis tasks to specialists",
            task_patterns=["documentation", "analysis", "exploration", "architecture"],
            capability_requirements=[
                "technical_writing",
                "pattern_discovery",
                "architectural_analysis",
            ],
            preferred_agents=["@documentation-specialist", "@code-archaeologist"],
            weight=3.0,
        )
        await self.register_routing_rule(documentation_rule)

    async def register_routing_rule(self, rule: RoutingRule):
        """Register a new routing rule."""
        self.routing_rules[rule.rule_id] = rule
        logger.debug(f"Registered routing rule: {rule.name}")

    async def route_task(
        self,
        task: TaskDefinition,
        strategy: RoutingStrategy | None = None,
        force_agent: str | None = None,
    ) -> RoutingDecision:
        """Route a task to the most appropriate agent."""

        routing_strategy = strategy or self.default_strategy

        # Force assignment if specified
        if force_agent and force_agent in self.agent_registry.agents:
            return RoutingDecision(
                task_id=task.task_id,
                selected_agent=force_agent,
                routing_strategy=routing_strategy,
                confidence_score=100.0,
                decision_factors={"forced_assignment": 100.0},
                applied_rules=["forced_assignment"],
            )

        # Apply routing strategy
        if routing_strategy == RoutingStrategy.ROUND_ROBIN:
            decision = await self._route_with_round_robin(task)
        elif routing_strategy == RoutingStrategy.LEAST_LOADED:
            decision = await self._route_with_least_loaded(task)
        elif routing_strategy == RoutingStrategy.BEST_FIT:
            decision = await self._route_with_best_fit(task)
        elif routing_strategy == RoutingStrategy.PRIORITY_BASED:
            decision = await self._route_with_priority(task)
        elif routing_strategy == RoutingStrategy.CAPABILITY_WEIGHTED:
            decision = await self._route_with_capability_weighting(task)
        elif routing_strategy == RoutingStrategy.LEARNING_OPTIMIZED:
            decision = await self._route_with_learning_optimization(task)
        else:
            decision = await self._route_with_best_fit(task)

        # Store routing decision
        self.routing_decisions.append(decision)

        # Update last assignment time
        self.last_assignments[decision.selected_agent] = datetime.utcnow()

        # Log routing decision
        await self._log_routing_decision(decision)

        logger.info(
            f"Routed task '{task.title}' to agent {decision.selected_agent} "
            f"(strategy: {routing_strategy.value}, confidence: {decision.confidence_score:.1f}%)"
        )

        return decision

    async def _route_with_round_robin(self, task: TaskDefinition) -> RoutingDecision:
        """Route task using round-robin strategy."""
        # Get available agents
        available_agents = self.agent_registry.get_available_agents()

        if not available_agents:
            raise Exception("No available agents for round-robin routing")

        # Sort agents by name for consistent ordering
        available_agents.sort(key=lambda a: a.name)

        # Get next agent in round-robin sequence
        category = "general"  # Could be determined from task
        if category not in self.round_robin_counters:
            self.round_robin_counters[category] = 0

        agent_index = self.round_robin_counters[category] % len(available_agents)
        selected_agent = available_agents[agent_index]

        # Update counter
        self.round_robin_counters[category] += 1

        return RoutingDecision(
            task_id=task.task_id,
            selected_agent=selected_agent.name,
            routing_strategy=RoutingStrategy.ROUND_ROBIN,
            confidence_score=70.0,
            decision_factors={"round_robin_selection": 70.0},
            applied_rules=["round_robin"],
            alternative_agents=[
                a.name for a in available_agents[:3] if a != selected_agent
            ],
        )

    async def _route_with_least_loaded(self, task: TaskDefinition) -> RoutingDecision:
        """Route task to least loaded agent."""
        available_agents = self.agent_registry.get_available_agents()

        if not available_agents:
            raise Exception("No available agents for least-loaded routing")

        # Find agent with lowest utilization
        least_loaded_agent = None
        lowest_utilization = float("inf")

        for agent in available_agents:
            agent_load = self.agent_loads.get(agent.name)
            if agent_load and agent_load.utilization_percentage < lowest_utilization:
                lowest_utilization = agent_load.utilization_percentage
                least_loaded_agent = agent

        if not least_loaded_agent:
            least_loaded_agent = available_agents[0]

        confidence = max(20.0, 100.0 - lowest_utilization)

        return RoutingDecision(
            task_id=task.task_id,
            selected_agent=least_loaded_agent.name,
            routing_strategy=RoutingStrategy.LEAST_LOADED,
            confidence_score=confidence,
            decision_factors={
                "load_utilization": 100.0 - lowest_utilization,
                "availability": 30.0,
            },
            applied_rules=["least_loaded"],
            alternative_agents=[
                a.name for a in available_agents[:3] if a != least_loaded_agent
            ],
        )

    async def _route_with_best_fit(self, task: TaskDefinition) -> RoutingDecision:
        """Route task using best-fit algorithm with capability matching."""
        # Get candidate agents using existing task coordinator logic
        candidate_assignments = await self.task_coordinator.find_suitable_agents(
            task, limit=10
        )

        if not candidate_assignments:
            # Fallback to any available agent
            available_agents = self.agent_registry.get_available_agents()
            if available_agents:
                selected_agent = available_agents[0]
                return RoutingDecision(
                    task_id=task.task_id,
                    selected_agent=selected_agent.name,
                    routing_strategy=RoutingStrategy.BEST_FIT,
                    confidence_score=30.0,
                    decision_factors={"fallback_assignment": 30.0},
                    applied_rules=["fallback"],
                )
            else:
                raise Exception("No available agents for best-fit routing")

        # Apply routing rules to refine selection
        best_assignment = candidate_assignments[0]
        applied_rules = []
        decision_factors = {"capability_match": best_assignment.assignment_score}

        # Apply routing rules
        for rule in self.routing_rules.values():
            if not rule.enabled:
                continue

            rule_score = await self._evaluate_routing_rule(
                rule, task, best_assignment.agent_name
            )
            if rule_score > 0:
                decision_factors[rule.name] = rule_score * rule.weight
                applied_rules.append(rule.name)

        # Calculate final confidence score
        confidence_score = min(
            100.0, sum(decision_factors.values()) / len(decision_factors)
        )

        return RoutingDecision(
            task_id=task.task_id,
            selected_agent=best_assignment.agent_name,
            routing_strategy=RoutingStrategy.BEST_FIT,
            confidence_score=confidence_score,
            decision_factors=decision_factors,
            applied_rules=applied_rules,
            alternative_agents=[a.agent_name for a in candidate_assignments[1:4]],
        )

    async def _route_with_priority(self, task: TaskDefinition) -> RoutingDecision:
        """Route task based on agent priority levels."""
        # Get agents matching task priority
        priority_agents = self.agent_registry.get_agents_by_priority(
            task.priority.value
        )
        available_priority_agents = [
            agent
            for agent in priority_agents
            if agent.name
            in [a.name for a in self.agent_registry.get_available_agents()]
        ]

        if not available_priority_agents:
            # Fallback to best-fit
            return await self._route_with_best_fit(task)

        # Select highest reliability agent from priority group
        selected_agent = max(
            available_priority_agents, key=lambda a: a.metrics.reliability_score
        )

        return RoutingDecision(
            task_id=task.task_id,
            selected_agent=selected_agent.name,
            routing_strategy=RoutingStrategy.PRIORITY_BASED,
            confidence_score=85.0,
            decision_factors={
                "priority_match": 85.0,
                "reliability_score": selected_agent.metrics.reliability_score,
            },
            applied_rules=["priority_based"],
            alternative_agents=[
                a.name for a in available_priority_agents[:3] if a != selected_agent
            ],
        )

    async def _route_with_capability_weighting(
        self, task: TaskDefinition
    ) -> RoutingDecision:
        """Route task using weighted capability matching."""
        available_agents = self.agent_registry.get_available_agents()

        if not available_agents:
            raise Exception("No available agents for capability-weighted routing")

        # Calculate weighted scores for each agent
        agent_scores = {}

        for agent in available_agents:
            score = 0.0
            total_weight = 0.0

            # Score based on task requirements
            if task.requirements:
                for requirement in task.requirements:
                    # Find matching capability
                    matching_capability = None
                    for capability in agent.capabilities:
                        if capability.name == requirement.capability:
                            matching_capability = capability
                            break

                    if matching_capability:
                        capability_score = (
                            matching_capability.proficiency_level / 10.0
                        ) * 100
                        weighted_score = capability_score * requirement.weight
                        score += weighted_score
                        total_weight += requirement.weight

            # Add load balancing factor
            agent_load = self.agent_loads.get(agent.name)
            if agent_load:
                load_factor = max(0, 100 - agent_load.utilization_percentage)
                score += load_factor * 0.3
                total_weight += 0.3

            # Add reliability factor
            reliability_factor = agent.metrics.reliability_score * 0.2
            score += reliability_factor
            total_weight += 0.2

            # Normalize score
            if total_weight > 0:
                agent_scores[agent.name] = score / total_weight
            else:
                agent_scores[agent.name] = 50.0  # Default score

        # Select agent with highest weighted score
        best_agent_name = max(agent_scores.keys(), key=lambda name: agent_scores[name])
        best_score = agent_scores[best_agent_name]

        return RoutingDecision(
            task_id=task.task_id,
            selected_agent=best_agent_name,
            routing_strategy=RoutingStrategy.CAPABILITY_WEIGHTED,
            confidence_score=min(100.0, best_score),
            decision_factors={
                "capability_weighted_score": best_score,
                "total_candidates": len(available_agents),
            },
            applied_rules=["capability_weighted"],
            alternative_agents=list(
                sorted(
                    agent_scores.keys(), key=lambda n: agent_scores[n], reverse=True
                )[1:4]
            ),
        )

    async def _route_with_learning_optimization(
        self, task: TaskDefinition
    ) -> RoutingDecision:
        """Route task using machine learning optimization."""
        # This is a simplified implementation - in production would use actual ML models

        # Start with best-fit as baseline
        baseline_decision = await self._route_with_best_fit(task)

        # Adjust based on historical performance
        task_type = self._classify_task_type(task)

        # Check historical success rates
        best_agent = baseline_decision.selected_agent
        best_success_rate = self.routing_success_rates.get(
            (best_agent, task_type), 80.0
        )

        # Look for agents with better historical performance
        for agent_name in self.agent_registry.agents.keys():
            if agent_name == best_agent:
                continue

            success_rate = self.routing_success_rates.get((agent_name, task_type), 70.0)
            if (
                success_rate > best_success_rate + 10
            ):  # Significant improvement threshold
                agent = self.agent_registry.get_agent(agent_name)
                if agent and agent.status.status == "available":
                    best_agent = agent_name
                    best_success_rate = success_rate

        return RoutingDecision(
            task_id=task.task_id,
            selected_agent=best_agent,
            routing_strategy=RoutingStrategy.LEARNING_OPTIMIZED,
            confidence_score=min(100.0, best_success_rate),
            decision_factors={
                "historical_success_rate": best_success_rate,
                "learning_optimization": 15.0,
            },
            applied_rules=["learning_optimized"],
            alternative_agents=[baseline_decision.selected_agent]
            if best_agent != baseline_decision.selected_agent
            else [],
        )

    def _classify_task_type(self, task: TaskDefinition) -> str:
        """Classify task type for learning optimization."""
        title_lower = task.title.lower()
        description_lower = task.description.lower()

        # Simple keyword-based classification
        if any(
            word in title_lower or word in description_lower
            for word in ["api", "endpoint", "rest"]
        ):
            return "api_development"
        elif any(
            word in title_lower or word in description_lower
            for word in ["database", "query", "sql"]
        ):
            return "database_operations"
        elif any(
            word in title_lower or word in description_lower
            for word in ["test", "testing", "validation"]
        ):
            return "testing"
        elif any(
            word in title_lower or word in description_lower
            for word in ["documentation", "docs", "readme"]
        ):
            return "documentation"
        elif any(
            word in title_lower or word in description_lower
            for word in ["security", "auth", "authentication"]
        ):
            return "security"
        elif any(
            word in title_lower or word in description_lower
            for word in ["performance", "optimization", "cache"]
        ):
            return "performance"
        else:
            return "general"

    async def _evaluate_routing_rule(
        self, rule: RoutingRule, task: TaskDefinition, agent_name: str
    ) -> float:
        """Evaluate how well a routing rule applies to a task-agent pair."""
        score = 0.0

        # Check task patterns
        if rule.task_patterns:
            title_lower = task.title.lower()
            description_lower = task.description.lower()

            for pattern in rule.task_patterns:
                if pattern == "*":  # Wildcard matches all
                    score += 10.0
                elif (
                    pattern.lower() in title_lower
                    or pattern.lower() in description_lower
                ):
                    score += 20.0

        # Check capability requirements
        if rule.capability_requirements:
            agent = self.agent_registry.get_agent(agent_name)
            if agent:
                agent_capabilities = {cap.name for cap in agent.capabilities}
                matching_capabilities = (
                    set(rule.capability_requirements) & agent_capabilities
                )
                if matching_capabilities:
                    score += (
                        len(matching_capabilities) / len(rule.capability_requirements)
                    ) * 30.0

        # Check preferred agents
        if rule.preferred_agents and agent_name in rule.preferred_agents:
            score += 40.0

        # Check excluded agents
        if rule.excluded_agents and agent_name in rule.excluded_agents:
            score = 0.0  # Rule doesn't apply

        # Check agent categories
        if rule.agent_categories:
            agent = self.agent_registry.get_agent(agent_name)
            if agent and agent.category in rule.agent_categories:
                score += 25.0

        # Check priority levels
        if rule.priority_levels and task.priority.value in rule.priority_levels:
            score += 15.0

        return score

    async def _monitor_agent_loads(self):
        """Monitor and update agent load information."""
        while True:
            try:
                await self._update_agent_loads()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error monitoring agent loads: {e}")
                await asyncio.sleep(60)  # Back off on error

    async def _update_agent_loads(self):
        """Update agent load information."""
        for agent_name in self.agent_registry.agents.keys():
            # Get current workload from task coordinator
            workload_info = self.task_coordinator.get_agent_workload(agent_name)

            agent_load = self.agent_loads.get(agent_name)
            if agent_load:
                # Update load information
                agent_load.current_tasks = workload_info["active_tasks"]
                agent_load.utilization_percentage = (
                    (agent_load.current_tasks / agent_load.max_capacity) * 100
                    if agent_load.max_capacity > 0
                    else 0
                )

                # Update load history
                agent_load.load_history.append(agent_load.utilization_percentage)
                if len(agent_load.load_history) > 100:  # Keep last 100 measurements
                    agent_load.load_history.pop(0)

                agent_load.last_updated = datetime.utcnow()

    async def _log_routing_decision(self, decision: RoutingDecision):
        """Log routing decision to database."""
        try:
            async with get_async_session() as session:
                activity = AgentActivity(
                    agent_name="@routing-manager",
                    activity_type=ActivityType.TASK_ASSIGNMENT,
                    description=f"Routed task to {decision.selected_agent}",
                    metadata={
                        "task_id": str(decision.task_id),
                        "selected_agent": decision.selected_agent,
                        "routing_strategy": decision.routing_strategy.value,
                        "confidence_score": decision.confidence_score,
                        "decision_factors": decision.decision_factors,
                        "applied_rules": decision.applied_rules,
                    },
                )
                session.add(activity)
                await session.commit()

        except Exception as e:
            logger.error(f"Error logging routing decision: {e}")

    def get_routing_statistics(self) -> dict:
        """Get routing manager statistics."""
        total_decisions = len(self.routing_decisions)

        if total_decisions == 0:
            return {
                "total_routing_decisions": 0,
                "average_confidence_score": 0.0,
                "routing_strategy_distribution": {},
                "agent_assignment_distribution": {},
                "last_updated": datetime.utcnow().isoformat(),
            }

        # Calculate statistics
        avg_confidence = (
            sum(d.confidence_score for d in self.routing_decisions) / total_decisions
        )

        strategy_counts = {}
        agent_counts = {}

        for decision in self.routing_decisions:
            # Strategy distribution
            strategy = decision.routing_strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

            # Agent assignment distribution
            agent = decision.selected_agent
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        return {
            "total_routing_decisions": total_decisions,
            "average_confidence_score": avg_confidence,
            "routing_strategy_distribution": strategy_counts,
            "agent_assignment_distribution": agent_counts,
            "active_routing_rules": len(
                [r for r in self.routing_rules.values() if r.enabled]
            ),
            "total_routing_rules": len(self.routing_rules),
            "load_balancing_mode": self.load_balancing_mode.value,
            "default_strategy": self.default_strategy.value,
            "last_updated": datetime.utcnow().isoformat(),
        }

    def get_agent_load_status(self) -> dict[str, dict]:
        """Get current load status for all agents."""
        return {
            agent_name: {
                "current_tasks": load.current_tasks,
                "max_capacity": load.max_capacity,
                "utilization_percentage": load.utilization_percentage,
                "success_rate": load.success_rate,
                "reliability_score": load.reliability_score,
                "last_updated": load.last_updated.isoformat(),
            }
            for agent_name, load in self.agent_loads.items()
        }


# Global routing manager instance
routing_manager = None


async def get_routing_manager() -> RoutingManager:
    """Get the global routing manager instance."""
    global routing_manager
    if routing_manager is None:
        from .agent_registry import agent_registry
        from .task_coordinator import get_task_coordinator

        await agent_registry.initialize()
        task_coordinator = await get_task_coordinator()

        routing_manager = RoutingManager(agent_registry, task_coordinator)
        await routing_manager.initialize()

        logger.info("Routing manager initialized")
    return routing_manager
