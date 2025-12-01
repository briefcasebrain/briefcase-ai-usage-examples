# Integration Guides

Welcome to the Briefcase AI Telemetry SDK integration guides! This directory contains comprehensive documentation for integrating the SDK with popular AI frameworks and platforms.

## Available Integrations

### 🤖 AI Model Providers

- **[OpenAI](openai.md)** - Complete integration guide for OpenAI's GPT models and API
- **[Anthropic](anthropic.md)** - Integration guide for Claude AI models
- **[Hugging Face](huggingface.md)** - Support for Transformers, Datasets, and model training

### 🔗 AI Frameworks

- **[LangChain](langchain.md)** - Comprehensive LangChain integration for chains, agents, and tools

## Quick Start

Each integration guide provides:

1. **Overview** - What gets tracked automatically
2. **Quick Start** - Get up and running in minutes
3. **Configuration Options** - Detailed configuration parameters
4. **Advanced Usage** - Manual tracking and custom implementations
5. **Best Practices** - Production-ready patterns
6. **Examples** - Real-world use cases and code samples
7. **Troubleshooting** - Common issues and solutions

## Common Setup Pattern

All integrations follow a similar setup pattern:

```python
from briefcase_ai_agent.integrations import {integration_name}_integration

# Configure the integration
{integration_name}_integration.configure(
    api_key="your-briefcase-api-key",
    default_agent_id=101,
    # Integration-specific options...
)

# Enable automatic instrumentation
{integration_name}_integration.enable_instrumentation()

# Your existing code works unchanged!
```

## Framework Comparison

| Integration | Auto Tracking | Cost Tracking | Streaming | Tool Calls | Training |
|-------------|--------------|---------------|-----------|------------|----------|
| OpenAI      | ✅           | ✅            | ✅        | ✅         | ❌       |
| Anthropic   | ✅           | ✅            | ✅        | ✅         | ❌       |
| LangChain   | ✅           | ✅            | ❌        | ✅         | ❌       |
| Hugging Face| ✅           | ❌            | ❌        | ❌         | ✅       |

## Configuration Management

### Environment Variables

All integrations support common environment variables:

```bash
export BRIEFCASE_API_KEY="your-briefcase-api-key"
export BRIEFCASE_AGENT_ID="101"
export ENVIRONMENT="production"  # or "development"
```

### Multi-Framework Setup

You can enable multiple integrations simultaneously:

```python
from briefcase_ai_agent.integrations import (
    openai_integration,
    langchain_integration,
    anthropic_integration
)

# Configure all integrations
for integration in [openai_integration, langchain_integration, anthropic_integration]:
    integration.configure(
        api_key="your-briefcase-api-key",
        default_agent_id=101
    )
    integration.enable_instrumentation()

# Now all frameworks are tracked automatically
```

## Best Practices

### 1. Environment-Based Configuration

```python
import os
from briefcase_ai_agent.integrations import openai_integration

env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    # Production: minimal data capture, high performance
    config = {
        "auto_capture_messages": False,
        "auto_capture_responses": False,
        "auto_calculate_costs": True,
        "sample_rate": 0.1
    }
else:
    # Development: full tracking for debugging
    config = {
        "auto_capture_messages": True,
        "auto_capture_responses": True,
        "auto_calculate_costs": True,
        "sample_rate": 1.0
    }

openai_integration.configure(
    api_key=os.getenv("BRIEFCASE_API_KEY"),
    **config
)
```

### 2. Graceful Error Handling

```python
from briefcase_ai_agent.integrations import openai_integration

try:
    openai_integration.configure(api_key="your-key")
    openai_integration.enable_instrumentation()
    print("✅ Telemetry enabled")
except Exception as e:
    print(f"⚠️ Telemetry failed to initialize: {e}")
    # Application continues without telemetry
```

### 3. Resource Cleanup

```python
import atexit
from briefcase_ai_agent.integrations import openai_integration

def cleanup():
    """Ensure all events are flushed before shutdown."""
    client = openai_integration.get_telemetry_client()
    if client:
        client.flush()

atexit.register(cleanup)
```

### 4. Selective Instrumentation

```python
from briefcase_ai_agent.integrations import openai_integration

# Enable only for specific operations
def sensitive_operation():
    openai_integration.disable_instrumentation()
    # This won't be tracked
    result = openai_client.chat.completions.create(...)
    openai_integration.enable_instrumentation()
    return result

def normal_operation():
    # This will be tracked normally
    return openai_client.chat.completions.create(...)
```

## Web Framework Integration

### FastAPI Example

