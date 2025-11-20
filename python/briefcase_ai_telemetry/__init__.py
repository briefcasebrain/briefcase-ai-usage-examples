"""
Briefcase AI Telemetry SDK

A high-performance telemetry SDK for AI applications, built with Rust and PyO3.

Core Features:
- High-performance event tracking and analytics
- AI/ML specific monitoring capabilities
- Advanced drift detection and analysis
- Cost tracking and optimization for AI models
- Comprehensive agent instrumentation
- Regulatory compliance checking (GDPR, SOC2, FSB)
- Real-time consensus analysis and validation

Key Components:
- TelemetryClient: Core telemetry tracking
- DriftCalculator: Advanced drift detection algorithms
- CostCalculator: AI model cost estimation and optimization
- AgentInstrument: Comprehensive AI agent monitoring
- ComplianceFrameworks: Built-in regulatory compliance checking

Example Usage:
    >>> import briefcase_ai_telemetry as bt
    >>>
    >>> # Basic telemetry
    >>> client = bt.create_client("your-api-key")
    >>> event = bt.create_event("user_action", level=bt.EventLevel.info())
    >>> client.track_event(event)
    >>>
    >>> # AI/ML specific features
    >>> drift_metrics = bt.calculate_drift(["output1", "output2", "output3"])
    >>> cost_estimate = bt.estimate_cost("gpt-4", "input", "output")
    >>>
    >>> # Agent instrumentation
    >>> instrument = bt.create_agent_instrument(123, client)
    >>> session = instrument.start()
    >>> session.set_input_output("query", "response")
    >>> session.finish()

For detailed documentation and examples, visit:
https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk
"""

import warnings
from typing import Any, Dict, List, Optional, Union

__version__ = "0.1.0"
__author__ = "Aansh Shah"
__email__ = "aansh@briefcasebrain.com"

try:
    from ._internal import PyAgentInstrument as AgentInstrument
    from ._internal import PyCostCalculator as CostCalculator
    from ._internal import PyCostEstimate as CostEstimate
    from ._internal import PyDriftCalculator as DriftCalculator
    from ._internal import PyDriftMetrics as DriftMetrics
    from ._internal import PyEvent as Event
    from ._internal import PyEventBuilder as EventBuilder
    from ._internal import PyEventLevel as EventLevel
    from ._internal import PyEventMetadata as EventMetadata
    from ._internal import PyInstrumentationConfig as InstrumentationConfig
    from ._internal import PySession as Session
    from ._internal import PyTelemetryClient as TelemetryClient
    from ._internal import (
        PyTelemetryConfig as TelemetryConfig,  # New instrumentation features
    )
except ImportError as e:
    warnings.warn(
        "Failed to import Rust extension module. "
        "Please ensure the package is properly installed with: pip install briefcase-ai-telemetry-sdk",
        ImportWarning,
        stacklevel=2,
    )
    raise ImportError(
        "Could not import Rust extension module. "
        "This usually means the package was not installed correctly."
    ) from e

__all__ = [
    "TelemetryConfig",
    "EventLevel",
    "EventMetadata",
    "EventBuilder",
    "Event",
    "Session",
    "TelemetryClient",
    # New instrumentation features
    "AgentInstrument",
    "InstrumentationConfig",
    "DriftCalculator",
    "DriftMetrics",
    "CostCalculator",
    "CostEstimate",
    # Convenience functions
    "create_client",
    "create_event",
    "create_agent_instrument",
    "calculate_drift",
    "estimate_cost",
]


def create_client(api_key: str, **kwargs: Any) -> TelemetryClient:
    """
    Create a new TelemetryClient with the provided API key and configuration.

    Args:
        api_key: Your Briefcase AI API key
        **kwargs: Additional configuration options (endpoint, timeout_seconds, etc.)

    Returns:
        A configured TelemetryClient instance

    Example:
        >>> client = create_client("your-api-key", timeout_seconds=30)
        >>> client.start_background_flush()
    """
    config = TelemetryConfig(api_key)

    if "endpoint" in kwargs:
        config.with_endpoint(kwargs["endpoint"])
    if "timeout_seconds" in kwargs:
        config.with_timeout_seconds(kwargs["timeout_seconds"])
    if "retry_attempts" in kwargs:
        config.with_retry_attempts(kwargs["retry_attempts"])
    if "batch_size" in kwargs:
        config.with_batch_size(kwargs["batch_size"])
    if "flush_interval_seconds" in kwargs:
        config.with_flush_interval_seconds(kwargs["flush_interval_seconds"])
    if "enabled" in kwargs:
        config.with_enabled(kwargs["enabled"])

    return TelemetryClient(config)


