# Briefcase AI Usage Examples

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![briefcase-ai v3.0.0](https://img.shields.io/badge/briefcase--ai-v3.0.0-green.svg)](https://pypi.org/project/briefcase-ai/)

Production examples for the [Briefcase AI SDK](https://github.com/briefcasebrain/briefcase-ai-sdk) across financial services, e-commerce, and criminal justice.

## Setup

```bash
pip install briefcase-ai
```

Or use the automated setup: `./setup.sh` | Docker: `./docker-run.sh build && ./docker-run.sh run`

## Examples

| Suite | Run | Description |
|-------|-----|-------------|
| [Regulatory Workflows](regulatory-workflows/) | `cd regulatory-workflows && python 01_credit_underwriting/example.py` | 14 financial compliance workflows (ECOA, BSA, CFPB, SEC, OCC, FINRA) |
| [Vantara Commerce](vantara-briefcase-demo/) | `cd vantara-briefcase-demo && python 01_agent_discovery/example.py` | Agent discovery, cost attribution, drift detection, governance reporting |
| [Criminal Evidence](criminal-evidence-workflow/) | `cd criminal-evidence-workflow && python experiments/run_experiment.py --fast` | LLM evidence summarization with guardrails, replay, PII sanitization, SOC2 |

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

See also: `@capture` decorator, `CostCalculator`, `DriftCalculator`, `Sanitizer`, `GuardrailPipeline`, `ReplayEngine`. Full SDK docs at [briefcaseai.io](https://briefcaseai.io).

## Support

support@briefcaseai.org | [briefcaseai.io](https://briefcaseai.io) | [LICENSE](LICENSE)
