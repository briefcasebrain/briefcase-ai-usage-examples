"""
Synthetic data used across the walkthrough.

Deterministic by construction — every script imports from here and sees
the same records. Nothing hits the network.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from briefcase.bitemporal import BitemporalRecord
from briefcase.routing import PolicyRule, PolicyVersion


UTC = timezone.utc

# Canonical day-zero for the walkthrough. Every relative date is computed
# off this anchor so the outputs are reproducible.
ANCHOR = datetime(2026, 4, 1, tzinfo=UTC)


def at(days: int = 0, hours: int = 0) -> datetime:
    """Return ANCHOR + offset."""
    return ANCHOR + timedelta(days=days, hours=hours)


# ---------------------------------------------------------------------------
# Market-data evidence — the Steve Cannon scenario
# ---------------------------------------------------------------------------

def ofac_clean_record() -> BitemporalRecord:
    """OFAC says counterparty cp-42 is clean, as observed on day 16."""
    return BitemporalRecord.new(
        key="ofac:cp-42",
        valid_time=at(16),
        value={"sanctioned": False, "jurisdiction": "US"},
        source="ofac",
        source_trust_level="primary",
        transaction_time=at(16),
        metadata={"sdn_list_version": "2026-04-17"},
    )


def bloomberg_original_record() -> BitemporalRecord:
    """Bloomberg's initial price observation for USDC/USD on day 16."""
    return BitemporalRecord.new(
        key="USDC/USD",
        valid_time=at(16),
        value={"px": 1.0001, "size": 1_000_000},
        source="bloomberg",
        source_trust_level="primary",
        transaction_time=at(16),
        metadata={"feed": "BVAL", "version": "v2"},
    )


# ---------------------------------------------------------------------------
# Routing policy — the Bridge scenario
# ---------------------------------------------------------------------------

def stablecoin_policy_v1() -> PolicyVersion:
    """Day-zero policy: US/EU clean → USDC; LATAM/SEA → USDT; sanctioned → review."""
    return PolicyVersion(
        policy_id="stablecoin_router",
        version="1.0.0",
        description="Initial policy. LATAM and SEA route USDT for liquidity.",
        rules=[
            PolicyRule(
                rule_id="sanctioned_review",
                condition={"sanctioned": True},
                choice="human_review",
                rationale="Sanctioned counterparties always escalate",
            ),
            PolicyRule(
                rule_id="us_eu_usdc",
                condition={"jurisdiction": {"in": ["US", "EU"]}},
                choice="USDC",
                rationale="US/EU regulatory alignment favors USDC",
            ),
            PolicyRule(
                rule_id="em_usdt",
                condition={"jurisdiction": {"in": ["LATAM", "SEA"]}},
                choice="USDT",
                rationale="EM liquidity advantage for USDT",
            ),
        ],
        default_choice="human_review",
    )


def stablecoin_policy_v2() -> PolicyVersion:
    """Policy update on day 60: compliant issuers now cover LATAM too."""
    return PolicyVersion(
        policy_id="stablecoin_router",
        version="2.0.0",
        description=(
            "LATAM routes USDC as compliant issuer distribution expanded. "
            "SEA still uses USDT."
        ),
        rules=[
            PolicyRule(
                rule_id="sanctioned_review",
                condition={"sanctioned": True},
                choice="human_review",
                rationale="Sanctioned counterparties always escalate",
            ),
            PolicyRule(
                rule_id="compliant_usdc",
                condition={"jurisdiction": {"in": ["US", "EU", "LATAM"]}},
                choice="USDC",
                rationale="Compliant issuer covers three corridors",
            ),
            PolicyRule(
                rule_id="sea_usdt",
                condition={"jurisdiction": "SEA"},
                choice="USDT",
                rationale="SEA still depends on USDT liquidity",
            ),
        ],
        default_choice="human_review",
    )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def describe_record(r: BitemporalRecord) -> Dict[str, str]:
    """Compact, human-readable view of a record."""
    return {
        "key": r.key,
        "valid_time": r.valid_time.isoformat(),
        "transaction_time": r.transaction_time.isoformat(),
        "value": str(r.value),
        "source": r.source,
        "parent": r.parent_record_id or "—",
    }


def print_table(rows: List[Dict[str, str]]) -> None:
    """Tiny dependency-free table printer used across the walkthrough."""
    if not rows:
        print("  (empty)")
        return
    cols = list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r[c])) for r in rows)) for c in cols}
    header = "  ".join(c.ljust(widths[c]) for c in cols)
    sep = "  ".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in rows:
        print("  ".join(str(r[c]).ljust(widths[c]) for c in cols))
