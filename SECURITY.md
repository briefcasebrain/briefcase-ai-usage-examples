# Security Policy

## Supported Versions

These examples track the `briefcase-ai` SDK. We actively support examples running against the following SDK versions:

| briefcase-ai version | Supported          |
| -------------------- | ------------------ |
| 3.2.x                | :white_check_mark: |
| 3.1.x                | :white_check_mark: |

## Reporting Security Vulnerabilities

We take security seriously. If you discover a security vulnerability in the Briefcase AI Telemetry SDK, please report it responsibly.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

Instead, please send an email to [support@briefcaseai.org] with the following information:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes or mitigations

### What to Include

When reporting a security vulnerability, please include as much information as possible:

1. **Type of vulnerability** (e.g., authentication bypass, data exposure, code injection)
2. **Location of the vulnerability** (specific file/function/endpoint)
3. **Step-by-step reproduction instructions**
4. **Proof of concept** (if applicable and safe)
5. **Suggested remediation** (if you have ideas)

### Response Timeline

We will acknowledge receipt of your vulnerability report within **48 hours** and provide a more detailed response within **7 days** indicating the next steps in handling your report.

We will keep you informed about the progress towards a fix and may ask for additional information or guidance.

### Disclosure Policy

- We will work with you to understand and resolve the issue quickly
- We will coordinate disclosure timing with you
- We will credit you for the discovery (unless you prefer anonymity)
- We will publish security advisories for significant vulnerabilities

## Security Best Practices

### For Users

When using the Briefcase AI Telemetry SDK:

1. **Protect API Keys**
   - Never hardcode API keys in source code
   - Use environment variables or secure configuration files
   - Rotate API keys regularly
   - Restrict API key permissions to minimum required scope

2. **Network Security**
   - Always use HTTPS endpoints
   - Validate SSL/TLS certificates
   - Use secure network configurations

3. **Data Privacy**
   - Review what data you're sending to telemetry endpoints
   - Avoid including sensitive information in telemetry data
   - Implement data retention policies
   - Consider data anonymization

4. **Access Control**
   - Limit access to telemetry configuration
   - Use principle of least privilege
   - Monitor for unauthorized access

### For Developers

When contributing to the SDK:

1. **Secure Coding**
   - Validate all inputs
   - Use safe APIs and avoid unsafe operations
   - Handle errors securely (don't expose sensitive info in error messages)
   - Follow OWASP secure coding guidelines

2. **Dependencies**
   - Keep dependencies up to date
   - Regularly audit dependencies for vulnerabilities
   - Use minimal dependency sets
   - Pin dependency versions appropriately

3. **Testing**
   - Include security testing in development workflow
   - Test with invalid/malicious inputs
   - Verify authentication and authorization
   - Test error handling paths

## Known Security Considerations

### Authentication
- API keys are included in request payloads (ensure HTTPS)
- Multiple authentication methods supported (Bearer token, API key)
- Failed authentication properly handled with appropriate error codes

### Data Handling
- Telemetry data is transmitted over HTTPS
- No client-side data persistence by default
- Configurable retry mechanisms with exponential backoff

### Network Security
- All communications use HTTPS
- Proper SSL/TLS certificate validation
- Configurable timeouts to prevent hanging connections
- Rate limiting support to prevent abuse

## Security Updates

Security updates will be:
- Released as soon as possible after discovery and verification
- Documented in release notes and security advisories
- Communicated through GitHub Security Advisories
- Backported to supported versions when feasible

## Security Tools

We use the following tools to help maintain security:

- **Rust**: Memory-safe language prevents many common vulnerabilities
- **Cargo Audit**: Scans for known security vulnerabilities in dependencies
- **Pre-commit Hooks**: Automated security checks before commits
- **GitHub Security Advisories**: Track and communicate security issues

### Running Security Audits

```bash
# Audit Rust dependencies
cargo audit

# Check for security issues
just audit

# Update dependencies
just update
```

## Contact

For any security-related questions or concerns that are not vulnerabilities, please contact [support@briefcaseai.org].

For general questions about the SDK, please use GitHub Issues or Discussions.

---

Thank you for helping keep the Briefcase AI Telemetry SDK secure! 🔒