"""
Pattern 11 — Decision replay

What this shows: a captured `DecisionSnapshot` stores the inputs that produced
an output, so you can re-run a candidate function against those same inputs
and compare. This is the regression-test primitive for model / prompt /
policy changes.
When to reach for it: any time you want to ship a change and prove that
historical decisions are unaffected (or, if affected, measure the delta).
See also: patterns/01_decision_capture.py (captures are the input to replay)
"""
from __future__ import annotations

import briefcase
from briefcase import DecisionSnapshot, Input, ModelParameters, Output
from briefcase.storage import SqliteBackend

briefcase.init()


def classify_v1(document: str) -> dict:
    """Original classifier."""
    score = 0.92 if "great" in document.lower() else 0.31
    return {"label": "positive" if score > 0.5 else "negative", "score": score}


def classify_v2(document: str) -> dict:
    """Candidate replacement — wider positive vocabulary."""
    positive_terms = ("great", "excellent", "love", "amazing")
    score = 0.95 if any(t in document.lower() for t in positive_terms) else 0.28
    return {"label": "positive" if score > 0.5 else "negative", "score": score}


backend = SqliteBackend.in_memory()


def main() -> None:
    # === Section: Capture baseline decisions into storage ===
    # Build DecisionSnapshots for each v1 call and save to the backend.
    # In production this is handled by @capture (see pattern 01); here we
    # construct them explicitly so the replay step is self-contained.
    docs = ["The product is great", "This is terrible", "Excellent value"]
    snapshot_ids: list[str] = []
    for doc in docs:
        out = classify_v1(doc)
        snap = DecisionSnapshot("classify_v1")
        snap.add_input(Input("document", doc, "string"))
        snap.with_model_parameters(ModelParameters("classify_v1"))
        snap.add_output(Output("label", out["label"], "string").with_confidence(out["score"]))
        snapshot_ids.append(backend.save_decision(snap))
    print(f"Captured {len(snapshot_ids)} baseline decisions")

    # === Section: Replay against the candidate ===
    # Load each snapshot, re-run the candidate with the stored input, and
    # compare outputs. The match rate is the regression-test signal.
    matches, diffs = 0, []
    for sid in snapshot_ids:
        original = backend.load_decision(sid)
        doc = next(i.value for i in original.inputs if i.name == "document")
        original_label = next(o.value for o in original.outputs if o.name == "label")
        new_out = classify_v2(doc)
        if new_out["label"] == original_label:
            matches += 1
        else:
            diffs.append((doc, original_label, new_out["label"]))

    print(f"\nReplay against classify_v2: {matches}/{len(snapshot_ids)} matched on label")
    for doc, orig, new in diffs:
        print(f"  DIFF: {doc!r} -- v1={orig} v2={new}")

    # === Section: Why this is the regression-test primitive ===
    print(
        "\nThe replay loop is the regression test: load historical inputs,\n"
        "re-run the candidate, diff outputs. A match rate of 100% means the\n"
        "change is safe for backfill; anything less flags what moved and how."
    )


if __name__ == "__main__":
    main()
