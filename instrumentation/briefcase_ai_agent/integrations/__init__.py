"""
Framework integrations for automatic instrumentation.

Supports popular AI/ML frameworks with minimal code changes.
"""

from .openai_integration import enable_openai_integration, OpenAIInstrumentationConfig
from .anthropic_integration import enable_anthropic_integration
from .langchain_integration import enable_langchain_integration, BriefcaseLangchainCallback
from .huggingface_integration import enable_huggingface_integration, create_instrumented_pipeline

__all__ = [
    "enable_openai_integration",
    "enable_anthropic_integration",
    "enable_langchain_integration",
    "enable_huggingface_integration",
    "OpenAIInstrumentationConfig",
    "BriefcaseLangchainCallback",
    "create_instrumented_pipeline",
]