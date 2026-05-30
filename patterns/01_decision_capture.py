"""
Pattern 01 — Decision capture

What this shows: `@capture` auto-records a function's inputs, outputs, timing,
and errors. Each call produces a decision record — the audit atom — describing
what the system DID, immutably, for every invocation. `briefcase.observe(...)`
routes those records to an exporter so they actually go somewhere.
When to reach for it: any SDK-instrumented function where you need an audit
trail of every call (who asked, what answer, how long, what model, what version).
`@capture` works on both sync and async functions; this pattern uses sync for
portability between scripts and notebooks.
See also: patterns/06_examiner_bundle.py (reproducibility layer on top of capture)
"""
from __future__ import annotations

import briefcase
from briefcase.decorators import capture


# `async_capture=False` records synchronously so the pattern can inspect the
# captured record in-process; the default (async) is fine in production.
@capture(decision_type="sentiment_classification", context_version="v1", async_capture=False)
def classify(document: str, model: str = "gpt-4o") -> dict:
    """Dummy 'LLM' — deterministic so the pattern runs offline."""
    score = 0.92 if "great" in document.lower() else 0.31
    return {"label": "positive" if score > 0.5 else "negative", "score": score}


def main() -> None:
    # === Section: Route captured records to an exporter ===
    # `@capture` records every call, but needs somewhere to send the records.
    # `observe()` wires up an exporter: "console" prints to stderr, a "*.jsonl"
    # path appends to a file, and "memory" collects records in-process so we can
    # inspect them here. (`briefcase.setup(exporter=...)` does the same thing.)
    recorder = briefcase.observe("memory")

    # === Section: Invoke the instrumented function ===
    # Every @capture'd call produces a decision record: decision_type, inputs,
    # outputs, started_at/ended_at, execution_time_ms, context_version, and any
    # error raised — each keyed by a fresh decision_id.
    result = classify("The product is great", model="gpt-4o")
    print(f"Classifier returned: {result}")

    # === Section: A second call produces a separate record ===
    # Each invocation produces its own immutable record — useful for comparing
    # runs, reproducing a specific call, or building drift metrics.
    result2 = classify("This is terrible", model="gpt-4o")
    print(f"Second call:         {result2}")

    # === Section: Inspect the captured audit atoms ===
    print(f"\nCaptured {len(recorder.records)} decision record(s):")
    for rec in recorder.records:
        print(
            f"  - {rec['decision_type']} ({rec['execution_time_ms']:.3f} ms): "
            f"inputs={rec['inputs']} -> outputs={rec['outputs']}"
        )

    # === Section: Errors are captured too ===
    # If the wrapped function raises, @capture records the exception on the
    # record and re-raises it. The audit trail retains failed calls with full
    # context — important for debugging and post-mortem analysis.
    @capture(decision_type="always_fails", async_capture=False)
    def always_fails(x: int) -> int:
        raise ValueError(f"no: {x}")

    try:
        always_fails(42)
    except ValueError as e:
        print(f"\nCaptured error: {type(e).__name__}: {e}")
        print(f"Total records (including the failed call): {len(recorder.records)}")


if __name__ == "__main__":
    main()
