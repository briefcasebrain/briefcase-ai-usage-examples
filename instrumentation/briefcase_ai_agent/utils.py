"""
Utility functions for AI agent instrumentation.

Includes cost estimation, text sanitization, model information, and helper functions.
"""

import re
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .config import SanitizationRule

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Information about an AI model."""
    name: str
    provider: str
    parameter_count: Optional[int] = None
    input_cost_per_1k: Optional[float] = None  # USD per 1K tokens
    output_cost_per_1k: Optional[float] = None  # USD per 1K tokens
    context_length: Optional[int] = None
    supports_function_calling: bool = False
    supports_streaming: bool = False

# Model pricing and information database (updated as of 2024)
MODEL_DATABASE = {
    # OpenAI Models
    "gpt-4": ModelInfo(
        name="gpt-4",
        provider="openai",
        parameter_count=None,  # Not disclosed
        input_cost_per_1k=0.03,
        output_cost_per_1k=0.06,
        context_length=8192,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    "gpt-4-turbo": ModelInfo(
        name="gpt-4-turbo",
        provider="openai",
        parameter_count=None,
        input_cost_per_1k=0.01,
        output_cost_per_1k=0.03,
        context_length=128000,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    "gpt-4o": ModelInfo(
        name="gpt-4o",
        provider="openai",
        parameter_count=None,
        input_cost_per_1k=0.005,
        output_cost_per_1k=0.015,
        context_length=128000,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    "gpt-4o-mini": ModelInfo(
        name="gpt-4o-mini",
        provider="openai",
        parameter_count=None,
        input_cost_per_1k=0.00015,
        output_cost_per_1k=0.0006,
        context_length=128000,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    "gpt-3.5-turbo": ModelInfo(
        name="gpt-3.5-turbo",
        provider="openai",
        parameter_count=None,
        input_cost_per_1k=0.0005,
        output_cost_per_1k=0.0015,
        context_length=16385,
        supports_function_calling=True,
        supports_streaming=True,
    ),

    # Anthropic Models
    "claude-3-5-sonnet-20241022": ModelInfo(
        name="claude-3-5-sonnet-20241022",
        provider="anthropic",
        parameter_count=None,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        context_length=200000,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    "claude-3-haiku-20240307": ModelInfo(
        name="claude-3-haiku-20240307",
        provider="anthropic",
        parameter_count=None,
        input_cost_per_1k=0.00025,
        output_cost_per_1k=0.00125,
        context_length=200000,
        supports_function_calling=False,
        supports_streaming=True,
    ),

    # Google Models
    "gemini-1.5-pro": ModelInfo(
        name="gemini-1.5-pro",
        provider="google",
        parameter_count=None,
        input_cost_per_1k=0.0035,
        output_cost_per_1k=0.0105,
        context_length=2000000,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    "gemini-1.5-flash": ModelInfo(
        name="gemini-1.5-flash",
        provider="google",
        parameter_count=None,
        input_cost_per_1k=0.000075,
        output_cost_per_1k=0.0003,
        context_length=1000000,
        supports_function_calling=True,
        supports_streaming=True,
    ),

    # Open Source Models (estimated costs for hosted versions)
    "llama-3.1-8b": ModelInfo(
        name="llama-3.1-8b",
        provider="meta",
        parameter_count=8_000_000_000,
        input_cost_per_1k=0.0001,
        output_cost_per_1k=0.0002,
        context_length=128000,
        supports_function_calling=False,
        supports_streaming=True,
    ),
    "llama-3.1-70b": ModelInfo(
        name="llama-3.1-70b",
        provider="meta",
        parameter_count=70_000_000_000,
        input_cost_per_1k=0.0005,
        output_cost_per_1k=0.001,
        context_length=128000,
        supports_function_calling=False,
        supports_streaming=True,
    ),
    "llama-3.1-405b": ModelInfo(
        name="llama-3.1-405b",
        provider="meta",
        parameter_count=405_000_000_000,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.006,
        context_length=128000,
        supports_function_calling=False,
        supports_streaming=True,
    ),
}

def count_tokens_approximate(text: str) -> int:
    """
    Approximate token counting for cost estimation.

    This is a rough approximation. For accurate counting, use the actual
    tokenizer for the specific model.

    Rule of thumb: ~4 characters per token for English text
    """
    if not text:
        return 0

    # Basic approximation: 4 chars per token
    return max(1, len(text) // 4)

def estimate_cost(
    model_name: str,
    input_text: str,
    output_text: str,
    exact_tokens: Optional[Dict[str, int]] = None
) -> float:
    """
    Estimate the cost of an AI model API call.

    Args:
        model_name: Name of the model used
        input_text: Input text sent to the model
        output_text: Output text received from the model
        exact_tokens: Optional dict with 'input' and 'output' token counts

    Returns:
        Estimated cost in USD
    """
    # Normalize model name
    model_name_lower = model_name.lower()

    # Find matching model info
    model_info = None
    for key, info in MODEL_DATABASE.items():
        if key.lower() == model_name_lower or model_name_lower in key.lower():
            model_info = info
            break

    if not model_info:
        logger.warning(f"Unknown model '{model_name}', cannot estimate cost")
        return 0.0

    if model_info.input_cost_per_1k is None or model_info.output_cost_per_1k is None:
        logger.warning(f"No pricing info available for model '{model_name}'")
        return 0.0

    # Get token counts
    if exact_tokens:
        input_tokens = exact_tokens.get('input', 0)
        output_tokens = exact_tokens.get('output', 0)
    else:
        input_tokens = count_tokens_approximate(input_text)
        output_tokens = count_tokens_approximate(output_text)

    # Calculate costs
    input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
    output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k

    total_cost = input_cost + output_cost

    logger.debug(
        f"Cost estimate for {model_name}: "
        f"{input_tokens} input tokens (${input_cost:.6f}) + "
        f"{output_tokens} output tokens (${output_cost:.6f}) = "
        f"${total_cost:.6f}"
    )

    return total_cost

def get_model_info(model_name: str) -> Optional[ModelInfo]:
    """Get information about a specific model."""
    model_name_lower = model_name.lower()

    for key, info in MODEL_DATABASE.items():
        if key.lower() == model_name_lower or model_name_lower in key.lower():
            return info

    return None

def sanitize_text(text: str, rules: List[SanitizationRule]) -> str:
    """
    Sanitize text according to the provided rules.

    Args:
        text: The text to sanitize
        rules: List of sanitization rules to apply

    Returns:
        Sanitized text
    """
    if not text or not rules:
        return text

    sanitized = text

    for rule in rules:
        try:
            if rule.rule_type in ["regex", "pii", "api_key"]:
                # Apply regex pattern
                sanitized = re.sub(
                    rule.pattern,
                    rule.replacement,
                    sanitized,
                    flags=re.IGNORECASE if rule.rule_type != "api_key" else 0
                )
            elif rule.rule_type == "keyword":
                # Simple keyword replacement
                keywords = rule.pattern.split("|")
                for keyword in keywords:
                    sanitized = sanitized.replace(keyword, rule.replacement)

        except re.error as e:
            logger.warning(f"Invalid regex pattern '{rule.pattern}': {e}")
            continue
        except Exception as e:
            logger.warning(f"Error applying sanitization rule: {e}")
            continue

    return sanitized

def extract_model_from_api_response(response_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract model name from API response data.

    Works with OpenAI, Anthropic, and other common API response formats.
    """
    if not isinstance(response_data, dict):
        return None

    # OpenAI format
    if "model" in response_data:
        return response_data["model"]

    # Anthropic format
    if "metadata" in response_data and "model" in response_data["metadata"]:
        return response_data["metadata"]["model"]

    # Check nested structures
    for key in ["response", "choices", "data"]:
        if key in response_data and isinstance(response_data[key], dict):
            if "model" in response_data[key]:
                return response_data[key]["model"]

    return None

