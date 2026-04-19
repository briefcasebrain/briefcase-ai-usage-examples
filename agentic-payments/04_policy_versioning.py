"""
04 — Versioned routing policy.

Bridge publishes v1 on day 0: LATAM routes USDT for liquidity. On day 60,
LATAM moves to USDC as compliant-issuer distribution expands. The registry
stores both versions bitemporally. Reading "the policy as-of day 50"
returns v1; reading "as-of day 90" returns v2 — with no reconstruction
from logs.

Run: python agentic-payments/04_policy_versioning.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _bootstrap  # noqa: F401,E402  — stubs briefcase._native if missing

from briefcase.routing import PolicyRegistry
from data.seed import (  # noqa: E402
    at,
    stablecoin_policy_v1,
    stablecoin_policy_v2,
)


def describe_policy(policy) -> None:
    if policy is None:
        print("  (no policy visible as-of that date)")
        return
    print(f"  policy_id:       {policy.policy_id}")
    print(f"  version:         {policy.version}")
    print(f"  description:     {policy.description}")
    print(f"  rules ({len(policy.rules)}):")
    for rule in policy.rules:
        print(f"    - {rule.rule_id}: {rule.condition} -> {rule.choice}")
    print(f"  default_choice:  {policy.default_choice}")


def main() -> None:
    registry = PolicyRegistry()

    # Publish v1 effective day 0, recorded day 0.
    v1 = stablecoin_policy_v1()
    registry.publish(v1, valid_from=at(0), transaction_time=at(0))
    print(f"Published v1 ({v1.version}) at transaction_time=day 0")

    # Publish v2 effective day 60, recorded day 60.
    v2 = stablecoin_policy_v2()
    registry.publish(v2, valid_from=at(60), transaction_time=at(60))
    print(f"Published v2 ({v2.version}) at transaction_time=day 60")

    print("\n--- Registry history for 'stablecoin_router' ---")
    for p in registry.history("stablecoin_router"):
        print(f"  {p.version}: {p.description}")

    print("\n--- As-of day 50 (before v2 published) ---")
    describe_policy(registry.get("stablecoin_router", as_of_transaction_time=at(50)))

    print("\n--- As-of day 90 (after v2 published) ---")
    describe_policy(registry.get("stablecoin_router", as_of_transaction_time=at(90)))

    print(
        "\nObservation: identical code path, different clamp, different policy. "
        "The v1 rule set is preserved by construction — nothing was overwritten. "
        "This is what lets the next script reproduce a routing decision months "
        "after the policy has moved on."
    )


if __name__ == "__main__":
    main()
