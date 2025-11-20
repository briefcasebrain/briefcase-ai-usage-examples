"""
Anthropic integration for automatic instrumentation.

Monkey-patches the Anthropic client to automatically capture API calls and responses.
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
class AnthropicInstrumentationConfig:
    """Configuration for Anthropic integration."""
    auto_capture_messages: bool = True
    auto_capture_responses: bool = True
    auto_calculate_costs: bool = True
    capture_tool_use: bool = True
    capture_thinking: bool = False  # Anthropic's internal reasoning
    capture_system_messages: bool = True
    default_agent_id: Optional[int] = None
    enabled: bool = True
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    max_input_length: int = 10000
    max_output_length: int = 10000

# Global state
_instrumentation_enabled = False
_instrumentation_config = AnthropicInstrumentationConfig()
_original_methods = {}
_telemetry_client: Optional[bai.TelemetryClient] = None
_cost_calculator = bai.CostCalculator()

def _truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def _extract_messages_text(messages: List[Dict[str, Any]]) -> str:
    """Extract text content from Anthropic messages format."""
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
            # Handle multi-modal content blocks
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(f"[{role}] {block.get('text', '')}")
                    elif block.get("type") == "tool_use":
                        tool_name = block.get("name", "unknown_tool")
                        tool_input = block.get("input", {})
                        text_parts.append(f"[{role}] Tool: {tool_name}({tool_input})")
                    elif block.get("type") == "tool_result":
                        tool_id = block.get("tool_use_id", "unknown")
                        result = block.get("content", "")
                        text_parts.append(f"[{role}] Tool Result ({tool_id}): {result}")

    return "\n".join(text_parts)

def _extract_response_text(response: Any) -> str:
    """Extract text content from Anthropic response."""
    try:
        if hasattr(response, 'content') and response.content:
            content_parts = []
            for content_block in response.content:
                if hasattr(content_block, 'type'):
                    if content_block.type == 'text' and hasattr(content_block, 'text'):
                        content_parts.append(content_block.text)
                    elif content_block.type == 'tool_use' and hasattr(content_block, 'name'):
                        tool_name = content_block.name
                        tool_input = getattr(content_block, 'input', {})
                        content_parts.append(f"Tool: {tool_name}({tool_input})")
            return "\n".join(content_parts)

        # Fallback for different response formats
        return str(response)

    except Exception as e:
        logger.warning(f"Failed to extract response text: {e}")
        return ""

def _extract_tool_calls(response: Any) -> Optional[List[Dict[str, Any]]]:
    """Extract tool calls from Anthropic response."""
    if not _instrumentation_config.capture_tool_use:
        return None

    try:
        tool_calls = []
        if hasattr(response, 'content') and response.content:
            for content_block in response.content:
                if hasattr(content_block, 'type') and content_block.type == 'tool_use':
                    tool_calls.append({
                        "type": "tool_use",
                        "id": getattr(content_block, 'id', None),
                        "name": getattr(content_block, 'name', 'unknown'),
                        "input": getattr(content_block, 'input', {}),
                    })

        return tool_calls if tool_calls else None

    except Exception as e:
        logger.warning(f"Failed to extract tool calls: {e}")
        return None

def _extract_thinking(response: Any) -> Optional[str]:
    """Extract thinking/reasoning from Anthropic response (if available)."""
    if not _instrumentation_config.capture_thinking:
        return None

    try:
        # Anthropic sometimes includes thinking in special content blocks
        if hasattr(response, 'content') and response.content:
            for content_block in response.content:
                if hasattr(content_block, 'type') and content_block.type == 'thinking':
                    return getattr(content_block, 'text', '')

        # Check for thinking in metadata or other fields
        if hasattr(response, 'thinking'):
            return response.thinking

        return None

    except Exception as e:
        logger.warning(f"Failed to extract thinking: {e}")
        return None

def _extract_token_usage(response: Any) -> Optional[Dict[str, int]]:
    """Extract token usage from Anthropic response."""
    try:
        if hasattr(response, 'usage'):
            usage = response.usage
            return {
                'input': getattr(usage, 'input_tokens', 0),
                'output': getattr(usage, 'output_tokens', 0),
                'total': getattr(usage, 'input_tokens', 0) + getattr(usage, 'output_tokens', 0),
            }
        return None

    except Exception as e:
        logger.debug(f"Failed to extract token usage: {e}")
        return None

def _instrument_messages_create(original_method):
    """Instrument the messages.create method."""

    @functools.wraps(original_method)
    def wrapper(self, **kwargs):
        # Check if instrumentation is enabled
        if not _instrumentation_enabled or not _instrumentation_config.enabled:
            return original_method(self, **kwargs)

        # Get agent configuration
        agent_id = _instrumentation_config.default_agent_id

        # Skip if no agent ID or client configured
        if not agent_id or not _telemetry_client:
            logger.debug("No agent_id or telemetry client configured for Anthropic integration")
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
                input_text = _truncate_text(input_text, _instrumentation_config.max_input_length)
                agent.set_input(input_text)

            # Extract model and temperature
            model_name = kwargs.get('model', 'claude-3-sonnet')
            temperature = kwargs.get('temperature')
            agent.set_model_info(model_name, temperature)

            # Add metadata
            agent.set_metadata("anthropic_params", {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": kwargs.get('max_tokens'),
                "top_p": kwargs.get('top_p'),
                "top_k": kwargs.get('top_k'),
                "stream": kwargs.get('stream', False),
            })

            # Add system message if present
            if 'system' in kwargs:
                agent.set_metadata("system_message", str(kwargs['system'])[:500])

            # Make the API call
            response = original_method(self, **kwargs)

            # Extract response information
            input_text = ""
            response_text = ""
            if _instrumentation_config.auto_capture_messages and 'messages' in kwargs:
                input_text = _extract_messages_text(kwargs['messages'])
            if _instrumentation_config.auto_capture_responses:
                response_text = _extract_response_text(response)
                response_text = _truncate_text(response_text, _instrumentation_config.max_output_length)
                agent.set_output(response_text)

            # Extract tool calls
            tool_calls = _extract_tool_calls(response)
            if tool_calls:
                for tool_call in tool_calls:
                    agent.add_tool_call(
                        tool_name=tool_call.get("name", "unknown"),
                        arguments=str(tool_call.get("input", {})),
                        result=tool_call.get("id")
                    )

            # Extract thinking if available
            thinking = _extract_thinking(response)
            if thinking:
                agent.set_metadata("thinking", thinking[:1000])  # Limit thinking text

            # Calculate cost if enabled
            if _instrumentation_config.auto_calculate_costs:
                token_usage = _extract_token_usage(response)
                if token_usage:
                    input_tokens = token_usage['input']
                    output_tokens = token_usage['output']

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
            logger.error(f"Error in Anthropic instrumentation: {e}")
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
                input_text = _truncate_text(input_text, _instrumentation_config.max_input_length)
                agent.set_input(input_text)

            # Extract model info
            model_name = kwargs.get('model', 'claude-instant')
            temperature = kwargs.get('temperature')
            agent.set_model_info(model_name, temperature)

            # Add metadata
            agent.set_metadata("anthropic_params", {
                "model": model_name,
                "temperature": temperature,
                "max_tokens_to_sample": kwargs.get('max_tokens_to_sample'),
                "stream": kwargs.get('stream', False),
            })

            # Make API call
            response = original_method(self, **kwargs)

            # Extract response
            response_text = ""
            if _instrumentation_config.auto_capture_responses:
                response_text = _extract_response_text(response)
                response_text = _truncate_text(response_text, _instrumentation_config.max_output_length)
                agent.set_output(response_text)

            # Calculate cost
            if _instrumentation_config.auto_calculate_costs:
                token_usage = _extract_token_usage(response)
                if token_usage:
                    input_tokens = token_usage['input']
                    output_tokens = token_usage['output']

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
            logger.error(f"Error in Anthropic completions instrumentation: {e}")
            return original_method(self, **kwargs)

    return wrapper

def enable_anthropic_integration(
    agent_id: Optional[int] = None,
    config: Optional[AnthropicInstrumentationConfig] = None,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None
) -> bool:
    """
    Enable automatic Anthropic instrumentation using Rust-based telemetry.

    Args:
        agent_id: Default agent ID for all Anthropic calls
        config: Anthropic-specific configuration
        api_key: Briefcase AI API key for telemetry
        endpoint: Optional custom telemetry endpoint

    Returns:
        True if successfully enabled, False otherwise
    """
    global _instrumentation_enabled, _instrumentation_config, _original_methods, _telemetry_client

    try:
        # Try to import Anthropic
        try:
            import anthropic
        except ImportError:
            logger.error("Anthropic library not installed. Install with: pip install anthropic")
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
            logger.error("agent_id is required for Anthropic integration")
            return False

        if not _instrumentation_config.api_key:
            logger.error("api_key is required for Anthropic integration")
            return False

        # Create telemetry client
        telemetry_config = bai.TelemetryConfig(_instrumentation_config.api_key)
        if _instrumentation_config.endpoint:
            telemetry_config.with_endpoint(_instrumentation_config.endpoint)

        _telemetry_client = bai.TelemetryClient(telemetry_config)

        # Monkey-patch the Anthropic client
        # Handle both new and legacy Anthropic clients

        try:
            # Modern Anthropic client (v0.3+)
            if hasattr(anthropic, 'Anthropic'):
                client_class = anthropic.Anthropic

                # Messages API
                if (hasattr(client_class, 'messages') and
                    hasattr(client_class.messages, 'create')):
                    original_messages_create = client_class.messages.create
                    _original_methods['messages_create'] = original_messages_create
                    client_class.messages.create = _instrument_messages_create(original_messages_create)

                # Completions API (if available)
                if (hasattr(client_class, 'completions') and
                    hasattr(client_class.completions, 'create')):
                    original_completions_create = client_class.completions.create
                    _original_methods['completions_create'] = original_completions_create
                    client_class.completions.create = _instrument_completions_create(original_completions_create)

        except Exception as e:
            logger.warning(f"Failed to patch modern Anthropic client: {e}")

        try:
            # Legacy Anthropic client (v0.2 and earlier)
            if hasattr(anthropic, 'Client'):
                # Legacy client class
                client_class = anthropic.Client

                if hasattr(client_class, 'messages'):
                    if hasattr(client_class.messages, 'create'):
                        original_messages = client_class.messages.create
                        _original_methods['legacy_messages_create'] = original_messages
                        client_class.messages.create = _instrument_messages_create(original_messages)

                if hasattr(client_class, 'completions'):
                    if hasattr(client_class.completions, 'create'):
                        original_completions = client_class.completions.create
                        _original_methods['legacy_completions_create'] = original_completions
                        client_class.completions.create = _instrument_completions_create(original_completions)

            # Direct function patching for very old versions
            if hasattr(anthropic, 'messages') and hasattr(anthropic.messages, 'create'):
                original_direct_messages = anthropic.messages.create
                _original_methods['direct_messages_create'] = original_direct_messages
                anthropic.messages.create = _instrument_messages_create(original_direct_messages)

            if hasattr(anthropic, 'completions') and hasattr(anthropic.completions, 'create'):
                original_direct_completions = anthropic.completions.create
                _original_methods['direct_completions_create'] = original_direct_completions
                anthropic.completions.create = _instrument_completions_create(original_direct_completions)

        except Exception as e:
            logger.warning(f"Failed to patch legacy Anthropic client: {e}")

        _instrumentation_enabled = True
        logger.info(f"Anthropic integration enabled for agent {_instrumentation_config.default_agent_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to enable Anthropic integration: {e}")
        return False

def disable_anthropic_integration() -> bool:
    """Disable Anthropic instrumentation and restore original methods."""
    global _instrumentation_enabled, _original_methods, _telemetry_client

    try:
        import anthropic

        # Restore original methods
        if 'messages_create' in _original_methods:
            anthropic.Anthropic.messages.create = _original_methods['messages_create']

        if 'completions_create' in _original_methods:
            anthropic.Anthropic.completions.create = _original_methods['completions_create']

        if 'legacy_messages_create' in _original_methods:
            anthropic.Client.messages.create = _original_methods['legacy_messages_create']

        if 'legacy_completions_create' in _original_methods:
            anthropic.Client.completions.create = _original_methods['legacy_completions_create']

        if 'direct_messages_create' in _original_methods:
            anthropic.messages.create = _original_methods['direct_messages_create']

        if 'direct_completions_create' in _original_methods:
            anthropic.completions.create = _original_methods['direct_completions_create']

        _original_methods.clear()
        _telemetry_client = None
        _instrumentation_enabled = False
        logger.info("Anthropic integration disabled")
        return True

    except Exception as e:
        logger.error(f"Failed to disable Anthropic integration: {e}")
        return False

def is_anthropic_integration_enabled() -> bool:
    """Check if Anthropic integration is currently enabled."""
    return _instrumentation_enabled

def update_anthropic_config(config: AnthropicInstrumentationConfig):
    """Update the Anthropic integration configuration."""
    global _instrumentation_config
    _instrumentation_config = config
    logger.info("Anthropic integration configuration updated")

# Convenience functions for common Anthropic patterns

def track_message_completion(client, messages: List[Dict[str, Any]], agent_id: int, api_key: str, **kwargs) -> Any:
    """
    Manually track a single message completion with telemetry.

    Args:
        client: Anthropic client instance
        messages: Messages for completion
        agent_id: Agent ID for telemetry
        api_key: Briefcase AI API key
        **kwargs: Additional arguments for the completion

    Returns:
        Completion result
    """
    # Temporarily enable integration if not already enabled
    was_enabled = _instrumentation_enabled
    if not was_enabled:
        enable_anthropic_integration(agent_id=agent_id, api_key=api_key)

    try:
        result = client.messages.create(messages=messages, **kwargs)
        return result
    finally:
        if not was_enabled:
            disable_anthropic_integration()

def track_completion(client, prompt: str, agent_id: int, api_key: str, **kwargs) -> Any:
    """
    Manually track a single completion with telemetry (legacy API).

    Args:
        client: Anthropic client instance
        prompt: Prompt for completion
        agent_id: Agent ID for telemetry
        api_key: Briefcase AI API key
        **kwargs: Additional arguments for the completion

    Returns:
        Completion result
    """
    # Temporarily enable integration if not already enabled
    was_enabled = _instrumentation_enabled
    if not was_enabled:
        enable_anthropic_integration(agent_id=agent_id, api_key=api_key)

    try:
        result = client.completions.create(prompt=prompt, **kwargs)
        return result
    finally:
        if not was_enabled:
            disable_anthropic_integration()