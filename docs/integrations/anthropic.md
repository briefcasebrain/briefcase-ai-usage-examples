# Anthropic Integration Guide

This guide provides comprehensive information on integrating Briefcase AI Telemetry SDK with Anthropic's Claude API.

## Overview

The Anthropic integration automatically instruments Claude API calls to capture:

- Chat completion requests and responses
- Token usage and cost tracking
- Model performance metrics
- Streaming response handling
- Error tracking and debugging information
- Tool/function usage (when using Claude's function calling)
- System prompt and conversation tracking

## Quick Start

### Basic Setup

```python
import anthropic
from briefcase_ai_agent.integrations import anthropic_integration

# Configure and enable automatic instrumentation
anthropic_integration.configure(
    api_key="your-briefcase-api-key",
    default_agent_id=301,
    auto_capture_messages=True,
    auto_capture_responses=True,
    auto_calculate_costs=True
)

# Enable instrumentation
anthropic_integration.enable_instrumentation()

# Your existing Anthropic code works unchanged
client = anthropic.Anthropic(api_key="your-anthropic-api-key")

response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello, how can you help me today?"}
    ]
)

print(response.content[0].text)
```

### Environment Variables

Set these environment variables for easier configuration:

```bash
export BRIEFCASE_API_KEY="your-briefcase-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export BRIEFCASE_AGENT_ID="301"
```

Then use simplified setup:

```python
from briefcase_ai_agent.integrations import anthropic_integration

# Auto-configure from environment variables
anthropic_integration.auto_configure()
anthropic_integration.enable_instrumentation()
```

## Configuration Options

### InstrumentationConfig

```python
from briefcase_ai_agent.integrations.anthropic_integration import AnthropicInstrumentationConfig

config = AnthropicInstrumentationConfig(
    auto_capture_messages=True,      # Capture input messages
    auto_capture_responses=True,     # Capture response content
    auto_calculate_costs=True,       # Track API costs
    capture_system_prompts=True,     # Track system prompts
    capture_tool_calls=True,         # Track function/tool calls
    capture_streaming=True,          # Track streaming responses
    default_agent_id=301,           # Default agent ID for tracking
    enabled=True,                   # Enable/disable instrumentation
    api_key="your-briefcase-key",   # Briefcase API key
    endpoint=None,                  # Custom endpoint (optional)
    max_message_length=10000,       # Max message content length
    max_response_length=10000       # Max response content length
)

anthropic_integration.configure_from_object(config)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_capture_messages` | bool | True | Automatically capture input messages |
| `auto_capture_responses` | bool | True | Automatically capture response content |
| `auto_calculate_costs` | bool | True | Calculate and track API costs |
| `capture_system_prompts` | bool | True | Include system prompts in tracking |
| `capture_tool_calls` | bool | True | Track function/tool calls |
| `capture_streaming` | bool | True | Track streaming responses |
| `default_agent_id` | int | None | Default agent ID for events |
| `enabled` | bool | True | Enable/disable instrumentation |
| `max_message_length` | int | 10000 | Maximum message content length |
| `max_response_length` | int | 10000 | Maximum response content length |

## Advanced Usage

### Manual Event Tracking

```python
import anthropic
from briefcase_ai_agent.integrations import anthropic_integration
import briefcase_ai_telemetry as bai
import time

# Setup
anthropic_integration.configure(api_key="your-briefcase-key")
client = anthropic.Anthropic()

# Manual event tracking
start_time = time.time()

try:
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0.7,
        system="You are a helpful AI assistant.",
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms"}
        ]
    )

    # Track successful completion
    event = bai.EventBuilder("anthropic_message_completion")
        .level(bai.EventLevel.info())
        .agent_id(301)
        .duration_ms(int((time.time() - start_time) * 1000))
        .tag("model", "claude-3-sonnet-20240229")
        .tag("status", "success")
        .custom_data("input_tokens", response.usage.input_tokens)
        .custom_data("output_tokens", response.usage.output_tokens)
        .custom_data("total_tokens", response.usage.input_tokens + response.usage.output_tokens)
        .custom_data("temperature", 0.7)
        .custom_data("max_tokens", 1000)
        .build()

    anthropic_integration.get_telemetry_client().track_event(event)

except Exception as e:
    # Track errors
    error_event = bai.EventBuilder("anthropic_message_error")
        .level(bai.EventLevel.error())
        .agent_id(301)
        .error(str(e))
        .tag("model", "claude-3-sonnet-20240229")
        .tag("status", "error")
        .build()

    anthropic_integration.get_telemetry_client().track_event(error_event)
    raise
```

### Streaming Support

The integration automatically handles streaming responses:

```python
import anthropic
from briefcase_ai_agent.integrations import anthropic_integration

anthropic_integration.enable_instrumentation()
client = anthropic.Anthropic()

# Streaming is automatically tracked
stream = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for event in stream:
    if event.type == "content_block_delta":
        print(event.delta.text, end="")
```

### Tool/Function Calling

Track Claude's function calling capabilities:

```python
import anthropic
from briefcase_ai_agent.integrations import anthropic_integration

anthropic_integration.configure(
    api_key="your-briefcase-key",
    capture_tool_calls=True
)
anthropic_integration.enable_instrumentation()

client = anthropic.Anthropic()

# Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
]

# This call will be automatically tracked including tool usage
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ]
)

# Process tool calls if any
for content in response.content:
    if content.type == "tool_use":
        print(f"Tool used: {content.name}")
        print(f"Arguments: {content.input}")
```

### Cost Tracking

Automatic cost calculation for all Claude models:

```python
from briefcase_ai_agent.integrations import anthropic_integration
import briefcase_ai_telemetry as bai

anthropic_integration.configure(
    api_key="your-briefcase-key",
    auto_calculate_costs=True
)

# Cost data is automatically tracked in events
# Access cost calculator directly if needed
cost_calc = bai.CostCalculator()

# Calculate costs for specific usage
cost = cost_calc.calculate_anthropic_cost(
    model="claude-3-opus-20240229",
    input_tokens=100,
    output_tokens=50
)

print(f"Estimated cost: ${cost:.4f}")
```

## Model Support

The integration supports all Claude models:

### Current Models

```python
# Claude 3 models
models = [
    "claude-3-opus-20240229",      # Most capable, highest cost
    "claude-3-sonnet-20240229",    # Balanced performance and speed
    "claude-3-haiku-20240307",     # Fastest, most affordable
]

# Legacy models (if still available)
legacy_models = [
    "claude-2.1",
    "claude-2.0",
    "claude-instant-1.2"
]

# All models are automatically supported
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-opus-20240229",  # Automatically tracked
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Best Practices

### 1. Environment-Based Configuration

```python
import os
from briefcase_ai_agent.integrations import anthropic_integration

# Production configuration
if os.getenv("ENVIRONMENT") == "production":
    anthropic_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY"),
        capture_system_prompts=False,   # Don't capture system prompts in prod
        auto_capture_responses=True,    # But do capture responses for debugging
        max_message_length=5000,        # Limit data size
        max_response_length=5000,
        endpoint="https://observe.briefcasebrain.io/api/v1/telemetry"
    )
