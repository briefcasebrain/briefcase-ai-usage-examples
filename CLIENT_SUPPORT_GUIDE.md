# 📞 Briefcase AI Telemetry SDK - Client Support Guide

**Comprehensive Support Resources for Beta Participants**

This guide provides complete support information, troubleshooting resources, and contact details for beta participants.

## 🎯 **Support Overview**

As a beta participant, you have access to dedicated support channels and resources to ensure successful integration and operation of the Briefcase AI Telemetry SDK.

### **Support Tiers**

**🚀 Beta Participant Support**
- Direct access to engineering team
- Priority response for critical issues
- Dedicated Slack channel access
- Monthly office hours sessions
- Early access to new features and updates

## 📧 **Contact Information**

### **Primary Support Channels**

| Issue Type | Email | Response Time |
|------------|-------|---------------|
| **Technical Issues** | engineering@briefcasebrain.com | 4-24 hours |
| **Beta Program** | beta-support@briefcasebrain.com | 24-48 hours |
| **Legal/Licensing** | legal@briefcasebrain.com | 1-3 business days |
| **Business Inquiries** | business@briefcasebrain.com | 1-3 business days |
| **Critical/Production** | emergency@briefcasebrain.com | 2-4 hours |

### **Support Hours**

**Standard Support**: Monday-Friday, 9:00 AM - 5:00 PM PST
**Emergency Support**: 24/7 for critical production issues
**Office Hours**: Every Friday, 2:00 PM - 3:00 PM PST (Zoom link provided)

### **Community Channels**

**Slack**: briefcase-beta-users (invitation sent after approval)
**GitHub Discussions**: Private repository access for beta participants
**Monthly Newsletter**: Product updates and feature announcements

## 🐛 **Issue Reporting & Escalation**

### **Bug Report Template**

```
Subject: [SDK Bug] Brief description of the issue

Environment Information:
- SDK Version: X.X.X (get with: import briefcase_ai_telemetry as bt; print(bt.__version__))
- Python Version: X.X.X
- Operating System: Linux/macOS/Windows + version
- Installation Method: pip/requirements.txt/wheel
- Environment: development/staging/production

Issue Description:
[Detailed description of the problem]

Steps to Reproduce:
1. Step one with specific details
2. Step two with specific details
3. Step three with specific details

Expected Behavior:
[What you expected to happen]

Actual Behavior:
[What actually happened]

Code Sample:
```python
# Minimal code to reproduce the issue
# Please include only essential code
```

Error Messages:
```
[Complete error messages and stack traces]
```

Additional Context:
- When did this issue start occurring?
- Does it happen consistently or intermittently?
- Any recent changes to your code or environment?
- Network configuration or proxy settings?

Impact Assessment:
[ ] Low - Minor inconvenience
[ ] Medium - Significant impact on development
[ ] High - Blocking development/testing
[ ] Critical - Production issue

Beta Agreement:
[ ] I confirm I have a signed beta participation agreement
[ ] I am following prohibited data guidelines
```

### **Escalation Process**

**Level 1**: Submit ticket via email (engineering@briefcasebrain.com)
**Level 2**: Critical issues (emergency@briefcasebrain.com)
**Level 3**: Beta program manager intervention
**Level 4**: Executive escalation for contract/business issues

### **Response Time SLAs**

| Priority | Initial Response | Resolution Target |
|----------|------------------|-------------------|
| **Critical** | 2-4 hours | 24-48 hours |
| **High** | 4-8 hours | 2-5 business days |
| **Medium** | 8-24 hours | 3-7 business days |
| **Low** | 1-3 business days | 1-2 weeks |

## 🔧 **Self-Service Troubleshooting**

### **Common Issues & Solutions**

#### **Installation Problems**

**Issue**: `pip install` fails with authentication error
```bash
ERROR: Exception:
Traceback (most recent call last):
...
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**Solutions**:
1. **Check Credentials**:
   ```bash
   # Verify you have correct username/password
   curl -u username:password https://pypi.briefcasebrain.com/simple/
   ```

2. **Update pip Configuration**:
   ```bash
   # Create or update ~/.pypirc
   [distutils]
   index-servers = briefcase-ai

   [briefcase-ai]
   repository = https://pypi.briefcasebrain.com/
   username = YOUR_USERNAME
   password = YOUR_PASSWORD
   ```

3. **Clear pip Cache**:
   ```bash
   pip cache purge
   pip install --no-cache-dir --index-url https://pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry
   ```

**Issue**: SSL Certificate verification failed
```bash
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError'
```

**Solutions**:
```bash
# Option 1: Add trusted host
pip install --trusted-host pypi.briefcasebrain.com --index-url https://pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry

