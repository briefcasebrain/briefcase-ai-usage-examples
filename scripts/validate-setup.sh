#!/bin/bash

# Validation script for Briefcase AI Telemetry SDK setup
# This script performs a dry run to validate that all workflow steps succeed

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate required tools
validate_dependencies() {
    log_info "Validating required dependencies..."

    local missing_deps=()

    if ! command_exists cargo; then
        missing_deps+=("cargo (Rust)")
    fi

    if ! command_exists python3; then
        missing_deps+=("python3")
    fi

    if ! command_exists pip; then
        missing_deps+=("pip")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        return 1
    fi

    log_success "All required dependencies found"
}

# Validate Rust setup
validate_rust() {
    log_info "Validating Rust setup..."

    # Check Rust version
    local rust_version
    rust_version=$(cargo --version)
    log_info "Found: $rust_version"

    # Check if workspace is valid
    if ! cargo check --workspace; then
        log_error "Cargo workspace validation failed"
        return 1
    fi

    log_success "Rust setup is valid"
}

# Validate Python setup
validate_python() {
    log_info "Validating Python setup..."

    # Check Python version
    local python_version
    python_version=$(python3 --version)
    log_info "Found: $python_version"

    # Check if we can install maturin
    if ! python3 -m pip install --dry-run maturin >/dev/null 2>&1; then
        log_warning "Cannot validate maturin installation (pip --dry-run may not be supported)"
    else
        log_success "Maturin installation validated"
    fi

    log_success "Python setup is valid"
}

# Test Rust compilation
test_rust_build() {
    log_info "Testing Rust compilation..."

    # Test Rust core library without Python bindings
    if ! cargo build --workspace --no-default-features; then
        log_error "Rust core compilation failed"
        return 1
    fi

    log_success "Rust core compilation succeeded"
}

# Test Rust tests
test_rust_tests() {
    log_info "Running Rust tests..."

    # Test Rust core without Python features
    if ! cargo test --workspace --no-default-features; then
        log_error "Rust core tests failed"
        return 1
    fi

    log_success "Rust core tests passed"
}

# Test Rust formatting
test_rust_format() {
    log_info "Checking Rust formatting..."

    if ! cargo fmt --check; then
        log_error "Rust code is not formatted correctly. Run 'cargo fmt' to fix."
        return 1
    fi

    log_success "Rust formatting is correct"
}

# Test Rust linting
test_rust_lint() {
    log_info "Running Rust linting..."

    if ! cargo clippy --all-targets --all-features -- -D warnings; then
        log_error "Rust linting failed"
        return 1
    fi

    log_success "Rust linting passed"
}

# Install development dependencies
install_dev_deps() {
    log_info "Installing development dependencies..."

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        /opt/homebrew/bin/python3 -m venv venv
    fi

    # Install maturin in virtual environment
    if ! ./venv/bin/python -m pip install --upgrade pip; then
        log_error "Failed to upgrade pip"
        return 1
    fi

    if ! ./venv/bin/python -m pip install 'maturin[patchelf]'; then
        log_error "Failed to install maturin"
        return 1
    fi

    # Install test dependencies
    if ! ./venv/bin/python -m pip install pytest pytest-asyncio; then
        log_error "Failed to install test dependencies"
        return 1
    fi

    log_success "Development dependencies installed in virtual environment"
}

# Test Python package build
test_python_build() {
    log_info "Testing Python package build..."

    # Set up virtual environment for maturin
    export VIRTUAL_ENV="$(pwd)/venv"

    if ! ./venv/bin/maturin develop --release; then
        log_error "Python package build failed"
        return 1
    fi

    log_success "Python package build succeeded"
}

# Test Python imports
test_python_imports() {
    log_info "Testing Python imports..."

    # Set up virtual environment for Python
    export VIRTUAL_ENV="$(pwd)/venv"

    if ! ./venv/bin/python -c "import briefcase_ai_telemetry; print('Import successful')"; then
        log_error "Python import test failed"
        return 1
    fi

    log_success "Python imports work correctly"
}

# Test Python tests
test_python_tests() {
    log_info "Running Python tests..."

    # Set up virtual environment for Python
    export VIRTUAL_ENV="$(pwd)/venv"

    if ! ./venv/bin/python -m pytest python/tests/ -v; then
        log_error "Python tests failed"
        return 1
    fi

    log_success "Python tests passed"
}

# Test Python formatting
test_python_format() {
    log_info "Checking Python formatting..."

    # Set up virtual environment for Python
    export VIRTUAL_ENV="$(pwd)/venv"

    if ./venv/bin/python -c "import black" 2>/dev/null; then
        if ! ./venv/bin/python -m black --check python/; then
            log_error "Python code is not formatted correctly. Run './venv/bin/python -m black python/' to fix."
            return 1
        fi
        log_success "Python formatting is correct"
    else
        log_warning "Black not installed, skipping Python format check"
    fi
}

