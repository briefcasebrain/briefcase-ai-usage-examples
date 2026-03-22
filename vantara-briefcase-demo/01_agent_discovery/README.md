# Agent Discovery - Vantara Commerce

## Overview

This example demonstrates how Briefcase AI solves the "shadow AI" problem for large enterprises like Vantara Commerce. With 45 product teams deploying AI features independently, the governance team had no central registry of active AI models, their vendors, or ownership information.

## The Problem

- **No Central Registry**: Product teams deploy AI without notifying governance
- **Shadow AI**: Unknown models running in production with no oversight
- **Vendor Sprawl**: No visibility into which AI vendors are being used
- **Compliance Blind Spots**: Cannot answer regulatory questions about AI usage
- **Manual Discovery**: Traditional approaches require IT access and weeks of investigation

## The Solution

Briefcase AI creates a self-populating agent registry through decision capture:

1. **Automatic Registration**: Every AI agent registers itself on first execution
2. **Zero IT Access**: No cloud account access or infrastructure scanning needed
3. **Real-time Discovery**: New agents appear immediately in the registry
4. **Complete Audit Trail**: Full governance metadata for each discovered agent

## Running the Example

### Prerequisites
- Python 3.9 or higher
- Briefcase AI SDK (falls back to mock implementation if not available)

### Basic Usage
```bash
cd 01_agent_discovery
python example.py
```

### Interactive Exploration
```bash
jupyter notebook agent_discovery_walkthrough.ipynb
```

## Expected Output

The example discovers 10 AI agents across Vantara's teams:

```
=== VANTARA COMMERCE — AI AGENT AUDIT REPORT ===
Generated: 2024-02-24 10:30:45
Total agents discovered: 10
Teams with active AI deployments: 10 of 10

AGENTS BY TEAM (sorted alphabetically):
  catalog-enrichment            title-enricher-exp            openai/gpt-4o              experiment   instrumented
  customer-support-ai           cx-triage-bot                 anthropic/claude-3-5-sonnet production   instrumented
  ...

ESTIMATED DAILY AI DECISIONS ACROSS FLEET: 12,572,500

SHADOW AI — PREVIOUSLY UNKNOWN AGENTS (2):
  [!] title-enricher-exp  (catalog-enrichment)    — first seen 2024-01-15 — environment: experiment
  [!] reorder-point-ai    (inventory-replenishment)— first seen 2024-02-10 — environment: staging

RISK FLAGS:
  [!] title-enricher-exp: experiment agent using gpt-4o (premium model) — no cost controls confirmed
  [!] reorder-point-ai: staging agent writing to output stream observed in production pipeline

DISCOVERY METHOD:
  7 agents: SDK instrumentation (zero IT access required)
  3 agents: output stream listener (Prometheus/Grafana)
  Cloud account access required: NONE
```

## Key Insights

### Discovery Statistics
- **10 agents** discovered across all 10 teams
- **12.5M daily decisions** across the AI fleet
- **2 shadow AI agents** previously unknown to governance
- **4 AI vendors** in use (OpenAI, Anthropic, Cohere, Google Vertex)

### Risk Identification
1. **title-enricher-exp**: Experiment using expensive GPT-4o without cost controls
2. **reorder-point-ai**: Staging agent detected in production pipeline

### Operational Benefits
- **Zero IT access** required for discovery
- **Real-time visibility** into AI deployments
- **Automatic compliance** documentation
- **Immediate risk flagging** for governance review

## Integration Guidance

### Production Deployment
1. Deploy Briefcase AI SDK across your AI applications
2. Configure central governance dashboard
3. Set up alerting for new agent discoveries
4. Integrate with existing compliance workflows

### Governance Workflows
- **Weekly Reviews**: New agent discoveries and risk flags
- **Quarterly Audits**: Comprehensive agent inventory reports
- **Compliance Reporting**: Automated regulatory documentation
- **Cost Management**: Agent-level spend attribution

## Technical Implementation

### Agent Registration
Each AI agent automatically creates a DecisionSnapshot on first execution containing:
- Agent metadata (name, team, vendor, model)
- Deployment information (environment, registration date)
- Governance data (ownership, compliance status)
- Operational metrics (estimated daily decisions)

### Data Storage
- All agent records stored in immutable audit trail
- Retrievable by governance_record_id for regulatory queries
- No external infrastructure dependencies (uses in-memory SQLite)

### Security Considerations
- No sensitive application code exposure
- No cloud account credentials required
- Agent metadata only (no business data)
- Compliant with enterprise security policies

## Related Examples

- **[02_cost_attribution](../02_cost_attribution/)**: Track spending by discovered agents
- **[03_peak_season_drift](../03_peak_season_drift/)**: Monitor performance of registered agents
- **[04_governance_report](../04_governance_report/)**: Generate compliance reports including agent inventory

## Support

For questions about implementing agent discovery in your organization:
- Review the interactive notebook for detailed walkthroughs
- Check the source code for implementation patterns
- Contact your Briefcase AI representative for enterprise guidance