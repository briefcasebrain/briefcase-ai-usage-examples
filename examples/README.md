# Briefcase AI Telemetry SDK Examples

This directory contains comprehensive examples demonstrating all features of the Briefcase AI Telemetry SDK.

## 📁 Example Files

### Core Telemetry

#### `basic_usage.py`
Demonstrates fundamental telemetry functionality:
- Client setup and configuration
- Event creation and tracking
- Session management
- Error handling and performance monitoring

```bash
python examples/basic_usage.py
```

### AI/ML Specific Features

#### `drift_analysis.py`
Shows AI model drift detection capabilities:
- Basic drift calculation between outputs
- Enhanced drift metrics with semantic analysis
- Temperature sensitivity analysis
- Real-time drift monitoring workflows
- Edge case handling

```bash
python examples/drift_analysis.py
```

#### `cost_estimation.py`
Demonstrates AI model cost tracking:
- Cost estimation for popular models (GPT, Claude, etc.)
- Token counting and pricing analysis
- Model comparison for budget optimization
- Monthly cost projections
- Custom model pricing integration

```bash
python examples/cost_estimation.py
```

#### `agent_instrumentation.py`
Comprehensive AI agent monitoring:
- Agent session tracking and timing
- Multi-step reasoning capture
- Tool usage monitoring
- Consensus mode for reliability
- Performance and accuracy tracking
- Sensitive data sanitization

```bash
python examples/agent_instrumentation.py
```

#### `compliance_checking.py`
Regulatory compliance verification:
- GDPR compliance assessment
- SOC2 compliance checking
- FSB (Financial Services Board) compliance
- Custom compliance frameworks
- Automated compliance monitoring workflows

```bash
python examples/compliance_checking.py
```

## 🚀 Getting Started

### Prerequisites

Ensure you have the Briefcase AI Telemetry SDK installed:

```bash
pip install briefcase-ai-telemetry-sdk
```

### Running Examples

1. **Individual Examples**: Run any example file directly:
   ```bash
   python examples/basic_usage.py
   ```

2. **All Examples**: Run all examples in sequence:
   ```bash
   python -c "
   import subprocess
   import sys

   examples = [
       'examples/basic_usage.py',
       'examples/drift_analysis.py',
       'examples/cost_estimation.py',
       'examples/agent_instrumentation.py',
       'examples/compliance_checking.py'
   ]

   for example in examples:
       print(f'\n{'='*60}')
       print(f'Running {example}')
       print(f'{'='*60}')
       subprocess.run([sys.executable, example])
   "
   ```

### Configuration Notes

- **API Key**: Examples use `"demo-api-key"` with `enabled=False` for demonstration
- **Production Usage**: Set `enabled=True` and provide your real API key
- **Network**: Examples run offline and don't make actual API calls

## 📊 Example Scenarios

### Basic Telemetry Scenarios
- User authentication events
- Application performance monitoring
- Error tracking and debugging
- Custom event creation

### AI/ML Monitoring Scenarios
- **Drift Detection**: Monitor model consistency over time
- **Cost Optimization**: Compare model costs for budget planning
- **Agent Monitoring**: Track complex AI agent workflows
- **Compliance**: Ensure regulatory requirement compliance

### Real-World Use Cases

#### 1. **Customer Support Chatbot**
```python
# Monitor chatbot performance and costs
from examples.agent_instrumentation import *
from examples.cost_estimation import *

# Track session, reasoning steps, and costs
# Detect when responses start drifting from expected patterns
```

#### 2. **Financial AI System**
```python
# Ensure regulatory compliance
from examples.compliance_checking import *

# Verify FSB compliance for financial predictions
# Monitor consistency requirements
```

#### 3. **Content Generation Pipeline**
```python
# Optimize costs and monitor quality
from examples.drift_analysis import *
from examples.cost_estimation import *

# Compare model costs vs quality
# Detect when outputs become inconsistent
```

## 🔧 Customization

### Modifying Examples

Each example is self-contained and can be easily modified:

```python
# Change API key and enable real telemetry
client = create_client("your-real-api-key", enabled=True)

# Modify model parameters
session.set_model_info("gpt-4", temperature=0.2)

# Add custom metadata
session.set_metadata("your_custom_field", "custom_value")
```

### Adding Custom Examples

To create your own example:

1. Import required modules:
   ```python
   from briefcase_ai_telemetry import (
       create_client, calculate_drift, estimate_cost
   )
   ```

2. Create client and configure:
   ```python
   client = create_client("your-api-key")
   ```

3. Use SDK features as needed
4. Add proper error handling
5. Include helpful print statements

## 📚 Advanced Features

### Consensus Mode
```python
config = InstrumentationConfig()
config.with_consensus_mode(True, runs=3, threshold=0.8)
```

### Data Sanitization
```python
config.with_sensitive_data_sanitization(True)
```

### Custom Compliance
```python
# Implement custom compliance checks
# See compliance_checking.py for examples
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the SDK is properly installed
   ```bash
   pip install --upgrade briefcase-ai-telemetry-sdk
   ```

2. **Module Not Found**: Run examples from the project root:
   ```bash
   cd /path/to/briefcase-ai-telemetry-sdk
   python examples/basic_usage.py
   ```

3. **API Key Issues**: For testing, use `enabled=False`

### Getting Help

- 📚 [Documentation](../README.md)
- 🐛 [Issue Tracker](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
- 💬 [Discussions](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/discussions)

## 🎯 Next Steps

After running the examples:

1. **Integrate into your application**: Start with `basic_usage.py` patterns
2. **Configure for production**: Set up real API keys and endpoints
3. **Monitor AI systems**: Use drift detection and cost tracking
4. **Ensure compliance**: Implement appropriate compliance frameworks
5. **Optimize performance**: Use insights from telemetry data

---

Built with ❤️ using the [Briefcase AI Telemetry SDK](../README.md)