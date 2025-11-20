# AI Agent Instrumentation Guide

Comprehensive guide to monitoring AI agents and workflows using the Briefcase AI Telemetry SDK.

## Overview

Agent instrumentation provides detailed monitoring and analytics for AI agents, workflows, and multi-step reasoning processes. This enables you to:

- Track agent performance and accuracy over time
- Monitor reasoning steps and decision-making processes
- Detect drift in agent outputs
- Implement consensus mechanisms for reliability
- Ensure compliance with regulatory requirements
- Optimize costs and resource usage

## Quick Start

### Basic Setup

```python
from briefcase_ai_telemetry import (
    create_client, create_agent_instrument,
    InstrumentationConfig
)

# Create client
client = create_client("your-api-key")

# Create agent instrument
instrument = create_agent_instrument(
    agent_id=12345,  # Unique identifier for your agent
    client=client
)

# Start a session
session = instrument.start()

# Set basic information
session.set_input_output(
    input="What is the capital of France?",
    output="The capital of France is Paris."
)

session.set_model_info("gpt-4", temperature=0.1)
session.set_accuracy(1.0)  # Perfect answer

# Finish session
session.finish()
```

### Advanced Configuration

```python
# Create configuration
config = InstrumentationConfig()
config.with_consensus_mode(True, runs=3, threshold=0.8)
config.with_sensitive_data_sanitization(True)

# Create instrument with configuration
instrument = create_agent_instrument(
    agent_id=12345,
    client=client,
    config=config
)
```

## Core Concepts

### Agent Sessions

Each agent execution creates a **session** that tracks:
- Input and output data
- Model information and parameters
- Reasoning steps and tool calls
- Performance metrics and costs
- Metadata and custom attributes

### Session Lifecycle

1. **Start**: Create a new session with `instrument.start()`
2. **Configure**: Set input, output, model info, etc.
3. **Track**: Add reasoning steps, tool calls, metadata
4. **Finish**: Complete the session with `session.finish()`

### Performance Metrics

- **Accuracy**: How correct the agent's output is (0.0-1.0)
- **Cost**: Execution cost in USD
- **Token Usage**: Input and output token counts
- **Timing**: Session start/end times and duration
- **Error Rate**: Percentage of failed executions

## Detailed Usage

### Setting Input and Output

```python
session.set_input_output(
    input="Analyze this customer data and provide insights",
    output="""Customer Analysis:
    - High-value customer (LTV: $15,000)
    - Risk level: Low
    - Recommended actions: Upsell premium services
    - Predicted churn probability: 5%"""
)
```

### Model Information

```python
session.set_model_info("gpt-4", temperature=0.2)
session.set_token_usage(input_tokens=150, output_tokens=89)
session.set_cost(0.0234)  # Cost in USD
```

### Tracking Reasoning Steps

For complex agents that perform multi-step reasoning:

```python
# Mathematical problem solving
session.add_reasoning_step("Identified the problem as a quadratic equation")
session.add_reasoning_step("Applied quadratic formula: x = (-b ± √(b²-4ac))/2a")
session.add_reasoning_step("Calculated discriminant: b²-4ac = 25")
session.add_reasoning_step("Found two solutions: x = 3 and x = -2")
session.add_reasoning_step("Verified solutions by substitution")
```

### Tool Usage Monitoring

Track when your agent uses external tools:

```python
# Weather API call
session.add_tool_call("weather_api", {
    "location": "New York, NY",
    "date": "2024-01-15",
    "units": "fahrenheit"
})

# Database query
session.add_tool_call("customer_database", {
    "query": "SELECT * FROM customers WHERE id = ?",
    "parameters": ["12345"]
})

# Calculator usage
session.add_tool_call("calculator", {
    "operation": "multiply",
    "operands": [157, 23]
})
```

### Custom Metadata

Add context-specific information:

```python
session.set_metadata("task_type", "financial_analysis")
session.set_metadata("complexity", "high")
session.set_metadata("domain", "healthcare")
session.set_metadata("user_role", "admin")
session.set_metadata("request_source", "mobile_app")
```

### Error Handling

Track and analyze failures:

```python
try:
    # Agent execution
    result = agent.process(input_data)
    session.set_accuracy(0.95)
except Exception as e:
    session.set_error(str(e))
    session.set_accuracy(0.0)  # Failed execution
    session.set_metadata("error_type", type(e).__name__)
```

## Advanced Features

### Consensus Mode

Run multiple instances of your agent and compare outputs:

```python
config = InstrumentationConfig()
config.with_consensus_mode(
    enabled=True,
    runs=5,           # Run agent 5 times
    threshold=0.8     # 80% agreement required
)

instrument = create_agent_instrument(123, client, config)

# Each session represents one run
for i in range(5):
    session = instrument.start()
    session.set_input_output(
        input="Diagnose this medical case",
        output=f"Diagnosis from run {i+1}: Acute bronchitis"
    )
    session.set_accuracy(calculate_accuracy(expected, actual))
    session.finish()

# SDK automatically calculates consensus metrics
```

