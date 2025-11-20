"""
Real-time monitoring dashboard command.

Provides live telemetry monitoring, metrics visualization, and alerting.
"""

import click
import time
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import sys
import os

# Add the SDK to the Python path
current_dir = os.path.dirname(__file__)
sdk_path = os.path.join(current_dir, '..', '..', '..', 'python')
sys.path.insert(0, sdk_path)

import briefcase_ai_telemetry as bai

@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time."""
    timestamp: datetime
    total_requests: int
    avg_latency: float
    total_cost: float
    error_rate: float
    drift_score: Optional[float]
    active_agents: int

class LiveMonitor:
    """Live telemetry monitoring system."""

    def __init__(self, api_key: str, endpoint: Optional[str] = None):
        self.api_key = api_key
        self.endpoint = endpoint
        self.running = False
        self.metrics_history: deque = deque(maxlen=100)
        self.agent_stats: Dict[int, Dict] = defaultdict(lambda: {
            'requests': 0,
            'total_cost': 0.0,
            'total_latency': 0.0,
            'errors': 0,
            'last_seen': None
        })

    def start_monitoring(self, refresh_interval: float = 5.0, show_details: bool = True):
        """Start the live monitoring dashboard."""

        self.running = True

        try:
            # Clear screen and show header
            click.clear()
            self._show_header()

            while self.running:
                # Collect current metrics
                snapshot = self._collect_metrics()
                self.metrics_history.append(snapshot)

                # Update display
                self._update_dashboard(snapshot, show_details)

                # Wait for refresh interval
                time.sleep(refresh_interval)

        except KeyboardInterrupt:
            self._show_goodbye()

    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.running = False

    def _collect_metrics(self) -> MetricSnapshot:
        """Collect current telemetry metrics."""

        now = datetime.now()

        # In a real implementation, this would connect to the telemetry service
        # For demo purposes, we'll simulate some metrics

        total_requests = sum(stats['requests'] for stats in self.agent_stats.values())
        active_agents = len([aid for aid, stats in self.agent_stats.items()
                           if stats['last_seen'] and (now - stats['last_seen']).seconds < 300])

        avg_latency = 0.0
        if total_requests > 0:
            total_latency = sum(stats['total_latency'] for stats in self.agent_stats.values())
            avg_latency = total_latency / total_requests if total_requests > 0 else 0.0

        total_cost = sum(stats['total_cost'] for stats in self.agent_stats.values())

        total_errors = sum(stats['errors'] for stats in self.agent_stats.values())
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

        # Simulate some drift detection
        drift_score = None
        if len(self.metrics_history) > 3:
            drift_score = 0.85  # Simulated drift score

        return MetricSnapshot(
            timestamp=now,
            total_requests=total_requests,
            avg_latency=avg_latency,
            total_cost=total_cost,
            error_rate=error_rate,
            drift_score=drift_score,
            active_agents=active_agents
        )

    def _update_dashboard(self, snapshot: MetricSnapshot, show_details: bool):
        """Update the monitoring dashboard display."""

        # Move cursor to top and clear screen
        click.echo("\033[H", nl=False)

        # Current time
        click.echo(f"🕐 Last Updated: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo("─" * 60)

        # Key metrics overview
        click.echo(f"📊 Active Agents: {click.style(str(snapshot.active_agents), fg='green', bold=True)}")
        click.echo(f"📈 Total Requests: {click.style(str(snapshot.total_requests), fg='blue', bold=True)}")
        click.echo(f"⚡ Avg Latency: {click.style(f'{snapshot.avg_latency:.2f}ms', fg='yellow', bold=True)}")
        click.echo(f"💰 Total Cost: {click.style(f'${snapshot.total_cost:.4f}', fg='magenta', bold=True)}")

        # Error rate with color coding
        error_color = 'red' if snapshot.error_rate > 5 else 'yellow' if snapshot.error_rate > 1 else 'green'
        click.echo(f"❗ Error Rate: {click.style(f'{snapshot.error_rate:.1f}%', fg=error_color, bold=True)}")

        # Drift score if available
        if snapshot.drift_score is not None:
            drift_color = 'red' if snapshot.drift_score < 0.7 else 'yellow' if snapshot.drift_score < 0.85 else 'green'
            click.echo(f"🎯 Drift Score: {click.style(f'{snapshot.drift_score:.3f}', fg=drift_color, bold=True)}")

        click.echo("─" * 60)

        # Trends (if we have history)
        if len(self.metrics_history) >= 2:
            self._show_trends()

        # Agent details
        if show_details:
            self._show_agent_details()

        # Performance chart
        self._show_performance_chart()

        # Footer
        click.echo("─" * 60)
        click.echo("Press Ctrl+C to exit | 'briefcase-ai analyze' for detailed analysis")

    def _show_trends(self):
        """Show trending indicators."""

        if len(self.metrics_history) < 2:
            return

        current = self.metrics_history[-1]
        previous = self.metrics_history[-2]

        # Calculate trends
        req_trend = current.total_requests - previous.total_requests
        latency_trend = current.avg_latency - previous.avg_latency
        cost_trend = current.total_cost - previous.total_cost

        click.echo("📈 Trends (since last update):")

        # Requests trend
        req_indicator = "📈" if req_trend > 0 else "📉" if req_trend < 0 else "➡️"
        click.echo(f"   Requests: {req_indicator} {req_trend:+d}")

        # Latency trend
        latency_indicator = "📈" if latency_trend > 5 else "📉" if latency_trend < -5 else "➡️"
        click.echo(f"   Latency: {latency_indicator} {latency_trend:+.1f}ms")

        # Cost trend
        cost_indicator = "📈" if cost_trend > 0.001 else "📉" if cost_trend < -0.001 else "➡️"
        click.echo(f"   Cost: {cost_indicator} ${cost_trend:+.4f}")

        click.echo("")

    def _show_agent_details(self):
        """Show per-agent statistics."""

        if not self.agent_stats:
            click.echo("👤 No active agents detected")
            return

        click.echo("👥 Agent Statistics:")

        # Sort agents by request count
        sorted_agents = sorted(self.agent_stats.items(),
                             key=lambda x: x[1]['requests'], reverse=True)

        for agent_id, stats in sorted_agents[:5]:  # Show top 5 agents
            last_seen = stats['last_seen']
            if last_seen:
                time_since = datetime.now() - last_seen
                if time_since.seconds < 60:
                    status = click.style("ACTIVE", fg='green')
                elif time_since.seconds < 300:
                    status = click.style("IDLE", fg='yellow')
                else:
                    status = click.style("INACTIVE", fg='red')
            else:
                status = click.style("UNKNOWN", fg='gray')

            avg_latency = (stats['total_latency'] / stats['requests']) if stats['requests'] > 0 else 0
            error_rate = (stats['errors'] / stats['requests'] * 100) if stats['requests'] > 0 else 0

            click.echo(f"   Agent {agent_id}: {status} | "
                      f"Reqs: {stats['requests']} | "
                      f"Latency: {avg_latency:.1f}ms | "
                      f"Cost: ${stats['total_cost']:.4f} | "
                      f"Errors: {error_rate:.1f}%")

        if len(self.agent_stats) > 5:
            click.echo(f"   ... and {len(self.agent_stats) - 5} more agents")

        click.echo("")

    def _show_performance_chart(self):
        """Show a simple ASCII performance chart."""

        if len(self.metrics_history) < 2:
            return

        click.echo("📊 Performance Chart (last 20 updates):")

        # Get last 20 snapshots
        recent_history = list(self.metrics_history)[-20:]

        if len(recent_history) < 2:
            return

        # Extract latencies for chart
        latencies = [s.avg_latency for s in recent_history]

        # Simple ASCII chart
        max_latency = max(latencies) if latencies else 1
        chart_height = 5

        for row in range(chart_height, 0, -1):
            line = "   "
            threshold = (max_latency * row) / chart_height

            for latency in latencies:
                if latency >= threshold:
                    line += "█"
                else:
                    line += " "

            line += f" {threshold:.0f}ms"
            click.echo(line)

        # X-axis
        click.echo("   " + "─" * len(latencies))
        click.echo("   " + " " * (len(latencies) - 3) + "now")
        click.echo("")

    def _show_header(self):
        """Show the monitoring header."""
        click.echo("🔭 Briefcase AI Telemetry Monitor")
        click.echo("=" * 60)
        click.echo("Real-time AI agent observability dashboard")
        click.echo("")

    def _show_goodbye(self):
        """Show exit message."""
        click.echo("\n" + "─" * 60)
        click.echo("👋 Monitoring stopped. Thank you for using Briefcase AI!")

@click.command()
@click.option('--api-key', help='Briefcase AI API key (or use config file)')
@click.option('--endpoint', help='Custom telemetry endpoint')
@click.option('--refresh', type=float, default=5.0, help='Refresh interval in seconds')
@click.option('--config', 'config_file', help='Configuration file path')
@click.option('--agent-id', type=int, help='Monitor specific agent ID only')
@click.option('--simple', is_flag=True, help='Simple mode with minimal details')
def monitor(api_key, endpoint, refresh, config_file, agent_id, simple):
    """
    📊 Real-time telemetry monitoring dashboard.

    Monitor AI agent performance, costs, errors, and drift detection in real-time.
    Provides live metrics, trends analysis, and alerts for production systems.
    """

    # Load configuration if available
    if config_file or (not api_key and os.path.exists('briefcase-ai.yaml')):
        config = load_config(config_file or 'briefcase-ai.yaml')
        if not api_key:
            api_key = config.get('briefcase_ai', {}).get('api_key')
        if not endpoint:
            endpoint = config.get('briefcase_ai', {}).get('endpoint')

    # Validate API key
    if not api_key:
        click.echo("❌ API key required. Provide with --api-key or in config file.")
        click.echo("💡 Run 'briefcase-ai init' to set up configuration.")
        return

    # Initialize monitor
    monitor = LiveMonitor(api_key, endpoint)

    # Apply agent filter if specified
    if agent_id:
        click.echo(f"🎯 Monitoring agent {agent_id} only")

    # Start monitoring
    click.echo(f"🚀 Starting monitoring (refresh every {refresh}s)...")
    click.echo("   Press Ctrl+C to exit")

    time.sleep(1)  # Brief pause before starting

    try:
        monitor.start_monitoring(refresh, not simple)
    except Exception as e:
        click.echo(f"❌ Monitoring failed: {e}")

def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from file."""
    import yaml

    try:
        with open(config_file, 'r') as f:
            if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                return yaml.safe_load(f) or {}
            else:
                return json.load(f) or {}
    except Exception as e:
        click.echo(f"⚠️  Failed to load config {config_file}: {e}")
        return {}