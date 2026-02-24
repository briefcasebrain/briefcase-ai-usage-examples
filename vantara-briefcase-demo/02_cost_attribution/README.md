# Cost Attribution - Vantara Commerce

## Overview

This example demonstrates how Briefcase AI solves the enterprise AI cost visibility problem for Vantara Commerce. With a $3.8M annual AI bill spread across 4 vendors (OpenAI, Anthropic, Cohere, Google Vertex), finance teams receive only aggregate invoices with no visibility into which teams, models, or decisions drive costs.

## The Problem

- **Aggregate Billing**: Vendors bill total token consumption with no team breakdown
- **No Cost Attribution**: Cannot determine if search ranking or product recommendations costs more
- **Model Selection Blindness**: Engineering cannot justify premium model choices without cost data
- **Peak Season Invisibility**: Q4 cost spikes (4.2x baseline) appear only when invoices arrive
- **Budget Management**: No ability to set team-level budgets or track spend in real-time

## The Solution

Briefcase AI captures cost at the decision level, enabling precise bottom-up attribution:

1. **Per-Decision Costing**: Every AI decision includes input/output token costs
2. **Team Attribution**: Aggregate individual decisions to team-level spend
3. **Model Comparison**: Compare actual costs across different model choices
4. **Peak Season Tracking**: Real-time visibility into seasonal cost multipliers
5. **Right-Sizing Analysis**: Identify opportunities to switch to cheaper models

## Running the Example

### Prerequisites
- Python 3.9 or higher
- Briefcase AI SDK (falls back to mock implementation if not available)

### Basic Usage
```bash
cd 02_cost_attribution
python example.py
```

### Interactive Analysis
```bash
jupyter notebook cost_attribution_walkthrough.ipynb
```

## Expected Output

The example analyzes 25 decisions across 10 teams with realistic token usage and costs:

```
=== VANTARA COMMERCE — AI SPEND ATTRIBUTION (LAST 30 DAYS) ===
Generated: 2024-02-24 10:45:30

TOTAL SPEND (SAMPLE): $0.0234 across 25 decisions
ESTIMATED MONTHLY SPEND (FLEET-WIDE): $316,667  # $3.8M / 12
ANNUAL RUN-RATE (THIS SAMPLE EXTRAPOLATED): $675,360,000

BY TEAM (sorted by spend descending):
  dynamic-pricing                   2 decisions      2,100 tokens    $0.0089  [openai/gpt-4o]
  catalog-enrichment                3 decisions      8,500 tokens    $0.0067  [openai/gpt-4o]
  demand-forecasting                2 decisions     12,800 tokens    $0.0045  [google-vertex/gemini-1.5-pro]
  ...

HIGHEST COST PER DECISION:
  dynamic-pricing / gpt-4o: $0.004450 per decision
  At 500,000 daily decisions → $2,225.00/day → $812,125/year

MODEL RIGHT-SIZING OPPORTUNITY:
  dynamic-pricing is using gpt-4o at $0.004450/decision
  Switching to gpt-4o-mini saves 75% per decision
  At estimated volume → saves $609,094/year

PEAK SEASON ALERT (Q4 — Oct/Nov/Dec):
  Vantara's Q4 AI spend runs 4.2x higher than Q1 baseline.
  Estimated Q4 monthly AI spend: $1,330,000
  Without per-decision cost attribution, this spike is invisible until the invoice arrives.
```

## Key Insights

### Cost Breakdown Analysis
- **Dynamic Pricing**: Highest cost per decision ($0.004450) due to GPT-4o usage
- **Catalog Enrichment**: Second highest spend due to batch processing volume
- **Search Ranking**: High volume but low per-decision cost with Gemini Flash
- **Total Sample**: $0.0234 across 25 decisions extrapolates to enterprise scale

### Right-Sizing Opportunities
1. **Dynamic Pricing GPT-4o → GPT-4o-mini**: 75% cost savings = $609K annually
2. **Catalog Enrichment**: Could evaluate Anthropic Claude Haiku for batch tasks
3. **Customer Support**: Consider switching from Claude Sonnet to Claude Haiku

### Peak Season Impact
- **Q4 Multiplier**: 4.2x higher spend during October-December
- **Monthly Peak**: $1.33M vs $317K baseline
- **Early Warning**: Per-decision tracking provides real-time cost visibility

## Operational Benefits

### For Finance Teams
- **Real-time Spend Tracking**: No waiting for monthly vendor invoices
- **Team Accountability**: Direct attribution of AI costs to business units
- **Budget Management**: Set and monitor team-level AI spending limits
- **Variance Analysis**: Understand cost drivers and seasonal patterns

### For Engineering Teams
- **Model Selection Justification**: Data-driven decisions on premium vs standard models
- **Performance vs Cost Trade-offs**: Quantify cost impact of model upgrades
- **Optimization Guidance**: Identify highest-impact cost reduction opportunities
- **Vendor Negotiation**: Detailed usage data for better contract terms

### for Leadership
- **ROI Visibility**: Connect AI spending to business outcomes
- **Strategic Planning**: Informed decisions about AI investment priorities
- **Risk Management**: Early warning system for cost overruns
- **Competitive Intelligence**: Benchmark AI spending against industry standards

## Technical Implementation

### Cost Calculation
- Uses exact vendor pricing from VENDOR_PRICING table
- Separates input and output token costs for transparency
- Handles batch processing with cost-per-decision calculation
- Validates cost computation accuracy in audit trail

### Decision Attribution
Each decision snapshot contains:
- Team and model identification
- Input/output token counts
- Calculated costs (input, output, total, per-decision)
- Timestamp for seasonal analysis
- Use case context (inference vs batch processing)

### Data Storage
- All cost calculations stored in immutable audit trail
- Retrievable for financial audits and regulatory compliance
- No external infrastructure dependencies
- Full lineage from token usage to final costs

## Integration Guidance

### Production Deployment
1. Configure vendor pricing tables with actual contract rates
2. Set up automated cost reporting dashboards
3. Integrate with existing financial systems and budgeting tools
4. Establish cost alerts and spending limits by team

### Financial Workflows
- **Daily**: Automated cost reports by team and model
- **Weekly**: Right-sizing recommendations and optimization opportunities
- **Monthly**: Vendor spend reconciliation against invoices
- **Quarterly**: Strategic cost planning and budget allocation

## Related Examples

- **[01_agent_discovery](../01_agent_discovery/)**: Identify agents contributing to costs
- **[03_peak_season_drift](../03_peak_season_drift/)**: Monitor cost impacts of model changes
- **[04_governance_report](../04_governance_report/)**: Include cost data in compliance reports

## Support

For questions about implementing cost attribution in your organization:
- Review the interactive notebook for detailed cost analysis techniques
- Check the source code for pricing calculation methodologies
- Contact your Briefcase AI representative for enterprise cost management features