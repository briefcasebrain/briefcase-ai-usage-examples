# Vantara Commerce — Briefcase AI Demo

This demo shows how Briefcase AI solves the enterprise AI governance problem for a fictional large retail e-commerce company (Vantara Commerce) with 45 AI-using teams, 180M monthly AI decisions, and $3.8M in annual AI vendor spend.

## The Problem

- 45 product teams deploying AI with no central agent registry
- $3.8M annual AI bill with no per-team, per-decision attribution
- Q4 model deployments causing mid-season regressions with no fast RCA path
- 21 days and 4 engineers to compile each quarterly AI governance report
- FTC and algorithmic pricing regulatory exposure on customer-facing AI outputs

## The Demo

| Module | Problem It Solves | Key Output |
|---|---|---|
| 01_agent_discovery | No central AI agent registry | Audit of all 10 agents — shadow AI flagged, no cloud access needed |
| 02_cost_attribution | $3.8M bill with no team-level breakdown | Per-team spend, cost-per-decision, model right-sizing savings |
| 03_peak_season_drift | Q4 model changes cause invisible regressions | RCA report identifying exact model version that degraded performance |
| 04_governance_report | 21-day manual report with 4 engineers | Full governance report in < 1 second with regulatory risk flags |

## Setup
pip install -r requirements.txt

## Run Any Example

### Command Line Execution
```bash
python vantara-briefcase-demo/01_agent_discovery/example.py
python vantara-briefcase-demo/02_cost_attribution/example.py
python vantara-briefcase-demo/03_peak_season_drift/example.py
python vantara-briefcase-demo/04_governance_report/example.py
```

### Interactive Jupyter Notebooks
For detailed analysis with visualizations and step-by-step walkthroughs:
```bash
cd vantara-briefcase-demo/01_agent_discovery && jupyter notebook agent_discovery_walkthrough.ipynb
cd vantara-briefcase-demo/02_cost_attribution && jupyter notebook cost_attribution_walkthrough.ipynb
cd vantara-briefcase-demo/03_peak_season_drift && jupyter notebook peak_season_drift_walkthrough.ipynb
cd vantara-briefcase-demo/04_governance_report && jupyter notebook governance_report_walkthrough.ipynb
```

No external infrastructure required. All data stored in-memory via SQLite.

## Company Profile: Vantara Commerce

**Industry**: Retail E-Commerce
**Domain**: vantara.com
**Scale**: 45 AI-using teams, 180M monthly decisions
**AI Spend**: $3.8M annually across 4 vendors
**Peak Season**: Q4 (4.2x cost multiplier)
**Compliance Challenge**: Manual governance reports take 21 days, 4 engineers

### AI Team Distribution
- search-ranking
- product-recommendations
- dynamic-pricing
- fraud-prevention
- returns-automation
- demand-forecasting
- catalog-enrichment
- customer-support-ai
- inventory-replenishment
- supplier-risk

### AI Vendor Portfolio
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Anthropic**: Claude-3.5-Sonnet, Claude-3-Haiku
- **Google Vertex**: Gemini-1.5-Pro, Gemini-1.5-Flash
- **Cohere**: Command-R, Command-R-Plus

## Example 01: Agent Discovery

**Problem**: No central registry of AI agents across 45 teams

**Demo**: Discovers 10 active AI agents through decision capture
- 2 "shadow AI" agents previously unknown to governance
- Zero cloud account access required
- Real-time agent registry through normal AI operations

**Key Output**:
```
=== VANTARA COMMERCE — AI AGENT AUDIT REPORT ===
Total agents discovered: 10
Teams with active AI deployments: 10 of 10
Estimated daily AI decisions across fleet: 12,607,500

SHADOW AI — PREVIOUSLY UNKNOWN AGENTS (2):
[!] title-enricher-exp (experiment agent using premium model)
[!] reorder-point-ai (staging agent detected in production)
```

**Time Savings**: Continuous real-time discovery vs quarterly manual surveys

**Interactive Analysis**: [agent_discovery_walkthrough.ipynb](01_agent_discovery/agent_discovery_walkthrough.ipynb) provides detailed visualizations and step-by-step analysis

## Example 02: Cost Attribution

**Problem**: $3.8M annual AI bill with no team-level breakdown

**Demo**: Attributes 25 decisions to teams with per-decision costs
- Bottom-up cost reconstruction from token usage
- Model right-sizing opportunities identified
- Q4 peak season cost impact analysis

**Key Output**:
```
TOTAL SPEND (SAMPLE): $0.0234 across 25 decisions
ESTIMATED MONTHLY SPEND (FLEET-WIDE): $316,667

MODEL RIGHT-SIZING OPPORTUNITY:
dynamic-pricing using gpt-4o at $0.004450/decision
Switching to gpt-4o-mini saves 75% per decision
At estimated volume → saves $609,094/year
```

**Time Savings**: Real-time spend tracking vs waiting for monthly invoices

**Interactive Analysis**: [cost_attribution_walkthrough.ipynb](02_cost_attribution/cost_attribution_walkthrough.ipynb) provides detailed cost analysis visualizations and optimization insights

## Example 03: Peak Season Drift Detection

**Problem**: Q4 model changes cause performance regressions with no fast root cause analysis

**Demo**: Compares pre/post Black Friday model performance
- Model version tracking across deployment waves
- Performance degradation detection and attribution
- Instant root cause analysis with rollback recommendations

