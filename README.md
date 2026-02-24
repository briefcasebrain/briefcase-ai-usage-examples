# Briefcase AI Regulatory Workflow Examples

**Professional-grade examples for AI regulatory compliance in financial services**

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

This repository contains 14 comprehensive examples demonstrating how financial institutions can implement AI regulatory compliance workflows using the Briefcase AI SDK. Each example provides complete audit trail capabilities, examiner query support, and regulatory documentation required for financial services AI applications.

### Key Features

- **Complete Audit Trails**: Immutable decision snapshots with full regulatory context
- **Examiner Readiness**: Pre-built responses for regulatory examination queries
- **Multi-Jurisdictional**: State and federal compliance across all major regulations
- **Production Ready**: Professional code suitable for financial institution deployment
- **Comprehensive Coverage**: 14 critical regulated AI workflows

---

## Regulatory Workflows Covered

| Workflow | Primary Regulation | Regulatory Focus | Examiner Scenarios |
|----------|-------------------|------------------|-------------------|
| [01. Credit Underwriting](regulatory-workflows/01_credit_underwriting/) | ECOA/Reg B | Adverse action tracking, fair lending | OCC examination readiness |
| [02. OFAC Sanctions Screening](regulatory-workflows/02_ofac_sanctions/) | OFAC/BSA | Watchlist integrity, violation defense | AML compliance validation |
| [03. Fraud Detection & Reg E](regulatory-workflows/03_fraud_reg_e/) | Reg E/EFTA | Dispute resolution, liability management | Consumer protection compliance |
| [04. Real-Time Payments Fraud](regulatory-workflows/04_realtime_payments_fraud/) | Fed RTP/OCC | Sub-500ms decisions, irrevocable risk | Operational risk management |
| [05. Mortgage Fair Lending](regulatory-workflows/05_mortgage_fair_lending/) | ECOA/HMDA/Reg B | Disparate impact analysis | Fair lending examination |
| [06. KYC/KYB Third-Party](regulatory-workflows/06_kyc_kyb_third_party/) | BSA/AML/FinCEN | Vendor independence, audit control | Third-party risk management |
| [07. AML Transaction Monitoring](regulatory-workflows/07_aml_transaction_monitoring/) | BSA/AML/FinCEN | Rule preservation, SAR filing | AML compliance examination |
| [08. Neobank BaaS Sponsor](regulatory-workflows/08_neobank_baas_sponsor/) | OCC SR 11-7 | Charter liability, partner oversight | Sponsor bank examination |
| [09. Fintech Release Monitoring](regulatory-workflows/09_fintech_release_monitoring/) | Sponsor Oversight | Change management, drift detection | Technology risk assessment |
| [10. Collections & Debt Management](regulatory-workflows/10_collections_debt/) | CFPB UDAAP/FDCPA | State-specific compliance | Consumer compliance examination |
| [11. Robo-Advisory Regulation BI](regulatory-workflows/11_robo_advisory_reg_bi/) | SEC Reg BI/FINRA | Fiduciary standard, client protection | SEC compliance examination |
| [12. Earned Wage Access](regulatory-workflows/12_ewa_non_traditional_credit/) | CFPB/TILA | Classification uncertainty tracking | CFPB supervision |
| [13. MCA Cash Flow Lending](regulatory-workflows/13_mca_cash_flow_lending/) | State Commercial Disclosure | Multi-state compliance | Commercial finance examination |
| [14. Algorithmic Trading Surveillance](regulatory-workflows/14_algo_trading_surveillance/) | SEC 17a-4/FINRA | Market manipulation detection | Trading surveillance examination |

---

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Briefcase AI SDK (contact support@briefcasebrain.com for access)
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/briefcasebrain/briefcase-ai-regulatory-workflows.git
cd briefcase-ai-regulatory-workflows

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Briefcase AI SDK
pip install briefcase-ai
```

### Running Examples

Each workflow example is self-contained and can be run independently:

```bash
# Run credit underwriting example
cd regulatory-workflows/01_credit_underwriting
python example.py

# Run OFAC sanctions screening example
cd ../02_ofac_sanctions
python example.py

