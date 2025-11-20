# Justfile for Briefcase AI Telemetry SDK

# Default recipe to display available commands
default:
    @just --list

# Development setup
setup:
    @echo "Setting up development environment..."
    python -m pip install --upgrade pip
    python -m pip install maturin[patchelf]
    python -m pip install -e .[dev]
    pre-commit install
    @echo "Development environment setup complete!"

# Install development dependencies
install-deps:
    python -m pip install --upgrade pip
    python -m pip install maturin[patchelf]
    python -m pip install -e .[dev,test,docs]

# Build the Rust extension in development mode
dev:
    maturin develop

# Build the Rust extension in release mode
dev-release:
    maturin develop --release

# Run Rust tests
test-rust:
    cargo test --all-features

# Run Python tests
test-python:
    python -m pytest python/tests/ -v

# Run all tests
test: test-rust test-python

# Run tests with coverage
test-coverage:
    python -m pytest python/tests/ --cov=briefcase_ai_telemetry --cov-report=html --cov-report=term

# Format Rust code
fmt-rust:
    cargo fmt

# Format Python code
fmt-python:
    black python/
    isort python/

# Format all code
fmt: fmt-rust fmt-python

# Lint Rust code
lint-rust:
    cargo clippy --all-targets --all-features -- -D warnings

# Lint Python code
lint-python:
    black --check python/
    isort --check-only python/
    ruff check python/
    mypy python/briefcase_ai_telemetry/ --ignore-missing-imports

# Lint all code
lint: lint-rust lint-python

# Run security audit
audit:
    cargo audit

# Clean build artifacts
clean:
    cargo clean
    rm -rf dist/
    rm -rf target/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete
    rm -rf python/briefcase_ai_telemetry.egg-info/
    rm -rf .pytest_cache/
    rm -rf .coverage
    rm -rf htmlcov/

# Build wheels for distribution
build-wheels:
    maturin build --release

# Build source distribution
build-sdist:
    maturin sdist

# Build all distribution files
build: build-wheels build-sdist

# Publish to PyPI (test)
publish-test:
    maturin publish --repository testpypi

# Publish to PyPI (production)
publish:
    maturin publish

# Run pre-commit hooks on all files
pre-commit:
    pre-commit run --all-files

# Update dependencies
update-deps:
    cargo update
    python -m pip install --upgrade pip
    python -m pip install --upgrade -e .[dev,test,docs]

# Run benchmarks
bench:
    cargo bench

# Generate documentation
docs:
    cd docs && make html

# Serve documentation
docs-serve:
    cd docs && python -m http.server 8000

# Run example scripts
example script:
    python examples/{{script}}.py

# Start a development shell
shell:
    python -c "import briefcase_ai_telemetry; print('Briefcase AI Telemetry SDK imported successfully'); import IPython; IPython.start_ipython()"

# Check project health
health: lint test audit

# Release workflow (local testing)
release-check version:
    @echo "Checking release for version {{version}}..."
    @git tag -a "v{{version}}" -m "Release v{{version}}"
    @echo "Tagged version v{{version}}"
    @echo "To push: git push origin v{{version}}"
    @echo "To delete tag: git tag -d v{{version}}"

# CI/CD simulation
ci: clean install-deps dev-release health test-coverage
    @echo "CI simulation complete!"

# Profile the application
profile:
    cargo build --release
    perf record --call-graph=dwarf target/release/briefcase-ai-telemetry
    perf report