**Key Output**:
```
SEARCH RANKING — MODEL VERSION CHANGE DETECTED:
Pre-BFCM (v8.2.1-stable): mean confidence 0.883, fallback rate 0%
Post-BFCM (v8.3.0-bfcm): mean confidence 0.508, fallback rate 33%
Root cause: model_version changed from v8.2.1-stable → v8.3.0-bfcm on Nov 28

Time to identify root cause: < 1 minute vs 2-5 days manual correlation
```

**Time Savings**: 1 minute vs 2-5 days for root cause analysis

**Interactive Analysis**: [peak_season_drift_walkthrough.ipynb](03_peak_season_drift/peak_season_drift_walkthrough.ipynb) provides detailed performance analysis and drift detection visualizations

## Example 04: Governance Report

**Problem**: Quarterly compliance reports take 21 days and 4 engineers

**Demo**: Generates comprehensive governance report from 18 decisions
- Human-in-loop tracking and compliance gap identification
- Regulatory risk analysis (FTC endorsement, algorithmic pricing)
- Vendor concentration and audit trail certification

**Key Output**:
```
=== VANTARA COMMERCE — AI GOVERNANCE REPORT ===
Total AI decisions captured: 18
Overall human-in-loop rate: 61%
Decisions with regulatory flags: 8 (44%)

REGULATORY RISK FLAGS:
[HIGH] product-recommendations: 2 of 3 personalization decisions had no human review
[HIGH] dynamic-pricing: 2 of 3 pricing decisions had no human review

Previous manual process: 21 days, 4 engineers
With Briefcase AI: < 1 second, 0 engineers
```

**Time Savings**: < 1 second vs 21 days (672 engineer-hours saved per report)

**Interactive Analysis**: [governance_report_walkthrough.ipynb](04_governance_report/governance_report_walkthrough.ipynb) provides comprehensive compliance analysis and regulatory risk assessment

## Key Benefits Demonstrated

### For AI Governance Teams
- **Agent Discovery**: Self-populating registry identifies shadow AI without IT access
- **Cost Attribution**: Per-decision costs enable team budgets and model optimization
- **Performance Monitoring**: Real-time drift detection with instant root cause analysis
- **Compliance Reporting**: Automated governance reports with regulatory risk analysis

### Operational Impact
- **Discovery**: Continuous vs quarterly manual surveys
- **Cost Management**: Real-time vs monthly invoice reconciliation
- **Incident Response**: 1-minute vs 2-5 day root cause analysis
- **Compliance**: 1-second vs 21-day report generation

### ROI Summary
- **Cost Optimization**: $609K annual savings from model right-sizing
- **Time Savings**: 672 engineer-hours saved per governance report
- **Risk Mitigation**: Early detection of shadow AI and compliance gaps
- **Revenue Protection**: Rapid resolution of peak season performance issues

## Technical Architecture

### Decision Capture
Every AI decision automatically creates a DecisionSnapshot containing:
- **Agent Metadata**: Team, model, version, deployment info
- **Execution Context**: Input/output data, token usage, timestamps
- **Cost Data**: Vendor pricing, per-decision costs
- **Governance Info**: Human-in-loop status, regulatory flags
- **Performance Metrics**: Confidence scores, business KPIs

### Audit Trail
- **Immutable Storage**: SQLite backend with decision preservation
- **Query Interface**: Retrieve by agent, team, time period, model version
- **Compliance Ready**: Full audit trail for regulatory examination
- **No External Dependencies**: Self-contained with no cloud requirements

### Data Security
- **Local Processing**: All data remains within organizational boundaries
- **No Secrets**: No API keys or credentials transmitted
- **Audit Only**: Captures metadata, not sensitive business data
- **Compliance**: Designed for financial services regulatory standards

## Integration Guidance

### Production Deployment
1. **SDK Integration**: Add Briefcase AI to existing AI applications
2. **Backend Setup**: Configure persistent storage (PostgreSQL/MySQL recommended)
3. **Dashboard Deployment**: Set up governance reporting interface
4. **Process Integration**: Connect to existing compliance workflows

### Scaling Considerations
- **High Volume**: Designed for 180M+ monthly decisions
- **Multi-Vendor**: Supports any AI provider (OpenAI, Anthropic, etc.)
- **Cross-Team**: Handles 45+ independent engineering teams
- **Peak Traffic**: Tested for 4.2x seasonal volume increases

## Getting Started

### Prerequisites
- Python 3.9+
- Briefcase AI SDK (contact support@briefcasebrain.com for access)

### Quick Start
```bash
git clone <repository>
cd vantara-briefcase-demo
pip install -r requirements.txt

# Run any example
python 01_agent_discovery/example.py
```

### Interactive Exploration
```bash
# Launch Jupyter for detailed analysis
jupyter notebook 01_agent_discovery/agent_discovery_walkthrough.ipynb
```

## Support

This demo showcases Briefcase AI's enterprise AI governance capabilities. For production deployment:

- **Enterprise Licensing**: Contact support@briefcasebrain.com
- **Integration Support**: Professional services available
- **Regulatory Guidance**: Compliance consulting for financial services
- **Custom Development**: Additional governance features and integrations

---

*Vantara Commerce is a fictional company created for demonstration purposes. All data, metrics, and scenarios are simulated to showcase Briefcase AI capabilities.*