# Option 2: Upgrade certificates
pip install --upgrade certifi

# Option 3: Corporate firewall - contact your IT department
```

#### **Import Errors**

**Issue**: `ImportError: Could not import Rust extension module`
```python
ImportError: Could not import Rust extension module.
This usually means the package was not installed correctly.
```

**Solutions**:
1. **Reinstall Package**:
   ```bash
   pip uninstall briefcase-ai-telemetry
   pip install --index-url https://pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry
   ```

2. **Check Python Version Compatibility**:
   ```python
   import sys
   print(f"Python version: {sys.version}")
   # Requires Python 3.9+
   ```

3. **Virtual Environment Issues**:
   ```bash
   # Create fresh virtual environment
   python -m venv fresh_env
   source fresh_env/bin/activate  # Linux/macOS
   # fresh_env\Scripts\activate  # Windows
   pip install --index-url https://pypi.briefcasebrain.com/simple/ briefcase-ai-telemetry
   ```

#### **Authentication Issues**

**Issue**: API key authentication failures
```python
requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: https://observe.briefcasebrain.io/api/v1/telemetry
```

**Debug Steps**:
1. **Check API Key Format**:
   ```python
   import os
   api_key = os.getenv("BRIEFCASE_API_KEY")
   print(f"API Key length: {len(api_key) if api_key else 'None'}")
   print(f"API Key prefix: {api_key[:8] if api_key else 'None'}...")
   ```

2. **Test Connection**:
   ```python
   import briefcase_ai_telemetry as bt

   client = bt.create_client(
       api_key="your-api-key",
       enabled=True,
       timeout_seconds=10
   )

   # Test with simple event
   event = bt.create_event("connection_test", level=bt.EventLevel.info())
   client.track_event(event)
   client.flush()
   print("✅ Connection successful")
   ```

3. **Check Environment Variables**:
   ```bash
   # Linux/macOS
   echo $BRIEFCASE_API_KEY

   # Windows
   echo %BRIEFCASE_API_KEY%

   # Python
   python -c "import os; print('API Key:', os.getenv('BRIEFCASE_API_KEY', 'NOT SET'))"
   ```

#### **Network Connectivity**

**Issue**: Connection timeouts or network errors

**Diagnostic Commands**:
```bash
# Test basic connectivity
curl -I https://observe.briefcasebrain.io/

# Test with authentication
curl -u username:password https://pypi.briefcasebrain.com/simple/

# Check DNS resolution
nslookup pypi.briefcasebrain.com
nslookup observe.briefcasebrain.io

# Test from Python
python -c "import requests; print(requests.get('https://observe.briefcasebrain.io/health', timeout=5).status_code)"
```

**Common Solutions**:
- Corporate firewall: Contact IT to whitelist domains
- Proxy configuration: Set HTTP_PROXY and HTTPS_PROXY environment variables
- VPN issues: Try disconnecting VPN temporarily for testing

#### **Performance Issues**

**Issue**: High latency or memory usage

**Performance Monitoring**:
```python
import briefcase_ai_telemetry as bt
import time
import psutil

def monitor_telemetry_performance():
    # Monitor memory usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss

    # Create client with performance settings
    client = bt.create_client(
        api_key="your-api-key",
        enabled=True,
        batch_size=200,  # Adjust based on volume
        flush_interval_seconds=30,  # Batch for efficiency
        timeout_seconds=5
    )

    # Track events with timing
    start_time = time.time()

    for i in range(100):
        event = bt.create_event(f"perf_test_{i}")
        client.track_event(event)

    client.flush()

    end_time = time.time()
    final_memory = process.memory_info().rss

    print(f"Time for 100 events: {(end_time - start_time) * 1000:.2f}ms")
    print(f"Memory increase: {(final_memory - initial_memory) / 1024 / 1024:.2f}MB")

