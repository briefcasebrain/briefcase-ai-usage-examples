# 🚀 Briefcase AI Telemetry SDK - Client Onboarding Guide

**Welcome to the Briefcase AI Beta Program**

This guide provides complete instructions for accessing and using the Briefcase AI Telemetry SDK as a beta participant.

## 📋 **Prerequisites & Legal Requirements**

### **Step 1: Beta Participation Agreement**

Before accessing the SDK, you **MUST** sign the Beta Participation and License Agreement:

📄 **[Download: Beta Participation Agreement](./legal/BETA_PARTICIPATION_AGREEMENT.pdf)**

**Key Points:**
- ✅ **Required**: Signed agreement for SDK access
- ⚠️ **Beta Status**: Experimental software - testing environments only
- 🔒 **Confidentiality**: No sharing of product information without consent
- 🚫 **Data Restrictions**: No PII, financial, or health data without DPA
- 💰 **Liability Cap**: Limited to $100 USD

**Agreement Covers:**
- Web dashboard access: https://observe.briefcasebrain.io/
- SDK download and integration rights
- Data transmission and usage terms
- Intellectual property and feedback ownership

### **Step 2: Submit Signed Agreement**

Email your signed agreement to: **beta@briefcasebrain.com**

**Required Information:**
- Signed PDF agreement
- Organization name and contact details
- Intended use case description
- Technical contact information

**Processing Time:** 1-2 business days for access provisioning

## 🔐 **Account Setup & Access**

### **Dashboard Access**

Once approved, you'll receive:
- ✅ **Dashboard Login**: https://observe.briefcasebrain.io/
- ✅ **API Key**: For SDK authentication
- ✅ **PyPI Credentials**: For package installation
- ✅ **Support Contact**: Direct channel for assistance

### **PyPI Repository Access**

**Private Repository:** https://pypi.briefcasebrain.com/

Your credentials will be provided via secure email after agreement approval.

## 📦 **SDK Installation**

### **System Requirements**

- **Python**: 3.9+ (3.11 recommended)
- **Platforms**: Linux (x86_64, aarch64), macOS (Intel, Apple Silicon), Windows (x64)
- **Dependencies**: pip, virtual environment support
- **Network**: HTTPS access to pypi.briefcasebrain.com

### **Installation Methods**

#### **Method 1: Direct Installation (Recommended)**

```bash
# Install from private PyPI with credentials
pip install --index-url https://USERNAME:PASSWORD@pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry
```

#### **Method 2: Configuration File**

Create `~/.pypirc`:

```ini
[distutils]
index-servers = briefcase-ai

[briefcase-ai]
repository = https://pypi.briefcasebrain.com/
username = YOUR_USERNAME
password = YOUR_PASSWORD
```

Then install:

```bash
pip install --index-url https://pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry
```

#### **Method 3: Requirements File**

Create `requirements.txt`:

```txt
--index-url https://pypi.briefcasebrain.com/simple/
--trusted-host pypi.briefcasebrain.com

briefcase-ai-telemetry>=0.1.0
```

Install:

```bash
pip install -r requirements.txt
```

### **Installation Verification**

```python
import briefcase_ai_telemetry as bt

print(f"✅ Briefcase AI Telemetry SDK v{bt.__version__}")
print("🎉 Installation successful!")

# Test basic functionality
client = bt.create_client("your-api-key", enabled=False)
event = bt.create_event("test_event", level=bt.EventLevel.info())
print("🔧 Core functionality verified")
```

## 🛠️ **Initial Configuration**

### **API Key Setup**

Add your API key to your environment:

```bash
# Environment variable
export BRIEFCASE_API_KEY="your-api-key-here"

# Or in .env file
echo "BRIEFCASE_API_KEY=your-api-key-here" >> .env
```

### **Basic Client Configuration**

```python
import briefcase_ai_telemetry as bt
import os

# Initialize client
client = bt.create_client(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    endpoint="https://observe.briefcasebrain.io/api/v1/telemetry",
    enabled=True,  # Set False for testing
    batch_size=100,
    flush_interval_seconds=30
)

# Start background telemetry
client.start_background_flush()
```

## 📊 **Beta Testing Guidelines**

### **Recommended Testing Approach**

**Phase 1: Local Development**
```python
# Disable telemetry for local development
client = bt.create_client(
    api_key="test-key",
    enabled=False  # No data transmission
)
```

**Phase 2: Staging Environment**
```python
# Enable telemetry in staging
client = bt.create_client(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    enabled=True,
    endpoint="https://observe.briefcasebrain.io/api/v1/telemetry"
)
```

**Phase 3: Limited Production** (⚠️ **Your Risk**)
- Only after thorough staging validation
- Monitor for any performance impact
- Have rollback plan ready

### **Data Sensitivity Guidelines**

**✅ Safe to Track:**
- Application performance metrics
- Error rates and system health
- User interaction patterns (anonymized)
- Feature usage statistics
- Infrastructure metrics

