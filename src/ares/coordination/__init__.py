"""Agent workflow coordination system for ARES.

This module provides comprehensive agent coordination capabilities including:
- Agent registry with 26 specialized ARES agents
- Intelligent task coordination and assignment
- Advanced workflow orchestration engine
- Smart routing and load balancing
- Real-time performance monitoring
"""

from .agent_registry import (
    AgentCapability,
    AgentMetrics,
    AgentProfile,
    AgentRegistry,
    AgentStatus,
    agent_registry,
)
from .routing_manager import (
    LoadBalancingMode,
    RoutingDecision,
    RoutingManager,
    RoutingStrategy,
    get_routing_manager,
)
from .task_coordinator import (
    TaskCoordinator,
    TaskDefinition,
    TaskPriority,
    TaskRequirement,
    TaskStatus,
    get_task_coordinator,
)
from .workflow_engine import (
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowStep,
    WorkflowType,
    get_workflow_engine,
)

__all__ = [
    # Core coordination classes
    "AgentRegistry",
    "TaskCoordinator",
    "WorkflowEngine",
    "RoutingManager",
    # Agent registry components
    "AgentProfile",
    "AgentCapability",
    "AgentMetrics",
    "AgentStatus",
    "agent_registry",
    # Task coordination components
    "TaskDefinition",
    "TaskRequirement",
    "TaskPriority",
    "TaskStatus",
    "get_task_coordinator",
    # Workflow engine components
    "WorkflowDefinition",
    "WorkflowType",
    "WorkflowStep",
    "get_workflow_engine",
    # Routing manager components
    "RoutingStrategy",
    "RoutingDecision",
    "LoadBalancingMode",
    "get_routing_manager",
]


async def initialize_coordination_system():
    """Initialize the complete agent coordination system."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info("Initializing ARES Agent Coordination System...")

    # Initialize components in order
    await agent_registry.initialize()
    task_coordinator = await get_task_coordinator()
    workflow_engine = await get_workflow_engine()
    routing_manager = await get_routing_manager()

    logger.info("ARES Agent Coordination System fully initialized")

    return {
        "agent_registry": agent_registry,
        "task_coordinator": task_coordinator,
        "workflow_engine": workflow_engine,
        "routing_manager": routing_manager,
    }
