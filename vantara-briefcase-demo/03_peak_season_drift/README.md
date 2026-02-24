# Peak Season Drift Detection - Vantara Commerce

## Overview

This example demonstrates how Briefcase AI solves the critical problem of model performance degradation during peak shopping seasons. During Q4 (Black Friday, Cyber Monday, holiday shopping), Vantara Commerce rapidly deploys updated AI models to handle traffic spikes. When model changes cause performance regressions mid-season, traditional troubleshooting takes 2-5 days of manual log correlation across multiple vendors.

## The Problem

### Peak Season Challenges
- **Rapid Model Deployment**: Multiple AI model updates during critical shopping periods
- **Performance Regressions**: New model versions may degrade accuracy or confidence
- **Root Cause Blindness**: No way to quickly identify which model version caused issues
- **Context Loss**: Cannot reconstruct what the model was processing during problem periods
- **Manual Investigation**: Days of manual log correlation across vendors and systems

### Business Impact
- **Revenue Loss**: Poor search ranking affects customer discovery
- **Conversion Drop**: Degraded recommendations reduce click-through rates
- **Customer Experience**: Fallback systems provide inferior user experience
- **Operational Stress**: Engineering teams scramble during peak sales periods

## The Solution

Briefcase AI captures complete model version and execution context for instant root cause analysis:

1. **Model Version Tracking**: Every decision records exact model version used
2. **Performance Monitoring**: Track confidence scores, CTR predictions, fallback rates
3. **Context Preservation**: Full input/output context available for any decision
4. **Instant Analysis**: Query by model version and timestamp for immediate insights
5. **Rollback Guidance**: Identify exact versions to rollback to

## Running the Example

### Prerequisites
- Python 3.9 or higher
- Briefcase AI SDK (falls back to mock implementation if not available)

### Basic Usage
```bash
cd 03_peak_season_drift
python example.py
```

### Interactive Analysis
```bash
jupyter notebook peak_season_drift_walkthrough.ipynb
```

## Expected Output

The example simulates two waves of model deployments:
- **Wave 1 (Nov 1-25)**: Stable pre-BFCM versions with good performance
- **Wave 2 (Nov 29-Dec 5)**: Updated BFCM versions with degraded performance

```
=== VANTARA COMMERCE — Q4 MODEL DRIFT REPORT ===
Analysis period: Nov 1 – Dec 5 (Black Friday / Cyber Monday window)

SEARCH RANKING — MODEL VERSION CHANGE DETECTED:
  Pre-BFCM  (v8.2.1-stable): mean confidence 0.883, fallback rate 0%
  Post-BFCM (v8.3.0-bfcm):   mean confidence 0.508, fallback rate 33%
  Δ confidence: -0.375 (-42% degradation)
  Root cause: model_version changed from v8.2.1-stable → v8.3.0-bfcm on Nov 28

PRODUCT RECOMMENDATIONS — MODEL VERSION CHANGE DETECTED:
  Pre-BFCM  (recs-v12.0):      mean predicted CTR 0.0731
  Post-BFCM (recs-v12.1-bfcm): mean predicted CTR 0.0309
  Δ CTR prediction: -0.0422 (-58% degradation)
  Root cause: model_version changed from recs-v12.0 → recs-v12.1-bfcm on Nov 28

WITHOUT BRIEFCASE AI:
  Time to identify root cause: 2–5 days (manual log correlation across 2 vendors)
  Evidence quality: reconstructed, not contemporaneous

WITH BRIEFCASE AI:
  Time to identify root cause: < 1 minute (query by model_version and decision_timestamp)
  Evidence quality: immutable decision traces captured at execution time
  Rollback target: v8.2.1-stable and recs-v12.0
```

## Key Insights

### Performance Degradation Analysis
- **Search Ranking**: 42% confidence degradation, 33% fallback rate increase
- **Recommendations**: 58% CTR prediction degradation
- **Root Cause**: Model version changes deployed on Nov 28
- **Resolution**: Rollback to v8.2.1-stable and recs-v12.0

