# Development Setup

This guide covers setting up a development environment for contributing to the Briefcase AI Telemetry SDK.

## Prerequisites

### Required Tools
- **Rust**: 1.70+ with `cargo`, `rustc`, `rustup`
- **Python**: 3.8+ with `pip`, `venv`
- **Node.js**: 16+ with `npm` or `yarn`
- **Git**: For version control
- **Make**: For build automation (optional but recommended)

### Optional Tools
- **Docker**: For containerized development and testing
- **maturin**: For Python binding development
- **wasm-pack**: For WebAssembly bindings (future)
- **pre-commit**: For automated code quality checks

## Environment Setup

### 1. Clone the Repository
```bash
# Clone the repository
git clone https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk.git
cd briefcase-ai-telemetry-sdk

# Install git hooks (optional)
git config core.hooksPath .githooks
chmod +x .githooks/*
```

### 2. Rust Development Environment
```bash
# Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install required components
rustup component add rustfmt clippy

# Install additional targets for cross-compilation
rustup target add x86_64-unknown-linux-gnu
rustup target add x86_64-pc-windows-gnu
rustup target add aarch64-apple-darwin

# Install cargo tools
cargo install cargo-nextest  # Better test runner
cargo install cargo-watch   # File watching
cargo install cargo-audit   # Security auditing
cargo install cargo-deny    # Dependency checking
```

### 3. Python Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip and install build tools
pip install --upgrade pip
pip install maturin[patchelf]  # For building Python wheels

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 4. Node.js Development Environment
```bash
# Install Node.js dependencies
npm install

# Or using Yarn
yarn install

# Install development tools globally (optional)
npm install -g @napi-rs/cli  # For Node.js native bindings
npm install -g typescript    # TypeScript support
```

### 5. Development Tools Configuration

#### VSCode Setup (Recommended)
```bash
# Install recommended extensions
code --install-extension rust-lang.rust-analyzer
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension bradlc.vscode-tailwindcss
code --install-extension tamasfe.even-better-toml
code --install-extension serayuzgur.crates

# Open project in VSCode
code .
```

#### Vim/Neovim Setup
```vim
" Add to your .vimrc or init.vim
Plugin 'rust-lang/rust.vim'
Plugin 'prabirshrestha/async.vim'
Plugin 'prabirshrestha/vim-lsp'
Plugin 'mattn/vim-lsp-settings'

" Configure rust-analyzer
let g:lsp_settings = {
\   'rust-analyzer': {
\     'initialization_options': {
\       'cargo': {
\         'buildScripts': {
\           'enable': v:true,
\         },
\       },
\     },
\   },
\}
```

## Building the SDK

### Rust Core
```bash
# Build the core Rust library
cargo build

# Build in release mode
cargo build --release

# Build with specific features
cargo build --features "python,cli"

# Build for different targets
cargo build --target x86_64-unknown-linux-gnu
```

### Python Bindings
```bash
# Activate Python virtual environment
source venv/bin/activate

# Build Python wheel
maturin develop

# Build wheel for distribution
maturin build

# Build and install in development mode
maturin develop --release
```

### Node.js Bindings
```bash
# Build Node.js native module
npm run build

# Build for specific platforms
npm run build:linux
npm run build:macos
npm run build:windows

# Generate TypeScript definitions
npm run build:types
```

### CLI Binary
```bash
# Build CLI binary
cargo build --bin briefcase-ai-telemetry --features cli

# Install locally for testing
cargo install --path . --features cli

# Create release binaries
./scripts/build-releases.sh
```

## Testing

### Running Tests

#### Rust Tests
```bash
# Run all Rust tests
cargo test

# Run tests without Python feature
cargo test --no-default-features

# Run tests with specific features
cargo test --features "python,cli"

# Run with better test output
cargo nextest run

# Run specific test modules
cargo test drift::tests
cargo test cost::tests
```

#### Python Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Install in development mode
maturin develop

# Run Python tests
pytest tests/python/

# Run with coverage
pytest --cov=briefcase_ai_telemetry tests/python/

# Run specific test files
pytest tests/python/test_client.py
```

#### Node.js Tests
```bash
# Run Node.js tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test suites
npm test -- --grep="TelemetryClient"
```

#### Integration Tests
```bash
# Run all integration tests
cargo test --test integration

# Run end-to-end tests
./scripts/run-e2e-tests.sh

# Test against live API (requires valid API key)
BRIEFCASE_AI_API_KEY="your-key" cargo test --test live_api
```

### Test Coverage

#### Generate Coverage Reports
```bash
# Rust coverage (requires cargo-tarpaulin)
cargo install cargo-tarpaulin
cargo tarpaulin --out Html --output-dir coverage/

# Python coverage
pytest --cov=briefcase_ai_telemetry --cov-report=html tests/python/

# Node.js coverage
npm run test:coverage
open coverage/lcov-report/index.html
```

#### Coverage Thresholds
- **Rust Core**: Minimum 85% line coverage
- **Python Bindings**: Minimum 80% line coverage
- **Node.js Bindings**: Minimum 80% line coverage
- **Integration Tests**: All critical paths covered

## Code Quality

### Formatting and Linting

#### Rust
```bash
# Format code
cargo fmt

# Check formatting
cargo fmt -- --check

# Run clippy lints
cargo clippy -- -D warnings

