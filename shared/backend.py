"""
Unified backend setup for Briefcase AI demo suites.
Provides centralized backend configuration and utility functions for both
Vantara Commerce (e-commerce) and regulatory workflow demonstrations.

This module requires the real Briefcase AI SDK to be installed.

For SDK access and licensing, contact: support@briefcaseai.org
"""

import sys
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

# Import the real SDK - examples require this to be installed
try:
    import briefcase
    from briefcase import DecisionSnapshot, Input, Output, ModelParameters, init, init_with_config, is_initialized
    from briefcase.storage import SqliteBackend

    try:
        from briefcase.cost import CostCalculator
    except ImportError:
        CostCalculator = None

    try:
        from briefcase.drift import DriftCalculator
    except ImportError:
        DriftCalculator = None

    print("SUCCESS: Using real Briefcase AI SDK")

except ImportError as e:
    print(f"ERROR: Briefcase AI SDK is required for demos")
    print(f"Import error: {e}")
    print("")
    print("Please install the SDK:")
    print("  pip install briefcase-ai")
    print("")
    print("For enterprise licensing and support:")
    print("  Contact: support@briefcaseai.org")
    sys.exit(1)

# Vantara Commerce company data
COMPANY = {
    "name": "Vantara Commerce",
    "domain": "vantara.com",
    "industry": "retail e-commerce",
    "team_count": 45,
    "ai_vendors": ["openai", "anthropic", "google-vertex", "cohere"],
    "annual_ai_spend_estimate_usd": 3_800_000,
    "monthly_ai_decisions_estimate": 180_000_000,
    "engineers_per_compliance_report": 4,
    "days_to_compile_report_manually": 21,
    "peak_season": "Q4 (Oct–Dec)",
    "peak_cost_multiplier": 4.2,
}

TEAMS = [
    "search-ranking", "product-recommendations", "dynamic-pricing",
    "fraud-prevention", "returns-automation", "demand-forecasting",
    "catalog-enrichment", "customer-support-ai", "inventory-replenishment",
    "supplier-risk",
]

CUSTOMER_SEGMENTS = ["high_ltv", "first_time_visitor", "returning_lapsed", "price_sensitive", "not_applicable"]

# Pricing table for cost attribution
VENDOR_PRICING = {
    # (input_price_per_1M_tokens, output_price_per_1M_tokens)
    "openai":        {"gpt-4o": (2.50, 10.00), "gpt-4o-mini": (0.15, 0.60)},
    "anthropic":     {"claude-3-5-sonnet": (3.00, 15.00), "claude-3-haiku": (0.25, 1.25)},
    "cohere":        {"command-r-plus": (0.50, 1.50), "command-r": (0.15, 0.60)},
    "google-vertex": {"gemini-1.5-pro": (1.25, 5.00), "gemini-1.5-flash": (0.075, 0.30)},
}


def get_backend():
    """
    Returns a configured in-memory SQLite backend for examples.
    All examples use this to avoid external infrastructure dependencies.
    """
    # Initialize the real SDK if not already done
    try:
        if not is_initialized():
            init()
            print("INFO: Initialized real Briefcase AI SDK")
    except Exception as e:
        print(f"INFO: Could not initialize SDK: {e}")

    return SqliteBackend.in_memory()


def compute_cost(vendor: str, model_name: str, input_tokens: int, output_tokens: int) -> Tuple[float, float]:
    """
    Computes cost breakdown for a decision based on token usage and vendor pricing.
    Used by Vantara Commerce demos for cost attribution.

    Args:
        vendor: Vendor name (e.g., "openai", "anthropic")
        model_name: Model name (e.g., "gpt-4o", "claude-3-5-sonnet")
        input_tokens: Number of input tokens consumed
        output_tokens: Number of output tokens generated

    Returns:
        Tuple of (input_cost_usd, output_cost_usd)
    """
    if vendor not in VENDOR_PRICING:
        raise ValueError(f"Vendor '{vendor}' not found in pricing table")

    vendor_models = VENDOR_PRICING[vendor]
    if model_name not in vendor_models:
        raise ValueError(f"Model '{model_name}' not found for vendor '{vendor}'")

    input_price_per_1M, output_price_per_1M = vendor_models[model_name]

    # Calculate costs (prices are per 1M tokens)
    input_cost_usd = (input_tokens / 1_000_000) * input_price_per_1M
    output_cost_usd = (output_tokens / 1_000_000) * output_price_per_1M

    return input_cost_usd, output_cost_usd