# Test Python linting
test_python_lint() {
    log_info "Running Python linting..."

    # Set up virtual environment for Python
    export VIRTUAL_ENV="$(pwd)/venv"

    if ./venv/bin/python -c "import ruff" 2>/dev/null; then
        if ! ./venv/bin/python -m ruff check python/; then
            log_error "Python linting failed"
            return 1
        fi
        log_success "Python linting passed"
    else
        log_warning "Ruff not installed, skipping Python lint check"
    fi
}

# Test security audit
test_security_audit() {
    log_info "Running security audit..."

    if command_exists cargo-audit; then
        if ! cargo audit; then
            log_error "Security audit failed"
            return 1
        fi
        log_success "Security audit passed"
    else
        log_warning "cargo-audit not installed, skipping security audit"
    fi
}

# Validate GitHub Actions workflow files
validate_workflows() {
    log_info "Validating GitHub Actions workflows..."

    local workflow_files=(".github/workflows/ci.yml" ".github/workflows/release.yml")

    for file in "${workflow_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Workflow file missing: $file"
            return 1
        fi

        # Basic YAML syntax validation
        if [ -f "./venv/bin/python" ]; then
            if ! ./venv/bin/python -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                log_error "Invalid YAML syntax in: $file"
                return 1
            fi
        elif command_exists python3; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                log_error "Invalid YAML syntax in: $file"
                return 1
            fi
        fi
    done

    log_success "GitHub Actions workflows are valid"
}

# Test wheel building (dry run)
test_wheel_build() {
    log_info "Testing wheel building..."

    # Set up virtual environment for maturin
    export VIRTUAL_ENV="$(pwd)/venv"

    if ! ./venv/bin/maturin build --release; then
        log_error "Wheel building failed"
        return 1
    fi

    log_success "Wheel building succeeded"
}

# Test example script
test_examples() {
    log_info "Testing example scripts..."

    # Set up virtual environment for Python
    export VIRTUAL_ENV="$(pwd)/venv"

    if [ -f "examples/basic_usage.py" ]; then
        if ! ./venv/bin/python examples/basic_usage.py; then
            log_error "Example script failed"
            return 1
        fi
        log_success "Example script ran successfully"
    else
        log_warning "No example scripts found to test"
    fi
}

# Main validation function
main() {
    echo "🚀 Briefcase AI Telemetry SDK - Setup Validation"
    echo "=================================================="
    echo ""

    local start_time
    start_time=$(date +%s)

    # Step 1: Validate dependencies
    if ! validate_dependencies; then
        log_error "Dependency validation failed"
        exit 1
    fi
    echo ""

    # Step 2: Validate basic setup
    if ! validate_rust; then
        log_error "Rust setup validation failed"
        exit 1
    fi
    echo ""

    if ! validate_python; then
        log_error "Python setup validation failed"
        exit 1
    fi
    echo ""

    # Step 3: Install dependencies (if not already installed)
    if [ ! -d "venv" ] || ! ./venv/bin/python -c "import maturin" 2>/dev/null; then
        if ! install_dev_deps; then
            log_error "Development dependency installation failed"
            exit 1
        fi
        echo ""
    else
        log_info "Development dependencies already installed"
        echo ""
    fi

    # Step 4: Test Rust components
    if ! test_rust_build; then
        log_error "Rust build test failed"
        exit 1
    fi
    echo ""

    if ! test_rust_format; then
        log_error "Rust format test failed"
        exit 1
    fi
    echo ""

    if ! test_rust_lint; then
        log_error "Rust lint test failed"
        exit 1
    fi
    echo ""

    if ! test_rust_tests; then
        log_error "Rust test execution failed"
        exit 1
    fi
    echo ""

    # Step 5: Test Python components
    if ! test_python_build; then
        log_error "Python build test failed"
        exit 1
    fi
    echo ""

    if ! test_python_imports; then
        log_error "Python import test failed"
        exit 1
    fi
    echo ""

    if ! test_python_tests; then
        log_error "Python test execution failed"
        exit 1
    fi
    echo ""

    # Step 6: Test formatting and linting
    test_python_format
    echo ""

    test_python_lint
    echo ""

    # Step 7: Security and quality checks
    test_security_audit
    echo ""

    # Step 8: Validate workflows
    if ! validate_workflows; then
        log_error "Workflow validation failed"
        exit 1
    fi
    echo ""

    # Step 9: Test building
    if ! test_wheel_build; then
        log_error "Wheel build test failed"
        exit 1
    fi
    echo ""

    # Step 10: Test examples
    test_examples
    echo ""

    local end_time
    end_time=$(date +%s)
    local duration
    duration=$((end_time - start_time))

    echo "=================================================="
    log_success "🎉 All validation tests passed! ($duration seconds)"
    echo ""
    echo "✅ The project setup is valid and ready for development"
    echo "✅ CI/CD workflows should work correctly"
    echo "✅ Ready for commit and push to feature branch"
    echo ""
    echo "Next steps:"
    echo "  1. git add ."
    echo "  2. git commit -m 'Initial project scaffolding'"
    echo "  3. git push -u origin feature/initial-scaffolding"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi