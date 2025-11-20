# Briefcase AI Telemetry SDK

[![CI](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/workflows/CI/badge.svg)](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/actions)
[![PyPI version](https://badge.fury.io/py/briefcase-ai-telemetry-sdk.svg)](https://badge.fury.io/py/briefcase-ai-telemetry-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/briefcase-ai-telemetry-sdk.svg)](https://pypi.org/project/briefcase-ai-telemetry-sdk/)
[![License: BSL](https://img.shields.io/badge/License-BSL-blue.svg)](LICENSE)
[![Codecov](https://codecov.io/gh/briefcasebrain/briefcase-ai-telemetry-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/briefcasebrain/briefcase-ai-telemetry-sdk)

A high-performance telemetry SDK for AI applications, built with Rust and PyO3 for maximum efficiency and reliability.

## Features

- 🚀 **High Performance**: Built with Rust for maximum speed and minimal overhead
- 🔄 **Async Support**: Non-blocking telemetry collection and transmission
- 📊 **Rich Event Data**: Comprehensive event tracking with metadata, tags, and custom data
- 🛡️ **Type Safe**: Full type hints and runtime type checking
- 🔧 **Configurable**: Flexible configuration options for various deployment scenarios
- 📦 **Easy Integration**: Simple Python API with sensible defaults
- 🌐 **Multi-platform**: Supports Linux, macOS, and Windows
- 🔒 **Secure**: Built-in security best practices and data validation

### 🤖 **AI/ML Specific Features**

- 📈 **Drift Detection**: Advanced algorithms to detect AI model output drift
- 💰 **Cost Tracking**: Accurate cost estimation for various AI models (GPT, Claude, etc.)
- 🎯 **Agent Instrumentation**: Comprehensive monitoring for AI agents and workflows
- ⚖️ **Compliance Frameworks**: Built-in support for GDPR, SOC2, and FSB compliance
- 🔍 **Consensus Analysis**: Detect agreement patterns in multi-run AI outputs

## Installation

### Private Distribution

This package is distributed through private channels only. For access:

1. **Contact Sales**: Email [support@briefcasebrain.com](mailto:support@briefcasebrain.com)
2. **License Agreement**: Sign Business Source License agreement
3. **Repository Access**: Receive access to private releases
4. **Download & Install**: Install from provided wheel files

```bash
# After obtaining access, install from wheel
pip install briefcase_ai_telemetry-0.1.0-*.whl
```

### From Source (Development)

For development and testing purposes:

```bash
git clone https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk.git
cd briefcase-ai-telemetry-sdk
pip install maturin[patchelf]
maturin develop --release
```

**Note**: Source builds are subject to BSL 1.1 license terms.

## Quick Start

```python
import asyncio
from briefcase_ai_telemetry import (
    create_client, create_event, EventLevel,
    # AI/ML features
    calculate_drift, estimate_cost, create_agent_instrument
)

# Create a client with your API key
client = create_client("your-api-key-here")

# Start background flushing
client.start_background_flush()

# Track an event
event = create_event(
    name="user_action",
    level=EventLevel.info(),
    message="User performed an action",
    user_id="user123",
    tags={"component": "auth", "action_type": "login"},
    custom_data={"session_duration": 120, "user_agent": "Mozilla/5.0..."}
)

client.track_event(event)

# Manually flush if needed
client.flush()
```

## Configuration

```python
from briefcase_ai_telemetry import TelemetryConfig, TelemetryClient

config = TelemetryConfig("your-api-key")
# Default endpoint: https://your-telemetry-endpoint.com/api/trpc/ingest.telemetry
config.with_endpoint("https://custom.endpoint.com/api/trpc/ingest.telemetry")
config.with_timeout_seconds(30)
config.with_batch_size(50)
config.with_flush_interval_seconds(10)
config.with_retry_attempts(5)

client = TelemetryClient(config)
```

## Event Levels

The SDK supports five event levels:

- `EventLevel.debug()` - Detailed information for debugging
- `EventLevel.info()` - General information about application flow
- `EventLevel.warning()` - Something unexpected happened, but the application can continue
- `EventLevel.error()` - A serious problem occurred
- `EventLevel.critical()` - A very serious error occurred

## Advanced Usage

### Custom Sessions

```python
from briefcase_ai_telemetry import Session, create_client

# Create a custom session
session = Session().with_user_id("user123")
session = session.add_metadata("app_version", "1.0.0")
session = session.add_metadata("platform", "web")

# Use the session with your client
client = create_client("your-api-key")
client.with_session(session)
```

### Error Tracking

```python
from briefcase_ai_telemetry import EventBuilder, EventLevel

try:
    # Your application code
    risky_operation()
except Exception as e:
    error_event = (
        EventBuilder("operation_failed")
        .level(EventLevel.error())
        .error(str(e))
        .tag("operation", "risky_operation")
        .custom_data("stack_trace", traceback.format_exc())
        .build()
    )
    client.track_event(error_event)
```

### Performance Monitoring

```python
import time
from briefcase_ai_telemetry import EventBuilder, EventLevel

start_time = time.time()

# Your operation
perform_computation()

duration_ms = int((time.time() - start_time) * 1000)

perf_event = (
    EventBuilder("computation_completed")
    .level(EventLevel.info())
    .duration_ms(duration_ms)
    .tag("operation_type", "ml_inference")
    .custom_data("input_size", len(input_data))
    .build()
)

client.track_event(perf_event)
```

## 🤖 AI/ML Features

### Drift Detection

Detect when your AI models start producing inconsistent outputs:

```python
from briefcase_ai_telemetry import calculate_drift, DriftCalculator

# Simple drift detection
outputs = [
    "The capital of France is Paris.",
    "France's capital city is Paris.",
    "Paris is the capital of France."
]

metrics = calculate_drift(outputs)
print(f"Agreement rate: {metrics.total_agreement_rate:.1f}%")
print(f"Consensus confidence: {metrics.consensus_confidence}")

# Advanced drift analysis
calculator = DriftCalculator()
enhanced_metrics = calculator.calculate_enhanced_metrics(
    outputs,
    context="Geography question about France"
)
print(f"Ensemble drift score: {enhanced_metrics.ensemble_score:.3f}")
```

### Cost Estimation

Track AI model usage costs accurately:

```python
from briefcase_ai_telemetry import estimate_cost, CostCalculator

# Simple cost estimation
cost = estimate_cost(
    model_name="gpt-4",
    input_text="What is the capital of France?",
    output_text="The capital of France is Paris."
)

if cost:
    print(f"Estimated cost: ${cost.total_cost:.6f}")
    print(f"Input tokens: {cost.input_tokens}")
    print(f"Output tokens: {cost.output_tokens}")

# Advanced cost analysis
calculator = CostCalculator()
models_under_budget = calculator.get_models_under_cost(0.01)  # Under 1 cent
print(f"Budget-friendly models: {[m.name for m in models_under_budget]}")
```

### Agent Instrumentation

Monitor AI agents and multi-step workflows:

```python
from briefcase_ai_telemetry import create_agent_instrument, InstrumentationConfig, create_client

# Setup instrumentation
client = create_client("your-api-key")
config = InstrumentationConfig()
config.with_consensus_mode(True, runs=3, threshold=0.8)

instrument = create_agent_instrument(
    agent_id=123,
    client=client,
    config=config
)

# Start monitoring
session = instrument.start()
session.set_input_output(
    input="Analyze this data",
    output="Analysis complete: found 5 anomalies"
)
session.set_model_info("gpt-4", temperature=0.1)
session.add_reasoning_step("Identified data patterns")
session.add_tool_call("data_analyzer", {"method": "anomaly_detection"})

# Finish and report
instrument.finish()
```

### Compliance Checking

Ensure your AI systems meet regulatory requirements:

```python
from briefcase_ai_telemetry import DriftCalculator, ComplianceFramework

calculator = DriftCalculator()

# Check GDPR compliance
gdpr_check = calculator.check_compliance(
    consistency_score=95.0,
    temperature=0.0,
    has_audit_trail=True,
    framework=ComplianceFramework.Gdpr
)

print(f"GDPR Compliant: {gdpr_check.compliant}")
print(f"Compliance Score: {gdpr_check.score:.1f}%")

# Check SOC2 compliance
soc2_check = calculator.check_compliance(
    consistency_score=97.0,
    temperature=0.0,
    has_audit_trail=True,
    framework=ComplianceFramework.Soc2
)

if not soc2_check.compliant:
    print(f"Issues: {soc2_check.issues}")
```

## Development

### Prerequisites

- Rust 1.70+
- Python 3.8+
- [Just](https://github.com/casey/just) (recommended for task running)

### Setup

```bash
# Clone the repository
git clone https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk.git
cd briefcase-ai-telemetry-sdk

# Set up development environment
just setup

# Or manually:
pip install maturin[patchelf]
maturin develop
pip install -e .[dev]
```

### Common Development Tasks

```bash
# Run all tests
just test

# Format code
just fmt

# Lint code
just lint

# Build for release
just build

# Run security audit
just audit

# Clean build artifacts
just clean
```

### Running Tests

```bash
# Run Rust tests
just test-rust
# or: cargo test

# Run Python tests
just test-python
# or: python -m pytest python/tests/

# Run with coverage
just test-coverage
```

## Architecture

The Briefcase AI Telemetry SDK is built with a hybrid Rust-Python architecture:

- **Rust Core**: High-performance event processing, HTTP client, and data serialization
- **Python Bindings**: PyO3-based bindings providing a Pythonic API
- **Async Runtime**: Tokio-based async runtime for non-blocking operations
- **Type Safety**: Comprehensive type checking in both Rust and Python layers

## Performance

The SDK is designed for high-throughput scenarios:

- **Batching**: Automatic event batching to reduce network overhead
- **Background Processing**: Non-blocking event transmission
- **Efficient Serialization**: Fast JSON serialization with serde
- **Connection Pooling**: Reuses HTTP connections for better performance
- **Memory Efficient**: Minimal memory allocations and fast cleanup

## Security

- All network communication uses HTTPS
- API keys are securely handled and never logged
- Input validation prevents injection attacks
- No sensitive data is collected by default
- Configurable data retention policies

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the Business Source License 1.1 - see the [LICENSE](LICENSE) file for details.

### What does this mean?

- ✅ **Free to use** for development, testing, and internal business purposes
- ✅ **Free to modify** and create derivative works
- ✅ **Free to redistribute** (with license intact)
- ❌ **Cannot offer as a service** - You may not use this software to provide telemetry, observability, monitoring, or analytics services to third parties
- 🕐 **Becomes open source** - Automatically becomes Apache 2.0 licensed on November 19, 2029

For commercial licensing to offer this as a service, please contact [support@briefcasebrain.com](mailto:support@briefcasebrain.com).

## Support

- 📚 [Documentation](https://docs.briefcase.ai/telemetry-sdk)
- 🐛 [Issue Tracker](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
- 💬 [Discussions](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/discussions)
- 📧 [Email Support](mailto:support@briefcasebrain.com)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed changelog.

---

Built with ❤️ by the [Briefcase AI](https://briefcasebrain.com) team.