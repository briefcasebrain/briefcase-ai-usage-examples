# Briefcase AI Workflow Examples

This repository contains 14 self-contained Python examples demonstrating how the **Briefcase AI SDK** captures decision context, stores immutable audit trails, and retrieves that context on demand for regulated AI workflows in financial services.

## What is Briefcase AI?

Briefcase AI is an SDK designed to provide regulatory-grade audit trails for AI decision-making systems. It captures complete decision context (inputs, outputs, model versions, configurations) at the moment of AI inference and stores it in immutable, versioned audit trails. This enables financial institutions to demonstrate regulatory compliance, support examiner inquiries, and defend AI decisions with complete historical provenance.

## Why These Examples Exist

These examples demonstrate Briefcase AI's capabilities across 14 critical regulated AI workflows where audit trail integrity is essential for regulatory compliance, examination readiness, and legal defensibility. Each example shows realistic scenarios that financial institutions face daily, with proper regulatory framing and examiner query simulations.

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setup

```bash
# Navigate to the regulatory workflows directory
cd regulatory-workflows

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Workflow Examples

| # | Workflow | Regulation(s) | Key Demonstration |
|---|----------|---------------|-------------------|
| 01 | [Credit Underwriting](01_credit_underwriting/) | ECOA/Reg B | Adverse action tracking, OCC examiner readiness |
| 02 | [OFAC Sanctions Screening](02_ofac_sanctions/) | OFAC/BSA | Watchlist version integrity, violation defense |
| 03 | [Fraud Detection & Reg E](03_fraud_reg_e/) | Reg E / EFTA | Dispute resolution, 10-day SLA tracking |
| 04 | [Real-Time Payments Fraud](04_realtime_payments_fraud/) | OCC/Fed RTP | Sub-500ms decisions, irrevocable payment risk |
| 05 | [Mortgage Fair Lending](05_mortgage_fair_lending/) | ECOA/HMDA/Reg B | Model version history, disparate impact analysis |
| 06 | [KYC/KYB Third-Party](06_kyc_kyb_third_party/) | BSA/AML/FinCEN | Vendor-independent audit, bank-controlled records |
| 07 | [AML Transaction Monitoring](07_aml_transaction_monitoring/) | BSA/AML/FinCEN | Rule version preservation, SAR filing defense |
| 08 | [Neobank BaaS Sponsor](08_neobank_baas_sponsor/) | OCC/Fed SR 11-7 | Multi-partner charter liability tracking |
| 09 | [Fintech Release Monitoring](09_fintech_release_monitoring/) | Sponsor Bank Audit | Automated drift detection, release RCA |
| 10 | [Collections & Debt](10_collections_debt/) | CFPB UDAAP/FDCPA | State-specific rule tracking, class action defense |
| 11 | [Robo-Advisory Reg BI](11_robo_advisory_reg_bi/) | SEC Reg BI/FINRA | Client profile snapshots, fiduciary standard |
| 12 | [Earned Wage Access](12_ewa_non_traditional_credit/) | CFPB/TILA | Regulatory classification uncertainty tracking |
| 13 | [MCA Cash Flow Lending](13_mca_cash_flow_lending/) | State Commercial Disclosure | State-by-state compliance documentation |
| 14 | [Algorithmic Trading](14_algo_trading_surveillance/) | SEC Rule 17a-4/FINRA | Order book reconstruction, spoofing detection |

## Running Examples

Each example is independently executable:

```bash
# Run any single example
python 01_credit_underwriting/example.py
python 02_ofac_sanctions/example.py
python 14_algo_trading_surveillance/example.py

