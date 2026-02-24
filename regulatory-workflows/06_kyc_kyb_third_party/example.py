#!/usr/bin/env python3
"""
Briefcase AI Example: KYC / KYB Verification (Third-Party Vendor)

Context: FinCEN/OCC/State regulators. Bank accountable to FinCEN and OCC —
third-party vendor decision is not a defense. Vendor IP is a barrier (model
internals cannot be exposed). Briefcase AI is deployed in-environment at the
bank layer, capturing vendor inputs/outputs without touching vendor internals.

Demonstrates:
- Third-party vendor KYC/KYB decision capture
- Bank-controlled audit record independent of vendor
- FinCEN examination readiness without vendor cooperation
- Vendor IP protection while maintaining compliance
"""

import sys
import os
import uuid
import hashlib
import random
from datetime import datetime
from typing import Dict, Any, Optional

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

try:
    import backend
    # Import SDK classes from backend (handles mock implementation if SDK not available)
    from backend import briefcase_ai, DecisionSnapshot, Input, Output, SqliteBackend
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)


def hash_document(document_content: str) -> str:
    """
    Hashes sensitive document content for secure audit trail storage.
    Never stores raw document content in audit records.

    Args:
        document_content: Simulated document content

    Returns:
        SHA-256 hash of document content
    """
    return hashlib.sha256(document_content.encode()).hexdigest()


def simulate_third_party_kyc_vendor(customer_data: Dict[str, Any], vendor_config: Dict[str, str]) -> Dict[str, Any]:
    """
    Simulates a third-party KYC/KYB vendor API call and response.
    In production, this would be an actual API call to vendors like
    Jumio, Onfido, LexisNexis, or Refinitiv.

    Args:
        customer_data: Customer information sent to vendor
        vendor_config: Vendor API configuration

    Returns:
        Dictionary containing vendor response
    """
    applicant_type = customer_data["applicant_type"]
    document_type = customer_data["document_type"]
    submitted_name = customer_data["submitted_name"]

    # Simulate different vendor behavior based on customer profile
    identity_score = 0.0
    document_auth_score = 0.0
    sanctions_match = False

    # Individual verification simulation
    if applicant_type == "individual":
        if document_type == "passport":
            # Passports generally have higher authenticity confidence
            document_auth_score = random.uniform(0.85, 0.98)
            identity_score = random.uniform(0.80, 0.95)
        elif document_type == "drivers_license":
            # Driver's licenses vary by state quality
            document_auth_score = random.uniform(0.70, 0.92)
            identity_score = random.uniform(0.75, 0.90)
        else:
            # Other documents
            document_auth_score = random.uniform(0.60, 0.85)
            identity_score = random.uniform(0.65, 0.85)

        # Simulate name variations that might cause identity matching issues
        if "Jr" in submitted_name or "III" in submitted_name:
            identity_score *= 0.9  # Name variations reduce confidence

    # Business verification simulation
    elif applicant_type == "business":
        if document_type == "ein":
            # EIN verification with IRS database
            document_auth_score = random.uniform(0.90, 0.99)
            identity_score = random.uniform(0.85, 0.95)
        else:
            # Articles of incorporation, business licenses
            document_auth_score = random.uniform(0.75, 0.90)
            identity_score = random.uniform(0.70, 0.88)

        # Business names with common words might have lower identity scores
        common_business_words = ["LLC", "Inc", "Corp", "Company"]
        if any(word in submitted_name for word in common_business_words):
            identity_score *= 0.95

    # Simulate sanctions screening (simplified)
    high_risk_indicators = ["Petrov", "Kozlov", "Volkov", "DPRK", "Iran"]
    if any(indicator in submitted_name for indicator in high_risk_indicators):
        sanctions_match = True
        identity_score *= 0.7  # Reduce confidence due to sanctions concern

    # Apply vendor-specific model behavior
    vendor_name = vendor_config["vendor_name"]
    if vendor_name == "jumio":
        # Jumio tends to be more conservative
        document_auth_score *= 0.95
    elif vendor_name == "onfido":
        # Onfido has strong liveness detection
        identity_score *= 1.02
    elif vendor_name == "lexisnexis":
        # LexisNexis has comprehensive databases
        identity_score *= 1.01

    # Determine final decision based on vendor thresholds
    identity_threshold = 0.80
    document_threshold = 0.75

    if sanctions_match:
        kyc_decision = "decline"
    elif identity_score >= identity_threshold and document_auth_score >= document_threshold:
        kyc_decision = "auto_approve"
    elif identity_score >= 0.60 and document_auth_score >= 0.60:
        kyc_decision = "manual_review"
    else:
        kyc_decision = "decline"

    return {
        "kyc_decision": kyc_decision,
        "identity_score": round(identity_score, 3),
        "document_auth_score": round(document_auth_score, 3),
        "sanctions_match_flag": sanctions_match,
        "vendor_decision_id": f"{vendor_name.upper()}-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(100000, 999999)}",
        "bank_audit_record_id": str(uuid.uuid4()),
        "vendor_rule_version": vendor_config["vendor_rule_version"],
        "vendor_api_endpoint": vendor_config["api_endpoint"]
    }


