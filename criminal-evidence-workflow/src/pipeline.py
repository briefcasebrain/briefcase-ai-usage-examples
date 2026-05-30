"""Instrumented RAG pipeline for criminal evidence summarization.

Uses Briefcase AI SDK to record every LLM decision with full lineage:
inputs, outputs, model parameters, execution time, data versioning,
and hardware metadata for reproducibility.
"""

import hashlib
import sys
import time
import asyncio

import platform

import briefcase
# DataRef is a native-only type (no public re-export)
from briefcase._native import DataRef
from briefcase.correlation import briefcase_workflow
from briefcase.decorators import capture
from briefcase.hardware import detect_hardware

from src.config import storage
from src.mock_llm import MockLLMProvider


@capture(decision_type="evidence_summarization")
async def summarize_report(
    report_id: str,
    report_text: str,
    query: str = "Summarize this police report",
    llm: MockLLMProvider = None,
    replay: bool = False,
) -> dict:
    """Summarize a police report and record the decision in Briefcase AI.

    The @capture decorator auto-records inputs, outputs, timing, and errors.
    DecisionSnapshot handles persistence for downstream replay/routing/lineage.
    """
    llm = llm or MockLLMProvider(simulate_latency=False)

    with briefcase_workflow("evidence_summarization", None) as workflow:
        decision = briefcase.DecisionSnapshot("summarize_evidence")

        # Record inputs
        decision = decision.add_input(
            briefcase.Input("document", report_text, "string")
        )
        decision = decision.add_input(
            briefcase.Input("query", query, "string")
        )

        # Model parameters
        config = llm.model_config
        params = briefcase.ModelParameters(config["model"])
        params = params.with_provider(config["provider"])
        params = params.with_parameter("temperature", str(config["temperature"]))
        params = params.with_parameter("max_tokens", "2000")
        decision = decision.with_model_parameters(params)

        # Execution context
        exec_ctx = briefcase.ExecutionContext()
        exec_ctx = exec_ctx.with_runtime_version(f"python-{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        exec_ctx = exec_ctx.with_dependency("briefcase-ai", briefcase.__version__)
        exec_ctx = exec_ctx.with_random_seed(42)
        decision = decision.add_tag("runtime_version", exec_ctx.runtime_version)
        decision = decision.add_tag("briefcase_version", briefcase.__version__)

        # Data version (content hash — simulates lakeFS commit SHA)
        content_hash = hashlib.sha256(report_text.encode()).hexdigest()[:12]
        decision = decision.add_tag("data_version", content_hash)
        decision = decision.add_tag("report_id", report_id)

        # Data reference
        data_ref_uri = f"file://data/police_reports/{report_id}.txt"
        data_ref = DataRef(data_ref_uri, content_hash)
        data_ref = data_ref.with_version(content_hash)
        decision = decision.add_tag("data_ref_uri", data_ref_uri)

        # Hardware metadata for reproducibility
        hw = detect_hardware()
        system = platform.system()
        machine = platform.machine().lower()
        if system == "Darwin" and machine.startswith("arm"):
            hw_type, hw_name = "metal", "Apple Silicon"
        else:
            hw_type = "cpu"
            hw_name = platform.processor() or "generic"
        decision = decision.add_tag("hardware_type", hw_type)
        decision = decision.add_tag("hardware_name", hw_name)

        # ---- "LLM call" (mocked by default) ----
        start = time.monotonic()
        result = await llm.generate(report_id, query, replay=replay)
        elapsed_ms = (time.monotonic() - start) * 1000

        # Record output
        output = briefcase.Output("summary", result["summary"], "string")
        output = output.with_confidence(result["confidence"])
        decision = decision.add_output(output)
        decision = decision.with_execution_time(elapsed_ms)

        # Persist
        snapshot_id = storage.save_decision(decision)

        return {
            "summary": result["summary"],
            "confidence": result["confidence"],
            "snapshot_id": snapshot_id,
            "decision": decision,
            "data_version": content_hash,
            "token_usage": result["token_usage"],
            "model": result["model"],
            "provider": result.get("provider", "unknown"),
            "latency_ms": elapsed_ms,
            "hardware_type": hw_type,
            "hardware_name": hw_name,
        }


async def main():
    """Quick self-test: summarize report_001 with mocked LLM."""
    from pathlib import Path

    report_path = Path("data/police_reports/report_001.txt")
    report_text = report_path.read_text()

    result = await summarize_report("report_001", report_text)

    print(f"Report: report_001")
    print(f"Model: {result['model']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Snapshot ID: {result['snapshot_id']}")
    print(f"Data Version: {result['data_version']}")
    print(f"Hardware: {result['hardware_type']} ({result['hardware_name']})")
    print(f"Latency: {result['latency_ms']:.0f}ms")
    print(f"\nSummary:\n{result['summary'][:300]}...")


if __name__ == "__main__":
    asyncio.run(main())
