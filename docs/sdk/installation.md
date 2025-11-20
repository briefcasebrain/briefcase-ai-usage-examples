# Installation Guide

This guide covers how to install the Briefcase AI Telemetry SDK in your project.

## System Requirements

### Supported Platforms
- **Operating Systems**: Linux, macOS, Windows
- **Python**: 3.8+ (for Python bindings)
- **Node.js**: 16+ (for JavaScript bindings)
- **Rust**: 1.70+ (for Rust usage)

### Dependencies
- Modern C++ compiler (for native extensions)
- OpenSSL/TLS support
- Internet connectivity for telemetry transmission

## Installation Methods

### Python Installation (Recommended)

#### From PyPI
```bash
# Install the latest stable version
pip install briefcase-ai-telemetry

# Install a specific version
pip install briefcase-ai-telemetry==0.1.0

# Install with optional dependencies
pip install briefcase-ai-telemetry[dev]
```

#### Using Poetry
```bash
# Add to your project
poetry add briefcase-ai-telemetry

# For development dependencies
poetry add briefcase-ai-telemetry --group dev
```

#### Using Pipenv
```bash
# Add to Pipfile
pipenv install briefcase-ai-telemetry

# For development
pipenv install briefcase-ai-telemetry --dev
```

#### Using conda/mamba
```bash
# Install from conda-forge (coming soon)
conda install -c conda-forge briefcase-ai-telemetry

# Using mamba
mamba install -c conda-forge briefcase-ai-telemetry
```

### Rust Installation

#### From Crates.io
```toml
# Add to your Cargo.toml
[dependencies]
briefcase-ai-telemetry = "0.1.0"

# With specific features
briefcase-ai-telemetry = { version = "0.1.0", features = ["python"] }

# For async runtime compatibility
briefcase-ai-telemetry = { version = "0.1.0", features = ["tokio"] }
```

#### Using Cargo
```bash
# Add to your project
cargo add briefcase-ai-telemetry

# With features
cargo add briefcase-ai-telemetry --features python,tokio
```

### JavaScript/Node.js Installation

#### From npm
```bash
# Install with npm
npm install briefcase-ai-telemetry

# Install globally for CLI usage
npm install -g briefcase-ai-telemetry

# Install specific version
npm install briefcase-ai-telemetry@0.1.0
```

#### Using Yarn
```bash
# Add to your project
yarn add briefcase-ai-telemetry

# For development
yarn add briefcase-ai-telemetry --dev
```

#### Using pnpm
```bash
# Add to your project
pnpm add briefcase-ai-telemetry
```

### CLI Installation

#### Standalone Binary (Recommended for CLI)
```bash
# Install via Cargo
cargo install briefcase-ai-telemetry --features cli

# Download pre-built binary (Linux/macOS/Windows)
curl -sSL https://releases.briefcase.ai/install.sh | sh

# Using Homebrew (macOS/Linux)
brew install briefcase-ai/tap/briefcase-ai-telemetry
```

#### Platform-specific Packages
```bash
# Ubuntu/Debian
wget https://releases.briefcase.ai/briefcase-ai-telemetry_0.1.0_amd64.deb
sudo dpkg -i briefcase-ai-telemetry_0.1.0_amd64.deb

# CentOS/RHEL/Fedora
wget https://releases.briefcase.ai/briefcase-ai-telemetry_0.1.0_x86_64.rpm
sudo rpm -i briefcase-ai-telemetry_0.1.0_x86_64.rpm

# Arch Linux (AUR)
yay -S briefcase-ai-telemetry

# Windows (Chocolatey)
choco install briefcase-ai-telemetry

# Windows (Scoop)
scoop bucket add briefcase-ai https://github.com/briefcasebrain/scoop-bucket
scoop install briefcase-ai-telemetry
```

## Installation Verification

### Python Verification
```python
import briefcase_ai_telemetry

# Check version
print(briefcase_ai_telemetry.__version__)

# Test basic import
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig

# Verify installation
config = TelemetryConfig("test-key")
client = TelemetryClient(config)
print("SDK successfully installed!")
```