def create_event(
    name: str,
    level: Optional[EventLevel] = None,
    message: Optional[str] = None,
    user_id: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[int] = None,
    error: Optional[str] = None,
) -> Event:
    """
    Create a new Event with the provided parameters.

    Args:
        name: The name of the event
        level: The event level (Debug, Info, Warning, Error, Critical)
        message: Optional message for the event
        user_id: Optional user ID associated with the event
        tags: Optional dictionary of tags
        custom_data: Optional dictionary of custom data (values converted to strings)
        duration_ms: Optional duration in milliseconds
        error: Optional error message

    Returns:
        A configured Event instance

    Example:
        >>> event = create_event(
        ...     "user_login",
        ...     level=EventLevel.info(),
        ...     user_id="user123",
        ...     tags={"component": "auth"},
        ...     custom_data={"login_method": "oauth"}
        ... )
    """
    builder = EventBuilder(name)

    if level is not None:
        builder.level(level)
    if message is not None:
        builder.message(message)
    if user_id is not None:
        builder.user_id(user_id)
    if tags:
        for key, value in tags.items():
            builder.tag(key, value)
    if custom_data:
        for key, value in custom_data.items():
            builder.custom_data(key, str(value))
    if duration_ms is not None:
        builder.duration_ms(duration_ms)
    if error is not None:
        builder.error(error)

    return builder.build()


def create_agent_instrument(
    agent_id: int,
    client: TelemetryClient,
    config: Optional[InstrumentationConfig] = None,
) -> AgentInstrument:
    """
    Create a new AgentInstrument for tracking AI agent execution metrics.

    This function sets up comprehensive monitoring for AI agents, enabling tracking of:
    - Multi-step reasoning processes
    - Tool usage and external API calls
    - Performance metrics (accuracy, cost, timing)
    - Consensus analysis across multiple runs
    - Compliance with regulatory requirements

    Args:
        agent_id: Unique identifier for the agent (used for grouping and analysis)
        client: TelemetryClient instance for sending telemetry data
        config: Optional InstrumentationConfig for advanced features like:
                - Consensus mode (multiple runs with agreement analysis)
                - Data sanitization (automatic removal of sensitive information)
                - Input/output truncation (for large data handling)

    Returns:
        A configured AgentInstrument instance ready for session tracking

    Example:
        Basic agent instrumentation:
        >>> client = create_client("your-api-key")
        >>> instrument = create_agent_instrument(123, client)
        >>> session = instrument.start()
        >>> session.set_input_output("query", "response")
        >>> session.finish()

        Advanced configuration with consensus mode:
        >>> config = InstrumentationConfig()
        >>> config.with_consensus_mode(True, runs=3, threshold=0.8)
        >>> config.with_sensitive_data_sanitization(True)
        >>> instrument = create_agent_instrument(123, client, config)
        >>>
        >>> # Track multi-step reasoning
        >>> session = instrument.start()
        >>> session.add_reasoning_step("Analyzed user intent")
        >>> session.add_tool_call("database", {"query": "SELECT * FROM users"})
        >>> session.set_accuracy(0.95)
        >>> session.finish()

    See Also:
        - InstrumentationConfig: For advanced configuration options
        - Examples in examples/agent_instrumentation.py
    """
    return AgentInstrument(agent_id, client, config)


