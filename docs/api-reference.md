# API Reference

Complete API reference for the Briefcase AI Telemetry SDK.

## Core Classes

### TelemetryClient

The main client for sending telemetry data.

```python
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig

config = TelemetryConfig("your-api-key")
client = TelemetryClient(config)
```

#### Methods

##### `track_event(event: Event)`
Track a telemetry event.

**Parameters:**
- `event` (Event): The event to track

**Example:**
```python
event = create_event("user_login", level=EventLevel.info())
client.track_event(event)
```

##### `flush()`
Manually flush all pending events to the server.

**Returns:** Number of events flushed

**Example:**
```python
flushed_count = client.flush()
print(f"Flushed {flushed_count} events")
```

##### `start_background_flush()`
Start automatic background flushing of events.

**Example:**
```python
client.start_background_flush()
```

##### `buffer_size()`
Get the current number of events in the buffer.

**Returns:** int - Number of pending events

##### `with_session(session: Session)`
Set a session for the client.

**Parameters:**
- `session` (Session): Session to attach to the client

### TelemetryConfig

Configuration for the telemetry client.

```python
config = TelemetryConfig("your-api-key")
```

#### Methods

##### `with_endpoint(endpoint: str)`
Set a custom endpoint URL.

**Parameters:**
- `endpoint` (str): Custom endpoint URL

**Example:**
```python
config.with_endpoint("https://custom.api.com/telemetry")
```

##### `with_timeout_seconds(seconds: int)`
Set request timeout.

**Parameters:**
- `seconds` (int): Timeout in seconds (default: 30)

##### `with_batch_size(size: int)`
Set batch size for event flushing.

**Parameters:**
- `size` (int): Number of events per batch (default: 100)

##### `with_flush_interval_seconds(seconds: int)`
Set automatic flush interval.

**Parameters:**
- `seconds` (int): Seconds between automatic flushes (default: 30)

##### `with_retry_attempts(attempts: int)`
Set number of retry attempts for failed requests.

**Parameters:**
- `attempts` (int): Number of retries (default: 3)

##### `with_enabled(enabled: bool)`
Enable or disable telemetry collection.

**Parameters:**
- `enabled` (bool): Whether to collect telemetry (default: True)

### Event

Represents a telemetry event.

#### Properties

- `name` (str): Event name
- `level` (EventLevel): Event severity level
- `message` (Optional[str]): Event message
- `user_id` (Optional[str]): Associated user ID
- `timestamp` (datetime): Event timestamp
- `metadata` (Optional[EventMetadata]): Event metadata

### EventBuilder

Builder pattern for creating complex events.

```python
event = (
    EventBuilder("event_name")
    .level(EventLevel.info())
    .message("Event message")
    .user_id("user123")
    .tag("component", "auth")
    .custom_data("key", "value")
    .duration_ms(1000)
    .error("Error message")
    .build()
)
```

#### Methods

##### `level(level: EventLevel)`
Set event level.

##### `message(message: str)`
Set event message.

##### `user_id(user_id: str)`
Set user ID.

##### `tag(key: str, value: str)`
Add a tag.

##### `custom_data(key: str, value: str)`
Add custom data.

##### `duration_ms(duration: int)`
Set duration in milliseconds.

##### `error(error: str)`
Set error message.

##### `build()`
Build and return the event.

### EventLevel

Event severity levels.

```python
from briefcase_ai_telemetry import EventLevel

debug_level = EventLevel.debug()
info_level = EventLevel.info()
warning_level = EventLevel.warning()
error_level = EventLevel.error()
critical_level = EventLevel.critical()
```

### Session

Represents a user or system session.

```python
session = Session()
session = session.with_user_id("user123")
session = session.add_metadata("key", "value")
```

#### Methods

##### `with_user_id(user_id: str)`
Set user ID for the session.

**Returns:** New Session instance

##### `add_metadata(key: str, value: str)`
Add metadata to the session.

**Returns:** New Session instance

## AI/ML Features

### DriftCalculator

Advanced drift detection and analysis.

```python
from briefcase_ai_telemetry import DriftCalculator

calculator = DriftCalculator()
metrics = calculator.calculate_metrics(outputs)
```

#### Methods

##### `calculate_metrics(outputs: List[str])`
Calculate basic drift metrics.

**Parameters:**
- `outputs` (List[str]): List of model outputs to analyze

