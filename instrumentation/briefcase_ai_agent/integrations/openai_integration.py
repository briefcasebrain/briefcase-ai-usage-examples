"""
OpenAI integration for automatic instrumentation.

Monkey-patches the OpenAI client to automatically capture API calls and responses.
Uses the high-performance Rust-based telemetry core.
"""

import functools
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, List
import sys
import os

# Add the SDK to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'python'))
import briefcase_ai_telemetry as bai

logger = logging.getLogger(__name__)

@dataclass
class OpenAIInstrumentationConfig:
    """Configuration for OpenAI integration."""
    auto_capture_messages: bool = True
    auto_capture_responses: bool = True
    auto_calculate_costs: bool = True
    capture_function_calls: bool = True
    capture_system_messages: bool = False
    default_agent_id: Optional[int] = None
    enabled: bool = True
    api_key: Optional[str] = None
    endpoint: Optional[str] = None

# Global state
_instrumentation_enabled = False
_instrumentation_config = OpenAIInstrumentationConfig()
_original_methods = {}
_telemetry_client: Optional[bai.TelemetryClient] = None
_cost_calculator = bai.CostCalculator()

def _extract_messages_text(messages: List[Dict[str, Any]]) -> str:
    """Extract text content from OpenAI messages format."""
    if not messages:
        return ""

    text_parts = []
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")

        # Skip system messages if not configured to capture them
        if role == "system" and not _instrumentation_config.capture_system_messages:
            continue

        if isinstance(content, str):
            text_parts.append(f"[{role}] {content}")
        elif isinstance(content, list):
            # Handle multi-modal content
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(f"[{role}] {item.get('text', '')}")

    return "\n".join(text_parts)

def _extract_response_text(response: Any) -> str:
    """Extract text content from OpenAI response."""
    try:
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content or ""
            elif hasattr(choice, 'text'):
                return choice.text or ""
        return str(response)
    except Exception as e:
        logger.warning(f"Failed to extract response text: {e}")
        return ""

def _extract_function_calls(response: Any) -> Optional[List[Dict[str, Any]]]:
    """Extract function calls from OpenAI response."""
    if not _instrumentation_config.capture_function_calls:
        return None

    try:
        function_calls = []
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message'):
                message = choice.message

                # Function calling (new format)
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        if hasattr(tool_call, 'function'):
                            function_calls.append({
                                "type": "function",
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                                "id": getattr(tool_call, 'id', None)
                            })

                # Function calling (legacy format)
                elif hasattr(message, 'function_call') and message.function_call:
                    function_calls.append({
                        "type": "function",
                        "name": message.function_call.name,
                        "arguments": message.function_call.arguments,
                    })

        return function_calls if function_calls else None

    except Exception as e:
        logger.warning(f"Failed to extract function calls: {e}")
        return None

