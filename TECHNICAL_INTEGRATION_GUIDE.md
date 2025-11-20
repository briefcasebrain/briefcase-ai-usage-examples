# 🔧 Briefcase AI Telemetry SDK - Technical Integration Guide

**Advanced Implementation Guide for Beta Participants**

This guide provides detailed technical instructions for integrating the Briefcase AI Telemetry SDK into your applications.

## 🎯 **Integration Overview**

The Briefcase AI Telemetry SDK provides comprehensive observability for AI applications with:
- **High-performance telemetry** with minimal overhead
- **AI/ML specific features** for model monitoring
- **Advanced drift detection** and analysis capabilities
- **Cost tracking and optimization** for AI models
- **Agent instrumentation** for comprehensive monitoring
- **Compliance checking** for GDPR, SOC2, and FSB regulations

## 🚀 **Quick Start Integration**

### **Basic Setup (5 minutes)**

```python
import briefcase_ai_telemetry as bt
import os

# 1. Initialize client
client = bt.create_client(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    endpoint="https://observe.briefcasebrain.io/api/v1/telemetry",
    enabled=True,
    batch_size=100,
    flush_interval_seconds=30,
    timeout_seconds=10,
    retry_attempts=3
)

# 2. Start background telemetry
client.start_background_flush()

# 3. Track your first event
client.track_event(bt.create_event(
    "application_started",
    level=bt.EventLevel.info(),
    message="Application successfully initialized",
    custom_data={
        "version": "1.0.0",
        "environment": "staging"
    }
))

print("✅ Briefcase AI Telemetry integrated successfully!")
```

### **Framework-Specific Examples**

#### **FastAPI Integration**

```python
from fastapi import FastAPI, HTTPException
import briefcase_ai_telemetry as bt
import time

app = FastAPI()

# Initialize telemetry
telemetry = bt.create_client(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    enabled=True
)
telemetry.start_background_flush()

@app.middleware("http")
async def telemetry_middleware(request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
        duration = int((time.time() - start_time) * 1000)

        # Track successful requests
        telemetry.track_event(bt.create_event(
            "api_request",
            level=bt.EventLevel.info(),
            custom_data={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": duration,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        ))

        return response

    except Exception as e:
        duration = int((time.time() - start_time) * 1000)

        # Track errors
        telemetry.track_event(bt.create_event(
            "api_error",
            level=bt.EventLevel.error(),
            message=str(e),
            error=str(e),
            duration_ms=duration,
            custom_data={
                "method": request.method,
                "path": str(request.url.path),
                "error_type": type(e).__name__
            }
        ))

        raise

@app.on_event("shutdown")
async def shutdown_telemetry():
    telemetry.flush()
```

#### **Flask Integration**

```python
from flask import Flask, request, g
import briefcase_ai_telemetry as bt
import time

app = Flask(__name__)

# Initialize telemetry
telemetry = bt.create_client(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    enabled=True
)
telemetry.start_background_flush()

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = int((time.time() - g.start_time) * 1000)

    telemetry.track_event(bt.create_event(
        "flask_request",
        level=bt.EventLevel.info(),
        custom_data={
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration,
            "remote_addr": request.remote_addr
        }
    ))

    return response

@app.errorhandler(Exception)
def handle_exception(e):
    telemetry.track_event(bt.create_event(
        "flask_error",
        level=bt.EventLevel.error(),
        message=str(e),
        error=str(e),
        custom_data={
            "method": request.method,
            "path": request.path,
            "error_type": type(e).__name__
        }
    ))
    raise
```

#### **Django Integration**