monitor_telemetry_performance()
```

### **Diagnostic Tools**

#### **SDK Health Check Script**

```python
#!/usr/bin/env python3
"""
Briefcase AI Telemetry SDK Health Check
Run this script to diagnose common issues
"""

import briefcase_ai_telemetry as bt
import os
import sys
import requests
import json
from datetime import datetime

def health_check():
    print("🏥 Briefcase AI Telemetry SDK Health Check")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print("=" * 50)

    # Check 1: SDK Installation
    print("\n📋 Check 1: SDK Installation")
    try:
        print(f"✅ SDK Version: {bt.__version__}")
        print(f"✅ Python Version: {sys.version}")
        print(f"✅ Platform: {sys.platform}")
    except Exception as e:
        print(f"❌ SDK Import Error: {e}")
        return

    # Check 2: Environment Variables
    print("\n📋 Check 2: Environment Variables")
    api_key = os.getenv("BRIEFCASE_API_KEY")
    if api_key:
        print(f"✅ API Key: {'*' * 8}{api_key[-4:] if len(api_key) > 4 else '****'}")
    else:
        print("⚠️  API Key: Not set (BRIEFCASE_API_KEY environment variable)")

    # Check 3: Network Connectivity
    print("\n📋 Check 3: Network Connectivity")
    endpoints = [
        "https://observe.briefcasebrain.io/health",
        "https://pypi.briefcasebrain.com/health"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

    # Check 4: Basic SDK Functionality
    print("\n📋 Check 4: SDK Functionality")
    try:
        # Test client creation
        client = bt.create_client(
            api_key=api_key or "test-key",
            enabled=False,  # Safe for testing
            timeout_seconds=5
        )
        print("✅ Client Creation: Success")

        # Test event creation
        event = bt.create_event(
            "health_check_test",
            level=bt.EventLevel.info(),
            message="Health check test event"
        )
        print("✅ Event Creation: Success")

        # Test event tracking (without network)
        client.track_event(event)
        print("✅ Event Tracking: Success")

        # Test buffer management
        buffer_size = client.buffer_size()
        print(f"✅ Buffer Size: {buffer_size}")

    except Exception as e:
        print(f"❌ SDK Functionality Error: {e}")

    # Check 5: Advanced Features
    print("\n📋 Check 5: Advanced Features")
    try:
        # Test drift detection
        test_outputs = ["output1", "output2", "output3"]
        metrics = bt.calculate_drift(test_outputs)
        print(f"✅ Drift Detection: {metrics.consensus_confidence}")

        # Test cost estimation
        cost = bt.estimate_cost("gpt-4", "test input", "test output")
        if cost:
            print(f"✅ Cost Estimation: ${cost.total_cost:.6f}")
        else:
            print("⚠️  Cost Estimation: Model not found (expected)")

        # Test agent instrumentation
        instrument = bt.create_agent_instrument(999, client)
        session = instrument.start()
        session.finish()
        print("✅ Agent Instrumentation: Success")

    except Exception as e:
        print(f"❌ Advanced Features Error: {e}")

    # Check 6: Configuration Validation
    print("\n📋 Check 6: Configuration Validation")

    # Check for common configuration issues
    if api_key and len(api_key) < 10:
        print("⚠️  API Key seems too short")

    # Check Python version compatibility
    python_version = sys.version_info
    if python_version < (3, 9):
        print(f"❌ Python {python_version.major}.{python_version.minor} not supported (requires 3.9+)")
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor} supported")

    # Summary
    print("\n" + "=" * 50)
    print("🏁 Health Check Complete")
    print("\nIf you see any ❌ or ⚠️  items above, please include this output when")
    print("contacting support at: engineering@briefcasebrain.com")

if __name__ == "__main__":
    health_check()
```

Save as `health_check.py` and run:
```bash
python health_check.py
```

#### **Performance Benchmark Script**

```python
#!/usr/bin/env python3
"""
Performance Benchmark for Briefcase AI Telemetry SDK
"""

import briefcase_ai_telemetry as bt
import time
import statistics
import gc
import psutil
import os

