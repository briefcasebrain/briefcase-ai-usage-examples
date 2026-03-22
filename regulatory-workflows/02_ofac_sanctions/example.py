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
import random
from datetime import datetime, timedelta
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

    print(f"\nSUCCESS: OFAC sanctions screening audit trail demonstration completed")
    print(f"Primary Decision ID: {stored_decision_id}")
    print(f"Secondary Decision ID: {second_stored_id}")


if __name__ == "__main__":
    main()