def extract_usage_from_api_response(response_data: Dict[str, Any]) -> Optional[Dict[str, int]]:
    """
    Extract token usage from API response data.

    Returns dict with 'input', 'output', and 'total' token counts if available.
    """
    if not isinstance(response_data, dict):
        return None

    usage = {}

    # OpenAI format
    if "usage" in response_data:
        usage_data = response_data["usage"]
        if "prompt_tokens" in usage_data:
            usage["input"] = usage_data["prompt_tokens"]
        if "completion_tokens" in usage_data:
            usage["output"] = usage_data["completion_tokens"]
        if "total_tokens" in usage_data:
            usage["total"] = usage_data["total_tokens"]

    # Anthropic format
    elif "metadata" in response_data and "usage" in response_data["metadata"]:
        usage_data = response_data["metadata"]["usage"]
        if "input_tokens" in usage_data:
            usage["input"] = usage_data["input_tokens"]
        if "output_tokens" in usage_data:
            usage["output"] = usage_data["output_tokens"]

    # Google Gemini format
    elif "usageMetadata" in response_data:
        usage_data = response_data["usageMetadata"]
        if "promptTokenCount" in usage_data:
            usage["input"] = usage_data["promptTokenCount"]
        if "candidatesTokenCount" in usage_data:
            usage["output"] = usage_data["candidatesTokenCount"]
        if "totalTokenCount" in usage_data:
            usage["total"] = usage_data["totalTokenCount"]

    return usage if usage else None

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length, adding suffix if truncated.

    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to add if text is truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    if max_length <= len(suffix):
        return text[:max_length]

    return text[:max_length - len(suffix)] + suffix

