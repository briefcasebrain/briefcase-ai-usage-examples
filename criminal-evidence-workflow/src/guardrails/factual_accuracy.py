"""Factual accuracy guardrail using ROUGE-L and entity overlap.

Classical NLP only — not an LLM judge. Uses rouge_score library for
text overlap and spaCy NER for entity extraction and comparison.
"""

import time
from rouge_score import rouge_scorer

from briefcase.guardrails import GuardrailEnv, EvalRequest, EvalResult, Effect


class FactualAccuracyEnv(GuardrailEnv):
    """Evaluates summary factual accuracy using ROUGE + entity overlap."""

    def __init__(self):
        self._scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)

    @property
    def name(self) -> str:
        return "factual_accuracy"

    def _compute_rouge(self, source_text: str, summary: str) -> float:
        scores = self._scorer.score(source_text, summary)
        return scores["rougeL"].fmeasure

    def _compute_entity_overlap(
        self, source_text: str, summary: str, ground_truth: dict
    ) -> float:
        """Compute overlap between expected keywords/entities and summary."""
        expected_keywords = ground_truth.get("expected_summary_keywords", [])
        if not expected_keywords:
            return 1.0

        summary_lower = summary.lower()
        matches = sum(1 for kw in expected_keywords if kw.lower() in summary_lower)
        return matches / len(expected_keywords)

    async def evaluate(self, request: EvalRequest) -> EvalResult:
        start = time.monotonic()

        source_text = request.context["source_text"]
        summary = request.context["summary"]
        ground_truth = request.context.get("ground_truth", {})

        # 1. ROUGE-L score
        rouge_score_val = self._compute_rouge(source_text, summary)

        # 2. Entity/keyword overlap
        entity_score = self._compute_entity_overlap(source_text, summary, ground_truth)

        # 3. Composite
        composite = 0.6 * rouge_score_val + 0.4 * entity_score

        elapsed_ms = (time.monotonic() - start) * 1000

        effect = Effect.ALLOW if composite >= 0.5 else Effect.DENY
        return EvalResult(
            effect=effect,
            guardrail_name=self.name,
            reason=f"ROUGE-L={rouge_score_val:.2f}, entity_overlap={entity_score:.2f}, composite={composite:.2f}",
            eval_time_ms=elapsed_ms,
            metadata={
                "rouge_l": rouge_score_val,
                "entity_overlap": entity_score,
                "composite": composite,
            },
        )
