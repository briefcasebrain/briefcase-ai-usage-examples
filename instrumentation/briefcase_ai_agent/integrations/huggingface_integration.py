"""
Hugging Face Integration for Briefcase AI Telemetry

Provides automatic telemetry capture for Hugging Face Transformers library including:
- Text generation models (GPT, T5, BART, etc.)
- Text classification models
- Question answering models
- Named entity recognition models
- Text summarization models
- Translation models
- Feature extraction models

Features:
- Automatic input/output capture
- Token count estimation
- Cost estimation for paid models
- Latency tracking
- Error capture and analysis
- Model metadata extraction
- Inference parameter tracking
"""

import functools
import time
import sys
import os
from typing import Any, Dict, Optional, List, Union
import logging

# Add Rust core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'python'))
import briefcase_ai_telemetry as bai

logger = logging.getLogger(__name__)

# Global state
_telemetry_client: Optional[bai.TelemetryClient] = None
_agent_id: Optional[int] = None
_instrumentation_config: Optional[bai.InstrumentationConfig] = None
_enabled = False

def enable_huggingface_integration(
    agent_id: int,
    api_key: str,
    endpoint: str = "https://observe.briefcasebrain.io/api/v1/telemetry",
    auto_capture_inputs: bool = True,
    auto_capture_outputs: bool = True,
    auto_calculate_costs: bool = True,
    max_input_length: int = 10000,
    max_output_length: int = 10000,
    capture_model_info: bool = True,
    capture_inference_params: bool = True,
) -> None:
    """
    Enable Briefcase AI telemetry for Hugging Face Transformers.

    Args:
        agent_id: Unique identifier for this agent
        api_key: Briefcase AI API key
        endpoint: Telemetry endpoint URL
        auto_capture_inputs: Whether to automatically capture inputs
        auto_capture_outputs: Whether to automatically capture outputs
        auto_calculate_costs: Whether to automatically calculate costs
        max_input_length: Maximum input text length to capture
        max_output_length: Maximum output text length to capture
        capture_model_info: Whether to capture model metadata
        capture_inference_params: Whether to capture inference parameters
    """
    global _telemetry_client, _agent_id, _instrumentation_config, _enabled

    try:
        # Initialize telemetry client
        _telemetry_client = bai.TelemetryClient(api_key, endpoint)
        _agent_id = agent_id

        # Create instrumentation config
        _instrumentation_config = bai.InstrumentationConfig(
            auto_capture_inputs=auto_capture_inputs,
            auto_capture_outputs=auto_capture_outputs,
            auto_calculate_costs=auto_calculate_costs,
            max_input_length=max_input_length,
            max_output_length=max_output_length
        )

        # Store HuggingFace-specific config
        _instrumentation_config.capture_model_info = capture_model_info
        _instrumentation_config.capture_inference_params = capture_inference_params

        # Patch HuggingFace classes
        _patch_transformers()

        _enabled = True
        logger.info(f"Hugging Face integration enabled for agent {agent_id}")

    except Exception as e:
        logger.error(f"Failed to enable Hugging Face integration: {e}")
        raise

def disable_huggingface_integration():
    """Disable Hugging Face telemetry integration."""
    global _enabled
    _enabled = False
    _unpatch_transformers()
    logger.info("Hugging Face integration disabled")

def _patch_transformers():
    """Patch Hugging Face Transformers classes for telemetry."""
    try:
        import transformers

        # Patch Pipeline classes
        _patch_pipeline()

        # Patch PreTrainedModel classes
        _patch_pretrained_model()

        # Patch Tokenizer classes
        _patch_tokenizer()

        logger.info("Hugging Face Transformers classes patched for telemetry")

    except ImportError:
        logger.warning("transformers library not available")
    except Exception as e:
        logger.error(f"Failed to patch transformers: {e}")

