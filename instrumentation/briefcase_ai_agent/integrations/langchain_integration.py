"""
LangChain integration for automatic instrumentation.

Monkey-patches LangChain components to automatically capture chain executions,
agent runs, retrievals, and tool usage. Uses the high-performance Rust-based telemetry core.
"""

import functools
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, List
import sys
import os
import json

# Add the SDK to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'python'))
import briefcase_ai_telemetry as bai

logger = logging.getLogger(__name__)

@dataclass
class LangChainInstrumentationConfig:
    """Configuration for LangChain integration."""
    auto_capture_inputs: bool = True
    auto_capture_outputs: bool = True
    auto_calculate_costs: bool = True
    capture_chain_steps: bool = True
    capture_tool_usage: bool = True
    capture_retrieval_docs: bool = False  # Can be large
    capture_agent_thoughts: bool = True
    default_agent_id: Optional[int] = None
    enabled: bool = True
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    max_input_length: int = 10000
    max_output_length: int = 10000

# Global state
_instrumentation_enabled = False
_instrumentation_config = LangChainInstrumentationConfig()
_original_methods = {}
_telemetry_client: Optional[bai.TelemetryClient] = None
_cost_calculator = bai.CostCalculator()

def _truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def _extract_model_from_llm(llm) -> str:
    """Extract model name from LangChain LLM instance."""
    try:
        # OpenAI models
        if hasattr(llm, 'model_name'):
            return llm.model_name
        if hasattr(llm, 'model'):
            return llm.model

        # Anthropic models
        if hasattr(llm, 'model_name'):
            return llm.model_name

        # Hugging Face models
        if hasattr(llm, 'repo_id'):
            return llm.repo_id

        # Generic fallback
        model_class = llm.__class__.__name__
        return f"{model_class.lower()}_model"

    except Exception:
        return "unknown_model"

def _extract_temperature_from_llm(llm) -> Optional[float]:
    """Extract temperature from LangChain LLM instance."""
    try:
        if hasattr(llm, 'temperature'):
            return llm.temperature
        return None
    except Exception:
        return None

def _extract_token_usage(llm_result) -> Optional[Dict[str, int]]:
    """Extract token usage from LangChain LLM result."""
    try:
        if hasattr(llm_result, 'llm_output') and llm_result.llm_output:
            token_usage = llm_result.llm_output.get('token_usage', {})
            if token_usage:
                return {
                    'input': token_usage.get('prompt_tokens', 0),
                    'output': token_usage.get('completion_tokens', 0),
                    'total': token_usage.get('total_tokens', 0),
                }
        return None
    except Exception as e:
        logger.debug(f"Failed to extract token usage: {e}")
        return None

def _instrument_chain_call(original_method):
    """Instrument LangChain Chain.__call__ method."""

    @functools.wraps(original_method)
    def wrapper(self, inputs, *args, **kwargs):
        if not _instrumentation_enabled or not _instrumentation_config.enabled:
            return original_method(self, inputs, *args, **kwargs)

        agent_id = _instrumentation_config.default_agent_id
        if not agent_id or not _telemetry_client:
            return original_method(self, inputs, *args, **kwargs)

        start_time = time.time()

        try:
            # Create instrumentation config
            instr_config = bai.InstrumentationConfig()
            instr_config.with_auto_submit(True)

            # Create agent instrument
            agent = bai.AgentInstrument(agent_id, _telemetry_client, instr_config)
            agent.start()

            # Extract input information
            chain_name = self.__class__.__name__
            if _instrumentation_config.auto_capture_inputs:
                if isinstance(inputs, dict):
                    input_text = json.dumps(inputs, default=str)
                else:
                    input_text = str(inputs)
                input_text = _truncate_text(input_text, _instrumentation_config.max_input_length)
                agent.set_input(input_text)

            # Extract model info if LLM is available
            model_name = "langchain_chain"
            temperature = None
            if hasattr(self, 'llm') and self.llm:
                model_name = _extract_model_from_llm(self.llm)
                temperature = _extract_temperature_from_llm(self.llm)

            agent.set_model_info(model_name, temperature)

            # Add chain metadata
            agent.set_metadata("chain_type", chain_name)
            agent.set_metadata("langchain_component", "chain")

            # Execute the chain
            result = original_method(self, inputs, *args, **kwargs)

            # Extract output information
            if _instrumentation_config.auto_capture_outputs:
                if isinstance(result, dict):
                    output_text = json.dumps(result, default=str)
                else:
                    output_text = str(result)
                output_text = _truncate_text(output_text, _instrumentation_config.max_output_length)
                agent.set_output(output_text)

            # Calculate costs if possible
            if _instrumentation_config.auto_calculate_costs and hasattr(self, 'llm'):
                try:
                    # For chains with direct LLM access, try to estimate cost
                    input_text = json.dumps(inputs, default=str) if isinstance(inputs, dict) else str(inputs)
                    output_text = json.dumps(result, default=str) if isinstance(result, dict) else str(result)

                    cost_estimate = _cost_calculator.estimate_cost(
                        model_name, input_text, output_text
                    )
                    if cost_estimate:
                        agent.set_cost(cost_estimate.total_cost)
                except Exception as e:
                    logger.debug(f"Failed to calculate cost: {e}")

            # Set execution time
            execution_time = time.time() - start_time
            agent.set_metadata("execution_time", execution_time)

            # Submit telemetry
            try:
                agent.finish()
            except Exception as e:
                logger.warning(f"Failed to submit telemetry: {e}")

            return result

        except Exception as e:
            logger.error(f"Error in LangChain chain instrumentation: {e}")
            return original_method(self, inputs, *args, **kwargs)

    return wrapper

