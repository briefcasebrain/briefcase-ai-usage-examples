"""
Pattern 02 — Bitemporal evidence

What this shows: `BitemporalRecord` + `InMemoryBitemporalStore` — evidence carries
both world-time (`valid_time`) and system-time (`transaction_time`), and the store
is append-only by construction.
When to reach for it: any time a decision's inputs may be corrected, restated, or
superseded after the fact, and an auditor may ask what you knew on decision day.
See also: patterns/03_correction_append.py, patterns/04_temporal_replay.py
"""
from __future__ import annotations

from datetime import datetime, timezone

from briefcase.bitemporal import BitemporalRecord, InMemoryBitemporalStore

UTC = timezone.utc


def main() -> None:
    # === Section: Construct a BitemporalRecord directly ===
    # Every record carries key, value, valid_time, transaction_time, source,
    # trust level, metadata, and (later) an optional parent_record_id for
    # corrections. `BitemporalRecord.new()` assigns a fresh record_id.
    record = BitemporalRecord.new(
        key="fx:USDC/USD",
        valid_time=datetime(2026, 4, 17, tzinfo=UTC),
        value={"px": 1.0001, "size": 1_000_000},
        source="bloomberg",
        source_trust_level="primary",
        transaction_time=datetime(2026, 4, 17, tzinfo=UTC),
        metadata={"feed": "BVAL"},
    )
    print("BitemporalRecord.new(...) produces:")
    print(f"  record_id:         {record.record_id}")
    print(f"  key:               {record.key}")
    print(f"  valid_time:        {record.valid_time.isoformat()}")
    print(f"  transaction_time:  {record.transaction_time.isoformat()}")
    print(f"  value:             {record.value}")
    print(f"  source:            {record.source} (trust={record.source_trust_level})")
    print(f"  parent_record_id:  {record.parent_record_id}  (None = original)")

    # === Section: Append to an InMemoryBitemporalStore ===
    # The store exposes append(), history(), latest(), as_of(), and keys().
    # There is no update() — corrections go through append_correction()
    # (see patterns/03_correction_append.py).
    store = InMemoryBitemporalStore()
    store.append(record)
    store.append(
        BitemporalRecord.new(
            key="ofac:cp-42",
            valid_time=datetime(2026, 4, 17, tzinfo=UTC),
            value={"sanctioned": False, "jurisdiction": "US"},
            source="ofac",
            source_trust_level="primary",
            transaction_time=datetime(2026, 4, 17, tzinfo=UTC),
        )
    )

    print(f"\nStore has {len(store)} records across keys: {sorted(store.keys())}")

    # === Section: Read back ===
    # latest() returns the most recent record for a key; history() returns all.
    latest = store.latest("fx:USDC/USD")
    print(f"\nstore.latest('fx:USDC/USD').value = {latest.value}")
    print(f"len(store.history('fx:USDC/USD')) = {len(store.history('fx:USDC/USD'))}")


if __name__ == "__main__":
    main()
