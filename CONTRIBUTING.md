# Contributing to Briefcase AI Telemetry SDK

We welcome contributions to the Briefcase AI Telemetry SDK! This document outlines the process for contributing to the project.

## Getting Started

### Prerequisites
- Rust 1.70 or later
- Python 3.8 or later
- [Just](https://github.com/casey/just) for task automation

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/briefcase-ai-telemetry-sdk.git
   cd briefcase-ai-telemetry-sdk
   ```

2. **Set up the development environment**
   ```bash
   # Install dependencies and set up environment
   just setup
   ```

3. **Verify the setup**
   ```bash
   # Run all tests
   just test

   # Build the project
   just build
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Follow existing code style and conventions
   - Add tests for new functionality

3. **Test your changes**
   ```bash
   # Run all tests
   just test

   # Format code
   just fmt

   # Run lints
   just lint
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Commit Message Format

We follow the [Conventional Commits](https://conventionalcommits.org/) specification:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add batch telemetry submission
fix: resolve authentication header handling
docs: update API documentation
test: add integration tests for client
```

## Code Style Guidelines

### Rust Code
- Use `cargo fmt` for formatting
- Follow Rust naming conventions
- Write documentation comments for public APIs
- Keep functions focused and small

### Python Code
- Use `black` for formatting
- Use `isort` for import organization
- Follow PEP 8 style guidelines
- Add type hints where appropriate

### Running Code Formatters
```bash
# Format all code
just fmt

# Or format individually
cargo fmt                    # Rust
black python/                # Python
isort python/                # Python imports
```

## Testing

### Running Tests

```bash
# Run all tests
just test

# Run Rust tests only
just test-rust
# or: cargo test

# Run Python tests only
just test-python
# or: python -m pytest python/tests/

# Run with coverage
just test-coverage
```

### Writing Tests

#### Rust Tests
- Write unit tests in the same file as the code being tested
- Use integration tests in the `tests/` directory for cross-module testing
- Mock external dependencies in tests

#### Python Tests
- Write tests in the `python/tests/` directory
- Use `pytest` for test framework
- Include both unit and integration tests

## Documentation

### Code Documentation
- Write clear docstrings for all public functions and classes
- Include examples in documentation where helpful
- Keep documentation up to date with code changes

### Project Documentation
- Update README.md for significant changes
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/) format
- Add examples for new features

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
   ```bash
   just test
   ```

2. **Verify code formatting**
   ```bash
   just fmt
   just lint
   ```

3. **Update documentation**
   - Add/update docstrings
   - Update README if needed
   - Add entry to CHANGELOG.md

4. **Rebase your branch**
   ```bash
   git rebase main
   ```

### Submitting the PR

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Use a clear, descriptive title
   - Fill out the PR template
   - Link any related issues

3. **PR Review Process**
   - Address reviewer feedback promptly
   - Keep discussions focused and professional
   - Update your branch based on feedback

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## Issue Reporting

### Bug Reports
When reporting bugs, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Rust/Python version)
- Code samples if relevant

### Feature Requests
When requesting features, include:
- Clear description of the feature
- Use case and motivation
- Proposed API or implementation approach
- Willingness to contribute implementation

## Development Tips

### Common Tasks
```bash
# Quick development cycle
just fmt && just test

# Build release version
just build

# Clean build artifacts
just clean

# Run security audit
just audit
```

### Debugging
- Use `tracing` crate for logging in Rust code
- Set `RUST_LOG=debug` for detailed logs
- Use debugger or print statements for complex issues

### Performance
- Profile code for performance-critical changes
- Benchmark before and after changes
- Consider memory usage and allocation patterns

## License and Contribution Agreement

### Business Source License
This project is licensed under the Business Source License 1.1. By contributing:

- You agree that your contributions will be licensed under the same BSL-1.1 license
- You confirm you have the right to submit your contribution under this license
- Your contributions may be used in commercial versions of the software
- The software (including your contributions) will become Apache 2.0 licensed on November 19, 2029

### Contributor License Agreement (CLA)
For significant contributions, we may require a signed Contributor License Agreement. This ensures:
- Legal clarity around contribution ownership
- Ability to offer commercial licenses
- Protection for both contributors and Briefcase AI

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

### Getting Help
- Check existing issues and documentation first
- Ask questions in GitHub Discussions
- Be specific about your problem and environment
- Provide minimal reproducible examples

## Release Process

### For Maintainers
1. Update version numbers in `Cargo.toml` and `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Create release tag and GitHub release
4. Publish to crates.io and PyPI
5. Update commercial licensing documentation

## Commercial Use

If you're interested in using this software to provide telemetry services to third parties, please contact [support@briefcasebrain.com](mailto:support@briefcasebrain.com) for commercial licensing options.

Thank you for contributing to the Briefcase AI Telemetry SDK! 🚀