def _instrument_llm_generate(original_method):
    """Instrument LangChain LLM.generate method."""

    @functools.wraps(original_method)
    def wrapper(self, prompts, *args, **kwargs):
        if not _instrumentation_enabled or not _instrumentation_config.enabled:
            return original_method(self, prompts, *args, **kwargs)

        agent_id = _instrumentation_config.default_agent_id
        if not agent_id or not _telemetry_client:
            return original_method(self, prompts, *args, **kwargs)

        start_time = time.time()

        try:
            # Create instrumentation config
            instr_config = bai.InstrumentationConfig()
            instr_config.with_auto_submit(True)

            # Create agent instrument
            agent = bai.AgentInstrument(agent_id, _telemetry_client, instr_config)
            agent.start()

            # Extract input information
            if _instrumentation_config.auto_capture_inputs:
                input_text = "\n---\n".join(prompts) if isinstance(prompts, list) else str(prompts)
                input_text = _truncate_text(input_text, _instrumentation_config.max_input_length)
                agent.set_input(input_text)

            # Extract model info
            model_name = _extract_model_from_llm(self)
            temperature = _extract_temperature_from_llm(self)
            agent.set_model_info(model_name, temperature)

            # Add LLM metadata
            agent.set_metadata("llm_class", self.__class__.__name__)
            agent.set_metadata("langchain_component", "llm")

            # Execute the LLM
            result = original_method(self, prompts, *args, **kwargs)

            # Extract output information
            if _instrumentation_config.auto_capture_outputs and hasattr(result, 'generations'):
                outputs = []
                for generation_list in result.generations:
                    for generation in generation_list:
                        if hasattr(generation, 'text'):
                            outputs.append(generation.text)
                output_text = "\n---\n".join(outputs)
                output_text = _truncate_text(output_text, _instrumentation_config.max_output_length)
                agent.set_output(output_text)

            # Extract token usage and calculate costs
            if _instrumentation_config.auto_calculate_costs:
                token_usage = _extract_token_usage(result)
                if token_usage:
                    input_tokens = token_usage['input']
                    output_tokens = token_usage['output']
                    agent.set_token_usage(input_tokens, output_tokens)

                    # Calculate cost using Rust-based calculator
                    input_text = "\n---\n".join(prompts) if isinstance(prompts, list) else str(prompts)
                    output_text = "\n---\n".join(outputs) if 'outputs' in locals() else ""

                    cost_estimate = _cost_calculator.estimate_cost(
                        model_name, input_text, output_text, input_tokens, output_tokens
                    )
                    if cost_estimate:
                        agent.set_cost(cost_estimate.total_cost)

            # Set execution time
            execution_time = time.time() - start_time
            agent.set_metadata("execution_time", execution_time)

            # Submit telemetry
            try:
                agent.finish()
            except Exception as e:
                logger.warning(f"Failed to submit telemetry: {e}")

            return result

        except Exception as e:
            logger.error(f"Error in LangChain LLM instrumentation: {e}")
            return original_method(self, prompts, *args, **kwargs)

    return wrapper

