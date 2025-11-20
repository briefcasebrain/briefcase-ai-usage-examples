#!/usr/bin/env python3
"""
Drift Analysis Example

This example demonstrates AI model output drift detection including:
- Basic drift calculation
- Enhanced drift metrics
- Temperature sensitivity analysis
- Consensus detection
- Trend analysis
"""

import time
import random
from briefcase_ai_telemetry import (
    calculate_drift, DriftCalculator, DriftMetrics,
    calculate_enhanced_drift_metrics
)


def basic_drift_examples():
    """Basic drift detection examples."""
    print("=== Basic Drift Detection ===")

    # Example 1: Identical outputs (no drift)
    identical_outputs = [
        "The capital of France is Paris.",
        "The capital of France is Paris.",
        "The capital of France is Paris."
    ]

    metrics = calculate_drift(identical_outputs)
    print(f"\n1. Identical outputs:")
    print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
    print(f"   Consensus confidence: {metrics.consensus_confidence}")
    print(f"   Consensus output: {metrics.consensus_output}")

    # Example 2: Similar but different outputs
    similar_outputs = [
        "The capital of France is Paris.",
        "France's capital city is Paris.",
        "Paris is the capital of France."
    ]

    metrics = calculate_drift(similar_outputs)
    print(f"\n2. Similar outputs:")
    print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
    print(f"   Edit distance: {metrics.normalized_edit_distance:.3f}")
    print(f"   Consensus confidence: {metrics.consensus_confidence}")

    # Example 3: Completely different outputs
    different_outputs = [
        "The capital of France is Paris.",
        "I like pizza and pasta.",
        "What is machine learning about?"
    ]

    metrics = calculate_drift(different_outputs)
    print(f"\n3. Different outputs:")
    print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
    print(f"   Edit distance: {metrics.normalized_edit_distance:.3f}")
    print(f"   Consensus confidence: {metrics.consensus_confidence}")
    print(f"   Consensus output: {metrics.consensus_output}")


def enhanced_drift_analysis():
    """Advanced drift analysis with context."""
    print("\n=== Enhanced Drift Analysis ===")

    # Example with context for semantic analysis
    outputs_with_context = [
        "Machine learning is a subset of artificial intelligence.",
        "ML is part of the broader field of AI.",
        "Artificial intelligence includes machine learning as a component."
    ]

    enhanced_metrics = calculate_enhanced_drift_metrics(
        outputs_with_context,
        context="Definition of machine learning and AI relationship"
    )

    print(f"\n1. Enhanced analysis with context:")
    print(f"   Ensemble drift score: {enhanced_metrics.ensemble_score:.3f}")
    print(f"   Semantic similarity: {enhanced_metrics.semantic_similarity:.3f}")
    print(f"   Statistical drift: {enhanced_metrics.statistical_drift}")
    print(f"   Structural drift: {enhanced_metrics.structural_drift}")
    print(f"   Drift severity: {enhanced_metrics.drift_severity}")


def temperature_sensitivity_demo():
    """Demonstrate temperature sensitivity analysis."""
    print("\n=== Temperature Sensitivity ===")

    calculator = DriftCalculator()

    # Simulate outputs at different temperatures
    outputs_t0 = [
        "2 + 2 = 4",
        "2 + 2 = 4",
        "2 + 2 = 4"
    ]

    outputs_t02 = [
        "2 + 2 = 4",
        "2 + 2 equals 4",
        "The sum of 2 and 2 is 4"
    ]

    sensitivity = calculator.calculate_temperature_sensitivity(outputs_t0, outputs_t02)

    print(f"\n1. Temperature sensitivity analysis:")
    print(f"   T=0.0 outputs: {outputs_t0}")
    print(f"   T=0.2 outputs: {outputs_t02}")
    print(f"   Sensitivity per 0.1 temp unit: {sensitivity:.2f}%")