```python
# middleware.py
import briefcase_ai_telemetry as bt
import time
import os

class BriefcaseTelemetryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.telemetry = bt.create_client(
            api_key=os.getenv("BRIEFCASE_API_KEY"),
            enabled=True
        )
        self.telemetry.start_background_flush()

    def __call__(self, request):
        start_time = time.time()

        try:
            response = self.get_response(request)
            duration = int((time.time() - start_time) * 1000)

            self.telemetry.track_event(bt.create_event(
                "django_request",
                level=bt.EventLevel.info(),
                custom_data={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": duration,
                    "user_authenticated": request.user.is_authenticated if hasattr(request, 'user') else False
                }
            ))

            return response

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)

            self.telemetry.track_event(bt.create_event(
                "django_error",
                level=bt.EventLevel.error(),
                message=str(e),
                error=str(e),
                duration_ms=duration,
                custom_data={
                    "method": request.method,
                    "path": request.path,
                    "error_type": type(e).__name__
                }
            ))

            raise

# settings.py
MIDDLEWARE = [
    'your_app.middleware.BriefcaseTelemetryMiddleware',
    # ... other middleware
]
```

## 🤖 **AI/ML Specific Features**

### **Model Performance Tracking**

```python
import briefcase_ai_telemetry as bt

# Initialize client with AI-specific configuration
client = bt.create_client(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    enabled=True
)

def track_model_inference(model_name, input_data, output_data, duration_ms):
    """Track ML model inference with performance metrics"""

    # Basic inference tracking
    client.track_event(bt.create_event(
        "model_inference",
        level=bt.EventLevel.info(),
        duration_ms=duration_ms,
        custom_data={
            "model_name": model_name,
            "input_size": len(str(input_data)),
            "output_size": len(str(output_data)),
            "inference_time": duration_ms
        }
    ))

# Example usage
def predict_with_tracking(model, input_text):
    start_time = time.time()

    try:
        # Your model prediction
        prediction = model.predict(input_text)

        duration = int((time.time() - start_time) * 1000)

        # Track successful prediction
        track_model_inference(
            model_name="sentiment_classifier_v1",
            input_data=input_text,
            output_data=prediction,
            duration_ms=duration
        )

        return prediction

    except Exception as e:
        # Track inference errors
        client.track_event(bt.create_event(
            "model_inference_error",
            level=bt.EventLevel.error(),
            message=f"Model inference failed: {str(e)}",
            error=str(e),
            custom_data={
                "model_name": "sentiment_classifier_v1",
                "input_preview": input_text[:100] if input_text else "None"
            }
        ))
        raise
```

### **Advanced Drift Detection**

```python
import briefcase_ai_telemetry as bt

# Collect model outputs for drift analysis
model_outputs = []

def track_model_output_for_drift(output):
    """Collect outputs for drift analysis"""
    model_outputs.append(output)

    # Analyze drift every 10 predictions
    if len(model_outputs) >= 10:
        analyze_model_drift()
        model_outputs.clear()

def analyze_model_drift():
    """Analyze drift in model outputs"""
    try:
        # Calculate drift metrics
        drift_metrics = bt.calculate_drift(model_outputs)

        # Track drift analysis
        client.track_event(bt.create_event(
            "drift_analysis",
            level=bt.EventLevel.info(),
            custom_data={
                "total_agreement_rate": drift_metrics.total_agreement_rate,
                "normalized_edit_distance": drift_metrics.normalized_edit_distance,
                "consistency_score": drift_metrics.consistency_score,
                "consensus_confidence": drift_metrics.consensus_confidence,
                "factual_drift_count": drift_metrics.factual_drift_count,
                "sample_size": len(model_outputs)
            }
        ))

        # Alert on high drift
        if drift_metrics.consensus_confidence == "low":
            client.track_event(bt.create_event(
                "drift_alert",
                level=bt.EventLevel.warning(),
                message="High model drift detected",
                custom_data={
                    "drift_severity": "high",
                    "consistency_score": drift_metrics.consistency_score,
                    "recommendation": "investigate_model_behavior"
                }
            ))

    except Exception as e:
        client.track_event(bt.create_event(
            "drift_analysis_error",
            level=bt.EventLevel.error(),
            message=f"Drift analysis failed: {str(e)}",
            error=str(e)
        ))
```

### **Cost Tracking for AI Models**

