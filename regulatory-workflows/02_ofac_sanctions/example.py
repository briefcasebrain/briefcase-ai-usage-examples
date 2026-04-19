#!/usr/bin/env python3
"""
Briefcase AI Example: OFAC / Sanctions Screening

Context: BSA/AML compliance. Civil penalties up to $1M+ per violation.
Each improperly cleared transaction is a separate OFAC violation.
10-calendar-day reporting window for blocked transactions.

Demonstrates:
- Real-time sanctions screening decision capture
- Watchlist version SHA tracking (critical for OFAC defense)
- OFAC examiner query simulation with exact watchlist provenance
- Blocked transaction reporting workflow
"""

import sys
import os
import uuid
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    import backend
    # Import SDK classes from backend (handles mock implementation if SDK not available)
    from backend import briefcase, DecisionSnapshot, Input, Output, SqliteBackend
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)

# Imports for the bitemporal replay capstone (Phase 1 of the replay pattern
# rollout across regulatory examples — see agentic-payments/ for the same
# primitives composed into a cross-border payments narrative).
from briefcase.bitemporal import (
    AsOfView,
    BitemporalRecord,
    InMemoryBitemporalStore,
    append_correction,
)
from briefcase.compliance import BundleIntegrityError, ExaminerBundle
from briefcase.routing import (
    AgentRoutingDecision,
    PolicyRegistry,
    PolicyRule,
    PolicyVersion,
)


def generate_watchlist_sha() -> str:
    """
    Simulates the SHA hash of a consolidated sanctions watchlist.
    In production, this would be the actual SHA of the OFAC SDN list
    plus other consolidated watchlists at screening time.
    """
    # Simulate a realistic watchlist hash
    watchlist_content = f"ofac_sdn_list_{datetime.utcnow().date()}_consolidated"
    return hashlib.sha256(watchlist_content.encode()).hexdigest()[:16]