def _patch_pipeline():
    """Patch transformers.Pipeline for telemetry."""
    try:
        from transformers import Pipeline

        # Store original method
        if not hasattr(Pipeline, '_original_call'):
            Pipeline._original_call = Pipeline.__call__

        def instrumented_call(self, inputs, *args, **kwargs):
            if not _enabled or not _telemetry_client:
                return self._original_call(inputs, *args, **kwargs)

            return _capture_pipeline_call(self, inputs, *args, **kwargs)

        Pipeline.__call__ = instrumented_call

    except Exception as e:
        logger.error(f"Failed to patch Pipeline: {e}")

def _patch_pretrained_model():
    """Patch PreTrainedModel for telemetry."""
    try:
        from transformers import PreTrainedModel

        # Patch generate method
        if not hasattr(PreTrainedModel, '_original_generate'):
            PreTrainedModel._original_generate = PreTrainedModel.generate

        def instrumented_generate(self, inputs=None, *args, **kwargs):
            if not _enabled or not _telemetry_client:
                return self._original_generate(inputs, *args, **kwargs)

            return _capture_model_generate(self, inputs, *args, **kwargs)

        PreTrainedModel.generate = instrumented_generate

        # Patch forward method
        if not hasattr(PreTrainedModel, '_original_forward'):
            PreTrainedModel._original_forward = PreTrainedModel.forward

        def instrumented_forward(self, *args, **kwargs):
            if not _enabled or not _telemetry_client:
                return self._original_forward(*args, **kwargs)

            return _capture_model_forward(self, *args, **kwargs)

        PreTrainedModel.forward = instrumented_forward

    except Exception as e:
        logger.error(f"Failed to patch PreTrainedModel: {e}")

def _patch_tokenizer():
    """Patch tokenizers for telemetry."""
    try:
        from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast

        # Patch encode methods
        for tokenizer_class in [PreTrainedTokenizer, PreTrainedTokenizerFast]:
            if not hasattr(tokenizer_class, '_original_encode'):
                tokenizer_class._original_encode = tokenizer_class.encode

            def instrumented_encode(self, text, *args, **kwargs):
                if not _enabled or not _telemetry_client:
                    return self._original_encode(text, *args, **kwargs)

                return _capture_tokenizer_encode(self, text, *args, **kwargs)

            tokenizer_class.encode = instrumented_encode

    except Exception as e:
        logger.error(f"Failed to patch tokenizers: {e}")