**Returns:** DriftMetrics

**Example:**
```python
outputs = ["Hello world", "Hello there", "Hi there"]
metrics = calculator.calculate_metrics(outputs)
print(f"Agreement rate: {metrics.total_agreement_rate}%")
```

##### `calculate_enhanced_metrics(outputs: List[str], context: Optional[str])`
Calculate enhanced drift metrics with semantic analysis.

**Parameters:**
- `outputs` (List[str]): List of model outputs
- `context` (Optional[str]): Context for semantic analysis

**Returns:** EnhancedDriftMetrics

##### `check_compliance(consistency_score: float, temperature: float, has_audit_trail: bool, framework: ComplianceFramework)`
Check compliance against regulatory frameworks.

**Parameters:**
- `consistency_score` (float): Model consistency score (0-100)
- `temperature` (float): Model temperature setting
- `has_audit_trail` (bool): Whether audit trail is enabled
- `framework` (ComplianceFramework): Compliance framework to check

**Returns:** ComplianceCheck

### DriftMetrics

Results from drift calculation.

#### Properties

- `total_agreement_rate` (float): Percentage of identical outputs (0-100)
- `normalized_edit_distance` (float): Average string similarity (0-1)
- `factual_drift_count` (int): Number of factual inconsistencies
- `consistency_score` (float): Overall consistency rating (0-100)
- `temperature_sensitivity` (float): Sensitivity to temperature changes
- `consensus_confidence` (str): Confidence level ('high', 'medium', 'low')
- `consensus_output` (Optional[str]): Agreed-upon output if consensus reached

### CostCalculator

AI model cost estimation and analysis.

```python
from briefcase_ai_telemetry import CostCalculator

calculator = CostCalculator()
models = calculator.list_models_by_provider()
```

#### Methods

##### `estimate_cost(model_name: str, input_text: str, output_text: str, input_tokens: Optional[int], output_tokens: Optional[int])`
Estimate cost for model usage.

**Parameters:**
- `model_name` (str): Name of the AI model
- `input_text` (str): Input text
- `output_text` (str): Output text
- `input_tokens` (Optional[int]): Exact input token count
- `output_tokens` (Optional[int]): Exact output token count

**Returns:** Optional[CostEstimate]

##### `get_models_under_cost(max_cost: float)`
Get models within a cost budget.

**Parameters:**
- `max_cost` (float): Maximum cost per request

**Returns:** List[ModelInfo]

##### `get_cheapest_model()`
Get the cheapest available model.

**Returns:** Optional[ModelInfo]

##### `list_models_by_provider()`
List models organized by provider.

**Returns:** Dict[str, List[ModelInfo]]

##### `calculate_monthly_cost(model_name: str, daily_requests: int, avg_input_tokens: int, avg_output_tokens: int)`
Calculate projected monthly costs.

**Parameters:**
- `model_name` (str): Model name
- `daily_requests` (int): Average daily requests
- `avg_input_tokens` (int): Average input tokens per request
- `avg_output_tokens` (int): Average output tokens per request

**Returns:** Optional[float] - Monthly cost in USD

### CostEstimate

Cost estimation results.

#### Properties

- `model_name` (str): Name of the model
- `input_tokens` (int): Number of input tokens
- `output_tokens` (int): Number of output tokens
- `input_cost` (float): Cost for input tokens
- `output_cost` (float): Cost for output tokens
- `total_cost` (float): Total cost
- `input_cost_per_token` (float): Cost per input token
- `output_cost_per_token` (float): Cost per output token

### AgentInstrument

Monitor AI agents and workflows.

```python
from briefcase_ai_telemetry import create_agent_instrument

instrument = create_agent_instrument(
    agent_id=123,
    client=client,
    config=config
)
```

#### Methods

##### `start()`
Start a new instrumentation session.

**Returns:** InstrumentationSession

##### `finish()`
Finish all active sessions.

### InstrumentationSession

Active instrumentation session for tracking agent execution.

#### Methods

##### `set_input_output(input: str, output: str)`
Set the input and output for this session.

##### `set_model_info(model: str, temperature: float)`
Set model information.

##### `set_token_usage(input_tokens: int, output_tokens: int)`
Set token usage information.

##### `set_accuracy(accuracy: float)`
Set accuracy score (0.0-1.0).

##### `set_cost(cost: float)`
Set execution cost in USD.

##### `set_error(error: str)`
Set error information if execution failed.

