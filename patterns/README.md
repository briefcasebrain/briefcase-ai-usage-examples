# Briefcase AI — pattern library

Single-file, domain-neutral demonstrations of each SDK primitive. For readers who want to learn the SDK before picking a domain example, or who want to compose primitives in a domain this repo doesn't ship an example for.

Every pattern has:
- a `.py` script — runnable standalone in <1s, prints a tight narrative
- a `.ipynb` sibling — same code split into cells with markdown intros
- a `patterns_walkthrough.ipynb` unified tour — all 11 primitives in one notebook, for readers who prefer one file

```
pip install -r patterns/requirements.txt
python patterns/02_bitemporal_evidence.py   # or any other
```

## Index

| # | Primitive | What it shows |
|---|---|---|
| 01 | [`@capture` + `DecisionSnapshot`](01_decision_capture.py) | Auto-record function inputs/outputs/timing/errors. The audit atom. |
| 02 | [`BitemporalRecord` + `InMemoryBitemporalStore`](02_bitemporal_evidence.py) | Append-only evidence with `valid_time` + `transaction_time`. |
| 03 | [`append_correction`](03_correction_append.py) | Corrections are new records with a back-pointer. Original preserved. |
| 04 | [`AsOfView`](04_temporal_replay.py) | Clamp reads to a historical `transaction_time`. Same code, replay or live. |
| 05 | [`PolicyRegistry`](05_versioned_policy.py) | Versioned policy, bitemporal. "Which rules were live on day X?" |
| 06 | [`ExaminerBundle`](06_examiner_bundle.py) | Content-addressed, tamper-evident artifact joining decision + policy + evidence. |
| 07 | [`CostCalculator`](07_cost_attribution.py) | Per-decision cost from model + token usage. Monthly projection. |
| 08 | [`DriftCalculator`](08_drift_detection.py) | Output-distribution drift: baseline vs. current window. |
| 09 | [`Sanitizer`](09_pii_sanitization.py) | PII detection + redaction for free text and structured payloads. |
| 10 | [`GuardrailPipeline`](10_guardrail_pipeline.py) | Compose multiple allow/deny stages; `FIRST_DENY` short-circuits. |
| 11 | Decision replay via `DecisionSnapshot` | Re-run a candidate against stored inputs; diff outputs. |

## Composition matrix

Rows = primitives. Columns = example suites in this repo that compose them. A `✓` means the suite actively demonstrates that primitive in its capstone or main narrative.

| Primitive | agentic-payments | 02_ofac_sanctions | 01_credit_underwriting* | 05_mortgage_fair_lending* | 07_aml_transaction_monitoring* | 14_algo_trading_surveillance* | criminal-evidence-workflow | vantara-briefcase-demo |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 01 `@capture` + `DecisionSnapshot` |   | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 02 `BitemporalRecord` | ✓ | ✓ | ⏳ | ⏳ | ⏳ | ⏳ |   |   |
| 03 `append_correction` | ✓ | ✓ | ⏳ | ⏳ | ⏳ | ⏳ |   |   |
| 04 `AsOfView` | ✓ | ✓ | ⏳ | ⏳ | ⏳ | ⏳ |   |   |
| 05 `PolicyRegistry` | ✓ | ✓ |   |   |   |   |   |   |
| 06 `ExaminerBundle` | ✓ | ✓ | ⏳ | ⏳ | ⏳ | ⏳ |   |   |
| 07 `CostCalculator` |   |   |   |   |   |   |   | ✓ |
| 08 `DriftCalculator` |   |   |   |   |   |   | ✓ | ✓ |
| 09 `Sanitizer` |   |   |   |   |   |   | ✓ |   |
| 10 `GuardrailPipeline` |   |   |   |   |   |   | ✓ |   |
| 11 Decision replay |   |   |   |   |   |   | ✓ |   |

\* Rollout in progress — see [plan](../../.claude/plans/move-the-content-from-vivid-anchor.md). `02_ofac_sanctions` is the reference implementation; the other four regulatory examples will follow.

## How to read this library

- **Reading the SDK:** start at pattern 01, then 02 → 06 for the replay family, then 07–11 in any order.
- **Picking primitives for your domain:** skim the index; the "What it shows" column identifies which primitive answers which question.
- **Understanding a domain example:** find its column in the matrix. The ticked rows are the primitives it composes; jump to those pattern files for the minimal demonstrations.

## Notebook vs. script

The two are generated from the same source — the script is canonical. If you edit a pattern, regenerate the sibling notebook (the generator lives in the commit history; same logic each time). The `patterns_walkthrough.ipynb` is the integration tour and is hand-curated.
