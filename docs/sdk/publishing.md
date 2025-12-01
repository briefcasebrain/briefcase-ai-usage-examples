# Publishing Workflow

This document outlines the automated publishing and distribution process for the Briefcase AI Telemetry SDK across multiple package repositories.

## Overview

The SDK is published to multiple package ecosystems to support different programming languages:

- **PyPI** (Python Package Index) - Python developers
- **npm** (Node Package Manager) - JavaScript/Node.js developers
- **crates.io** (Rust Package Registry) - Rust developers
- **GitHub Releases** - Pre-built binaries and CLI tools

All publishing is automated through GitHub Actions with proper versioning, testing, and security controls.

## Repository Structure

```
briefcase-ai-telemetry-sdk/
├── .github/workflows/          # CI/CD automation
│   ├── release.yml            # Main release workflow
│   ├── test.yml               # Testing on PRs
│   └── security.yml           # Security scanning
├── crates/                    # Rust source code
│   └── briefcase-ai-telemetry/
├── bindings/                  # Language bindings
│   ├── python/               # Python package setup
│   └── node/                 # Node.js package setup
├── Cargo.toml                # Rust package manifest
├── pyproject.toml            # Python package manifest
├── package.json              # Node.js package manifest
└── release.toml              # Release configuration
```

## Release Process

### Automated Release (Recommended)

#### 1. Trigger Release
```bash
# Create and push a version tag
git tag v0.2.0
git push origin v0.2.0

# Or use GitHub CLI
gh release create v0.2.0 --title "Release v0.2.0" --notes "Release notes here"
```

#### 2. Automated Workflow
The GitHub Actions workflow automatically:

1. **Validates Release**
   - Runs full test suite across all languages
   - Performs security vulnerability scanning
   - Validates package manifests
   - Checks documentation links

2. **Builds Packages**
   - Builds Rust crate for crates.io
   - Cross-compiles binaries for multiple platforms
   - Builds Python wheels for multiple platforms
   - Builds Node.js native modules

3. **Publishes to Registries**
   - Publishes to crates.io (Rust)
   - Publishes to PyPI (Python)
   - Publishes to npm (JavaScript)
   - Creates GitHub release with artifacts

4. **Updates Documentation**
   - Updates API documentation
   - Publishes docs to GitHub Pages
   - Updates version in examples

### Manual Release (Emergency/Testing)

#### Prerequisites
```bash
# Install required tools
cargo install cargo-release
pip install twine
npm install -g publish-please

# Authenticate with registries
cargo login  # Enter crates.io token
echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" >> ~/.npmrc
echo "[pypi]\nusername = __token__\npassword = ${PYPI_TOKEN}" >> ~/.pypirc
```

#### Release Steps
```bash
# 1. Bump versions
./scripts/bump-version.sh 0.2.0

# 2. Build packages
make build-all

# 3. Run tests
make test-all

# 4. Publish packages
make publish-all

# 5. Create GitHub release
gh release create v0.2.0 --title "v0.2.0" --generate-notes
```

## Package Publishing

### PyPI (Python Package Index)

#### Configuration
```toml
# pyproject.toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "briefcase-ai-telemetry"
dynamic = ["version"]
description = "AI telemetry SDK for Python"
authors = [
    {name = "Briefcase AI", email = "sdk@briefcasebrain.com"},
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Rust",
    "Topic :: Software Development :: Libraries",
]
```

#### Build Process
```bash
# Local testing
maturin develop

# Build wheel for current platform
maturin build

# Build wheels for all platforms (requires CI/CD)
maturin build --release --universal2
maturin build --release --target x86_64-unknown-linux-gnu
maturin build --release --target aarch64-unknown-linux-gnu
```

#### Publishing
```yaml
# .github/workflows/release.yml (excerpt)
- name: Build wheels
  uses: PyO3/maturin-action@v1
  with:
    target: ${{ matrix.target }}
    args: --release --out dist --find-interpreter
    sccache: 'true'
    manylinux: auto

- name: Upload wheels
  uses: PyO3/maturin-action@v1
  with:
    command: upload
    args: --skip-existing dist/*
```

