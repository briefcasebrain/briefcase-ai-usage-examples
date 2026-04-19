"""
05 — Agent routing with evidence attribution.

An agent routes a LATAM cross-border payout. It needs (a) the policy in
effect today and (b) the evidence records that justified the inputs
(OFAC screen, FX print). The AgentRouter joins them and emits a
decision record that contains everything needed to replay the call.

Run: python agentic-payments/05_agent_routing.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _bootstrap  # noqa: F401,E402  — stubs briefcase._native if missing

from briefcase.bitemporal import InMemoryBitemporalStore
from briefcase.routing import AgentRouter, PolicyRegistry
from data.seed import (  # noqa: E402
    at,
    bloomberg_original_record,
    ofac_clean_record,
    stablecoin_policy_v1,
    stablecoin_policy_v2,
)


def main() -> None:
    # 1. Evidence store with the OFAC and FX observations.
    evidence = InMemoryBitemporalStore()
    ofac = ofac_clean_record()
    fx = bloomberg_original_record()
    evidence.append(ofac)
    evidence.append(fx)

    # 2. Policy registry with v1 (day 0) and v2 (day 60).
    registry = PolicyRegistry()
    registry.publish(stablecoin_policy_v1(), valid_from=at(0), transaction_time=at(0))
    registry.publish(stablecoin_policy_v2(), valid_from=at(60), transaction_time=at(60))

    # 3. Router configured for the cross-border payout use case.
    router = AgentRouter(
        registry,
        use_case="cross_border_payout",
        policy_id="stablecoin_router",
    )

    # 4. Route a LATAM payout.
    #    OFAC says counterparty is clean; FX print is fresh. Both inform the
    #    decision and are attached as evidence_refs.
    context = {
        "jurisdiction": "LATAM",
        "sanctioned": ofac.value["sanctioned"],
        "notional_usd": 250_000,
    }
    evidence_refs = [ofac.record_id, fx.record_id]

    print("=== Route 1: today (v2 is live) ===")
    decision_today = router.route(context, evidence_refs=evidence_refs)
    print(f"  use_case:         {decision_today.use_case}")
    print(f"  context:          {decision_today.context}")
    print(f"  candidates:       {decision_today.candidates}")
    print(f"  selected:         {decision_today.selected}")
    print(f"  policy_version:   {decision_today.policy_version}")
    print(f"  matched_rule_id:  {decision_today.matched_rule_id}")
    print(f"  rationale:        {decision_today.rationale}")
    print(f"  evidence_refs:    {len(decision_today.evidence_refs)} record(s)")

    print("\n=== Route 2: same context, clamped to day 30 (v1 was live) ===")
    decision_then = router.route(
        context, evidence_refs=evidence_refs, as_of_transaction_time=at(30)
    )
    print(f"  selected:         {decision_then.selected}")
    print(f"  policy_version:   {decision_then.policy_version}")
    print(f"  matched_rule_id:  {decision_then.matched_rule_id}")
    print(f"  rationale:        {decision_then.rationale}")

    print(
        "\nObservation: the LATAM context routes USDT under v1 and USDC under v2. "
        "Both decisions are reproducible — the registry holds both versions and "
        "the as-of clamp chooses one. No feature flag, no environment variable, "
        "no 'prod database at time T' snapshot. Just a clamp."
    )


if __name__ == "__main__":
    main()
