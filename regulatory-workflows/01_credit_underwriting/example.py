#!/usr/bin/env python3
"""
Briefcase AI Example: ML Credit Underwriting (ECOA/Reg B Compliance)

Context: OCC/CFPB regulated bank. ECOA/Reg B nondiscrimination applies.
Adverse action notice required for any denial or unfavorable credit term change.

Demonstrates:
- AI underwriting model decision capture
- Adverse action reason code tracking
- ECOA/Reg B compliance audit trail
- OCC examiner query simulation
"""

import sys
import os
import uuid
import random
from datetime import datetime
from typing import Dict, Any

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


def simulate_credit_underwriting_model(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates an AI credit underwriting model decision.
    In production, this would be replaced with actual ML model inference.

    Args:
        applicant_data: Dictionary containing applicant information

    Returns:
        Dictionary containing underwriting decision and supporting data
    """
    # Simulate model scoring based on inputs
    annual_income = applicant_data["annual_income"]
    bureau_score = applicant_data["bureau_score"]
    dti_ratio = applicant_data["debt_to_income_ratio"]
    loan_amount = applicant_data["loan_amount_requested"]

    # Simple rule-based simulation for demonstration
    risk_score = 0.0
    if bureau_score >= 720:
        risk_score += 0.4
    elif bureau_score >= 650:
        risk_score += 0.2
    else:
        risk_score -= 0.2

    if dti_ratio <= 0.35:
        risk_score += 0.3
    elif dti_ratio <= 0.45:
        risk_score += 0.1
    else:
        risk_score -= 0.1

    if annual_income >= 75000:
        risk_score += 0.2

    # Add some randomness to simulate model uncertainty
    risk_score += random.uniform(-0.1, 0.1)
    confidence = max(0.6, min(0.95, risk_score + 0.3))

    # Decision logic
    if risk_score >= 0.5:
        decision = "approve"
        approved_amount = loan_amount
        adverse_action_codes = None
    elif risk_score >= 0.2:
        decision = "counter_offer"
        approved_amount = loan_amount * 0.75  # Reduce loan amount
        adverse_action_codes = ["credit_history", "debt_to_income_ratio"]
    else:
        decision = "decline"
        approved_amount = None
        adverse_action_codes = ["credit_history", "insufficient_income", "debt_to_income_ratio"]

    return {
        "decision": decision,
        "approved_amount": approved_amount,
        "adverse_action_reason_codes": adverse_action_codes,
        "confidence_score": round(confidence, 3),
        "model_version": "underwriting-model-v3.2.1",
        "decision_trace_id": str(uuid.uuid4())
    }


def main():
    """
    Main execution function demonstrating credit underwriting workflow.
    """
    print("=== Briefcase AI Credit Underwriting Example ===")
    print("Regulation: ECOA/Reg B (OCC/CFPB)")
    print("Workflow: ML-based credit decision with adverse action tracking\n")

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

    # Simulate loan application data
    applicant_id = str(uuid.uuid4())
    application_data = {
        "applicant_id": applicant_id,
        "annual_income": 65000.0,
        "bureau_score": 685,
        "debt_to_income_ratio": 0.42,
        "loan_amount_requested": 25000.0,
        "loan_purpose": "auto",
        "behavioral_attributes_version": "v2.1.4"
    }

    print("Processing loan application:")
    for key, value in application_data.items():
        print(f"  {key}: {value}")
    print()

    # Simulate AI underwriting model execution
    print("Running AI underwriting model...")
    model_output = simulate_credit_underwriting_model(application_data)
    print(f"SUCCESS: Model decision: {model_output['decision']}")
    print(f"SUCCESS: Confidence: {model_output['confidence_score']}")

    # Create decision snapshot for audit trail
    decision_inputs = application_data
    decision_outputs = model_output

    # Regulatory metadata required for ECOA/Reg B compliance
    regulatory_metadata = {
        "regulation": "ECOA/Reg B",
        "adverse_action_required": model_output["decision"] in ["decline", "counter_offer"],
        "bank_owns_model": True,
        "decision_timestamp": datetime.utcnow().isoformat(),
        "examiner_ready": True
    }

    # Create DecisionSnapshot using shared utility
    try:
        decision_snapshot = backend.create_decision_snapshot(
            function_name="credit_underwriting_decision",
            inputs=decision_inputs,
            outputs=decision_outputs,
            metadata=regulatory_metadata,
            input_types={
                "annual_income": "float",
                "bureau_score": "int",
                "debt_to_income_ratio": "float",
                "loan_amount_requested": "float"
            },
            output_types={
                "confidence_score": "float",
                "approved_amount": "float"
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
    print("\n" + "="*50)
    print("AUDIT TRAIL DEMONSTRATION")
    print("="*50)

    # Load decision back from backend
    try:
        retrieved_decision = db_backend.load_decision(stored_decision_id)
        if retrieved_decision:
            backend.print_audit_summary(stored_decision_id, "Credit underwriting decision retrieved")
            print(f"Function: {getattr(retrieved_decision, 'function_name', 'N/A')}")
            print(f"Decision ID: {stored_decision_id}")
        else:
            print("ERROR: Failed to retrieve decision from backend")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error retrieving decision: {e}")
        sys.exit(1)

    # Simulate OCC examiner query
    print("="*50)
    print("OCC EXAMINER SIMULATION")
    print("="*50)

    examiner_query = f"What were the model inputs and adverse action reasons for applicant {applicant_id}?"
    print(f"EXAMINER QUERY: {examiner_query}")

    examiner_response = backend.format_examiner_response(
        stored_decision_id,
        examiner_query,
        db_backend
    )
    print(examiner_response)

    # Demonstrate deterministic replay (if supported by SDK)
    print("="*50)
    print("DETERMINISTIC REPLAY")
    print("="*50)

    try:
        # Note: This would use the actual replay API from the SDK
        # For now, we simulate by reloading and validating consistency
        replay_decision = db_backend.load_decision(stored_decision_id)

        if replay_decision:
            print("SUCCESS: Decision replay validation successful")
            print(f"  Original decision ID: {stored_decision_id}")
            print(f"  Decision function: {getattr(replay_decision, 'function_name', 'N/A')}")
            # Model version would be preserved in outputs
            for output in getattr(replay_decision, 'outputs', []):
                if output.name == 'model_version':
                    print(f"  Model version preserved: {output.value}")
        else:
            print("ERROR: Decision replay validation failed")

    except Exception as e:
        print(f"ERROR: Replay error: {e}")

    # Regulatory validation
    print("="*50)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*50)

    required_fields = [
        "regulation",
        "adverse_action_required",
        "bank_owns_model",
        "decision_timestamp"
    ]

    validation_result = backend.validate_regulatory_completeness(
        retrieved_decision,
        required_fields
    )

    print(f"Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Fields: {', '.join(validation_result['missing_fields'])}")

    print(f"\nSUCCESS: Credit underwriting audit trail demonstration completed")
    print(f"Decision ID: {stored_decision_id}")


if __name__ == "__main__":
    main()