def main():
    """
    Main execution function demonstrating KYC/KYB third-party vendor workflow.
    """
    print("=== Briefcase AI KYC/KYB Third-Party Vendor Example ===")
    print("Regulation: BSA/AML / FinCEN CDD Rule")
    print("Workflow: Third-party vendor verification with bank-controlled audit trail\n")

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

    # Simulate vendor configuration
    vendor_config = {
        "vendor_name": "jumio",
        "vendor_rule_version": "jumio-kyc-rules-v4.2.1",
        "api_endpoint": "https://api.jumio.com/api/v1/verification",
        "timeout_seconds": 30
    }

    print(f"Configured third-party vendor: {vendor_config['vendor_name'].title()}")
    print(f"Vendor rule version: {vendor_config['vendor_rule_version']}")
    print(f"API endpoint: {vendor_config['api_endpoint']}")
    print()

    # Simulate new account applicant data
    applicant_id = str(uuid.uuid4())
    passport_content = f"PASSPORT_USA_{applicant_id}_JOHN_DOE"  # Simulated document content

    customer_data = {
        "applicant_id": applicant_id,
        "applicant_type": "individual",
        "document_type": "passport",
        "document_hash": hash_document(passport_content),
        "submitted_name": "John Doe",
        "submitted_dob": "1985-03-15",
        "submitted_ein": None,  # Not applicable for individuals
        "vendor_rule_version": vendor_config["vendor_rule_version"],
        "vendor_api_endpoint": vendor_config["api_endpoint"]
    }

    print("Processing KYC verification for new applicant:")
    for key, value in customer_data.items():
        if key == "document_hash":
            print(f"  {key}: {value[:16]}...")  # Truncate hash for display
        elif value is not None:
            print(f"  {key}: {value}")
    print()

    # Call third-party vendor API (simulated)
    print(f"Calling {vendor_config['vendor_name'].title()} KYC API...")
    try:
        vendor_response = simulate_third_party_kyc_vendor(customer_data, vendor_config)
        print(f"SUCCESS: Vendor API response received")
        print(f"SUCCESS: KYC decision: {vendor_response['kyc_decision']}")
        print(f"SUCCESS: Identity score: {vendor_response['identity_score']}")
        print(f"SUCCESS: Document auth score: {vendor_response['document_auth_score']}")
        print(f"SUCCESS: Vendor decision ID: {vendor_response['vendor_decision_id']}")
    except Exception as e:
        print(f"ERROR: Vendor API call failed: {e}")
        sys.exit(1)

    # Create decision snapshot for bank-controlled audit trail
    decision_inputs = customer_data
    decision_outputs = vendor_response

    # Regulatory metadata for FinCEN/OCC compliance
    regulatory_metadata = {
        "regulation": "BSA/AML / FinCEN CDD Rule",
        "vendor_ip_exposed": False,
        "bank_controlled_audit_record": True,
        "vendor_cooperation_required_for_retrieval": False,
        "third_party_risk_documented": True,
        "vendor_name": vendor_config["vendor_name"],
        "audit_timestamp": datetime.utcnow().isoformat()
    }

    # Create DecisionSnapshot using shared utility
    try:
        decision_snapshot = backend.create_decision_snapshot(
            function_name="kyc_kyb_third_party_verification",
            inputs=decision_inputs,
            outputs=decision_outputs,
            metadata=regulatory_metadata,
            input_types={
                "applicant_type": "str",
                "document_type": "str"
            },
            output_types={
                "identity_score": "float",
                "document_auth_score": "float",
                "sanctions_match_flag": "bool"
            }
        )

        print(f"SUCCESS: Decision snapshot created")

    except Exception as e:
        print(f"ERROR: Error creating decision snapshot: {e}")
        sys.exit(1)

    # Store decision in bank-controlled backend
    try:
        stored_decision_id = db_backend.save_decision(decision_snapshot)
        print(f"SUCCESS: Decision stored in bank-controlled audit trail: {stored_decision_id}")

        # Demonstrate bank independence
        print(f"SUCCESS: Audit record {vendor_response['bank_audit_record_id']} stored independently of vendor")
    except Exception as e:
        print(f"ERROR: Error storing decision: {e}")
        sys.exit(1)

    # Demonstrate audit retrieval
    print("\n" + "="*70)
    print("AUDIT TRAIL DEMONSTRATION")
    print("="*70)

    # Load decision back from backend
    try:
        retrieved_decision = db_backend.load_decision(stored_decision_id)
        if retrieved_decision:
            backend.print_audit_summary(retrieved_decision)
        else:
            print("ERROR: Failed to retrieve decision from backend")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error retrieving decision: {e}")
        sys.exit(1)

    # Simulate FinCEN examiner query
    print("="*70)
    print("FINCEN EXAMINER SIMULATION")
    print("="*70)

    examiner_query = f"Justify the KYC decision for account {applicant_id}."
    print(f"EXAMINER QUERY: {examiner_query}")

    examiner_response = backend.format_examiner_response(
        stored_decision_id,
        examiner_query,
        db_backend
    )
    print(examiner_response)

    # Demonstrate vendor independence
    print("="*70)
    print("VENDOR INDEPENDENCE DEMONSTRATION")
    print("="*70)

    print("BANK-CONTROLLED AUDIT CAPABILITIES:")
    print(f"SUCCESS: Complete audit record stored in bank system: {stored_decision_id}")
    print(f"SUCCESS: Vendor decision ID preserved: {vendor_response['vendor_decision_id']}")
    print(f"SUCCESS: Vendor rule version documented: {vendor_response['vendor_rule_version']}")
    print(f"SUCCESS: Bank audit record ID: {vendor_response['bank_audit_record_id']}")
    print()
    print("VENDOR COOPERATION NOT REQUIRED:")
    print("- Bank can retrieve complete audit trail independently")
    print("- Vendor IP and internals remain protected")
    print("- FinCEN examination supported without vendor involvement")
    print("- Regulatory compliance maintained under bank control")

    # Simulate a scenario where vendor is unavailable
    print("\n" + "="*70)
    print("VENDOR UNAVAILABILITY SCENARIO")
    print("="*70)
    print("SCENARIO: Vendor system is down or vendor relationship terminated")
    print("BANK RESPONSE: Complete audit trail still available")
    print()

    # Retrieve decision again to demonstrate independence
    try:
        independent_retrieval = db_backend.load_decision(stored_decision_id)
        if independent_retrieval:
            print("SUCCESS: Audit record retrieved successfully without vendor cooperation")
            print(f"  - KYC Decision: {independent_retrieval.outputs[0].value if independent_retrieval.outputs else 'N/A'}")
            print(f"  - Vendor Used: {independent_retrieval.tags.get('vendor_name', 'N/A')}")
            print(f"  - Decision Timestamp: {getattr(independent_retrieval, 'created_at', 'N/A')}")
            print(f"  - Bank Audit ID: {getattr(independent_retrieval, 'id', 'N/A')}")
    except Exception as e:
        print(f"ERROR: Error in independent retrieval: {e}")

    # Regulatory validation
    print("\n" + "="*70)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*70)

    required_kyc_fields = [
        "regulation",
        "vendor_ip_exposed",
        "bank_controlled_audit_record",
        "vendor_cooperation_required_for_retrieval"
    ]

    validation_result = backend.validate_regulatory_completeness(
        retrieved_decision,
        required_kyc_fields
    )

    print(f"FinCEN Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Required Fields: {', '.join(validation_result['missing_fields'])}")

    # Business continuity demonstration
    print("\n" + "="*70)
    print("BUSINESS CONTINUITY BENEFITS")
    print("="*70)
    print("SUCCESS: Vendor relationship changes: Audit trail preserved")
    print("SUCCESS: Vendor system outages: Bank operations continue")
    print("SUCCESS: Regulatory examinations: No vendor coordination required")
    print("SUCCESS: Vendor IP protection: Model internals never exposed")
    print("SUCCESS: Multi-vendor strategies: Consistent audit across all vendors")

    print(f"\nSUCCESS: KYC/KYB third-party vendor audit trail demonstration completed")
    print(f"Decision ID: {stored_decision_id}")
    print(f"Vendor Decision ID: {vendor_response['vendor_decision_id']}")
    print(f"Bank Audit Record ID: {vendor_response['bank_audit_record_id']}")


if __name__ == "__main__":
    main()