def _capture_pipeline_call(pipeline, inputs, *args, **kwargs):
    """Capture telemetry for Pipeline.__call__."""
    agent = bai.AgentInstrument(_agent_id, _telemetry_client, _instrumentation_config)

    try:
        agent.start()

        # Prepare input data
        input_text = _extract_text_from_inputs(inputs)
        agent.add_input(input_text)

        # Capture model metadata
        if _instrumentation_config.capture_model_info:
            model_info = {
                "model_name": getattr(pipeline.model, 'name_or_path', 'unknown'),
                "task": pipeline.task,
                "framework": "huggingface",
                "model_type": pipeline.model.__class__.__name__,
                "tokenizer_type": pipeline.tokenizer.__class__.__name__,
                "device": str(pipeline.device),
            }
            agent.add_metadata("model_info", model_info)

        # Capture inference parameters
        if _instrumentation_config.capture_inference_params:
            inference_params = {
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k not in ['return_tensors']},
            }
            agent.add_metadata("inference_params", inference_params)

        # Execute original method
        start_time = time.time()
        result = pipeline._original_call(inputs, *args, **kwargs)
        latency = time.time() - start_time

        # Capture output
        output_text = _extract_text_from_outputs(result, pipeline.task)
        agent.add_output(output_text)

        # Estimate tokens and cost
        if _instrumentation_config.auto_calculate_costs:
            input_tokens, output_tokens = _estimate_tokens(input_text, output_text, pipeline)

            cost_estimate = _estimate_cost(
                model_name=getattr(pipeline.model, 'name_or_path', 'unknown'),
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

            if cost_estimate:
                agent.add_metadata("cost_estimate", {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": cost_estimate
                })

        # Add performance metrics
        agent.add_metadata("performance", {
            "latency_seconds": latency,
            "success": True
        })

        return result

    except Exception as e:
        agent.add_error(str(e))
        agent.add_metadata("performance", {
            "success": False,
            "error": str(e)
        })
        raise

    finally:
        agent.end()

def _capture_model_generate(model, inputs, *args, **kwargs):
    """Capture telemetry for model.generate()."""
    agent = bai.AgentInstrument(_agent_id, _telemetry_client, _instrumentation_config)

    try:
        agent.start()

        # Extract input text
        input_text = _extract_text_from_tensor_inputs(inputs, model)
        agent.add_input(input_text)

        # Capture model info
        if _instrumentation_config.capture_model_info:
            model_info = {
                "model_name": getattr(model, 'name_or_path', 'unknown'),
                "model_type": model.__class__.__name__,
                "framework": "huggingface",
                "config": getattr(model, 'config', {}).to_dict() if hasattr(getattr(model, 'config', None), 'to_dict') else {}
            }
            agent.add_metadata("model_info", model_info)

        # Capture generation parameters
        if _instrumentation_config.capture_inference_params:
            generation_params = {k: v for k, v in kwargs.items() if k not in ['input_ids', 'attention_mask']}
            agent.add_metadata("generation_params", generation_params)

        # Execute generation
        start_time = time.time()
        result = model._original_generate(inputs, *args, **kwargs)
        latency = time.time() - start_time

        # Extract output text
        output_text = _extract_text_from_tensor_outputs(result, model)
        agent.add_output(output_text)

        # Estimate cost
        if _instrumentation_config.auto_calculate_costs:
            input_tokens = _count_tokens_from_tensor(inputs)
            output_tokens = _count_tokens_from_tensor(result)

            cost_estimate = _estimate_cost(
                model_name=getattr(model, 'name_or_path', 'unknown'),
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

            if cost_estimate:
                agent.add_metadata("cost_estimate", {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": cost_estimate
                })

        agent.add_metadata("performance", {
            "latency_seconds": latency,
            "success": True
        })

        return result

    except Exception as e:
        agent.add_error(str(e))
        agent.add_metadata("performance", {
            "success": False,
            "error": str(e)
        })
        raise

    finally:
        agent.end()

def _capture_model_forward(model, *args, **kwargs):
    """Capture telemetry for model.forward()."""
    # Only capture forward calls for inference, not training
    if model.training:
        return model._original_forward(*args, **kwargs)

    agent = bai.AgentInstrument(_agent_id, _telemetry_client, _instrumentation_config)

    try:
        agent.start()

        # Extract relevant information from inputs
        input_info = _extract_forward_inputs(*args, **kwargs)
        if input_info:
            agent.add_input(str(input_info))

        # Model metadata
        if _instrumentation_config.capture_model_info:
            model_info = {
                "model_name": getattr(model, 'name_or_path', 'unknown'),
                "model_type": model.__class__.__name__,
                "framework": "huggingface"
            }
            agent.add_metadata("model_info", model_info)

        # Execute forward pass
        start_time = time.time()
        result = model._original_forward(*args, **kwargs)
        latency = time.time() - start_time

        # Extract output information
        output_info = _extract_forward_outputs(result)
        if output_info:
            agent.add_output(str(output_info))

        agent.add_metadata("performance", {
            "latency_seconds": latency,
            "success": True
        })

        return result

    except Exception as e:
        agent.add_error(str(e))
        agent.add_metadata("performance", {
            "success": False,
            "error": str(e)
        })
        raise

    finally:
        agent.end()

def _capture_tokenizer_encode(tokenizer, text, *args, **kwargs):
    """Capture telemetry for tokenizer.encode()."""
    if not _instrumentation_config.capture_inference_params:
        return tokenizer._original_encode(text, *args, **kwargs)

    agent = bai.AgentInstrument(_agent_id, _telemetry_client, _instrumentation_config)

    try:
        agent.start()

        agent.add_input(str(text))

        # Tokenizer metadata
        tokenizer_info = {
            "tokenizer_type": tokenizer.__class__.__name__,
            "vocab_size": tokenizer.vocab_size,
            "model_max_length": getattr(tokenizer, 'model_max_length', None)
        }
        agent.add_metadata("tokenizer_info", tokenizer_info)

        # Execute encoding
        start_time = time.time()
        result = tokenizer._original_encode(text, *args, **kwargs)
        latency = time.time() - start_time

        # Add token count and encoding info
        agent.add_metadata("encoding_result", {
            "token_count": len(result) if isinstance(result, list) else None,
            "latency_seconds": latency
        })

        return result

    except Exception as e:
        agent.add_error(str(e))
        raise

    finally:
        agent.end()

def _extract_text_from_inputs(inputs) -> str:
    """Extract text from various input formats."""
    if isinstance(inputs, str):
        return inputs
    elif isinstance(inputs, list):
        if all(isinstance(item, str) for item in inputs):
            return " ".join(inputs)
        else:
            return str(inputs)
    elif isinstance(inputs, dict):
        # Look for common text keys
        for key in ['text', 'question', 'context', 'input', 'prompt']:
            if key in inputs:
                return str(inputs[key])
        return str(inputs)
    else:
        return str(inputs)

def _extract_text_from_outputs(outputs, task: str) -> str:
    """Extract text from pipeline outputs based on task type."""
    if isinstance(outputs, str):
        return outputs
    elif isinstance(outputs, list):
        if len(outputs) > 0:
            output = outputs[0]
            if isinstance(output, dict):
                # Different tasks have different output formats
                if task in ['text-generation', 'text2text-generation']:
                    return output.get('generated_text', str(output))
                elif task == 'text-classification':
                    return f"Label: {output.get('label', '')}, Score: {output.get('score', '')}"
                elif task == 'question-answering':
                    return output.get('answer', str(output))
                elif task == 'summarization':
                    return output.get('summary_text', str(output))
                elif task == 'translation':
                    return output.get('translation_text', str(output))
                else:
                    return str(output)
            else:
                return str(output)
        return str(outputs)
    elif isinstance(outputs, dict):
        # Handle single dict output
        if task in ['text-generation', 'text2text-generation']:
            return outputs.get('generated_text', str(outputs))
        elif task == 'question-answering':
            return outputs.get('answer', str(outputs))
        else:
            return str(outputs)
    else:
        return str(outputs)

def _extract_text_from_tensor_inputs(inputs, model) -> str:
    """Extract text from tensor inputs using model's tokenizer."""
    try:
        if hasattr(model, 'tokenizer'):
            return model.tokenizer.decode(inputs[0], skip_special_tokens=True)
        elif hasattr(inputs, 'shape'):
            return f"Tensor input with shape {inputs.shape}"
        else:
            return str(inputs)
    except Exception:
        return str(inputs)

def _extract_text_from_tensor_outputs(outputs, model) -> str:
    """Extract text from tensor outputs using model's tokenizer."""
    try:
        if hasattr(model, 'tokenizer') and hasattr(outputs, 'shape'):
            # For generation, typically decode the last generated sequence
            if len(outputs.shape) >= 2:
                return model.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return str(outputs)
    except Exception:
        return str(outputs)

def _extract_forward_inputs(*args, **kwargs) -> Optional[Dict]:
    """Extract relevant information from forward() inputs."""
    try:
        info = {}

        # Common input keys
        for key in ['input_ids', 'attention_mask', 'token_type_ids', 'position_ids']:
            if key in kwargs and kwargs[key] is not None:
                tensor = kwargs[key]
                if hasattr(tensor, 'shape'):
                    info[f"{key}_shape"] = list(tensor.shape)

        # Add batch size if available
        if 'input_ids' in kwargs and hasattr(kwargs['input_ids'], 'shape'):
            info['batch_size'] = kwargs['input_ids'].shape[0]
            info['sequence_length'] = kwargs['input_ids'].shape[1]

        return info if info else None

    except Exception:
        return None

def _extract_forward_outputs(outputs) -> Optional[Dict]:
    """Extract relevant information from forward() outputs."""
    try:
        info = {}

        if hasattr(outputs, 'last_hidden_state') and hasattr(outputs.last_hidden_state, 'shape'):
            info['hidden_state_shape'] = list(outputs.last_hidden_state.shape)

        if hasattr(outputs, 'logits') and hasattr(outputs.logits, 'shape'):
            info['logits_shape'] = list(outputs.logits.shape)

        if hasattr(outputs, 'loss') and outputs.loss is not None:
            info['loss'] = float(outputs.loss)

        return info if info else None

    except Exception:
        return None

def _count_tokens_from_tensor(tensor) -> int:
    """Estimate token count from tensor shape."""
    try:
        if hasattr(tensor, 'shape'):
            if len(tensor.shape) >= 2:
                return tensor.shape[1]  # Sequence length
            elif len(tensor.shape) == 1:
                return tensor.shape[0]
        return 0
    except Exception:
        return 0

def _estimate_tokens(input_text: str, output_text: str, pipeline) -> tuple[int, int]:
    """Estimate token counts for input and output text."""
    try:
        if hasattr(pipeline, 'tokenizer'):
            input_tokens = len(pipeline.tokenizer.encode(input_text))
            output_tokens = len(pipeline.tokenizer.encode(output_text))
            return input_tokens, output_tokens
        else:
            # Rough estimation: ~4 chars per token
            input_tokens = len(input_text) // 4
            output_tokens = len(output_text) // 4
            return input_tokens, output_tokens
    except Exception:
        # Fallback estimation
        return len(input_text) // 4, len(output_text) // 4

def _estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Estimate cost for model usage."""
    try:
        cost_calculator = bai.CostCalculator()

        cost_estimate = cost_calculator.estimate_cost(
            model_name,
            "",  # input_text (not needed for token-based calculation)
            "",  # output_text (not needed for token-based calculation)
            input_tokens,
            output_tokens
        )

        return cost_estimate.total_cost if cost_estimate else None

    except Exception as e:
        logger.warning(f"Cost estimation failed: {e}")
        return None

def _unpatch_transformers():
    """Remove patches from Hugging Face Transformers classes."""
    try:
        import transformers

        # Restore Pipeline
        from transformers import Pipeline
        if hasattr(Pipeline, '_original_call'):
            Pipeline.__call__ = Pipeline._original_call
            delattr(Pipeline, '_original_call')

        # Restore PreTrainedModel
        from transformers import PreTrainedModel
        if hasattr(PreTrainedModel, '_original_generate'):
            PreTrainedModel.generate = PreTrainedModel._original_generate
            delattr(PreTrainedModel, '_original_generate')

        if hasattr(PreTrainedModel, '_original_forward'):
            PreTrainedModel.forward = PreTrainedModel._original_forward
            delattr(PreTrainedModel, '_original_forward')

        # Restore Tokenizers
        from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast
        for tokenizer_class in [PreTrainedTokenizer, PreTrainedTokenizerFast]:
            if hasattr(tokenizer_class, '_original_encode'):
                tokenizer_class.encode = tokenizer_class._original_encode
                delattr(tokenizer_class, '_original_encode')

        logger.info("Hugging Face Transformers patches removed")

    except Exception as e:
        logger.error(f"Failed to unpatch transformers: {e}")

# Utility functions for common HuggingFace workflows

def create_instrumented_pipeline(task: str, model: str = None, **kwargs):
    """Create a Hugging Face pipeline with telemetry enabled."""
    try:
        from transformers import pipeline

        # Create pipeline
        pipe = pipeline(task, model=model, **kwargs)

        # Ensure telemetry is enabled
        if not _enabled:
            logger.warning("Hugging Face telemetry not enabled. Call enable_huggingface_integration() first.")

        return pipe

    except ImportError:
        raise ImportError("transformers library not installed")

def instrument_existing_pipeline(pipe):
    """Add telemetry to an existing pipeline."""
    if not _enabled:
        logger.warning("Hugging Face telemetry not enabled. Call enable_huggingface_integration() first.")
        return pipe

    # Telemetry is automatically applied through patches
    return pipe