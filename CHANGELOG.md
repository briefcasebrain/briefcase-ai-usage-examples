# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-11-18

### Added
- Initial release of Briefcase AI Telemetry SDK
- High-performance Rust core with Python bindings
- Comprehensive event tracking with metadata, tags, and custom data
- Async telemetry collection and transmission
- Configurable batching and retry mechanisms
- Type-safe Python API with full type hints
- Session management with user tracking
- Multiple event levels (Debug, Info, Warning, Error, Critical)
- Background flushing for non-blocking operations
- Comprehensive test suite for both Rust and Python components
- CI/CD pipeline with GitHub Actions
- Cross-platform support (Linux, macOS, Windows)
- PyPI publishing automation
- Development tooling with Just and pre-commit hooks
- Security auditing and dependency review
- Performance monitoring and error tracking examples
- Comprehensive documentation and examples

### Features
- **TelemetryClient**: Main client for tracking events
- **TelemetryConfig**: Flexible configuration system
- **Event System**: Rich event data model with builder pattern
- **Session Management**: User session tracking and metadata
- **Background Processing**: Non-blocking event transmission
- **Error Handling**: Comprehensive error tracking and retry logic
- **Type Safety**: Full type annotations and runtime validation

### Developer Experience
- Easy installation via PyPI
- Simple Python API with sensible defaults
- Comprehensive documentation
- Example code and usage patterns
- Development environment setup with one command
- Automated testing and linting
- Security best practices built-in

[Unreleased]: https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/releases/tag/v0.1.0