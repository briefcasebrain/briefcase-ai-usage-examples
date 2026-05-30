"""Data lineage and versioning demo.

Shows how every DecisionSnapshot is traceable to a specific data version,
demonstrates drift detection when source data changes, emits structured
events on drift, validates evidence references before summarization,
and generates compliance reports.
"""

import hashlib
import asyncio
from pathlib import Path
from briefcase.drift import DriftCalculator
from briefcase.external_data import ExternalDataTracker, SnapshotPolicy, SnapshotFrequency
from briefcase.events.emitter import emit_drift_detected

from src.mock_llm import MockLLMProvider
from src.pipeline import summarize_report
from src.validation import validate_prompt


def load_versioned_report(filepath: str) -> tuple:
    """Load report with version hash (simulates lakeFS commit SHA)."""
    content = Path(filepath).read_text()
    version_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
    return content, version_hash


async def demo_lineage() -> dict:
    """Show data lineage: every decision linked to its source version.

    Validates evidence references before each summarization call.
    """
    llm = MockLLMProvider(model="gpt-4o", simulate_latency=False)

    # Validate references before summarization
    v1_validation = validate_prompt("Summarize report_001")
    v2_validation = validate_prompt("Summarize report_001_amended")

    # Run on original report
    text_v1, hash_v1 = load_versioned_report("data/police_reports/report_001.txt")
    result_v1 = await summarize_report("report_001", text_v1, llm=llm)

    # Run on amended report
    text_v2, hash_v2 = load_versioned_report("data/police_reports/report_001_amended.txt")
    amended_llm = MockLLMProvider(model="gpt-4o", simulate_latency=False)
    result_v2 = await summarize_report("report_001_amended", text_v2, llm=amended_llm)

    summary_changed = result_v1["summary"] != result_v2["summary"]

    return {
        "v1_hash": hash_v1,
        "v2_hash": hash_v2,
        "v1_snapshot": result_v1["snapshot_id"],
        "v2_snapshot": result_v2["snapshot_id"],
        "v1_summary": result_v1["summary"],
        "v2_summary": result_v2["summary"],
        "version_changed": hash_v1 != hash_v2,
        "summary_changed": summary_changed,
        "v1_validation": v1_validation.status,
        "v2_validation": v2_validation.status,
    }


async def demo_drift(lineage: dict) -> dict:
    """Show output drift when source data changes using DriftCalculator.

    Emits a drift.detected event when drift is measured.

    Args:
        lineage: Results from demo_lineage() containing v1/v2 summaries.
    """
    # DriftCalculator compares output strings
    drift_calc = DriftCalculator()
    drift_metrics = drift_calc.calculate_drift([
        lineage["v1_summary"],
        lineage["v2_summary"],
    ])

    # Emit structured drift event
    await emit_drift_detected(None, {
        "drift_score": drift_metrics.drift_score,
        "consistency_score": drift_metrics.consistency_score,
        "source": "lineage_comparison",
    })

    return {
        "lineage": lineage,
        "drift_score": drift_metrics.drift_score,
        "consistency_score": drift_metrics.consistency_score,
    }


def demo_external_data_tracking() -> dict:
    """Demonstrate ExternalDataTracker for monitoring external data sources.

    Tracks file fetches, applies snapshot policies, and detects drift
    when the underlying data changes between versions.
    """
    # Step 1: Create tracker
    tracker = ExternalDataTracker()

    # Step 2: Set a snapshot policy — snapshot on every change
    policy = SnapshotPolicy(frequency=SnapshotFrequency.ON_CHANGE)
    tracker.set_policy("evidence_reports", policy)

    # Step 3: Track initial file fetch (original report) — establishes baseline
    file_path = "data/police_reports/report_001.txt"
    file_bytes = Path(file_path).read_bytes()
    tracker.track_file_fetch("evidence_reports", file_bytes, file_path="report_001.txt")

    # Step 4: Detect drift by comparing baseline against amended version
    # (without tracking the amended version first — simulates "has my source changed?")
    amended_path = "data/police_reports/report_001_amended.txt"
    amended_bytes = Path(amended_path).read_bytes()
    drift_report = tracker.detect_drift(
        "evidence_reports", current_data=amended_bytes
    )

    return {
        "has_changed": drift_report.has_changed,
        "drift_score": drift_report.drift_score,
        "size_delta": drift_report.size_delta,
        "baseline_hash": drift_report.baseline_hash,
        "current_hash": drift_report.current_hash,
    }


async def main():
    print("=== Data Lineage Demo ===")
    lineage = await demo_lineage()
    print(f"  v1: hash={lineage['v1_hash']}, snapshot={lineage['v1_snapshot']}")
    print(f"      validation: {lineage['v1_validation']}")
    print(f"  v2: hash={lineage['v2_hash']}, snapshot={lineage['v2_snapshot']}")
    print(f"      validation: {lineage['v2_validation']}")
    print(f"  Version changed: {lineage['version_changed']}")
    print(f"  Summary changed: {lineage['summary_changed']}")

    print("\n=== Drift Detection Demo ===")
    drift = await demo_drift(lineage)
    print(f"  Drift score: {drift['drift_score']:.3f}")
    print(f"  Consistency score: {drift['consistency_score']:.3f}")

    print("\n=== External Data Tracking Demo ===")
    ext_tracking = demo_external_data_tracking()
    print(f"  Data changed: {ext_tracking['has_changed']}")
    print(f"  Drift score: {ext_tracking['drift_score']:.3f}")
    print(f"  Size delta: {ext_tracking['size_delta']} bytes")
    print(f"  Baseline hash: {ext_tracking['baseline_hash']}")
    print(f"  Current hash: {ext_tracking['current_hash']}")


if __name__ == "__main__":
    asyncio.run(main())