### npm (Node Package Manager)

#### Configuration
```json
{
  "name": "briefcase-ai-telemetry",
  "version": "0.1.0",
  "description": "AI telemetry SDK for Node.js",
  "main": "index.js",
  "types": "index.d.ts",
  "napi": {
    "name": "briefcase-ai-telemetry",
    "triples": {
      "defaults": true,
      "additional": [
        "x86_64-unknown-linux-musl",
        "aarch64-unknown-linux-gnu",
        "i686-pc-windows-msvc",
        "armv7-unknown-linux-gnueabihf",
        "aarch64-apple-darwin",
        "aarch64-pc-windows-msvc",
        "aarch64-unknown-linux-musl"
      ]
    }
  },
  "license": "MIT",
  "files": [
    "index.js",
    "index.d.ts"
  ],
  "keywords": [
    "telemetry",
    "ai",
    "monitoring",
    "analytics",
    "rust",
    "napi"
  ],
  "engines": {
    "node": ">= 16"
  }
}
```

#### Build Process
```bash
# Build for current platform
npm run build

# Build for all platforms (CI/CD)
npm run build:release

# Generate TypeScript definitions
npm run build:types
```

#### Publishing
```yaml
# .github/workflows/release.yml (excerpt)
- name: Build Node.js bindings
  run: npm run build:release

- name: Publish to npm
  run: npm publish
  env:
    NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### crates.io (Rust Package Registry)

#### Configuration
```toml
# Cargo.toml
[package]
name = "briefcase-ai-telemetry"
version = "0.1.0"
edition = "2021"
authors = ["Briefcase AI <sdk@briefcasebrain.com>"]
license = "MIT"
description = "AI telemetry and monitoring SDK"
homepage = "https://briefcasebrain.com"
repository = "https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk"
documentation = "https://docs.rs/briefcase-ai-telemetry"
readme = "README.md"
keywords = ["telemetry", "ai", "monitoring", "analytics"]
categories = ["development-tools", "web-programming"]

[lib]
name = "briefcase_ai_telemetry"
crate-type = ["cdylib", "rlib"]

[features]
default = ["python"]
python = ["dep:pyo3"]
cli = ["dep:clap"]
```

#### Publishing
```bash
# Check package before publishing
cargo check --all-targets --all-features

# Dry run
cargo publish --dry-run

# Publish to crates.io
cargo publish
```

### GitHub Releases

#### Binary Builds
```yaml
# .github/workflows/release.yml (excerpt)
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        target: x86_64-unknown-linux-gnu
        artifact-name: briefcase-ai-telemetry-linux-amd64
      - os: ubuntu-latest
        target: aarch64-unknown-linux-gnu
        artifact-name: briefcase-ai-telemetry-linux-arm64
      - os: macos-latest
        target: x86_64-apple-darwin
        artifact-name: briefcase-ai-telemetry-macos-amd64
      - os: macos-latest
        target: aarch64-apple-darwin
        artifact-name: briefcase-ai-telemetry-macos-arm64
      - os: windows-latest
        target: x86_64-pc-windows-msvc
        artifact-name: briefcase-ai-telemetry-windows-amd64.exe
```

## Version Management

### Semantic Versioning
We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality, backward compatible
- **PATCH** version: Bug fixes, backward compatible

### Version Synchronization
All package manifests must maintain synchronized versions:

```bash
# Update all versions atomically
./scripts/bump-version.sh 0.2.0

# This updates:
# - Cargo.toml
# - pyproject.toml
# - package.json
# - Version constants in code
```

### Release Branches
```bash
# Development happens on main
git checkout main

# Release candidates on release branches
git checkout -b release/0.2.0

