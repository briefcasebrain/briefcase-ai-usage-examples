# Documentation

Comprehensive documentation for the Briefcase AI Telemetry SDK.

## 📚 Documentation Overview

This directory contains detailed guides and references for all aspects of the SDK:

### Core Documentation

- **[API Reference](api-reference.md)** - Complete API documentation for all classes and functions
- **[Examples](../examples/)** - Practical examples and code samples for all features

### Feature-Specific Guides

- **[Agent Instrumentation Guide](instrumentation-guide.md)** - Comprehensive AI agent monitoring
- **[Drift Analysis Guide](drift-analysis.md)** - Detecting and analyzing AI model drift
- **[Cost Tracking Guide](cost-tracking.md)** - AI model cost estimation and optimization
- **[Compliance Guide](compliance.md)** - Regulatory compliance (GDPR, SOC2, FSB)

## 🚀 Quick Navigation

### Getting Started
1. **Installation**: See main [README](../README.md#installation)
2. **Basic Usage**: Check [examples/basic_usage.py](../examples/basic_usage.py)
3. **AI Features**: Review [AI/ML section](../README.md#🤖-aiml-features) in main README

### By Use Case

#### 📊 Basic Telemetry
- **What**: Track events, sessions, and application performance
- **Start Here**: [Basic Usage Example](../examples/basic_usage.py)
- **API**: [TelemetryClient](api-reference.md#telemetryclient), [Event](api-reference.md#event)

#### 🤖 AI Agent Monitoring
- **What**: Monitor AI agents, reasoning steps, tool usage
- **Start Here**: [Agent Instrumentation Example](../examples/agent_instrumentation.py)
- **Guide**: [Instrumentation Guide](instrumentation-guide.md)
- **API**: [AgentInstrument](api-reference.md#agentinstrument)

#### 📈 Drift Detection
- **What**: Detect when AI models start producing inconsistent outputs
- **Start Here**: [Drift Analysis Example](../examples/drift_analysis.py)
- **Guide**: [Drift Analysis Guide](drift-analysis.md)
- **API**: [DriftCalculator](api-reference.md#driftcalculator)

#### 💰 Cost Optimization
- **What**: Track and optimize AI model usage costs
- **Start Here**: [Cost Estimation Example](../examples/cost_estimation.py)
- **Guide**: [Cost Tracking Guide](cost-tracking.md)
- **API**: [CostCalculator](api-reference.md#costcalculator)

#### ⚖️ Compliance Monitoring
- **What**: Ensure regulatory compliance (GDPR, SOC2, FSB)
- **Start Here**: [Compliance Example](../examples/compliance_checking.py)
- **Guide**: [Compliance Guide](compliance.md)
- **API**: [ComplianceFramework](api-reference.md#complianceframework)

### By Industry

#### 🏦 Financial Services
- **High Consistency Requirements**: FSB compliance with 99% model consistency
- **Deterministic Outputs**: Temperature = 0.0 for regulatory requirements
- **Cross-Model Validation**: Multi-model consensus for critical decisions
- **Example**: [Financial Model Monitor](compliance.md#fsb-financial-services-board)

#### 🏥 Healthcare
- **GDPR Compliance**: Patient data protection and consent management
- **Audit Trails**: Complete decision tracking for medical AI
- **Drift Monitoring**: Ensure consistent medical recommendations
- **Example**: [Medical AI Compliance](compliance.md#gdpr-general-data-protection-regulation)

#### 💼 SaaS/Enterprise
- **SOC 2 Compliance**: Security and operational controls
- **Cost Management**: Multi-tenant cost attribution and optimization
- **Performance Monitoring**: Agent performance across different use cases
- **Example**: [Enterprise Agent Monitoring](instrumentation-guide.md#real-world-examples)

## 📖 Learning Path

### Beginner (New to AI Telemetry)
1. Read [main README](../README.md) for overview
2. Try [Basic Usage Example](../examples/basic_usage.py)
3. Explore [AI Features](../README.md#🤖-aiml-features) in main README
4. Run [Drift Analysis Example](../examples/drift_analysis.py)

### Intermediate (Implementing AI Monitoring)
1. Study [Agent Instrumentation Guide](instrumentation-guide.md)
2. Implement basic agent monitoring with [example](../examples/agent_instrumentation.py)
3. Set up [Cost Tracking](cost-tracking.md) for budget management
4. Review [API Reference](api-reference.md) for detailed usage

### Advanced (Production Deployment)
1. Implement [Compliance Monitoring](compliance.md) for your industry
2. Set up automated [Drift Detection](drift-analysis.md#continuous-monitoring)
3. Build custom [Cost Optimization](cost-tracking.md#advanced-cost-optimization) strategies
4. Create comprehensive monitoring dashboards

## 🔍 Search by Topic

### Monitoring & Analytics
- [Event Tracking](api-reference.md#event) - Basic event collection
- [Session Management](api-reference.md#session) - User/system sessions
- [Performance Metrics](instrumentation-guide.md#performance-monitoring) - Response time, accuracy
- [Custom Metadata](instrumentation-guide.md#custom-metadata) - Context-specific data

### AI/ML Specific
- [Output Consistency](drift-analysis.md#types-of-drift) - Detect model drift
- [Multi-Step Reasoning](instrumentation-guide.md#tracking-reasoning-steps) - Track AI reasoning
- [Tool Usage](instrumentation-guide.md#tool-usage-monitoring) - Monitor external API calls
- [Consensus Analysis](instrumentation-guide.md#consensus-mode) - Multi-run agreement

### Cost & Budget
- [Model Comparison](cost-tracking.md#model-comparison) - Compare costs across models
- [Budget Planning](cost-tracking.md#monthly-budget-planning) - Project monthly expenses
- [Cost Attribution](cost-tracking.md#cost-attribution) - Track costs by user/department
- [Optimization Strategies](cost-tracking.md#advanced-cost-optimization) - Reduce AI costs

### Compliance & Security
- [GDPR Requirements](compliance.md#gdpr-general-data-protection-regulation) - European data protection
- [SOC 2 Controls](compliance.md#soc-2-service-organization-control-2) - Security controls
- [FSB Standards](compliance.md#fsb-financial-services-board) - Financial regulations
- [Data Sanitization](instrumentation-guide.md#data-sanitization) - Remove sensitive data

## 🛠️ Integration Guides

### Existing Applications
```python
# Add to existing AI application
import briefcase_ai_telemetry as bt

client = bt.create_client("your-api-key")
client.start_background_flush()

# Wrap your AI calls
def track_ai_call(model, input_text, output_text):
    # Your existing AI logic
    result = your_ai_function(input_text)

    # Add telemetry
    cost = bt.estimate_cost(model, input_text, result)
    drift_metrics = bt.calculate_drift([result])  # With historical data

    event = bt.create_event(
        "ai_call_completed",
        level=bt.EventLevel.info(),
        custom_data={
            "cost": str(cost.total_cost) if cost else "unknown",
            "consistency": str(drift_metrics.consistency_score)
        }
    )
    client.track_event(event)

    return result
```

### CI/CD Pipelines
```python
# Add to deployment pipeline
def validate_model_before_deployment():
    test_outputs = run_model_tests()
    drift_metrics = bt.calculate_drift(test_outputs)

    if drift_metrics.consistency_score < 95.0:
        raise Exception("Model consistency below deployment threshold")

    compliance = check_compliance(drift_metrics)
    if not compliance.compliant:
        raise Exception(f"Compliance check failed: {compliance.issues}")
```

### Monitoring Dashboards
```python
# Export metrics for dashboards
def export_metrics_for_dashboard():
    daily_metrics = {
        "ai_requests": get_request_count(),
        "total_cost": get_daily_cost(),
        "avg_consistency": get_avg_consistency_score(),
        "compliance_status": get_compliance_status()
    }

    # Export to your monitoring system
    send_to_dashboard(daily_metrics)
```

## 🤝 Contributing to Documentation

Found an issue or want to improve the documentation?

1. **Issues**: Report documentation issues on [GitHub Issues](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
2. **Improvements**: Submit pull requests with documentation enhancements
3. **Examples**: Share your real-world usage examples

## 📞 Support

- **Documentation Issues**: Check [GitHub Issues](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
- **General Questions**: Visit [GitHub Discussions](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/discussions)
- **API Reference**: See [API Documentation](api-reference.md)
- **Examples**: Browse [Examples Directory](../examples/)

---

## Quick Reference Card

### Import Statement
```python
import briefcase_ai_telemetry as bt
```

### Essential Functions
```python
# Basic telemetry
client = bt.create_client("api-key")
event = bt.create_event("event_name", level=bt.EventLevel.info())
client.track_event(event)

# AI monitoring
drift = bt.calculate_drift(["output1", "output2", "output3"])
cost = bt.estimate_cost("gpt-4", "input", "output")
instrument = bt.create_agent_instrument(123, client)
```

### Key Classes
- `TelemetryClient` - Main telemetry client
- `DriftCalculator` - Advanced drift analysis
- `CostCalculator` - Cost estimation and optimization
- `AgentInstrument` - AI agent monitoring
- `ComplianceFramework` - Regulatory compliance checking

---

Built with ❤️ by the [Briefcase AI](https://briefcase.ai) team.