# Running Briefcase AI Demo Suites

This repository contains two comprehensive demo suites showcasing the Briefcase AI SDK for enterprise AI governance and decision tracking.

## Quick Setup (Recommended)

Use the automated setup script to install all dependencies and configure a virtual environment:

```bash
./setup.sh
```

This script will:
- Check Python 3.8+ installation
- Create a virtual environment (`briefcase-ai-demos-env`)
- Install briefcase-ai SDK and all dependencies
- Configure Jupyter kernel
- Verify the installation

After setup completes:

```bash
# Activate the environment
source briefcase-ai-demos-env/bin/activate

# Run demos
cd vantara-briefcase-demo
python 01_agent_discovery/example.py

# Or start Jupyter
jupyter notebook
```

## Manual Setup (Alternative)

### Python Version Compatibility

**Recommended: Python 3.11 or 3.12** for best compatibility with pre-compiled wheels.

Python 3.14+ may require compiling briefcase-ai from source, which needs Rust toolchain.

### 1. Install Briefcase AI SDK

The demos require the real Briefcase AI SDK to be installed:

```bash
pip install briefcase-ai
```

**Note**: If installation fails due to compilation errors, try using Python 3.11 or 3.12.

### 2. Install Additional Dependencies

For notebooks and analysis tools:

```bash
pip install pandas matplotlib seaborn jupyter numpy scipy
```

For development and testing (optional):

```bash
pip install pytest black
```

## Demo Suites Overview

### Vantara Commerce Demo (`vantara-briefcase-demo/`)

**Industry**: E-Commerce
**Focus**: Operational AI governance, cost attribution, performance monitoring
**Company Profile**: Vantara Commerce - 45 engineers, $3.8M annual AI spend, 180M monthly decisions

**Use Cases**:
- **Agent Discovery**: Automatically catalog AI agents across teams
- **Cost Attribution**: Track AI spend by team, model, and decision
- **Peak Season Drift**: Detect model performance degradation during traffic spikes
- **Governance Reporting**: Generate automated compliance reports

### Regulatory Workflows Demo (`regulatory-workflows/`)

**Industry**: Financial Services
**Focus**: Regulatory compliance, audit trails, examination readiness
**Use Cases**: Model risk management, regulatory examiner responses, compliance documentation

## Running the Vantara Commerce Demo

### Quick Start - Command Line Examples

Navigate to the demo directory:

```bash
cd vantara-briefcase-demo
```

Run individual examples:

```bash
# Agent Discovery - Find all AI agents across teams
python 01_agent_discovery/example.py

# Cost Attribution - Analyze AI spending by team
python 02_cost_attribution/example.py

# Peak Season Drift - Monitor model performance changes
python 03_peak_season_drift/example.py

# Governance Report - Generate compliance documentation
python 04_governance_report/example.py
```

### Interactive Jupyter Notebooks

Start Jupyter and explore the interactive walkthroughs:

```bash
jupyter notebook
```

Open notebooks:
- `01_agent_discovery/agent_discovery_walkthrough.ipynb`
- `02_cost_attribution/cost_attribution_walkthrough.ipynb`
- `03_peak_season_drift/peak_season_drift_walkthrough.ipynb`
- `04_governance_report/governance_report_walkthrough.ipynb`

### Expected Output

Each demo will:

1. **Initialize the SDK**: Connect to in-memory SQLite backend
2. **Create Decision Snapshots**: Simulate AI function execution with real instrumentation
3. **Store Audit Records**: Save decisions in immutable audit trail
4. **Generate Reports**: Produce governance-ready documentation
5. **Verify Data Integrity**: Confirm all records are retrievable

Example success output:
```
SUCCESS: Briefcase AI SDK initialized
SUCCESS: In-memory SQLite backend configured
SUCCESS: Generated 10 decisions with cost attribution
[AUDIT] search-ranking/search-ranker-v8 | decision_id=abc123... | stored OK
=== VANTARA COMMERCE — AI COST ATTRIBUTION REPORT ===
```

## Running the Regulatory Workflows Demo

### Command Line Examples

Navigate to the regulatory demo directory:

```bash
cd regulatory-workflows
```

Run regulatory compliance examples:

```bash
# Model Risk Management
python 01_model_risk_management/example.py

# Examiner Response System
python 02_examiner_responses/example.py

# Release Validation
python 03_release_validation/example.py

# Audit Trail Generation
python 04_audit_trails/example.py
```

### Expected Output for Regulatory

Each regulatory demo demonstrates:

1. **Regulatory-Grade Audit Trails**: Immutable decision records
2. **Examiner Response Capability**: Instant answers to regulatory queries
3. **Compliance Documentation**: Automated report generation
4. **Risk Management**: Model validation and monitoring