else:
    # Development configuration
    anthropic_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY_DEV"),
        capture_system_prompts=True,    # Capture everything in dev
        endpoint="https://telemetry.briefcasebrain.com/api"
    )
```

### 2. Error Handling

```python
try:
    anthropic_integration.enable_instrumentation()
except Exception as e:
    print(f"Failed to enable instrumentation: {e}")
    # Continue without instrumentation rather than failing
```

### 3. Resource Management

```python
import atexit
from briefcase_ai_agent.integrations import anthropic_integration

def cleanup():
    client = anthropic_integration.get_telemetry_client()
    if client:
        client.flush()  # Ensure all events are sent

atexit.register(cleanup)
```

### 4. Conversation Tracking

Track multi-turn conversations:

```python
import anthropic
from briefcase_ai_agent.integrations import anthropic_integration
import briefcase_ai_telemetry as bai

anthropic_integration.enable_instrumentation()

class ConversationTracker:
    def __init__(self, client, agent_id=301):
        self.client = client
        self.agent_id = agent_id
        self.conversation_id = bai.generate_uuid()
        self.message_count = 0

    def send_message(self, messages, **kwargs):
        self.message_count += 1

        # Add conversation context to tracking
        response = self.client.messages.create(
            messages=messages,
            **kwargs
        )

        # Track conversation metadata
        conv_event = bai.EventBuilder("anthropic_conversation_turn")
            .level(bai.EventLevel.info())
            .agent_id(self.agent_id)
            .tag("conversation_id", self.conversation_id)
            .custom_data("turn_number", self.message_count)
            .custom_data("total_turns", self.message_count)
            .build()

        anthropic_integration.get_telemetry_client().track_event(conv_event)
        return response

# Usage
client = anthropic.Anthropic()
conversation = ConversationTracker(client)

# Each message is tracked with conversation context
response1 = conversation.send_message([
    {"role": "user", "content": "Hello"}
], model="claude-3-sonnet-20240229", max_tokens=1000)

response2 = conversation.send_message([
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": response1.content[0].text},
    {"role": "user", "content": "Tell me more"}
], model="claude-3-sonnet-20240229", max_tokens=1000)
```

## Integration Examples

### Web Application with FastAPI

```python
from fastapi import FastAPI, HTTPException
from briefcase_ai_agent.integrations import anthropic_integration
import anthropic

app = FastAPI()

@app.on_event("startup")
async def startup():
    anthropic_integration.configure(api_key="your-briefcase-key")
    anthropic_integration.enable_instrumentation()

@app.post("/chat")
async def chat_endpoint(message: str, model: str = "claude-3-haiku-20240307"):
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": message}]
        )
        return {"response": response.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown():
    client = anthropic_integration.get_telemetry_client()
    if client:
        client.flush()
```

### Batch Processing

```python
import anthropic
from briefcase_ai_agent.integrations import anthropic_integration
import asyncio

anthropic_integration.enable_instrumentation()

async def process_batch(messages: list, model: str = "claude-3-haiku-20240307"):
    """Process multiple messages - each call is tracked."""
    client = anthropic.AsyncAnthropic()
    tasks = []

    for msg in messages:
        task = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": msg}]
        )
        tasks.append(task)

    responses = await asyncio.gather(*tasks)
    return [r.content[0].text for r in responses]