```python
import briefcase_ai_telemetry as bt

def track_ai_costs(model_name, input_text, output_text, tokens_used=None):
    """Track costs for AI model usage"""
    try:
        # Estimate costs
        if tokens_used:
            cost_estimate = bt.estimate_cost(
                model_name=model_name,
                input_text=input_text,
                output_text=output_text,
                input_tokens=tokens_used.get('input', None),
                output_tokens=tokens_used.get('output', None)
            )
        else:
            cost_estimate = bt.estimate_cost(
                model_name=model_name,
                input_text=input_text,
                output_text=output_text
            )

        if cost_estimate:
            # Track cost metrics
            client.track_event(bt.create_event(
                "ai_cost_tracking",
                level=bt.EventLevel.info(),
                custom_data={
                    "model_name": model_name,
                    "total_cost": cost_estimate.total_cost,
                    "input_cost": cost_estimate.input_cost,
                    "output_cost": cost_estimate.output_cost,
                    "input_tokens": cost_estimate.input_tokens,
                    "output_tokens": cost_estimate.output_tokens,
                    "cost_per_input_token": cost_estimate.input_cost_per_token,
                    "cost_per_output_token": cost_estimate.output_cost_per_token
                }
            ))

            # Alert on high costs
            if cost_estimate.total_cost > 0.10:  # Alert if over 10 cents
                client.track_event(bt.create_event(
                    "high_cost_alert",
                    level=bt.EventLevel.warning(),
                    message=f"High cost request: ${cost_estimate.total_cost:.4f}",
                    custom_data={
                        "model_name": model_name,
                        "cost": cost_estimate.total_cost,
                        "tokens_used": cost_estimate.input_tokens + cost_estimate.output_tokens
                    }
                ))

    except Exception as e:
        client.track_event(bt.create_event(
            "cost_tracking_error",
            level=bt.EventLevel.error(),
            message=f"Cost tracking failed: {str(e)}",
            error=str(e)
        ))

# Example usage with OpenAI
def openai_request_with_tracking(prompt, model="gpt-4"):
    import openai

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        output_text = response.choices[0].message.content
        tokens_used = {
            'input': response.usage.prompt_tokens,
            'output': response.usage.completion_tokens
        }

        # Track costs
        track_ai_costs(
            model_name=model,
            input_text=prompt,
            output_text=output_text,
            tokens_used=tokens_used
        )

        return output_text

    except Exception as e:
        client.track_event(bt.create_event(
            "openai_request_error",
            level=bt.EventLevel.error(),
            message=f"OpenAI request failed: {str(e)}",
            error=str(e),
            custom_data={"model": model, "prompt_preview": prompt[:100]}
        ))
        raise
```

### **Agent Instrumentation**

```python
import briefcase_ai_telemetry as bt

# Advanced agent monitoring
def create_agent_monitor(agent_id, agent_name):
    """Create comprehensive agent monitoring"""

    # Create instrumentation configuration
    config = bt.InstrumentationConfig()
    config.with_consensus_mode(True, runs=3, threshold=0.8)
    config.with_sensitive_data_sanitization(True)
    config.with_input_output_truncation(True, max_length=1000)

    # Create agent instrument
    instrument = bt.create_agent_instrument(
        agent_id=agent_id,
        client=client,
        config=config
    )

    return instrument

# Example agent implementation
class AIAgent:
    def __init__(self, agent_id, name):
        self.agent_id = agent_id
        self.name = name
        self.monitor = create_agent_monitor(agent_id, name)

    def execute_task(self, task_input):
        """Execute task with comprehensive monitoring"""

        # Start monitoring session
        session = self.monitor.start()

        try:
            # Step 1: Analyze input
            session.add_reasoning_step("Analyzing user input and intent")
            analysis_result = self._analyze_input(task_input)

            # Step 2: Tool usage
            session.add_tool_call("database", {"query": "SELECT relevant_data"})
            data = self._query_database(analysis_result)

            # Step 3: Generate response
            session.add_reasoning_step("Generating response based on analysis and data")
            response = self._generate_response(data)

            # Set session metadata
            session.set_input_output(task_input, response)
            session.set_accuracy(0.95)
            session.set_model_info("gpt-4", "OpenAI")
            session.set_token_usage(150, 89)

            # Finish successful session
            session.finish()

            return response

        except Exception as e:
            # Track errors in agent execution
            session.set_error(str(e))
            session.finish()

            client.track_event(bt.create_event(
                "agent_execution_error",
                level=bt.EventLevel.error(),
                message=f"Agent {self.name} failed: {str(e)}",
                error=str(e),
                custom_data={
                    "agent_id": self.agent_id,
                    "agent_name": self.name,
                    "task_type": "general_execution"
                }
            ))

            raise

    def _analyze_input(self, input_text):
        # Your input analysis logic
        return {"intent": "information_request", "entities": ["user", "data"]}

    def _query_database(self, analysis):
        # Your database query logic
        return {"results": ["relevant", "data", "items"]}

    def _generate_response(self, data):
        # Your response generation logic
        return "Based on the data, here's your answer..."

# Usage
agent = AIAgent(agent_id=123, name="CustomerServiceAgent")
result = agent.execute_task("What's my account balance?")
```

