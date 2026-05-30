"""Error reproduction and triage: ReplayEngine + ConfidenceRouter.

Demonstrates:
1. Deterministic replay catching stochastic failures
2. Confidence-based routing to human review
3. Structured event emission on drift and low confidence
"""

import asyncio
from pathlib import Path

import time

from briefcase.replay import ReplayEngine
from briefcase.drift import DriftCalculator
from briefcase.routing import BaseRouter, RoutingDecision
from briefcase.events.emitter import emit_low_confidence, emit_drift_detected

from src.mock_llm import MockLLMProvider
from src.pipeline import summarize_report
from src.config import storage


class ConfidenceRouter(BaseRouter):
    """Routes decisions based on output confidence threshold."""

    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold

    async def route(self, decision_context) -> RoutingDecision:
        start = time.monotonic()
        confidence = 0.0
        for out in decision_context.outputs:
            if out.confidence is not None:
                confidence = out.confidence
                break

        if confidence < self.confidence_threshold:
            action = "human_review"
            reason = f"Confidence {confidence:.2f} below threshold {self.confidence_threshold}"
        else:
            action = "auto"
            reason = f"Confidence {confidence:.2f} meets threshold {self.confidence_threshold}"

        elapsed = (time.monotonic() - start) * 1000
        return RoutingDecision(
            action=action, source="internal", eval_time_ms=elapsed, reason=reason
        )


replay_engine = ReplayEngine(storage)
router = ConfidenceRouter(confidence_threshold=0.85)


async def demo_replay() -> dict:
    """Demonstrate stochastic failure detection.

    Runs the same report twice with temperature=0.7 — once with the original
    fixture, once with the _replay fixture. The two outputs differ, proving
    the LLM is non-deterministic at this temperature.

    Also demonstrates ReplayEngine.replay() for snapshot validation.
    """
    report_text = Path("data/police_reports/report_001.txt").read_text()

    # Step 1: Run with temperature=0.7 → store decision (original fixture)
    stochastic_llm = MockLLMProvider(
        model="gpt-4o", temperature=0.7, simulate_latency=False
    )
    result = await summarize_report(
        "report_001", report_text, llm=stochastic_llm
    )
    original_id = result["snapshot_id"]

    # Step 2: "Replay" — re-run same input but get the _replay fixture
    # This simulates what happens when you re-run the same prompt:
    # the stochastic model produces different output
    replay_result_data = await summarize_report(
        "report_001", report_text, llm=stochastic_llm, replay=True
    )
    replay_id = replay_result_data["snapshot_id"]

    # Step 3: Use ReplayEngine to validate both stored snapshots
    # replay() checks that the stored snapshot is internally consistent
    original_replay = replay_engine.replay(original_id, "strict")
    replay_replay = replay_engine.replay(replay_id, "strict")

    # Step 4: Batch replay — validate multiple snapshots at once
    batch_results = replay_engine.replay_batch(
        [original_id, replay_id], "strict", 2
    )

    # Step 5: Compare the two runs directly — this is the stochastic failure
    # The same input produced different output at temperature=0.7
    outputs_match = result["summary"] == replay_result_data["summary"]

    # Use DriftCalculator to quantify the difference
    drift_calc = DriftCalculator()
    drift = drift_calc.calculate_drift([
        result["summary"],
        replay_result_data["summary"],
    ])

    # Emit drift event
    await emit_drift_detected(result["decision"], {
        "drift_score": drift.drift_score,
        "outputs_match": outputs_match,
        "source": "stochastic_replay",
    })

    return {
        "original_id": original_id,
        "replay_id": replay_id,
        "original_confidence": result["confidence"],
        "replay_confidence": replay_result_data["confidence"],
        "outputs_match": outputs_match,
        "replay_validation_status": original_replay.status,
        "batch_all_passed": all(r.status == "success" for r in batch_results),
        "drift_score": drift.drift_score,
    }


async def demo_routing() -> list:
    """Show automatic routing based on confidence scores.

    report_003 (conflicting witnesses) → human_review
    report_001 (clear facts) → auto
    """
    routing_results = []

    # Low confidence: report_003 with conflicting witnesses
    report_003_text = Path("data/police_reports/report_003.txt").read_text()
    low_conf_llm = MockLLMProvider(model="gpt-4o", simulate_latency=False)
    result_003 = await summarize_report("report_003", report_003_text, llm=low_conf_llm)

    # Router needs a DecisionSnapshot (loaded from storage) to read confidence
    loaded_003 = storage.load_decision(result_003["snapshot_id"])
    routing_003 = await router.route(loaded_003)

    # Emit low-confidence event for flagged reports
    if routing_003.action == "human_review":
        await emit_low_confidence(loaded_003, result_003["confidence"], threshold=0.85)

    routing_results.append({
        "report_id": "report_003",
        "confidence": result_003["confidence"],
        "action": routing_003.action,
        "reason": routing_003.reason,
        "eval_time_ms": routing_003.eval_time_ms,
    })

    # High confidence: report_001 with clear facts
    report_001_text = Path("data/police_reports/report_001.txt").read_text()
    high_conf_llm = MockLLMProvider(model="gpt-4o", simulate_latency=False)
    result_001 = await summarize_report("report_001", report_001_text, llm=high_conf_llm)

    loaded_001 = storage.load_decision(result_001["snapshot_id"])
    routing_001 = await router.route(loaded_001)

    routing_results.append({
        "report_id": "report_001",
        "confidence": result_001["confidence"],
        "action": routing_001.action,
        "reason": routing_001.reason,
        "eval_time_ms": routing_001.eval_time_ms,
    })

    return routing_results


async def main():
    print("=== Replay Demo ===")
    replay = await demo_replay()
    print(f"  Original: {replay['original_id']} (conf={replay['original_confidence']})")
    print(f"  Replay:   {replay['replay_id']} (conf={replay['replay_confidence']})")
    print(f"  Outputs match: {replay['outputs_match']}")
    print(f"  Replay validation: {replay['replay_validation_status']}")
    print(f"  Drift score: {replay['drift_score']:.3f}")
    if not replay["outputs_match"]:
        print(f"  !! STOCHASTIC FAILURE DETECTED")

    print("\n=== Routing Demo ===")
    routing = await demo_routing()
    for r in routing:
        marker = " <-- flagged" if r["action"] == "human_review" else ""
        print(f"  {r['report_id']} (conf={r['confidence']:.2f}) -> {r['action']}{marker}")


if __name__ == "__main__":
    asyncio.run(main())
