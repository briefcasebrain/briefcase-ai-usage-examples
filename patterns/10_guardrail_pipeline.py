"""
Pattern 10 — Guardrail pipeline

What this shows: `GuardrailPipeline` composes multiple `GuardrailEnv` stages
into a single request/allow/deny check. Default mode `FIRST_DENY` short-circuits
on the first stage that says no.
When to reach for it: any time a request must pass multiple independent policy
checks (PII, jurisdiction, rate-limit, output-content) before hitting an LLM.
See also: patterns/09_pii_sanitization.py (PII stage is a common first guardrail)
"""
from __future__ import annotations

from briefcase.guardrails import (
    BaseGuardrailEnv,
    Effect,
    EnvSpec,
    EvalRequest,
    EvalResult,
    GuardrailPipeline,
    PolicySpace,
)


class MaxNotionalEnv(BaseGuardrailEnv):
    """Deny requests whose context.notional_usd exceeds a hard cap."""

    def __init__(self, cap: float = 100_000.0):
        self._cap = cap
        self._spec = EnvSpec(id="max_notional", entry_point=f"{__name__}:MaxNotionalEnv")

    @property
    def name(self) -> str:
        return "max_notional"

    @property
    def request_space(self) -> PolicySpace:
        return PolicySpace(dimensions={}, constraints=[])

    def evaluate(self, request: EvalRequest) -> EvalResult:
        notional = request.context.get("notional_usd", 0)
        if notional > self._cap:
            return EvalResult(effect=Effect.DENY, guardrail_name=self.name, reason=f"notional {notional} exceeds cap {self._cap}")
        return EvalResult(effect=Effect.ALLOW, guardrail_name=self.name, reason="under cap")

    def reset(self) -> None:
        pass

    def close(self) -> None:
        pass


class JurisdictionAllowlistEnv(BaseGuardrailEnv):
    """Allow only a configured set of jurisdictions."""

    def __init__(self, allowed=("US", "EU", "UK")):
        self._allowed = set(allowed)
        self._spec = EnvSpec(id="juris_allow", entry_point=f"{__name__}:JurisdictionAllowlistEnv")

    @property
    def name(self) -> str:
        return "juris_allow"

    @property
    def request_space(self) -> PolicySpace:
        return PolicySpace(dimensions={}, constraints=[])

    def evaluate(self, request: EvalRequest) -> EvalResult:
        j = request.context.get("jurisdiction", "??")
        if j not in self._allowed:
            return EvalResult(effect=Effect.DENY, guardrail_name=self.name, reason=f"jurisdiction {j} not in {sorted(self._allowed)}")
        return EvalResult(effect=Effect.ALLOW, guardrail_name=self.name, reason=f"{j} allowed")

    def reset(self) -> None:
        pass

    def close(self) -> None:
        pass


def main() -> None:
    # === Section: Compose two guardrails into a pipeline ===
    # FIRST_DENY mode short-circuits: if any stage denies, the pipeline denies
    # with that stage's reason. Stages run in order.
    pipeline = GuardrailPipeline(
        stages=[JurisdictionAllowlistEnv(), MaxNotionalEnv(cap=100_000)],
        name="payment_checks",
    )

    # === Section: Exercise three cases ===
    cases = [
        ("allowed", EvalRequest(agent="a1", action="route_payment", resource="corridor_us_eu",
                                context={"jurisdiction": "US", "notional_usd": 25_000})),
        ("bad_jurisdiction", EvalRequest(agent="a1", action="route_payment", resource="corridor_kp",
                                context={"jurisdiction": "KP", "notional_usd": 25_000})),
        ("over_cap", EvalRequest(agent="a1", action="route_payment", resource="corridor_us_eu",
                                context={"jurisdiction": "US", "notional_usd": 500_000})),
    ]
    for label, req in cases:
        result = pipeline.evaluate(req)
        first = result.individual_results[-1]  # the deciding stage
        print(f"  [{label:<18}] final={result.final_effect.value:<5} short_circuited={result.short_circuited:<5} reason={first.reason}")

    print(
        "\nThe FIRST_DENY short-circuit is what makes guardrails fast: for the\n"
        "over_cap request, the jurisdiction stage allows then the cap stage\n"
        "denies — but a request with a bad jurisdiction short-circuits on\n"
        "stage 1 and never runs the cap check."
    )


if __name__ == "__main__":
    main()