### Rust Verification
```rust
use briefcase_ai_telemetry::{TelemetryClient, TelemetryConfig};

fn main() -> anyhow::Result<()> {
    // Check that imports work
    let config = TelemetryConfig::new("test-key".to_string());
    let _client = TelemetryClient::new(config)?;

    println!("SDK successfully installed!");
    Ok(())
}
```

### JavaScript Verification
```javascript
const { TelemetryClient, TelemetryConfig } = require('briefcase-ai-telemetry');

// Check version
console.log(require('briefcase-ai-telemetry/package.json').version);

// Test basic usage
const config = new TelemetryConfig('test-key');
const client = new TelemetryClient(config);
console.log('SDK successfully installed!');
```

### CLI Verification
```bash
# Check installation
briefcase-ai-telemetry --version

# Run basic help command
briefcase-ai-telemetry --help

# Test connectivity (optional)
briefcase-ai-telemetry test-connection --api-key "your-test-key"
```

## Environment Setup

### API Key Configuration

#### Environment Variable (Recommended)
```bash
# Set in your shell profile (.bashrc, .zshrc, etc.)
export BRIEFCASE_AI_API_KEY="your-api-key-here"

# Or create a .env file
echo "BRIEFCASE_AI_API_KEY=your-api-key-here" > .env
```

#### Configuration File
```bash
# Create config directory
mkdir -p ~/.config/briefcase-ai

# Create config file
cat > ~/.config/briefcase-ai/config.toml << EOF
api_key = "your-api-key-here"
endpoint = "https://observe.briefcasebrain.io/api/v1/telemetry"
timeout = 10
batch_size = 100
EOF
```

### Network Configuration

#### Proxy Settings
```bash
# HTTP proxy
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"

# No proxy for specific domains
export NO_PROXY="localhost,127.0.0.1,.local"
```

#### Firewall Configuration
Ensure your firewall allows outbound HTTPS connections to:
- `api.briefcase.ai:443`
- `telemetry.briefcase.ai:443`

## Troubleshooting

### Common Installation Issues

#### Python: Missing Compiler
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# macOS
xcode-select --install

# Windows
# Install Microsoft C++ Build Tools
# Or install Visual Studio with C++ workload
```

#### Rust: Toolchain Issues
```bash
# Install/update Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup update

# Install required targets
rustup target add x86_64-unknown-linux-gnu
rustup target add x86_64-pc-windows-gnu
rustup target add aarch64-apple-darwin
```

#### Node.js: Native Module Build Failures
```bash
# Install node-gyp globally
npm install -g node-gyp

# Rebuild native modules
npm rebuild

# Clear npm cache if needed
npm cache clean --force
```

#### Permission Issues
```bash
# Fix npm permissions (avoid sudo)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc

# Python user installation
pip install --user briefcase-ai-telemetry

# Cargo user installation
cargo install briefcase-ai-telemetry --locked
```

### Verification Issues

#### Import Errors
```python
# Python: Check installation location
import briefcase_ai_telemetry
print(briefcase_ai_telemetry.__file__)

# Python: Check Python path
import sys
print(sys.path)
```

#### Version Conflicts
```bash
# Check installed versions
pip list | grep briefcase
cargo tree | grep briefcase
npm list briefcase-ai-telemetry
```

#### API Key Issues
```bash
# Test API key validity
briefcase-ai-telemetry validate-key --api-key "your-key"

# Check environment variables
echo $BRIEFCASE_AI_API_KEY
printenv | grep BRIEFCASE
```

### Getting Help

If you encounter installation issues:

1. **Check our FAQ**: [Common installation problems](https://docs.briefcase.ai/faq)
2. **Search existing issues**: [GitHub Issues](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
3. **Create a new issue**: Include your OS, Python/Node/Rust version, and error messages
4. **Join our community**: [Discord server](https://discord.gg/briefcase-ai) for real-time help

## Next Steps

After successful installation:

1. **Configure your API key** following the environment setup above
2. **Read the [Usage Examples](examples.md)** to understand basic SDK usage
3. **Review the [API Reference](api-reference.md)** for comprehensive documentation
4. **Check out [Integration Guides](../integrations/README.md)** for framework-specific usage

---

**Installation complete?** Continue to [Usage Examples](examples.md) to start using the SDK!