## 🔧 **Advanced Configuration**

### **Performance Optimization**

```python
# High-throughput configuration
client = bt.create_client(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    enabled=True,

    # Batching settings
    batch_size=500,           # Larger batches for high volume
    flush_interval_seconds=10, # More frequent flushes

    # Network settings
    timeout_seconds=30,       # Longer timeout for large batches
    retry_attempts=5,         # More retries for reliability

    # Performance settings
    compression_enabled=True,  # Reduce bandwidth usage
    async_mode=True           # Non-blocking telemetry
)

# Custom session configuration
session_config = bt.Session()
session_config.with_user_id("anonymous")  # Don't track individual users
session_config.add_metadata("service", "api-gateway")
session_config.add_metadata("version", "2.1.0")
client.with_session(session_config)
```

### **Error Handling & Resilience**

```python
import briefcase_ai_telemetry as bt
import logging

class ResilientTelemetryClient:
    def __init__(self, api_key):
        self.primary_client = bt.create_client(
            api_key=api_key,
            enabled=True,
            timeout_seconds=5,
            retry_attempts=2
        )

        self.fallback_client = bt.create_client(
            api_key="fallback-key",
            enabled=False,  # Local only fallback
            endpoint="http://localhost:8080/telemetry"
        )

        self.logger = logging.getLogger(__name__)

    def track_event(self, event):
        """Track event with fallback handling"""
        try:
            self.primary_client.track_event(event)
        except Exception as primary_error:
            self.logger.warning(f"Primary telemetry failed: {primary_error}")

            try:
                self.fallback_client.track_event(event)
            except Exception as fallback_error:
                self.logger.error(f"Both telemetry clients failed: {fallback_error}")
                # Continue application execution without telemetry

    def flush(self):
        """Flush both clients"""
        try:
            self.primary_client.flush()
        except Exception as e:
            self.logger.warning(f"Primary flush failed: {e}")

        try:
            self.fallback_client.flush()
        except Exception as e:
            self.logger.warning(f"Fallback flush failed: {e}")

# Usage
resilient_telemetry = ResilientTelemetryClient(os.getenv("BRIEFCASE_API_KEY"))
```

### **Environment-Specific Configuration**

```python
import os
import briefcase_ai_telemetry as bt

def create_environment_client():
    """Create telemetry client based on environment"""

    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return bt.create_client(
            api_key=os.getenv("BRIEFCASE_API_KEY"),
            enabled=True,
            batch_size=200,
            flush_interval_seconds=30,
            endpoint="https://observe.briefcasebrain.io/api/v1/telemetry"
        )

    elif env == "staging":
        return bt.create_client(
            api_key=os.getenv("BRIEFCASE_API_KEY_STAGING"),
            enabled=True,
            batch_size=50,
            flush_interval_seconds=10,
            endpoint="https://staging.observe.briefcasebrain.io/api/v1/telemetry"
        )

    else:  # development
        return bt.create_client(
            api_key="dev-key",
            enabled=False,  # Disabled in development
            endpoint="http://localhost:8080/telemetry"
        )

# Global client instance
telemetry = create_environment_client()
```

## 📊 **Testing & Validation**

