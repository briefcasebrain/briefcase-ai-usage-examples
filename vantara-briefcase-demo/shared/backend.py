"""
Shared backend setup for Vantara Commerce Briefcase AI demo.
Provides centralized backend configuration, cost calculation, and utility functions.

This module requires the Briefcase AI SDK to be installed. The SDK provides
enterprise-grade audit trails for AI decision-making systems in retail e-commerce.

For SDK access and licensing, contact: support@briefcasebrain.com
"""

import uuid
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

# Import the real SDK - examples require this to be installed
import briefcase_ai

# Make classes available for import - using real SDK
DecisionSnapshot = briefcase_ai.DecisionSnapshot
Input = briefcase_ai.Input
Output = briefcase_ai.Output
SqliteBackend = briefcase_ai.SqliteBackend

# Company data exactly as specified
COMPANY = {
    "name": "Vantara Commerce",
    "domain": "vantara.com",
    "industry": "retail e-commerce",
    "team_count": 45,
    "ai_vendors": ["openai", "anthropic", "google-vertex", "cohere"],
    "annual_ai_spend_estimate_usd": 3_800_000,
    "monthly_ai_decisions_estimate": 180_000_000,   # 180M decisions/month across all models
    "engineers_per_compliance_report": 4,
    "days_to_compile_report_manually": 21,
    "peak_season": "Q4 (Oct–Dec)",                  # Black Friday / Cyber Monday / holiday
    "peak_cost_multiplier": 4.2,                    # AI spend 4.2x higher in Q4 vs Q1
}

TEAMS = [
    "search-ranking",
    "product-recommendations",
    "dynamic-pricing",
    "fraud-prevention",
    "returns-automation",
    "demand-forecasting",
    "catalog-enrichment",
    "customer-support-ai",
    "inventory-replenishment",
    "supplier-risk",
]

# Customer segments for realistic e-commerce data
CUSTOMER_SEGMENTS = ["high_ltv", "first_time_visitor", "returning_lapsed", "price_sensitive", "not_applicable"]

# Pricing table - use these exact values as specified
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
    return briefcase_ai.SqliteBackend.in_memory()


def compute_cost(vendor: str, model_name: str, input_tokens: int, output_tokens: int) -> Tuple[float, float]:
    """
    Computes cost breakdown for a decision based on token usage and vendor pricing.

    Args:
        vendor: Vendor name (e.g., "openai", "anthropic")
        model_name: Model name (e.g., "gpt-4o", "claude-3-5-sonnet")
        input_tokens: Number of input tokens consumed
        output_tokens: Number of output tokens generated

    Returns:
        Tuple of (input_cost_usd, output_cost_usd)

    Raises:
        ValueError: If vendor or model not found in pricing table
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

    Args:
        decision_id: The decision ID that was stored
        label: Descriptive label for this audit entry
    """
    print(f"[AUDIT] {label} | decision_id={decision_id} | stored OK")


def format_demo_answer(capability: str, evidence: str) -> None:
    """
    Formats demo output showing capability and supporting evidence.

    Args:
        capability: What Briefcase AI capability was demonstrated
        evidence: The evidence that proves the capability works
    """
    print(f"CAPABILITY: {capability}")
    print(f"EVIDENCE:   {evidence}")


def create_decision_snapshot(
    function_name: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    metadata: Dict[str, Any],
    input_types: Optional[Dict[str, str]] = None,
    output_types: Optional[Dict[str, str]] = None
) -> DecisionSnapshot:
    """
    Helper function to create a properly formatted DecisionSnapshot.
    Standardizes the creation process across all examples using real SDK API.

    Args:
        function_name: Name of the AI function being tracked
        inputs: Dictionary of input name -> value
        outputs: Dictionary of output name -> value
        metadata: Additional metadata for the decision
        input_types: Optional type annotations for inputs
        output_types: Optional type annotations for outputs

    Returns:
        Configured DecisionSnapshot ready for storage
    """
    # Create decision snapshot with function name
    decision = briefcase_ai.DecisionSnapshot(function_name)

    # Add inputs using SDK API
    for name, value in inputs.items():
        type_str = input_types.get(name, "string") if input_types else "string"
        decision.add_input(briefcase_ai.Input(name, str(value), type_str))

    # Add outputs using SDK API
    for name, value in outputs.items():
        type_str = output_types.get(name, "string") if output_types else "string"
        output = briefcase_ai.Output(name, str(value), type_str)
        # Add confidence if available in metadata
        if f"{name}_confidence" in metadata:
            output = output.with_confidence(float(metadata[f"{name}_confidence"]))
        decision.add_output(output)

    # Add metadata as tags for regulatory tracking
    if metadata:
        for key, value in metadata.items():
            decision.add_tag(key, str(value))

    return decision


# Make classes and functions available for import
__all__ = [
    'briefcase_ai', 'DecisionSnapshot', 'Input', 'Output', 'SqliteBackend',
    'get_backend', 'compute_cost', 'print_audit_summary', 'format_demo_answer',
    'create_decision_snapshot', 'COMPANY', 'TEAMS', 'CUSTOMER_SEGMENTS', 'VENDOR_PRICING'
]