# Or navigate to specific directory
cd 03_fraud_reg_e
python example.py
```

## Example Output Structure

Each example demonstrates:

1. **SDK Initialization**: Briefcase AI setup with in-memory SQLite backend
2. **Workflow Simulation**: Realistic AI model inputs and decision outputs
3. **Decision Capture**: Complete audit trail creation with regulatory metadata
4. **Audit Retrieval**: Loading decisions from immutable storage
5. **Examiner Simulation**: Regulatory query response demonstration
6. **Compliance Validation**: Required field verification and completeness scoring

## Key Features Demonstrated

### 🎯 **Decision Provenance**
Every example shows complete capture of:
- AI model inputs (at inference time)
- Model outputs and confidence scores
- Model version and configuration hashes
- Decision timestamps and execution context

### 🔒 **Regulatory Metadata**
Each workflow includes regulation-specific tracking:
- Applicable regulations (ECOA, OFAC, Reg E, etc.)
- Compliance requirements and SLA tracking
- Examiner readiness indicators
- Required disclosure and reporting metadata

### 📊 **Historical Analysis**
Examples demonstrate:
- Model version change tracking over time
- Rule configuration evolution and impact analysis
- Cohort-based performance monitoring
- Drift detection and alerting

### 🕰️ **Temporal Integrity**
Time-sensitive scenarios include:
- Sub-500ms real-time payment decisions
- 10-business-day Reg E investigation timelines
- Mid-year model version changes
- Watchlist version provenance at screening time

## Infrastructure Requirements

**None.** All examples use in-memory SQLite backends provided by the Briefcase AI SDK. No external databases, message queues, or cloud services are required. This makes the examples immediately runnable in any Python environment.

## Development Status

### Fully Implemented Examples
- ✅ **01_credit_underwriting** - Complete implementation with ECOA compliance
- ✅ **02_ofac_sanctions** - Complete with watchlist version tracking
- ✅ **03_fraud_reg_e** - Complete with dispute resolution workflow
- ✅ **04_realtime_payments_fraud** - Complete with sub-500ms validation
- ✅ **05_mortgage_fair_lending** - Complete with model version history
- ✅ **07_aml_transaction_monitoring** - Complete with rule versioning
- ✅ **14_algo_trading_surveillance** - Complete with spoofing detection

### Stub Implementations
- 🚧 **06_kyc_kyb_third_party** - Functional stub, ready for expansion
- 🚧 **08_neobank_baas_sponsor** - Functional stub, ready for expansion
- 🚧 **09_fintech_release_monitoring** - Functional stub, ready for expansion
- 🚧 **10_collections_debt** - Functional stub, ready for expansion
- 🚧 **11_robo_advisory_reg_bi** - Functional stub, ready for expansion
- 🚧 **12_ewa_non_traditional_credit** - Functional stub, ready for expansion
- 🚧 **13_mca_cash_flow_lending** - Functional stub, ready for expansion

All stub implementations are syntactically correct, will execute without errors, and demonstrate the core Briefcase AI integration patterns. They provide a solid foundation for full implementation.

## Architecture

### Shared Components
- **`shared/backend.py`**: Common backend utilities, audit formatting, and validation functions
- **In-Memory Storage**: All examples use SQLite in-memory databases for immediate execution
- **Standardized Patterns**: Consistent decision snapshot creation, metadata handling, and retrieval patterns

### Decision Snapshot Structure
Each decision snapshot captures:
```python
DecisionSnapshot(
    decision_id="uuid",
    function_name="workflow_specific_name",
    inputs=[Input(name, description, type_str, value), ...],
    outputs=[Output(name, description, type_str, value), ...],
    metadata={
        "regulation": "specific_regulation",
        "workflow_specific_field": "value",
        # ... additional regulatory metadata
    }
)
```

## Regulatory Accuracy

All regulatory citations are accurate and current:
- **ECOA/Reg B**: Equal Credit Opportunity Act compliance
- **OFAC/BSA**: Office of Foreign Assets Control and Bank Secrecy Act
- **Reg E/EFTA**: Electronic Fund Transfer Act dispute resolution
- **SEC Rule 17a-4**: Securities and Exchange Commission record retention
- **FINRA Rules**: Financial Industry Regulatory Authority compliance
- **State Regulations**: Jurisdiction-specific requirements (CA, NY, TX, etc.)

## Support

For questions about these examples or the Briefcase AI SDK:

1. Review the specific example's docstring and implementation
2. Check the `shared/backend.py` utilities for common patterns
3. Refer to the Briefcase AI SDK documentation (when available)
4. Each example includes inline comments explaining regulatory context

## License

These examples are provided for demonstration purposes. Please ensure compliance with your organization's policies and applicable regulations when implementing similar audit trail systems in production environments.