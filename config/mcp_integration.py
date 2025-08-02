"""MCP Server Integration Configuration for ARES Agent Reliability Monitoring."""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any


class MCPServerType(Enum):
    """Types of MCP servers available for ARES agents."""

    DATABASE = "database"
    CODE_QUALITY = "code_quality"
    BROWSER_AUTOMATION = "browser_automation"
    INFRASTRUCTURE = "infrastructure"
    SEARCH_ANALYSIS = "search_analysis"
    DOCUMENTATION = "documentation"


@dataclass
class MCPServerConfig:
    """Configuration for individual MCP servers."""

    name: str
    server_type: MCPServerType
    tools: list[str]
    reliability_use_cases: list[str]
    required_for_agents: list[str]
    performance_impact: str  # low, medium, high


class AresMCPIntegration:
    """ARES MCP Server Integration Manager."""

    # Core MCP servers for agent reliability monitoring
    MCP_SERVERS = {
        # Database Operations - Critical for reliability metrics
        "sqlite": MCPServerConfig(
            name="SQLite MCP Server",
            server_type=MCPServerType.DATABASE,
            tools=[
                "mcp__sqlite__read_query",
                "mcp__sqlite__write_query",
                "mcp__sqlite__create_table",
                "mcp__sqlite__list_tables",
                "mcp__sqlite__describe_table",
            ],
            reliability_use_cases=[
                "Agent performance metrics storage",
                "Task completion verification data",
                "Reliability scoring persistence",
                "Agent behavior pattern tracking",
                "Proof-of-work evidence storage",
            ],
            required_for_agents=[
                "tech-lead-orchestrator",
                "code-reviewer",
                "backend-developer",
                "performance-optimizer",
            ],
            performance_impact="low",
        ),
        # Code Quality Assurance - Essential for agent reliability
        "python_checker": MCPServerConfig(
            name="Python Code Checker",
            server_type=MCPServerType.CODE_QUALITY,
            tools=[
                "mcp__code_checker__run_pylint_check",
                "mcp__code_checker__run_pytest_check",
                "mcp__code_checker__run_all_checks",
            ],
            reliability_use_cases=[
                "Agent code quality validation",
                "Automated testing of agent implementations",
                "Quality gate enforcement",
                "Reliability standard compliance checking",
            ],
            required_for_agents=[
                "code-reviewer",
                "backend-developer",
                "django-backend-expert",
                "laravel-backend-expert",
                "rails-backend-expert",
            ],
            performance_impact="medium",
        ),
        # Browser Automation - For end-to-end reliability testing
        "playwright": MCPServerConfig(
            name="Playwright Enhanced",
            server_type=MCPServerType.BROWSER_AUTOMATION,
            tools=[
                "mcp__playwright-enhanced__playwright_navigate",
                "mcp__playwright-enhanced__playwright_screenshot",
                "mcp__playwright-enhanced__playwright_click",
                "mcp__playwright-enhanced__playwright_fill",
                "mcp__playwright-enhanced__playwright_evaluate",
            ],
            reliability_use_cases=[
                "Agent dashboard UI testing",
                "Real-time monitoring interface validation",
                "End-to-end agent workflow testing",
                "WebSocket reliability verification",
            ],
            required_for_agents=[
                "frontend-developer",
                "react-component-architect",
                "vue-component-architect",
            ],
            performance_impact="high",
        ),
        # Search and Analysis - For agent pattern discovery
        "ripgrep": MCPServerConfig(
            name="Ripgrep Search",
            server_type=MCPServerType.SEARCH_ANALYSIS,
            tools=[
                "mcp__ripgrep-search__search",
                "mcp__ripgrep-search__advanced-search",
                "mcp__ripgrep-search__count-matches",
                "mcp__ripgrep-search__list-files",
            ],
            reliability_use_cases=[
                "Agent behavior pattern detection",
                "Code quality issue identification",
                "Reliability metric correlation analysis",
                "Agent implementation consistency checks",
            ],
            required_for_agents=[
                "code-archaeologist",
                "performance-optimizer",
                "project-analyst",
            ],
            performance_impact="low",
        ),
        # Documentation - For reliability reporting
        "context7": MCPServerConfig(
            name="Context7 Documentation",
            server_type=MCPServerType.DOCUMENTATION,
            tools=[
                "mcp__context7__resolve-library-id",
                "mcp__context7__get-library-docs",
            ],
            reliability_use_cases=[
                "Framework best practices validation",
                "Agent implementation standard verification",
                "Reliability pattern documentation",
                "Quality benchmark establishment",
            ],
            required_for_agents=[
                "documentation-specialist",
                "django-backend-expert",
                "laravel-backend-expert",
                "rails-backend-expert",
            ],
            performance_impact="low",
        ),
    }

    @classmethod
    def get_required_tools_for_agent(cls, agent_name: str) -> list[str]:
        """Get required MCP tools for a specific agent."""
        required_tools = []

        for server_config in cls.MCP_SERVERS.values():
            if agent_name in server_config.required_for_agents:
                required_tools.extend(server_config.tools)

        return required_tools

    @classmethod
    def get_reliability_monitoring_tools(cls) -> dict[str, list[str]]:
        """Get MCP tools specifically for reliability monitoring."""
        return {
            "database_operations": cls.MCP_SERVERS["sqlite"].tools,
            "quality_assurance": cls.MCP_SERVERS["python_checker"].tools,
            "pattern_analysis": cls.MCP_SERVERS["ripgrep"].tools,
            "ui_testing": cls.MCP_SERVERS["playwright"].tools[:3],  # Core tools only
            "documentation": cls.MCP_SERVERS["context7"].tools,
        }

    @classmethod
    def validate_agent_mcp_usage(
        cls, agent_name: str, tools_used: list[str]
    ) -> dict[str, Any]:
        """Validate that an agent is using required MCP tools properly."""
        required_tools = cls.get_required_tools_for_agent(agent_name)

        validation_result = {
            "agent_name": agent_name,
            "required_tools": required_tools,
            "tools_used": tools_used,
            "missing_tools": [
                tool for tool in required_tools if tool not in tools_used
            ],
            "extra_tools": [tool for tool in tools_used if tool not in required_tools],
            "compliance_score": 0.0,
            "recommendations": [],
        }

        if required_tools:
            compliance_score = len(
                [t for t in required_tools if t in tools_used]
            ) / len(required_tools)
            validation_result["compliance_score"] = compliance_score

            if compliance_score < 0.8:
                validation_result["recommendations"].append(
                    f"Agent should use more required MCP tools. Missing: {validation_result['missing_tools']}"
                )

        return validation_result