def _instrument_agent_run(original_method):
    """Instrument LangChain Agent._call method."""

    @functools.wraps(original_method)
    def wrapper(self, inputs, *args, **kwargs):
        if not _instrumentation_enabled or not _instrumentation_config.enabled:
            return original_method(self, inputs, *args, **kwargs)

        agent_id = _instrumentation_config.default_agent_id
        if not agent_id or not _telemetry_client:
            return original_method(self, inputs, *args, **kwargs)

        start_time = time.time()

        try:
            # Create instrumentation config
            instr_config = bai.InstrumentationConfig()
            instr_config.with_auto_submit(True)

            # Create agent instrument
            agent = bai.AgentInstrument(agent_id, _telemetry_client, instr_config)
            agent.start()

            # Extract input information
            agent_name = self.__class__.__name__
            if _instrumentation_config.auto_capture_inputs:
                input_text = json.dumps(inputs, default=str) if isinstance(inputs, dict) else str(inputs)
                input_text = _truncate_text(input_text, _instrumentation_config.max_input_length)
                agent.set_input(input_text)

            # Extract model info if LLM is available
            model_name = "langchain_agent"
            temperature = None
            if hasattr(self, 'llm_chain') and hasattr(self.llm_chain, 'llm'):
                model_name = _extract_model_from_llm(self.llm_chain.llm)
                temperature = _extract_temperature_from_llm(self.llm_chain.llm)

            agent.set_model_info(model_name, temperature)

            # Add agent metadata
            agent.set_metadata("agent_type", agent_name)
            agent.set_metadata("langchain_component", "agent")

            # Track available tools
            if hasattr(self, 'tools') and self.tools:
                tool_names = [tool.name for tool in self.tools if hasattr(tool, 'name')]
                agent.set_metadata("available_tools", tool_names)

            # Execute the agent
            result = original_method(self, inputs, *args, **kwargs)

            # Extract output information
            if _instrumentation_config.auto_capture_outputs:
                output_text = json.dumps(result, default=str) if isinstance(result, dict) else str(result)
                output_text = _truncate_text(output_text, _instrumentation_config.max_output_length)
                agent.set_output(output_text)

            # Set execution time
            execution_time = time.time() - start_time
            agent.set_metadata("execution_time", execution_time)

            # Submit telemetry
            try:
                agent.finish()
            except Exception as e:
                logger.warning(f"Failed to submit telemetry: {e}")

            return result

        except Exception as e:
            logger.error(f"Error in LangChain agent instrumentation: {e}")
            return original_method(self, inputs, *args, **kwargs)

    return wrapper

def _instrument_tool_run(original_method):
    """Instrument LangChain Tool._run method."""

    @functools.wraps(original_method)
    def wrapper(self, tool_input, *args, **kwargs):
        if not _instrumentation_enabled or not _instrumentation_config.enabled:
            return original_method(self, tool_input, *args, **kwargs)

        agent_id = _instrumentation_config.default_agent_id
        if not agent_id or not _telemetry_client:
            return original_method(self, tool_input, *args, **kwargs)

        start_time = time.time()

        try:
            # Create instrumentation config
            instr_config = bai.InstrumentationConfig()
            instr_config.with_auto_submit(True)

            # Create agent instrument
            agent = bai.AgentInstrument(agent_id, _telemetry_client, instr_config)
            agent.start()

            # Extract tool information
            tool_name = getattr(self, 'name', self.__class__.__name__)

            if _instrumentation_config.capture_tool_usage:
                # Add as tool call
                agent.add_tool_call(
                    tool_name=tool_name,
                    arguments=str(tool_input),
                    result=None  # Will be set after execution
                )

            # Set metadata
            agent.set_metadata("tool_name", tool_name)
            agent.set_metadata("langchain_component", "tool")

            # Execute the tool
            result = original_method(self, tool_input, *args, **kwargs)

            # Update tool call with result
            if _instrumentation_config.capture_tool_usage:
                agent.add_tool_call(
                    tool_name=tool_name,
                    arguments=str(tool_input),
                    result=str(result)
                )

            # Set execution time
            execution_time = time.time() - start_time
            agent.set_metadata("execution_time", execution_time)

            # Submit telemetry
            try:
                agent.finish()
            except Exception as e:
                logger.warning(f"Failed to submit telemetry: {e}")

            return result

        except Exception as e:
            logger.error(f"Error in LangChain tool instrumentation: {e}")
            return original_method(self, tool_input, *args, **kwargs)

    return wrapper