def simulate_ofac_screening_model(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates an AI-based OFAC sanctions screening model.
    In production, this would be replaced with actual ML model inference
    against consolidated watchlists.

    Args:
        transaction_data: Dictionary containing transaction and entity information

    Returns:
        Dictionary containing screening decision and match information
    """
    originator_name = transaction_data["originator_name"]
    beneficiary_name = transaction_data["beneficiary_name"]
    originator_country = transaction_data["originator_country"]
    payment_amount = transaction_data["payment_amount"]

    # Simulate known high-risk indicators
    high_risk_names = ["Aleksei Petrov", "Viktor Kozlov", "Maria Volkov"]
    high_risk_countries = ["RU", "IR", "KP"]
    high_risk_amounts = payment_amount > 100000  # Large transactions get extra scrutiny

    # Calculate match scores
    name_match_score = 0.0
    matched_entity = None

    # Check for exact name matches (simulated)
    if originator_name in high_risk_names or beneficiary_name in high_risk_names:
        name_match_score = 0.95
        matched_entity = originator_name if originator_name in high_risk_names else beneficiary_name
    elif originator_country in high_risk_countries:
        name_match_score = 0.75
        matched_entity = f"Country risk: {originator_country}"
    else:
        # Simulate fuzzy matching with some randomness
        name_match_score = random.uniform(0.0, 0.4)
        if name_match_score > 0.3:
            matched_entity = f"Potential match: {originator_name[:8]}..."

    # Decision thresholds
    auto_clear_threshold = 0.2
    block_threshold = 0.8

    # Make screening decision
    if name_match_score >= block_threshold:
        decision = "block"
    elif name_match_score >= auto_clear_threshold:
        decision = "escalate_to_analyst"
    else:
        decision = "auto_clear"

    return {
        "decision": decision,
        "match_score": round(name_match_score, 3),
        "matched_entity": matched_entity,
        "decision_threshold": block_threshold if decision == "block" else auto_clear_threshold,
        "screening_timestamp": datetime.utcnow().isoformat()
    }


def main():
    """
    Main execution function demonstrating OFAC sanctions screening workflow.
    """
    print("=== Briefcase AI OFAC Sanctions Screening Example ===")
    print("Regulation: OFAC/BSA (FinCEN)")
    print("Workflow: Real-time sanctions screening with watchlist version tracking\n")

    # Initialize Briefcase AI SDK
    try:
        briefcase.init_with_config(2)
        print("SUCCESS: Briefcase AI SDK initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize SDK: {e}")
        sys.exit(1)

    # Get configured backend
    db_backend = backend.get_backend()
    print("SUCCESS: SQLite backend configured\n")

    # Generate current watchlist version (critical for OFAC defense)
    current_watchlist_sha = generate_watchlist_sha()
    print(f"Current watchlist version: {current_watchlist_sha}")

    # Simulate payment transaction data
    transaction_id = str(uuid.uuid4())
    payment_data = {
        "transaction_id": transaction_id,
        "originator_name": "Aleksei Petrov",  # Known high-risk name
        "originator_country": "RU",  # High-risk country
        "beneficiary_name": "John Smith",
        "payment_amount": 50000.0,
        "payment_type": "wire",
        "watchlist_version_sha": current_watchlist_sha,
        "screening_config_version": "ofac-screening-v2.3.1"
    }

    print("Processing payment transaction:")
    for key, value in payment_data.items():
        if key != "watchlist_version_sha":  # Don't clutter output with SHA
            print(f"  {key}: {value}")
    print(f"  watchlist_version: {current_watchlist_sha[:12]}...")
    print()

    # Simulate OFAC screening model execution
    print("Running OFAC sanctions screening...")
    screening_result = simulate_ofac_screening_model(payment_data)
    print(f"SUCCESS: Screening decision: {screening_result['decision']}")
    print(f"SUCCESS: Match score: {screening_result['match_score']}")

    if screening_result['matched_entity']:
        print(f"SUCCESS: Matched entity: {screening_result['matched_entity']}")

    # Create decision snapshot for audit trail
    decision_inputs = payment_data
    decision_outputs = screening_result

    # Calculate reporting deadline (10 calendar days for blocked transactions)
    reporting_deadline = None
    if screening_result['decision'] == 'block':
        reporting_deadline = (datetime.utcnow() + timedelta(days=10)).isoformat()

    # Regulatory metadata required for OFAC compliance
    regulatory_metadata = {
        "regulation": "OFAC/BSA",
        "watchlist_version_sha": current_watchlist_sha,  # CRITICAL: exact watchlist in use
        "reporting_deadline": reporting_deadline,
        "violation_risk": screening_result['decision'] == 'block',
        "screening_timestamp": screening_result['screening_timestamp'],
        "examiner_ready": True
    }

    # Create DecisionSnapshot using shared utility
    try:
        decision_snapshot = backend.create_decision_snapshot(
            function_name="ofac_sanctions_screening",
            inputs=decision_inputs,
            outputs=decision_outputs,
            metadata=regulatory_metadata,
            input_types={
                "payment_amount": "float"
            },
            output_types={
                "match_score": "float",
                "decision_threshold": "float"
            }
        )

        print(f"SUCCESS: Decision snapshot created")

    except Exception as e:
        print(f"ERROR: Error creating decision snapshot: {e}")
        sys.exit(1)

    # Store decision in backend (immutable audit trail)
    try:
        stored_decision_id = db_backend.save_decision(decision_snapshot)
        print(f"SUCCESS: Decision stored in audit trail: {stored_decision_id}")
    except Exception as e:
        print(f"ERROR: Error storing decision: {e}")
        sys.exit(1)

    # Demonstrate audit retrieval
    print("\n" + "="*60)
    print("AUDIT TRAIL DEMONSTRATION")
    print("="*60)

    # Load decision back from backend
    try:
        retrieved_decision = db_backend.load_decision(stored_decision_id)
        if retrieved_decision:
            backend.print_audit_summary(stored_decision_id, "Decision retrieved from audit trail")
            print(f"Function: {getattr(retrieved_decision, 'function_name', 'N/A')}")
            print(f"Decision ID: {stored_decision_id}")
        else:
            print("ERROR: Failed to retrieve decision from backend")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error retrieving decision: {e}")
        sys.exit(1)

    # Simulate OFAC examiner query (the critical capability)
    print("="*60)
    print("OFAC EXAMINER SIMULATION")
    print("="*60)

    examiner_query = f"What watchlist version were you running when you screened transaction {transaction_id}?"
    print(f"EXAMINER QUERY: {examiner_query}")

    examiner_response = backend.format_examiner_response(
        stored_decision_id,
        examiner_query,
        db_backend
    )
    print(examiner_response)

    # Additional OFAC-specific validation
    print("="*60)
    print("OFAC-SPECIFIC VALIDATION")
    print("="*60)

    # Verify critical watchlist provenance
    retrieved_watchlist_sha = retrieved_decision.tags.get("watchlist_version_sha")
    if retrieved_watchlist_sha == current_watchlist_sha:
        print(f"SUCCESS: Watchlist version integrity confirmed")
        print(f"  Original SHA: {current_watchlist_sha}")
        print(f"  Retrieved SHA: {retrieved_watchlist_sha}")
    else:
        print(f"ERROR: Watchlist version mismatch - CRITICAL COMPLIANCE ISSUE")
        print(f"  Expected: {current_watchlist_sha}")
        print(f"  Retrieved: {retrieved_watchlist_sha}")

    # Check reporting deadline compliance
    if screening_result['decision'] == 'block':
        deadline = retrieved_decision.tags.get("reporting_deadline")
        if deadline:
            deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00') if deadline.endswith('Z') else deadline)
            days_remaining = (deadline_date - datetime.utcnow()).days
            print(f"SUCCESS: Blocked transaction reporting deadline: {deadline_date.strftime('%Y-%m-%d')}")
            print(f"SUCCESS: Days remaining for OFAC filing: {days_remaining}")
        else:
            print("ERROR: Missing reporting deadline for blocked transaction")

    # Regulatory validation
    print("="*60)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*60)

    required_ofac_fields = [
        "regulation",
        "watchlist_version_sha",
        "screening_timestamp",
        "violation_risk"
    ]

    validation_result = backend.validate_regulatory_completeness(
        retrieved_decision,
        required_ofac_fields
    )

    print(f"OFAC Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Required Fields: {', '.join(validation_result['missing_fields'])}")

    # Demonstrate the unique value proposition: watchlist version immutability
    print("="*60)
    print("BRIEFCASE AI VALUE DEMONSTRATION")
    print("="*60)
    print("SCENARIO: OFAC updates watchlist mid-day. Bank needs to prove which")
    print("version was active when each transaction was screened.")
    print()

    # Simulate a second transaction with updated watchlist
    new_watchlist_sha = generate_watchlist_sha()
    print(f"Simulated watchlist update: {new_watchlist_sha[:12]}...")

    second_transaction = {
        "transaction_id": str(uuid.uuid4()),
        "originator_name": "Jane Doe",
        "originator_country": "US",
        "beneficiary_name": "Bob Johnson",
        "payment_amount": 1000.0,
        "payment_type": "ach",
        "watchlist_version_sha": new_watchlist_sha,
        "screening_config_version": "ofac-screening-v2.3.1"
    }

    # Quick screening and storage
    second_result = simulate_ofac_screening_model(second_transaction)
    second_metadata = {
        "regulation": "OFAC/BSA",
        "watchlist_version_sha": new_watchlist_sha,
        "screening_timestamp": datetime.utcnow().isoformat()
    }

    second_snapshot = backend.create_decision_snapshot(
        function_name="ofac_sanctions_screening",
        inputs=second_transaction,
        outputs=second_result,
        metadata=second_metadata
    )

    second_stored_id = db_backend.save_decision(second_snapshot)

    # Demonstrate provenance tracking
    print("AUDIT TRAIL COMPARISON:")
    print(f"Transaction 1 ({transaction_id[:8]}...): Watchlist {current_watchlist_sha[:12]}...")
    print(f"Transaction 2 ({second_transaction['transaction_id'][:8]}...): Watchlist {new_watchlist_sha[:12]}...")
    print()
    print("SUCCESS: Both transactions maintain immutable watchlist version provenance")
    print("SUCCESS: OFAC examination defense: Complete audit trail with exact watchlist versions")

    # =====================================================================
    # BITEMPORAL REPLAY DEMONSTRATION
    # =====================================================================
    # The watchlist_version_sha above proves WHICH version was used.
    # The bitemporal store below proves WHAT was in it — so the same
    # screening can be replayed offline, without re-contacting OFAC.
    print("=" * 60)
    print("BITEMPORAL REPLAY DEMONSTRATION")
    print("=" * 60)

    utc = timezone.utc
    decision_time = datetime.now(utc) - timedelta(days=30)
    correction_time = datetime.now(utc)

    # Seed a bitemporal SDN store with the entries that were live at decision time.
    sdn_store = InMemoryBitemporalStore()
    petrov = BitemporalRecord.new(
        key="ofac:entity-petrov",
        valid_time=decision_time,
        value={"name": "Aleksei Petrov", "program": "RUSSIA-EO14024", "listed": True},
        source="ofac",
        source_trust_level="primary",
        transaction_time=decision_time,
        metadata={"sdn_list_version": current_watchlist_sha},
    )
    kozlov = BitemporalRecord.new(
        key="ofac:entity-kozlov",
        valid_time=decision_time,
        value={"name": "Viktor Kozlov", "program": "RUSSIA-EO14024", "listed": True},
        source="ofac",
        source_trust_level="primary",
        transaction_time=decision_time,
        metadata={"sdn_list_version": current_watchlist_sha},
    )
    sdn_store.append(petrov)
    sdn_store.append(kozlov)
    print(f"Seeded bitemporal SDN store: {len(sdn_store)} entries at decision_time={decision_time.date()}")

    # OFAC delists Petrov on appeal, 30 days after the screening. The original
    # record is preserved; the correction is appended with a later transaction_time.
    append_correction(
        sdn_store,
        petrov,
        corrected_value={
            "name": "Aleksei Petrov",
            "program": "RUSSIA-EO14024",
            "listed": False,
            "delisted_reason": "appeal_granted",
        },
        transaction_time=correction_time,
    )
    print(f"Correction appended: Petrov delisted on appeal at transaction_time={correction_time.date()}")

    # Replay: naive (today's view) vs as-of (decision day).
    live_entry = sdn_store.latest("ofac:entity-petrov").value
    print(f"\nLive view (today):                listed={live_entry['listed']} → would CLEAR")
    with AsOfView(sdn_store, transaction_time=decision_time) as view:
        replay_entry = view.latest("ofac:entity-petrov").value
        print(f"As-of decision day:               listed={replay_entry['listed']} → would BLOCK")
    print("\nThe as-of replay reconstructs the SDN list as it stood on decision day")
    print("without contacting OFAC. Same code path as production — only the clamp changes.")

    # Build an ExaminerBundle — a self-contained, content-addressed artifact
    # that an auditor can verify offline. Complements the DecisionSnapshot:
    # the snapshot captures WHAT happened; the bundle captures WHAT WAS KNOWN.
    screening_policy = PolicyVersion(
        policy_id="ofac_screening",
        version="1.0.0",
        description="Block on exact SDN match; escalate on score > 0.75; else clear.",
        rules=[
            PolicyRule(
                rule_id="sdn_match_block",
                condition={"sdn_match": True},
                choice="block",
                rationale="Exact match against active SDN entry",
            ),
        ],
        default_choice="clear",
    )
    policy_registry = PolicyRegistry()
    policy_registry.publish(
        screening_policy, valid_from=decision_time, transaction_time=decision_time
    )

    routing_decision = AgentRoutingDecision(
        decision_id=stored_decision_id,
        use_case="sanctions_screening",
        context={
            "originator": payment_data["originator_name"],
            "notional_usd": payment_data["payment_amount"],
        },
        candidates=["clear", "escalate", "block"],
        selected=screening_result["decision"],
        policy_id="ofac_screening",
        policy_version="1.0.0",
        matched_rule_id="sdn_match_block",
        evidence_refs=[petrov.record_id],
        rationale=f"Matched SDN entity: {screening_result['matched_entity']}",
        decided_at=decision_time,
    )

    bundle = ExaminerBundle.build(
        routing_decision,
        evidence_store=sdn_store,
        policy_registry=policy_registry,
        metadata={"transaction_id": transaction_id, "regulation": "OFAC/BSA"},
    )

    print(f"\nExaminerBundle assembled:")
    print(f"  content_hash:            {bundle.content_hash}")
    print(f"  policy captured:         v{bundle.policy['version']}")
    print(f"  evidence rows:           {len(bundle.evidence)}")

    bundle.verify()
    print(f"\nverify() on untouched bundle:    OK")

    payload = bundle.to_json(indent=2)
    ExaminerBundle.from_json(payload).verify()
    print(f"verify() after JSON round-trip:  OK")

    # Tamper check: flip the decision to "clear" and confirm verify() rejects.
    tampered_dict = json.loads(payload)
    tampered_dict["decision"]["selected"] = "clear"
    try:
        ExaminerBundle.from_dict(tampered_dict).verify()
    except BundleIntegrityError as e:
        print(f"verify() on tampered bundle:     REJECTED ({type(e).__name__})")

    print("")
    print("The watchlist_version_sha tag (earlier) proves WHICH list was used.")
    print("The ExaminerBundle (here) captures the list CONTENT — so an auditor")
    print("can verify the decision offline, even if OFAC later amends the list.")

    print(f"\nSUCCESS: OFAC sanctions screening audit trail demonstration completed")
    print(f"Primary Decision ID: {stored_decision_id}")
    print(f"Secondary Decision ID: {second_stored_id}")


if __name__ == "__main__":
    main()