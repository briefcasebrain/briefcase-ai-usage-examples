"""
Pattern 07 — Cost attribution

What this shows: `CostCalculator` turns model + token usage into a deterministic
per-decision cost using real provider pricing. Aggregated across decisions, this
is the ground truth for team-level AI spend attribution.
When to reach for it: any time you need to charge-back AI spend to teams,
models, or decisions — or forecast monthly cost given current traffic.
See also: patterns/01_decision_capture.py (decisions are what you attribute cost to)
"""
from __future__ import annotations

from briefcase._native import CostCalculator

calc = CostCalculator()


def main() -> None:
    # === Section: Per-decision cost for one model ===
    # estimate_cost takes model + input/output tokens and returns the cost in
    # USD using real provider pricing compiled into the SDK.
    c = calc.estimate_cost("gpt-4o", input_tokens=1200, output_tokens=350)
    print(f"gpt-4o 1200 in / 350 out: ${c.total_cost:.6f}")
    print(f"  input portion:  ${c.input_cost:.6f}")
    print(f"  output portion: ${c.output_cost:.6f}")

    # === Section: Cross-model comparison ===
    # estimate_cost returns a CostEstimate with total_cost, input_cost, etc.
    # Running it for multiple models supports routing decisions such as
    # "cheapest model that meets the quality bar."
    for model in ["gpt-4o", "claude-3-5-sonnet", "gpt-4o-mini"]:
        try:
            est = calc.estimate_cost(model, 1200, 350)
            print(f"  {model:<25} ${est.total_cost:.6f}")
        except Exception as e:
            print(f"  {model:<25} (not registered: {type(e).__name__})")

    # === Section: Monthly projection ===
    # Scale a single-decision cost by expected traffic. Use this for budget
    # planning and proactive alerts before month-end overruns.
    per_day = 50_000
    per_call = calc.estimate_cost("gpt-4o-mini", 800, 200)
    monthly = per_call.total_cost * per_day * 30
    print(f"\nProjection for 50k gpt-4o-mini calls/day: ${monthly:,.2f}/month")


if __name__ == "__main__":
    main()