def enable_langchain_integration(
    agent_id: Optional[int] = None,
    config: Optional[LangChainInstrumentationConfig] = None,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None
) -> bool:
    """
    Enable automatic LangChain instrumentation using Rust-based telemetry.

    Args:
        agent_id: Default agent ID for all LangChain operations
        config: LangChain-specific configuration
        api_key: Briefcase AI API key for telemetry
        endpoint: Optional custom telemetry endpoint

    Returns:
        True if successfully enabled, False otherwise
    """
    global _instrumentation_enabled, _instrumentation_config, _original_methods, _telemetry_client

    try:
        # Try to import LangChain
        try:
            import langchain
            from langchain.schema import BaseLanguageModel
            from langchain.chains.base import Chain
            from langchain.agents.agent import AgentExecutor
            from langchain.tools.base import BaseTool
        except ImportError:
            logger.error("LangChain library not installed. Install with: pip install langchain")
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
            logger.error("agent_id is required for LangChain integration")
            return False

        if not _instrumentation_config.api_key:
            logger.error("api_key is required for LangChain integration")
            return False

        # Create telemetry client
        telemetry_config = bai.TelemetryConfig(_instrumentation_config.api_key)
        if _instrumentation_config.endpoint:
            telemetry_config.with_endpoint(_instrumentation_config.endpoint)

        _telemetry_client = bai.TelemetryClient(telemetry_config)

        # Monkey-patch LangChain components

        # Patch Chain.__call__
        if hasattr(Chain, '__call__'):
            _original_methods['chain_call'] = Chain.__call__
            Chain.__call__ = _instrument_chain_call(Chain.__call__)

        # Patch BaseLanguageModel.generate
        if hasattr(BaseLanguageModel, 'generate'):
            _original_methods['llm_generate'] = BaseLanguageModel.generate
            BaseLanguageModel.generate = _instrument_llm_generate(BaseLanguageModel.generate)

        # Patch AgentExecutor._call (if available)
        if hasattr(AgentExecutor, '_call'):
            _original_methods['agent_call'] = AgentExecutor._call
            AgentExecutor._call = _instrument_agent_run(AgentExecutor._call)

        # Patch BaseTool._run
        if hasattr(BaseTool, '_run'):
            _original_methods['tool_run'] = BaseTool._run
            BaseTool._run = _instrument_tool_run(BaseTool._run)

        _instrumentation_enabled = True
        logger.info(f"LangChain integration enabled for agent {_instrumentation_config.default_agent_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to enable LangChain integration: {e}")
        return False

def disable_langchain_integration() -> bool:
    """Disable LangChain instrumentation and restore original methods."""
    global _instrumentation_enabled, _original_methods, _telemetry_client

    try:
        # Restore original methods
        if 'chain_call' in _original_methods:
            from langchain.chains.base import Chain
            Chain.__call__ = _original_methods['chain_call']

        if 'llm_generate' in _original_methods:
            from langchain.schema import BaseLanguageModel
            BaseLanguageModel.generate = _original_methods['llm_generate']

        if 'agent_call' in _original_methods:
            from langchain.agents.agent import AgentExecutor
            AgentExecutor._call = _original_methods['agent_call']

        if 'tool_run' in _original_methods:
            from langchain.tools.base import BaseTool
            BaseTool._run = _original_methods['tool_run']

        _original_methods.clear()
        _telemetry_client = None
        _instrumentation_enabled = False
        logger.info("LangChain integration disabled")
        return True

    except Exception as e:
        logger.error(f"Failed to disable LangChain integration: {e}")
        return False

def is_langchain_integration_enabled() -> bool:
    """Check if LangChain integration is currently enabled."""
    return _instrumentation_enabled

def update_langchain_config(config: LangChainInstrumentationConfig):
    """Update the LangChain integration configuration."""
    global _instrumentation_config
    _instrumentation_config = config
    logger.info("LangChain integration configuration updated")

# Convenience functions for common LangChain patterns

def track_chain_execution(chain, inputs: Dict[str, Any], agent_id: int, api_key: str) -> Any:
    """
    Manually track a single chain execution with telemetry.

    Args:
        chain: LangChain chain instance
        inputs: Chain inputs
        agent_id: Agent ID for telemetry
        api_key: Briefcase AI API key

    Returns:
        Chain execution result
    """
    # Temporarily enable integration if not already enabled
    was_enabled = _instrumentation_enabled
    if not was_enabled:
        enable_langchain_integration(agent_id=agent_id, api_key=api_key)

    try:
        result = chain(inputs)
        return result
    finally:
        if not was_enabled:
            disable_langchain_integration()

def track_agent_execution(agent, inputs: Dict[str, Any], agent_id: int, api_key: str) -> Any:
    """
    Manually track a single agent execution with telemetry.

    Args:
        agent: LangChain agent instance
        inputs: Agent inputs
        agent_id: Agent ID for telemetry
        api_key: Briefcase AI API key

    Returns:
        Agent execution result
    """
    # Temporarily enable integration if not already enabled
    was_enabled = _instrumentation_enabled
    if not was_enabled:
        enable_langchain_integration(agent_id=agent_id, api_key=api_key)

    try:
        result = agent(inputs)
        return result
    finally:
        if not was_enabled:
            disable_langchain_integration()