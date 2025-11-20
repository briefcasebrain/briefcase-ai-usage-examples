"""
Briefcase AI Agent Instrumentation

High-level Python instrumentation library for AI agent observability.
Built on top of the Briefcase AI Telemetry SDK.

Usage:
    # Decorator approach
    @briefcase_agent(agent_id=123, api_key="your_key")
    def my_agent(prompt):
        return openai.chat.completions.create(...)

    # Context manager approach
    with BriefcaseAgent(agent_id=123, api_key="your_key") as agent:
        response = openai.chat.completions.create(...)
        agent.set_accuracy(95)
        return response
"""

from .core import BriefcaseAgent, briefcase_agent, configure
from .config import BriefcaseConfig
from .integrations import enable_openai_integration, enable_langchain_integration
from .drift import calculate_drift_metrics, DriftCalculator
from .utils import sanitize_text, estimate_cost, get_model_info

__version__ = "0.1.0"
__all__ = [
    "BriefcaseAgent",
    "briefcase_agent",
    "configure",
    "BriefcaseConfig",
    "enable_openai_integration",
    "enable_langchain_integration",
    "calculate_drift_metrics",
    "DriftCalculator",
    "sanitize_text",
    "estimate_cost",
    "get_model_info",
]