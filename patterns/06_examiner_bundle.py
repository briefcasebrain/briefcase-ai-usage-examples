"""
Pattern 06 — The examiner bundle

What this shows: `ExaminerBundle.build()` joins a decision + the policy-as-of
decision + the evidence records referenced by the decision into a single JSON
payload with a SHA-256 content hash. `verify()` detects any mutation.
When to reach for it: when you need to hand an auditor a self-contained,
verifiable artifact — one file that reproduces the decision offline without
contacting the originating system.
See also: patterns/02_bitemporal_evidence.py, patterns/04_temporal_replay.py, patterns/05_versioned_policy.py
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from briefcase.bitemporal import BitemporalRecord, InMemoryBitemporalStore
from briefcase.compliance import BundleIntegrityError, ExaminerBundle
from briefcase.routing import (
    AgentRoutingDecision,
    PolicyRegistry,
    PolicyRule,
    PolicyVersion,
)

UTC = timezone.utc


def main() -> None:
    # === Section: Evidence + policy registry ===
    # One evidence record plus a minimal policy. In a real system both come
    # from the existing bitemporal store + registry; the bundle just joins them.
    day_0 = datetime(2026, 4, 1, tzinfo=UTC)
    evidence = InMemoryBitemporalStore()
    fx = BitemporalRecord.new(
        key="fx:USDC/USD",
        valid_time=day_0,
        value={"px": 1.0001},
        source="bloomberg",
        source_trust_level="primary",
        transaction_time=day_0,
    )
    evidence.append(fx)

    registry = PolicyRegistry()
    registry.publish(
        PolicyVersion(
            policy_id="fx_check",
            version="1.0.0",
            description="Block if FX px deviates from peg by >2bps.",
            rules=[PolicyRule(rule_id="peg_check", condition={"within_peg": True}, choice="allow", rationale="within peg")],
            default_choice="block",
        ),
        valid_from=day_0,
        transaction_time=day_0,
    )

    # === Section: Build and fingerprint the bundle ===
    # A decision (projected here for demo) references the evidence by record_id.
    # ExaminerBundle.build() clamps policy to decided_at and captures everything.
    decision = AgentRoutingDecision(
        decision_id="demo-001",
        use_case="fx_routing",
        context={"px": 1.0001},
        candidates=["allow", "block"],
        selected="allow",
        policy_id="fx_check",
        policy_version="1.0.0",
        matched_rule_id="peg_check",
        evidence_refs=[fx.record_id],
        rationale="within peg",
        decided_at=day_0 + timedelta(hours=1),
    )

    bundle = ExaminerBundle.build(
        decision,
        evidence_store=evidence,
        policy_registry=registry,
        metadata={"doc": "pattern 06 demo"},
    )
    print(f"Bundle assembled:")
    print(f"  content_hash:   {bundle.content_hash}")
    print(f"  policy version: v{bundle.policy['version']}")
    print(f"  evidence rows:  {len(bundle.evidence)}")

    # === Section: Verify, round-trip, tamper-check ===
    # verify() passes on the untouched bundle and after JSON round-trip; any
    # mutation (here: flipping the decision) causes it to raise.
    bundle.verify()
    print(f"\nverify() on untouched bundle:    OK")

    payload = bundle.to_json(indent=2)
    ExaminerBundle.from_json(payload).verify()
    print(f"verify() after JSON round-trip:  OK")

    tampered = json.loads(payload)
    tampered["decision"]["selected"] = "block"
    try:
        ExaminerBundle.from_dict(tampered).verify()
    except BundleIntegrityError as e:
        print(f"verify() on tampered bundle:     REJECTED ({type(e).__name__})")


if __name__ == "__main__":
    main()