##### `set_metadata(key: str, value: str)`
Add custom metadata.

##### `add_reasoning_step(step: str)`
Add a reasoning step description.

##### `add_tool_call(tool: str, parameters: Dict[str, str])`
Record a tool call.

##### `finish()`
Finish this instrumentation session.

### InstrumentationConfig

Configuration for agent instrumentation.

```python
config = InstrumentationConfig()
config.with_consensus_mode(True, runs=3, threshold=0.8)
```

#### Methods

##### `with_consensus_mode(enabled: bool, runs: int, threshold: float)`
Enable consensus mode for multi-run analysis.

**Parameters:**
- `enabled` (bool): Whether to enable consensus mode
- `runs` (int): Number of runs to perform
- `threshold` (float): Agreement threshold (0.0-1.0)

##### `with_input_output_truncation(enabled: bool, max_input_length: int, max_output_length: int)`
Configure input/output truncation.

**Parameters:**
- `enabled` (bool): Whether to enable truncation
- `max_input_length` (int): Maximum input length
- `max_output_length` (int): Maximum output length

##### `with_sensitive_data_sanitization(enabled: bool)`
Enable automatic sanitization of sensitive data.

**Parameters:**
- `enabled` (bool): Whether to sanitize sensitive data

## Compliance

### ComplianceFramework

Supported regulatory frameworks.

```python
from briefcase_ai_telemetry import ComplianceFramework

gdpr = ComplianceFramework.Gdpr
soc2 = ComplianceFramework.Soc2
fsb = ComplianceFramework.Fsb
```

### ComplianceCheck

Results from compliance checking.

#### Properties

- `framework` (ComplianceFramework): The framework checked
- `compliant` (bool): Whether the system is compliant
- `score` (float): Compliance score (0-100)
- `requirements` (Dict[str, bool]): Individual requirement status
- `issues` (List[str]): List of compliance issues

## Convenience Functions

### `create_client(api_key: str, **kwargs)`
Create a telemetry client with optional configuration.

**Parameters:**
- `api_key` (str): Your API key
- `**kwargs`: Optional configuration parameters

**Returns:** TelemetryClient

### `create_event(name: str, **kwargs)`
Create an event with optional parameters.

**Parameters:**
- `name` (str): Event name
- `**kwargs`: Optional event parameters

**Returns:** Event

### `create_agent_instrument(agent_id: int, client: TelemetryClient, config: Optional[InstrumentationConfig])`
Create an agent instrument.

**Parameters:**
- `agent_id` (int): Unique agent identifier
- `client` (TelemetryClient): Telemetry client
- `config` (Optional[InstrumentationConfig]): Instrumentation configuration

**Returns:** AgentInstrument

### `calculate_drift(outputs: List[str])`
Calculate drift metrics for a list of outputs.

**Parameters:**
- `outputs` (List[str]): List of outputs to analyze

**Returns:** DriftMetrics

### `estimate_cost(model_name: str, input_text: str, output_text: str, input_tokens: Optional[int], output_tokens: Optional[int])`
Estimate cost for model usage.

**Returns:** Optional[CostEstimate]

## Error Handling

The SDK raises specific exceptions for different error conditions:

### `TelemetryError`
Base exception for all telemetry-related errors.

### `ConfigurationError`
Raised when there are configuration issues.

### `NetworkError`
Raised when network requests fail.

### `ValidationError`
Raised when data validation fails.

## Type Hints

The SDK provides comprehensive type hints for all public APIs:

```python
from briefcase_ai_telemetry import TelemetryClient, Event, DriftMetrics
from typing import Optional, List, Dict

def process_events(
    client: TelemetryClient,
    events: List[Event]
) -> Optional[Dict[str, float]]:
    for event in events:
        client.track_event(event)

    return {"processed": len(events)}
```

## Thread Safety

- `TelemetryClient` is thread-safe and can be used across multiple threads
- Background flushing runs in a separate thread
- All instrumentation components are thread-safe

## Performance Notes

- Events are batched automatically for efficient network usage
- Background flushing prevents blocking the main thread
- Token counting uses optimized algorithms for fast estimation
- Drift calculations use efficient string comparison algorithms

## Version Compatibility

This API reference is for version 0.1.0 of the Briefcase AI Telemetry SDK.

For version-specific changes, see the [CHANGELOG](../CHANGELOG.md).