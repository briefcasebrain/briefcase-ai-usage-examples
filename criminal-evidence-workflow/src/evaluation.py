"""Evaluation runner: multi-model comparison with guardrail pipeline.

Runs all 5 reports through multiple models, evaluates with 3 guardrails,
attaches Scorecards, and produces comparison tables.
"""

import json
import asyncio
from pathlib import Path

from briefcase.cost import CostCalculator
# Scorecard and ExperimentMetadata are native-only types (no public re-export)
from briefcase._native import Scorecard, ExperimentMetadata
from briefcase.guardrails import GuardrailPipeline, PipelineMode, EvalRequest

from src.mock_llm import MockLLMProvider
from src.pipeline import summarize_report
from src.config import storage
from src.guardrails.factual_accuracy import FactualAccuracyEnv
from src.guardrails.confidence_calibration import ConfidenceCalibrationEnv
from src.guardrails.consistency import CrossDocConsistencyEnv


REPORT_IDS = ["report_001", "report_002", "report_003", "report_004", "report_005"]
REPORTS_DIR = Path("data/police_reports")
EXPERIMENT_ID = "criminal-summary-eval-v1"


def load_report(report_id: str) -> str:
    return (REPORTS_DIR / f"{report_id}.txt").read_text()


def load_ground_truth(report_id: str) -> dict:
    gt_path = REPORTS_DIR / f"{report_id}_ground_truth.json"
    return json.loads(gt_path.read_text())


async def evaluate_single(
    report_id: str,
    llm: MockLLMProvider,
    factual_env: FactualAccuracyEnv,
    calibration_env: ConfidenceCalibrationEnv,
    run_index: int = 0,
    total_runs: int = 1,
) -> dict:
    """Run pipeline + evaluation for a single report/model combo."""
    report_text = load_report(report_id)
    ground_truth = load_ground_truth(report_id)

    result = await summarize_report(report_id, report_text, llm=llm)

    # Factual accuracy
    accuracy_result = await factual_env.evaluate(
        EvalRequest(
            agent="summarizer",
            action="summarize",
            resource=report_id,
            context={
                "source_text": report_text,
                "summary": result["summary"],
                "ground_truth": ground_truth,
            },
        )
    )

    # Confidence calibration
    calibration_result = await calibration_env.evaluate(
        EvalRequest(
            agent="summarizer",
            action="summarize",
            resource=report_id,
            context={
                "confidence": result["confidence"],
                "accuracy_score": accuracy_result.metadata["composite"],
            },
        )
    )

    # Attach scorecard to decision
    scorecard = Scorecard()
    scorecard = scorecard.add_score(
        "factual_accuracy", accuracy_result.metadata["composite"], 0.5
    )
    scorecard = scorecard.add_score(
        "confidence_calibration",
        calibration_result.metadata["calibration_score"],
        0.3,
    )

    # Attach scorecard to decision
    decision = result["decision"]
    decision = decision.with_scorecard(scorecard)

    # Tag with experiment metadata
    experiment_metadata = ExperimentMetadata(
        EXPERIMENT_ID, run_index, total_runs
    )
    decision.add_tag("experiment_id", EXPERIMENT_ID)
    decision.add_tag("experiment_run", str(run_index))

    # Cost calculation — map fixture model names to CostCalculator's known models
    cost_calc = CostCalculator()
    token_usage = result["token_usage"]
    cost_model_map = {"gpt-4o": "gpt-4o", "claude-sonnet": "claude-3-5-sonnet"}
    cost_model = cost_model_map.get(result["model"], "gpt-4o")
    cost_estimate = cost_calc.estimate_cost(
        cost_model, token_usage["prompt_tokens"], token_usage["completion_tokens"]
    )

    return {
        "report_id": report_id,
        "model": result["model"],
        "provider": result["provider"],
        "confidence": result["confidence"],
        "accuracy": accuracy_result.metadata["composite"],
        "rouge_l": accuracy_result.metadata["rouge_l"],
        "entity_overlap": accuracy_result.metadata["entity_overlap"],
        "calibration_error": calibration_result.metadata["calibration_error"],
        "calibration_score": calibration_result.metadata["calibration_score"],
        "calibration_direction": calibration_result.metadata["direction"],
        "accuracy_effect": str(accuracy_result.effect),
        "calibration_effect": str(calibration_result.effect),
        "latency_ms": result["latency_ms"],
        "token_usage": token_usage,
        "snapshot_id": result["snapshot_id"],
        "cost_total": cost_estimate.total_cost,
        "cost_input": cost_estimate.input_cost,
        "cost_output": cost_estimate.output_cost,
        "experiment_metadata": experiment_metadata,
    }


async def run_cross_doc_consistency(
    results_by_model: dict, consistency_env: CrossDocConsistencyEnv
) -> dict:
    """Run consistency check on report_004 vs report_005 for each model."""
    consistency_results = {}

    for model_name, results in results_by_model.items():
        r004 = next((r for r in results if r["report_id"] == "report_004"), None)
        r005 = next((r for r in results if r["report_id"] == "report_005"), None)

        if r004 and r005:
            # We need the summaries — get them from fixtures
            llm_config = model_name.split("/")
            provider = llm_config[0] if len(llm_config) > 1 else "openai"
            model = llm_config[-1]

            llm = MockLLMProvider(
                model=model,
                provider=provider,
                simulate_latency=False,
            )
            summary_004 = (await llm.generate("report_004", "Summarize"))["summary"]
            summary_005 = (await llm.generate("report_005", "Summarize"))["summary"]

            consistency_result = await consistency_env.evaluate(
                EvalRequest(
                    agent="summarizer",
                    action="consistency_check",
                    resource=f"{r004['report_id']}+{r005['report_id']}",
                    context={
                        "summary_a": summary_004,
                        "summary_b": summary_005,
                    },
                )
            )

            consistency_results[model_name] = {
                "consistency_score": consistency_result.metadata["consistency_score"],
                "contradictions": consistency_result.metadata["contradictions"],
                "effect": str(consistency_result.effect),
            }

    return consistency_results


