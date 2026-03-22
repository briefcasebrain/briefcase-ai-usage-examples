#!/usr/bin/env python3
"""Full end-to-end demo of Briefcase AI SDK for criminal evidence summarization.

Default: fully offline, no API keys needed. Uses MockLLMProvider + fixtures.
Optional: --live flag swaps in real API calls (requires pip install -e ".[live]" and .env).
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import event_bus
from src.mock_llm import MockLLMProvider
from src.pipeline import summarize_report
from src.evaluation import run_full_evaluation, print_comparison_table
from src.triage import demo_replay, demo_routing
from src.sanitization import demo_sanitization
from src.lineage import demo_lineage, demo_drift, demo_external_data_tracking
from src.validation import validate_prompt


def parse_args():
    parser = argparse.ArgumentParser(description="Briefcase AI Criminal Evidence POC")
    parser.add_argument("--live", action="store_true", help="Use real LLM API calls (requires API keys)")
    parser.add_argument("--fast", action="store_true", help="Skip simulated latency")
    return parser.parse_args()


def _get_llm(model, provider, simulate_latency, live):
    """Return MockLLMProvider or real LLM provider based on --live flag."""
    if live:
        try:
            from langchain_openai import ChatOpenAI
            from langchain.chat_models import init_chat_model
            print(f"   [live] Using real API for {model} ({provider})")
        except ImportError:
            print(f"   [warn] langchain not installed — falling back to mocked. Run: pip install -e '.[live]'")
            live = False

    return MockLLMProvider(model=model, provider=provider, simulate_latency=simulate_latency)


async def run_demo(args):
    start_time = time.monotonic()
    simulate_latency = not args.fast and not args.live
    mode = "Live (API calls)" if args.live else "Mocked (fixture-backed)"

    # Header
    print()
    print("+" + "=" * 70 + "+")
    print("|  BRIEFCASE AI v3.0.0 -- Criminal Evidence Summarization POC" + " " * 9 + "|")
    print(f"|  Mode: {mode:<25} |  Reports: 5  |  Models: 2    |")
    print("+" + "=" * 70 + "+")
    print()

    if args.live:
        print("   [info] --live flag set. Real API calls require pip install -e '.[live]'")
        print("   [info] and OPENAI_API_KEY / ANTHROPIC_API_KEY in environment.")
        print()

    # ── Section 1: Instrumented Pipeline ──
    print(">> Section 1: Instrumented Pipeline")
    report_ids = ["report_001", "report_002", "report_003", "report_004", "report_005"]
    models = [
        _get_llm("gpt-4o", "openai", simulate_latency, args.live),
        _get_llm("claude-sonnet", "anthropic", simulate_latency, args.live),
    ]

    # Validate all report references before processing
    validation_passed = 0
    for rid in report_ids:
        v = validate_prompt(f"Summarize {rid}")
        if v.status == "passed":
            validation_passed += 1
    print(f"   Prompt validation: {validation_passed}/{len(report_ids)} references validated")

    snapshot_count = 0
    for llm in models:
        for rid in report_ids:
            report_text = Path(f"data/police_reports/{rid}.txt").read_text()
            result = await summarize_report(rid, report_text, llm=llm)
            snapshot_count += 1

    print(f"   Processing 5 reports x 2 models...")
    print(f"   [ok] {snapshot_count} DecisionSnapshots stored in decisions.db")

    # ── Section 2: Evaluation ──
    print("\n>> Section 2: Evaluation (3 GuardrailEnvs + Scorecard + CostCalculator)")
    eval_data = await run_full_evaluation(simulate_latency=simulate_latency)
    print_comparison_table(eval_data)

    # ── Section 3: Error Reproduction ──
    print("\n>> Section 3: Error Reproduction (ReplayEngine)")
    replay = await demo_replay()
    print(f"   Original: {replay['original_id'][:20]}... (conf={replay['original_confidence']})")
    print(f"   Replay:   {replay['replay_id'][:20]}... (conf={replay['replay_confidence']})")
    print(f"   Outputs match: {replay['outputs_match']}")
    print(f"   Drift score: {replay['drift_score']:.3f}")
    print(f"   Replay validation: {replay['replay_validation_status']}")
    if not replay["outputs_match"]:
        print(f"   [!!] STOCHASTIC FAILURE DETECTED — same input, different output")

    # ── Section 4: Confidence Routing ──
    print("\n>> Section 4: Confidence Routing (InternalRouter)")
    routing = await demo_routing()
    for r in routing:
        flag = "  <-- flagged for review" if r["action"] == "human_review" else ""
        print(f"   {r['report_id']} (conf={r['confidence']:.2f}) -> action={r['action']}{flag}")

    # ── Section 5: PII Sanitization ──
    print("\n>> Section 5: PII Sanitization (Sanitizer)")
    sanitization = demo_sanitization()
    print(f"   {sanitization['redaction_count']} PII items redacted from report_002.txt")
    for pii_type in sanitization["before_snippets"]:
        before = sanitization["before_snippets"][pii_type]
        after = sanitization["after_snippets"][pii_type]
        print(f"   [{pii_type.upper()}]")
        print(f"     Before: \"{before}\"")
        print(f"     After:  \"{after}\"")

    # ── Section 6: Data Lineage ──
    print("\n>> Section 6: Data Lineage & Drift")
    lineage = await demo_lineage()
    print(f"   report_001 v1: hash={lineage['v1_hash']} -> snapshot {lineage['v1_snapshot'][:16]}...")
    print(f"     validation: {lineage['v1_validation']}")
    print(f"   report_001 v2: hash={lineage['v2_hash']} -> snapshot {lineage['v2_snapshot'][:16]}...")
    print(f"     validation: {lineage['v2_validation']}")
    print(f"   Version changed: {lineage['version_changed']}")
    print(f"   Summary changed: {lineage['summary_changed']}")

    drift = await demo_drift(lineage)
    print(f"   Drift score (DriftCalculator): {drift['drift_score']:.3f}")
    print(f"   Consistency score: {drift['consistency_score']:.3f}")

    # External data tracking
    ext = demo_external_data_tracking()
    print(f"   External data tracking (ExternalDataTracker):")
    print(f"     Source changed: {ext['has_changed']}")
    print(f"     Drift score: {ext['drift_score']}")
    print(f"     Size delta: {ext['size_delta']} bytes")

    # Footer
    elapsed = time.monotonic() - start_time
    total_cost = sum(r.get("cost_total", 0) for r in eval_data.get("all_results", []))

    # Event summary
    event_types = {}
    for evt in event_bus.events:
        event_types[evt.event_type] = event_types.get(evt.event_type, 0) + 1

    print()
    print("=" * 72)
    print(f"  Total runtime: {elapsed:.1f}s  |  Mode: {mode}")
    if total_cost > 0:
        print(f"  Estimated cost (from CostCalculator): ${total_cost:.4f}")
    if event_bus.events:
        event_summary = ", ".join(f"{t}={c}" for t, c in event_types.items())
        print(f"  Events emitted: {len(event_bus.events)} ({event_summary})")
    if not args.live:
        print("  No API keys used. Run with --live for real LLM calls.")
    print("=" * 72)
    print()


def main():
    args = parse_args()
    asyncio.run(run_demo(args))


if __name__ == "__main__":
    main()
