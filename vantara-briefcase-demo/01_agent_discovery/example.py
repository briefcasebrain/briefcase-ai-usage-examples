#!/usr/bin/env python3
"""
Vantara Commerce AI Agent Discovery Example

Problem: Vantara Commerce has 45 product teams. Each team ships AI features independently.
There is no central registry — the AI governance team cannot answer "how many AI models are
running in production right now, who owns them, and which vendors power them?"

When a new agent is deployed, it registers itself with Briefcase AI by creating a
DecisionSnapshot at first execution. This builds a self-populating, always-current ledger
without requiring cloud account access.

Demonstrates:
- Self-populating agent registry through decision capture
- Shadow AI detection (previously unknown agents)
- Zero IT access discovery method
- Complete audit trail for governance teams
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

try:
    import backend
    from backend import briefcase_ai, DecisionSnapshot, SqliteBackend
    from backend import COMPANY, TEAMS, print_audit_summary
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)

# Set deterministic random seed for reproducible output
random.seed(42)

# Agent configuration table exactly as specified in prompt
AGENTS_CONFIG = [
    {"agent_name": "search-ranker-v8", "team": "search-ranking", "vendor": "google-vertex",
     "model": "gemini-1.5-flash", "environment": "production", "deployment_type": "instrumented",
     "was_previously_known": True, "estimated_daily_decisions": 2500000},
    {"agent_name": "collab-filter-recs", "team": "product-recommendations", "vendor": "openai",
     "model": "gpt-4o-mini", "environment": "production", "deployment_type": "instrumented",
     "was_previously_known": True, "estimated_daily_decisions": 1800000},
    {"agent_name": "real-time-pricer", "team": "dynamic-pricing", "vendor": "openai",
     "model": "gpt-4o", "environment": "production", "deployment_type": "discovered_via_output_stream",
     "was_previously_known": True, "estimated_daily_decisions": 5000000},
    {"agent_name": "checkout-fraud-v3", "team": "fraud-prevention", "vendor": "anthropic",
     "model": "claude-3-haiku", "environment": "production", "deployment_type": "instrumented",
     "was_previously_known": True, "estimated_daily_decisions": 3200000},
    {"agent_name": "returns-classifier", "team": "returns-automation", "vendor": "cohere",
     "model": "command-r", "environment": "production", "deployment_type": "instrumented",
     "was_previously_known": True, "estimated_daily_decisions": 15000},
    {"agent_name": "demand-lstm-wrapper", "team": "demand-forecasting", "vendor": "google-vertex",
     "model": "gemini-1.5-pro", "environment": "production", "deployment_type": "discovered_via_output_stream",
     "was_previously_known": True, "estimated_daily_decisions": 2500},
    {"agent_name": "title-enricher-exp", "team": "catalog-enrichment", "vendor": "openai",
     "model": "gpt-4o", "environment": "experiment", "deployment_type": "instrumented",
     "was_previously_known": False, "estimated_daily_decisions": 8000},
    {"agent_name": "cx-triage-bot", "team": "customer-support-ai", "vendor": "anthropic",
     "model": "claude-3-5-sonnet", "environment": "production", "deployment_type": "instrumented",
     "was_previously_known": True, "estimated_daily_decisions": 45000},
    {"agent_name": "reorder-point-ai", "team": "inventory-replenishment", "vendor": "cohere",
     "model": "command-r-plus", "environment": "staging", "deployment_type": "discovered_via_output_stream",
     "was_previously_known": False, "estimated_daily_decisions": 1200},
    {"agent_name": "vendor-scorecard-ai", "team": "supplier-risk", "vendor": "google-vertex",
     "model": "gemini-1.5-flash", "environment": "staging", "deployment_type": "instrumented",
     "was_previously_known": True, "estimated_daily_decisions": 800}
]


def simulate_agent_discovery() -> List[DecisionSnapshot]:
    """
    Simulates the agent discovery process by creating DecisionSnapshot records
    for each AI agent in the Vantara Commerce ecosystem.

    Returns:
        List of DecisionSnapshot objects representing discovered agents
    """
    discovered_agents = []

    for agent_config in AGENTS_CONFIG:
        # Generate realistic registration data
        agent_id = str(uuid.uuid4())
        registered_by = generate_employee_email(agent_config["team"])
        first_seen_timestamp = generate_discovery_timestamp()

        # Create governance inputs for agent registration
        inputs = {
            "agent_id": agent_id,
            "agent_name": agent_config["agent_name"],
            "team_name": agent_config["team"],
            "vendor": agent_config["vendor"],
            "model_name": agent_config["model"],
            "environment": agent_config["environment"],
            "registered_by": registered_by,
            "first_seen_timestamp": first_seen_timestamp,
            "deployment_type": agent_config["deployment_type"],
            "estimated_daily_decisions": agent_config["estimated_daily_decisions"]
        }

        # Create governance outputs for discovery results
        outputs = {
            "execution_result": "success",
            "was_previously_known": agent_config["was_previously_known"],
            "governance_record_id": str(uuid.uuid4())
        }

        # Create metadata for governance tracking
        metadata = {
            "function_type": "agent_discovery",
            "company": COMPANY["name"],
            "discovery_method": agent_config["deployment_type"],
            "governance_category": "agent_registry",
            "compliance_status": "tracked"
        }

        # Create decision snapshot for audit trail
        decision = backend.create_decision_snapshot(
            function_name="agent_discovery_registration",
            inputs=inputs,
            outputs=outputs,
            metadata=metadata
        )

        discovered_agents.append(decision)

    return discovered_agents


def generate_employee_email(team_name: str) -> str:
    """Generate a realistic employee email for the given team."""
    first_names = ["sarah", "james", "maria", "david", "jennifer", "michael", "lisa", "robert"]
    last_names = ["chen", "johnson", "garcia", "williams", "brown", "jones", "miller", "davis"]

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return f"{first_name}.{last_name}@vantara.com"


def generate_discovery_timestamp() -> str:
    """Generate a timestamp within the last 90 days."""
    now = datetime.now()
    days_ago = random.randint(1, 90)
    discovery_date = now - timedelta(days=days_ago)
    return discovery_date.isoformat()


def print_discovery_report(agents: List[DecisionSnapshot], backend_instance: SqliteBackend) -> None:
    """
    Prints the agent discovery report as specified in the prompt.

    Args:
        agents: List of discovered agent DecisionSnapshot objects
        backend_instance: Backend instance for retrieving stored decisions
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate report statistics
    teams_with_ai = len(set(agent.inputs[2].value for agent in agents))  # team_name
    total_daily_decisions = sum(int(agent.inputs[9].value) for agent in agents)  # estimated_daily_decisions
    shadow_agents = [agent for agent in agents if agent.outputs[1].value == "False"]  # was_previously_known

    print("=== VANTARA COMMERCE — AI AGENT AUDIT REPORT ===")
    print(f"Generated: {timestamp}")
    print(f"Total agents discovered: {len(agents)}")
    print(f"Teams with active AI deployments: {teams_with_ai} of {len(TEAMS)}")
    print()

    print("AGENTS BY TEAM (sorted alphabetically):")
    # Sort agents by team name for consistent output
    sorted_agents = sorted(agents, key=lambda x: x.inputs[2].value)  # team_name

    for agent in sorted_agents:
        team_name = agent.inputs[2].value
        agent_name = agent.inputs[1].value
        vendor = agent.inputs[3].value
        model = agent.inputs[4].value
        environment = agent.inputs[5].value
        deployment_type = agent.inputs[8].value

        print(f"  {team_name:<35} {agent_name:<30} {vendor}/{model:<25} {environment:<12} {deployment_type}")

    print()
    print(f"ESTIMATED DAILY AI DECISIONS ACROSS FLEET: {total_daily_decisions:,}")
    print()

    # Shadow AI section
    print(f"SHADOW AI — PREVIOUSLY UNKNOWN AGENTS ({len(shadow_agents)}):")
    for agent in shadow_agents:
        agent_name = agent.inputs[1].value
        team_name = agent.inputs[2].value
        first_seen = agent.inputs[7].value[:10]  # Just the date part
        environment = agent.inputs[5].value
        print(f"  [!] {agent_name:<20} ({team_name})<TRUNCATED>")
    print()

    # Risk flags section
    print("RISK FLAGS:")
    for agent in agents:
        agent_name = agent.inputs[1].value
        environment = agent.inputs[5].value
        model = agent.inputs[4].value
        deployment_type = agent.inputs[8].value

        if agent_name == "title-enricher-exp":
            print(f"  [!] {agent_name}: experiment agent using {model} (premium model) — no cost controls confirmed")
        elif agent_name == "reorder-point-ai":
            print(f"  [!] {agent_name}: staging agent writing to output stream observed in production pipeline")
    print()

    # Discovery method summary
    instrumented_count = sum(1 for agent in agents if agent.inputs[8].value == "instrumented")
    stream_count = len(agents) - instrumented_count

    print("DISCOVERY METHOD:")
    print(f"  {instrumented_count} agents: SDK instrumentation (zero IT access required)")
    print(f"  {stream_count} agents: output stream listener (Prometheus/Grafana)")
    print("  Cloud account access required: NONE")
    print()
    print("Full audit trail stored in Briefcase AI. All records retrievable by governance_record_id.")
    print("=================================================")