async def run_full_evaluation(simulate_latency: bool = True) -> dict:
    """Run evaluation across all reports and models."""
    factual_env = FactualAccuracyEnv()
    calibration_env = ConfidenceCalibrationEnv()
    consistency_env = CrossDocConsistencyEnv()

    # Compose guardrails into a pipeline (demonstrates the API surface;
    # individual evaluate() calls are kept because GuardrailPipeline.evaluate()
    # doesn't await sub-guardrails properly in the current SDK version).
    guardrail_pipeline = GuardrailPipeline(
        stages=[factual_env, calibration_env, consistency_env],
        mode=PipelineMode.ALL,
        name="criminal-summary-guardrails",
    )

    models = [
        MockLLMProvider(model="gpt-4o", provider="openai", simulate_latency=simulate_latency),
        MockLLMProvider(model="claude-sonnet", provider="anthropic", simulate_latency=simulate_latency),
    ]

    all_results = []
    results_by_model = {}
    total_runs = len(models) * len(REPORT_IDS)
    run_index = 0

    for llm in models:
        model_key = f"{llm.model}"
        results_by_model[model_key] = []

        for report_id in REPORT_IDS:
            result = await evaluate_single(
                report_id, llm, factual_env, calibration_env,
                run_index=run_index, total_runs=total_runs,
            )
            all_results.append(result)
            results_by_model[model_key].append(result)
            run_index += 1

    # Cross-document consistency
    consistency_results = await run_cross_doc_consistency(
        results_by_model, consistency_env
    )

    # Compare costs across models
    cost_calc = CostCalculator()
    cost_model_map = {"gpt-4o": "gpt-4o", "claude-sonnet": "claude-3-5-sonnet"}
    cost_names = [cost_model_map.get(llm.model, "gpt-4o") for llm in models]
    if len(cost_names) >= 2:
        avg_input = sum(
            r["token_usage"]["prompt_tokens"] for r in all_results
        ) // len(all_results)
        avg_output = sum(
            r["token_usage"]["completion_tokens"] for r in all_results
        ) // len(all_results)
        cost_comparison = cost_calc.compare_models(
            cost_names[0], cost_names[1], avg_input, avg_output
        )
    else:
        cost_comparison = None

    return {
        "all_results": all_results,
        "results_by_model": results_by_model,
        "consistency_results": consistency_results,
        "guardrail_pipeline": guardrail_pipeline,
        "cost_comparison": cost_comparison,
    }


def print_comparison_table(eval_data: dict):
    """Print formatted comparison table."""
    results_by_model = eval_data["results_by_model"]
    consistency_results = eval_data["consistency_results"]

    print("\n" + "=" * 75)
    print("  MODEL COMPARISON: GPT-4o vs Claude Sonnet (5 reports, mocked)")
    print("=" * 75)

    header = f"{'Model':<16}| {'Avg Accuracy':>12} | {'Avg Calibr.':>11} | {'Consistency':>11} | {'Avg Latency':>11} | {'Avg Cost':>10}"
    print(f"\n{header}")
    print("-" * 16 + "+" + "-" * 14 + "+" + "-" * 13 + "+" + "-" * 13 + "+" + "-" * 13 + "+" + "-" * 12)

    model_composites = {}

    for model_name, results in results_by_model.items():
        avg_accuracy = sum(r["accuracy"] for r in results) / len(results)
        avg_calibration = sum(r["calibration_score"] for r in results) / len(results)
        avg_latency = sum(r["latency_ms"] for r in results) / len(results)
        avg_cost = sum(r["cost_total"] for r in results) / len(results)

        consistency = consistency_results.get(model_name, {})
        consistency_score = consistency.get("consistency_score", 1.0)

        composite = 0.5 * avg_accuracy + 0.3 * avg_calibration + 0.2 * consistency_score
        model_composites[model_name] = composite

        print(
            f"{model_name:<16}| {avg_accuracy:>12.2f} | {avg_calibration:>11.2f} | {consistency_score:>11.2f} | {avg_latency:>9.0f}ms | ${avg_cost:>8.4f}"
        )

    print()
    for model_name, composite in model_composites.items():
        print(f"  Scorecard composite (weighted): {model_name}={composite:.3f}")

    # Print cost comparison if available
    cost_comparison = eval_data.get("cost_comparison")
    if cost_comparison:
        print(f"\n  Cost comparison: cheaper model = {cost_comparison['cheaper_model']}, "
              f"savings = ${cost_comparison['savings']:.4f}, "
              f"difference = {cost_comparison['percent_difference']:.1f}%")

    # Per-report detail
    print(f"\n{'--- Per-Report Detail ---':^75}")
    print(f"{'Report':<12}{'Model':<16}{'Conf':>6}{'Accur':>7}{'Calib':>7}  {'Effect':<12}")
    print("-" * 62)
    for result in eval_data["all_results"]:
        effect = "ALLOW" if "ALLOW" in result["accuracy_effect"] else "DENY"
        print(
            f"{result['report_id']:<12}{result['model']:<16}"
            f"{result['confidence']:>6.2f}{result['accuracy']:>7.2f}"
            f"{result['calibration_score']:>7.2f}  {effect:<12}"
        )


if __name__ == "__main__":
    eval_data = asyncio.run(run_full_evaluation(simulate_latency=False))
    print_comparison_table(eval_data)