### Time to Resolution
- **Traditional Method**: 2-5 days manual investigation
- **With Briefcase AI**: < 1 minute query-based analysis
- **Evidence Quality**: Immutable contemporaneous records vs reconstructed logs
- **Rollback Precision**: Exact version identification vs guesswork

### Decision Reconstruction
The example demonstrates loading specific problematic decisions with full context:
- Complete input queries and recommendation contexts
- Exact model versions and performance metrics
- Timestamps for precise temporal analysis
- Immediate availability without log aggregation

## Technical Implementation

### Model Version Capture
Each decision snapshot includes:
- **Model Version**: Exact version string (e.g., "v8.3.0-bfcm")
- **Deployment Date**: When the version was deployed
- **Performance Metrics**: Confidence scores, CTR predictions, fallback indicators
- **Input Context**: Full query or recommendation context

### Drift Detection
The system automatically identifies:
- Version changes between time periods
- Performance metric degradations
- Fallback rate increases
- Statistical significance of changes

### Root Cause Analysis
- **Immediate**: Query decisions by model version
- **Precise**: Exact timestamp correlation
- **Contextual**: Full input/output preservation
- **Actionable**: Clear rollback recommendations

## Operational Benefits

### For Engineering Teams
- **Instant Debugging**: No manual log correlation required
- **Precise Rollbacks**: Exact version identification for quick recovery
- **Context Preservation**: Full debugging context always available
- **Confidence in Deployments**: Clear performance impact visibility

### for Operations Teams
- **Proactive Monitoring**: Real-time performance degradation alerts
- **Rapid Response**: Minutes instead of days for root cause analysis
- **Deployment Validation**: Immediate feedback on model performance
- **Risk Mitigation**: Quick identification of problematic releases

### For Business Teams
- **Revenue Protection**: Rapid resolution minimizes sales impact
- **Customer Experience**: Faster restoration of optimal model performance
- **Peak Season Readiness**: Confidence in critical shopping period deployments
- **Performance Accountability**: Clear attribution of model changes to business metrics

## Peak Season Workflow

### Pre-Deployment
1. **Baseline Capture**: Record stable model performance metrics
2. **Version Tagging**: Clear model version identification
3. **Context Sampling**: Capture representative input patterns

### During Deployment
1. **Real-time Monitoring**: Track performance metrics immediately
2. **Automated Alerting**: Flag significant performance degradations
3. **Context Comparison**: Compare new decisions to historical patterns

### Post-Incident
1. **Instant Analysis**: Query by model version for immediate insights
2. **Impact Assessment**: Quantify performance and business impact
3. **Rollback Execution**: Precise version targeting for recovery
4. **Postmortem Evidence**: Complete decision history for analysis

## Integration Guidance

### Production Deployment
1. Instrument all AI models with Briefcase AI decision capture
2. Configure model version tracking in deployment pipelines
3. Set up performance degradation alerts and thresholds
4. Create dashboards for real-time model performance monitoring

### Peak Season Preparation
- **Baseline Establishment**: Capture stable performance benchmarks
- **Alerting Configuration**: Set thresholds for confidence, CTR, fallback rates
- **Response Procedures**: Define escalation and rollback processes
- **Communication Plans**: Prepare stakeholder notification workflows

## Related Examples

- **[01_agent_discovery](../01_agent_discovery/)**: Identify agents that require drift monitoring
- **[02_cost_attribution](../02_cost_attribution/)**: Track cost impacts of model version changes
- **[04_governance_report](../04_governance_report/)**: Include drift analysis in compliance reports

## Support

For questions about implementing drift detection in your organization:
- Review the interactive notebook for detailed statistical analysis
- Check the source code for model version tracking patterns
- Contact your Briefcase AI representative for enterprise drift monitoring features