#!/usr/bin/env python3
"""
Vantara Commerce AI Governance Report Example

Problem: Vantara Commerce's legal and compliance team currently spends 21 days and 4
engineers manually assembling the quarterly AI governance report — pulling data from
vendor dashboards, Confluence pages, and Slack threads. The report covers: what AI is
running, what decisions it makes, whether humans are in the loop, and whether any
outputs could create regulatory exposure (FTC endorsement guidelines, state consumer
protection laws, algorithmic pricing scrutiny).

Briefcase AI generates this automatically from stored decision traces.

Demonstrates:
- Automated governance report generation from decision data
- Human-in-loop tracking and compliance gap identification
- Regulatory flag analysis for FTC and algorithmic pricing risks
- Vendor concentration risk assessment
- Complete audit trail documentation for regulatory readiness
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    import backend
    from backend import briefcase, DecisionSnapshot, SqliteBackend
    from backend import COMPANY, TEAMS, compute_cost, print_audit_summary
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)

# Set deterministic random seed for reproducible output
random.seed(42)

# Governance decision configuration exactly as specified in prompt
GOVERNANCE_CONFIG = [
    {"team": "search-ranking", "agent_name": "search-ranker-v8", "decision_category": "content_ranking",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "search-ranking", "agent_name": "search-ranker-v8", "decision_category": "content_ranking",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "product-recommendations", "agent_name": "collab-filter-recs", "decision_category": "personalization",
     "human_in_loop": False, "regulatory_flag": "ftc_endorsement_watch"},
    {"team": "product-recommendations", "agent_name": "collab-filter-recs", "decision_category": "personalization",
     "human_in_loop": False, "regulatory_flag": "ftc_endorsement_watch"},
    {"team": "product-recommendations", "agent_name": "collab-filter-recs", "decision_category": "personalization",
     "human_in_loop": True, "regulatory_flag": "ftc_endorsement_watch"},
    {"team": "dynamic-pricing", "agent_name": "real-time-pricer", "decision_category": "pricing",
     "human_in_loop": False, "regulatory_flag": "algorithmic_pricing_scrutiny"},
    {"team": "dynamic-pricing", "agent_name": "real-time-pricer", "decision_category": "pricing",
     "human_in_loop": False, "regulatory_flag": "algorithmic_pricing_scrutiny"},
    {"team": "dynamic-pricing", "agent_name": "real-time-pricer", "decision_category": "pricing",
     "human_in_loop": True, "regulatory_flag": "algorithmic_pricing_scrutiny"},
    {"team": "fraud-prevention", "agent_name": "checkout-fraud-v3", "decision_category": "risk_decision",
     "human_in_loop": True, "regulatory_flag": "none"},
    {"team": "fraud-prevention", "agent_name": "checkout-fraud-v3", "decision_category": "risk_decision",
     "human_in_loop": True, "regulatory_flag": "none"},
    {"team": "fraud-prevention", "agent_name": "checkout-fraud-v3", "decision_category": "risk_decision",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "returns-automation", "agent_name": "returns-classifier", "decision_category": "operational",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "returns-automation", "agent_name": "returns-classifier", "decision_category": "operational",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "demand-forecasting", "agent_name": "demand-lstm-wrapper", "decision_category": "forecasting",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "catalog-enrichment", "agent_name": "title-enricher-exp", "decision_category": "content_generation",
     "human_in_loop": False, "regulatory_flag": "ftc_endorsement_watch"},
    {"team": "customer-support-ai", "agent_name": "cx-triage-bot", "decision_category": "customer_interaction",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "inventory-replenishment", "agent_name": "reorder-point-ai", "decision_category": "operational",
     "human_in_loop": False, "regulatory_flag": "none"},
    {"team": "supplier-risk", "agent_name": "vendor-scorecard-ai", "decision_category": "risk_decision",
     "human_in_loop": True, "regulatory_flag": "none"}
]

# Model assignments for governance decisions
MODEL_ASSIGNMENTS = {
    "search-ranker-v8": {"vendor": "google-vertex", "model": "gemini-1.5-flash"},
    "collab-filter-recs": {"vendor": "openai", "model": "gpt-4o-mini"},
    "real-time-pricer": {"vendor": "openai", "model": "gpt-4o"},
    "checkout-fraud-v3": {"vendor": "anthropic", "model": "claude-3-haiku"},
    "returns-classifier": {"vendor": "cohere", "model": "command-r"},
    "demand-lstm-wrapper": {"vendor": "google-vertex", "model": "gemini-1.5-pro"},
    "title-enricher-exp": {"vendor": "openai", "model": "gpt-4o"},
    "cx-triage-bot": {"vendor": "anthropic", "model": "claude-3-5-sonnet"},
    "reorder-point-ai": {"vendor": "cohere", "model": "command-r-plus"},
    "vendor-scorecard-ai": {"vendor": "google-vertex", "model": "gemini-1.5-flash"}
}


def simulate_governance_decisions() -> List[DecisionSnapshot]:
    """
    Simulates 18 governance decisions across all 10 teams with regulatory metadata.

    Returns:
        List of DecisionSnapshot objects with governance information
    """
    decisions = []

    for i, config in enumerate(GOVERNANCE_CONFIG):
        # Get model assignment
        agent_name = config["agent_name"]
        model_info = MODEL_ASSIGNMENTS[agent_name]

        # Generate realistic token usage
        if config["decision_category"] in ["forecasting", "content_generation"]:
            # Larger token usage for complex tasks
            input_tokens = random.randint(2000, 6000)
            output_tokens = random.randint(500, 1500)
        else:
            # Standard token usage
            input_tokens = random.randint(150, 1500)
            output_tokens = random.randint(30, 500)

        # Calculate estimated cost
        try:
            input_cost, output_cost = compute_cost(
                model_info["vendor"],
                model_info["model"],
                input_tokens,
                output_tokens
            )
            estimated_cost_usd = input_cost + output_cost
        except ValueError:
            estimated_cost_usd = 0.001  # Fallback cost

        # Generate decision timestamp within last 90 days
        now = datetime.now()
        days_ago = random.randint(0, 89)
        decision_timestamp = now - timedelta(days=days_ago)

        # Generate realistic customer segment
        if config["decision_category"] in ["personalization", "pricing", "content_ranking"]:
            customer_segment = random.choice(["high_ltv", "first_time_visitor", "returning_lapsed", "price_sensitive"])
        else:
            customer_segment = "not_applicable"

        # Determine compliance gaps
        compliance_gaps = []
        if config["regulatory_flag"] != "none" and not config["human_in_loop"]:
            compliance_gaps = ["human_review_recommended"]

        # Create decision inputs
        inputs = {
            "team_name": config["team"],
            "agent_name": agent_name,
            "decision_category": config["decision_category"],
            "human_in_loop": config["human_in_loop"],
            "regulatory_flag": config["regulatory_flag"],
            "vendor": model_info["vendor"],
            "model_name": model_info["model"],
            "model_version": generate_model_version(agent_name),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "customer_segment": customer_segment,
            "decision_timestamp": decision_timestamp.isoformat()
        }

        # Create decision outputs
        outputs = {
            "governance_record_id": str(uuid.uuid4()),
            "report_ready": True,
            "compliance_gaps": compliance_gaps,
            "regulatory_flag": config["regulatory_flag"]
        }

        # Create metadata for governance tracking
        metadata = {
            "function_type": "governance_report",
            "company": COMPANY["name"],
            "report_period": "Last 90 Days",
            "compliance_framework": "FTC_ALGORITHMIC_PRICING",
            "report_generation_method": "automated_briefcase"
        }

        # Create decision snapshot using instrumented pattern
        decision = backend.create_instrumented_decision(
            function_name="governance_decision_tracking",
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
            vendor=model_info["vendor"],
            model=model_info["model"]
        )

        decisions.append(decision)

    return decisions


def generate_model_version(agent_name: str) -> str:
    """Generate consistent model versions for agents."""
    version_map = {
        "search-ranker-v8": "v8.2.1-stable",
        "collab-filter-recs": "recs-v12.0",
        "real-time-pricer": "pricing-v4.1.2",
        "checkout-fraud-v3": "fraud-v3.0.1",
        "returns-classifier": "returns-v2.3.0",
        "demand-lstm-wrapper": "forecast-v1.8.4",
        "title-enricher-exp": "enricher-v0.5.0-exp",
        "cx-triage-bot": "support-v2.1.0",
        "reorder-point-ai": "inventory-v1.2.0",
        "vendor-scorecard-ai": "risk-v3.4.1"
    }
    return version_map.get(agent_name, "v1.0.0")


def print_governance_report(decisions: List[DecisionSnapshot]) -> None:
    """
    Prints the comprehensive governance report exactly as specified in the prompt.

    Args:
        decisions: List of DecisionSnapshot objects with governance data
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate summary statistics
    total_decisions = len(decisions)
    total_spend = sum(float(d.inputs[10].value) for d in decisions)
    unique_agents = len(set(d.inputs[1].value for d in decisions))
    teams_with_ai = len(set(d.inputs[0].value for d in decisions))
    hil_count = sum(1 for d in decisions if d.inputs[3].value == "True")
    hil_rate = (hil_count / total_decisions) * 100
    reg_flag_count = sum(1 for d in decisions if d.inputs[4].value != "none")
    reg_flag_pct = (reg_flag_count / total_decisions) * 100

    print("=== VANTARA COMMERCE — AI GOVERNANCE REPORT ===")
    print(f"Period: Last 90 Days")
    print(f"Generated: {timestamp}")
    print()

    print("--- SECTION 1: EXECUTIVE SUMMARY ---")
    print(f"Total AI decisions captured:        {total_decisions}")
    print(f"Total AI spend (sample):            ${total_spend:.4f}")
    print(f"Estimated fleet-wide monthly spend: $316,667")
    print(f"Unique AI agents active:            {unique_agents}")
    print(f"Teams with AI deployments:          {teams_with_ai} of {len(TEAMS)}")
    print(f"Overall human-in-loop rate:         {hil_rate:.0f}%")
    print(f"Decisions with regulatory flags:    {reg_flag_count} ({reg_flag_pct:.0f}%)")
    print()

    # Team breakdown
    print("--- SECTION 2: TEAM BREAKDOWN ---")
    team_stats = {}
    for decision in decisions:
        team = decision.inputs[0].value
        agent = decision.inputs[1].value
        cost = float(decision.inputs[10].value)
        hil = decision.inputs[3].value == "True"
        reg_flag = decision.inputs[4].value

        if team not in team_stats:
            team_stats[team] = {
                "agents": set(),
                "decisions": 0,
                "spend": 0.0,
                "hil_count": 0,
                "reg_flags": set()
            }

        team_stats[team]["agents"].add(agent)
        team_stats[team]["decisions"] += 1
        team_stats[team]["spend"] += cost
        if hil:
            team_stats[team]["hil_count"] += 1
        if reg_flag != "none":
            team_stats[team]["reg_flags"].add(reg_flag)

    print("  Team                         Agents  Decisions  Spend        HiL Rate  Reg Flags")
    print("  ---------------------------- ------- ---------- ------------ --------- ---------")
    for team in sorted(team_stats.keys()):
        stats = team_stats[team]
        agents_count = len(stats["agents"])
        decisions_count = stats["decisions"]
        spend = stats["spend"]
        hil_rate = (stats["hil_count"] / decisions_count) * 100
        reg_flags = len(stats["reg_flags"])

        print(f"  {team:<28} {agents_count:>7} {decisions_count:>10} ${spend:>10.4f} {hil_rate:>8.0f}%  {reg_flags}")
    print()

    # Regulatory risk flags
    print("--- SECTION 3: REGULATORY RISK FLAGS ---")

    # Analyze regulatory risks
    ftc_decisions = [d for d in decisions if d.inputs[4].value == "ftc_endorsement_watch"]
    pricing_decisions = [d for d in decisions if d.inputs[4].value == "algorithmic_pricing_scrutiny"]

    # FTC endorsement risk
    ftc_no_hil = [d for d in ftc_decisions if d.inputs[3].value == "False"]
    print(f"  [HIGH]  product-recommendations: {len(ftc_no_hil)} of {len(ftc_decisions)} personalization decisions had no human review")
    print("          Regulatory exposure: FTC Endorsement Guidelines (§255) — AI-generated recommendations")
    print("          without human oversight may require disclosure")

    # Algorithmic pricing risk
    pricing_no_hil = [d for d in pricing_decisions if d.inputs[3].value == "False"]
    print(f"  [HIGH]  dynamic-pricing: {len(pricing_no_hil)} of {len(pricing_decisions)} pricing decisions had no human review")
    print("          Regulatory exposure: Algorithmic pricing scrutiny (FTC, DOJ, state AGs)")
    print("          Automated price decisions without audit trail create antitrust risk")

    # Catalog enrichment risk
    enrichment_decisions = [d for d in decisions if d.inputs[1].value == "title-enricher-exp"]
    if enrichment_decisions:
        print("  [MED]   catalog-enrichment: title-enricher-exp (experiment agent) generating customer-facing")
        print("          content — FTC endorsement watch active, compliance gap: human_review_recommended")
    print()

    # Agent risk summary
    print("--- SECTION 4: AGENT RISK SUMMARY ---")
    print("  Agents with regulatory flags + no human review:")

    # Find risky agents
    risky_agents = {}
    for decision in decisions:
        agent = decision.inputs[1].value
        team = decision.inputs[0].value
        reg_flag = decision.inputs[4].value
        hil = decision.inputs[3].value == "True"

        if reg_flag != "none":
            if agent not in risky_agents:
                risky_agents[agent] = {"team": team, "reg_flag": reg_flag, "hil_count": 0, "total": 0}
            risky_agents[agent]["total"] += 1
            if hil:
                risky_agents[agent]["hil_count"] += 1

    for agent, stats in risky_agents.items():
        hil_rate = (stats["hil_count"] / stats["total"]) * 100
        print(f"    - {agent:<18} ({stats['team']}): {stats['reg_flag']}, HiL rate {hil_rate:.0f}%")
    print()

    # Vendor concentration
    print("--- SECTION 5: VENDOR CONCENTRATION ---")
    vendor_counts = {}
    for decision in decisions:
        vendor = decision.inputs[5].value
        vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

    for vendor, count in sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_decisions) * 100
        print(f"  {vendor}: {pct:.0f}% of decisions")

    max_vendor_pct = max(vendor_counts.values()) / total_decisions * 100
    if max_vendor_pct > 60:
        print(f"  [WARNING] High vendor concentration detected")
    print()

    # Report certification
    print("--- SECTION 6: REPORT CERTIFICATION ---")
    print(f"  Company:                       {COMPANY['name']}")
    print(f"  Report generated:              {timestamp}")
    print("  Data source:                   Briefcase AI decision trace ledger")
    print(f"  Records retrieved:             {total_decisions}")
    print("  Manual engineering required:   NONE")
    print("  Time to generate:              < 1 second")
    print()
    print(f"  Previous manual process:       {COMPANY['days_to_compile_report_manually']} days, {COMPANY['engineers_per_compliance_report']} engineers")
    print("  With Briefcase AI:             < 1 second, 0 engineers")
    print()
    print("  All records are immutable and retrievable on demand by governance_record_id.")
    print("===============================================")