def benchmark_sdk():
    print("⚡ Briefcase AI Telemetry SDK Performance Benchmark")
    print("=" * 50)

    # Setup
    client = bt.create_client(
        api_key=os.getenv("BRIEFCASE_API_KEY", "test-key"),
        enabled=False,  # No network overhead
        batch_size=100
    )

    # Benchmark 1: Event Creation
    print("\n📊 Benchmark 1: Event Creation (1000 events)")
    times = []

    for i in range(5):  # 5 iterations for average
        gc.collect()  # Clean garbage collection

        start_time = time.perf_counter()
        for j in range(1000):
            event = bt.create_event(
                f"benchmark_event_{j}",
                level=bt.EventLevel.info(),
                custom_data={"iteration": j, "batch": i}
            )
        end_time = time.perf_counter()

        duration = (end_time - start_time) * 1000
        times.append(duration)

    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0

    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Std Dev: {std_dev:.2f}ms")
    print(f"  Per Event: {avg_time/1000:.3f}ms")

    # Benchmark 2: Event Tracking
    print("\n📊 Benchmark 2: Event Tracking (1000 events)")
    times = []

    for i in range(5):
        events = [
            bt.create_event(f"track_test_{j}")
            for j in range(1000)
        ]

        gc.collect()
        start_time = time.perf_counter()

        for event in events:
            client.track_event(event)

        end_time = time.perf_counter()

        duration = (end_time - start_time) * 1000
        times.append(duration)

    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0

    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Std Dev: {std_dev:.2f}ms")
    print(f"  Per Event: {avg_time/1000:.3f}ms")

    # Benchmark 3: Memory Usage
    print("\n📊 Benchmark 3: Memory Usage")
    process = psutil.Process()

    initial_memory = process.memory_info().rss

    # Create many events
    events = [
        bt.create_event(f"memory_test_{i}", custom_data={"data": "x" * 100})
        for i in range(10000)
    ]

    for event in events:
        client.track_event(event)

    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / 1024 / 1024

    print(f"  Memory Increase: {memory_increase:.2f}MB")
    print(f"  Per 1000 Events: {memory_increase/10:.3f}MB")

    # Benchmark 4: Advanced Features
    print("\n📊 Benchmark 4: Advanced Features")

    # Drift detection timing
    test_outputs = [f"output_{i}" for i in range(100)]

    start_time = time.perf_counter()
    metrics = bt.calculate_drift(test_outputs)
    end_time = time.perf_counter()

    drift_time = (end_time - start_time) * 1000
    print(f"  Drift Analysis (100 outputs): {drift_time:.2f}ms")

    # Cost estimation timing
    start_time = time.perf_counter()
    for i in range(100):
        cost = bt.estimate_cost("gpt-4", "test input", "test output")
    end_time = time.perf_counter()

    cost_time = (end_time - start_time) * 1000
    print(f"  Cost Estimation (100 calls): {cost_time:.2f}ms")
    print(f"  Per Cost Estimation: {cost_time/100:.3f}ms")

    # Summary
    print("\n" + "=" * 50)
    print("📈 Performance Summary")
    print("If you notice performance issues:")
    print("1. Increase batch_size for high-volume applications")
    print("2. Increase flush_interval_seconds to reduce network calls")
    print("3. Consider async_mode for non-blocking operation")
    print("4. Monitor application performance impact")

if __name__ == "__main__":
    benchmark_sdk()
```

## 💡 **Best Practices & Tips**

### **Development Workflow**

1. **Local Development**:
   ```python
   # Disable telemetry during development
   client = bt.create_client(
       api_key="dev-key",
       enabled=False
   )
   ```

2. **Testing Environment**:
   ```python
   # Enable with test API key
   client = bt.create_client(
       api_key=os.getenv("BRIEFCASE_TEST_API_KEY"),
       enabled=True,
       endpoint="https://staging.observe.briefcasebrain.io/api/v1/telemetry"
   )
   ```

3. **Production**:
   ```python
   # Full telemetry with production settings
   client = bt.create_client(
       api_key=os.getenv("BRIEFCASE_API_KEY"),
       enabled=True,
       batch_size=200,
       flush_interval_seconds=30
   )
   ```

### **Error Handling Patterns**

```python
import briefcase_ai_telemetry as bt
import logging

logger = logging.getLogger(__name__)

def safe_telemetry_track(event):
    """Track event with error handling"""
    try:
        telemetry_client.track_event(event)
    except Exception as e:
        logger.warning(f"Telemetry failed: {e}")
        # Application continues normally

