"""
Pattern 13 — Prompt-cache cost accounting

What this shows: models with prompt caching bill reused context separately.
`estimate_cost(..., cache_read_tokens=..., cache_write_5m_tokens=..., cache_write_1h_tokens=...)`
prices cache reads at ~0.1x input and cache writes at a premium (1.25x for the 5-minute
TTL, 2x for the 1-hour TTL). `CostEstimate.cache_cost` itemizes the cache portion.
When to reach for it: long-context or system-prompt-heavy workloads (RAG, agents)
that resend the same context across many calls — model the warm-cache savings and
the write-once breakeven before committing to a caching strategy.
See also: patterns/07_cost_attribution.py (baseline cost),
          patterns/12_rate_card_pricing.py (tiers & platforms).
"""
from __future__ import annotations

from briefcase.cost import CostCalculator

calc = CostCalculator()
MODEL = "claude-opus-4-8"

CONTEXT = 90_000   # the large, reusable prefix (system prompt + retrieved docs)
PROMPT = 10_000    # the per-call, uncached portion (the user's question)
OUT = 1_000


def main() -> None:
    # === Section: Cold call — no cache ===
    # The whole context is billed as normal input on every call.
    cold = calc.estimate_cost(MODEL, CONTEXT + PROMPT, OUT)
    print(f"Cold  (all {CONTEXT + PROMPT:,} input tokens uncached): ${cold.total_cost:.4f}")

    # === Section: Warm call — context served from cache ===
    # Only the uncached prompt is billed as input; the reused prefix is a cache read
    # at ~0.1x. Split the tokens — do NOT also count the cached prefix as input, or
    # you double-bill it.
    warm = calc.estimate_cost(MODEL, PROMPT, OUT, cache_read_tokens=CONTEXT)
    print(f"Warm  ({PROMPT:,} input + {CONTEXT:,} cache_read):       ${warm.total_cost:.4f}  "
          f"(cache portion ${warm.cache_cost:.4f})")
    print(f"      -> {(1 - warm.total_cost / cold.total_cost) * 100:.0f}% cheaper than cold, per call")

    # === Section: The write — paid once to populate the cache ===
    # Writing the prefix costs a premium over input: 1.25x for the 5-minute TTL,
    # 2x for the 1-hour TTL. After that, every read is cheap.
    write5m = calc.estimate_cost(MODEL, PROMPT, OUT, cache_write_5m_tokens=CONTEXT)
    write1h = calc.estimate_cost(MODEL, PROMPT, OUT, cache_write_1h_tokens=CONTEXT)
    print(f"Write (5m TTL): total ${write5m.total_cost:.4f}  (cache write ${write5m.cache_cost:.4f})")
    print(f"Write (1h TTL): total ${write1h.total_cost:.4f}  (cache write ${write1h.cache_cost:.4f})")

    # === Section: Breakeven ===
    # One write + N warm reads vs N cold calls. How many reuses before caching pays off?
    write_premium = write5m.total_cost - warm.total_cost   # extra cost of the write call
    per_call_saving = cold.total_cost - warm.total_cost    # saving on each warm call
    breakeven = write_premium / per_call_saving if per_call_saving > 0 else float("inf")
    print(f"\nBreakeven: ~{breakeven:.1f} reuses to recoup the 5m cache write, "
          f"then save ${per_call_saving:.4f}/call.")


if __name__ == "__main__":
    main()