def main():
    """Main execution function for governance report demonstration."""
    print("=== Vantara Commerce AI Governance Report Generation ===")
    print("Demonstrates: Automated compliance reporting from decision audit trails\n")

    # Initialize Briefcase AI SDK
    try:
        briefcase.init_with_config(2)
        print("SUCCESS: Briefcase AI SDK initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize SDK: {e}")
        sys.exit(1)

    # Get backend for storage
    backend_instance = backend.get_backend()
    print("SUCCESS: In-memory SQLite backend configured\n")

    # Simulate governance decision tracking
    print("Simulating AI governance decision tracking across 10 teams...")
    print("Tracking human-in-loop rates, regulatory flags, and compliance gaps...")

    governance_decisions = simulate_governance_decisions()
    print(f"SUCCESS: Generated {len(governance_decisions)} governance-tracked decisions")

    # Store all decisions in backend
    stored_decision_ids = []
    for decision in governance_decisions:
        if hasattr(backend_instance, 'save_decision'):
            decision_id = backend_instance.save_decision(decision)
        else:
            decision_id = backend_instance.store_decision(decision)
        stored_decision_ids.append(decision_id)
        team = decision.inputs[0].value
        agent = decision.inputs[1].value
        reg_flag = decision.inputs[4].value
        print_audit_summary(decision_id, f"{team}/{agent} ({reg_flag})")

    print()

    # Generate comprehensive governance report
    print_governance_report(governance_decisions)
    print()

    # Demonstrate governance record retrieval
    print("GOVERNANCE AUDIT TRAIL VERIFICATION:")
    print("Loading governance records by governance_record_id:")
    print("=" * 60)

    verification_count = 0
    for i, decision in enumerate(governance_decisions[-5:]):  # Check last 5 decisions
        gov_record_id = decision.outputs[0].value  # governance_record_id
        # Get the stored decision ID from the list
        decision_idx = len(governance_decisions) - 5 + i
        stored_decision_id = stored_decision_ids[decision_idx]
        retrieved_decision = backend_instance.load_decision(stored_decision_id)

        if retrieved_decision:
            team = retrieved_decision.inputs[0].value
            agent = retrieved_decision.inputs[1].value
            reg_flag = retrieved_decision.inputs[4].value
            hil = retrieved_decision.inputs[3].value
            verification_count += 1

            print(f"[VERIFY] {team}/{agent} | regulatory_flag={reg_flag} | human_in_loop={hil} | gov_record_id={gov_record_id} | retrieved OK")
        else:
            print(f"[ERROR] Failed to retrieve governance record {gov_record_id}")

    print()

    # Demonstrate compliance gap analysis
    print("COMPLIANCE GAP ANALYSIS:")
    print("Analyzing decisions with regulatory flags but no human review:")
    print("=" * 60)

    gap_count = 0
    for decision in governance_decisions:
        compliance_gaps = decision.outputs[2].value  # compliance_gaps field
        if compliance_gaps and compliance_gaps != "[]":  # Has compliance gaps
            team = decision.inputs[0].value
            agent = decision.inputs[1].value
            reg_flag = decision.inputs[4].value
            gap_count += 1

            print(f"[GAP] {team}/{agent} | {reg_flag} | gap: human_review_recommended")

    print(f"\nTotal compliance gaps identified: {gap_count}")
    print(f"Recommendations generated for regulatory review")

    print(f"\nSUCCESS: Governance report generation completed")
    print(f"Manual process: {COMPANY['days_to_compile_report_manually']} days, {COMPANY['engineers_per_compliance_report']} engineers")
    print("Briefcase AI process: < 1 second, 0 engineers")
    print(f"Time savings: {COMPANY['days_to_compile_report_manually'] * 8 * COMPANY['engineers_per_compliance_report']} engineer-hours per report")


if __name__ == "__main__":
    main()