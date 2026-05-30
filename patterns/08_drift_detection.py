"""
Pattern 08 — Drift detection

What this shows: `DriftCalculator` measures how far recent model outputs have
moved from a baseline distribution. Rising drift typically signals a changed
input mix, a silent model regression, or a prompt change that didn't get
rolled back.
When to reach for it: any time you want an automated signal that "yesterday's
model is not behaving like today's," without manually inspecting samples.
See also: patterns/01_decision_capture.py (decisions are the inputs to drift)
"""
from __future__ import annotations

from briefcase.drift import DriftCalculator


def main() -> None:
    # === Section: Baseline vs. current distribution ===
    # Feed the calculator a batch of outputs (strings); it computes the internal
    # similarity structure and reports a drift score. Thresholds around 0.7-0.8
    # are reasonable defaults for "meaningfully different."
    baseline = [
        "approved: credit score 720, debt-to-income 0.28",
        "approved: credit score 705, debt-to-income 0.31",
        "approved: credit score 740, debt-to-income 0.22",
        "denied: credit score 610, debt-to-income 0.44",
    ]
    current = [
        "approved: credit score 680, debt-to-income 0.35",
        "approved: credit score 690, debt-to-income 0.33",
        "denied: credit score 600, debt-to-income 0.45",
        "denied: credit score 625, debt-to-income 0.42",
    ]

    calc = DriftCalculator()
    baseline_m = calc.calculate_drift(baseline)
    current_m = calc.calculate_drift(current)
    print(f"Baseline: drift={baseline_m.drift_score:.4f}  consistency={baseline_m.consistency_score:.4f}")
    print(f"Current:  drift={current_m.drift_score:.4f}  consistency={current_m.consistency_score:.4f}")

    # === Section: Combined pool ===
    # calculate_drift on baseline+current together surfaces whether the two
    # windows cluster apart — the classic "something changed" signal.
    combined = baseline + current
    combined_m = calc.calculate_drift(combined)
    print(f"Combined: drift={combined_m.drift_score:.4f}  samples={combined_m.total_samples}")
    print(
        "\nInterpretation: combined drift notably higher than either window\n"
        "alone indicates the two populations are pulling apart. In production\n"
        "this is the automated signal to page a model owner."
    )


if __name__ == "__main__":
    main()
