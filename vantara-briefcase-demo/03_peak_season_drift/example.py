#!/usr/bin/env python3
"""
Vantara Commerce Peak Season Model Drift Detection Example

Problem: Every Q4, Vantara Commerce deploys updated AI models to handle Black Friday
and Cyber Monday traffic spikes. Model versions change rapidly across search,
recommendations, and fraud. When a model change causes degraded performance mid-season,
there is currently no way to pinpoint which version caused the regression or reconstruct
what the model was doing during the affected window.

Briefcase AI captures model version and full input/output context at every decision,
enabling instant root-cause analysis.

Demonstrates:
- Model version tracking across deployment waves
- Performance degradation detection between versions
- Root cause analysis with instant version identification
- Full input/output context preservation for debugging
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    import backend
    from backend import briefcase, DecisionSnapshot, SqliteBackend
    from backend import COMPANY, print_audit_summary
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)

# Set deterministic random seed for reproducible output
random.seed(42)

# Wave configuration exactly as specified in prompt
WAVE_1_CONFIG = {
    "period": "pre_bfcm",
    "start_date": datetime(2024, 11, 1),
    "end_date": datetime(2024, 11, 25),
    "search_ranking": {
        "model_version": "v8.2.1-stable",
        "confidence_mean": 0.88,
        "decisions": 6,
        "result_pattern": ["served"] * 6
    },
    "product_recommendations": {
        "model_version": "recs-v12.0",
        "ctr_prediction_mean": 0.073,
        "decisions": 6,
        "result_pattern": ["served"] * 6
    }
}

WAVE_2_CONFIG = {
    "period": "post_bfcm",
    "start_date": datetime(2024, 11, 29),
    "end_date": datetime(2024, 12, 5),
    "search_ranking": {
        "model_version": "v8.3.0-bfcm",
        "confidence_mean": 0.51,
        "decisions": 6,
        "result_pattern": ["served", "served", "served", "served", "fallback_to_rules", "fallback_to_rules"]
    },
    "product_recommendations": {
        "model_version": "recs-v12.1-bfcm",
        "ctr_prediction_mean": 0.031,
        "decisions": 6,
        "result_pattern": ["served"] * 6
    }
}


def simulate_peak_season_decisions() -> List[DecisionSnapshot]:
    """
    Simulates AI decisions across two waves: pre-BFCM and post-BFCM with model version changes.

    Returns:
        List of DecisionSnapshot objects representing seasonal model performance
    """
    all_decisions = []

    # Generate Wave 1 decisions (pre-BFCM)
    wave1_decisions = generate_wave_decisions(WAVE_1_CONFIG)
    all_decisions.extend(wave1_decisions)

    # Generate Wave 2 decisions (post-BFCM)
    wave2_decisions = generate_wave_decisions(WAVE_2_CONFIG)
    all_decisions.extend(wave2_decisions)

    return all_decisions


def generate_wave_decisions(wave_config: Dict[str, Any]) -> List[DecisionSnapshot]:
    """
    Generates decisions for a specific wave (pre or post BFCM).

    Args:
        wave_config: Configuration dictionary for the wave

    Returns:
        List of DecisionSnapshot objects for the wave
    """
    decisions = []

    # Generate search ranking decisions
    search_decisions = generate_team_decisions(
        team="search-ranking",
        agent_name="search-ranker-v8",
        vendor="google-vertex",
        model="gemini-1.5-flash",
        wave_config=wave_config,
        team_key="search_ranking"
    )
    decisions.extend(search_decisions)

    # Generate product recommendation decisions
    rec_decisions = generate_team_decisions(
        team="product-recommendations",
        agent_name="collab-filter-recs",
        vendor="openai",
        model="gpt-4o-mini",
        wave_config=wave_config,
        team_key="product_recommendations"
    )
    decisions.extend(rec_decisions)

    return decisions


def generate_team_decisions(
    team: str,
    agent_name: str,
    vendor: str,
    model: str,
    wave_config: Dict[str, Any],
    team_key: str
) -> List[DecisionSnapshot]:
    """
    Generates decisions for a specific team during a wave.

    Args:
        team: Team name (e.g., "search-ranking")
        agent_name: Agent name (e.g., "search-ranker-v8")
        vendor: AI vendor (e.g., "google-vertex")
        model: Model name (e.g., "gemini-1.5-flash")
        wave_config: Wave configuration dictionary
        team_key: Key to access team config in wave_config

    Returns:
        List of DecisionSnapshot objects for the team
    """
    decisions = []
    team_config = wave_config[team_key]
    period = wave_config["period"]

    for i in range(team_config["decisions"]):
        # Generate realistic timestamp within wave period
        start_timestamp = wave_config["start_date"]
        end_timestamp = wave_config["end_date"]
        time_range = (end_timestamp - start_timestamp).total_seconds()
        random_seconds = random.uniform(0, time_range)
        decision_timestamp = start_timestamp + timedelta(seconds=random_seconds)

        # Generate realistic token counts (short, as specified)
        input_tokens = random.randint(150, 600)
        output_tokens = random.randint(30, 150)

        # Generate realistic e-commerce query/context
        if team == "search-ranking":
            query_context = generate_search_query()
            confidence_score = add_noise(team_config["confidence_mean"], 0.05)
            ctr_prediction = None
        else:  # product-recommendations
            query_context = generate_recommendation_context()
            confidence_score = None
            ctr_prediction = add_noise(team_config["ctr_prediction_mean"], 0.005)

        # Get result pattern for this decision
        result = team_config["result_pattern"][i]

        # Create decision inputs
        inputs = {
            "team_name": team,
            "agent_name": agent_name,
            "vendor": vendor,
            "model_name": model,
            "model_version": team_config["model_version"],
            "query_or_context": query_context,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "decision_timestamp": decision_timestamp.isoformat(),
            "wave": period
        }

        # Create decision outputs based on team type
        outputs = {
            "result": result,
            "model_version": team_config["model_version"]  # Store in outputs for drift analysis
        }

        # Add team-specific outputs
        if team == "search-ranking":
            outputs["confidence_score"] = confidence_score
        else:  # product-recommendations
            outputs["click_through_rate_predicted"] = ctr_prediction

        # Create metadata for drift tracking
        metadata = {
            "function_type": "peak_season_drift_analysis",
            "company": COMPANY["name"],
            "wave_period": period,
            "deployment_date": "Nov 28" if period == "post_bfcm" else "Oct 15",
            "peak_season": True
        }

        # Create decision snapshot using instrumented pattern
        decision = backend.create_instrumented_decision(
            function_name="peak_season_model_execution",
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
            vendor=vendor,
            model=model
        )

        decisions.append(decision)

    return decisions


def generate_search_query() -> str:
    """Generate realistic e-commerce search queries."""
    queries = [
        "black sectional sofa under 500",
        "wireless bluetooth headphones noise cancelling",
        "women winter boots waterproof",
        "gaming laptop 16gb ram rtx",
        "kitchen stand mixer stainless steel",
        "outdoor patio furniture set",
        "smart home security camera system",
        "organic cotton bed sheets queen",
        "coffee maker programmable timer",
        "yoga mat non slip extra thick"
    ]
    return random.choice(queries)


def generate_recommendation_context() -> str:
    """Generate realistic recommendation contexts."""
    contexts = [
        "viewed: SKU-8821043, cart: empty, segment: returning_lapsed",
        "viewed: SKU-7745291, cart: SKU-2234567, segment: high_ltv",
        "viewed: SKU-9982847, cart: empty, segment: first_time_visitor",
        "viewed: SKU-5566778, cart: SKU-1122334, segment: price_sensitive",
        "viewed: SKU-4433221, cart: SKU-9988776, segment: returning_lapsed",
        "viewed: SKU-3344556, cart: empty, segment: high_ltv"
    ]
    return random.choice(contexts)


def add_noise(base_value: float, noise_level: float) -> float:
    """Add gaussian noise to a base value."""
    noise = random.gauss(0, noise_level)
    return max(0, base_value + noise)


def print_drift_analysis_report(decisions: List[DecisionSnapshot]) -> None:
    """
    Prints the drift analysis report exactly as specified in the prompt.

    Args:
        decisions: List of DecisionSnapshot objects from both waves
    """
    print("=== VANTARA COMMERCE — Q4 MODEL DRIFT REPORT ===")
    print("Analysis period: Nov 1 – Dec 5 (Black Friday / Cyber Monday window)")
    print()

    # Separate decisions by wave and team
    pre_bfcm_search = [d for d in decisions if d.inputs[9].value == "pre_bfcm" and d.inputs[0].value == "search-ranking"]
    post_bfcm_search = [d for d in decisions if d.inputs[9].value == "post_bfcm" and d.inputs[0].value == "search-ranking"]
    pre_bfcm_recs = [d for d in decisions if d.inputs[9].value == "pre_bfcm" and d.inputs[0].value == "product-recommendations"]
    post_bfcm_recs = [d for d in decisions if d.inputs[9].value == "post_bfcm" and d.inputs[0].value == "product-recommendations"]

    # Calculate search ranking metrics
    pre_search_confidence = calculate_mean_confidence(pre_bfcm_search)
    post_search_confidence = calculate_mean_confidence(post_bfcm_search)
    pre_search_fallback_rate = calculate_fallback_rate(pre_bfcm_search)
    post_search_fallback_rate = calculate_fallback_rate(post_bfcm_search)
    search_confidence_change = post_search_confidence - pre_search_confidence
    search_confidence_pct_change = (search_confidence_change / pre_search_confidence) * 100

    print("SEARCH RANKING — MODEL VERSION CHANGE DETECTED:")
    print(f"  Pre-BFCM  (v8.2.1-stable): mean confidence {pre_search_confidence:.3f}, fallback rate {pre_search_fallback_rate:.0f}%")
    print(f"  Post-BFCM (v8.3.0-bfcm):   mean confidence {post_search_confidence:.3f}, fallback rate {post_search_fallback_rate:.0f}%")
    print(f"  Δ confidence: {search_confidence_change:.3f} ({search_confidence_pct_change:.0f}% degradation)")
    print("  Root cause: model_version changed from v8.2.1-stable → v8.3.0-bfcm on Nov 28")
    print()

    # Calculate recommendation metrics
    pre_recs_ctr = calculate_mean_ctr(pre_bfcm_recs)
    post_recs_ctr = calculate_mean_ctr(post_bfcm_recs)
    recs_ctr_change = post_recs_ctr - pre_recs_ctr
    recs_ctr_pct_change = (recs_ctr_change / pre_recs_ctr) * 100

    print("PRODUCT RECOMMENDATIONS — MODEL VERSION CHANGE DETECTED:")
    print(f"  Pre-BFCM  (recs-v12.0):      mean predicted CTR {pre_recs_ctr:.4f}")
    print(f"  Post-BFCM (recs-v12.1-bfcm): mean predicted CTR {post_recs_ctr:.4f}")
    print(f"  Δ CTR prediction: {recs_ctr_change:.4f} ({recs_ctr_pct_change:.0f}% degradation)")
    print("  Root cause: model_version changed from recs-v12.0 → recs-v12.1-bfcm on Nov 28")
    print()

    print("WITHOUT BRIEFCASE AI:")
    print("  Time to identify root cause: 2–5 days (manual log correlation across 2 vendors)")
    print("  Evidence quality: reconstructed, not contemporaneous")
    print()
    print("WITH BRIEFCASE AI:")
    print("  Time to identify root cause: < 1 minute (query by model_version and decision_timestamp)")
    print("  Evidence quality: immutable decision traces captured at execution time")
    print("  Rollback target: v8.2.1-stable and recs-v12.0")
    print()

    print("DECISIONS RECONSTRUCTED ON DEMAND:")
    print("=" * 50)
    for i, decision in enumerate(decisions):
        team = decision.inputs[0].value
        model_version = decision.inputs[4].value
        wave = decision.inputs[9].value
        result = decision.outputs[0].value

        # Get performance metric
        if team == "search-ranking":
            if len(decision.outputs) > 2:  # Has confidence score
                perf_metric = f"confidence={float(decision.outputs[2].value):.3f}"
            else:
                perf_metric = "confidence=N/A"
        else:  # product-recommendations
            if len(decision.outputs) > 2:  # Has CTR prediction
                perf_metric = f"ctr_pred={float(decision.outputs[2].value):.4f}"
            else:
                perf_metric = "ctr_pred=N/A"

        print(f"  decision_{i+1:02d} | {model_version} | {wave} | {result} | {perf_metric}")

    print("=================================================")


def calculate_mean_confidence(decisions: List[DecisionSnapshot]) -> float:
    """Calculate mean confidence score from search ranking decisions."""
    if not decisions:
        return 0.0

    confidences = []
    for decision in decisions:
        if len(decision.outputs) > 2:  # Has confidence score output
            try:
                confidence = float(decision.outputs[2].value)
                confidences.append(confidence)
            except (ValueError, AttributeError):
                pass

    return sum(confidences) / len(confidences) if confidences else 0.0


def calculate_fallback_rate(decisions: List[DecisionSnapshot]) -> float:
    """Calculate fallback rate from search ranking decisions."""
    if not decisions:
        return 0.0

    fallback_count = sum(1 for d in decisions if d.outputs[0].value == "fallback_to_rules")
    return (fallback_count / len(decisions)) * 100


def calculate_mean_ctr(decisions: List[DecisionSnapshot]) -> float:
    """Calculate mean CTR prediction from recommendation decisions."""
    if not decisions:
        return 0.0

    ctrs = []
    for decision in decisions:
        if len(decision.outputs) > 2:  # Has CTR prediction output
            try:
                ctr = float(decision.outputs[2].value)
                ctrs.append(ctr)
            except (ValueError, AttributeError):
                pass

    return sum(ctrs) / len(ctrs) if ctrs else 0.0


def demonstrate_decision_reconstruction(decisions: List[DecisionSnapshot], backend_instance: SqliteBackend, stored_decision_ids: List[str]) -> None:
    """
    Demonstrates loading worst-performing decisions and showing full input context.

    Args:
        decisions: List of all decisions
        backend_instance: Backend instance for decision retrieval
        stored_decision_ids: List of stored decision IDs corresponding to decisions
    """
    print("DETAILED DECISION RECONSTRUCTION:")
    print("Loading 4 worst-performing decisions with full input context:")
    print("=" * 70)

    # Find worst-performing decisions with their stored IDs
    worst_decisions = []

    # Find lowest confidence search decisions
    search_decisions = [(d, stored_decision_ids[i]) for i, d in enumerate(decisions) if d.inputs[0].value == "search-ranking"]
    for decision, decision_id in search_decisions:
        if len(decision.outputs) > 2:
            try:
                confidence = float(decision.outputs[2].value)
                worst_decisions.append((decision, decision_id, confidence, "confidence"))
            except (ValueError, AttributeError):
                pass

    # Find lowest CTR prediction decisions
    rec_decisions = [(d, stored_decision_ids[i]) for i, d in enumerate(decisions) if d.inputs[0].value == "product-recommendations"]
    for decision, decision_id in rec_decisions:
        if len(decision.outputs) > 2:
            try:
                ctr = float(decision.outputs[2].value)
                worst_decisions.append((decision, decision_id, ctr, "ctr"))
            except (ValueError, AttributeError):
                pass

    # Sort by performance metric (lowest first) and take top 4
    worst_decisions.sort(key=lambda x: x[2])
    top_worst = worst_decisions[:4]

    for i, (decision, decision_id, metric_value, metric_type) in enumerate(top_worst, 1):
        retrieved_decision = backend_instance.load_decision(decision_id)
        if retrieved_decision:
            team = retrieved_decision.inputs[0].value
            model_version = retrieved_decision.inputs[4].value
            query_context = retrieved_decision.inputs[5].value
            wave = retrieved_decision.inputs[9].value
            result = retrieved_decision.outputs[0].value

            print(f"[{i}] WORST PERFORMING DECISION:")
            print(f"    Decision ID: {decision_id}")
            print(f"    Team: {team}")
            print(f"    Model Version: {model_version}")
            print(f"    Wave: {wave}")
            print(f"    Result: {result}")
            print(f"    {metric_type.title()} Score: {metric_value:.4f}")
            print(f"    Input Context: {query_context}")
            print(f"    Timestamp: {retrieved_decision.inputs[7].value[:19]}")
            print()


def main():
    """Main execution function for peak season drift detection demonstration."""
    print("=== Vantara Commerce Peak Season Model Drift Detection ===")
    print("Demonstrates: Instant root cause analysis for Q4 model version changes\n")

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

    # Simulate peak season model deployment and drift
    print("Simulating Q4 model deployments across Black Friday window...")
    print("Wave 1 (Nov 1-25): Pre-BFCM stable versions")
    print("Wave 2 (Nov 29-Dec 5): Post-BFCM updated versions with performance degradation")

    drift_decisions = simulate_peak_season_decisions()
    print(f"SUCCESS: Generated {len(drift_decisions)} decisions across 2 waves")

    # Store all decisions in backend
    stored_decision_ids = []
    for decision in drift_decisions:
        if hasattr(backend_instance, 'save_decision'):
            decision_id = backend_instance.save_decision(decision)
        else:
            decision_id = backend_instance.store_decision(decision)
        stored_decision_ids.append(decision_id)
        team = decision.inputs[0].value
        model_version = decision.inputs[4].value
        wave = decision.inputs[9].value
        print_audit_summary(decision_id, f"{team} {model_version} ({wave})")

    print()

    # Generate drift analysis report
    print_drift_analysis_report(drift_decisions)
    print()

    # Demonstrate detailed decision reconstruction
    demonstrate_decision_reconstruction(drift_decisions, backend_instance, stored_decision_ids)

    # Demonstrate audit trail retrieval by wave
    print("AUDIT TRAIL VERIFICATION BY WAVE:")
    print("Loading decisions by wave to verify model version tracking:")
    print("=" * 65)

    wave_counts = {"pre_bfcm": 0, "post_bfcm": 0}
    for decision_id in stored_decision_ids:
        retrieved_decision = backend_instance.load_decision(decision_id)
        if retrieved_decision:
            wave = retrieved_decision.inputs[9].value
            wave_counts[wave] += 1

    print(f"Pre-BFCM decisions retrieved: {wave_counts['pre_bfcm']}")
    print(f"Post-BFCM decisions retrieved: {wave_counts['post_bfcm']}")
    print(f"Total decisions in audit trail: {sum(wave_counts.values())}")

    if sum(wave_counts.values()) == len(stored_decision_ids):
        print("SUCCESS: All decisions retrievable with complete model version history")
    else:
        print("WARNING: Some decisions could not be retrieved from audit trail")

    print(f"\nSUCCESS: Peak season drift detection demonstration completed")
    print("Root cause analysis: model version changes on Nov 28 caused performance degradation")
    print("Time to resolution: < 1 minute vs 2-5 days manual correlation")


if __name__ == "__main__":
    main()