def main():
    """Main execution function for agent discovery demonstration."""
    print("=== Vantara Commerce AI Agent Discovery ===")
    print("Demonstrates: Self-populating agent registry with zero IT access\n")

    # Initialize Briefcase AI SDK
    try:
        briefcase_ai.init_with_config(2)
        print("SUCCESS: Briefcase AI SDK initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize SDK: {e}")
        sys.exit(1)

    # Get backend for storage
    backend_instance = backend.get_backend()
    print("SUCCESS: In-memory SQLite backend configured\n")

    # Simulate agent discovery process
    print("Running agent discovery across Vantara Commerce teams...")
    discovered_agents = simulate_agent_discovery()
    print(f"SUCCESS: Discovered {len(discovered_agents)} AI agents")

    # Store all agent records in backend
    stored_decision_ids = []
    for agent in discovered_agents:
        decision_id = backend_instance.save_decision(agent)
        stored_decision_ids.append(decision_id)
        print_audit_summary(decision_id, f"Agent {agent.inputs[1].value} registered")

    print()

    # Generate and display discovery report
    print_discovery_report(discovered_agents, backend_instance)
    print()

    # Demonstrate audit trail retrieval
    print("AUDIT TRAIL VERIFICATION:")
    print("Loading each agent record by governance_record_id:")

    for i, decision_id in enumerate(stored_decision_ids):
        retrieved_agent = backend_instance.load_decision(decision_id)
        if retrieved_agent:
            agent_name = retrieved_agent.inputs[1].value
            team_name = retrieved_agent.inputs[2].value
            print(f"[AUDIT] Agent {i+1:2d}: {agent_name} ({team_name}) | decision_id={decision_id} | retrieved OK")
        else:
            print(f"[ERROR] Failed to retrieve decision {decision_id}")

    print(f"\nSUCCESS: Agent discovery demonstration completed")
    print(f"All {len(discovered_agents)} agents tracked in immutable audit trail")


if __name__ == "__main__":
    main()