### Data Sanitization

Automatically remove sensitive information:

```python
config = InstrumentationConfig()
config.with_sensitive_data_sanitization(True)

# The following data will be automatically sanitized:
session.set_input_output(
    input="Process payment for John Smith, card 4532-1234-5678-9012",
    output="Payment processed for customer J***n S***h"
)
# Credit card numbers, SSNs, emails, etc. are automatically redacted
```

### Input/Output Truncation

Manage large inputs and outputs:

```python
config = InstrumentationConfig()
config.with_input_output_truncation(
    enabled=True,
    max_input_length=1000,   # Truncate input after 1000 chars
    max_output_length=2000   # Truncate output after 2000 chars
)
```

## Multi-Agent Systems

### Agent Hierarchies

Track parent-child relationships between agents:

```python
# Parent agent
parent_instrument = create_agent_instrument(100, client)
parent_session = parent_instrument.start()

# Child agents
child1_instrument = create_agent_instrument(101, client)
child2_instrument = create_agent_instrument(102, client)

# Set relationships via metadata
child1_session = child1_instrument.start()
child1_session.set_metadata("parent_agent_id", "100")
child1_session.set_metadata("agent_role", "data_analyzer")

child2_session = child2_instrument.start()
child2_session.set_metadata("parent_agent_id", "100")
child2_session.set_metadata("agent_role", "result_synthesizer")
```

### Agent Workflows

Track complex workflows:

```python
workflow_steps = [
    {"agent_id": 201, "role": "data_collector", "input": "Gather customer data"},
    {"agent_id": 202, "role": "analyzer", "input": "Analyze collected data"},
    {"agent_id": 203, "role": "reporter", "input": "Generate final report"}
]

workflow_id = "workflow_12345"

for step in workflow_steps:
    instrument = create_agent_instrument(step["agent_id"], client)
    session = instrument.start()
    session.set_metadata("workflow_id", workflow_id)
    session.set_metadata("step_role", step["role"])
    # ... configure session
    session.finish()
```

## Performance Monitoring

### Key Performance Indicators (KPIs)

Track essential metrics:

```python
def track_agent_kpis(session, result, expected, cost, duration):
    # Accuracy
    accuracy = calculate_similarity(result, expected)
    session.set_accuracy(accuracy)

    # Cost efficiency
    session.set_cost(cost)
    session.set_metadata("cost_per_accuracy", str(cost / accuracy))

    # Response time
    session.set_metadata("duration_ms", str(int(duration * 1000)))

    # Quality score (custom metric)
    quality = assess_output_quality(result)
    session.set_metadata("quality_score", str(quality))
```

### Trend Analysis

Monitor performance over time:

```python
# Daily performance tracking
import datetime

session.set_metadata("date", datetime.date.today().isoformat())
session.set_metadata("week", str(datetime.date.today().isocalendar()[1]))
session.set_metadata("month", str(datetime.date.today().month))
```

### A/B Testing

Compare different agent configurations:

```python
# Version A: Conservative settings
config_a = InstrumentationConfig()
instrument_a = create_agent_instrument(301, client, config_a)

session_a = instrument_a.start()
session_a.set_metadata("experiment", "conservative_agent")
session_a.set_metadata("version", "A")
session_a.set_model_info("gpt-4", temperature=0.1)

# Version B: Creative settings
session_b = instrument_a.start()
session_b.set_metadata("experiment", "creative_agent")
session_b.set_metadata("version", "B")
session_b.set_model_info("gpt-4", temperature=0.8)
```

## Real-World Examples

### Customer Support Agent

```python
class CustomerSupportAgent:
    def __init__(self, client):
        self.instrument = create_agent_instrument(
            agent_id=1001,
            client=client
        )

    def handle_inquiry(self, customer_input, customer_id):
        session = self.instrument.start()

        try:
            # Set context
            session.set_input_output(
                input=customer_input,
                output=""  # Will be set later
            )
            session.set_metadata("customer_id", customer_id)
            session.set_metadata("inquiry_type", "support")

            # Process inquiry
            session.add_reasoning_step("Analyzing customer inquiry")
            intent = self.classify_intent(customer_input)
            session.add_reasoning_step(f"Classified intent: {intent}")

            # Look up information
            session.add_tool_call("knowledge_base", {"query": intent})
            knowledge = self.query_knowledge_base(intent)

            # Generate response
            response = self.generate_response(customer_input, knowledge)
            session.set_input_output(customer_input, response)

            # Assess quality
            confidence = self.assess_confidence(response)
            session.set_accuracy(confidence)
            session.set_metadata("confidence_score", str(confidence))

            return response

        except Exception as e:
            session.set_error(str(e))
            session.set_accuracy(0.0)
            raise
        finally:
            session.finish()
```

