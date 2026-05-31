"""
Pattern 14 — Multi-cloud & tier pricing

What this shows: the same model priced across platforms (first-party, Bedrock,
Vertex, Azure) and tiers via `rate_card`. The SDK's base rate is unified across
platforms, so platform choice at the standard tier is cost-neutral — the real cost
levers are the *tier* (batch is ~0.5x) and *modifiers* (regional / data-residency
add ~10%). Pick a platform for compliance and availability, then optimize with tier.
When to reach for it: comparing deployment options, or quantifying the cost of a
regional/residency constraint against the savings of batch processing.
See also: patterns/12_rate_card_pricing.py (the full card grammar),
          patterns/07_cost_attribution.py (baseline per-decision cost).
"""
from __future__ import annotations

from briefcase.cost import CostCalculator

calc = CostCalculator()
MODEL = "claude-opus-4-8"
IN, OUT = 1200, 350
PLATFORMS = ["first_party", "bedrock", "vertex", "azure"]


def main() -> None:
    base = calc.estimate_cost(MODEL, IN, OUT).total_cost

    # === Section: Platform x tier matrix ===
    # Same model, same tokens; only the rate card changes.
    print(f"{MODEL}  {IN} in / {OUT} out — cost per decision")
    print(f"  {'platform':<12} {'standard':>12} {'batch':>12} {'regional':>12}")
    for plat in PLATFORMS:
        cells = []
        for tier in ["standard", "batch", "standard,regional"]:
            try:
                e = calc.estimate_cost(MODEL, IN, OUT, rate_card=f"{plat}:{tier}")
                cells.append(f"${e.total_cost:.6f}")
            except ValueError:
                cells.append("—")
        print(f"  {plat:<12} {cells[0]:>12} {cells[1]:>12} {cells[2]:>12}")

    # === Section: Read the levers ===
    bedrock_batch = calc.estimate_cost(MODEL, IN, OUT, rate_card="bedrock:batch").total_cost
    regional = calc.estimate_cost(MODEL, IN, OUT, rate_card="vertex:standard,regional").total_cost
    print("\nWhat moves the price:")
    print(f"  standard base (any platform): ${base:.6f}  — platform choice is cost-neutral here")
    print(f"  batch tier:                   ${bedrock_batch:.6f}  ({bedrock_batch / base:.2f}x — offline/throughput work)")
    print(f"  + regional modifier:          ${regional:.6f}  ({regional / base:.2f}x — data stays in-region)")

    print("\nTakeaway: choose the platform for compliance/availability; cut cost with the"
          " batch tier; pay ~10% more only when residency requires it.")


if __name__ == "__main__":
    main()
