"""
Core instrumentation classes and decorators for Briefcase AI agent monitoring.
"""

import asyncio
import functools
import json
import logging
import threading
import time
import traceback
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, Union, List
from dataclasses import dataclass, asdict
from queue import Queue, Empty
import uuid

from .config import BriefcaseConfig
from .drift import calculate_drift_metrics
from .utils import sanitize_text, estimate_cost, get_model_info

try:
    from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig, EventBuilder, EventLevel, Session
except ImportError:
    raise ImportError(
        "briefcase-ai-telemetry SDK not found. Please install with: pip install briefcase-ai-telemetry-sdk"
    )

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Metrics collected during agent execution."""
    latency: Optional[float] = None
    cost: Optional[float] = None
    accuracy: Optional[float] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    reasoning_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    model_name: Optional[str] = None
    status: str = "success"

class BriefcaseAgent:
    """
    Context manager for instrumenting AI agent execution.

    Usage:
        with BriefcaseAgent(agent_id=123, api_key="key") as agent:
            result = run_my_agent()
            agent.set_accuracy(95)
            return result
    """

    def __init__(
        self,
        agent_id: int,
        api_key: Optional[str] = None,
        config: Optional[BriefcaseConfig] = None,
        auto_submit: bool = True,
        consensus_mode: bool = False,
        consensus_runs: int = 3,
    ):
        self.agent_id = agent_id
        self.config = config or BriefcaseConfig()
        self.auto_submit = auto_submit
        self.consensus_mode = consensus_mode
        self.consensus_runs = consensus_runs

        # Initialize telemetry client
        if api_key:
            self.config.api_key = api_key

        if not self.config.api_key:
            raise ValueError("API key is required. Set via parameter, environment variable BRIEFCASE_API_KEY, or config file.")

        telemetry_config = TelemetryConfig(self.config.api_key)
        if self.config.endpoint:
            telemetry_config.with_endpoint(self.config.endpoint)

        self.telemetry_client = TelemetryClient(telemetry_config)

        # Execution tracking
        self.metrics = AgentMetrics()
        self.start_time = None
        self.run_id = str(uuid.uuid4())
        self._context_stack = []

        # Consensus mode tracking
        self.consensus_outputs = []

    def __enter__(self):
        """Start timing and return self for method chaining."""
        self.start_time = time.time()
        self._context_stack.append(self.run_id)
        logger.debug(f"Started agent execution tracking: {self.run_id}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finalize timing and submit telemetry."""
        if self.start_time:
            self.metrics.latency = time.time() - self.start_time

        if exc_type is not None:
            self.metrics.status = "failure"
            self.metrics.error_message = str(exc_val)
            logger.warning(f"Agent execution failed: {exc_val}")

        if self.auto_submit:
            self._submit_telemetry()

        self._context_stack.pop()
        return False  # Don't suppress exceptions

    def set_accuracy(self, accuracy: float) -> 'BriefcaseAgent':
        """Set the accuracy score (0-100)."""
        self.metrics.accuracy = max(0, min(100, accuracy))
        return self

    def set_cost(self, cost: float) -> 'BriefcaseAgent':
        """Set the execution cost in dollars."""
        self.metrics.cost = cost
        return self

    def set_input(self, input_data: str) -> 'BriefcaseAgent':
        """Set the input data (will be sanitized if configured)."""
        self.metrics.input_data = sanitize_text(input_data, self.config.sanitization_rules)
        return self

    def set_output(self, output_data: str) -> 'BriefcaseAgent':
        """Set the output data (will be sanitized if configured)."""
        self.metrics.output_data = sanitize_text(output_data, self.config.sanitization_rules)

        # Store for consensus mode
        if self.consensus_mode:
            self.consensus_outputs.append(output_data)

        return self

    def add_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: Any = None) -> 'BriefcaseAgent':
        """Add a tool call to the execution trace."""
        if self.metrics.tool_calls is None:
            self.metrics.tool_calls = []

        self.metrics.tool_calls.append({
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": time.time()
        })
        return self

    def add_reasoning_step(self, step: str) -> 'BriefcaseAgent':
        """Add a reasoning step to the execution path."""
        if self.metrics.reasoning_path is None:
            self.metrics.reasoning_path = ""

        self.metrics.reasoning_path += f"[{time.time():.3f}] {step}\n"
        return self

    def set_metadata(self, key: str, value: Any) -> 'BriefcaseAgent':
        """Set custom metadata."""
        if self.metrics.metadata is None:
            self.metrics.metadata = {}

        self.metrics.metadata[key] = value
        return self

    def set_model_info(self, model_name: str, temperature: Optional[float] = None) -> 'BriefcaseAgent':
        """Set model information."""
        self.metrics.model_name = model_name
        if temperature is not None:
            self.metrics.temperature = temperature

        # Auto-estimate cost if not set
        if self.metrics.cost is None and self.metrics.input_data and self.metrics.output_data:
            try:
                estimated_cost = estimate_cost(
                    model_name,
                    self.metrics.input_data,
                    self.metrics.output_data
                )
                self.metrics.cost = estimated_cost
            except Exception as e:
                logger.warning(f"Failed to estimate cost: {e}")

        return self

    def _submit_telemetry(self):
        """Submit telemetry data to Briefcase AI."""
        try:
            # Handle consensus mode
            if self.consensus_mode and len(self.consensus_outputs) >= self.consensus_runs:
                drift_metrics = calculate_drift_metrics(self.consensus_outputs)
                self.set_metadata("consensus_outputs", self.consensus_outputs)
                self.set_metadata("drift_metrics", asdict(drift_metrics))

            # Build event
            event_builder = EventBuilder(f"agent_execution_{self.run_id}")
            event_builder.level(EventLevel.info())

            if self.metrics.error_message:
                event_builder.level(EventLevel.error())
                event_builder.error(self.metrics.error_message)

            if self.metrics.input_data:
                event_builder.message(f"Input: {self.metrics.input_data[:200]}...")

            # Add all metrics as custom data
            metrics_dict = asdict(self.metrics)
            for key, value in metrics_dict.items():
                if value is not None:
                    if isinstance(value, (dict, list)):
                        event_builder.custom_data(key, json.dumps(value))
                    else:
                        event_builder.custom_data(key, str(value))

            # Add agent and execution metadata
            event_builder.custom_data("agent_id", str(self.agent_id))
            event_builder.custom_data("run_id", self.run_id)
            event_builder.custom_data("sdk_version", "0.1.0")

            # Set duration if available
            if self.metrics.latency:
                event_builder.duration_ms(int(self.metrics.latency * 1000))

            event = event_builder.build()
            self.telemetry_client.track_event(event)

            logger.info(f"Submitted telemetry for agent {self.agent_id}, run {self.run_id}")

        except Exception as e:
            logger.error(f"Failed to submit telemetry: {e}")
            if self.config.raise_on_telemetry_error:
                raise

