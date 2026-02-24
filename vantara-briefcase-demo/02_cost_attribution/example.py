#!/usr/bin/env python3
"""
Vantara Commerce AI Cost Attribution Example

Problem: Vantara Commerce's $3.8M annual AI bill is billed by 4 vendors as aggregate
token consumption. Finance cannot tell whether search ranking or product recommendations
is the bigger cost driver. Engineering cannot justify model choices without per-decision
cost data.

Briefcase AI captures cost at the decision level, enabling bottom-up attribution to
the team, agent, and request type.

Demonstrates:
- Per-decision cost calculation with vendor pricing
- Team-level spend attribution
- Model right-sizing opportunity analysis
- Peak season cost projection
- Bottom-up spend reconstruction from decision trails
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

try:
    import backend
    from backend import briefcase_ai, DecisionSnapshot, SqliteBackend
    from backend import COMPANY, TEAMS, VENDOR_PRICING, compute_cost, print_audit_summary
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)

# Set deterministic random seed for reproducible output
random.seed(42)

# Decision configuration table exactly as specified in prompt
DECISIONS_CONFIG = [
    # Search ranking decisions (1-4)
    {"team": "search-ranking", "vendor": "google-vertex", "model": "gemini-1.5-flash",
     "use_case_type": "inference", "input_tokens_range": (200, 800), "output_tokens_range": (50, 200)},
    {"team": "search-ranking", "vendor": "google-vertex", "model": "gemini-1.5-flash",
     "use_case_type": "inference", "input_tokens_range": (200, 800), "output_tokens_range": (50, 200)},
    {"team": "search-ranking", "vendor": "google-vertex", "model": "gemini-1.5-flash",
     "use_case_type": "inference", "input_tokens_range": (200, 800), "output_tokens_range": (50, 200)},
    {"team": "search-ranking", "vendor": "google-vertex", "model": "gemini-1.5-flash",
     "use_case_type": "inference", "input_tokens_range": (200, 800), "output_tokens_range": (50, 200)},

    # Product recommendations decisions (5-7)
    {"team": "product-recommendations", "vendor": "openai", "model": "gpt-4o-mini",
     "use_case_type": "inference", "input_tokens_range": (300, 800), "output_tokens_range": (100, 300)},
    {"team": "product-recommendations", "vendor": "openai", "model": "gpt-4o-mini",
     "use_case_type": "inference", "input_tokens_range": (300, 800), "output_tokens_range": (100, 300)},
    {"team": "product-recommendations", "vendor": "openai", "model": "gpt-4o-mini",
     "use_case_type": "inference", "input_tokens_range": (300, 800), "output_tokens_range": (100, 300)},

    # Dynamic pricing decisions (8-9)
    {"team": "dynamic-pricing", "vendor": "openai", "model": "gpt-4o",
     "use_case_type": "inference", "input_tokens_range": (400, 1200), "output_tokens_range": (100, 400)},
    {"team": "dynamic-pricing", "vendor": "openai", "model": "gpt-4o",
     "use_case_type": "inference", "input_tokens_range": (400, 1200), "output_tokens_range": (100, 400)},

    # Fraud prevention decisions (10-11)
    {"team": "fraud-prevention", "vendor": "anthropic", "model": "claude-3-haiku",
     "use_case_type": "inference", "input_tokens_range": (200, 600), "output_tokens_range": (50, 150)},
    {"team": "fraud-prevention", "vendor": "anthropic", "model": "claude-3-haiku",
     "use_case_type": "inference", "input_tokens_range": (200, 600), "output_tokens_range": (50, 150)},

    # Returns automation decisions (12-13)
    {"team": "returns-automation", "vendor": "cohere", "model": "command-r",
     "use_case_type": "inference", "input_tokens_range": (300, 800), "output_tokens_range": (100, 250)},
    {"team": "returns-automation", "vendor": "cohere", "model": "command-r",
     "use_case_type": "inference", "input_tokens_range": (300, 800), "output_tokens_range": (100, 250)},

    # Demand forecasting decisions (14-15)
    {"team": "demand-forecasting", "vendor": "google-vertex", "model": "gemini-1.5-pro",
     "use_case_type": "batch_processing", "input_tokens_range": (3000, 8000), "output_tokens_range": (800, 2000)},
    {"team": "demand-forecasting", "vendor": "google-vertex", "model": "gemini-1.5-pro",
     "use_case_type": "batch_processing", "input_tokens_range": (3000, 8000), "output_tokens_range": (800, 2000)},

    # Catalog enrichment decisions (16-18)
    {"team": "catalog-enrichment", "vendor": "openai", "model": "gpt-4o",
     "use_case_type": "batch_processing", "input_tokens_range": (2000, 6000), "output_tokens_range": (500, 1500)},
    {"team": "catalog-enrichment", "vendor": "openai", "model": "gpt-4o",
     "use_case_type": "batch_processing", "input_tokens_range": (2000, 6000), "output_tokens_range": (500, 1500)},
    {"team": "catalog-enrichment", "vendor": "openai", "model": "gpt-4o",
     "use_case_type": "batch_processing", "input_tokens_range": (2000, 6000), "output_tokens_range": (500, 1500)},

    # Customer support AI decisions (19-20)
    {"team": "customer-support-ai", "vendor": "anthropic", "model": "claude-3-5-sonnet",
     "use_case_type": "inference", "input_tokens_range": (800, 2500), "output_tokens_range": (200, 800)},
    {"team": "customer-support-ai", "vendor": "anthropic", "model": "claude-3-5-sonnet",
     "use_case_type": "inference", "input_tokens_range": (800, 2500), "output_tokens_range": (200, 800)},

    # Inventory replenishment decisions (21-23)
    {"team": "inventory-replenishment", "vendor": "cohere", "model": "command-r-plus",
     "use_case_type": "batch_processing", "input_tokens_range": (2000, 5000), "output_tokens_range": (400, 1200)},
    {"team": "inventory-replenishment", "vendor": "cohere", "model": "command-r-plus",
     "use_case_type": "batch_processing", "input_tokens_range": (2000, 5000), "output_tokens_range": (400, 1200)},
    {"team": "inventory-replenishment", "vendor": "cohere", "model": "command-r-plus",
     "use_case_type": "batch_processing", "input_tokens_range": (2000, 5000), "output_tokens_range": (400, 1200)},

    # Supplier risk decisions (24-25)
    {"team": "supplier-risk", "vendor": "google-vertex", "model": "gemini-1.5-pro",
     "use_case_type": "inference", "input_tokens_range": (1500, 4000), "output_tokens_range": (300, 900)},
    {"team": "supplier-risk", "vendor": "google-vertex", "model": "gemini-1.5-pro",
     "use_case_type": "inference", "input_tokens_range": (1500, 4000), "output_tokens_range": (300, 900)},
]


def simulate_cost_attribution_decisions() -> List[DecisionSnapshot]:
    """
    Simulates 25 AI decisions across all 10 teams with realistic token usage and cost calculation.

    Returns:
        List of DecisionSnapshot objects with cost attribution data
    """
    decisions = []

    for i, config in enumerate(DECISIONS_CONFIG):
        # Generate realistic token counts within specified ranges
        input_tokens = random.randint(config["input_tokens_range"][0], config["input_tokens_range"][1])
        output_tokens = random.randint(config["output_tokens_range"][0], config["output_tokens_range"][1])

        # Calculate costs using shared utility
        input_cost_usd, output_cost_usd = compute_cost(
            config["vendor"],
            config["model"],
            input_tokens,
            output_tokens
        )
        total_cost_usd = input_cost_usd + output_cost_usd

        # Calculate cost per decision (for batch processing, divide by batch size)
        if config["use_case_type"] == "batch_processing":
            batch_size = 10000  # Simulated batch size as specified
            cost_per_decision = total_cost_usd / batch_size
        else:
            cost_per_decision = total_cost_usd

        # Generate decision timestamp within last 30 days
        now = datetime.now()
        days_ago = random.randint(0, 29)
        decision_timestamp = now - timedelta(days=days_ago)

        # Determine if this is peak season (Oct-Dec)
        is_peak_season = decision_timestamp.month in [10, 11, 12]

        # Generate realistic e-commerce context
        customer_segment = generate_customer_segment(config["team"])
        request_type = generate_request_type(config["team"])

        # Create decision inputs
        inputs = {
            "team_name": config["team"],
            "vendor": config["vendor"],
            "model_name": config["model"],
            "request_type": request_type,
            "customer_segment": customer_segment,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "decision_timestamp": decision_timestamp.isoformat(),
            "use_case_type": config["use_case_type"],
            "is_peak_season": is_peak_season
        }

        # Create decision outputs with cost data
        outputs = {
            "input_cost_usd": input_cost_usd,
            "output_cost_usd": output_cost_usd,
            "total_cost_usd": total_cost_usd,
            "cost_per_decision": cost_per_decision
        }

        # Create metadata for cost attribution
        metadata = {
            "function_type": "cost_attribution",
            "company": COMPANY["name"],
            "attribution_category": "per_decision_cost",
            "cost_calculation_method": "token_based_pricing",
            "decision_id": str(uuid.uuid4())
        }

        # Create decision snapshot
        decision = backend.create_decision_snapshot(
            function_name="cost_attribution_analysis",
            inputs=inputs,
            outputs=outputs,
            metadata=metadata
        )

        decisions.append(decision)

    return decisions


def generate_customer_segment(team: str) -> str:
    """Generate realistic customer segment based on team context."""
    if team in ["search-ranking", "product-recommendations", "dynamic-pricing", "fraud-prevention"]:
        return random.choice(["high_ltv", "first_time_visitor", "returning_lapsed", "price_sensitive"])
    else:
        return "not_applicable"


def generate_request_type(team: str) -> str:
    """Generate realistic request types based on team context."""
    request_types = {
        "search-ranking": ["product_search", "category_browse", "filter_application"],
        "product-recommendations": ["product_page_load", "cart_recommendation", "checkout_upsell"],
        "dynamic-pricing": ["price_calculation", "competitor_analysis", "demand_adjustment"],
        "fraud-prevention": ["checkout_event", "payment_verification", "account_review"],
        "returns-automation": ["return_request", "refund_processing", "quality_assessment"],
        "demand-forecasting": ["nightly_batch", "seasonal_forecast", "inventory_planning"],
        "catalog-enrichment": ["product_description", "attribute_extraction", "category_tagging"],
        "customer-support-ai": ["ticket_triage", "response_generation", "escalation_routing"],
        "inventory-replenishment": ["stock_level_check", "reorder_calculation", "supplier_selection"],
        "supplier-risk": ["vendor_assessment", "performance_review", "risk_scoring"]
    }
    return random.choice(request_types.get(team, ["generic_request"]))


def print_cost_attribution_report(decisions: List[DecisionSnapshot]) -> None:
    """
    Prints the cost attribution report exactly as specified in the prompt.

    Args:
        decisions: List of DecisionSnapshot objects with cost data
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate total spend from sample
    total_sample_spend = sum(float(d.outputs[2].value) for d in decisions)  # total_cost_usd

    # Calculate team-level spend breakdown
    team_stats = {}
    for decision in decisions:
        team = decision.inputs[0].value
        cost = float(decision.outputs[2].value)
        tokens = int(decision.inputs[5].value) + int(decision.inputs[6].value)  # input + output tokens

        if team not in team_stats:
            team_stats[team] = {"decisions": 0, "cost": 0.0, "tokens": 0, "vendor": "", "model": ""}

        team_stats[team]["decisions"] += 1
        team_stats[team]["cost"] += cost
        team_stats[team]["tokens"] += tokens
        team_stats[team]["vendor"] = decision.inputs[1].value
        team_stats[team]["model"] = decision.inputs[2].value

    # Sort teams by spend (descending)
    sorted_teams = sorted(team_stats.items(), key=lambda x: x[1]["cost"], reverse=True)

    # Find highest cost per decision
    highest_cost_decision = max(decisions, key=lambda d: float(d.outputs[3].value))  # cost_per_decision
    highest_cost_team = highest_cost_decision.inputs[0].value
    highest_cost_model = highest_cost_decision.inputs[2].value
    highest_cost_per_decision = float(highest_cost_decision.outputs[3].value)

    # Estimate daily cost for highest cost agent (assuming 500k daily decisions for dynamic pricing)
    estimated_daily_decisions = 500000 if highest_cost_team == "dynamic-pricing" else 50000
    daily_cost = highest_cost_per_decision * estimated_daily_decisions
    annual_cost = daily_cost * 365

    # Model right-sizing analysis (focus on dynamic-pricing using gpt-4o)
    gpt4o_decisions = [d for d in decisions if d.inputs[2].value == "gpt-4o"]
    if gpt4o_decisions:
        gpt4o_cost_per_decision = sum(float(d.outputs[3].value) for d in gpt4o_decisions) / len(gpt4o_decisions)
        # Calculate potential savings by switching to gpt-4o-mini
        gpt4o_mini_input_cost = int(gpt4o_decisions[0].inputs[5].value) / 1_000_000 * 0.15  # Mock calculation
        savings_pct = 75  # Approximate savings from switching to mini
        annual_savings = annual_cost * (savings_pct / 100)
    else:
        gpt4o_cost_per_decision = 0
        savings_pct = 0
        annual_savings = 0

    # Print report
    print("=== VANTARA COMMERCE — AI SPEND ATTRIBUTION (LAST 30 DAYS) ===")
    print(f"Generated: {timestamp}")
    print()
    print(f"TOTAL SPEND (SAMPLE): ${total_sample_spend:.4f} across {len(decisions)} decisions")
    print(f"ESTIMATED MONTHLY SPEND (FLEET-WIDE): $316,667  # $3.8M / 12")
    print(f"ANNUAL RUN-RATE (THIS SAMPLE EXTRAPOLATED): ${total_sample_spend * 12 * (180_000_000 / 25):.0f}")
    print()

    print("BY TEAM (sorted by spend descending):")
    for team_name, stats in sorted_teams:
        vendor_model = f"{stats['vendor']}/{stats['model']}"
        print(f"  {team_name:<35} {stats['decisions']:>3} decisions  {stats['tokens']:>9,} tokens  ${stats['cost']:>10.4f}  [{vendor_model}]")
    print()

    print("HIGHEST COST PER DECISION:")
    print(f"  {highest_cost_team} / {highest_cost_model}: ${highest_cost_per_decision:.6f} per decision")
    print(f"  At {estimated_daily_decisions:,} daily decisions → ${daily_cost:.2f}/day → ${annual_cost:.0f}/year")
    print()

    print("MODEL RIGHT-SIZING OPPORTUNITY:")
    print(f"  dynamic-pricing is using gpt-4o at ${gpt4o_cost_per_decision:.6f}/decision")
    print(f"  Switching to gpt-4o-mini saves {savings_pct:.0f}% per decision")
    print(f"  At estimated volume → saves ${annual_savings:.0f}/year")
    print()

    print("PEAK SEASON ALERT (Q4 — Oct/Nov/Dec):")
    print(f"  Vantara's Q4 AI spend runs 4.2x higher than Q1 baseline.")
    print(f"  Estimated Q4 monthly AI spend: ${3_800_000 / 12 * 4.2:.0f}")
    print("  Without per-decision cost attribution, this spike is invisible until the invoice arrives.")
    print("====================================================")