### Financial Analysis Agent

```python
class FinancialAnalysisAgent:
    def __init__(self, client):
        # High compliance requirements
        config = InstrumentationConfig()
        config.with_sensitive_data_sanitization(True)
        config.with_consensus_mode(True, runs=3, threshold=0.9)

        self.instrument = create_agent_instrument(
            agent_id=2001,
            client=client,
            config=config
        )

    def analyze_portfolio(self, portfolio_data):
        session = self.instrument.start()

        # Set high-level metadata
        session.set_metadata("analysis_type", "portfolio")
        session.set_metadata("compliance_level", "high")
        session.set_metadata("regulation", "FSB")

        # Multi-step analysis
        session.add_reasoning_step("Loading portfolio data")
        session.add_reasoning_step("Calculating risk metrics")

        # Tool usage
        session.add_tool_call("risk_calculator", {
            "portfolio_size": str(len(portfolio_data)),
            "calculation_type": "var_95"
        })

        # Generate analysis
        analysis = self.perform_analysis(portfolio_data)
        session.set_input_output(
            input=f"Portfolio analysis request ({len(portfolio_data)} assets)",
            output=analysis
        )

        # Compliance and accuracy
        session.set_accuracy(0.98)  # High confidence in financial calculations
        session.set_cost(0.045)     # Track analysis costs

        session.finish()
        return analysis
```

## Best Practices

### 1. Consistent Agent IDs
Use meaningful, consistent agent identifiers:

```python
# Good: Descriptive IDs
CUSTOMER_SUPPORT_AGENT = 1001
FINANCIAL_ANALYZER = 2001
CONTENT_GENERATOR = 3001

# Bad: Random or unclear IDs
agent_id = 12345  # What does this agent do?
```

### 2. Meaningful Metadata
Add context that helps with analysis:

```python
# Good: Rich context
session.set_metadata("customer_segment", "premium")
session.set_metadata("inquiry_complexity", "high")
session.set_metadata("language", "en")
session.set_metadata("channel", "mobile_app")

# Less useful: Minimal context
session.set_metadata("type", "request")
```

### 3. Accurate Accuracy Scoring
Implement consistent accuracy assessment:

```python
def calculate_accuracy(expected, actual, task_type):
    if task_type == "classification":
        return 1.0 if expected == actual else 0.0
    elif task_type == "generation":
        return semantic_similarity(expected, actual)
    elif task_type == "numerical":
        return 1.0 - abs(expected - actual) / expected
    # ... other task types
```

### 4. Error Categorization
Classify errors for better debugging:

```python
try:
    result = agent.execute()
except ValidationError as e:
    session.set_error(str(e))
    session.set_metadata("error_category", "validation")
except TimeoutError as e:
    session.set_error(str(e))
    session.set_metadata("error_category", "timeout")
except Exception as e:
    session.set_error(str(e))
    session.set_metadata("error_category", "unknown")
```

### 5. Cost Tracking
Monitor and optimize costs:

```python
# Track cost components
session.set_cost(total_cost)
session.set_metadata("model_cost", str(model_cost))
session.set_metadata("api_cost", str(api_cost))
session.set_metadata("compute_cost", str(compute_cost))

# Cost per unit metrics
session.set_metadata("cost_per_token", str(cost / tokens))
session.set_metadata("cost_per_second", str(cost / duration))
```

## Troubleshooting

### Common Issues

#### 1. Session Not Finishing
```python
# Always finish sessions, even on error
session = instrument.start()
try:
    # ... agent execution
    pass
finally:
    session.finish()  # Ensures proper cleanup
```

#### 2. Memory Usage with Large Outputs
```python
# Use truncation for large outputs
config = InstrumentationConfig()
config.with_input_output_truncation(True, 1000, 2000)
```

#### 3. Sensitive Data Leakage
```python
# Enable automatic sanitization
config.with_sensitive_data_sanitization(True)

# Or manually sanitize
safe_output = sanitize_sensitive_data(raw_output)
session.set_input_output(input_text, safe_output)
```

### Performance Considerations

1. **Batch Sessions**: Process multiple agent executions before flushing
2. **Async Processing**: Use background flushing to avoid blocking
3. **Sampling**: For high-volume agents, consider sampling a percentage of executions
4. **Metadata Size**: Keep metadata values concise to reduce overhead

### Monitoring Recommendations

1. **Set up Alerts**: Monitor accuracy drops, error rate increases
2. **Regular Reviews**: Weekly analysis of agent performance trends
3. **Cost Optimization**: Monthly cost analysis and model comparison
4. **Compliance Checks**: Automated compliance verification for regulated environments

---

This guide covers the essential aspects of AI agent instrumentation. For additional examples, see the [examples directory](../examples/) and [API reference](api-reference.md).