"""
Shared backend setup for Briefcase AI regulatory workflow examples.
Provides centralized backend configuration and utility functions.

This module requires the Briefcase AI SDK to be installed. The SDK provides
regulatory-grade audit trails for AI decision-making systems in financial services.

For SDK access and licensing, contact: support@briefcasebrain.com
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import the real SDK - examples require this to be installed
import briefcase_ai

# Make classes available for import - using real SDK
DecisionSnapshot = briefcase_ai.DecisionSnapshot
Input = briefcase_ai.Input
Output = briefcase_ai.Output
SqliteBackend = briefcase_ai.SqliteBackend

__all__ = ['briefcase_ai', 'DecisionSnapshot', 'Input', 'Output', 'SqliteBackend',
           'get_backend', 'print_audit_summary', 'format_examiner_response',
           'create_decision_snapshot', 'simulate_model_drift_detection',
           'validate_regulatory_completeness']


def get_backend():
    """
    Returns a configured in-memory SQLite backend for examples.
    All examples use this to avoid external infrastructure dependencies.
    """
    return briefcase_ai.SqliteBackend.in_memory()


def print_audit_summary(decision: DecisionSnapshot) -> None:
    """
    Prints a standardized audit log summary for any loaded decision.
    Used across all examples for consistent output formatting.

    Args:
        decision: The DecisionSnapshot to summarize
    """
    print(f"\n=== AUDIT SUMMARY ===")
    print(f"Decision ID: {getattr(decision, 'id', 'N/A')}")
    print(f"Function: {getattr(decision, 'function_name', 'N/A')}")
    print(f"Timestamp: {getattr(decision, 'created_at', 'N/A')}")

    print(f"\nInputs:")
    if hasattr(decision, 'inputs'):
        for inp in decision.inputs:
            print(f"  - {inp.name}: {inp.value} ({getattr(inp, 'data_type', 'string')})")

    print(f"\nOutputs:")
    if hasattr(decision, 'outputs'):
        for out in decision.outputs:
            print(f"  - {out.name}: {out.value} ({getattr(out, 'data_type', 'string')})")

    print(f"\nTags (Regulatory Metadata):")
    if hasattr(decision, 'tags'):
        for key, value in decision.tags.items():
            print(f"  - {key}: {value}")

    print(f"===================\n")


def format_examiner_response(decision_id: str, query: str, backend) -> str:
    """
    Formats a simulated regulatory examiner response by loading a decision
    and presenting it as audit evidence.

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
        response += f"Execution Time: {getattr(decision, 'created_at', 'N/A')}\n\n"

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


def simulate_model_drift_detection(
    decisions: list,
    group_by_field: str,
    metric_field: str
) -> Dict[str, Any]:
    """
    Simulates automated drift detection across decision cohorts.
    Used in release monitoring examples.

    Args:
        decisions: List of DecisionSnapshot objects
        group_by_field: Model parameter field to group by (e.g., "model_version")
        metric_field: Output field to analyze for drift

    Returns:
        Drift analysis report
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

    Args:
        decision: DecisionSnapshot to validate
        required_fields: List of required field names in tags

    Returns:
        Validation report
    """
    missing_fields = []
    present_fields = []

    tags = getattr(decision, 'tags', {}) or {}

    for field in required_fields:
        if field in tags:
            present_fields.append(field)
        else:
            missing_fields.append(field)

    return {
        "decision_id": getattr(decision, 'id', 'N/A'),
        "is_compliant": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "present_fields": present_fields,
        "completeness_score": len(present_fields) / len(required_fields) if required_fields else 1.0
    }