class AgentReliabilityMCPPatterns:
    """Common MCP usage patterns for agent reliability monitoring."""

    @staticmethod
    def database_reliability_tracking() -> dict[str, str]:
        """SQL patterns for tracking agent reliability."""
        return {
            "create_agent_metrics": """
                CREATE TABLE IF NOT EXISTS agent_reliability_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    completion_score REAL NOT NULL,
                    quality_score REAL NOT NULL,
                    mcp_tools_used TEXT, -- JSON array
                    execution_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "record_task_completion": """
                INSERT INTO agent_reliability_metrics
                (agent_name, task_id, completion_score, quality_score, mcp_tools_used, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            "get_agent_reliability_score": """
                SELECT
                    agent_name,
                    AVG(completion_score) as avg_completion,
                    AVG(quality_score) as avg_quality,
                    COUNT(*) as task_count,
                    AVG(execution_time) as avg_execution_time
                FROM agent_reliability_metrics
                WHERE agent_name = ? AND created_at > datetime('now', '-7 days')
                GROUP BY agent_name
            """,
            "get_reliability_trends": """
                SELECT
                    DATE(created_at) as date,
                    agent_name,
                    AVG(completion_score) as daily_completion_score,
                    AVG(quality_score) as daily_quality_score
                FROM agent_reliability_metrics
                WHERE created_at > datetime('now', '-30 days')
                GROUP BY DATE(created_at), agent_name
                ORDER BY date DESC, agent_name
            """,
        }

    @staticmethod
    def code_quality_validation_patterns() -> dict[str, str]:
        """Patterns for using code quality MCP tools."""
        return {
            "validate_agent_implementation": """
                # Use code checker to validate agent-generated code
                result = mcp__code_checker__run_all_checks()

                # Parse results for reliability scoring
                quality_metrics = {
                    'pylint_score': extract_pylint_score(result),
                    'test_coverage': extract_coverage(result),
                    'error_count': count_errors(result),
                    'warning_count': count_warnings(result)
                }

                # Calculate reliability score
                reliability_score = calculate_reliability_score(quality_metrics)
                """,
            "continuous_quality_monitoring": """
                # Regular quality checks for agent implementations
                async def monitor_agent_quality():
                    agents = get_active_agents()
                    for agent in agents:
                        quality_result = await run_quality_checks(agent.code_files)
                        reliability_score = calculate_score(quality_result)
                        await update_agent_reliability(agent.id, reliability_score)
                """,
        }

    @staticmethod
    def browser_automation_testing_patterns() -> dict[str, str]:
        """Patterns for testing agent-generated UIs."""
        return {
            "test_agent_dashboard": """
                # Test agent reliability dashboard functionality
                await mcp__playwright-enhanced__playwright_navigate({
                    "url": "http://localhost:8000/dashboard"
                })

                # Take screenshot for visual validation
                await mcp__playwright-enhanced__playwright_screenshot({
                    "name": "agent_dashboard_baseline",
                    "fullPage": True
                })

                # Test real-time updates
                await mcp__playwright-enhanced__playwright_click({
                    "selector": "[data-testid='refresh-metrics']"
                })
                """,
            "validate_realtime_updates": """
                # Validate WebSocket reliability monitoring
                await mcp__playwright-enhanced__playwright_evaluate({
                    "script": '''
                        window.reliabilityTestResults = {
                            websocket_connected: !!window.ws && window.ws.readyState === 1,
                            last_update_timestamp: window.lastMetricUpdate,
                            active_agents_count: document.querySelectorAll('.agent-status.active').length
                        };
                    '''
                })
                """,
        }


# Example usage in ARES agents
class AresAgentMCPExample:
    """Example of how ARES agents should integrate with MCP servers."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.required_tools = AresMCPIntegration.get_required_tools_for_agent(
            agent_name
        )
        self.mcp_patterns = AgentReliabilityMCPPatterns()

    async def record_task_completion(
        self, task_id: str, evidence: dict[str, Any]
    ) -> float:
        """Record task completion with reliability metrics."""
        # Use SQLite MCP to store reliability data
        completion_score = self.calculate_completion_score(evidence)
        quality_score = await self.run_quality_validation(
            evidence.get("code_files", [])
        )

        # Store in reliability database
        await self.execute_mcp_sql(
            self.mcp_patterns.database_reliability_tracking()["record_task_completion"],
            [
                self.agent_name,
                task_id,
                completion_score,
                quality_score,
                json.dumps(self.required_tools),
                evidence.get("execution_time", 0),
            ],
        )

        return completion_score

    async def validate_implementation_quality(
        self, code_files: list[str]
    ) -> dict[str, Any]:
        """Use code quality MCP tools to validate implementation."""
        # Run comprehensive quality checks
        quality_result = await self.execute_mcp_tool(
            "mcp__code_checker__run_all_checks", {"files": code_files}
        )

        return {
            "quality_score": self.extract_quality_score(quality_result),
            "recommendations": self.extract_recommendations(quality_result),
            "compliance": quality_result.get("compliance", {}),
        }

    async def search_reliability_patterns(
        self, search_term: str
    ) -> list[dict[str, Any]]:
        """Use ripgrep MCP to find reliability patterns in codebase."""
        search_result = await self.execute_mcp_tool(
            "mcp__ripgrep-search__advanced-search",
            {"pattern": search_term, "path": "src/", "fileType": "py", "context": 3},
        )

        return self.parse_reliability_patterns(search_result)
