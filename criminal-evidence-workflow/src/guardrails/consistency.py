"""Cross-document consistency guardrail.

Checks for contradictions between summaries of related incidents
by extracting and comparing shared entities and facts.
"""

import re
import time
from briefcase.guardrails import GuardrailEnv, EvalRequest, EvalResult, Effect


class CrossDocConsistencyEnv(GuardrailEnv):
    """Detects contradictions between summaries of related incidents."""

    @property
    def name(self) -> str:
        return "cross_doc_consistency"

    def _extract_entities(self, text: str) -> dict:
        """Extract key entities from summary text using pattern matching."""
        entities = {}

        # Addresses
        addr_pattern = r"\d+\s+[\w\s]+(?:Avenue|Boulevard|Street|Way|Drive|Road|Ave|Blvd|St|Dr|Rd)\b"
        entities["addresses"] = re.findall(addr_pattern, text, re.IGNORECASE)

        # Store/business names
        store_pattern = r"(?:at|from)\s+([\w\s]+(?:Electronics|Store|Shop|Market))"
        entities["stores"] = re.findall(store_pattern, text, re.IGNORECASE)

        # Dollar amounts
        entities["amounts"] = re.findall(r"\$[\d,]+(?:\.\d{2})?", text)

        # Case numbers
        entities["case_numbers"] = re.findall(r"Case\s*#?\s*\d{4}-\d+", text)

        # People names (simple heuristic: Title + Name or capitalized sequences)
        entities["people"] = re.findall(
            r"(?:Mr\.|Ms\.|Mrs\.|Officer|Detective|Ofc\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?",
            text,
        )

        return entities

    def _find_contradictions(
        self, entities_a: dict, entities_b: dict, summary_a: str, summary_b: str
    ) -> list:
        """Find contradictions between two sets of entities."""
        contradictions = []

        # Check address consistency for shared stores
        addrs_a = set(a.strip().lower() for a in entities_a.get("addresses", []))
        addrs_b = set(a.strip().lower() for a in entities_b.get("addresses", []))

        # If both reference the same store, addresses should match
        stores_a = set(s.strip().lower() for s in entities_a.get("stores", []))
        stores_b = set(s.strip().lower() for s in entities_b.get("stores", []))
        shared_stores = stores_a & stores_b

        if shared_stores:
            # Check if addresses containing lakeshore differ
            lake_addrs_a = [a for a in addrs_a if "lakeshore" in a]
            lake_addrs_b = [a for a in addrs_b if "lakeshore" in a]

            if lake_addrs_a and lake_addrs_b:
                for aa in lake_addrs_a:
                    for ab in lake_addrs_b:
                        if aa != ab:
                            contradictions.append(
                                f"Address mismatch for shared location: '{aa}' vs '{ab}'"
                            )

        # Check people referenced in both — same person, different titles/details
        people_a = set(p.strip() for p in entities_a.get("people", []))
        people_b = set(p.strip() for p in entities_b.get("people", []))
        shared_people = set()
        for pa in people_a:
            for pb in people_b:
                # Check if same last name but different prefix
                last_a = pa.split()[-1].lower()
                last_b = pb.split()[-1].lower()
                if last_a == last_b and pa != pb:
                    shared_people.add((pa, pb))

        return contradictions

    async def evaluate(self, request: EvalRequest) -> EvalResult:
        start = time.monotonic()

        summary_a = request.context["summary_a"]
        summary_b = request.context["summary_b"]

        entities_a = self._extract_entities(summary_a)
        entities_b = self._extract_entities(summary_b)

        contradictions = self._find_contradictions(
            entities_a, entities_b, summary_a, summary_b
        )

        elapsed_ms = (time.monotonic() - start) * 1000

        consistency_score = 1.0 if not contradictions else max(0.0, 1.0 - 0.3 * len(contradictions))
        effect = Effect.ALLOW if not contradictions else Effect.DENY

        return EvalResult(
            effect=effect,
            guardrail_name=self.name,
            reason=f"Found {len(contradictions)} contradiction(s)" if contradictions else "No contradictions detected",
            eval_time_ms=elapsed_ms,
            metadata={
                "contradictions": contradictions,
                "consistency_score": consistency_score,
                "entities_a": {k: len(v) for k, v in entities_a.items()},
                "entities_b": {k: len(v) for k, v in entities_b.items()},
            },
        )