def drift_over_time_simulation():
    """Simulate drift detection over time."""
    print("\n=== Drift Monitoring Over Time ===")

    calculator = DriftCalculator()

    # Simulate model outputs degrading over time
    base_response = "The solution is X = 5"

    time_periods = [
        ("Day 1", [base_response, base_response, base_response]),
        ("Day 7", [base_response, "X = 5 is the solution", base_response]),
        ("Day 14", ["X = 5", "The answer is X = 5", "Solution: X = 5"]),
        ("Day 21", ["X = 5", "X equals 5", "Five is the value of X"]),
        ("Day 30", ["X = 5", "The value is 5", "I think X might be 5"])
    ]

    drift_history = []

    for day, outputs in time_periods:
        metrics = calculator.calculate_metrics(outputs)
        drift_history.append({
            'day': day,
            'agreement_rate': metrics.total_agreement_rate,
            'consistency_score': metrics.consistency_score,
            'confidence': metrics.consensus_confidence
        })

        print(f"\n{day}:")
        print(f"   Outputs: {outputs}")
        print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
        print(f"   Consistency score: {metrics.consistency_score:.1f}")
        print(f"   Confidence: {metrics.consensus_confidence}")

    # Analyze trend
    print(f"\n=== Drift Trend Analysis ===")
    print("Day | Agreement | Consistency | Confidence")
    print("-" * 45)
    for entry in drift_history:
        print(f"{entry['day']:<8} | {entry['agreement_rate']:>8.1f}% | {entry['consistency_score']:>10.1f} | {entry['confidence']}")


def edge_case_testing():
    """Test edge cases in drift detection."""
    print("\n=== Edge Case Testing ===")

    # Empty list
    try:
        metrics = calculate_drift([])
        print(f"\n1. Empty outputs:")
        print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
        print(f"   Confidence: {metrics.consensus_confidence}")
    except Exception as e:
        print(f"   Error with empty list: {e}")

    # Single output
    single_output = ["Only one response"]
    metrics = calculate_drift(single_output)
    print(f"\n2. Single output:")
    print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
    print(f"   Confidence: {metrics.consensus_confidence}")
    print(f"   Consensus: {metrics.consensus_output}")

    # Very long outputs
    long_outputs = [
        "This is a very long response that contains multiple sentences and detailed explanations about a complex topic that requires extensive analysis.",
        "This represents a lengthy response with multiple sentences discussing complex topics that need thorough analysis and explanation.",
        "Here we have an extended response containing several sentences about complicated subjects requiring detailed examination."
    ]

    metrics = calculate_drift(long_outputs)
    print(f"\n3. Long outputs:")
    print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
    print(f"   Edit distance: {metrics.normalized_edit_distance:.3f}")
    print(f"   Confidence: {metrics.consensus_confidence}")

    # Mixed length outputs
    mixed_outputs = ["Short", "Medium length response", "This is a very long response with lots of details"]
    metrics = calculate_drift(mixed_outputs)
    print(f"\n4. Mixed length outputs:")
    print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
    print(f"   Edit distance: {metrics.normalized_edit_distance:.3f}")
    print(f"   Confidence: {metrics.consensus_confidence}")


def real_world_scenario():
    """Simulate a real-world AI model drift scenario."""
    print("\n=== Real-World Scenario: Code Generation Model ===")

    # Simulate a code generation model's outputs over time
    scenarios = [
        {
            "name": "Fresh Model",
            "outputs": [
                "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            ]
        },
        {
            "name": "After 1 Week",
            "outputs": [
                "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            ]
        },
        {
            "name": "After 1 Month",
            "outputs": [
                "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)",
                "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
            ]
        }
    ]

    for scenario in scenarios:
        metrics = calculate_drift(scenario["outputs"])
        print(f"\n{scenario['name']}:")
        print(f"   Agreement rate: {metrics.total_agreement_rate:.1f}%")
        print(f"   Edit distance: {metrics.normalized_edit_distance:.3f}")
        print(f"   Consistency: {metrics.consistency_score:.1f}")
        print(f"   Confidence: {metrics.consensus_confidence}")

        # Show if drift is concerning
        if metrics.total_agreement_rate < 80:
            print(f"   ⚠️  DRIFT DETECTED - Agreement below 80%")
        elif metrics.total_agreement_rate < 90:
            print(f"   ⚡ Minor drift detected")
        else:
            print(f"   ✅ Model stable")


if __name__ == "__main__":
    try:
        basic_drift_examples()
        enhanced_drift_analysis()
        temperature_sensitivity_demo()
        drift_over_time_simulation()
        edge_case_testing()
        real_world_scenario()

        print("\n🎉 All drift analysis examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()