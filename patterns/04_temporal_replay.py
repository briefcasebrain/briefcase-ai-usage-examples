"""
Pattern 04 — Temporal replay with AsOfView

What this shows: `AsOfView` wraps any bitemporal store and clamps reads to a
historical `transaction_time`. Production code and backtest/replay code share
the same function body — only the wrapper changes. Writes are refused on a
view of the past.
When to reach for it: any time you need to answer "what did the system know on
day D" — regulatory replay, backtesting without look-ahead bias, explaining a
past decision whose inputs have since been corrected.
See also: patterns/03_correction_append.py, patterns/06_examiner_bundle.py
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from briefcase.bitemporal import (
    AsOfView,
    BitemporalRecord,
    InMemoryBitemporalStore,
    append_correction,
)

UTC = timezone.utc


def main() -> None:
    # === Section: Set up a store with a correction ===
    # Original on day 16; correction on day 46. See pattern 03.
    store = InMemoryBitemporalStore()
    day_16 = datetime(2026, 4, 17, tzinfo=UTC)
    original = BitemporalRecord.new(
        key="fx:USDC/USD",
        valid_time=day_16,
        value={"px": 1.0001, "size": 1_000_000},
        source="bloomberg",
        source_trust_level="primary",
        transaction_time=day_16,
    )
    store.append(original)
    append_correction(
        store, original,
        corrected_value={"px": 1.0002, "size": 1_000_000},
        transaction_time=day_16 + timedelta(days=30),
    )

    # === Section: Three reads, same code, different clamps ===
    # Live (no clamp), as-of day 30 (before correction), as-of day 50 (after).
    print(f"Live view (no clamp):             {store.latest('fx:USDC/USD').value}")
    with AsOfView(store, transaction_time=day_16 + timedelta(days=14)) as view:
        print(f"As-of day 30 (pre-correction):    {view.latest('fx:USDC/USD').value}")
    with AsOfView(store, transaction_time=day_16 + timedelta(days=34)) as view:
        print(f"As-of day 50 (post-correction):   {view.latest('fx:USDC/USD').value}")

    # === Section: Writes are refused on a view of the past ===
    # An AsOfView is strictly read-only. Attempting to append through it
    # raises, because a write into a historical view would leak post-as-of
    # knowledge into the view's timeline.
    view = AsOfView(store, transaction_time=day_16 + timedelta(days=14))
    try:
        view.append(original)
    except Exception as e:
        print(f"\nWrite refused on AsOfView: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
