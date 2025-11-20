#!/usr/bin/env python3
"""
Main CLI entry point for Briefcase AI Telemetry tools.
"""

import click
import sys
import os

# Add the SDK to the Python path
current_dir = os.path.dirname(__file__)
sdk_path = os.path.join(current_dir, '..', '..', 'python')
sys.path.insert(0, sdk_path)

from .commands import init, monitor, analyze, config

@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx):
    """
    🔭 Briefcase AI Telemetry CLI

    Developer tools for AI agent observability, monitoring, and configuration.
    Built with high-performance Rust core for minimal overhead.
    """
    ctx.ensure_object(dict)

# Register commands
cli.add_command(init.init)
cli.add_command(monitor.monitor)
cli.add_command(analyze.analyze)
cli.add_command(config.config)

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main()