def calculate_drift(outputs: List[str]) -> DriftMetrics:
    """
    Calculate drift metrics for a list of AI model outputs.

    This function analyzes output consistency to detect model drift - when AI systems
    start producing outputs that differ from their expected behavior. It calculates
    multiple metrics to provide comprehensive drift analysis:

    - Total Agreement Rate: Percentage of outputs that are identical
    - Normalized Edit Distance: String similarity measure (0-1 scale)
    - Consistency Score: Overall reproducibility rating
    - Consensus Confidence: Reliability classification (high/medium/low)
    - Factual Drift Count: Number of factual inconsistencies detected

    Args:
        outputs: List of output strings to analyze for drift. Should contain
                at least 2 outputs for meaningful analysis. More outputs (5-10+)
                provide better statistical significance.

    Returns:
        DriftMetrics object containing:
        - total_agreement_rate: Percentage of identical outputs (0-100)
        - normalized_edit_distance: Average string similarity (0-1)
        - consistency_score: Overall consistency rating (0-100)
        - consensus_confidence: 'high', 'medium', or 'low'
        - consensus_output: Agreed-upon output if consensus exists
        - factual_drift_count: Number of factual inconsistencies

    Example:
        Basic drift detection:
        >>> outputs = ["The capital of France is Paris.",
        ...           "France's capital city is Paris.",
        ...           "Paris is the capital of France."]
        >>> metrics = calculate_drift(outputs)
        >>> print(f"Agreement rate: {metrics.total_agreement_rate:.1f}%")
        >>> print(f"Confidence: {metrics.consensus_confidence}")

        Detecting high drift:
        >>> different_outputs = ["Hello world", "Goodbye world", "Maybe later"]
        >>> metrics = calculate_drift(different_outputs)
        >>> if metrics.consensus_confidence == "low":
        ...     print("⚠️ High drift detected - investigate model behavior")

        Production monitoring:
        >>> daily_outputs = get_model_outputs_from_last_24_hours()
        >>> if len(daily_outputs) >= 10:
        ...     metrics = calculate_drift(daily_outputs)
        ...     if metrics.consistency_score < 80.0:
        ...         trigger_drift_alert(metrics)

    See Also:
        - DriftCalculator: For advanced drift analysis with context
        - Examples in examples/drift_analysis.py
        - Compliance checking for regulatory requirements
    """
    calculator = DriftCalculator()
    return calculator.calculate_metrics(outputs)


def estimate_cost(
    model_name: str,
    input_text: str,
    output_text: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
) -> Optional[CostEstimate]:
    """
    Estimate the cost for an AI model execution with accurate pricing.

    This function provides cost estimation for popular AI models including OpenAI GPT
    models, Anthropic Claude models, and custom models. It handles both token-based
    estimation and exact token counts for precise cost calculation.

    Supported Models:
    - OpenAI: gpt-4, gpt-3.5-turbo, gpt-3.5-turbo-instruct
    - Anthropic: claude-3-sonnet, claude-3-haiku, claude-3-opus
    - Custom models: Added via CostCalculator.add_custom_model()

    Args:
        model_name: Name of the AI model. Must match supported model names exactly.
                   Case-sensitive. Examples: "gpt-4", "claude-3-sonnet"
        input_text: Input text sent to the model. Used for token estimation if
                   exact token counts not provided.
        output_text: Output text received from the model. Used for token estimation
                    if exact token counts not provided.
        input_tokens: Optional exact input token count. When provided, overrides
                     token estimation from input_text for more accurate costing.
        output_tokens: Optional exact output token count. When provided, overrides
                      token estimation from output_text for more accurate costing.

    Returns:
        CostEstimate object containing:
        - total_cost: Total cost in USD for the request
        - input_cost: Cost for input tokens
        - output_cost: Cost for output tokens
        - input_tokens: Number of input tokens used
        - output_tokens: Number of output tokens used
        - input_cost_per_token: Cost per input token
        - output_cost_per_token: Cost per output token

        Returns None if the model is not found in the pricing database.

    Example:
        Basic cost estimation:
        >>> cost = estimate_cost("gpt-4", "What is AI?", "AI is artificial intelligence...")
        >>> if cost:
        ...     print(f"Total cost: ${cost.total_cost:.6f}")
        ...     print(f"Input tokens: {cost.input_tokens}")
        ...     print(f"Output tokens: {cost.output_tokens}")

        Using exact token counts:
        >>> cost = estimate_cost("gpt-4", "Sample input", "Sample output",
        ...                     input_tokens=150, output_tokens=89)
        >>> print(f"Precise cost: ${cost.total_cost:.6f}")

        Model comparison:
        >>> models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]
        >>> input_text = "Explain quantum computing"
        >>> output_text = "Quantum computing uses quantum mechanics..."
        >>>
        >>> for model in models:
        ...     cost = estimate_cost(model, input_text, output_text)
        ...     if cost:
        ...         print(f"{model}: ${cost.total_cost:.6f}")

        Budget planning:
        >>> daily_requests = 1000
        >>> avg_cost = estimate_cost("gpt-3.5-turbo", sample_input, sample_output)
        >>> if avg_cost:
        ...     monthly_cost = avg_cost.total_cost * daily_requests * 30
        ...     print(f"Monthly estimate: ${monthly_cost:.2f}")

    See Also:
        - CostCalculator: For advanced cost analysis and budget planning
        - Examples in examples/cost_estimation.py
        - Model comparison and optimization strategies
    """
    calculator = CostCalculator()
    return calculator.estimate_cost(
        model_name, input_text, output_text, input_tokens, output_tokens
    )