# Run clippy on all targets
cargo clippy --all-targets --all-features -- -D warnings
```

#### Python
```bash
# Format with black
black src/python/ tests/python/

# Lint with flake8
flake8 src/python/ tests/python/

# Type checking with mypy
mypy src/python/

# Sort imports
isort src/python/ tests/python/
```

#### Node.js/TypeScript
```bash
# Format with prettier
npm run format

# Lint with ESLint
npm run lint

# Type checking
npm run type-check

# Fix linting issues automatically
npm run lint:fix
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

The pre-commit configuration includes:
- Rust formatting and linting
- Python formatting (black), linting (flake8), and type checking
- JavaScript/TypeScript formatting and linting
- TOML and YAML formatting
- Trailing whitespace and line ending fixes
- Security vulnerability scanning

## Debugging

### Rust Debugging
```bash
# Build with debug symbols
cargo build

# Run with debug output
RUST_LOG=debug cargo run --bin briefcase-ai-telemetry

# Use GDB or LLDB
gdb target/debug/briefcase-ai-telemetry
lldb target/debug/briefcase-ai-telemetry

# Memory debugging with Valgrind (Linux)
valgrind --tool=memcheck cargo test
```

### Python Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugpy for VSCode debugging
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### Performance Profiling
```bash
# Profile Rust code with perf (Linux)
cargo build --release
perf record target/release/briefcase-ai-telemetry
perf report

# Profile with cargo flamegraph
cargo install flamegraph
cargo flamegraph --bin briefcase-ai-telemetry

# Benchmark with criterion
cargo bench
```

## Development Workflow

### Feature Development
1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Tests First** (TDD approach recommended)
   ```bash
   # Add tests for new functionality
   cargo test your_new_test -- --nocapture
   ```

3. **Implement Feature**
   - Follow existing code patterns
   - Add comprehensive error handling
   - Include documentation

4. **Validate Changes**
   ```bash
   # Run all tests
   make test

   # Run linting
   make lint

   # Check formatting
   make format-check
   ```

### Making Changes

#### Adding New Features
```bash
# 1. Add to Rust core
vim crates/briefcase-ai-telemetry/src/new_module.rs

# 2. Update lib.rs to expose module
vim crates/briefcase-ai-telemetry/src/lib.rs

# 3. Add Python bindings if needed
vim crates/briefcase-ai-telemetry/src/python.rs

# 4. Add tests
vim crates/briefcase-ai-telemetry/src/new_module.rs  # Add #[cfg(test)] mod

# 5. Update documentation
vim docs/sdk/api-reference.md
```

#### Modifying Existing Code
- Always run tests before and after changes
- Update relevant documentation
- Consider backward compatibility
- Add changelog entries for breaking changes

### Release Process
```bash
# 1. Update version numbers
vim Cargo.toml
vim pyproject.toml
vim package.json

# 2. Update changelog
vim CHANGELOG.md

# 3. Create release commit
git commit -m "chore: release v0.2.0"

# 4. Tag release
git tag v0.2.0

# 5. Push changes
git push origin main --tags
```

## Environment Variables for Development

```bash
# Development environment
export RUST_LOG=debug                    # Enable debug logging
export BRIEFCASE_AI_API_KEY="test-key"  # Test API key
export BRIEFCASE_AI_ENDPOINT="http://localhost:8080"  # Local dev server

# Testing
export RUST_BACKTRACE=1                 # Full backtraces on panic
export CARGO_TERM_COLOR=always          # Colored output
export PYTHONDONTWRITEBYTECODE=1        # Don't create .pyc files

# Performance
export CARGO_BUILD_JOBS=4               # Parallel build jobs
export RUST_MIN_STACK=8388608           # Larger stack for complex operations
```

## Troubleshooting Development Issues

### Build Issues
```bash
# Clean build artifacts
cargo clean
rm -rf target/

# Update dependencies
cargo update

# Check for dependency conflicts
cargo tree --duplicates
```

### Python Binding Issues
```bash
# Reinstall maturin
pip install --force-reinstall maturin

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Rebuild wheel
maturin develop --force
```

### Test Failures
```bash
# Run single test with output
cargo test test_name -- --nocapture --exact

# Run tests with thread count = 1 (avoid race conditions)
cargo test -- --test-threads=1

# Enable backtraces
RUST_BACKTRACE=1 cargo test
```

## Getting Help

### Internal Resources
- **Architecture docs**: `docs/architecture/`
- **API examples**: `examples/`
- **Test cases**: `tests/` and module `#[cfg(test)]` sections
- **Issue tracker**: [GitHub Issues](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)

### External Resources
- **Rust documentation**: [doc.rust-lang.org](https://doc.rust-lang.org/)
- **PyO3 guide**: [pyo3.rs](https://pyo3.rs/)
- **maturin docs**: [maturin.rs](https://maturin.rs/)
- **Cargo reference**: [doc.rust-lang.org/cargo](https://doc.rust-lang.org/cargo/)

### Community
- **Discord**: [Join our development chat](https://discord.gg/briefcase-ai-dev)
- **Discussions**: [GitHub Discussions](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/discussions)
- **Developer Office Hours**: Fridays 10 AM PST

---

**Ready to contribute?** Check out our [good first issues](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/labels/good%20first%20issue) or continue to [Publishing Workflow](publishing.md) to understand our release process.