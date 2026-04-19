"""
02 — The correction pattern.

Bloomberg publishes a price. Later, Bloomberg discovers an error and
issues a correction. The architecturally correct response is NOT to
overwrite the original — it is to APPEND a new record with the same
valid_time as the original and a fresh transaction_time.

Run: python agentic-payments/02_correction_pattern.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _bootstrap  # noqa: F401,E402  — stubs briefcase._native if missing

from briefcase.bitemporal import (
    InMemoryBitemporalStore,
    append_correction,
)
from data.seed import (  # noqa: E402
    at,
    bloomberg_original_record,
    describe_record,
    print_table,
)


def main() -> None:
    store = InMemoryBitemporalStore()
    original = bloomberg_original_record()
    store.append(original)

    print("Initial state:")
    print_table([describe_record(r) for r in store.history("USDC/USD")])

    # Bloomberg issues a correction at t+30 days. The original record is
    # not touched; a new record is appended with the same valid_time.
    correction = append_correction(
        store,
        original,
        corrected_value={"px": 1.0002, "size": 1_000_000},
        transaction_time=at(46),  # 30 days after the original
    )

    print("\nAfter the correction is appended:")
    print_table([describe_record(r) for r in store.history("USDC/USD")])

    print("\nObservations:")
    print(f"  History length:           {len(store.history('USDC/USD'))}")
    print(f"  Original record_id:       {original.record_id}")
    print(f"  Correction record_id:     {correction.record_id}")
    print(f"  Correction.parent_record: {correction.parent_record_id}")
    print(f"  latest().value:           {store.latest('USDC/USD').value}")
    print(
        "\nThe original belief is preserved. The correction supersedes it for "
        "any query whose transaction_time clamp is at or after the correction's "
        "transaction_time. See 03_asof_replay.py for that query."
    )


if __name__ == "__main__":
    main()