### **Unit Testing with Telemetry**

```python
import unittest
import briefcase_ai_telemetry as bt
from unittest.mock import Mock, patch

class TestTelemetryIntegration(unittest.TestCase):

    def setUp(self):
        """Set up test client"""
        self.client = bt.create_client(
            api_key="test-key",
            enabled=False  # Disabled for testing
        )

    def test_event_creation(self):
        """Test basic event creation"""
        event = bt.create_event(
            "test_event",
            level=bt.EventLevel.info(),
            message="Test message",
            custom_data={"key": "value"}
        )

        self.assertEqual(event.name, "test_event")
        self.assertEqual(event.message, "Test message")
        self.assertIsNotNone(event.id)
        self.assertIsNotNone(event.timestamp)

    def test_client_tracking(self):
        """Test event tracking"""
        event = bt.create_event("test_tracking")

        # This should not raise any exceptions
        self.client.track_event(event)
        self.client.flush()

    @patch('briefcase_ai_telemetry.TelemetryClient')
    def test_error_handling(self, mock_client):
        """Test error handling in telemetry"""
        mock_client.track_event.side_effect = Exception("Network error")

        # Your application should handle telemetry errors gracefully
        try:
            self.client.track_event(bt.create_event("test"))
        except Exception:
            self.fail("Telemetry errors should be handled gracefully")

class TestDriftDetection(unittest.TestCase):

    def test_drift_calculation(self):
        """Test drift detection functionality"""
        outputs = [
            "The weather is sunny today.",
            "Today the weather is sunny.",
            "It's sunny weather today."
        ]

        metrics = bt.calculate_drift(outputs)

        self.assertGreater(metrics.consistency_score, 50)
        self.assertIn(metrics.consensus_confidence, ["high", "medium", "low"])
        self.assertGreaterEqual(metrics.total_agreement_rate, 0)
        self.assertLessEqual(metrics.total_agreement_rate, 100)

if __name__ == "__main__":
    unittest.main()
```

### **Integration Testing**

```python
import briefcase_ai_telemetry as bt
import time
import os

def integration_test_suite():
    """Comprehensive integration test"""

    print("🧪 Starting Briefcase AI Telemetry Integration Tests...")

    # Test 1: Client initialization
    print("📋 Test 1: Client Initialization")
    try:
        client = bt.create_client(
            api_key=os.getenv("BRIEFCASE_API_KEY_TEST", "test-key"),
            enabled=True,
            timeout_seconds=5
        )
        print("  ✅ Client initialized successfully")
    except Exception as e:
        print(f"  ❌ Client initialization failed: {e}")
        return

    # Test 2: Basic event tracking
    print("📋 Test 2: Basic Event Tracking")
    try:
        event = bt.create_event(
            "integration_test",
            level=bt.EventLevel.info(),
            message="Integration test event",
            custom_data={"test_run": str(int(time.time()))}
        )
        client.track_event(event)
        print("  ✅ Event tracking successful")
    except Exception as e:
        print(f"  ❌ Event tracking failed: {e}")

    # Test 3: Drift detection
    print("📋 Test 3: Drift Detection")
    try:
        test_outputs = [
            "Test output one",
            "Test output two",
            "Test output three"
        ]
        metrics = bt.calculate_drift(test_outputs)
        print(f"  ✅ Drift detection successful (confidence: {metrics.consensus_confidence})")
    except Exception as e:
        print(f"  ❌ Drift detection failed: {e}")

    # Test 4: Cost estimation
    print("📋 Test 4: Cost Estimation")
    try:
        cost = bt.estimate_cost("gpt-4", "test input", "test output")
        if cost:
            print(f"  ✅ Cost estimation successful (${cost.total_cost:.6f})")
        else:
            print("  ⚠️ Cost estimation returned None (model not found)")
    except Exception as e:
        print(f"  ❌ Cost estimation failed: {e}")

    # Test 5: Agent instrumentation
    print("📋 Test 5: Agent Instrumentation")
    try:
        instrument = bt.create_agent_instrument(999, client)
        session = instrument.start()
        session.set_input_output("test input", "test output")
        session.finish()
        print("  ✅ Agent instrumentation successful")
    except Exception as e:
        print(f"  ❌ Agent instrumentation failed: {e}")

    # Test 6: Flush and cleanup
    print("📋 Test 6: Flush and Cleanup")
    try:
        client.flush()
        print("  ✅ Flush successful")
    except Exception as e:
        print(f"  ❌ Flush failed: {e}")

    print("🎉 Integration test suite completed!")

if __name__ == "__main__":
    integration_test_suite()
```