# Usage
messages = ["Summarize AI ethics", "Explain machine learning", "What is quantum computing?"]
responses = asyncio.run(process_batch(messages))
```

### Content Generation Pipeline

```python
import anthropic
from briefcase_ai_agent.integrations import anthropic_integration
import briefcase_ai_telemetry as bai

anthropic_integration.enable_instrumentation()

class ContentPipeline:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.pipeline_id = bai.generate_uuid()

    def generate_outline(self, topic):
        """Generate content outline."""
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system="You are a content strategist. Create detailed outlines for articles.",
            messages=[
                {"role": "user", "content": f"Create an outline for an article about: {topic}"}
            ]
        )

        # Track pipeline step
        step_event = bai.EventBuilder("content_pipeline_outline")
            .level(bai.EventLevel.info())
            .tag("pipeline_id", self.pipeline_id)
            .tag("step", "outline")
            .custom_data("topic", topic)
            .build()

        anthropic_integration.get_telemetry_client().track_event(step_event)
        return response.content[0].text

    def write_content(self, outline):
        """Write content from outline."""
        response = self.client.messages.create(
            model="claude-3-opus-20240229",  # Use best model for content
            max_tokens=4000,
            system="You are an expert writer. Write engaging, well-structured articles.",
            messages=[
                {"role": "user", "content": f"Write a full article based on this outline:\n\n{outline}"}
            ]
        )

        # Track pipeline step
        step_event = bai.EventBuilder("content_pipeline_writing")
            .level(bai.EventLevel.info())
            .tag("pipeline_id", self.pipeline_id)
            .tag("step", "writing")
            .custom_data("outline_length", len(outline))
            .custom_data("content_length", len(response.content[0].text))
            .build()

        anthropic_integration.get_telemetry_client().track_event(step_event)
        return response.content[0].text

    def review_content(self, content):
        """Review and improve content."""
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            system="You are an editor. Review content and suggest improvements.",
            messages=[
                {"role": "user", "content": f"Review and improve this article:\n\n{content}"}
            ]
        )

        # Track pipeline completion
        completion_event = bai.EventBuilder("content_pipeline_complete")
            .level(bai.EventLevel.info())
            .tag("pipeline_id", self.pipeline_id)
            .tag("step", "review")
            .custom_data("original_length", len(content))
            .custom_data("reviewed_length", len(response.content[0].text))
            .build()

        anthropic_integration.get_telemetry_client().track_event(completion_event)
        return response.content[0].text

    def generate_article(self, topic):
        """Full content generation pipeline."""
        outline = self.generate_outline(topic)
        content = self.write_content(outline)
        final_content = self.review_content(content)
        return final_content

# Usage
pipeline = ContentPipeline()
article = pipeline.generate_article("The Future of Artificial Intelligence")
```

## Troubleshooting

### Common Issues

1. **Events not appearing**: Check your API key and network connectivity
2. **Large token usage tracking**: Adjust `max_message_length` and `max_response_length`
3. **Streaming response issues**: Ensure `capture_streaming=True`

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
from briefcase_ai_agent.integrations import anthropic_integration

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("briefcase_ai_agent.integrations.anthropic_integration")
logger.setLevel(logging.DEBUG)

anthropic_integration.enable_instrumentation()
```

### Health Check

Verify integration is working correctly:

```python
from briefcase_ai_agent.integrations import anthropic_integration

# Check if instrumentation is active
if anthropic_integration.is_instrumentation_enabled():
    print("✅ Anthropic instrumentation is active")
else:
    print("❌ Anthropic instrumentation is not active")

# Check telemetry client
client = anthropic_integration.get_telemetry_client()
if client:
    print("✅ Telemetry client is available")
else:
    print("❌ Telemetry client is not configured")

# Test basic functionality
try:
    import anthropic
    test_client = anthropic.Anthropic()
    response = test_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✅ Basic Anthropic call successful")
except Exception as e:
    print(f"❌ Basic Anthropic call failed: {e}")
```

## Migration from Other Solutions

### From Direct Anthropic Usage

```python
# Old direct usage
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)

# New usage with Briefcase tracking
from briefcase_ai_agent.integrations import anthropic_integration

anthropic_integration.enable_instrumentation()

# All your existing code works unchanged
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### From Custom Instrumentation

```python
# Old custom instrumentation
def tracked_anthropic_call(model, messages):
    start_time = time.time()
    try:
        response = client.messages.create(model=model, messages=messages, max_tokens=1000)
        # Custom tracking code...
        return response
    except Exception as e:
        # Custom error tracking...
        raise

# New automatic instrumentation
from briefcase_ai_agent.integrations import anthropic_integration

anthropic_integration.enable_instrumentation()

# Just use Anthropic normally - tracking is automatic
response = client.messages.create(model=model, messages=messages, max_tokens=1000)
```

This Anthropic integration provides comprehensive tracking of your Claude API usage with minimal changes to your existing code.