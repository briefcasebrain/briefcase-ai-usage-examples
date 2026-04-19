"""
07 — The examiner bundle.

Months after a decision ships, an examiner asks: "reproduce this routing
call, and prove the bundle you're handing me is the one you actually had
at the time." ExaminerBundle.build() joins the decision, the policy
as-of the decision, and the evidence records into a single JSON payload
with a SHA-256 content hash. verify() detects any tamper.

Run: python agentic-payments/07_examiner_bundle.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _bootstrap  # noqa: F401,E402  — stubs briefcase._native if missing

from briefcase.bitemporal import InMemoryBitemporalStore
from briefcase.compliance import BundleIntegrityError, ExaminerBundle
from briefcase.routing import AgentRouter, PolicyRegistry
from data.seed import (  # noqa: E402
    at,
    bloomberg_original_record,
    ofac_clean_record,
    stablecoin_policy_v1,
    stablecoin_policy_v2,
)


def main() -> None:
    # 1. Evidence + policy registry, as in script 05.
    evidence = InMemoryBitemporalStore()
    ofac = ofac_clean_record()
    fx = bloomberg_original_record()
    evidence.append(ofac)
    evidence.append(fx)

    registry = PolicyRegistry()
    registry.publish(stablecoin_policy_v1(), valid_from=at(0), transaction_time=at(0))
    registry.publish(stablecoin_policy_v2(), valid_from=at(60), transaction_time=at(60))

    # 2. Produce a decision under v1 (as if it happened on day 30).
    router = AgentRouter(
        registry, use_case="cross_border_payout", policy_id="stablecoin_router"
    )
    context = {
        "jurisdiction": "LATAM",
        "sanctioned": ofac.value["sanctioned"],
        "notional_usd": 250_000,
    }
    decision = router.route(
        context,
        evidence_refs=[ofac.record_id, fx.record_id],
        as_of_transaction_time=at(30),
    )
    # Anchor decided_at to day 30 so the bundle clamps there.
    decision.decided_at = at(30)

    print(f"Decision selected:       {decision.selected}")
    print(f"Decision policy_version: {decision.policy_version}")

    # 3. Build the bundle — clamps policy + joins evidence + hashes.
    bundle = ExaminerBundle.build(
        decision,
        evidence_store=evidence,
        policy_registry=registry,
        metadata={"use_case": decision.use_case, "notional_usd": context["notional_usd"]},
    )

    print("\n=== Bundle summary ===")
    print(f"  schema_version:          {bundle.schema_version}")
    print(f"  as_of_transaction_time:  {bundle.as_of_transaction_time}")
    print(f"  policy in bundle:        {bundle.policy['version']}  (expected 1.0.0)")
    print(f"  evidence rows in bundle: {len(bundle.evidence)}")
    print(f"  content_hash:            {bundle.content_hash}")

    # 4. Verify the untouched bundle.
    bundle.verify()
    print("\nverify() on the untouched bundle: OK")

    # 5. Round-trip through JSON.
    payload = bundle.to_json(indent=2)
    rehydrated = ExaminerBundle.from_json(payload)
    rehydrated.verify()
    print("verify() after JSON round-trip:   OK")

    # 6. Tamper check.
    tampered_dict = json.loads(payload)
    tampered_dict["decision"]["selected"] = "USDC"  # was USDT under v1
    tampered = ExaminerBundle.from_dict(tampered_dict)
    try:
        tampered.verify()
    except BundleIntegrityError as e:
        print(f"verify() on tampered bundle:      REJECTED ({type(e).__name__})")
        print(f"   └─ {str(e).splitlines()[0]}")

    print(
        "\nThe bundle is self-contained, reproducible, and integrity-checked. "
        "The content_hash fingerprints the decision + policy-as-of + evidence "
        "together. A downstream reviewer can rehydrate it from bytes and "
        "verify() without contacting the originating system."
    )


if __name__ == "__main__":
    main()
