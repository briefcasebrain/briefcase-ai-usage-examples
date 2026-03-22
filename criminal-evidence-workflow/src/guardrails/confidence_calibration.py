"""Confidence calibration guardrail.

Checks whether the model's self-reported confidence aligns with
measured accuracy. Catches overconfident or underconfident outputs.
"""

import time
from briefcase.guardrails import GuardrailEnv, EvalRequest, EvalResult, Effect


class ConfidenceCalibrationEnv(GuardrailEnv):
    """Detects miscalibration between confidence and actual accuracy."""

    def __init__(self, max_calibration_error: float = 0.2):
        self.max_calibration_error = max_calibration_error

    @property
    def name(self) -> str:
        return "confidence_calibration"

    async def evaluate(self, request: EvalRequest) -> EvalResult:
        start = time.monotonic()

        confidence = request.context["confidence"]
        accuracy_score = request.context["accuracy_score"]

        calibration_error = abs(confidence - accuracy_score)
        direction = (
            "overconfident" if confidence > accuracy_score else "underconfident"
        )

        elapsed_ms = (time.monotonic() - start) * 1000

        effect = (
            Effect.ALLOW
            if calibration_error < self.max_calibration_error
            else Effect.DENY
        )

        return EvalResult(
            effect=effect,
            guardrail_name=self.name,
            reason=f"calibration_error={calibration_error:.2f} ({direction}), threshold={self.max_calibration_error}",
            eval_time_ms=elapsed_ms,
            metadata={
                "calibration_error": calibration_error,
                "direction": direction,
                "confidence": confidence,
                "accuracy_score": accuracy_score,
                "calibration_score": 1.0 - calibration_error,
            },
        )