# View interactive Jupyter notebooks
cd ../01_credit_underwriting
jupyter notebook credit_underwriting_walkthrough.ipynb
```

---

## Repository Structure

```
regulatory-workflows/
├── 01_credit_underwriting/
│   ├── example.py                           # Complete Python implementation
│   └── credit_underwriting_walkthrough.ipynb   # Interactive Jupyter walkthrough
├── 02_ofac_sanctions/
│   ├── example.py
│   └── ofac_sanctions_walkthrough.ipynb
├── ... (all 14 workflows)
├── shared/
│   └── backend.py                           # Shared utilities and backend setup
├── README.md                               # Detailed workflow documentation
└── requirements.txt                        # Python dependencies
```

---

## Documentation

### For Financial Institutions

- **[Getting Started Guide](regulatory-workflows/README.md)** - Complete setup and usage instructions
- **[Regulatory Compliance Overview](regulatory-workflows/README.md#regulatory-compliance)** - Compliance framework details
- **[Examiner Query Examples](regulatory-workflows/README.md#examiner-simulation)** - Sample regulatory examination scenarios

### For Developers

- **[API Integration Guide](regulatory-workflows/shared/backend.py)** - Briefcase AI SDK integration patterns
- **[Audit Trail Architecture](regulatory-workflows/README.md#audit-trail-architecture)** - Decision snapshot design
- **[Testing and Validation](regulatory-workflows/README.md#testing)** - Quality assurance approaches

---

## Key Benefits

### For Compliance Teams
- **Regulatory Readiness**: Pre-built audit trails for all major financial regulations
- **Examiner Support**: Structured responses to typical regulatory examination queries
- **Risk Mitigation**: Complete documentation trail for AI decision justification

### For Technology Teams
- **Production Ready**: Professional-grade code suitable for financial institution deployment
- **Scalable Architecture**: Designed for high-volume financial services applications
- **Integration Friendly**: Clean APIs that integrate with existing compliance infrastructure

### For Risk Management
- **Audit Trail Integrity**: Immutable decision snapshots with cryptographic validation
- **Multi-Jurisdictional**: Compliance across federal and state regulatory frameworks
- **Defensibility**: Complete historical context for legal and regulatory defense

---

## Support and Licensing

### Business Software License (BSL 1.1)
This software is provided under the Business Software License 1.1. The license allows:
- **Internal use** within your organization
- **Development and testing** for compliance purposes
- **Production deployment** within licensed financial institutions

For production licensing and support:
- **Email**: support@briefcasebrain.com
- **Documentation**: https://docs.briefcasebrain.com
- **License Inquiries**: legal@briefcasebrain.com

### Enterprise Support
Available for licensed financial institutions:
- **Regulatory consultation** for compliance implementation
- **Custom workflow development** for institution-specific requirements
- **Integration support** for existing compliance infrastructure
- **Regulatory examination assistance** and documentation support

---

## Professional Services

Our team provides comprehensive professional services for financial institutions implementing AI regulatory compliance:

- **Compliance Assessment**: Review existing AI systems for regulatory gaps
- **Implementation Support**: Deploy Briefcase AI workflows in production environments
- **Regulatory Training**: Train compliance teams on AI audit trail best practices
- **Examination Preparation**: Support for regulatory examinations and documentation

Contact support@briefcasebrain.com for professional services inquiries.

---

## Security and Compliance

All workflow examples are designed with financial services security requirements:

- **Data Privacy**: No sensitive data transmission outside your environment
- **Audit Integrity**: Cryptographically secured decision snapshots
- **Regulatory Standards**: Designed for SOC 2 Type II and financial examination compliance
- **Multi-Tenant**: Safe for use in shared banking infrastructure

For security documentation and compliance certifications, contact security@briefcasebrain.com.

---

## Vantara Commerce E-Commerce Demo

**Complete enterprise AI governance demonstration for retail e-commerce**

In addition to the regulatory workflows above, this repository includes a comprehensive demo showcasing enterprise AI governance for a fictional large-scale retail e-commerce company, Vantara Commerce. This demo illustrates how organizations with multiple AI-powered teams can achieve complete governance and audit capabilities.

### Demo Overview

**Company Profile**: Vantara Commerce
- **Industry**: Retail E-Commerce
- **Scale**: 45 AI-using teams, 180M monthly decisions
- **AI Spend**: $3.8M annually across 4 vendors (OpenAI, Anthropic, Google Vertex, Cohere)
- **Challenge**: No central governance, cost attribution, or performance monitoring

### Four Complete Examples

| Module | Enterprise Challenge | Briefcase AI Solution |
|--------|---------------------|----------------------|
| **[01. Agent Discovery](vantara-briefcase-demo/01_agent_discovery/)** | No central AI agent registry | Self-populating discovery with shadow AI detection |
| **[02. Cost Attribution](vantara-briefcase-demo/02_cost_attribution/)** | $3.8M bill with no team breakdown | Per-decision cost tracking and optimization |
| **[03. Peak Season Drift](vantara-briefcase-demo/03_peak_season_drift/)** | Model regressions during Q4 | Instant root cause analysis and rollback guidance |
| **[04. Governance Report](vantara-briefcase-demo/04_governance_report/)** | 21-day manual compliance reports | Automated regulatory risk analysis in <1 second |

### Quick Start - Vantara Demo

```bash
# Run the complete Vantara Commerce demo
cd vantara-briefcase-demo

# Agent discovery - find all AI agents across 45 teams
python 01_agent_discovery/example.py

# Cost attribution - track $3.8M annual spend by team and decision
python 02_cost_attribution/example.py

# Peak season drift - detect Q4 model performance issues
python 03_peak_season_drift/example.py

# Governance reporting - generate compliance report in <1 second
python 04_governance_report/example.py
```

### Key Demonstrated Benefits

**Operational Impact**:
- **Discovery**: Continuous agent registry vs quarterly manual surveys
- **Cost Management**: Real-time spend tracking vs monthly invoice reconciliation
- **Incident Response**: 1-minute vs 2-5 day root cause analysis
- **Compliance**: 1-second vs 21-day report generation (672 engineer-hours saved)

**Financial Impact**:
- **Cost Optimization**: $609K annual savings from model right-sizing recommendations
- **Risk Mitigation**: Early detection of shadow AI and compliance gaps
- **Revenue Protection**: Rapid resolution of peak season performance issues

### Interactive Exploration

Each example includes both Python scripts and Jupyter notebooks:

```bash
# Launch interactive analysis
jupyter notebook vantara-briefcase-demo/01_agent_discovery/agent_discovery_walkthrough.ipynb
```

The Vantara Commerce demo provides a complete blueprint for implementing enterprise AI governance in high-volume, multi-team environments. See [vantara-briefcase-demo/README.md](vantara-briefcase-demo/README.md) for detailed documentation.

---

*Copyright 2026 Briefcase AI. All rights reserved.*