**🚫 Prohibited Data:**
- Personally Identifiable Information (PII)
- Financial data (PCI compliance required)
- Protected Health Information (PHI)
- Sensitive business data without DPA
- Customer passwords or credentials

### **Example Safe Usage**

```python
# ✅ Safe: Performance tracking
client.track_event(bt.create_event(
    "api_request",
    level=bt.EventLevel.info(),
    custom_data={
        "endpoint": "/api/users",
        "duration_ms": 234,
        "status_code": 200,
        "region": "us-west-2"
    }
))

# ✅ Safe: Feature usage
client.track_event(bt.create_event(
    "feature_used",
    level=bt.EventLevel.info(),
    custom_data={
        "feature": "export_data",
        "user_type": "premium",
        "success": True
    }
))

# 🚫 Prohibited: PII data
client.track_event(bt.create_event(
    "user_login",
    level=bt.EventLevel.info(),
    custom_data={
        "email": "user@example.com",  # ❌ PII
        "password": "secret123"       # ❌ Sensitive
    }
))
```

## 🐛 **Bug Reporting & Feedback**

### **Issue Reporting**

**Email**: beta-support@briefcasebrain.com

**Include in Reports:**
- SDK version (`bt.__version__`)
- Python version and OS
- Minimal code to reproduce
- Error messages and stack traces
- Expected vs actual behavior

**Bug Report Template:**
```
Subject: [SDK Bug] Brief description

Environment:
- SDK Version: X.X.X
- Python Version: 3.X.X
- OS: Linux/macOS/Windows
- Installation Method: pip/requirements.txt

Issue Description:
[Detailed description]

Steps to Reproduce:
1. Step one
2. Step two
3. Step three

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happens]

Code Sample:
```python
# Minimal reproduction code
```

Error Messages:
[Full stack trace if available]
```

### **Feature Requests**

**Process:**
1. Email: feature-requests@briefcasebrain.com
2. Include business justification
3. Describe current workarounds
4. Provide usage examples

**Response Time:**
- Bug reports: 24-48 hours
- Feature requests: 1 week
- Critical issues: 4-6 hours

## 📞 **Support & Resources**

### **Contact Information**

**Primary Support**: beta-support@briefcasebrain.com
**Legal Questions**: legal@briefcasebrain.com
**Technical Issues**: engineering@briefcasebrain.com
**Business Inquiries**: business@briefcasebrain.com

### **Office Hours**

**Live Support**: Monday-Friday, 9 AM - 5 PM PST
**Emergency**: 24/7 for critical production issues
**Response SLA**:
- Critical: 4 hours
- High: 24 hours
- Medium: 72 hours
- Low: 1 week

### **Documentation Links**

- **Dashboard**: https://observe.briefcasebrain.io/docs
- **API Reference**: https://observe.briefcasebrain.io/docs/api
- **Examples**: https://observe.briefcasebrain.io/docs/examples
- **SDK Documentation**: [Technical Integration Guide](./TECHNICAL_INTEGRATION_GUIDE.md)

### **Community & Updates**

**Beta Program Updates:**
- Monthly newsletter with new features
- Early access to new versions
- Direct feedback channel to product team

**Slack Channel**: briefcase-beta-users (invitation sent post-approval)

## ⚠️ **Important Reminders**

### **Legal Compliance**

- ✅ **Agreement Required**: Must be signed before use
- ✅ **Confidentiality**: No sharing of product information
- ✅ **Data Protection**: Follow prohibited data guidelines
- ✅ **Terms Updates**: Will be notified of any changes

### **Beta Limitations**

- 🔄 **API Changes**: May occur with notice
- 🐛 **Bugs Expected**: Report promptly for fixes
- 📊 **Data Retention**: Subject to beta program policies
- 🔒 **Access Revocation**: Company reserves right to terminate

### **Success Metrics**

Help us improve by tracking:
- **Integration Time**: How long to get started?
- **Feature Gaps**: What's missing for your use case?
- **Performance Impact**: Any issues in your application?
- **Documentation Quality**: What needs clarification?

### **Graduation to Production**

**Timeline**: Beta expected to run 3-6 months
**Production Criteria**:
- Stability and performance benchmarks met
- Major feature set complete
- Customer validation achieved

**Benefits of Beta Participation:**
- 🎯 **Early Access**: First to use new features
- 💰 **Pricing Advantage**: Preferential rates for early adopters
- 🤝 **Direct Influence**: Shape product development
- 🏆 **Partnership Opportunities**: Potential case studies and co-marketing

---

## 📧 **Next Steps**

1. **Sign Agreement**: Download, complete, and return beta agreement
2. **Await Approval**: Receive access credentials via email
3. **Install SDK**: Follow installation instructions
4. **Join Community**: Access Slack channel and resources
5. **Start Testing**: Begin integration with provided examples
6. **Provide Feedback**: Help us improve the product

**Welcome to the future of AI observability! 🚀**

For immediate assistance: beta-support@briefcasebrain.com