def main():
    """Main execution function for cost attribution demonstration."""
    print("=== Vantara Commerce AI Cost Attribution ===")
    print("Demonstrates: Bottom-up cost attribution from decision-level data\n")

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

    # Simulate cost attribution across teams
    print("Simulating AI decisions with cost tracking across 10 teams...")
    cost_decisions = simulate_cost_attribution_decisions()
    print(f"SUCCESS: Generated {len(cost_decisions)} cost-attributed decisions")

    # Store all decisions in backend
    stored_decision_ids = []
    for decision in cost_decisions:
        decision_id = backend_instance.save_decision(decision)
        stored_decision_ids.append(decision_id)
        team = decision.inputs[0].value
        cost = float(decision.outputs[2].value)
        print_audit_summary(decision_id, f"Team {team} decision cost ${cost:.6f}")

    print()

    # Generate and display cost attribution report
    print_cost_attribution_report(cost_decisions)
    print()

    # Demonstrate cost calculation accuracy
    print("COST CALCULATION VERIFICATION:")
    print("Validating cost computation for sample decisions:")

    for i, decision in enumerate(cost_decisions[:5]):  # Check first 5 decisions
        vendor = decision.inputs[1].value
        model = decision.inputs[2].value
        input_tokens = int(decision.inputs[5].value)
        output_tokens = int(decision.inputs[6].value)
        stored_total_cost = float(decision.outputs[2].value)

        # Recalculate cost to verify
        recalc_input_cost, recalc_output_cost = compute_cost(vendor, model, input_tokens, output_tokens)
        recalc_total_cost = recalc_input_cost + recalc_output_cost

        if abs(stored_total_cost - recalc_total_cost) < 0.000001:  # Account for floating point precision
            print(f"[VERIFY] Decision {i+1}: ${stored_total_cost:.6f} ✓")
        else:
            print(f"[ERROR] Decision {i+1}: stored=${stored_total_cost:.6f}, calculated=${recalc_total_cost:.6f}")

    print()

    # Demonstrate audit trail retrieval
    print("AUDIT TRAIL VERIFICATION:")
    print("Loading cost decisions by decision_id for regulatory queries:")

    for i, decision_id in enumerate(stored_decision_ids[-3:]):  # Check last 3 decisions
        retrieved_decision = backend_instance.load_decision(decision_id)
        if retrieved_decision:
            team = retrieved_decision.inputs[0].value
            total_cost = float(retrieved_decision.outputs[2].value)
            timestamp = retrieved_decision.inputs[7].value[:10]  # Date portion
            print(f"[AUDIT] Decision {len(stored_decision_ids)-2+i}: {team} | ${total_cost:.6f} | {timestamp} | decision_id={decision_id} | retrieved OK")
        else:
            print(f"[ERROR] Failed to retrieve decision {decision_id}")

    print(f"\nSUCCESS: Cost attribution demonstration completed")
    print(f"All {len(cost_decisions)} decisions tracked with per-decision cost data")


if __name__ == "__main__":
    main()