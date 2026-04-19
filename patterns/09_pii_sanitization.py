"""
Pattern 09 — PII sanitization

What this shows: the `Sanitizer` scans text for PII (SSNs, phone numbers,
emails, credit cards, etc.) and redacts matches. Works on free-form text or
structured JSON. Patterns are configurable per deployment.
When to reach for it: any time user-supplied or upstream-fetched text needs
to be scrubbed before storage, log emission, or LLM prompting.
See also: patterns/10_guardrail_pipeline.py (sanitization often sits in front of guardrails)
"""
from __future__ import annotations

import json

from briefcase._native import Sanitizer

sanitizer = Sanitizer()


def main() -> None:
    # === Section: Detect and redact PII in free text ===
    # sanitize() returns the scrubbed text; contains_pii() is a quick bool
    # check useful for gating (e.g., "never send PII to this vendor").
    dirty = (
        "Subject: Mr. John Smith. SSN: 123-45-6789. "
        "Reachable at john.smith@example.com or (415) 555-0199. "
        "Card on file: 4111 1111 1111 1111."
    )
    print("Before sanitization:")
    print(f"  {dirty}")
    print(f"\nSanitizer.contains_pii(): {sanitizer.contains_pii(dirty)}")

    result = sanitizer.sanitize(dirty)
    print(f"\nAfter sanitization:")
    print(f"  {result.sanitized}")
    print(f"  redactions: {result.redaction_count}")

    # === Section: Inspect the match set ===
    # analyze_pii() returns a dict describing what matched, so you can log
    # counts / types without logging the underlying values. Useful for
    # observability on redaction rate.
    analysis = sanitizer.analyze_pii(dirty)
    print(f"\nanalyze_pii() summary:")
    print(f"  has_pii:         {analysis['has_pii']}")
    print(f"  total_matches:   {analysis['total_matches']}")
    print(f"  detected_types:  {analysis['detected_types']}")

    # === Section: Sanitize structured payloads ===
    # sanitize_json() walks a JSON-serializable payload and redacts PII in
    # any string value. Keys are preserved.
    record = {
        "id": "case-2026-04-01",
        "summary": "Witness interviewed at home (phone 415-555-0100).",
        "officer_email": "officer.smith@policedept.gov",
    }
    print(f"\nOriginal record:  {json.dumps(record)}")
    json_res = sanitizer.sanitize_json(json.dumps(record))
    print(f"Sanitized record: {json_res.sanitized if hasattr(json_res, 'sanitized') else json_res}")


if __name__ == "__main__":
    main()