def print_audit_summary(decision_id: str, label: str) -> None:
    """
    Prints a standardized audit log summary for any decision ID.
    Used across all examples for consistent output formatting.
    """
    print(f"[AUDIT] {label} | decision_id={decision_id} | stored OK")


def format_demo_answer(capability: str, evidence: str) -> None:
    """
    Formats demo output showing capability and supporting evidence.
    Used by Vantara Commerce demos.
    """
    print(f"CAPABILITY: {capability}")
    print(f"EVIDENCE:   {evidence}")


def format_examiner_response(decision_id: str, query: str, backend) -> str:
    """
    Formats a simulated regulatory examiner response by loading a decision
    and presenting it as audit evidence. Used by regulatory workflow demos.

    Args:
        decision_id: The decision ID to retrieve
        query: The examiner's query for context
        backend: Backend to load from

    Returns:
        Formatted examiner response string
    """
    try:
        decision = backend.load_decision(decision_id)
        if not decision:
            return f"ERROR: Decision {decision_id} not found in audit trail."

        response = f"\n=== REGULATORY EXAMINER RESPONSE ===\n"
        response += f"Query: {query}\n"
        response += f"Decision ID: {decision_id}\n\n"

        response += f"AUDIT EVIDENCE:\n"
        response += f"Function: {getattr(decision, 'function_name', 'N/A')}\n"

        # Handle timestamps
        timestamp = getattr(decision, 'created_at', None) or getattr(decision, 'timestamp', 'N/A')
        response += f"Execution Time: {timestamp}\n\n"

        response += f"MODEL INPUTS (at decision time):\n"
        if hasattr(decision, 'inputs'):
            for inp in decision.inputs:
                response += f"  • {inp.name}: {inp.value}\n"

        response += f"\nMODEL OUTPUTS:\n"
        if hasattr(decision, 'outputs'):
            for out in decision.outputs:
                response += f"  • {out.name}: {out.value}\n"

        response += f"\nREGULATORY METADATA:\n"
        if hasattr(decision, 'tags'):
            for key, value in decision.tags.items():
                if 'regulation' in key.lower() or 'rule' in key.lower() or 'version' in key.lower():
                    response += f"  • {key}: {value}\n"

        response += f"\n=== END EXAMINER RESPONSE ===\n"
        return response

    except Exception as e:
        return f"ERROR retrieving decision {decision_id}: {str(e)}"


def create_instrumented_decision(
    function_name: str,
    inputs: Dict[str, Any] = None,
    outputs: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    vendor: str = None,
    model: str = None
) -> DecisionSnapshot:
    """
    Creates a DecisionSnapshot using real SDK instrumentation patterns.
    Preferred method for creating decisions in both demo suites.

    Args:
        function_name: Name of the AI function being tracked
        inputs: Dictionary of input name -> value
        outputs: Dictionary of output name -> value
        metadata: Additional metadata for the decision
        vendor: AI vendor (e.g., "openai", "anthropic")
        model: AI model (e.g., "gpt-4o", "claude-3-5-sonnet")

    Returns:
        Configured DecisionSnapshot ready for storage
    """
    # Create decision snapshot
    decision = DecisionSnapshot(function_name)

    # Add inputs
    if inputs:
        for name, value in inputs.items():
            decision.add_input(Input(name, str(value), "string"))

    # Add model metadata
    if vendor or model:
        params = ModelParameters(model or "unknown")
        if vendor:
            params.with_provider(vendor)
        decision.with_model_parameters(params)

    # Add metadata
    if metadata:
        for key, value in metadata.items():
            decision.add_input(Input(key, str(value), "metadata"))

    # Add outputs
    if outputs:
        for name, value in outputs.items():
            decision.add_output(Output(name, str(value), "string"))

    return decision