def critical_path_with_telemetry(func):
    """Decorator for critical path functions"""
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)

            # Track success
            duration = int((time.time() - start_time) * 1000)
            safe_telemetry_track(bt.create_event(
                f"{func.__name__}_success",
                duration_ms=duration,
                level=bt.EventLevel.info()
            ))

            return result

        except Exception as e:
            # Track error
            safe_telemetry_track(bt.create_event(
                f"{func.__name__}_error",
                level=bt.EventLevel.error(),
                error=str(e)
            ))
            raise

    return wrapper

# Usage
@critical_path_with_telemetry
def important_business_function():
    # Your critical business logic
    pass
```

### **Data Privacy Guidelines**

**✅ Safe Data to Track**:
- Performance metrics (response times, throughput)
- Error rates and types
- Feature usage statistics (anonymized)
- System health metrics
- Application version and environment info

**🚫 Data to Avoid**:
- Personal Identifiable Information (PII)
- Financial account numbers or payment info
- Health records or medical information
- Customer passwords or API keys
- Detailed user behavior without consent

**🔄 Data Sanitization Example**:
```python
import re
import briefcase_ai_telemetry as bt

def sanitize_data(data):
    """Remove sensitive information from data"""
    if isinstance(data, str):
        # Remove email addresses
        data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', data)

        # Remove phone numbers
        data = re.sub(r'\b\d{3}-?\d{3}-?\d{4}\b', '[PHONE]', data)

        # Remove credit card numbers
        data = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', data)

    return data

def safe_track_user_action(action, user_data):
    """Track user action with data sanitization"""
    sanitized_data = {
        key: sanitize_data(value) if isinstance(value, str) else value
        for key, value in user_data.items()
    }

    event = bt.create_event(
        f"user_{action}",
        level=bt.EventLevel.info(),
        custom_data=sanitized_data
    )

    client.track_event(event)
```

## 📚 **Additional Resources**

### **Documentation Links**

- **API Reference**: https://observe.briefcasebrain.io/docs/api
- **Dashboard Guide**: https://observe.briefcasebrain.io/docs/dashboard
- **Examples Repository**: https://observe.briefcasebrain.io/docs/examples
- **Beta Program Terms**: [Legal Agreement](./legal/BETA_PARTICIPATION_AGREEMENT.pdf)

### **Community Resources**

- **Slack Channel**: briefcase-beta-users (post-approval access)
- **Office Hours**: Every Friday 2-3 PM PST
- **Newsletter**: Monthly product updates and tips
- **Feature Requests**: beta-feedback@briefcasebrain.com

### **Training Resources**

**Video Tutorials**: Available in dashboard after login
**Webinar Series**: Monthly technical deep-dives
**Documentation Workshops**: Quarterly live sessions

## ⚠️ **Emergency Procedures**

### **Critical Production Issues**

**Contact**: emergency@briefcasebrain.com
**Phone**: +1-555-BRIEFCASE (24/7 hotline for critical issues)

**When to Use Emergency Contact**:
- Production system down due to SDK
- Data privacy breach or exposure
- Security vulnerability discovered
- Legal compliance issues

**Information to Include**:
- Severity level (P0-Critical, P1-High, P2-Medium, P3-Low)
- Production impact description
- Timeline of events
- Current workarounds implemented
- Contact information for immediate response

### **Escalation Matrix**

| Issue Type | Primary Contact | Escalation |
|------------|----------------|------------|
| Technical | engineering@briefcasebrain.com | emergency@briefcasebrain.com |
| Legal | legal@briefcasebrain.com | business@briefcasebrain.com |
| Business | business@briefcasebrain.com | Executive team |
| Security | security@briefcasebrain.com | emergency@briefcasebrain.com |

---

## 📧 **Next Steps**

1. **Save Support Contacts**: Add key emails to your organization's support system
2. **Test Integration**: Use health check script to validate setup
3. **Join Community**: Access Slack channel for peer support
4. **Schedule Office Hours**: Join weekly sessions for direct access to engineering team
5. **Monitor Performance**: Set up monitoring for SDK performance impact

**Remember**: As a beta participant, you have direct access to our engineering team. Don't hesitate to reach out with questions, feedback, or suggestions!

**Primary Support**: engineering@briefcasebrain.com