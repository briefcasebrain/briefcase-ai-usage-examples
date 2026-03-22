#!/usr/bin/env python3
"""
Briefcase AI Example: Real-Time Payments Fraud (FedNow / RTP)

Context: OCC/Fed/CFPB. FedNow and RTP payments are irrevocable — no recall mechanism
once sent. Fraud routing decision must complete within 500ms. Every wrong approval
is a permanent, unrecoverable loss.

Demonstrates:
- Sub-500ms fraud routing decision capture
- Irrevocable payment risk tracking
- Model drift detection before production exposure
- Complete decision audit trail for unrecoverable losses
"""

import sys
import os
import uuid
import hashlib
import random
import time
from datetime import datetime
from typing import Dict, Any

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


def hash_account(account_number: str) -> str:
    """
    Hashes account numbers for secure storage in audit trail.

    Args:
        account_number: Account number to hash

    Returns:
        SHA-256 hash of account number
    """
    return hashlib.sha256(account_number.encode()).hexdigest()[:16]


def simulate_rtp_fraud_routing_model(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates a real-time payment fraud routing model.
    Must complete decision within 500ms for FedNow/RTP requirements.

    Args:
        payment_data: Dictionary containing payment information

    Returns:
        Dictionary containing routing decision and risk assessment
    """
    start_time = time.time()

    payment_amount = payment_data["payment_amount"]
    sender_velocity = payment_data["sender_velocity_score"]
    receiver_risk = payment_data["receiver_risk_score"]
    payment_rail = payment_data["payment_rail"]

    # Risk scoring for real-time payments
    risk_score = 0.0

    # Amount-based risk
    if payment_amount > 10000:
        risk_score += 0.3
    elif payment_amount > 25000:
        risk_score += 0.5

    # Sender velocity risk (higher score = more trusted)
    if sender_velocity < 0.3:
        risk_score += 0.4
    elif sender_velocity < 0.6:
        risk_score += 0.2

    # Receiver risk (higher score = riskier)
    risk_score += receiver_risk * 0.3

    # Rail-specific risk adjustments
    if payment_rail == "fednow":
        # FedNow has additional scrutiny due to government backing
        risk_score *= 0.9
    elif payment_rail == "rtp":
        # RTP has established fraud patterns
        risk_score *= 1.1

    # Add model uncertainty
    risk_score += random.uniform(-0.05, 0.05)
    risk_score = max(0.0, min(1.0, risk_score))

    # Conservative threshold for irrevocable payments
    approval_threshold = 0.4

    # Make routing decision
    if risk_score <= approval_threshold:
        routing_decision = "approve"
    else:
        routing_decision = "reject"

    # Calculate decision latency
    end_time = time.time()
    decision_latency_ms = int((end_time - start_time) * 1000)

    return {
        "routing_decision": routing_decision,
        "confidence_score": round(1.0 - risk_score, 3),  # Confidence inversely related to risk
        "decision_latency_ms": decision_latency_ms,
        "irrevocability_flag": routing_decision == "approve",  # All approvals are irrevocable
        "risk_threshold": approval_threshold,
        "model_version": "rtp-fraud-v5.1.2"
    }


def main():
    """
    Main execution function demonstrating real-time payments fraud workflow.
    """
    print("=== Briefcase AI Real-Time Payments Fraud Example ===")
    print("Regulation: OCC/Fed RTP Guidance (FedNow/RTP)")
    print("Workflow: Sub-500ms irrevocable payment fraud routing\n")

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

    # Simulate real-time payment data
    payment_id = str(uuid.uuid4())
    sender_account = "987654321012"
    receiver_account = "123456789098"

    payment_data = {
        "payment_id": payment_id,
        "payment_rail": "fednow",
        "sender_account_hash": hash_account(sender_account),
        "receiver_account_hash": hash_account(receiver_account),
        "payment_amount": 15000.0,
        "payment_timestamp": datetime.utcnow().isoformat(),
        "sender_velocity_score": 0.25,  # Low trust score
        "receiver_risk_score": 0.65,    # High risk score
        "model_version": "rtp-fraud-v5.1.2",
        "routing_config_version": "rtp-routing-v2.0.4"
    }

    print("Processing real-time payment:")
    for key, value in payment_data.items():
        if "hash" in key:
            print(f"  {key}: {value[:12]}...")
        else:
            print(f"  {key}: {value}")
    print()

    # Simulate fraud routing model execution
    print("Running fraud routing model (must complete <500ms)...")
    routing_result = simulate_rtp_fraud_routing_model(payment_data)

    print(f"SUCCESS: Routing decision: {routing_result['routing_decision']}")
    print(f"SUCCESS: Confidence: {routing_result['confidence_score']}")
    print(f"SUCCESS: Decision latency: {routing_result['decision_latency_ms']}ms")

    # Validate latency requirement
    if routing_result['decision_latency_ms'] <= 500:
        print(f"SUCCESS: Latency compliant: {routing_result['decision_latency_ms']}ms <= 500ms")
    else:
        print(f"ERROR: Latency violation: {routing_result['decision_latency_ms']}ms > 500ms")

    # Create decision snapshot for audit trail
    decision_inputs = payment_data
    decision_outputs = routing_result

    # Regulatory metadata for RTP compliance
    regulatory_metadata = {
        "regulation": "OCC/Fed RTP Guidance",
        "irrevocable": routing_result["irrevocability_flag"],
        "max_decision_latency_ms": 500,
        "actual_latency_ms": routing_result["decision_latency_ms"],
        "permanent_loss_risk": routing_result["routing_decision"] == "approve",
        "routing_timestamp": datetime.utcnow().isoformat()
    }

    # Create DecisionSnapshot using shared utility
    try:
        decision_snapshot = backend.create_decision_snapshot(
            function_name="rtp_fraud_routing",
            inputs=decision_inputs,
            outputs=decision_outputs,
            metadata=regulatory_metadata,
            input_types={
                "payment_amount": "float",
                "sender_velocity_score": "float",
                "receiver_risk_score": "float"
            },
            output_types={
                "confidence_score": "float",
                "decision_latency_ms": "int"
            }
        )

        print(f"SUCCESS: Decision snapshot created")

    except Exception as e:
        print(f"ERROR: Error creating decision snapshot: {e}")
        sys.exit(1)

    # Store decision in backend
    try:
        stored_decision_id = db_backend.save_decision(decision_snapshot)
        print(f"SUCCESS: Decision stored in audit trail: {stored_decision_id}")
    except Exception as e:
        print(f"ERROR: Error storing decision: {e}")
        sys.exit(1)

    # Demonstrate model drift detection (special requirement)
    print("\n" + "="*70)
    print("MODEL DRIFT DETECTION DEMONSTRATION")
    print("="*70)

    # Simulate a second decision with different model version
    print("Simulating model version change before production...")

    # Second payment with updated model version
    second_payment_data = payment_data.copy()
    second_payment_data["payment_id"] = str(uuid.uuid4())
    second_payment_data["model_version"] = "rtp-fraud-v5.2.0"  # New version

    # Simulate different behavior in new model
    second_routing_result = simulate_rtp_fraud_routing_model(second_payment_data)
    second_routing_result["model_version"] = "rtp-fraud-v5.2.0"

    # Create second snapshot
    second_snapshot = backend.create_decision_snapshot(
        function_name="rtp_fraud_routing",
        inputs=second_payment_data,
        outputs=second_routing_result,
        metadata={
            "regulation": "OCC/Fed RTP Guidance",
            "irrevocable": second_routing_result["irrevocability_flag"],
            "routing_timestamp": datetime.utcnow().isoformat()
        }
    )

    second_stored_id = db_backend.save_decision(second_snapshot)

    # Demonstrate drift detection
    decisions_for_analysis = [
        db_backend.load_decision(stored_decision_id),
        db_backend.load_decision(second_stored_id)
    ]

    drift_analysis = backend.simulate_model_drift_detection(
        decisions_for_analysis,
        "model_version",
        "confidence_score"
    )

    print("DRIFT DETECTION RESULTS:")
    if drift_analysis["drift_detected"]:
        print("WARNING: Model drift detected before production deployment")
        for version, stats in drift_analysis["cohorts"].items():
            print(f"  Model {version}: Avg confidence = {stats['mean']:.3f} ({stats['count']} decisions)")
    else:
        print("SUCCESS: No significant model drift detected")

    # Demonstrate audit retrieval
    print("\n" + "="*70)
    print("AUDIT TRAIL DEMONSTRATION")
    print("="*70)

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

    # Simulate post-dispute examiner query
    print("="*70)
    print("POST-DISPUTE EXAMINER SIMULATION")
    print("="*70)

    examiner_query = f"Prove the fraud routing decision for payment {payment_id} was defensible at the time it was made."
    print(f"EXAMINER QUERY: {examiner_query}")

    examiner_response = backend.format_examiner_response(
        stored_decision_id,
        examiner_query,
        db_backend
    )
    print(examiner_response)

    # RTP-specific compliance validation
    print("="*70)
    print("RTP COMPLIANCE VALIDATION")
    print("="*70)

    # Check irrevocability tracking
    is_irrevocable = retrieved_decision.tags.get("irrevocable", False)
    routing_decision = None
    for output in retrieved_decision.outputs:
        if output.name == "routing_decision":
            routing_decision = output.value

    if routing_decision == "approve" and is_irrevocable:
        print("SUCCESS: Irrevocable approval properly flagged")
        print("  - Payment cannot be recalled once processed")
        print("  - Audit trail preserves decision rationale permanently")
    elif routing_decision == "reject":
        print("SUCCESS: Payment rejected - no irrevocability risk")
    else:
        print("ERROR: Irrevocability flag inconsistent with decision")

    # Check latency compliance
    actual_latency = retrieved_decision.tags.get("actual_latency_ms")
    max_latency = retrieved_decision.tags.get("max_decision_latency_ms", 500)

    if actual_latency and int(actual_latency) <= int(max_latency):
        print(f"SUCCESS: Decision latency compliant: {actual_latency}ms <= {max_latency}ms")
    else:
        print(f"ERROR: Decision latency non-compliant: {actual_latency}ms > {max_latency}ms")

    # Regulatory validation
    print("="*70)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*70)

    required_rtp_fields = [
        "regulation",
        "irrevocable",
        "max_decision_latency_ms",
        "actual_latency_ms"
    ]

    validation_result = backend.validate_regulatory_completeness(
        retrieved_decision,
        required_rtp_fields
    )

    print(f"RTP Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Required Fields: {', '.join(validation_result['missing_fields'])}")

    # Summary of key capabilities
    print("="*70)
    print("BRIEFCASE AI VALUE FOR RTP")
    print("="*70)
    print("SUCCESS: Sub-500ms decision capture and storage")
    print("SUCCESS: Irrevocable payment risk tracking")
    print("SUCCESS: Model drift detection before production")
    print("SUCCESS: Complete audit defense for unrecoverable losses")
    print("SUCCESS: Regulatory examiner readiness")

    print(f"\nSUCCESS: Real-time payments fraud audit trail demonstration completed")
    print(f"Primary Decision ID: {stored_decision_id}")
    print(f"Model Drift Analysis Decision ID: {second_stored_id}")


if __name__ == "__main__":
    main()