## 🚨 **Common Issues & Troubleshooting**

### **Authentication Issues**

```python
# Debug authentication problems
import briefcase_ai_telemetry as bt
import os

def debug_authentication():
    api_key = os.getenv("BRIEFCASE_API_KEY")

    if not api_key:
        print("❌ BRIEFCASE_API_KEY environment variable not set")
        return

    if len(api_key) < 20:
        print("❌ API key appears to be too short")
        return

    try:
        client = bt.create_client(
            api_key=api_key,
            enabled=True,
            timeout_seconds=5
        )

        # Test connection with a simple event
        test_event = bt.create_event("auth_test", level=bt.EventLevel.info())
        client.track_event(test_event)
        client.flush()

        print("✅ Authentication successful")

    except Exception as e:
        print(f"❌ Authentication failed: {e}")

        if "401" in str(e):
            print("💡 Check your API key is correct")
        elif "403" in str(e):
            print("💡 API key may not have required permissions")
        elif "timeout" in str(e).lower():
            print("💡 Network connectivity issue")
        else:
            print("💡 Check network connectivity and firewall settings")

debug_authentication()
```

### **Performance Issues**

```python
# Monitor telemetry performance impact
import briefcase_ai_telemetry as bt
import time
import psutil
import os

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.start_memory = None

    def __enter__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        duration = (end_time - self.start_time) * 1000
        memory_delta = end_memory - self.start_memory

        print(f"⏱️ Duration: {duration:.2f}ms")
        print(f"💾 Memory delta: {memory_delta / 1024 / 1024:.2f}MB")

def benchmark_telemetry():
    client = bt.create_client(
        api_key=os.getenv("BRIEFCASE_API_KEY", "test"),
        enabled=False  # Disable network for pure SDK benchmarking
    )

    # Benchmark event creation
    print("📊 Benchmarking event creation...")
    with PerformanceMonitor():
        for i in range(1000):
            event = bt.create_event(f"benchmark_event_{i}")
            client.track_event(event)

    # Benchmark batch flush
    print("📊 Benchmarking batch flush...")
    with PerformanceMonitor():
        client.flush()

if __name__ == "__main__":
    benchmark_telemetry()
```

### **Network Connectivity**

```python
import requests
import briefcase_ai_telemetry as bt

def test_connectivity():
    """Test network connectivity to Briefcase AI services"""

    endpoints = [
        "https://observe.briefcasebrain.io/health",
        "https://pypi.briefcasebrain.com/health",
        "https://observe.briefcasebrain.io/api/v1/telemetry"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"⚠️ {endpoint} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - {e}")

test_connectivity()
```

## 📈 **Best Practices**

### **Production Checklist**

- ✅ **API Key Security**: Store in environment variables, never in code
- ✅ **Error Handling**: Graceful degradation when telemetry fails
- ✅ **Data Sensitivity**: No PII, financial, or health data without DPA
- ✅ **Performance**: Monitor telemetry overhead in production
- ✅ **Batching**: Use appropriate batch sizes for your volume
- ✅ **Monitoring**: Track telemetry client health and errors
- ✅ **Compliance**: Follow beta agreement terms strictly

### **Development Workflow**

1. **Local Development**: Disable telemetry (`enabled=False`)
2. **Staging**: Enable with test API key and staging endpoint
3. **Production**: Full telemetry with production API key
4. **Monitoring**: Track both your app and telemetry health

---

For technical support: **engineering@briefcasebrain.com**

**Next**: [Client Support Documentation](./CLIENT_SUPPORT_GUIDE.md)