```python
from fastapi import FastAPI
from briefcase_ai_agent.integrations import openai_integration

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize telemetry on startup
    openai_integration.configure(
        api_key="your-briefcase-key",
        default_agent_id=101
    )
    openai_integration.enable_instrumentation()

@app.on_event("shutdown")
async def shutdown():
    # Flush events on shutdown
    client = openai_integration.get_telemetry_client()
    if client:
        client.flush()

@app.post("/chat")
async def chat_endpoint(message: str):
    # All AI calls in this endpoint are automatically tracked
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return {"response": response.choices[0].message.content}
```

### Django Example

```python
# settings.py
from briefcase_ai_agent.integrations import openai_integration

# Initialize during Django startup
openai_integration.configure(
    api_key="your-briefcase-key",
    default_agent_id=101
)
openai_integration.enable_instrumentation()

# views.py
from django.http import JsonResponse
import openai

def chat_view(request):
    # Automatically tracked
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": request.POST.get("message")}]
    )
    return JsonResponse({"response": response.choices[0].message.content})
```

## Performance Considerations

### High-Volume Applications

For applications with high request volumes:

```python
from briefcase_ai_agent.integrations import openai_integration

openai_integration.configure(
    api_key="your-briefcase-key",
    # Reduce data capture
    auto_capture_messages=False,
    auto_capture_responses=False,
    # Sample only 10% of requests
    sample_rate=0.1,
    # Limit text lengths
    max_message_length=1000,
    max_response_length=1000
)
```

### Memory-Constrained Environments

```python
from briefcase_ai_agent.integrations import openai_integration

openai_integration.configure(
    api_key="your-briefcase-key",
    # Minimal tracking
    auto_capture_messages=False,
    auto_capture_responses=False,
    capture_function_calls=False,
    # Only track costs and basic metrics
    auto_calculate_costs=True
)
```

## Security Considerations

### Sensitive Data Handling

```python
from briefcase_ai_agent.integrations import openai_integration

# Don't capture system prompts in production
openai_integration.configure(
    api_key="your-briefcase-key",
    capture_system_messages=False,  # Avoid capturing sensitive prompts
    auto_capture_messages=False,    # Don't capture user inputs
    auto_capture_responses=False,   # Don't capture AI responses
    auto_calculate_costs=True       # But do track costs
)
```

### API Key Management

```python
import os
from briefcase_ai_agent.integrations import openai_integration

# Never hardcode API keys
api_key = os.getenv("BRIEFCASE_API_KEY")
if not api_key:
    raise ValueError("BRIEFCASE_API_KEY environment variable required")

openai_integration.configure(api_key=api_key)
```

## Testing

### Unit Tests

```python
import pytest
from briefcase_ai_agent.integrations import openai_integration

class TestWithTelemetry:
    def setup_method(self):
        # Enable test mode
        openai_integration.configure(
            api_key="test-key",
            endpoint="http://localhost:8080/test"  # Test endpoint
        )
        openai_integration.enable_instrumentation()

    def teardown_method(self):
        # Clean up
        openai_integration.disable_instrumentation()

    def test_ai_function(self):
        # Your test code here
        result = my_ai_function()
        assert result is not None
```

### Integration Tests

```python
from briefcase_ai_agent.integrations import openai_integration

def test_telemetry_integration():
    """Test that telemetry doesn't break existing functionality."""

    # Enable telemetry
    openai_integration.configure(api_key="test-key")
    openai_integration.enable_instrumentation()

    # Test existing functionality
    result = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )

    # Verify functionality still works
    assert result.choices[0].message.content
    assert len(result.choices[0].message.content) > 0

    # Verify telemetry client is working
    client = openai_integration.get_telemetry_client()
    assert client is not None

    # Cleanup
    openai_integration.disable_instrumentation()
```

## Migration Guide

### From Manual Tracking

If you're currently doing manual tracking:

```python
# OLD: Manual tracking
import time
import logging

def tracked_openai_call(messages):
    start_time = time.time()
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        duration = time.time() - start_time
        logging.info(f"OpenAI call succeeded in {duration:.2f}s")
        return response
    except Exception as e:
        logging.error(f"OpenAI call failed: {e}")
        raise

# NEW: Automatic tracking
from briefcase_ai_agent.integrations import openai_integration

openai_integration.enable_instrumentation()

# Just use OpenAI normally - tracking is automatic
response = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages
)
```

### From Other Telemetry Solutions

Migration is straightforward:

1. Remove existing telemetry code
2. Install Briefcase AI Telemetry SDK
3. Add 2-3 lines of configuration
4. Your existing AI code works unchanged with better tracking

## Support and Community

- 📚 [Main Documentation](../README.md)
- 🐛 [Issue Tracker](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
- 💬 [Discussions](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/discussions)
- 📧 [Email Support](mailto:support@briefcasebrain.com)

## Contributing

We welcome contributions for new integrations! See our [Contributing Guide](../../CONTRIBUTING.md) for details on how to add support for new frameworks.

---

**Need help with a specific integration?** Check the individual guide linked above or reach out to our support team.