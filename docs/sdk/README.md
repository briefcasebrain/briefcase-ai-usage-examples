# Briefcase AI Telemetry SDK Documentation

Welcome to the Briefcase AI Telemetry SDK documentation! This directory contains comprehensive guides for installing, using, and contributing to the SDK.

## Documentation Overview

### 📦 [Installation](installation.md)
Complete installation guide covering:
- Installing from PyPI (Python users)
- Installing from npm (JavaScript/Node.js users)
- Installing from Cargo (Rust users)
- System requirements and dependencies
- Verification steps

### 🛠️ [Development Setup](development.md)
Development environment setup for contributors:
- Setting up Rust development environment
- Building Python bindings with PyO3
- Running tests and benchmarks
- Code style and contribution guidelines
- Local development workflow

### 🚀 [Publishing Workflow](publishing.md)
SDK publishing and distribution process:
- Automated PyPI publishing via GitHub Actions
- npm package publishing workflow
- Cargo crate publishing
- Version management and release process
- Quality gates and validation

### 📋 [Usage Examples](examples.md)
Practical examples demonstrating SDK usage:
- Basic telemetry tracking
- Agent instrumentation
- Cost estimation
- Drift detection
- Compliance monitoring
- Integration patterns

### 🔧 [API Reference](api-reference.md)
Complete API documentation:
- Core telemetry APIs
- Instrumentation interfaces
- Configuration options
- Error handling
- Advanced usage patterns

## Quick Start

### For Python Developers
```bash
# Install the SDK
pip install briefcase-ai-telemetry

# Basic usage
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig

config = TelemetryConfig("your-api-key")
client = TelemetryClient(config)
```

### For Rust Developers
```toml
# Add to Cargo.toml
[dependencies]
briefcase-ai-telemetry = "0.1.0"
```

```rust
// Basic usage
use briefcase_ai_telemetry::{TelemetryClient, TelemetryConfig};

let config = TelemetryConfig::new("your-api-key".to_string());
let client = TelemetryClient::new(config)?;
```

### For JavaScript/Node.js Developers
```bash
# Install the SDK
npm install briefcase-ai-telemetry

# Basic usage
const { TelemetryClient, TelemetryConfig } = require('briefcase-ai-telemetry');

const config = new TelemetryConfig('your-api-key');
const client = new TelemetryClient(config);
```

## SDK Features

### Core Capabilities
- **Multi-language Support**: Native APIs for Python, Rust, and JavaScript
- **Real-time Telemetry**: Efficient event collection and transmission
- **Agent Instrumentation**: Comprehensive AI agent monitoring
- **Cost Tracking**: Multi-provider cost estimation and optimization
- **Drift Detection**: Advanced output consistency monitoring
- **Compliance Monitoring**: Support for GDPR, SOC 2, HIPAA, and financial regulations

### Performance
- **Low Overhead**: Minimal impact on application performance
- **Async Processing**: Non-blocking telemetry collection
- **Batching**: Efficient data transmission with configurable batch sizes
- **Retry Logic**: Robust error handling and recovery
- **Privacy Protection**: Built-in data sanitization and PII detection

## Architecture

The SDK is built with a Rust core and provides bindings for multiple languages:

```
┌─────────────────────────────────────────────┐
│                 Language Bindings           │
├─────────────┬─────────────┬─────────────────┤
│   Python    │ JavaScript  │      CLI        │
│   (PyO3)    │  (NAPI-RS)  │   (Native)      │
└─────────────┴─────────────┴─────────────────┘
┌─────────────────────────────────────────────┐
│              Rust Core                      │
│  • Telemetry Client                         │
│  • Event Processing                         │
│  • Cost Calculation                         │
│  • Drift Detection                          │
│  • Compliance Monitoring                    │
│  • Data Sanitization                        │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│              Briefcase AI API               │
│         https://api.briefcase.ai            │
└─────────────────────────────────────────────┘
```

## Getting Help

### Community Support
- **GitHub Issues**: [Report bugs and request features](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
- **Discussions**: [Community Q&A and discussions](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/discussions)
- **Documentation**: [Complete API documentation](api-reference.md)

### Professional Support
- **Enterprise Support**: Custom integration assistance
- **Consulting**: Architecture review and optimization
- **Training**: Team workshops and best practices
- **Contact**: [support@briefcase.ai](mailto:support@briefcase.ai)

## Contributing

We welcome contributions! Please see our [development guide](development.md) for:
- Setting up your development environment
- Code style guidelines
- Testing requirements
- Pull request process
- Release workflow

## License

This SDK is licensed under [MIT License](../../LICENSE). See the license file for details.

---

**Ready to get started?** Begin with the [Installation Guide](installation.md) or explore our [Usage Examples](examples.md).