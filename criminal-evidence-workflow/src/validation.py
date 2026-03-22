"""Prompt validation for evidence references.

Validates that evidence references in prompts (report IDs, case numbers)
actually exist before sending to the LLM. Uses the Briefcase AI SDK's
PromptValidationEngine with custom extractors and resolvers.
"""

import json
import re
import asyncio
from pathlib import Path

from briefcase.validation.engine import PromptValidationEngine
from briefcase.validation.errors import ValidationError, ValidationErrorCode


class EvidenceExtractor:
    """Extracts evidence references from prompts.

    Finds report IDs (report_001) and case numbers (Case #2024-0892).
    """

    REPORT_ID_PATTERN = re.compile(r"report_\d{3}(?:_amended)?")
    CASE_NUMBER_PATTERN = re.compile(r"Case\s*#\d{4}-\d{4}")

    def extract(self, prompt: str) -> list:
        refs = []
        refs.extend(self.REPORT_ID_PATTERN.findall(prompt))
        refs.extend(self.CASE_NUMBER_PATTERN.findall(prompt))
        return refs


class EvidenceResolver:
    """Resolves evidence references against the local data directory.

    Checks that referenced report files exist in data/police_reports/.
    """

    def __init__(self, data_dir: str = "data/police_reports"):
        self.data_dir = Path(data_dir)

    def resolve_all(self, references: list) -> list:
        errors = []
        for ref in references:
            if ref.startswith("report_"):
                filepath = self.data_dir / f"{ref}.txt"
                if not filepath.exists():
                    errors.append(ValidationError(
                        code=ValidationErrorCode.REFERENCE_NOT_FOUND,
                        message=f"Evidence file not found: {ref}.txt",
                        reference=ref,
                        severity="error",
                        layer="resolution",
                        remediation=f"Check that {ref}.txt exists in {self.data_dir}",
                    ))
            elif ref.startswith("Case"):
                # Case numbers are informational — no file resolution needed
                pass
        return errors


class MockLakeFSClient:
    """Simulates lakeFS commit lookups for offline operation."""

    def get_commit(self, repository: str, branch: str) -> str:
        return "abc123def456"


def create_validation_engine(
    data_dir: str = "data/police_reports",
    mode: str = "strict",
) -> PromptValidationEngine:
    """Create a configured PromptValidationEngine for evidence validation."""
    return PromptValidationEngine(
        extractor=EvidenceExtractor(),
        resolver=EvidenceResolver(data_dir),
        lakefs_client=MockLakeFSClient(),
        repository="evidence-repo",
        branch="main",
        mode=mode,
    )


_engine = create_validation_engine()


def validate_prompt(prompt: str) -> "ValidationReport":
    """Validate an evidence prompt. Returns a ValidationReport."""
    return _engine.validate(prompt)


def demo_validation() -> list:
    """Run validation scenarios from fixtures."""
    fixtures_path = Path("data/fixtures/validation_scenarios.json")
    scenarios = json.loads(fixtures_path.read_text())

    results = []
    for scenario in scenarios:
        report = validate_prompt(scenario["prompt"])
        results.append({
            "name": scenario["name"],
            "prompt": scenario["prompt"],
            "expected_status": scenario["expected_status"],
            "actual_status": report.status,
            "passed": report.status == scenario["expected_status"],
            "references_checked": report.references_checked,
            "errors": [e.to_dict() for e in report.errors],
            "validation_time_ms": report.validation_time_ms,
            "lakefs_commit": report.lakefs_commit,
        })
    return results


async def main():
    print("=== Evidence Prompt Validation ===\n")
    results = demo_validation()
    for r in results:
        status_marker = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status_marker}] {r['name']}")
        print(f"    Prompt: \"{r['prompt']}\"")
        print(f"    Status: {r['actual_status']} (expected: {r['expected_status']})")
        print(f"    Refs checked: {r['references_checked']}")
        if r["errors"]:
            for e in r["errors"]:
                print(f"    Error: [{e['code']}] {e['message']}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
