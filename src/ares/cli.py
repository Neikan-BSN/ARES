"""Command line interface for ARES - Agent Reliability Enforcement System."""

import click


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(verbose: bool) -> None:
    """ARES CLI - Agent Reliability Enforcement System."""
    if verbose:
        click.echo("Starting ARES in verbose mode...")
    else:
        click.echo("Hello from ARES - Agent Reliability Enforcement System!")


if __name__ == "__main__":
    main()

