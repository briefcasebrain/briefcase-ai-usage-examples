"""
03 — AsOfView: the API-wrapping pattern.

The examiner asks, months later: "what did your system believe on
day 17?" AsOfView wraps any bitemporal store and clamps reads to a
historical transaction_time. Application code does not change between
live operation and replay — only the clamp changes.

Run: python agentic-payments/03_asof_replay.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _bootstrap  # noqa: F401,E402  — stubs briefcase._native if missing

from briefcase.bitemporal import (
    AsOfView,
    InMemoryBitemporalStore,
    append_correction,
)
from data.seed import (  # noqa: E402
    at,
    bloomberg_original_record,
)


def main() -> None:
    store = InMemoryBitemporalStore()
    original = bloomberg_original_record()  # observed day 16
    store.append(original)
    append_correction(
        store, original, corrected_value={"px": 1.0002, "size": 1_000_000},
        transaction_time=at(46),
    )

    # Query 1: no clamp — live production view.
    live = store.latest("USDC/USD").value
    print(f"Live view (no clamp):                 {live}")

    # Query 2: clamp to day 30 — before the correction landed.
    with AsOfView(store, transaction_time=at(30)) as view:
        replayed_before = view.latest("USDC/USD").value
    print(f"As-of day 30 (before correction):     {replayed_before}")

    # Query 3: clamp to day 50 — after the correction landed.
    with AsOfView(store, transaction_time=at(50)) as view:
        replayed_after = view.latest("USDC/USD").value
    print(f"As-of day 50 (after correction):      {replayed_after}")

    print()
    print(
        "The three answers differ. That is the whole point. An examiner who "
        "asks 'what did you know on day 30' sees the pre-correction value. "
        "The store does not need to be reconstructed from logs — the answer "
        "is present by construction."
    )

    # Writes are refused on a view of the past.
    view = AsOfView(store, transaction_time=at(30))
    try:
        view.append(original)
    except Exception as e:
        print(f"\nWrite on AsOfView refused: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
