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

1. **Per-Decision Costing**: Every AI decision is priced through the SDK `CostCalculator` (input/output token costs)
2. **Team Attribution**: Aggregate individual decisions to team-level spend
3. **Model Comparison**: Compare actual costs across different model choices
4. **Peak Season Tracking**: Real-time visibility into seasonal cost multipliers
5. **Right-Sizing Analysis**: Identify opportunities to switch to cheaper models
6. **Rate-Card Tiers** *(v3.2.1)*: Re-price batch-eligible workloads on the `batch` tier (≈50% cheaper) and discover available pricing schemes via `get_available_rate_cards()`

## Running the Example

### Prerequisites
- Python 3.9 or higher
- Briefcase AI SDK v3.2.1+ (`pip install briefcase-ai`) — required; the demo exits if it is not installed

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

The example analyzes 25 decisions across 10 teams. Costs are computed by the SDK
`CostCalculator` and the run is seeded, so the numbers are reproducible:

```
=== VANTARA COMMERCE — AI SPEND ATTRIBUTION (LAST 30 DAYS) ===
Generated: 2026-05-30 23:50:08
Per-decision cost via SDK CostCalculator (briefcase.cost)

TOTAL SPEND (SAMPLE): $0.1740 across 25 decisions
ESTIMATED MONTHLY SPEND (FLEET-WIDE): $316,667  # $3.8M / 12

BY TEAM (sorted by spend descending):
  catalog-enrichment                    3 decisions     13,324 tokens  $  0.090980  [openai/gpt-4o]
  demand-forecasting                    2 decisions     12,227 tokens  $  0.024640  [google-vertex/gemini-1.5-pro]
  customer-support-ai                   2 decisions      4,210 tokens  $  0.022686  [anthropic/claude-3-5-sonnet]
  supplier-risk                         2 decisions      6,570 tokens  $  0.012701  [google-vertex/gemini-1.5-pro]
  dynamic-pricing                       2 decisions      1,872 tokens  $  0.012680  [openai/gpt-4o]
  ...

HIGHEST COST PER DECISION:
  catalog-enrichment / gpt-4o: $0.030327 per decision
  At 50,000 daily decisions → $1,516.33/day → $553,462/year

MODEL RIGHT-SIZING OPPORTUNITY:
  catalog-enrichment is using gpt-4o at $0.030327/decision
  Switching to gpt-4o-mini saves 97% per decision (same SDK pricing)
  At estimated volume → saves $534,091/year

PEAK SEASON ALERT (Q4 — Oct/Nov/Dec):
  Vantara's Q4 AI spend runs 4.2x higher than Q1 baseline.
  Estimated Q4 monthly AI spend: $1,330,000
  Without per-decision cost attribution, this spike is invisible until the invoice arrives.

=== RATE CARDS (v3.2.1) — PRICING TIER OPTIMIZATION ===
  Available rate cards (15): standard, batch, cached, priority, flex, first_party:fast,
  first_party:standard,us, bedrock:standard, bedrock:batch, bedrock:standard,regional,
  vertex:standard, vertex:batch, vertex:standard,regional, azure:standard, azure:standard,regional

  catalog-enrichment / gpt-4o (3,326 in / 1,470 out tokens):
    standard tier: $0.038680/decision
    batch tier:    $0.019340/decision  (50% cheaper)
```

## Key Insights

### Cost Breakdown Analysis
- **Catalog Enrichment**: Highest spend — GPT-4o on large batch-processing payloads
- **Demand Forecasting / Customer Support**: Next tier — large-context Gemini Pro and Claude Sonnet calls
- **Search Ranking**: High volume but low per-decision cost with Gemini Flash
- **Total Sample**: $0.1740 across 25 decisions extrapolates to enterprise scale

### Right-Sizing Opportunities
1. **Catalog Enrichment GPT-4o → GPT-4o-mini**: ~97% cost savings on the same workload
2. **Catalog Enrichment batch tier**: nightly/offline work re-priced on the `batch` rate card is ~50% cheaper with no latency cost
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
- Pricing comes from the SDK `CostCalculator` (`briefcase.cost`) — the single source of truth, with the latest provider pricing built in
- `rate_card` selects a `platform × tier × modifier` pricing scheme (e.g. `batch`, `bedrock:standard,regional`); call `available_rate_cards()` to list them
- The local `VENDOR_PRICING` table is only an offline fallback for models the SDK does not price (e.g. Cohere, legacy Gemini 1.5)
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