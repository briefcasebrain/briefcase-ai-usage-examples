"""
Pattern 01 — Decision capture

What this shows: `@capture` auto-records a function's inputs, outputs, timing,
and errors. The resulting `DecisionSnapshot` is the audit atom — what the
system DID, immutably, for every invocation.
When to reach for it: any SDK-instrumented function where you need an audit
trail of every call (who asked, what answer, how long, what model, what version).
`@capture` works on both sync and async functions; this pattern uses sync for
portability between scripts and notebooks.
See also: patterns/06_examiner_bundle.py (reproducibility layer on top of capture)
"""
from __future__ import annotations

from briefcase.decorators import capture


@capture(decision_type="sentiment_classification", context_version="v1")
def classify(document: str, model: str = "gpt-4o") -> dict:
    """Dummy 'LLM' — deterministic so the pattern runs offline."""
    score = 0.92 if "great" in document.lower() else 0.31
    return {"label": "positive" if score > 0.5 else "negative", "score": score}


def main() -> None:
    # === Section: Invoke the instrumented function ===
    # Every @capture'd call produces a DecisionSnapshot that records: inputs,
    # outputs, started_at, ended_at, execution_time_ms, and any error raised.
    # The snapshot is persisted to the configured backend (SqliteBackend by
    # default) and keyed by a fresh decision_id (UUID).
    result = classify("The product is great", model="gpt-4o")
    print(f"Classifier returned: {result}")

    # === Section: A second call produces a separate snapshot ===
    # Each invocation produces its own immutable snapshot — useful for
    # comparing runs, reproducing a specific call, or building drift metrics.
    result2 = classify("This is terrible", model="gpt-4o")
    print(f"Second call:         {result2}")

    # === Section: Errors are captured too ===
    # If the wrapped function raises, @capture records the exception on the
    # snapshot and re-raises it. The audit trail retains failed calls with
    # full context — important for debugging and post-mortem analysis.
    @capture(decision_type="always_fails")
    def always_fails(x: int) -> int:
        raise ValueError(f"no: {x}")

    try:
        always_fails(42)
    except ValueError as e:
        print(f"\nCaptured error: {type(e).__name__}: {e}")
        print("The snapshot records the exception; verify via the configured backend.")


if __name__ == "__main__":
    main()
