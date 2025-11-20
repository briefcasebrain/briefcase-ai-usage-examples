# OpenAI Integration Guide

This guide provides comprehensive information on integrating Briefcase AI Telemetry SDK with OpenAI applications.

## Overview

The OpenAI integration automatically instruments OpenAI API calls to capture:

- Chat completion requests and responses
- Token usage and cost tracking
- Model performance metrics
- Error tracking and debugging information
- Function/tool calls and responses

## Quick Start

### Basic Setup

```python
import openai
from briefcase_ai_agent.integrations import openai_integration

# Configure and enable automatic instrumentation
openai_integration.configure(
    api_key="your-briefcase-api-key",
    default_agent_id=101,
    auto_capture_messages=True,
    auto_capture_responses=True,
    auto_calculate_costs=True
)

# Enable instrumentation
openai_integration.enable_instrumentation()

# Your existing OpenAI code works unchanged
client = openai.OpenAI(api_key="your-openai-api-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how can you help me?"}
    ]
)

print(response.choices[0].message.content)
```

### Environment Variables

Set these environment variables for easier configuration:

```bash
export BRIEFCASE_API_KEY="your-briefcase-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export BRIEFCASE_AGENT_ID="101"
```

Then use simplified setup:

```python
from briefcase_ai_agent.integrations import openai_integration

# Auto-configure from environment variables
openai_integration.auto_configure()
openai_integration.enable_instrumentation()
```

## Configuration Options

### InstrumentationConfig

```python
from briefcase_ai_agent.integrations.openai_integration import OpenAIInstrumentationConfig

config = OpenAIInstrumentationConfig(
    auto_capture_messages=True,      # Capture input messages
    auto_capture_responses=True,     # Capture response content
    auto_calculate_costs=True,       # Track API costs
    capture_function_calls=True,     # Track function/tool calls
    capture_system_messages=False,   # Include system messages
    default_agent_id=101,           # Default agent ID for tracking
    enabled=True,                   # Enable/disable instrumentation
    api_key="your-briefcase-key",   # Briefcase API key
    endpoint=None                   # Custom endpoint (optional)
)

openai_integration.configure_from_object(config)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_capture_messages` | bool | True | Automatically capture input messages |
| `auto_capture_responses` | bool | True | Automatically capture response content |
| `auto_calculate_costs` | bool | True | Calculate and track API costs |
| `capture_function_calls` | bool | True | Track function/tool calls |
| `capture_system_messages` | bool | False | Include system messages in tracking |
| `default_agent_id` | int | None | Default agent ID for events |
| `enabled` | bool | True | Enable/disable instrumentation |
| `api_key` | str | None | Briefcase AI API key |
| `endpoint` | str | None | Custom Briefcase endpoint |

## Advanced Usage

### Manual Event Tracking

For fine-grained control, you can manually track events:

```python
import openai
from briefcase_ai_agent.integrations import openai_integration
import briefcase_ai_telemetry as bai

# Setup
openai_integration.configure(api_key="your-briefcase-key")
client = openai.OpenAI(api_key="your-openai-api-key")

# Manual event tracking
start_time = time.time()

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Explain quantum computing"}],
        temperature=0.7,
        max_tokens=500
    )

    # Track successful completion
    event = bai.EventBuilder("openai_chat_completion")
        .level(bai.EventLevel.info())
        .agent_id(101)
        .duration_ms(int((time.time() - start_time) * 1000))
        .tag("model", "gpt-4")
        .tag("status", "success")
        .custom_data("prompt_tokens", response.usage.prompt_tokens)
        .custom_data("completion_tokens", response.usage.completion_tokens)
        .custom_data("total_tokens", response.usage.total_tokens)
        .custom_data("temperature", 0.7)
        .custom_data("max_tokens", 500)
        .build()

    openai_integration.get_telemetry_client().track_event(event)

except Exception as e:
    # Track errors
    error_event = bai.EventBuilder("openai_chat_error")
        .level(bai.EventLevel.error())
        .agent_id(101)
        .error(str(e))
        .tag("model", "gpt-4")
        .tag("status", "error")
        .build()

    openai_integration.get_telemetry_client().track_event(error_event)
    raise
```

### Function Calling Integration

Track function/tool calls automatically:

```python
import openai
from briefcase_ai_agent.integrations import openai_integration

openai_integration.configure(
    api_key="your-briefcase-key",
    capture_function_calls=True
)
openai_integration.enable_instrumentation()

client = openai.OpenAI()

# Define function
functions = [
    {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
]

# This call will be automatically tracked including function calls
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in New York?"}],
    functions=functions,
    function_call="auto"
)
```

### Cost Tracking

Automatic cost calculation for all supported models:

```python
from briefcase_ai_agent.integrations import openai_integration
import briefcase_ai_telemetry as bai

openai_integration.configure(
    api_key="your-briefcase-key",
    auto_calculate_costs=True
)

# Cost data is automatically tracked in events
# Access cost calculator directly if needed
cost_calc = bai.CostCalculator()

# Calculate costs for specific usage
cost = cost_calc.calculate_openai_cost(
    model="gpt-4",
    prompt_tokens=100,
    completion_tokens=50
)

print(f"Estimated cost: ${cost:.4f}")
```

## Streaming Support

The integration automatically handles streaming responses:

```python
import openai
from briefcase_ai_agent.integrations import openai_integration

openai_integration.enable_instrumentation()
client = openai.OpenAI()

# Streaming is automatically tracked
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## Best Practices

### 1. Environment-Based Configuration

Use different configurations for different environments:

```python
import os
from briefcase_ai_agent.integrations import openai_integration

