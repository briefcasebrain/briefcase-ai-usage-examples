"""
Pattern 03 — The correction pattern

What this shows: when an upstream source restates a value (Bloomberg issues a
correction, OFAC delists an entity on appeal, a credit bureau removes a
disputed tradeline), the correction is APPENDED with the same `valid_time`
and a fresh `transaction_time`. The original record is never mutated.
When to reach for it: any time an input may be restated after the fact, AND
you need to prove later what you knew BEFORE the restatement.
See also: patterns/02_bitemporal_evidence.py, patterns/04_temporal_replay.py
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from briefcase.bitemporal import (
    BitemporalRecord,
    InMemoryBitemporalStore,
    append_correction,
)

UTC = timezone.utc


def main() -> None:
    # === Section: Original observation ===
    # Bloomberg's original print lands on day 16: px=1.0001.
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
    print(f"Original record: px={original.value['px']} at t={original.transaction_time.date()}")

    # === Section: Correction appended ===
    # 30 days later, Bloomberg issues a correction — the print should have been
    # 1.0002. append_correction() creates a NEW record with the same valid_time
    # and a new transaction_time; it links back via parent_record_id.
    day_46 = day_16 + timedelta(days=30)
    correction = append_correction(
        store,
        original,
        corrected_value={"px": 1.0002, "size": 1_000_000},
        transaction_time=day_46,
    )
    print(f"Correction:      px={correction.value['px']} at t={correction.transaction_time.date()}")
    print(f"Correction.parent_record_id = {correction.parent_record_id}")
    print(f"  (points back to original.record_id = {original.record_id})")

    # === Section: Both records coexist ===
    # The store holds both. `latest()` returns the correction (most recent
    # transaction_time); `history()` returns both. The original belief is
    # preserved and recoverable via AsOfView (see pattern 04).
    hist = store.history("fx:USDC/USD")
    print(f"\nStore history length: {len(hist)} records")
    for r in hist:
        note = "(original)" if r.parent_record_id is None else "(correction)"
        print(f"  t={r.transaction_time.date()}  px={r.value['px']}  {note}")
    print(f"\nstore.latest('fx:USDC/USD').value = {store.latest('fx:USDC/USD').value}")


if __name__ == "__main__":
    main()
