# Agentic payments — end-to-end walkthrough

This walkthrough demonstrates the bitemporal evidence, versioned routing
policy, and examiner bundle primitives working together for an agentic
cross-border payment decision.

The scenario combines two architectural patterns:

- **Bitemporal storage** for evidence. Every fact carries `valid_time`
  (when it was true in the world) and `transaction_time` (when the
  system learned about it). Corrections are appended, never mutated.
- **Versioned routing policy** for the agent's decision logic. The agent's
  "if this use case, then this stablecoin" rules are themselves stored
  bitemporally so examiners can reconstruct which version was active on
  any past date.

The two combine to produce a reproducible **examiner bundle** — a
content-addressed artifact an examiner uses to verify, 18 months later,
why a specific decision was made.

## Prerequisites

```bash
pip install "briefcase-ai[bitemporal,compliance,routing,external]>=3.2.0"
```

The walkthrough uses only synthetic data and in-memory stores. No
external services are required.

## Narrative order

Run the scripts in numeric order. Each builds on the previous.

| Script | Concept |
| --- | --- |
| `01_bitemporal_basics.py` | `BitemporalRecord`, append-only store |
| `02_correction_pattern.py` | Bloomberg-style correction: append, don't mutate |
| `03_asof_replay.py` | `AsOfView` — the API-wrapping pattern |
| `04_policy_versioning.py` | `PolicyRegistry` with bitemporal policy rules |
| `05_agent_routing.py` | `AgentRouter` tying evidence + policy into one decision |
| `06_backtest_lookahead.py` | Why bitemporal is not optional for backtests |
| `07_examiner_bundle.py` | `ExaminerBundle` — the reproducible compliance artifact |

Run all of them:

```bash
for i in 01 02 03 04 05 06 07; do
  echo "=== $i ===" && python agentic-payments/${i}_*.py
done
```

## The one result to remember

`06_backtest_lookahead.py` and `07_examiner_bundle.py` both demonstrate
the same invariant:

> The naive query reads the current store. The as-of query reads the
> store as it stood on the decision date. For any decision whose inputs
> have since been corrected, these two return different values. The
> difference is the look-ahead bias — and it is exactly the thing an
> examiner will ask you to prove is not there.

## Mapping to Briefcase's governance use case

The scripts talk about stablecoin routing and market data because those
are the cleanest demonstrations. The identical primitives apply directly
to Briefcase's compliance use cases:

- **SAR narrative replay** — evidence was the OFAC SDN list as of day 0;
  examiner replays 18 months later and the bundle reconstructs the day-0
  view even though the SDN list has since changed.
- **Prior-auth decisions** — policy version in effect on the day a claim
  was adjudicated, not the current policy.
- **Multi-agent correlation** — every sub-agent's decision references
  the same bitemporal evidence set, so the full chain is reproducible.