# Production configuration
if os.getenv("ENVIRONMENT") == "production":
    openai_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY"),
        capture_system_messages=False,  # Don't capture system prompts in prod
        auto_capture_responses=True,    # But do capture responses for debugging
        endpoint="https://observe.briefcasebrain.io/api/v1/telemetry"
    )
else:
    # Development configuration
    openai_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY_DEV"),
        capture_system_messages=True,   # Capture everything in dev
        endpoint="https://api-dev.briefcase.ai/telemetry"
    )
```

### 2. Error Handling

Always handle potential instrumentation errors:

```python
try:
    openai_integration.enable_instrumentation()
except Exception as e:
    print(f"Failed to enable instrumentation: {e}")
    # Continue without instrumentation rather than failing
```

### 3. Resource Management

Properly clean up when shutting down:

```python
import atexit
from briefcase_ai_agent.integrations import openai_integration

def cleanup():
    client = openai_integration.get_telemetry_client()
    if client:
        client.flush()  # Ensure all events are sent

atexit.register(cleanup)
```

### 4. Selective Instrumentation

Enable instrumentation only for specific parts of your application:

```python
from briefcase_ai_agent.integrations import openai_integration

# Enable only for specific operations
openai_integration.enable_instrumentation()

# Your instrumented operations
result = some_openai_operation()

# Disable for operations you don't want tracked
openai_integration.disable_instrumentation()

# This won't be tracked
internal_operation()

# Re-enable if needed
openai_integration.enable_instrumentation()
```

## Troubleshooting

### Common Issues

1. **Events not appearing**: Check your API key and network connectivity
2. **High memory usage**: Disable `auto_capture_responses` for large responses
3. **Performance impact**: Use `capture_system_messages=False` in production

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
from briefcase_ai_agent.integrations import openai_integration

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("briefcase_ai_agent.integrations.openai_integration")
logger.setLevel(logging.DEBUG)

openai_integration.enable_instrumentation()
```

### Health Check

Verify integration is working correctly:

```python
from briefcase_ai_agent.integrations import openai_integration

# Check if instrumentation is active
if openai_integration.is_instrumentation_enabled():
    print("✅ OpenAI instrumentation is active")
else:
    print("❌ OpenAI instrumentation is not active")

# Check telemetry client
client = openai_integration.get_telemetry_client()
if client:
    print("✅ Telemetry client is available")
else:
    print("❌ Telemetry client is not configured")
```

## Examples

### Basic Chat Application

```python
import openai
from briefcase_ai_agent.integrations import openai_integration

# Setup
openai_integration.configure(
    api_key="your-briefcase-key",
    default_agent_id=101
)
openai_integration.enable_instrumentation()

client = openai.OpenAI(api_key="your-openai-key")

def chat_with_gpt(user_message: str) -> str:
    """Simple chat function - automatically instrumented."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

# Usage
response = chat_with_gpt("Hello, how are you?")
print(response)
```

### Batch Processing

```python
import openai
from briefcase_ai_agent.integrations import openai_integration
import asyncio

openai_integration.configure(api_key="your-briefcase-key")
openai_integration.enable_instrumentation()

client = openai.AsyncOpenAI(api_key="your-openai-key")

async def process_batch(messages: list[str]) -> list[str]:
    """Process multiple messages - each call is tracked."""
    tasks = []

    for msg in messages:
        task = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": msg}]
        )
        tasks.append(task)

    responses = await asyncio.gather(*tasks)
    return [r.choices[0].message.content for r in responses]

# Usage
messages = ["Hello", "How are you?", "What's the weather?"]
responses = asyncio.run(process_batch(messages))
```

## Integration with Other Services

### Combine with LangChain

```python
from langchain.llms import OpenAI
from briefcase_ai_agent.integrations import openai_integration, langchain_integration

# Enable both integrations
openai_integration.configure(api_key="your-briefcase-key", default_agent_id=101)
langchain_integration.configure(api_key="your-briefcase-key", default_agent_id=102)

openai_integration.enable_instrumentation()
langchain_integration.enable_instrumentation()

# Both OpenAI direct calls and LangChain usage will be tracked
llm = OpenAI(openai_api_key="your-openai-key")
result = llm("Tell me about artificial intelligence")
```

### Web Framework Integration (FastAPI)

```python
from fastapi import FastAPI
from briefcase_ai_agent.integrations import openai_integration
import openai

app = FastAPI()

# Setup instrumentation on startup
@app.on_event("startup")
async def startup():
    openai_integration.configure(api_key="your-briefcase-key")
    openai_integration.enable_instrumentation()

@app.post("/chat")
async def chat_endpoint(message: str):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return {"response": response.choices[0].message.content}

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown():
    client = openai_integration.get_telemetry_client()
    if client:
        client.flush()
```

## Migration from Other Telemetry Solutions

### From OpenAI's Built-in Logging

```python
# Old approach
import openai
openai.log = "debug"  # Built-in logging

# New approach with Briefcase
from briefcase_ai_agent.integrations import openai_integration

openai_integration.configure(api_key="your-briefcase-key")
openai_integration.enable_instrumentation()
# All your existing code works unchanged
```

### From Custom Instrumentation

```python
# Old custom instrumentation
def tracked_openai_call(model, messages):
    start_time = time.time()
    try:
        response = openai.ChatCompletion.create(model=model, messages=messages)
        # Custom tracking code...
        return response
    except Exception as e:
        # Custom error tracking...
        raise

# New automatic instrumentation
from briefcase_ai_agent.integrations import openai_integration

openai_integration.enable_instrumentation()

# Just use OpenAI normally - tracking is automatic
response = client.chat.completions.create(model=model, messages=messages)
```

This integration provides comprehensive tracking of your OpenAI usage with minimal changes to your existing code.