def _instrument_chat_completions_create(original_method):
    """Instrument the chat.completions.create method."""

    @functools.wraps(original_method)
    def wrapper(self, **kwargs):
        # Check if instrumentation is enabled
        if not _instrumentation_enabled or not _instrumentation_config.enabled:
            return original_method(self, **kwargs)

        # Get agent configuration
        agent_id = _instrumentation_config.default_agent_id

        # Skip if no agent ID or client configured
        if not agent_id or not _telemetry_client:
            logger.debug("No agent_id or telemetry client configured for OpenAI integration")
            return original_method(self, **kwargs)

        # Start instrumentation
        start_time = time.time()

        try:
            # Create instrumentation config
            instr_config = bai.InstrumentationConfig()
            instr_config.with_auto_submit(True)

            # Create agent instrument
            agent = bai.AgentInstrument(agent_id, _telemetry_client, instr_config)
            agent.start()

            # Extract input information
            if _instrumentation_config.auto_capture_messages and 'messages' in kwargs:
                input_text = _extract_messages_text(kwargs['messages'])
                agent.set_input(input_text)

            # Extract model and temperature
            model_name = kwargs.get('model', 'unknown')
            temperature = kwargs.get('temperature')
            agent.set_model_info(model_name, temperature)

            # Add metadata
            agent.set_metadata("openai_params", {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": kwargs.get('max_tokens'),
                "top_p": kwargs.get('top_p'),
                "frequency_penalty": kwargs.get('frequency_penalty'),
                "presence_penalty": kwargs.get('presence_penalty'),
                "stream": kwargs.get('stream', False),
            })

            # Make the API call
            response = original_method(self, **kwargs)

            # Extract response information
            input_text = ""
            response_text = ""
            if _instrumentation_config.auto_capture_messages and 'messages' in kwargs:
                input_text = _extract_messages_text(kwargs['messages'])
            if _instrumentation_config.auto_capture_responses:
                response_text = _extract_response_text(response)
                agent.set_output(response_text)

            # Extract function calls
            function_calls = _extract_function_calls(response)
            if function_calls:
                for func_call in function_calls:
                    agent.add_tool_call(
                        tool_name=func_call.get("name", "unknown"),
                        arguments=str(func_call.get("arguments", {})),
                        result=func_call.get("id")
                    )

            # Calculate cost if enabled
            if _instrumentation_config.auto_calculate_costs:
                if hasattr(response, 'usage'):
                    input_tokens = getattr(response.usage, 'prompt_tokens', 0)
                    output_tokens = getattr(response.usage, 'completion_tokens', 0)

                    # Use Rust-based cost calculator
                    cost_estimate = _cost_calculator.estimate_cost(
                        model_name, input_text, response_text, input_tokens, output_tokens
                    )
                    if cost_estimate:
                        agent.set_cost(cost_estimate.total_cost)

                    # Set token usage
                    agent.set_token_usage(input_tokens, output_tokens)

            # Set execution time and finalize
            execution_time = time.time() - start_time
            agent.set_metadata("execution_time", execution_time)

            # Submit telemetry
            try:
                agent.finish()
            except Exception as e:
                logger.warning(f"Failed to submit telemetry: {e}")

            return response

        except Exception as e:
            logger.error(f"Error in OpenAI instrumentation: {e}")
            # Still return the original response even if instrumentation failed
            return original_method(self, **kwargs)

    return wrapper

def _instrument_completions_create(original_method):
    """Instrument the completions.create method (legacy)."""

    @functools.wraps(original_method)
    def wrapper(self, **kwargs):
        if not _instrumentation_enabled or not _instrumentation_config.enabled:
            return original_method(self, **kwargs)

        agent_id = _instrumentation_config.default_agent_id

        if not agent_id or not _telemetry_client:
            return original_method(self, **kwargs)

        start_time = time.time()

        try:
            # Create instrumentation config
            instr_config = bai.InstrumentationConfig()
            instr_config.with_auto_submit(True)

            # Create agent instrument
            agent = bai.AgentInstrument(agent_id, _telemetry_client, instr_config)
            agent.start()

            # Extract input
            input_text = ""
            if _instrumentation_config.auto_capture_messages and 'prompt' in kwargs:
                input_text = str(kwargs['prompt'])
                agent.set_input(input_text)

            # Extract model info
            model_name = kwargs.get('model', 'unknown')
            temperature = kwargs.get('temperature')
            agent.set_model_info(model_name, temperature)

            # Add metadata
            agent.set_metadata("openai_params", {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": kwargs.get('max_tokens'),
                "stream": kwargs.get('stream', False),
            })

            # Make API call
            response = original_method(self, **kwargs)

            # Extract response
            response_text = ""
            if _instrumentation_config.auto_capture_responses:
                response_text = _extract_response_text(response)
                agent.set_output(response_text)

            # Calculate cost
            if _instrumentation_config.auto_calculate_costs and hasattr(response, 'usage'):
                input_tokens = getattr(response.usage, 'prompt_tokens', 0)
                output_tokens = getattr(response.usage, 'completion_tokens', 0)

                # Use Rust-based cost calculator
                cost_estimate = _cost_calculator.estimate_cost(
                    model_name, input_text, response_text, input_tokens, output_tokens
                )
                if cost_estimate:
                    agent.set_cost(cost_estimate.total_cost)

                # Set token usage
                agent.set_token_usage(input_tokens, output_tokens)

            execution_time = time.time() - start_time
            agent.set_metadata("execution_time", execution_time)

            # Submit telemetry
            try:
                agent.finish()
            except Exception as e:
                logger.warning(f"Failed to submit telemetry: {e}")

            return response

        except Exception as e:
            logger.error(f"Error in OpenAI completions instrumentation: {e}")
            return original_method(self, **kwargs)

    return wrapper