def briefcase_agent(
    agent_id: int,
    api_key: Optional[str] = None,
    config: Optional[BriefcaseConfig] = None,
    auto_capture_io: bool = True,
    consensus_mode: bool = False,
    consensus_runs: int = 3,
):
    """
    Decorator for automatic agent instrumentation.

    Usage:
        @briefcase_agent(agent_id=123, api_key="key")
        def my_agent(prompt):
            return openai.chat.completions.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with BriefcaseAgent(
                agent_id=agent_id,
                api_key=api_key,
                config=config,
                consensus_mode=consensus_mode,
                consensus_runs=consensus_runs,
            ) as agent:
                try:
                    # Auto-capture input if enabled
                    if auto_capture_io:
                        input_repr = f"args={args}, kwargs={kwargs}"
                        agent.set_input(input_repr)

                    # Execute function
                    result = func(*args, **kwargs)

                    # Auto-capture output if enabled
                    if auto_capture_io:
                        agent.set_output(str(result))

                    return result

                except Exception as e:
                    # Error is automatically captured by context manager
                    raise

        # Handle async functions
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with BriefcaseAgent(
                agent_id=agent_id,
                api_key=api_key,
                config=config,
                consensus_mode=consensus_mode,
                consensus_runs=consensus_runs,
            ) as agent:
                try:
                    if auto_capture_io:
                        input_repr = f"args={args}, kwargs={kwargs}"
                        agent.set_input(input_repr)

                    result = await func(*args, **kwargs)

                    if auto_capture_io:
                        agent.set_output(str(result))

                    return result

                except Exception as e:
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


# Global configuration
_global_config = None

def configure(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    **kwargs
) -> BriefcaseConfig:
    """Configure global settings for Briefcase AI instrumentation."""
    global _global_config

    _global_config = BriefcaseConfig(
        api_key=api_key,
        endpoint=endpoint,
        **kwargs
    )

    return _global_config

def get_global_config() -> Optional[BriefcaseConfig]:
    """Get the global configuration."""
    return _global_config