# Hotfixes on hotfix branches
git checkout -b hotfix/0.1.1
```

## Quality Gates

### Automated Testing
Before any release, all tests must pass:

```yaml
# Required checks for release
- unit-tests-rust
- integration-tests-python
- integration-tests-node
- security-scan
- license-check
- documentation-build
- cross-platform-build
```

### Security Scanning
```yaml
# Security validation
- name: Security audit
  run: |
    cargo audit
    safety check
    npm audit

- name: SAST scanning
  uses: github/codeql-action/analyze@v2
  with:
    languages: rust, python, javascript
```

### Performance Benchmarks
```bash
# Performance regression detection
cargo bench --bench telemetry_benchmark > current_bench.txt
python scripts/compare_benchmarks.py baseline_bench.txt current_bench.txt
```

## Publishing Credentials

### Required Secrets
Configure these secrets in GitHub repository settings:

- **`CARGO_REGISTRY_TOKEN`**: crates.io API token
- **`PYPI_API_TOKEN`**: PyPI API token
- **`NPM_TOKEN`**: npm registry token
- **`GITHUB_TOKEN`**: GitHub releases token (auto-provided)

### Token Management
```bash
# Rotate tokens quarterly
# 1. Generate new tokens in each registry
# 2. Update GitHub secrets
# 3. Test with dry-run releases
# 4. Revoke old tokens
```

## Monitoring and Rollback

### Release Monitoring
```bash
# Monitor package downloads
cargo search briefcase-ai-telemetry
pip download briefcase-ai-telemetry --no-deps
npm view briefcase-ai-telemetry

# Check for issues
github-cli api repos/briefcasebrain/briefcase-ai-telemetry-sdk/issues
```

### Rollback Procedures

#### PyPI Rollback
```bash
# Cannot delete from PyPI, but can yank
pip install twine
twine yank briefcase-ai-telemetry 0.2.0 --reason "Critical security issue"
```

#### npm Rollback
```bash
# Deprecate version
npm deprecate briefcase-ai-telemetry@0.2.0 "Critical security issue, upgrade to 0.2.1"

# Or unpublish within 24 hours
npm unpublish briefcase-ai-telemetry@0.2.0
```

#### crates.io Rollback
```bash
# Yank version
cargo yank --vers 0.2.0 briefcase-ai-telemetry
```

#### GitHub Release Rollback
```bash
# Delete release
gh release delete v0.2.0

# Delete tag
git tag -d v0.2.0
git push origin --delete v0.2.0
```

## Release Checklist

### Pre-Release
- [ ] All tests passing on main branch
- [ ] Security vulnerabilities addressed
- [ ] Documentation updated
- [ ] Version numbers bumped consistently
- [ ] Changelog updated with release notes
- [ ] Breaking changes documented

### Release
- [ ] Create and push version tag
- [ ] Monitor automated release workflow
- [ ] Verify packages published to all registries
- [ ] Test installation from each registry
- [ ] Update documentation website

### Post-Release
- [ ] Announce release on community channels
- [ ] Monitor for installation issues
- [ ] Update dependent projects and examples
- [ ] Plan next release milestone

## Troubleshooting

### Common Publishing Issues

#### Build Failures
```bash
# Check cross-compilation setup
rustup target list --installed
cargo check --target x86_64-unknown-linux-gnu

# Python wheel build issues
pip install --upgrade maturin
maturin build --compatibility=linux
```

#### Authentication Issues
```bash
# Verify credentials
cargo login --dry-run
npm whoami
twine check dist/*
```

#### Network Issues
```bash
# Configure proxy settings
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080

# Or use .cargo/config.toml for registry settings
```

### Support
For publishing issues:
- **Technical**: [GitHub Issues](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
- **Security**: [security@briefcasebrain.com](mailto:security@briefcasebrain.com)
- **Registry support**: Contact individual registry support teams

---

**Next**: Learn about [SDK Usage Examples](examples.md) or explore our [API Reference](api-reference.md).