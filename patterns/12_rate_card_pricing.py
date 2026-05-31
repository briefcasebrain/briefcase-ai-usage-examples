"""
Pattern 12 — Rate cards (pricing tiers & platforms)

What this shows: `CostCalculator.estimate_cost(..., rate_card=...)` re-prices the
same decision under a `platform x tier x modifier` scheme. Batch and flex tiers are
half price; data-residency and regional modifiers add a premium; fast-mode is a
per-model premium. `get_available_rate_cards()` lists the representative cards.
When to reach for it: choosing a deployment (first-party vs Bedrock/Vertex/Azure),
trading latency for cost (batch vs standard vs priority), or pricing a compliance
constraint (US / regional data residency).
See also: patterns/07_cost_attribution.py (baseline per-decision cost),
          patterns/14_multicloud_cost.py (platform x tier matrix).
"""
from __future__ import annotations

from briefcase.cost import CostCalculator

calc = CostCalculator()
MODEL = "claude-opus-4-8"
IN, OUT = 1200, 350


def main() -> None:
    # === Section: Discover available rate cards ===
    # The cards are forgiving strings of the form "platform:tier,modifier".
    cards = calc.get_available_rate_cards()
    print(f"{len(cards)} representative rate cards:")
    print("  " + ", ".join(cards))

    # No rate_card (or "standard") == first-party standard pricing — the baseline.
    base = calc.estimate_cost(MODEL, IN, OUT)
    print(f"\n{MODEL}  {IN} in / {OUT} out — standard: ${base.total_cost:.6f}")

    # === Section: Tiers (the latency / throughput trade-off) ===
    # batch and flex are half price; priority is a premium *where a model offers it*.
    print("\nTiers (same model, same tokens):")
    for tier in ["standard", "batch", "flex", "priority"]:
        try:
            e = calc.estimate_cost(MODEL, IN, OUT, rate_card=tier)
            print(f"  {tier:<10} ${e.total_cost:.6f}  ({e.total_cost / base.total_cost:.2f}x)")
        except ValueError as err:
            # Tiers are per-model: not every model offers every tier.
            print(f"  {tier:<10} not available for this model ({err})")

    # === Section: Modifiers (residency, region, fast-mode) ===
    print("\nModifiers:")
    for card, label in [
        ("first_party:standard,us", "US data residency"),
        ("bedrock:standard,regional", "Bedrock regional"),
        ("first_party:fast", "fast-mode"),
    ]:
        e = calc.estimate_cost(MODEL, IN, OUT, rate_card=card)
        print(f"  {card:<28} {label:<18} ${e.total_cost:.6f}  ({e.total_cost / base.total_cost:.2f}x)")

    # === Section: Forgiving card strings ===
    # "bedrock regional" parses to the same card as "bedrock:standard,regional":
    # tier defaults to standard, separators may be spaces, ':' or ','.
    a = calc.estimate_cost(MODEL, IN, OUT, rate_card="bedrock regional")
    b = calc.estimate_cost(MODEL, IN, OUT, rate_card="bedrock:standard,regional")
    print(f"\n'bedrock regional' == 'bedrock:standard,regional': "
          f"{a.total_cost == b.total_cost}  (${a.total_cost:.6f})")


if __name__ == "__main__":
    main()