def create_decision_snapshot(
    function_name: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    metadata: Dict[str, Any],
    input_types: Optional[Dict[str, str]] = None,
    output_types: Optional[Dict[str, str]] = None
) -> DecisionSnapshot:
    """
    Legacy function for creating DecisionSnapshot with type annotations.
    DEPRECATED: Use create_instrumented_decision() for better SDK integration.
    """
    # Create decision snapshot with function name
    decision = DecisionSnapshot(function_name)

    # Add inputs using SDK API
    for name, value in inputs.items():
        type_str = input_types.get(name, "string") if input_types else "string"
        decision.add_input(Input(name, str(value), type_str))

    # Add outputs using SDK API
    for name, value in outputs.items():
        type_str = output_types.get(name, "string") if output_types else "string"
        output = Output(name, str(value), type_str)
        # Add confidence if available in metadata
        if f"{name}_confidence" in metadata:
            try:
                output = output.with_confidence(float(metadata[f"{name}_confidence"]))
            except Exception:
                pass
        decision.add_output(output)

    # Add metadata as tags for regulatory tracking
    if metadata:
        for key, value in metadata.items():
            try:
                decision.add_tag(key, str(value))
            except Exception:
                decision.add_input(Input(key, str(value), "metadata"))

    return decision


def simulate_model_drift_detection(
    decisions: list,
    group_by_field: str,
    metric_field: str
) -> Dict[str, Any]:
    """
    Simulates automated drift detection across decision cohorts.
    Used in regulatory workflow drift monitoring examples.
    """
    cohorts = {}

    # Group decisions by the specified field
    for decision in decisions:
        group_value = "unknown"
        if hasattr(decision, 'tags'):
            group_value = decision.tags.get(group_by_field, "unknown")

        if group_value not in cohorts:
            cohorts[group_value] = []
        cohorts[group_value].append(decision)

    # Calculate metrics per cohort
    cohort_stats = {}
    for group, group_decisions in cohorts.items():
        values = []
        for decision in group_decisions:
            if hasattr(decision, 'outputs'):
                for output in decision.outputs:
                    if output.name == metric_field:
                        try:
                            values.append(float(output.value))
                        except (ValueError, TypeError):
                            pass

        if values:
            cohort_stats[group] = {
                "count": len(values),
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }

    return {
        "cohorts": cohort_stats,
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "drift_detected": len(cohort_stats) > 1 and
                         max(s["mean"] for s in cohort_stats.values()) -
                         min(s["mean"] for s in cohort_stats.values()) > 0.1
    }


def validate_regulatory_completeness(decision: DecisionSnapshot, required_fields: list) -> Dict[str, Any]:
    """
    Validates that a decision snapshot contains all required regulatory fields in tags.
    Used by regulatory workflow compliance validation.
    """
    missing_fields = []
    present_fields = []

    tags = getattr(decision, 'tags', {}) or {}

    for field in required_fields:
        if field in tags:
            present_fields.append(field)
        else:
            missing_fields.append(field)

    # Handle decision ID
    decision_id = getattr(decision, 'id', None) or getattr(decision, 'decision_id', 'N/A')

    return {
        "decision_id": decision_id,
        "is_compliant": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "present_fields": present_fields,
        "completeness_score": len(present_fields) / len(required_fields) if required_fields else 1.0
    }


# Make classes and functions available for import
__all__ = [
    'briefcase', 'DecisionSnapshot', 'Input', 'Output', 'ModelParameters', 'SqliteBackend', 'CostCalculator', 'DriftCalculator',
    'get_backend', 'compute_cost', 'print_audit_summary', 'format_demo_answer', 'format_examiner_response',
    'create_decision_snapshot', 'create_instrumented_decision', 'simulate_model_drift_detection',
    'validate_regulatory_completeness',
    'COMPANY', 'TEAMS', 'CUSTOMER_SEGMENTS', 'VENDOR_PRICING'
]
