"""
01 — Bitemporal basics.

Build BitemporalRecord rows, append to the store, observe that the only
write primitive is INSERT.

Run: python agentic-payments/01_bitemporal_basics.py
"""

from __future__ import annotations

import os
import sys

# Allow running this script directly from the repo root.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _bootstrap  # noqa: F401,E402  — stubs briefcase._native if missing

from briefcase.bitemporal import (
    BitemporalRecord,
    InMemoryBitemporalStore,
)
from data.seed import (  # noqa: E402
    at,
    bloomberg_original_record,
    describe_record,
    ofac_clean_record,
    print_table,
)


def main() -> None:
    print("Building a bitemporal store of two evidence records.\n")

    store = InMemoryBitemporalStore()
    store.append(ofac_clean_record())
    store.append(bloomberg_original_record())

    print("Keys currently in the store:")
    for k in store.keys():
        print(f"  - {k}")
    print()

    print("Full history per key:")
    for k in store.keys():
        print(f"\nKey: {k}")
        print_table([describe_record(r) for r in store.history(k)])

    print(
        "\nNote: the store exposes append(), history(), latest(), as_of(), "
        "and keys(). There is no update() method by design."
    )
    print("Total rows:", len(store))


if __name__ == "__main__":
    main()
