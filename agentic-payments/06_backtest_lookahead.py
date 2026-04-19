"""
06 — The look-ahead trap, and how AsOfView closes it.

The look-ahead trap: a naive backtest reads the current store and asks
"what does this system think about USDC/USD on day 17?" — but the store
has already absorbed a correction that did not exist on day 17. The
backtest sees the future. The Sharpe ratio lifts. The trader loses
money in production.

AsOfView fixes this. Same code, same store, same query — but clamped.

Run: python agentic-payments/06_backtest_lookahead.py
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


def naive_backtest(store, day: int) -> dict:
    """Naive backtest: query the live store 'as of' a historical day.

    BUG: the store contains all corrections, including those appended
    after ``day``. This is the look-ahead trap.
    """
    return store.latest("USDC/USD").value


def asof_backtest(store, day: int) -> dict:
    """Correct backtest: clamp transaction_time to the historical day.

    Identical body to the naive version except for the AsOfView wrapper.
    """
    with AsOfView(store, transaction_time=at(day)) as view:
        return view.latest("USDC/USD").value


def main() -> None:
    # Set up the store as it would exist today: an original observation
    # plus a correction that landed 30 days later.
    store = InMemoryBitemporalStore()
    original = bloomberg_original_record()  # day 16
    store.append(original)
    append_correction(
        store,
        original,
        corrected_value={"px": 1.0002, "size": 1_000_000},
        transaction_time=at(46),  # correction landed day 46
    )

    print("Backtest question: 'what was the px on day 30?'\n")

    for day in (20, 30, 45, 50):
        naive = naive_backtest(store, day)
        correct = asof_backtest(store, day)
        tag = "   LEAK" if naive != correct else "  clean"
        print(
            f"  day {day:>3}: naive={naive['px']:.4f}  "
            f"as-of={correct['px']:.4f}  [{tag}]"
        )

    print()
    print(
        "The naive query returns 1.0002 on every day — the corrected value, "
        "which was not knowable until day 46. An as-of clamp returns 1.0001 "
        "for days 20, 30, 45 and 1.0002 for day 50. The divergence is the "
        "look-ahead that the AsOfView pattern eliminates."
    )
    print(
        "\nThe production code path and the backtest code path are the same "
        "function. Only the wrapper differs. That property — "
        "'backtest is production with a clamp' — is what makes the guarantee "
        "hold in the general case."
    )


if __name__ == "__main__":
    main()