Example regulatory output:
```
=== REGULATORY EXAMINER RESPONSE ===
Query: Show me all pricing decisions from last quarter
Decision ID: reg_123...
AUDIT EVIDENCE:
Function: dynamic_pricing_decision
Execution Time: 2024-03-15T10:30:00Z
```

## Troubleshooting

### SDK Import Errors

If you see:
```
ERROR: Briefcase AI SDK is required for [demo name]
ImportError: No module named 'briefcase'
```

**Solution**: Install the SDK:
```bash
pip install briefcase-ai
```

### SDK Compilation Errors (Python 3.14+)

If you see compilation errors when installing briefcase-ai:

```
Building wheel for briefcase-ai (pyproject.toml) did not run successfully
```

**Solutions**:
1. **Use Python 3.11 or 3.12** (recommended):
   ```bash
   # Install via Homebrew
   brew install python@3.12
   # Use specific version for virtual environment
   python3.12 -m venv briefcase-ai-demos-env
   ```

2. **Install Rust toolchain** for compilation:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source ~/.cargo/env
   ```

### Missing Dependencies

For notebook visualization errors:
```bash
pip install matplotlib seaborn pandas
```

For Jupyter kernel issues:
```bash
pip install ipykernel
python -m ipykernel install --user
```

### Mock Implementation Warning

The demos are designed to **fail** if the real SDK is not available. There are no mock fallbacks - this ensures you're seeing authentic SDK instrumentation.

If you see references to "mock implementation", the real SDK is not properly installed.

## Understanding the Output

### Decision Snapshots

Each AI function call creates a `DecisionSnapshot` containing:
- **Inputs**: All parameters passed to the AI function
- **Outputs**: All results from the AI function
- **Metadata**: Timestamps, model versions, cost information
- **Audit Trail**: Immutable record for governance

### Audit Trail Format

```
[AUDIT] team/agent | decision_id=abc123... | stored OK
```

This confirms:
- Decision was captured from team/agent
- Assigned unique decision_id
- Successfully stored in audit trail
- Available for retrieval and analysis

### Cost Attribution

Each decision includes precise cost calculation:
```
Team: search-ranking | Model: gemini-1.5-flash | Cost: $0.0023
```

Based on:
- Actual token usage (input + output)
- Real vendor pricing (per-token costs)
- Exact model and provider used

### Governance Reports

Automated reports include:
- **Executive Summary**: High-level metrics and KPIs
- **Team Breakdown**: Cost and usage by organizational unit
- **Risk Analysis**: Regulatory flags and compliance gaps
- **Audit Certification**: Immutable trail documentation

## Architecture Notes

### Backend Configuration

Both demos use an in-memory SQLite backend for simplicity:

```python
backend_instance = backend.get_backend()  # Returns SqliteBackend.in_memory()
```

For production deployments, the SDK supports:
- PostgreSQL backends
- Cloud storage backends
- Enterprise data lakes

### Real SDK Integration

The demos use authentic Briefcase AI SDK patterns:

```python
# Real decision snapshot creation
from briefcase import DecisionSnapshot, Input, Output
from briefcase.storage import SqliteBackend

decision = DecisionSnapshot("function_name")
decision.add_input(Input("param", "value", "string"))
decision.add_output(Output("result", "output", "string"))

# Real backend storage
backend = SqliteBackend.in_memory()
decision_id = backend.save_decision(decision)
```

This ensures the demos reflect actual production usage.

## Next Steps

### For Enterprise Evaluation

1. **Run All Demos**: Experience the full governance workflow
2. **Review Generated Reports**: Understand compliance capabilities
3. **Examine Audit Trails**: Verify data integrity and retrievability
4. **Analyze Cost Attribution**: See bottom-up spend reconstruction

### For Technical Integration

1. **Study `shared/backend.py`**: Reference implementation patterns
2. **Review SDK Usage**: Real instrumentation examples
3. **Understand Data Models**: DecisionSnapshot structure
4. **Plan Production Deployment**: Backend and infrastructure needs

### For Compliance Teams

1. **Review Generated Reports**: Assess regulatory readiness
2. **Test Audit Trail Queries**: Verify examination response capability
3. **Evaluate Documentation**: Check completeness for auditors
4. **Plan Governance Workflows**: Integrate with existing processes

## Support

For questions about:
- **SDK Installation**: Check pip installation and Python environment
- **Demo Execution**: Review prerequisites and dependencies
- **Briefcase AI Platform**: Contact support@briefcaseai.org
- **Enterprise Licensing**: Contact support@briefcaseai.org

The demos provide a comprehensive introduction to enterprise AI governance with Briefcase AI. They demonstrate how the SDK transforms AI operations from black boxes into transparent, auditable, and governable systems.