"""
Pattern 05 — Versioned routing policy

What this shows: `PolicyRegistry` stores policy versions bitemporally. Publishing
v2 does not erase v1 — reading "as-of day X" returns whichever version was live
at that transaction_time.
When to reach for it: any time the rules governing a decision can change and
you need to reproduce *which rules were in effect* on a past decision's day.
See also: patterns/04_temporal_replay.py, patterns/06_examiner_bundle.py
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from briefcase.routing import PolicyRegistry, PolicyRule, PolicyVersion

UTC = timezone.utc


def _policy(version: str, description: str, rules: list[PolicyRule]) -> PolicyVersion:
    return PolicyVersion(
        policy_id="stablecoin_router",
        version=version,
        description=description,
        rules=rules,
        default_choice="human_review",
    )


def main() -> None:
    # === Section: Publish v1 and v2 into the registry ===
    # v1 live from day 0; v2 live from day 60. Publication is bitemporal —
    # publishing v2 does not delete v1.
    registry = PolicyRegistry()
    day_0 = datetime(2026, 4, 1, tzinfo=UTC)

    v1 = _policy(
        "1.0.0",
        "LATAM routes USDT for liquidity.",
        [PolicyRule(rule_id="latam_usdt", condition={"jurisdiction": "LATAM"}, choice="USDT", rationale="EM liquidity")],
    )
    v2 = _policy(
        "2.0.0",
        "LATAM routes USDC as compliant issuer distribution expands.",
        [PolicyRule(rule_id="latam_usdc", condition={"jurisdiction": "LATAM"}, choice="USDC", rationale="compliant issuer")],
    )

    registry.publish(v1, valid_from=day_0, transaction_time=day_0)
    registry.publish(v2, valid_from=day_0 + timedelta(days=60), transaction_time=day_0 + timedelta(days=60))

    print("Registry history for 'stablecoin_router':")
    for p in registry.history("stablecoin_router"):
        print(f"  {p.version}: {p.description}")

    # === Section: As-of reads pick the right version ===
    # Reading "as-of day 50" returns v1; "as-of day 90" returns v2.
    for days in (50, 90):
        p = registry.get("stablecoin_router", as_of_transaction_time=day_0 + timedelta(days=days))
        print(f"\nAs-of day {days}: policy version = {p.version if p else '(none)'}")


if __name__ == "__main__":
    main()
