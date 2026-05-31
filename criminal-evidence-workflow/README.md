# Criminal Evidence Summarization Workflow

An end-to-end demonstration of how the **Briefcase AI SDK** instruments, evaluates, and triages an LLM-powered evidence-summarization pipeline for criminal justice. Every AI-generated summary is auditable, reproducible, and traceable to its exact source document.

The workflow runs entirely offline. Pre-generated fixtures simulate LLM outputs so you can explore every SDK capability without API keys, Docker, or external services.

---

## Table of Contents

- [Setup](#setup)
- [Running the Demo](#running-the-demo)
- [What the Demo Shows](#what-the-demo-shows)
- [Demo Output](#demo-output)
- [Interactive Notebooks](#interactive-notebooks)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [How the Mock Layer Works](#how-the-mock-layer-works)
- [SDK Surface Coverage](#sdk-surface-coverage)
- [Test Data](#test-data)
- [Using Real LLMs](#using-real-llms)
- [Deployment Constraints](#deployment-constraints)

---

## Setup

### Prerequisites

| Requirement | Version |
|------------|---------|
| Python | 3.9 or higher |
| pip | Any recent version |
| OS | macOS, Linux, or Windows |

No Docker, no database servers, no cloud accounts.

### Install

```bash
# 1. Clone the repository
git clone <repo-url>
cd criminal-evidence-workflow

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install the project and dependencies
pip install -e .
```

This installs:
- `briefcase-ai` — the SDK being demonstrated
- `rouge-score` — ROUGE-L metric for the factual accuracy guardrail

No `openai`, `anthropic`, or `langchain` packages are installed by default. Those are optional for live mode.

### Verify Installation

```bash
python -c "import briefcase; print(f'briefcase-ai {briefcase.__version__} installed')"
```

---

## Running the Demo

### Full Demo (Recommended First Run)

```bash
python experiments/run_experiment.py --fast
```

This runs all 7 sections end-to-end in under 1 second. The `--fast` flag skips simulated latency. Without it, `MockLLMProvider` adds realistic delays (800–2500ms per call) to simulate real API behavior.

### Model Comparison Only

```bash
python experiments/compare_models.py
```

Prints a side-by-side GPT-4o vs Claude Sonnet comparison table with guardrail scores, costs, and per-report detail.

### Individual Modules

Each source file is independently runnable:

```bash
python -m src.pipeline          # Single report summarization
python -m src.evaluation        # Full evaluation with comparison table
python -m src.triage            # Replay + routing demo
python -m src.sanitization      # PII redaction demo
python -m src.lineage           # Versioning + drift + compliance
python -m src.validation        # Evidence reference validation
```

---

## What the Demo Shows

### Section 1: Instrumented Pipeline

Every LLM call is wrapped by the `@capture` decorator for automatic observability and persisted as a `DecisionSnapshot` with:
- **Inputs**: source document text and summarization query
- **Outputs**: generated summary with model confidence score
- **Model parameters**: model name, provider, temperature, max tokens
- **Execution time**: wall-clock latency of the LLM call
- **Data version**: SHA-256 content hash of the source document (maps to lakeFS commit SHAs in production)
- **Hardware metadata**: execution environment type and name via `detect_hardware()` for reproducibility
- **Execution context**: Python runtime version and `briefcase-ai` dependency version
- **Data reference**: URI pointer to the source file with fingerprint

Evidence references are validated via `PromptValidationEngine` before summarization. Ten decisions are stored across 5 reports and 2 models (GPT-4o, Claude Sonnet), all persisted to `SqliteBackend` configured through `briefcase.setup()`. The pipeline uses `briefcase_workflow` for W3C traceparent propagation.

### Section 2: Structured Evaluation

Three `GuardrailEnv` implementations evaluate every summary using classical NLP — no LLM-as-judge:

| Guardrail | What It Catches | Method | Threshold |
|-----------|----------------|--------|-----------|
| **FactualAccuracyEnv** | Missing or hallucinated facts | ROUGE-L (60% weight) + keyword entity overlap (40%) against ground truth | Composite >= 0.5 |
| **ConfidenceCalibrationEnv** | Overconfident or underconfident models | `|confidence - accuracy|` calibration error | Error < 0.2 |
| **CrossDocConsistencyEnv** | Contradictions between related reports | Entity extraction (addresses, stores, people, amounts) + comparison | Zero contradictions |

All three are composed into a `GuardrailPipeline` with `PipelineMode.ALL` and feed into a weighted `Scorecard`:
- 50% factual accuracy
- 30% confidence calibration
- 20% cross-document consistency

The `Scorecard` is attached to each `DecisionSnapshot` via `decision.with_scorecard()`.

`CostCalculator` computes per-summary dollar cost from token usage (`estimate_cost`) and compares models (`compare_models`). Each evaluation run is tagged with `ExperimentMetadata` for A/B tracking.

### Section 3: Stochastic Failure Detection

The same report is summarized twice at `temperature=0.7`. The fixture pair produces meaningfully different output:

- Original: confidence 0.87, detailed summary with specific entity names
- Replay: confidence 0.82, vaguer summary with fewer specifics
- Drift score: 0.686 (scale 0–1)

`ReplayEngine` validates both stored snapshots via `replay()` in strict mode, plus `replay_batch()` for batch validation. The manual comparison confirms `outputs_match=False` — the model is non-deterministic at this temperature. A `drift.detected` event is emitted via `emit_drift_detected()`.

### Section 4: Confidence-Based Routing

`ConfidenceRouter(confidence_threshold=0.85)` reads the `Output.confidence` from each stored `DecisionSnapshot` and routes:

| Report | Confidence | Action | Why |
|--------|-----------|--------|-----|
| report_001 | 0.93 | `auto` | Clear burglary, unambiguous facts |
| report_003 | 0.62 | `human_review` | Three witnesses contradict each other on every material detail |

The router loads decisions from `SqliteBackend` via `storage.load_decision()` to read confidence. Reports routed to `human_review` emit a `decision.low_confidence` event via `emit_low_confidence()`.

### Section 5: PII Sanitization

Report 002 (DUI traffic stop) contains 9 PII items:
- SSN: `478-93-6152`
- Phone numbers: `(510) 555-8734`, `(510) 555-4271`, and others
- Email addresses: `maria.fitzgerald@gmail.com`, `rjfitzgerald@coastlinefin.com`, and others

The Rust-powered `Sanitizer` redacts all of them:
- `sanitize(text)` returns a `SanitizationResult` with `.sanitized` text and `.redactions` list
- `sanitize_json(dict)` processes structured decision payloads

### Section 6: Data Lineage & Drift

**Reference validation**: Before summarization, `PromptValidationEngine` validates that evidence references exist. Both `report_001` and `report_001_amended` pass validation.

**Version tracking**: Report 001 exists in two versions — original and amended (with a detective's addendum identifying a suspect via AFIS). Content hashing produces different version tags (`853251b1869f` vs `3ba04c9ef750`), linking each decision to its exact input.

**Output drift**: `DriftCalculator.calculate_drift()` compares the two summaries, returning `drift_score=0.521` and `consistency_score=0.479`. A `drift.detected` event is emitted via `emit_drift_detected()`.

**External data tracking**: `ExternalDataTracker` monitors the evidence source with `SnapshotPolicy(frequency=ON_CHANGE)`. After tracking the original file and detecting drift against the amended version: `has_changed=True`, `drift_score=1.0`, `size_delta=835 bytes`.

---

## Demo Output

```
+======================================================================+
|  BRIEFCASE AI v3.2.1 -- Criminal Evidence Summarization POC         |
|  Mode: Mocked (fixture-backed)   |  Reports: 5  |  Models: 2    |
+======================================================================+

>> Section 1: Instrumented Pipeline
   Prompt validation: 5/5 references validated
   Processing 5 reports x 2 models...
   [ok] 10 DecisionSnapshots stored in decisions.db

>> Section 2: Evaluation (3 GuardrailEnvs + Scorecard + CostCalculator)

   Model           | Avg Accuracy | Avg Calibr. | Consistency | Avg Latency |   Avg Cost
   ────────────────+──────────────+─────────────+─────────────+─────────────+───────────
   gpt-4o          |         0.56 |        0.72 |        1.00 |         0ms | $  0.0142
   claude-sonnet   |         0.49 |        0.68 |        0.70 |         0ms | $  0.0099

   Scorecard composite: gpt-4o=0.698, claude-sonnet=0.589
   Cost comparison: claude-3-5-sonnet is 27.4% cheaper (saves $0.0038/summary)

>> Section 3: Error Reproduction (ReplayEngine)
   Outputs match: False | Drift score: 0.686
   [!!] STOCHASTIC FAILURE DETECTED — same input, different output

>> Section 4: Confidence Routing (ConfidenceRouter)
   report_003 (conf=0.62) -> action=human_review  <-- flagged for review
   report_001 (conf=0.93) -> action=auto

>> Section 5: PII Sanitization (Sanitizer)
   9 PII items redacted from report_002.txt
   SSN: 478-93-6152 -> [REDACTED_SSN]
   Phone: (510) 555-8734 -> [REDACTED_PHONE]
   Email: maria.fitzgerald@gmail.com -> [REDACTED_EMAIL]

>> Section 6: Data Lineage & Drift
   report_001 v1: hash=853251b1869f | v2: hash=3ba04c9ef750
     validation: passed
   DriftCalculator: drift_score=0.521
   ExternalDataTracker: source changed, size_delta=835 bytes

  Events emitted: 3 (drift.detected=2, decision.low_confidence=1)
  No API keys used. Run with --live for real LLM calls.
```

---

## Interactive Notebooks

Four Jupyter notebooks walk through each capability interactively with markdown explanations between cells. All cells use `MockLLMProvider` — no API keys needed.

| Notebook | Focus | What You'll Explore |
|----------|-------|---------------------|
| **01 — Pipeline & Decision Tracking** | Instrumentation | `@capture` decorator, `briefcase.setup()` config, `detect_hardware()` metadata, `DecisionSnapshot` inspection, GPT-4o vs Claude Sonnet comparison, batch processing, content-hash versioning |
| **02 — Evaluation & Guardrails** | Structured validation | Run each guardrail individually on good vs bad reports, see `Effect.ALLOW`/`DENY` decisions with metadata, compose into `Scorecard`, full model comparison table, per-report calibration analysis, `CostCalculator` token tracking |
| **03 — Error Reproduction & Triage** | Failure handling | Stochastic runs with drift detection, `emit_drift_detected` events, `ReplayEngine` validation, `ConfidenceRouter` routing with `emit_low_confidence` events, `Sanitizer` PII redaction, event bus inspection |
| **04 — Data Lineage & Compliance** | Auditability | `PromptValidationEngine` reference checking, version-linked decisions, `DriftCalculator` with event emission, `MockLakeFSClient` → `VersionedClient` production pattern |

### Running Notebooks

```bash
# Install Jupyter if needed
pip install jupyter

# Launch the notebook server
jupyter notebook notebooks/

# Or execute headlessly (useful for CI)
pip install nbconvert ipykernel
jupyter execute notebooks/01_pipeline_and_decision_tracking.ipynb
```

---

## Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run the full test suite
pytest tests/ -v
```

**30 tests, ~2 seconds, zero network calls.** All tests use `MockLLMProvider(simulate_latency=False)`.

| Test File | What It Covers | Tests |
|-----------|---------------|-------|
| `test_pipeline.py` | `DecisionSnapshot` creation, storage, retrieval, data versioning, model info, multi-model support, hardware metadata | 7 |
| `test_guardrails.py` | `FactualAccuracyEnv` scoring, `ConfidenceCalibrationEnv` allow/deny, `CrossDocConsistencyEnv` address mismatch detection, same-model consistency | 6 |
| `test_replay.py` | Stochastic output mismatch, deterministic match, `ConfidenceRouter` routing for low/high confidence, `Sanitizer` SSN and phone redaction | 6 |
| `test_lineage.py` | Version hash uniqueness, `data_version` tag presence, amended report produces different summary, all reports versioned | 4 |
| `test_validation.py` | `EvidenceExtractor` reference extraction, `EvidenceResolver` error for missing reports, `PromptValidationEngine` pass/fail | 7 |
| `test_events.py` | `InMemoryEventBus` collection, `emit_low_confidence`, `emit_drift_detected`, event field validation | 4 |

---

## Project Structure

```
criminal-evidence-workflow/
├── README.md
├── pyproject.toml                     # Dependencies, build config, pytest config
│
├── data/
│   ├── police_reports/                # 5 synthetic reports + 1 amended version
│   │   ├── report_001.txt             #   Residential burglary (clear facts)
│   │   ├── report_001_amended.txt     #   Same + detective addendum (AFIS match)
│   │   ├── report_002.txt             #   DUI traffic stop (PII-heavy)
│   │   ├── report_003.txt             #   Assault with 3 conflicting witnesses
│   │   ├── report_004.txt             #   Retail theft at Bay Area Electronics
│   │   ├── report_005.txt             #   Earlier theft at same store
│   │   └── *_ground_truth.json        #   Key facts, entities, expected keywords (5 files)
│   │
│   └── fixtures/                      # 21 pre-generated LLM output + validation scenarios
│       ├── report_001_gpt-4o.json             # temp=0.0, conf=0.93
│       ├── report_001_claude-sonnet.json       # temp=0.0, conf=0.90
│       ├── report_001_gpt-4o_t0.7.json        # temp=0.7, conf=0.87
│       ├── report_001_gpt-4o_t0.7_replay.json # replay variant (different output)
│       ├── report_001_amended_gpt-4o.json     # summary of amended report
│       ├── report_003_gpt-4o.json             # conf=0.62 (low — conflicting witnesses)
│       └── ...                                # 5 reports x 2 models, partial temp=0.7 coverage
│
├── src/
│   ├── __init__.py
│   ├── config.py                      # Centralized briefcase.setup() + InMemoryEventBus
│   ├── mock_llm.py                    # MockLLMProvider: fixture-backed, zero API calls
│   ├── pipeline.py                    # @capture + DecisionSnapshot + detect_hardware()
│   ├── validation.py                  # PromptValidationEngine + EvidenceExtractor/Resolver
│   ├── evaluation.py                  # GuardrailPipeline + Scorecard + CostCalculator
│   ├── triage.py                      # ReplayEngine + ConfidenceRouter + event emission
│   ├── sanitization.py                # Sanitizer PII redaction
│   ├── lineage.py                     # DataRef versioning + ExternalDataTracker + events
│   └── guardrails/
│       ├── __init__.py
│       ├── factual_accuracy.py        # ROUGE-L + keyword entity overlap
│       ├── confidence_calibration.py  # |confidence - accuracy| calibration check
│       └── consistency.py             # Cross-document entity contradiction detection
│
├── experiments/
│   ├── run_experiment.py              # Full demo with validation + events (--fast, --live)
│   └── compare_models.py             # Side-by-side model comparison table
│
├── notebooks/
│   ├── 01_pipeline_and_decision_tracking.ipynb
│   ├── 02_evaluation_and_guardrails.ipynb
│   ├── 03_error_reproduction_and_triage.ipynb
│   └── 04_data_lineage_and_compliance.ipynb
│
└── tests/
    ├── __init__.py
    ├── test_pipeline.py
    ├── test_guardrails.py
    ├── test_replay.py
    ├── test_lineage.py
    ├── test_validation.py
    └── test_events.py
```

---

## How the Mock Layer Works

`MockLLMProvider` returns pre-generated responses from `data/fixtures/` with zero API calls:

```python
from src.mock_llm import MockLLMProvider

llm = MockLLMProvider(model="gpt-4o", temperature=0.0, simulate_latency=False)
result = await llm.generate("report_001", "Summarize this report")
# Returns: {
#   "summary": "On March 15, 2024, at approximately 0247 hours...",
#   "confidence": 0.93,
#   "token_usage": {"prompt_tokens": 1847, "completion_tokens": 289, "total_tokens": 2136},
#   "model": "gpt-4o",
#   "provider": "openai",
#   "temperature": 0.0,
# }
```

**Fixture key format**: `{report_id}_{model}[_t{temperature}][_replay].json`

Examples: `report_001_gpt-4o.json`, `report_003_claude-sonnet.json`, `report_001_gpt-4o_t0.7_replay.json`

**Fixture design choices** that make each demo section work:

| Design Choice | Why | Which Demo |
|--------------|-----|------------|
| Temperature 0.0 fixtures have high confidence (0.86–0.93) | Baseline for comparison | Pipeline, Evaluation |
| Temperature 0.7 fixtures have varied confidence (0.55–0.87) | Shows stochastic behavior | Replay |
| Report 003 always produces low confidence (0.55–0.62) | Conflicting witnesses make summarization genuinely hard | Routing to `human_review` |
| Report 002 summaries include raw PII from source | SSN, phone, email pass through to output | Sanitization |
| Report 005 Claude Sonnet says "Lakeshore Boulevard" | Source report says "Lakeshore Avenue" | Consistency guardrail catches it |
| Replay fixtures (`_replay` suffix) differ substantially | Not just one word changed — different structure, different detail level | `outputs_match=False` |
| Amended report fixture includes addendum details | New suspect, AFIS match, updated description | Lineage drift |

**Model presets** are available for convenience:

```python
from src.mock_llm import GPT4O, GPT4O_STOCHASTIC, CLAUDE_SONNET, ALL_MODELS
```

---

## SDK Surface Coverage

Every SDK module listed below is instantiated and called with real arguments in the demo — not just imported.

### Core (Rust via PyO3)

| Class | Methods Used | File |
|-------|-------------|------|
| `DecisionSnapshot` | `add_input`, `add_output`, `add_tag`, `with_model_parameters`, `with_execution_time`, `with_scorecard` | `pipeline.py`, `evaluation.py` |
| `Input` | constructor with `(name, value, data_type)` | `pipeline.py` |
| `Output` | constructor, `with_confidence` | `pipeline.py` |
| `ModelParameters` | constructor, `with_provider`, `with_parameter` | `pipeline.py` |
| `HardwareMetadata` | `detect_hardware()` → `.hardware_type`, `.name` | `pipeline.py` |
| `SqliteBackend` | constructor, `save_decision`, `load_decision` | `config.py`, `triage.py` |
| `Scorecard` | `add_score`, `composite_score` | `evaluation.py` |
| `ReplayEngine` | `replay` (strict mode), `replay_batch` | `triage.py` |
| `DriftCalculator` | `calculate_drift` → `DriftMetrics` (`.drift_score`, `.consistency_score`, `.agreement_rate`) | `triage.py`, `lineage.py` |
| `CostCalculator` | `estimate_cost` → `CostEstimate` (`.total_cost`), `compare_models`, `get_available_models` | `evaluation.py` |
| `Sanitizer` | `sanitize` → `SanitizationResult` (`.sanitized`, `.redactions`), `sanitize_json`, `analyze_pii`, `contains_pii` | `sanitization.py` |
| `DataRef` | constructor with `(uri, fingerprint)`, `with_version` | `pipeline.py` |
| `ExecutionContext` | `with_runtime_version`, `with_dependency`, `with_random_seed` | `pipeline.py` |
| `ExperimentMetadata` | constructor with `(experiment_id, run_index, total_runs)` | `evaluation.py` |

### Python SDK

| Module | Class / Function | File |
|--------|-----------------|------|
| `briefcase.decorators` | `@capture` decorator (auto-records inputs, outputs, timing, errors) | `pipeline.py` |
| `briefcase.config` | `setup()` → `BriefcaseConfig`, global SDK configuration | `config.py` |
| `briefcase.hardware` | `detect_hardware()` → `HardwareMetadata` | `pipeline.py` |
| `briefcase.correlation` | `briefcase_workflow` context manager | `pipeline.py` |
| `briefcase.validation.engine` | `PromptValidationEngine`, `Extractor`, `Resolver` protocols | `validation.py` |
| `briefcase.validation.errors` | `ValidationReport`, `ValidationError`, `ValidationErrorCode` | `validation.py` |
| `briefcase.events.emitter` | `emit_low_confidence()`, `emit_drift_detected()` | `triage.py`, `lineage.py` |
| `briefcase.events.types` | `BriefcaseEvent` dataclass | `config.py` |
| `briefcase.guardrails` | `GuardrailEnv` protocol, `EvalRequest`, `EvalResult`, `Effect.ALLOW`/`DENY` | `guardrails/*.py` |
| `briefcase.guardrails` | `GuardrailPipeline`, `PipelineMode.ALL` | `evaluation.py` |
| `briefcase.routing` | `BaseRouter`, `RoutingDecision` — extended by local `ConfidenceRouter` | `triage.py` |
| `briefcase.external_data` | `ExternalDataTracker`, `SnapshotPolicy`, `SnapshotFrequency.ON_CHANGE` | `lineage.py` |

---

## Test Data

All 5 police reports are **synthetic and fictional**. No real evidence data is used.

| Report | Incident Type | Key Feature |
|--------|--------------|-------------|
| `report_001` | Residential burglary | Clear facts, high confidence baseline. Victim David Park, forced entry through rear window, laptop and jewelry stolen, neighbor eyewitness, Ring camera footage. |
| `report_001_amended` | Same + detective addendum | Added 3 days later: updated suspect description (6 ft, tattoo, Honda Civic), AFIS fingerprint match to Marcus Webb (prior convictions). |
| `report_002` | DUI traffic stop | PII-heavy: driver SSN `478-93-6152`, multiple phone numbers, email addresses, employer info. BAC 0.14%, failed field sobriety tests. |
| `report_003` | Aggravated assault | Three witnesses contradict each other on: number of attackers (2 vs 3), suspect description (red jacket vs blue/black jacket, different races), direction fled (south vs west vs east), duration (30 sec vs 2 min), whether items were taken, and whether victim knew attackers. |
| `report_004` | Retail theft (April) | Bay Area Electronics, 3200 Lakeshore Avenue. Two-person team, magnet key, $6,195 in iPhones and Samsung phones. Second incident in 30 days. |
| `report_005` | Retail theft (March) | Same store, same MO, $3,996 in iPhones. Paired with report_004 for consistency checking. Witness section has intentional address error ("Lakeshore Boulevard"). |

Each report has a `*_ground_truth.json` file with:
- `incident_type`, `date`, `location`
- `key_facts` — bulleted list of material facts
- `entities` — officers, victims, witnesses, suspects, evidence, locations
- `expected_summary_keywords` — terms the factual accuracy guardrail checks for
- `conflicting_details` (report_003 only) — structured witness contradictions

---

## Using Real LLMs

The `--live` flag is a placeholder for swapping in real API calls. The architecture is designed so that replacing `MockLLMProvider` with a real provider requires changing only the provider instantiation — the pipeline, guardrails, replay, routing, and lineage code stays the same.

```bash
# Install live dependencies
pip install -e ".[live]"

# This installs: langchain, langchain-openai, openai, anthropic

# Set API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Run
python experiments/run_experiment.py --live
```

The `[live]` extra adds:
- `langchain >= 0.2.0`
- `langchain-openai >= 0.1.0`
- `openai >= 1.0.0`
- `anthropic >= 0.25.0`

---

## Deployment Constraints

This workflow runs within the constraints of grant-funded criminal justice infrastructure:

| Constraint | How It's Satisfied |
|-----------|-------------------|
| **Open source** | `briefcase-ai` is Apache-2.0, published on PyPI |
| **Azure Gov Cloud** | `SqliteBackend` is fully offline — no external service calls, no telemetry endpoints |
| **Air-gappable** | Zero network dependencies in default mode; `pip install` is the only step that touches the internet |
| **No fine-tuned models** | Off-the-shelf GPT-4o and Claude Sonnet only |
| **Audit-ready** | Content-hash–versioned `DecisionSnapshot` lineage plus `DriftCalculator` event emission produce a reconstructable audit trail |
| **Privacy-first** | All demo data is synthetic; `Sanitizer` handles real PII at the SDK level |
| **Python 3.9+** | Compatible with older Azure Gov Cloud runtimes |
| **No Docker required** | Single `pip install`, runs directly on the host |
