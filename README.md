# Briefcase AI Usage Examples

Enterprise AI governance demonstrations for financial services, e-commerce, and criminal justice.

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![briefcase-ai v3.0.0](https://img.shields.io/badge/briefcase--ai-v3.0.0-green.svg)](https://pypi.org/project/briefcase-ai/)

| **Financial Services** | **E-Commerce** | **Criminal Justice** |
|------------------------|----------------|----------------------|
| 14 regulatory compliance workflows | 4 enterprise governance modules | LLM evidence summarization pipeline |
| Banks, credit unions, fintechs | Retail, e-commerce, tech companies | Law enforcement, prosecutors, courts |
| Examiner-ready audit trails | Multi-team AI oversight | Guardrails, replay, PII sanitization |
| OCC, CFPB, SEC compliance | Cost attribution and performance monitoring | SOC2 compliance, data lineage |

---

## Overview

These examples demonstrate the [Briefcase AI SDK](https://github.com/briefcasebrain/briefcase-ai-sdk) across three industry verticals. Each example produces immutable audit trails, cost attribution data, and compliance-ready documentation using production SDK patterns.

**Problems addressed:**
- No immutable record of AI decisions for regulatory examination
- AI spend without per-team, per-decision attribution
- Unknown agents deployed without governance oversight
- Model degradation with no root cause analysis
- Manual compliance reporting requiring weeks and multiple engineers

---

## Setup

### Option 1: Docker

```bash
./docker-run.sh build
./docker-run.sh test
./docker-run.sh run
./docker-run.sh jupyter  # http://localhost:8889
```

### Option 2: Local

```bash
# Automated setup (Python 3.11/3.12 recommended)
./setup.sh
source briefcase-ai-demos-env/bin/activate
```

### Option 3: Manual

```bash
python -m venv venv && source venv/bin/activate
pip install briefcase-ai
pip install -r regulatory-workflows/requirements.txt     # Financial services
pip install -r vantara-briefcase-demo/requirements.txt   # E-commerce
```

---

## Quick Start

<table>
<tr>
<td width="33%">

### Financial Services

```bash
cd regulatory-workflows

python 01_credit_underwriting/example.py
python 02_ofac_sanctions/example.py
```

14 workflows covering ECOA, BSA, CFPB, SEC, OCC, and FINRA compliance.

</td>
<td width="33%">

### E-Commerce

```bash
cd vantara-briefcase-demo

python 01_agent_discovery/example.py
python 02_cost_attribution/example.py
```

4 modules for agent discovery, cost attribution, drift detection, and governance reporting.

</td>
<td width="33%">

### Criminal Justice

```bash
cd criminal-evidence-workflow

python experiments/run_experiment.py --fast
pytest tests/ -v
```

LLM evidence summarization with guardrails, replay, routing, PII sanitization, and SOC2 compliance.

</td>
</tr>
</table>

---

## SDK Usage

All examples use the [Briefcase AI SDK](https://github.com/briefcasebrain/briefcase-ai-sdk) v3.0.0, imported as `briefcase` and installed via `pip install briefcase-ai`.

### Decision Tracking

```python
from briefcase import DecisionSnapshot, Input, Output, ModelParameters, init
from briefcase.storage import SqliteBackend

init()

# Create a decision snapshot
decision = DecisionSnapshot("credit_underwriting")
decision.add_input(Input("bureau_score", "685", "integer"))
decision.add_input(Input("annual_income", "65000.0", "float"))

output = Output("decision", "approve", "string")
output.with_confidence(0.92)
decision.add_output(output)

# Attach model metadata
params = ModelParameters("gpt-4o")
params.with_provider("openai")
decision.with_model_parameters(params)

decision.with_execution_time(42.5)
decision.add_tag("regulation", "ECOA/Reg B")

# Store and retrieve
backend = SqliteBackend.in_memory()
decision_id = backend.save_decision(decision)
retrieved = backend.load_decision(decision_id)
```

### Decorator-Based Tracking

```python
from briefcase.decorators import capture

@capture(decision_type="classify_text")
def classify(text: str) -> str:
    return model.predict(text)

result = classify("loan application data")  # Automatically tracked
```

### Additional Capabilities

| Module | Import | Purpose |
|--------|--------|---------|
| Cost calculation | `from briefcase.cost import CostCalculator` | Model cost estimation and budget monitoring |
| Drift detection | `from briefcase.drift import DriftCalculator` | Output consistency scoring and alerts |
| Data sanitization | `from briefcase.sanitize import Sanitizer` | PII redaction before storage |
| Correlation | `from briefcase.correlation import briefcase_workflow` | Cross-service workflow tracing |

---

## Financial Services: Regulatory Workflows

14 workflows for financial institution AI compliance, each with a Python script and Jupyter notebook.

| Workflow | Regulation | Focus |
|----------|-----------|-------|
| [01. Credit Underwriting](regulatory-workflows/01_credit_underwriting/) | ECOA/Reg B | Adverse action tracking, fair lending |
| [02. OFAC Sanctions Screening](regulatory-workflows/02_ofac_sanctions/) | OFAC/BSA | Watchlist integrity, violation defense |
| [03. Fraud Detection & Reg E](regulatory-workflows/03_fraud_reg_e/) | Reg E/EFTA | Dispute resolution, liability management |
| [04. Real-Time Payments Fraud](regulatory-workflows/04_realtime_payments_fraud/) | Fed RTP/OCC | Sub-500ms decisions, irrevocable risk |
| [05. Mortgage Fair Lending](regulatory-workflows/05_mortgage_fair_lending/) | ECOA/HMDA/Reg B | Disparate impact analysis |
| [06. KYC/KYB Third-Party](regulatory-workflows/06_kyc_kyb_third_party/) | BSA/AML/FinCEN | Vendor independence, audit control |
| [07. AML Transaction Monitoring](regulatory-workflows/07_aml_transaction_monitoring/) | BSA/AML/FinCEN | Rule preservation, SAR filing |
| [08. Neobank BaaS Sponsor](regulatory-workflows/08_neobank_baas_sponsor/) | OCC SR 11-7 | Charter liability, partner oversight |
| [09. Fintech Release Monitoring](regulatory-workflows/09_fintech_release_monitoring/) | Sponsor Oversight | Change management, drift detection |
| [10. Collections & Debt](regulatory-workflows/10_collections_debt/) | CFPB UDAAP/FDCPA | State-specific compliance |
| [11. Robo-Advisory Reg BI](regulatory-workflows/11_robo_advisory_reg_bi/) | SEC Reg BI/FINRA | Fiduciary standard, client protection |
| [12. Earned Wage Access](regulatory-workflows/12_ewa_non_traditional_credit/) | CFPB/TILA | Classification uncertainty tracking |
| [13. MCA Cash Flow Lending](regulatory-workflows/13_mca_cash_flow_lending/) | State Commercial | Multi-state compliance |
| [14. Algo Trading Surveillance](regulatory-workflows/14_algo_trading_surveillance/) | SEC 17a-4/FINRA | Market manipulation detection |

---

## E-Commerce: Vantara Commerce Demo

Enterprise AI governance for a simulated retailer with 45 teams, $3.8M annual AI spend, and 180M monthly decisions across OpenAI, Anthropic, Google Vertex, and Cohere.

| Module | Challenge | Outcome |
|--------|-----------|---------|
| [01. Agent Discovery](vantara-briefcase-demo/01_agent_discovery/) | No central AI registry | 10 agents discovered, 2 shadow AI identified |
| [02. Cost Attribution](vantara-briefcase-demo/02_cost_attribution/) | $3.8M with no team breakdown | Per-decision cost tracking, $609K savings identified |
| [03. Peak Season Drift](vantara-briefcase-demo/03_peak_season_drift/) | Q4 model regressions | Root cause analysis in <1 minute vs 2-5 days |
| [04. Governance Report](vantara-briefcase-demo/04_governance_report/) | 21-day manual reports | Automated report generation in <1 second |

---

## Criminal Justice: Evidence Summarization Workflow

LLM-powered evidence summarization for criminal investigations, instrumented end-to-end with the Briefcase AI SDK. Runs fully offline using pre-generated fixtures.

| Section | Capability | SDK Features |
|---------|-----------|-------------|
| Instrumented Pipeline | 5 reports x 2 models, automatic decision capture | `@capture`, `DecisionSnapshot`, `ModelParameters`, `detect_hardware()` |
| Structured Evaluation | 3 guardrails composed into weighted scorecard | `GuardrailPipeline`, `Scorecard`, `CostCalculator` |
| Error Reproduction | Stochastic failure detection at temperature=0.7 | `ReplayEngine`, `DriftCalculator`, event emission |
| Confidence Routing | Auto vs human review based on confidence threshold | `InternalRouter`, `RoutingDecision` |
| PII Sanitization | SSN, phone, email redaction from reports | `Sanitizer`, `sanitize_json` |
| Data Lineage | Version tracking, drift detection, external data monitoring | `ExternalDataTracker`, `PromptValidationEngine` |
| SOC2 Compliance | Automated control evaluation and report generation | `SOC2ReportGenerator` |

34 tests, all passing. See [criminal-evidence-workflow/README.md](criminal-evidence-workflow/README.md) for full documentation.

---

## Repository Structure

```
shared/
  backend.py                           # SDK wrapper and backend configuration
  ai_functions.py                      # Instrumented AI model simulations

regulatory-workflows/                  # Financial services (14 workflows)
  01_credit_underwriting/              # example.py + Jupyter notebook + README
  02_ofac_sanctions/
  ...
  14_algo_trading_surveillance/

vantara-briefcase-demo/                # E-commerce (4 modules)
  01_agent_discovery/
  02_cost_attribution/
  03_peak_season_drift/
  04_governance_report/

criminal-evidence-workflow/            # Criminal justice
  src/                                 # Pipeline, guardrails, evaluation, routing
  data/                                # 5 synthetic police reports + LLM fixtures
  experiments/                         # Full demo and model comparison scripts
  notebooks/                           # 4 interactive Jupyter walkthroughs
  tests/                               # 34 tests (pytest)
```

---

## Architecture

Every AI function call creates a `DecisionSnapshot` containing:

- **Inputs/Outputs**: Parameters and results with type annotations
- **Model metadata**: Provider, model name, version via `ModelParameters`
- **Execution context**: Timestamps, execution time, tags
- **Cost data**: Token usage mapped to vendor pricing
- **Governance flags**: Human-in-loop status, regulatory annotations

Decisions are stored in `SqliteBackend` (in-memory for demos, persistent for production). The audit trail supports query by agent, team, time period, and model version.

**Data security**: All processing is local. No API keys, credentials, or sensitive business data leave your environment.

---

## Results

| Metric | Financial Services | E-Commerce |
|--------|-------------------|------------|
| Compliance reporting | Examiner-ready responses | 672 hours reduced to 1 second |
| Cost optimization | Risk-adjusted ROI tracking | $609K annual savings identified |
| Incident response | Regulatory violation detection | 1 minute vs 2-5 day RCA |
| Agent discovery | Shadow AI identification | 100% coverage, zero IT access |
| Audit trail | Immutable regulatory evidence | 180M decisions tracked |

---

## Support

| | |
|-|-|
| General support | support@briefcaseai.org |
| Enterprise licensing | legal@briefcaseai.org |
| Professional services | services@briefcaseai.org |
| Security and compliance | security@briefcaseai.org |
| Documentation | https://briefcaseai.io |

**License**: Business Software License (BSL 1.1). See [LICENSE](LICENSE) for details.

---

*Copyright 2026 Briefcase AI. All rights reserved.*
