"""
ARES MCP Client

MCP client for connecting to external MCP servers and integrating
verification capabilities with other systems.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import structlog
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ARESMCPClient:
    """
    ARES MCP client for integration with external MCP servers.

    Provides connection pooling, caching, and performance optimization
    for MCP protocol communication.
    """

    def __init__(
        self,
        server_configs: dict[str, dict[str, Any]],
        max_connections_per_server: int = 5,
        cache_ttl: int = 300,  # 5 minutes
        circuit_breaker_threshold: int = 5,
    ):
        self.logger = structlog.get_logger("ares.mcp.client")
        self.server_configs = server_configs
        self.max_connections = max_connections_per_server
        self.cache_ttl = cache_ttl

        # Connection pools per server
        self._connection_pools: dict[str, list[ClientSession]] = {}
        self._pool_locks: dict[str, asyncio.Lock] = {}

        # Response cache
        self._query_cache: dict[str, dict[str, Any]] = {}
        self._cache_timestamps: dict[str, datetime] = {}

        # Circuit breaker per server
        self._circuit_breaker_failures: dict[str, int] = {}
        self._circuit_breaker_threshold = circuit_breaker_threshold
        self._circuit_breaker_open: dict[str, bool] = {}
        self._last_failure_times: dict[str, datetime | None] = {}

        # Performance metrics
        self._metrics = {
            "queries_executed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "connection_pool_hits": 0,
            "circuit_breaker_trips": 0,
        }

    async def initialize(self) -> None:
        """Initialize MCP client with connection pools for all servers."""
        self.logger.info("Initializing ARES MCP client")

        for server_name, config in self.server_configs.items():
            # Initialize connection pool for each server
            self._connection_pools[server_name] = []
            self._pool_locks[server_name] = asyncio.Lock()
            self._circuit_breaker_failures[server_name] = 0
            self._circuit_breaker_open[server_name] = False
            self._last_failure_times[server_name] = None

            # Pre-create connections
            for i in range(self.max_connections):
                try:
                    session = await self._create_mcp_session(server_name, config)
                    self._connection_pools[server_name].append(session)
                    self.logger.debug(
                        f"Created MCP connection {i + 1}/{self.max_connections} for {server_name}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Failed to create MCP connection for {server_name}: {e}"
                    )
                    break

        self.logger.info(
            "ARES MCP client initialized successfully",
            servers=list(self.server_configs.keys()),
            total_connections=sum(
                len(pool) for pool in self._connection_pools.values()
            ),
        )

    async def _create_mcp_session(
        self, server_name: str, config: dict[str, Any]
    ) -> ClientSession:
        """Create a new MCP session for a specific server."""
        server_params = StdioServerParameters(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {}),
        )

        return await stdio_client(server_params)

    @asynccontextmanager
    async def _get_session(self, server_name: str):
        """Get an MCP session from the pool for a specific server."""
        if server_name not in self._connection_pools:
            raise ValueError(f"Unknown MCP server: {server_name}")

        session = None

        async with self._pool_locks[server_name]:
            if self._connection_pools[server_name]:
                session = self._connection_pools[server_name].pop()
                self._metrics["connection_pool_hits"] += 1

        if session is None:
            # Pool exhausted, create temporary session
            config = self.server_configs[server_name]
            session = await self._create_mcp_session(server_name, config)

        try:
            yield session
        finally:
            # Return session to pool if there's space
            async with self._pool_locks[server_name]:
                if len(self._connection_pools[server_name]) < self.max_connections:
                    self._connection_pools[server_name].append(session)
                else:
                    # Pool full, close session
                    await session.close()

    def _get_cache_key(
        self, server_name: str, operation: str, params: dict[str, Any]
    ) -> str:
        """Generate cache key for operation and parameters."""
        param_str = json.dumps(params, sort_keys=True)
        return f"{server_name}:{operation}:{hash(param_str)}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid."""
        if cache_key not in self._cache_timestamps:
            return False

        timestamp = self._cache_timestamps[cache_key]
        age = (datetime.now() - timestamp).total_seconds()
        return age < self.cache_ttl

    async def _execute_with_circuit_breaker(
        self, server_name: str, operation_func, *args, **kwargs
    ):
        """Execute operation with circuit breaker pattern."""
        if self._circuit_breaker_open.get(server_name, False):
            # Check if we should try to close the circuit breaker
            last_failure = self._last_failure_times.get(server_name)
            if last_failure:
                time_since_failure = (datetime.now() - last_failure).total_seconds()
                if time_since_failure < 60:  # Wait 60 seconds before retry
                    raise Exception(f"Circuit breaker is open for {server_name}")

            # Try to close circuit breaker
            self._circuit_breaker_open[server_name] = False
            self.logger.info(f"Attempting to close circuit breaker for {server_name}")

        try:
            result = await operation_func(*args, **kwargs)
            # Reset failure count on success
            self._circuit_breaker_failures[server_name] = 0
            return result

        except Exception:
            failures = self._circuit_breaker_failures.get(server_name, 0) + 1
            self._circuit_breaker_failures[server_name] = failures
            self._last_failure_times[server_name] = datetime.now()

            if failures >= self._circuit_breaker_threshold:
                self._circuit_breaker_open[server_name] = True
                self._metrics["circuit_breaker_trips"] += 1
                self.logger.error(
                    f"Circuit breaker opened for {server_name}", failure_count=failures
                )

            raise

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
        use_cache: bool = True,
    ) -> Any:
        """Call a tool on a specific MCP server."""
        operation = f"call_tool:{tool_name}"
        cache_key = self._get_cache_key(server_name, operation, arguments)

        # Check cache first if enabled
        if use_cache and self._is_cache_valid(cache_key):
            self._metrics["cache_hits"] += 1
            self.logger.debug(f"Cache hit for {server_name}:{tool_name}")
            return self._query_cache[cache_key]

        if use_cache:
            self._metrics["cache_misses"] += 1

        async def _call_tool():
            async with self._get_session(server_name) as session:
                result = await session.call_tool(tool_name, arguments)
                return result

        result = await self._execute_with_circuit_breaker(server_name, _call_tool)
        self._metrics["queries_executed"] += 1

        # Cache the result if caching is enabled
        if use_cache:
            self._query_cache[cache_key] = result
            self._cache_timestamps[cache_key] = datetime.now()

        self.logger.debug(
            f"Tool call completed: {server_name}:{tool_name}", arguments=arguments
        )

        return result

    async def list_tools(self, server_name: str) -> list[dict[str, Any]]:
        """List available tools from a specific MCP server."""

        async def _list_tools():
            async with self._get_session(server_name) as session:
                result = await session.list_tools()
                return result

        result = await self._execute_with_circuit_breaker(server_name, _list_tools)
        self._metrics["queries_executed"] += 1

        self.logger.debug(f"Listed tools for {server_name}")
        return result

    async def get_server_info(self, server_name: str) -> dict[str, Any]:
        """Get server information from a specific MCP server."""

        async def _get_info():
            async with self._get_session(server_name):
                # This would call server info endpoint
                # Implementation depends on MCP server capabilities
                return {"server_name": server_name, "status": "connected"}

        result = await self._execute_with_circuit_breaker(server_name, _get_info)
        return result

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for monitoring."""
        cache_hit_rate = 0
        if self._metrics["cache_hits"] + self._metrics["cache_misses"] > 0:
            cache_hit_rate = self._metrics["cache_hits"] / (
                self._metrics["cache_hits"] + self._metrics["cache_misses"]
            )

        return {
            **self._metrics,
            "cache_hit_rate": cache_hit_rate,
            "active_servers": len(self.server_configs),
            "total_pool_connections": sum(
                len(pool) for pool in self._connection_pools.values()
            ),
            "circuit_breaker_status": {
                server: {
                    "open": self._circuit_breaker_open.get(server, False),
                    "failures": self._circuit_breaker_failures.get(server, 0),
                }
                for server in self.server_configs.keys()
            },
        }

    async def clear_cache(self) -> None:
        """Clear query cache."""
        self._query_cache.clear()
        self._cache_timestamps.clear()
        self.logger.info("MCP client cache cleared")

    async def close(self) -> None:
        """Clean shutdown of MCP client."""
        self.logger.info("Closing ARES MCP client")

        # Close all connections in all pools
        for server_name, pool in self._connection_pools.items():
            async with self._pool_locks[server_name]:
                for session in pool:
                    try:
                        await session.close()
                    except Exception as e:
                        self.logger.warning(
                            f"Error closing MCP session for {server_name}: {e}"
                        )
                pool.clear()

        # Clear caches
        self._query_cache.clear()
        self._cache_timestamps.clear()

        self.logger.info("ARES MCP client closed successfully")
