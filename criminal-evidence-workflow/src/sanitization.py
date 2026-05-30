"""PII sanitization demo using Briefcase AI's Rust-powered Sanitizer.

Demonstrates redaction of SSNs, phone numbers, emails, and other PII
from police report text and decision payloads.
"""

import re
from pathlib import Path

from briefcase.sanitize import Sanitizer


sanitizer = Sanitizer()


def demo_sanitization() -> dict:
    """Sanitize PII from evidence text before storage."""
    report_text = Path("data/police_reports/report_002.txt").read_text()

    # Find snippets containing PII
    pii_patterns = {
        "ssn": r"SSN:\s*\d{3}-\d{2}-\d{4}",
        "phone": r"\(\d{3}\)\s*\d{3}-\d{4}",
        "email": r"\S+@\S+\.\S+",
    }

    before_snippets = {}
    for name, pattern in pii_patterns.items():
        match = re.search(pattern, report_text)
        if match:
            start = max(0, match.start() - 20)
            end = min(len(report_text), match.end() + 20)
            before_snippets[name] = report_text[start:end]

    # Sanitize the full text
    sanitize_result = sanitizer.sanitize(report_text)
    sanitized_text = sanitize_result.sanitized

    # Find same regions in sanitized text
    after_snippets = {}
    for name, pattern in pii_patterns.items():
        match = re.search(pattern, sanitized_text)
        if match:
            start = max(0, match.start() - 20)
            end = min(len(sanitized_text), match.end() + 20)
            after_snippets[name] = sanitized_text[start:end]
        else:
            # PII was redacted — find the redaction marker in roughly the same area
            after_snippets[name] = "[REDACTED — pattern no longer present]"

    # Also sanitize a JSON payload
    decision_dict = {
        "inputs": [{"name": "document", "value": report_text[:500]}],
        "metadata": {"report_id": "report_002"},
    }
    sanitized_json_result = sanitizer.sanitize_json(decision_dict)

    return {
        "original_length": len(report_text),
        "sanitized_length": len(sanitized_text),
        "redaction_count": sanitize_result.redaction_count,
        "before_snippets": before_snippets,
        "after_snippets": after_snippets,
        "json_redaction_count": sanitized_json_result.redaction_count,
    }


def main():
    print("=== PII Sanitization Demo ===")
    result = demo_sanitization()

    print(f"\nDocument: report_002.txt ({result['original_length']} chars)")
    print(f"Sanitized: {result['sanitized_length']} chars ({result['redaction_count']} redactions)")

    print("\nBefore/After PII regions:")
    for pii_type in result["before_snippets"]:
        print(f"\n  [{pii_type.upper()}]")
        print(f"    Before: ...{result['before_snippets'][pii_type]}...")
        print(f"    After:  ...{result['after_snippets'][pii_type]}...")

    print(f"\nJSON payload redactions: {result['json_redaction_count']}")


if __name__ == "__main__":
    main()