def format_duration(duration_seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        duration_seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if duration_seconds < 1:
        return f"{duration_seconds * 1000:.0f}ms"
    elif duration_seconds < 60:
        return f"{duration_seconds:.2f}s"
    elif duration_seconds < 3600:
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        return f"{minutes:.0f}m {seconds:.1f}s"
    else:
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"

def format_cost(cost_usd: float) -> str:
    """
    Format cost in human-readable format.

    Args:
        cost_usd: Cost in USD

    Returns:
        Formatted cost string
    """
    if cost_usd < 0.01:
        return f"${cost_usd:.6f}"
    elif cost_usd < 1:
        return f"${cost_usd:.4f}"
    else:
        return f"${cost_usd:.2f}"

def validate_agent_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate agent configuration and return list of issues.

    Args:
        config: Configuration dictionary

    Returns:
        List of validation error messages
    """
    issues = []

    required_fields = ["agent_id", "api_key"]
    for field in required_fields:
        if field not in config or not config[field]:
            issues.append(f"Missing required field: {field}")

    if "agent_id" in config and not isinstance(config["agent_id"], int):
        issues.append("agent_id must be an integer")

    if "api_key" in config and not isinstance(config["api_key"], str):
        issues.append("api_key must be a string")

    if "consensus_runs" in config:
        runs = config["consensus_runs"]
        if not isinstance(runs, int) or runs < 1 or runs > 10:
            issues.append("consensus_runs must be an integer between 1 and 10")

    if "consensus_threshold" in config:
        threshold = config["consensus_threshold"]
        if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 100):
            issues.append("consensus_threshold must be a number between 0 and 100")

    return issues

def safe_json_serialize(obj: Any) -> str:
    """
    Safely serialize object to JSON, handling common problematic types.

    Args:
        obj: Object to serialize

    Returns:
        JSON string
    """
    def json_serializer(obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif isinstance(obj, Exception):
            return {
                "type": type(obj).__name__,
                "message": str(obj),
                "args": obj.args
            }
        else:
            return str(obj)

    try:
        return json.dumps(obj, default=json_serializer, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to serialize object to JSON: {e}")
        return json.dumps({"error": "Failed to serialize", "type": type(obj).__name__})

def generate_correlation_id() -> str:
    """Generate a unique correlation ID for tracking requests."""
    import uuid
    return str(uuid.uuid4())

def get_system_info() -> Dict[str, Any]:
    """Get basic system information for debugging."""
    import platform
    import sys

    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
        "processor": platform.processor() or "unknown",
    }