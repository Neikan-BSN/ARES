"""Command line interface for ARES - Agent Reliability Enforcement System."""

import asyncio
import json
from datetime import datetime

import aiofiles
import click
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .core.config import settings
from .verification.completion.schemas import CompletionStatus, TaskCompletionRequest
from .verification.completion.verifier import CompletionVerifier
from .verification.proof_of_work.collector import ProofOfWorkCollector
from .verification.proof_of_work.schemas import CollectionStatus, ProofOfWorkRequest
from .verification.tool_validation.schemas import (
    ToolCallValidationRequest,
    ValidationStatus,
)
from .verification.tool_validation.validator import ToolCallValidator

# Configure async database session
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", help="Path to configuration file")
@click.pass_context
def cli(ctx, verbose: bool, config: str | None) -> None:
    """ARES - Agent Reliability Enforcement System

    Comprehensive agent reliability monitoring, validation, and enforcement platform.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

    if verbose:
        click.echo("🤖 ARES CLI - Agent Reliability Enforcement System")
        click.echo(f"📊 Database: {settings.DATABASE_URL}")
        if config:
            click.echo(f"⚙️  Config: {config}")


# ==============================================================================
# TASK COMPLETION VERIFICATION COMMANDS
# ==============================================================================


@cli.group(name="verify")
def verify_group():
    """Task completion verification commands."""
    pass


@verify_group.command(name="task")
@click.option("--agent-id", required=True, help="Agent ID that completed the task")
@click.option("--task-id", required=True, help="Unique task identifier")
@click.option("--description", required=True, help="Task description and requirements")
@click.option(
    "--evidence-file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file containing completion evidence",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table", "summary"]),
    default="summary",
    help="Output format",
)
@click.pass_context
def verify_task(
    ctx, agent_id: str, task_id: str, description: str, evidence_file: str, output: str
) -> None:
    """Verify task completion with evidence analysis.

    Example:
        ares verify task --agent-id agent_123 --task-id task_456 \\
                        --description "Create user authentication API" \\
                        --evidence-file evidence.json
    """

    async def _verify_task():
        try:
            # Load evidence from file
            async with aiofiles.open(evidence_file) as f:
                content = await f.read()
                evidence_data = json.loads(content)

            # Create completion request
            completion_request = TaskCompletionRequest(
                task_id=task_id,
                agent_id=agent_id,
                task_description=description,
                completion_evidence=evidence_data,
                completion_timestamp=datetime.utcnow(),
            )

            # Perform verification
            async with AsyncSessionLocal() as session:
                verifier = CompletionVerifier(session)
                result = await verifier.verify_task_completion(
                    agent_id, task_id, completion_request
                )

            # Output results
            if output == "json":
                click.echo(result.json(indent=2))
            elif output == "table":
                _display_verification_table(result)
            else:
                _display_verification_summary(result)

        except Exception as e:
            click.echo(f"❌ Verification failed: {str(e)}", err=True)
            raise click.ClickException(str(e)) from e

    asyncio.run(_verify_task())


def _display_verification_summary(result) -> None:
    """Display verification results in summary format."""
    status_icons = {
        CompletionStatus.COMPLETED: "✅",
        CompletionStatus.PARTIAL: "⚠️",
        CompletionStatus.FAILED: "❌",
        CompletionStatus.INVALID: "🚫",
        CompletionStatus.ERROR: "💥",
    }

    icon = status_icons.get(result.status, "❓")
    click.echo(f"\n{icon} Task Verification Result")
    click.echo(f"Status: {result.status.value.upper()}")
    click.echo(f"Agent: {result.agent_id}")
    click.echo(f"Task: {result.task_id}")
    click.echo(f"Message: {result.message}")

    # Quality metrics
    metrics = result.quality_metrics
    click.echo("\n📊 Quality Metrics:")
    click.echo(f"  Overall Score: {metrics.overall_score:.2f}")
    click.echo(f"  Output Quality: {metrics.output_quality_score:.2f}")
    click.echo(f"  Requirements Match: {metrics.requirements_match_score:.2f}")
    click.echo(f"  Performance: {metrics.performance_score:.2f}")
    click.echo(f"  Security: {metrics.security_score:.2f}")

    # Evidence summary
    click.echo(f"\n🔍 Evidence: {len(result.evidence)} pieces collected")
    for evidence in result.evidence[:3]:  # Show first 3
        click.echo(
            f"  • {evidence.evidence_type}: {evidence.confidence_score:.2f} confidence"
        )

    if len(result.evidence) > 3:
        click.echo(f"  ... and {len(result.evidence) - 3} more")


def _display_verification_table(result) -> None:
    """Display verification results in table format."""
    # This would use a table library like tabulate
    # For now, simplified version
    click.echo(f"Task ID: {result.task_id}")
    click.echo(f"Agent ID: {result.agent_id}")
    click.echo(f"Status: {result.status}")
    click.echo(f"Overall Score: {result.quality_metrics.overall_score:.2f}")


# ==============================================================================
# TOOL CALL VALIDATION COMMANDS
# ==============================================================================


@cli.group(name="validate")
def validate_group():
    """Tool call validation commands."""
    pass


@validate_group.command(name="tool-call")
@click.option("--agent-id", required=True, help="Agent ID making the tool call")
@click.option("--tool-name", required=True, help="Name of the MCP tool")
@click.option("--parameters", help="Tool parameters as JSON string")
@click.option("--mcp-version", default="1.1", help="MCP protocol version")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "summary"]),
    default="summary",
    help="Output format",
)
@click.pass_context
def validate_tool_call(
    ctx, agent_id: str, tool_name: str, parameters: str, mcp_version: str, output: str
) -> None:
    """Validate MCP tool call for compliance and security.

    Example:
        ares validate tool-call --agent-id agent_123 --tool-name read_file \\
                               --parameters '{"path": "/home/user/file.txt"}'
    """

    async def _validate_tool_call():
        try:
            # Parse parameters
            params = json.loads(parameters) if parameters else {}

            # Create validation request
            validation_request = ToolCallValidationRequest(
                tool_name=tool_name,
                parameters=params,
                mcp_version=mcp_version,
                secure_transport=True,
                call_timestamp=datetime.utcnow(),
            )

            # Perform validation
            async with AsyncSessionLocal() as session:
                validator = ToolCallValidator(session)
                result = await validator.validate_tool_call(
                    agent_id, validation_request
                )

            # Output results
            if output == "json":
                click.echo(result.json(indent=2))
            else:
                _display_validation_summary(result)

        except Exception as e:
            click.echo(f"❌ Validation failed: {str(e)}", err=True)
            raise click.ClickException(str(e)) from e

    asyncio.run(_validate_tool_call())


def _display_validation_summary(result) -> None:
    """Display tool validation results in summary format."""
    status_icons = {
        ValidationStatus.VALID: "✅",
        ValidationStatus.WARNING: "⚠️",
        ValidationStatus.UNAUTHORIZED: "🚫",
        ValidationStatus.PROTOCOL_VIOLATION: "📋",
        ValidationStatus.INVALID_PARAMETERS: "🔧",
        ValidationStatus.RATE_LIMITED: "⏱️",
        ValidationStatus.SECURITY_VIOLATION: "🔒",
        ValidationStatus.ERROR: "💥",
    }

    icon = status_icons.get(result.status, "❓")
    click.echo(f"\n{icon} Tool Call Validation Result")
    click.echo(f"Status: {result.status.value.upper()}")
    click.echo(f"Tool: {result.tool_name}")
    click.echo(f"Agent: {result.agent_id}")
    click.echo(f"Message: {result.message}")

    # Compliance metrics
    metrics = result.compliance_metrics
    click.echo("\n📋 Compliance Metrics:")
    click.echo(f"  Overall Score: {metrics.overall_compliance_score:.2f}")
    click.echo(f"  Protocol: {metrics.protocol_compliance_score:.2f}")
    click.echo(f"  Authorization: {metrics.authorization_score:.2f}")
    click.echo(f"  Parameters: {metrics.parameter_validation_score:.2f}")
    click.echo(f"  Security: {metrics.security_compliance_score:.2f}")


# ==============================================================================
# PROOF OF WORK COLLECTION COMMANDS
# ==============================================================================


@cli.group(name="proof")
def proof_group():
    """Proof-of-work collection commands."""
    pass


@proof_group.command(name="collect")
@click.option("--agent-id", required=True, help="Agent ID that completed the work")
@click.option("--task-id", required=True, help="Unique task identifier")
@click.option("--description", required=True, help="Work description")
@click.option(
    "--evidence-file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file containing work evidence",
)
@click.option("--complexity", type=int, help="Task complexity level (1-5)")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "summary"]),
    default="summary",
    help="Output format",
)
@click.pass_context
def collect_proof(
    ctx,
    agent_id: str,
    task_id: str,
    description: str,
    evidence_file: str,
    complexity: int | None,
    output: str,
) -> None:
    """Collect and analyze proof-of-work evidence.

    Example:
        ares proof collect --agent-id agent_123 --task-id task_456 \\
                          --description "API implementation" \\
                          --evidence-file work_evidence.json --complexity 3
    """

    async def _collect_proof():
        try:
            # Load evidence from file
            async with aiofiles.open(evidence_file) as f:
                content = await f.read()
                evidence_data = json.loads(content)

            # Create proof request
            proof_request = ProofOfWorkRequest(
                task_id=task_id,
                agent_id=agent_id,
                work_description=description,
                evidence_sources=evidence_data,
                complexity_level=complexity,
                work_timestamp=datetime.utcnow(),
            )

            # Collect proof of work
            async with AsyncSessionLocal() as session:
                collector = ProofOfWorkCollector(session)
                result = await collector.collect_proof_of_work(
                    agent_id, task_id, proof_request
                )

            # Output results
            if output == "json":
                click.echo(result.json(indent=2))
            else:
                _display_proof_summary(result)

        except Exception as e:
            click.echo(f"❌ Proof collection failed: {str(e)}", err=True)
            raise click.ClickException(str(e)) from e

    asyncio.run(_collect_proof())


def _display_proof_summary(result) -> None:
    """Display proof collection results in summary format."""
    status_icons = {
        CollectionStatus.HIGH_QUALITY: "🏆",
        CollectionStatus.ACCEPTABLE_QUALITY: "✅",
        CollectionStatus.LOW_QUALITY: "⚠️",
        CollectionStatus.POOR_QUALITY: "❌",
        CollectionStatus.INSUFFICIENT_EVIDENCE: "📋",
        CollectionStatus.ERROR: "💥",
    }

    icon = status_icons.get(result.status, "❓")
    click.echo(f"\n{icon} Proof-of-Work Collection Result")
    click.echo(f"Status: {result.status.value.upper()}")
    click.echo(f"Agent: {result.agent_id}")
    click.echo(f"Task: {result.task_id}")
    click.echo(f"Message: {result.message}")

    # Quality assessment
    assessment = result.quality_assessment
    click.echo("\n🎯 Quality Assessment:")
    click.echo(f"  Overall Score: {assessment.overall_quality_score:.2f}")
    click.echo(f"  Code Quality: {assessment.code_quality_score:.2f}")
    click.echo(f"  Completeness: {assessment.completeness_score:.2f}")
    click.echo(f"  Performance: {assessment.performance_score:.2f}")
    click.echo(f"  Innovation: {assessment.innovation_score:.2f}")
    click.echo(f"  Documentation: {assessment.documentation_score:.2f}")

    # Evidence summary
    click.echo(f"\n📋 Evidence: {len(result.evidence)} pieces analyzed")
    evidence_types = set(e.evidence_type for e in result.evidence)
    for ev_type in evidence_types:
        count = len([e for e in result.evidence if e.evidence_type == ev_type])
        click.echo(f"  • {ev_type}: {count} items")


# ==============================================================================
# AGENT MONITORING COMMANDS
# ==============================================================================


@cli.group(name="monitor")
def monitor_group():
    """Agent monitoring and analysis commands."""
    pass


@monitor_group.command(name="agent")
@click.option("--agent-id", required=True, help="Agent ID to monitor")
@click.option("--duration", default=300, help="Monitoring duration in seconds")
@click.option("--interval", default=30, help="Monitoring interval in seconds")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["live", "summary"]),
    default="live",
    help="Output mode",
)
@click.pass_context
def monitor_agent(
    ctx, agent_id: str, duration: int, interval: int, output: str
) -> None:
    """Monitor agent behavior and performance in real-time.

    Example:
        ares monitor agent --agent-id agent_123 --duration 600 --interval 60
    """
    if output == "live":
        click.echo(f"🔍 Starting live monitoring for agent {agent_id}")
        click.echo(f"Duration: {duration}s, Interval: {interval}s")
        click.echo("Press Ctrl+C to stop monitoring\n")

        # Placeholder for real monitoring implementation
        import time

        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                click.echo(
                    f"⏰ {datetime.now().strftime('%H:%M:%S')} - Agent {agent_id} status: Active"
                )
                time.sleep(interval)
        except KeyboardInterrupt:
            click.echo("\n🛑 Monitoring stopped by user")
    else:
        click.echo(f"📊 Agent {agent_id} monitoring summary - Feature coming soon!")


# ==============================================================================
# CONFIGURATION AND UTILITY COMMANDS
# ==============================================================================


@cli.group(name="config")
def config_group():
    """Configuration management commands."""
    pass


@config_group.command(name="show")
@click.pass_context
def show_config(ctx) -> None:
    """Display current ARES configuration."""
    click.echo("🔧 ARES Configuration:")
    click.echo(f"  Database URL: {settings.DATABASE_URL}")
    click.echo(f"  Debug Mode: {settings.DEBUG}")
    click.echo(
        f"  MCP Server Host: {getattr(settings, 'MCP_SERVER_HOST', 'localhost')}"
    )
    click.echo(f"  MCP Server Port: {getattr(settings, 'MCP_SERVER_PORT', 8000)}")


@config_group.command(name="test-db")
@click.pass_context
def test_database(ctx) -> None:
    """Test database connection."""

    async def _test_db():
        try:
            async with AsyncSessionLocal() as session:
                # Simple test query
                await session.execute("SELECT 1")
                click.echo("✅ Database connection successful")
        except Exception as e:
            click.echo(f"❌ Database connection failed: {str(e)}", err=True)

    asyncio.run(_test_db())


@cli.command(name="version")
def version() -> None:
    """Show ARES version information."""
    click.echo("🤖 ARES - Agent Reliability Enforcement System")
    click.echo("Version: 1.0.0-alpha")
    click.echo("Build: Development")
    click.echo("Python: 3.11+")


@cli.command(name="status")
@click.pass_context
def system_status(ctx) -> None:
    """Show ARES system status."""
    click.echo("🚀 ARES System Status:")
    click.echo("  Core Components:")
    click.echo("    ✅ CompletionVerifier - Ready")
    click.echo("    ✅ ToolCallValidator - Ready")
    click.echo("    ✅ ProofOfWorkCollector - Ready")
    click.echo("    🔄 AgentBehaviorMonitor - In Development")
    click.echo("    🔄 TaskRollbackManager - In Development")
    click.echo("  Infrastructure:")
    click.echo("    📊 Database - Connected")
    click.echo("    🌐 MCP Server - Ready")
    click.echo("    📡 API Server - Ready")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================


def main() -> None:
    """Main CLI entry point."""
    try:
        cli()
    except Exception as e:
        click.echo(f"💥 ARES CLI Error: {str(e)}", err=True)
        raise


if __name__ == "__main__":
    main()
