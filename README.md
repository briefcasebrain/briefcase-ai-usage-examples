# Briefcase AI Usage Examples

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![briefcase-ai v3.0.0](https://img.shields.io/badge/briefcase--ai-v3.0.0-green.svg)](https://pypi.org/project/briefcase-ai/)

Production examples for the [Briefcase AI SDK](https://github.com/briefcasebrain/briefcase-ai-sdk) across financial services, e-commerce, and criminal justice. The repo is organized in two tiers — **primitives** (domain-neutral, one per file) and **compositions** (SDK primitives assembled into realistic stories).

## Setup

```bash
pip install briefcase-ai
```

Or use the automated setup: `./setup.sh` | Docker: `./docker-run.sh build && ./docker-run.sh run`

## Primitives — the `patterns/` library

Single-file, domain-neutral demonstrations of each SDK primitive. Each `.py` has a sibling `.ipynb` for notebook users; `patterns_walkthrough.ipynb` is the unified tour.

| # | Pattern | What it shows |
|---|---|---|
| 01 | [Decision capture](patterns/01_decision_capture.py) | `@capture` + `DecisionSnapshot` — the audit atom |
| 02 | [Bitemporal evidence](patterns/02_bitemporal_evidence.py) | `BitemporalRecord` + `InMemoryBitemporalStore` |
| 03 | [Correction append](patterns/03_correction_append.py) | `append_correction` — corrections never mutate originals |
| 04 | [Temporal replay](patterns/04_temporal_replay.py) | `AsOfView` — clamp reads to a historical instant |
| 05 | [Versioned policy](patterns/05_versioned_policy.py) | `PolicyRegistry` — bitemporal policy as-of |
| 06 | [Examiner bundle](patterns/06_examiner_bundle.py) | `ExaminerBundle` — content-addressed, verifiable artifact |
| 07 | [Cost attribution](patterns/07_cost_attribution.py) | `CostCalculator` — per-decision cost + monthly projection |
| 08 | [Drift detection](patterns/08_drift_detection.py) | `DriftCalculator` — baseline vs. window comparison |
| 09 | [PII sanitization](patterns/09_pii_sanitization.py) | `Sanitizer` — detect and redact PII |
| 10 | [Guardrail pipeline](patterns/10_guardrail_pipeline.py) | `GuardrailPipeline` — multi-stage allow/deny |
| 11 | [Decision replay](patterns/11_decision_replay.py) | Regression-test primitive — re-run candidates on stored inputs |

See [`patterns/README.md`](patterns/README.md) for the full composition matrix.

## Compositions — example suites

Primitives assembled into realistic, industry-specific narratives. The **Primitives** column lists which pattern numbers each suite composes.

| Suite | Run | Primitives | Description |
|-------|-----|:---:|-------------|
| [Agentic Payments](agentic-payments/) | `python agentic-payments/01_bitemporal_basics.py` | 02+03+04+05+06 | 7-script walkthrough: cross-border payment routing with bitemporal evidence, versioned policy, examiner bundles |
| [Regulatory Workflows](regulatory-workflows/) | `cd regulatory-workflows && python 01_credit_underwriting/example.py` | 01 everywhere; 02+03+04+06 in the five replay-enabled examples | 14 financial compliance workflows (ECOA, BSA, CFPB, SEC, OCC, FINRA). Five include a replay capstone: `01_credit_underwriting`, `02_ofac_sanctions`, `05_mortgage_fair_lending`, `07_aml_transaction_monitoring`, `14_algo_trading_surveillance` |
| [Vantara Commerce](vantara-briefcase-demo/) | `cd vantara-briefcase-demo && python 01_agent_discovery/example.py` | 01+07+08 | Agent discovery, cost attribution, drift detection, governance reporting |
| [Criminal Evidence](criminal-evidence-workflow/) | `cd criminal-evidence-workflow && python experiments/run_experiment.py --fast` | 01+09+10+11 | LLM evidence summarization with guardrails, replay, PII sanitization, SOC2 |

Each suite includes Python scripts, Jupyter notebooks, and detailed documentation.

## SDK Quick Reference

```python
from briefcase import DecisionSnapshot, Input, Output, ModelParameters, init
from briefcase.storage import SqliteBackend

init()

decision = DecisionSnapshot("credit_underwriting")
decision.add_input(Input("bureau_score", "685", "integer"))

output = Output("decision", "approve", "string")
output.with_confidence(0.92)
decision.add_output(output)

params = ModelParameters("gpt-4o")
params.with_provider("openai")
decision.with_model_parameters(params)

backend = SqliteBackend.in_memory()
decision_id = backend.save_decision(decision)
```

See also: `@capture` decorator, `CostCalculator`, `DriftCalculator`, `Sanitizer`, `GuardrailPipeline`, `ReplayEngine`, `BitemporalRecord`, `PolicyRegistry`, `AgentRouter`, `ExaminerBundle`. Full SDK docs at [briefcaseai.io](https://briefcaseai.io).

## Support

support@briefcaseai.org | [briefcaseai.io](https://briefcaseai.io) | [LICENSE](LICENSE)
