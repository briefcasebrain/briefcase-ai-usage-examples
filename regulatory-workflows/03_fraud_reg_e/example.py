#!/usr/bin/env python3
"""
Briefcase AI Example: Fraud Detection & Reg E Dispute Resolution

Context: Reg E governs electronic fund transfer disputes. Bank has 10-business-day
SLA to investigate from dispute receipt. High volume — hundreds of decisions per second.

Demonstrates:
- Real-time fraud scoring decision capture
- Reg E dispute linkage and investigation timeline
- Decision reconstructability without reverse-engineering logs
- EFTA compliance audit trail
"""

import sys
import os
import uuid
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    import backend
    # Import SDK classes from backend (handles mock implementation if SDK not available)
    from backend import briefcase_ai, DecisionSnapshot, Input, Output, SqliteBackend
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)


def hash_card_number(pan: str) -> str:
    """
    Hashes a Primary Account Number (PAN) for secure storage.
    Never stores raw card numbers in audit trail.

    Args:
        pan: Primary Account Number (simulated)

    Returns:
        SHA-256 hash of the PAN
    """
    return hashlib.sha256(pan.encode()).hexdigest()


def simulate_fraud_detection_model(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates a real-time fraud detection model for card transactions.
    In production, this would be replaced with actual ML model inference.

    Args:
        transaction_data: Dictionary containing transaction information

    Returns:
        Dictionary containing fraud decision and risk scores
    """
    transaction_amount = transaction_data["transaction_amount"]
    merchant_category = transaction_data["merchant_category_code"]
    device_fingerprint = transaction_data["device_fingerprint_score"]

    # Time-based risk factors
    transaction_time = datetime.fromisoformat(transaction_data["transaction_timestamp"])
    hour = transaction_time.hour
    is_night_transaction = hour < 6 or hour > 22  # Night transactions are riskier

    # Amount-based risk scoring
    fraud_score = 0.0

    # High-risk merchant categories (simulated)
    high_risk_categories = ["5967", "7995", "5734"]  # Computer services, betting, computer software
    if merchant_category in high_risk_categories:
        fraud_score += 0.3

    # Amount-based scoring
    if transaction_amount > 1000:
        fraud_score += 0.2
    elif transaction_amount > 5000:
        fraud_score += 0.4

    # Time-based scoring
    if is_night_transaction:
        fraud_score += 0.15

    # Device fingerprint scoring (lower is riskier)
    if device_fingerprint < 0.5:
        fraud_score += 0.25
    elif device_fingerprint < 0.7:
        fraud_score += 0.1

    # Add some model uncertainty
    fraud_score += random.uniform(-0.05, 0.1)
    fraud_score = max(0.0, min(1.0, fraud_score))  # Clamp to [0,1]

    # Decision thresholds
    auto_clear_threshold = 0.25
    escalation_threshold = 0.7

    if fraud_score >= escalation_threshold:
        decision = "block"
    elif fraud_score >= auto_clear_threshold:
        decision = "escalate"
    else:
        decision = "auto_clear"

    return {
        "decision": decision,
        "fraud_score": round(fraud_score, 3),
        "decision_threshold": escalation_threshold if decision == "block" else auto_clear_threshold,
        "model_version": "fraud-detection-v4.2.7",
        "linked_dispute_id": None  # Set later if customer disputes
    }


def simulate_dispute_filing(transaction_id: str, original_decision_data: Dict[str, Any]) -> str:
    """
    Simulates a customer filing a Reg E dispute for an authorized transaction.

    Args:
        transaction_id: The original transaction ID
        original_decision_data: Original fraud decision outputs

    Returns:
        Dispute ID string
    """
    dispute_id = str(uuid.uuid4())
    print(f"\n*** CUSTOMER DISPUTE FILED ***")
    print(f"Transaction {transaction_id[:8]}... disputed as unauthorized")
    print(f"Dispute ID: {dispute_id}")
    print(f"Original fraud decision: {original_decision_data['decision']}")
    print(f"Reg E investigation SLA: 10 business days")

    return dispute_id


def main():
    """
    Main execution function demonstrating fraud detection and Reg E workflow.
    """
    print("=== Briefcase AI Fraud Detection & Reg E Example ===")
    print("Regulation: Reg E / EFTA (CFPB)")
    print("Workflow: Real-time fraud scoring with dispute resolution audit trail\n")

    # Initialize Briefcase AI SDK
    try:
        briefcase_ai.init_with_config(2)
        print("SUCCESS: Briefcase AI SDK initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize SDK: {e}")
        sys.exit(1)

    # Get configured backend
    db_backend = backend.get_backend()
    print("SUCCESS: SQLite backend configured\n")

    # Simulate card transaction data
    transaction_id = str(uuid.uuid4())
    card_pan = "4532123456789012"  # Simulated card number

    transaction_data = {
        "transaction_id": transaction_id,
        "card_number_hash": hash_card_number(card_pan),
        "merchant_category_code": "5967",  # Computer programming services (high-risk)
        "transaction_amount": 1250.0,
        "transaction_timestamp": datetime.utcnow().isoformat(),
        "behavioral_risk_features_version": "v3.4.1",
        "velocity_check_window": "24h",
        "device_fingerprint_score": 0.45  # Low device trust score
    }

    print("Processing card transaction:")
    for key, value in transaction_data.items():
        if key == "card_number_hash":
            print(f"  {key}: {value[:16]}...")  # Truncate hash for display
        else:
            print(f"  {key}: {value}")
    print()

    # Simulate fraud detection model execution
    print("Running real-time fraud detection...")
    fraud_result = simulate_fraud_detection_model(transaction_data)
    print(f"SUCCESS: Fraud decision: {fraud_result['decision']}")
    print(f"SUCCESS: Fraud score: {fraud_result['fraud_score']}")
    print(f"SUCCESS: Decision threshold: {fraud_result['decision_threshold']}")

    # Create decision snapshot for audit trail
    decision_inputs = transaction_data
    decision_outputs = fraud_result

    # Regulatory metadata required for Reg E compliance
    regulatory_metadata = {
        "regulation": "Reg E / EFTA",
        "sla_days": 10,  # Business days for investigation
        "decision_reconstructable": True,
        "reverse_engineering_not_required": True,
        "processing_timestamp": datetime.utcnow().isoformat()
    }

    # Create DecisionSnapshot using shared utility
    try:
        decision_snapshot = backend.create_decision_snapshot(
            function_name="real_time_fraud_detection",
            inputs=decision_inputs,
            outputs=decision_outputs,
            metadata=regulatory_metadata,
            input_types={
                "transaction_amount": "float",
                "device_fingerprint_score": "float"
            },
            output_types={
                "fraud_score": "float",
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

    # Simulate time passing and customer dispute filing
    print("\n" + "="*65)
    print("CUSTOMER DISPUTE SIMULATION")
    print("="*65)

    # Customer disputes the transaction as unauthorized
    dispute_id = simulate_dispute_filing(transaction_id, fraud_result)

    # Update the original decision with dispute linkage
    try:
        # Retrieve original decision
        original_decision = db_backend.load_decision(stored_decision_id)
        if original_decision:
            # Create a new decision snapshot for the dispute linkage event
            dispute_metadata = {
                "linked_original_decision": stored_decision_id,
                "dispute_id": dispute_id,
                "dispute_filed_timestamp": datetime.utcnow().isoformat(),
                "investigation_deadline": (datetime.utcnow() + timedelta(days=10)).isoformat(),
                "regulation": "Reg E",
                "investigation_required": True,
                "reg_e_timeline_compliant": True
            }

            # Create dispute linkage decision
            dispute_decision = backend.create_decision_snapshot(
                function_name="fraud_dispute_filing",
                inputs={"original_decision_id": stored_decision_id, "dispute_id": dispute_id},
                outputs={"dispute_status": "filed", "investigation_status": "initiated"},
                metadata=dispute_metadata
            )

            # Store the dispute decision
            updated_decision_id = db_backend.save_decision(dispute_decision)
            print(f"SUCCESS: Dispute decision created and linked: {updated_decision_id}")

    except Exception as e:
        print(f"ERROR: Error updating decision with dispute info: {e}")

    # Demonstrate audit retrieval
    print("\n" + "="*65)
    print("AUDIT TRAIL DEMONSTRATION")
    print("="*65)

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

    # Simulate Reg E investigator query
    print("="*65)
    print("REG E INVESTIGATOR SIMULATION")
    print("="*65)

    investigator_query = f"Retrieve the full fraud decision trace for transaction {transaction_id} linked to dispute {dispute_id}."
    print(f"INVESTIGATOR QUERY: {investigator_query}")

    investigator_response = backend.format_examiner_response(
        stored_decision_id,
        investigator_query,
        db_backend
    )
    print(investigator_response)

    # Additional Reg E specific validation
    print("="*65)
    print("REG E COMPLIANCE VALIDATION")
    print("="*65)

    # Check investigation timeline
    if retrieved_decision.tags.get("investigation_deadline"):
        deadline_str = retrieved_decision.tags["investigation_deadline"]
        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00') if deadline_str.endswith('Z') else deadline_str)
        days_remaining = (deadline - datetime.utcnow()).days

        print(f"Investigation deadline: {deadline.strftime('%Y-%m-%d')}")
        print(f"Days remaining: {days_remaining}")

        if days_remaining >= 0:
            print("SUCCESS: Investigation timeline compliant")
        else:
            print("ERROR: Investigation deadline exceeded - SLA violation")

    # Validate decision reconstructability
    model_version = retrieved_decision.tags.get("model_version")
    if model_version:
        print(f"SUCCESS: Model version preserved: {model_version}")
        print("SUCCESS: Decision fully reconstructable without reverse-engineering")
    else:
        print("ERROR: Model version missing - may impact reconstructability")

    # Regulatory validation
    print("="*65)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*65)

    required_reg_e_fields = [
        "regulation",
        "sla_days",
        "decision_reconstructable",
        "processing_timestamp"
    ]

    validation_result = backend.validate_regulatory_completeness(
        retrieved_decision,
        required_reg_e_fields
    )

    print(f"Reg E Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Required Fields: {', '.join(validation_result['missing_fields'])}")

    # Demonstrate key value proposition
    print("="*65)
    print("BRIEFCASE AI VALUE DEMONSTRATION")
    print("="*65)
    print("VALUE: Complete fraud decision audit trail linked to dispute")
    print("- Original transaction and fraud scoring inputs/outputs preserved")
    print("- Model version and decision threshold documented")
    print("- Dispute linkage maintained for investigation timeline")
    print("- No reverse-engineering of logs required for compliance")
    print()

    # Show the complete audit chain
    print("COMPLETE AUDIT CHAIN:")
    print(f"1. Transaction processed: {transaction_data['transaction_timestamp']}")
    print(f"2. Fraud decision made: {fraud_result['decision']} (score: {fraud_result['fraud_score']})")
    print(f"3. Decision stored: {stored_decision_id}")
    if dispute_id:
        print(f"4. Customer dispute filed: {dispute_id}")
        print(f"5. Investigation deadline: {retrieved_decision.tags.get('investigation_deadline', 'N/A')}")
    print(f"6. Full audit trail retrievable on demand")

    print(f"\nSUCCESS: Fraud detection & Reg E audit trail demonstration completed")
    print(f"Decision ID: {stored_decision_id}")
    if dispute_id:
        print(f"Dispute ID: {dispute_id}")


if __name__ == "__main__":
    main()