def enable_openai_integration(
    agent_id: Optional[int] = None,
    config: Optional[OpenAIInstrumentationConfig] = None,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None
) -> bool:
    """
    Enable automatic OpenAI instrumentation using Rust-based telemetry.

    Args:
        agent_id: Default agent ID for all OpenAI calls
        config: OpenAI-specific configuration
        api_key: Briefcase AI API key for telemetry
        endpoint: Optional custom telemetry endpoint

    Returns:
        True if successfully enabled, False otherwise
    """
    global _instrumentation_enabled, _instrumentation_config, _original_methods, _telemetry_client

    try:
        # Try to import OpenAI
        try:
            import openai
        except ImportError:
            logger.error("OpenAI library not installed. Install with: pip install openai")
            return False

        # Update configuration
        if config:
            _instrumentation_config = config
        if agent_id:
            _instrumentation_config.default_agent_id = agent_id
        if api_key:
            _instrumentation_config.api_key = api_key
        if endpoint:
            _instrumentation_config.endpoint = endpoint

        # Validate configuration
        if not _instrumentation_config.default_agent_id:
            logger.error("agent_id is required for OpenAI integration")
            return False

        if not _instrumentation_config.api_key:
            logger.error("api_key is required for OpenAI integration")
            return False

        # Create telemetry client
        telemetry_config = bai.TelemetryConfig(_instrumentation_config.api_key)
        if _instrumentation_config.endpoint:
            telemetry_config.with_endpoint(_instrumentation_config.endpoint)

        _telemetry_client = bai.TelemetryClient(telemetry_config)

        # Monkey-patch the OpenAI client
        # Handle both v1.0+ and legacy OpenAI clients
        try:
            # OpenAI v1.0+ (new client structure)
            if hasattr(openai, 'OpenAI'):
                # Patch the client class methods
                client_class = openai.OpenAI

                # Chat completions
                if hasattr(client_class, 'chat') and hasattr(client_class.chat, 'completions'):
                    original_create = client_class.chat.completions.create
                    _original_methods['chat_completions_create'] = original_create
                    client_class.chat.completions.create = _instrument_chat_completions_create(original_create)

                # Legacy completions
                if hasattr(client_class, 'completions'):
                    original_completions = client_class.completions.create
                    _original_methods['completions_create'] = original_completions
                    client_class.completions.create = _instrument_completions_create(original_completions)

        except Exception as e:
            logger.warning(f"Failed to patch OpenAI v1.0+ client: {e}")

        try:
            # Legacy OpenAI (v0.x) - direct module methods
            if hasattr(openai, 'ChatCompletion'):
                original_chat = openai.ChatCompletion.create
                _original_methods['legacy_chat_create'] = original_chat
                openai.ChatCompletion.create = _instrument_chat_completions_create(original_chat)

            if hasattr(openai, 'Completion'):
                original_completion = openai.Completion.create
                _original_methods['legacy_completion_create'] = original_completion
                openai.Completion.create = _instrument_completions_create(original_completion)

        except Exception as e:
            logger.warning(f"Failed to patch legacy OpenAI client: {e}")

        _instrumentation_enabled = True
        logger.info(f"OpenAI integration enabled for agent {_instrumentation_config.default_agent_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to enable OpenAI integration: {e}")
        return False

def disable_openai_integration() -> bool:
    """Disable OpenAI instrumentation and restore original methods."""
    global _instrumentation_enabled, _original_methods, _telemetry_client

    try:
        import openai

        # Restore original methods
        if 'chat_completions_create' in _original_methods:
            openai.OpenAI.chat.completions.create = _original_methods['chat_completions_create']

        if 'completions_create' in _original_methods:
            openai.OpenAI.completions.create = _original_methods['completions_create']

        if 'legacy_chat_create' in _original_methods:
            openai.ChatCompletion.create = _original_methods['legacy_chat_create']

        if 'legacy_completion_create' in _original_methods:
            openai.Completion.create = _original_methods['legacy_completion_create']

        _original_methods.clear()
        _telemetry_client = None
        _instrumentation_enabled = False
        logger.info("OpenAI integration disabled")
        return True

    except Exception as e:
        logger.error(f"Failed to disable OpenAI integration: {e}")
        return False

def is_openai_integration_enabled() -> bool:
    """Check if OpenAI integration is currently enabled."""
    return _instrumentation_enabled

def update_openai_config(config: OpenAIInstrumentationConfig):
    """Update the OpenAI integration configuration."""
    global _instrumentation_config
    _instrumentation_config = config
    logger.info("OpenAI integration configuration updated")