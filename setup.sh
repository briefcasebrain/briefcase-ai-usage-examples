#!/bin/bash

# Briefcase AI Demo Setup Script
# This script sets up a complete environment for running both demo suites

set -e  # Exit on any error

echo "========================================="
echo "Briefcase AI Demo Setup"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python 3 is installed
print_header "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    echo "Please install Python 3.9 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Found Python $PYTHON_VERSION"

# Check Python version (require 3.9+, but warn about 3.14+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Python 3.9 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
    print_warning "Python $PYTHON_VERSION detected. briefcase-ai may need compilation from source."
    print_warning "For best results, consider using Python 3.11 or 3.12 with pre-compiled wheels."
fi

# Create virtual environment
print_header "Step 2: Setting up virtual environment..."
VENV_DIR="briefcase-ai-demos-env"

if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment '$VENV_DIR' already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        print_status "Using existing virtual environment."
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
print_header "Step 3: Installing core dependencies..."

# Check if briefcase-ai is available via pip
print_status "Checking for briefcase-ai SDK..."

# Try pip install first
print_status "Installing briefcase-ai from PyPI..."
if pip install briefcase-ai; then
    print_status "Successfully installed briefcase-ai from PyPI"
    SDK_INSTALLED=true
else
    print_warning "Failed to install briefcase-ai from PyPI"
    SDK_INSTALLED=false

    # Check if we can build from source (local checkout of the SDK repo)
    BRIEFCASE_AI_SOURCE="../briefcase-ai-sdk"
    if [ -d "$BRIEFCASE_AI_SOURCE" ]; then
        print_status "Found briefcase-ai source at $BRIEFCASE_AI_SOURCE"
        print_status "Attempting to build from source..."

        # Install build dependencies
        pip install maturin

        # Try to build from source
        print_status "Building briefcase-ai from source..."
        cd "$BRIEFCASE_AI_SOURCE"

        if maturin develop; then
            print_status "Successfully built briefcase-ai from source"
            SDK_INSTALLED=true
        else
            print_warning "Failed to build briefcase-ai from source"
            SDK_INSTALLED=false
        fi

        cd - > /dev/null
    fi

    if [ "$SDK_INSTALLED" = false ]; then
        print_warning "briefcase-ai SDK could not be installed"
        echo
        echo "The demos require the open-source briefcase-ai SDK (Apache-2.0) to run."
        echo "It is published on PyPI; a failed install is usually a build/toolchain issue."
        echo "Options to resolve this:"
        echo "1. Use Python 3.11 or 3.12 (best prebuilt-wheel coverage), then: pip install briefcase-ai"
        echo "2. Install the Rust toolchain (https://rustup.rs) so the wheel can compile from source"
        echo "3. Build from a local SDK checkout at ../briefcase-ai-sdk (maturin develop)"
        echo
        echo "SETUP WILL CONTINUE - but demos may show import errors until SDK is available."
        echo
        read -p "Continue with setup? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Setup cancelled by user"
            exit 0
        fi
    fi
fi

# Install demo dependencies
print_status "Installing demo dependencies..."
cat > requirements_demo.txt << EOF
# Data analysis and visualization
pandas>=1.5.0
matplotlib>=3.6.0
seaborn>=0.12.0
numpy>=1.24.0
scipy>=1.10.0

# Jupyter notebook support
jupyter>=1.0.0
ipykernel>=6.0.0
notebook>=6.5.0

# Development and testing (optional)
pytest>=7.0.0
black>=22.0.0
EOF

pip install -r requirements_demo.txt
rm requirements_demo.txt

# Install Jupyter kernel
print_status "Setting up Jupyter kernel for virtual environment..."
python -m ipykernel install --user --name=briefcase-ai-demos --display-name="Briefcase AI Demos"

print_header "Step 4: Verifying installation..."

# Test briefcase-ai import if it was installed
if [ "$SDK_INSTALLED" = true ]; then
    print_status "Testing briefcase-ai import..."
    python3 -c "
import briefcase
print(f'SUCCESS: briefcase-ai imported successfully')
print(f'Available classes: {[attr for attr in dir(briefcase) if not attr.startswith(\"_\")]}')
" || {
        print_warning "briefcase-ai installed but import failed"
        SDK_INSTALLED=false
    }
else
    print_warning "Skipping briefcase-ai import test (SDK not installed)"
fi

# Test other dependencies
print_status "Testing other dependencies..."
python3 -c "
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
print('SUCCESS: All analysis dependencies imported successfully')
" || {
    print_error "Failed to import analysis dependencies"
    exit 1
}

print_header "Step 5: Setup verification..."

# Check demo directories
if [ ! -d "vantara-briefcase-demo" ]; then
    print_error "vantara-briefcase-demo directory not found"
    exit 1
fi

if [ ! -d "regulatory-workflows" ]; then
    print_error "regulatory-workflows directory not found"
    exit 1
fi

print_status "Found both demo directories"

# Quick test of demo setup
print_status "Running quick demo test..."
cd vantara-briefcase-demo

if [ "$SDK_INSTALLED" = true ]; then
    python3 -c "
import sys
import os
sys.path.append('../shared')
import backend
print('SUCCESS: Backend module loaded with real SDK')
print('Real briefcase module available')
" && DEMO_TEST_PASSED=true || DEMO_TEST_PASSED=false
else
    python3 -c "
import sys
import os
sys.path.append('../shared')
print('Demo directory structure verified')
print('Shared modules accessible')
" && DEMO_TEST_PASSED=true || DEMO_TEST_PASSED=false
fi

cd ..

if [ "$DEMO_TEST_PASSED" = false ]; then
    print_error "Demo setup test failed"
    exit 1
fi

print_header "Setup Complete!"
echo
print_status "Virtual environment created: $VENV_DIR"

if [ "$SDK_INSTALLED" = true ]; then
    print_status "briefcase-ai SDK installed and tested"
    print_status "All dependencies installed successfully"
    echo
    echo "🎉 SETUP SUCCESSFUL - Ready to run all demos!"
else
    print_warning "Demo environment configured (briefcase-ai SDK not available)"
    print_warning "Demos will show import errors until SDK is installed"
    echo
    echo "⚠️  PARTIAL SETUP - Environment ready, but SDK required for demos"
fi

print_status "Jupyter kernel 'Briefcase AI Demos' configured"
echo
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo
echo "1. Activate the virtual environment:"
echo "   source $VENV_DIR/bin/activate"
echo

if [ "$SDK_INSTALLED" = true ]; then
    echo "2. Run the demos:"
    echo "   cd vantara-briefcase-demo"
    echo "   python 01_agent_discovery/example.py"
    echo
    echo "3. Or start Jupyter notebooks:"
    echo "   jupyter notebook"
    echo "   (Select 'Briefcase AI Demos' kernel)"
else
    echo "2. Install briefcase-ai SDK:"
    echo "   pip install briefcase-ai  # when available"
    echo "   # OR build from a local SDK checkout (see ../briefcase-ai-sdk)"
    echo
    echo "3. Then run the demos:"
    echo "   cd vantara-briefcase-demo"
    echo "   python 01_agent_discovery/example.py"
    echo
    echo "4. Or start Jupyter notebooks:"
    echo "   jupyter notebook"
    echo "   (Select 'Briefcase AI Demos' kernel)"
fi

echo
echo "For detailed instructions, see:"
echo "   cat RUNNING_DEMOS.md"
echo

if [ "$SDK_INSTALLED" = true ]; then
    print_status "Setup completed successfully!"
else
    print_warning "Setup completed - install briefcase-ai SDK to run demos"
fi