"""
ARES MCP Server Implementation

Production-ready MCP server for ARES verification capabilities.
Provides verification tools for AI assistants and external integrations.
"""

from datetime import datetime
from typing import Any

import structlog
from mcp.server.fastmcp import FastMCP

from ..core.config import get_settings
from ..verification import (
    AgentBehaviorMonitor,
    CompletionVerifier,
    ProofOfWorkCollector,
    TaskRollbackManager,
    ToolCallValidator,
)


class ARESMCPServer:
    """
    ARES MCP Server providing verification capabilities as MCP tools.

    Exposes ARES verification components through the Model Context Protocol
    for integration with AI assistants and external systems.
    """

    def __init__(self):
        self.logger = structlog.get_logger("ares.mcp.server")
        self.settings = get_settings()

        # Initialize verification components
        self.completion_verifier = None
        self.tool_validator = None
        self.rollback_manager = None
        self.proof_collector = None
        self.behavior_monitor = None

        # MCP server instance
        self.server = None
        self.app = None

    async def initialize(self) -> None:
        """Initialize ARES MCP server and verification components."""
        self.logger.info("Initializing ARES MCP server")

        # Initialize verification components
        self.completion_verifier = CompletionVerifier()
        self.tool_validator = ToolCallValidator()
        self.rollback_manager = TaskRollbackManager()
        self.proof_collector = ProofOfWorkCollector()
        self.behavior_monitor = AgentBehaviorMonitor()

        await self.completion_verifier.initialize()
        await self.tool_validator.initialize()
        await self.rollback_manager.initialize()
        await self.proof_collector.initialize()
        await self.behavior_monitor.initialize()

        # Create FastMCP application
        self.app = FastMCP("ARES")

        # Register MCP tools
        await self._register_verification_tools()
        await self._register_monitoring_tools()
        await self._register_enforcement_tools()

        self.logger.info("ARES MCP server initialized successfully")

    async def _register_verification_tools(self) -> None:
        """Register verification-related MCP tools."""

        @self.app.tool()
        async def verify_task_completion(
            task_id: str,
            expected_outputs: dict[str, Any],
            success_criteria: dict[str, Any],
        ) -> dict[str, Any]:
            """Verify that a task has been completed successfully.

            Args:
                task_id: Unique identifier for the task
                expected_outputs: Expected outputs from the task
                success_criteria: Criteria for determining success

            Returns:
                Verification result with status and details
            """
            try:
                result = await self.completion_verifier.verify_completion(
                    task_id=task_id,
                    expected_outputs=expected_outputs,
                    success_criteria=success_criteria,
                )

                self.logger.info(
                    "Task completion verification completed",
                    task_id=task_id,
                    status=result.get("status"),
                )

                return result

            except Exception as e:
                self.logger.error(f"Task completion verification failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        @self.app.tool()
        async def validate_tool_call(
            tool_name: str,
            tool_arguments: dict[str, Any],
            expected_result_schema: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Validate an MCP tool call and its parameters.

            Args:
                tool_name: Name of the MCP tool being called
                tool_arguments: Arguments passed to the tool
                expected_result_schema: Optional schema for result validation

            Returns:
                Validation result with status and details
            """
            try:
                result = await self.tool_validator.validate_call(
                    tool_name=tool_name,
                    arguments=tool_arguments,
                    result_schema=expected_result_schema,
                )

                self.logger.debug(
                    "Tool call validation completed",
                    tool_name=tool_name,
                    status=result.get("status"),
                )

                return result

            except Exception as e:
                self.logger.error(f"Tool call validation failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        @self.app.tool()
        async def collect_proof_of_work(
            task_id: str,
            agent_id: str,
            evidence_type: str,
            evidence_data: dict[str, Any],
        ) -> dict[str, Any]:
            """Collect proof of work evidence for a task.

            Args:
                task_id: Unique identifier for the task
                agent_id: Identifier of the agent performing the task
                evidence_type: Type of evidence being collected
                evidence_data: Actual evidence data

            Returns:
                Collection result with evidence ID and validation status
            """
            try:
                result = await self.proof_collector.collect_evidence(
                    task_id=task_id,
                    agent_id=agent_id,
                    evidence_type=evidence_type,
                    evidence_data=evidence_data,
                )

                self.logger.info(
                    "Proof of work collected",
                    task_id=task_id,
                    agent_id=agent_id,
                    evidence_type=evidence_type,
                )

                return result

            except Exception as e:
                self.logger.error(f"Proof of work collection failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

    async def _register_monitoring_tools(self) -> None:
        """Register monitoring-related MCP tools."""

        @self.app.tool()
        async def monitor_agent_behavior(
            agent_id: str,
            behavior_data: dict[str, Any],
            monitoring_window: int | None = 300,  # 5 minutes default
        ) -> dict[str, Any]:
            """Monitor agent behavior patterns for anomalies.

            Args:
                agent_id: Identifier of the agent to monitor
                behavior_data: Current behavior data to analyze
                monitoring_window: Time window in seconds for analysis

            Returns:
                Monitoring result with anomaly detection status
            """
            try:
                result = await self.behavior_monitor.analyze_behavior(
                    agent_id=agent_id,
                    behavior_data=behavior_data,
                    window_seconds=monitoring_window,
                )

                self.logger.debug(
                    "Agent behavior monitoring completed",
                    agent_id=agent_id,
                    anomalies_detected=result.get("anomalies_detected", False),
                )

                return result

            except Exception as e:
                self.logger.error(f"Agent behavior monitoring failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        @self.app.tool()
        async def get_agent_reliability_metrics(
            agent_id: str, time_range: str | None = "24h"
        ) -> dict[str, Any]:
            """Get reliability metrics for a specific agent.

            Args:
                agent_id: Identifier of the agent
                time_range: Time range for metrics (e.g., "1h", "24h", "7d")

            Returns:
                Agent reliability metrics and statistics
            """
            try:
                # This would integrate with your database models
                metrics = await self._get_agent_metrics(agent_id, time_range)

                self.logger.debug(
                    "Agent reliability metrics retrieved",
                    agent_id=agent_id,
                    time_range=time_range,
                )

                return {
                    "status": "success",
                    "agent_id": agent_id,
                    "time_range": time_range,
                    "metrics": metrics,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                self.logger.error(f"Failed to get agent metrics: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

    async def _register_enforcement_tools(self) -> None:
        """Register enforcement-related MCP tools."""

        @self.app.tool()
        async def create_rollback_checkpoint(
            task_id: str,
            checkpoint_data: dict[str, Any],
            checkpoint_type: str = "automatic",
        ) -> dict[str, Any]:
            """Create a rollback checkpoint for a task.

            Args:
                task_id: Unique identifier for the task
                checkpoint_data: State data to checkpoint
                checkpoint_type: Type of checkpoint (automatic, manual, etc.)

            Returns:
                Checkpoint creation result with checkpoint ID
            """
            try:
                result = await self.rollback_manager.create_checkpoint(
                    task_id=task_id,
                    state_data=checkpoint_data,
                    checkpoint_type=checkpoint_type,
                )

                self.logger.info(
                    "Rollback checkpoint created",
                    task_id=task_id,
                    checkpoint_id=result.get("checkpoint_id"),
                    type=checkpoint_type,
                )

                return result

            except Exception as e:
                self.logger.error(f"Checkpoint creation failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        @self.app.tool()
        async def execute_rollback(
            task_id: str,
            checkpoint_id: str | None = None,
            reason: str = "verification_failure",
        ) -> dict[str, Any]:
            """Execute rollback to a previous state.

            Args:
                task_id: Unique identifier for the task
                checkpoint_id: Specific checkpoint to rollback to (latest if not specified)
                reason: Reason for the rollback

            Returns:
                Rollback execution result
            """
            try:
                result = await self.rollback_manager.execute_rollback(
                    task_id=task_id, checkpoint_id=checkpoint_id, reason=reason
                )

                self.logger.warning(
                    "Rollback executed",
                    task_id=task_id,
                    checkpoint_id=checkpoint_id,
                    reason=reason,
                )

                return result

            except Exception as e:
                self.logger.error(f"Rollback execution failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

    async def _get_agent_metrics(
        self, agent_id: str, time_range: str
    ) -> dict[str, Any]:
        """Get agent reliability metrics from database."""
        # This would implement actual database queries
        # For now, return mock data structure
        return {
            "success_rate": 0.95,
            "average_completion_time": 120.5,
            "total_tasks": 45,
            "failed_tasks": 2,
            "anomalies_detected": 1,
            "last_activity": datetime.now().isoformat(),
        }

    def get_app(self):
        """Get the FastMCP application instance."""
        return self.app

    async def run_server(self, host: str = "localhost", port: int = 8001) -> None:
        """Run the ARES MCP server."""
        self.logger.info(f"Starting ARES MCP server on {host}:{port}")

        try:
            await self.app.run(host=host, port=port)
        except Exception as e:
            self.logger.error(f"MCP server failed to start: {e}")
            raise

    async def close(self) -> None:
        """Clean shutdown of ARES MCP server."""
        self.logger.info("Shutting down ARES MCP server")

        # Cleanup verification components
        if self.completion_verifier:
            await self.completion_verifier.close()
        if self.tool_validator:
            await self.tool_validator.close()
        if self.rollback_manager:
            await self.rollback_manager.close()
        if self.proof_collector:
            await self.proof_collector.close()
        if self.behavior_monitor:
            await self.behavior_monitor.close()

        self.logger.info("ARES MCP server shutdown complete")
