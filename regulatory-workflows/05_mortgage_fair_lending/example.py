#!/usr/bin/env python3
"""
Briefcase AI Example: Mortgage Underwriting & Fair Lending (HMDA)

Context: OCC/CFPB/DOJ/HUD. HMDA requires reporting of covered mortgage applications
with demographic data. ECOA prohibits disparate impact even when intent is neutral.
Mid-year model version change creates retroactive fair lending liability.

Demonstrates:
- Mortgage underwriting with demographic data capture
- Mid-year model version change tracking
- Historical cohort replay across date ranges
- DOJ/CFPB disparate impact investigation support
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

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


def simulate_mortgage_underwriting_model(application_data: Dict[str, Any], model_version: str) -> Dict[str, Any]:
    """
    Simulates mortgage underwriting model with version-specific behavior.

    Args:
        application_data: Mortgage application data
        model_version: Version of the underwriting model to simulate

    Returns:
        Dictionary containing underwriting decision
    """
    income = application_data["applicant_income"]
    loan_amount = application_data["loan_amount"]
    ltv_ratio = application_data["ltv_ratio"]
    property_state = application_data["property_state"]

    # Base risk scoring
    risk_score = 0.0

    # Income-based scoring
    debt_to_income = (loan_amount * 0.004) / (income / 12)  # Rough monthly payment estimation
    if debt_to_income <= 0.28:
        risk_score += 0.4
    elif debt_to_income <= 0.36:
        risk_score += 0.2

    # LTV-based scoring
    if ltv_ratio <= 0.80:
        risk_score += 0.3
    elif ltv_ratio <= 0.90:
        risk_score += 0.1

    # Property state risk (simplified)
    high_appreciation_states = ["CA", "NY", "FL"]
    if property_state in high_appreciation_states:
        risk_score += 0.1

    # Model version specific behavior (simulate algorithmic changes)
    if model_version == "mortgage-model-v1.0":
        # V1 model was more conservative
        approval_threshold = 0.6
        risk_score *= 0.9  # Slightly more conservative
    elif model_version == "mortgage-model-v2.0":
        # V2 model introduced in August, more aggressive
        approval_threshold = 0.5
        risk_score *= 1.1  # Slightly more aggressive

    # Add randomness
    risk_score += random.uniform(-0.1, 0.1)
    risk_score = max(0.0, min(1.0, risk_score))

    # Make decision
    if risk_score >= approval_threshold:
        decision = "approve"
        approved_rate = 3.75 + random.uniform(-0.25, 0.25)
        denial_codes = None
    elif risk_score >= 0.3:
        decision = "counter_offer"
        approved_rate = 4.25 + random.uniform(-0.25, 0.25)
        denial_codes = ["credit_history", "debt_to_income_ratio"]
    else:
        decision = "deny"
        approved_rate = None
        denial_codes = ["credit_history", "insufficient_income", "ltv_ratio"]

    return {
        "decision": decision,
        "approved_rate": approved_rate,
        "denial_reason_codes": denial_codes,
        "confidence_score": round(risk_score, 3),
        "decision_timestamp": datetime.utcnow().isoformat(),
        "model_version": model_version
    }


def create_hmda_application(applicant_type: str, month_offset: int = 0) -> Dict[str, Any]:
    """
    Creates a simulated HMDA-reportable mortgage application.

    Args:
        applicant_type: Demographic profile to simulate
        month_offset: Months before current date

    Returns:
        Dictionary with application data including HMDA demographics
    """
    application_date = datetime.utcnow() - timedelta(days=30 * month_offset)

    # Base application data
    application = {
        "application_id": str(uuid.uuid4()),
        "applicant_income": random.uniform(45000, 150000),
        "loan_amount": random.uniform(200000, 800000),
        "ltv_ratio": random.uniform(0.70, 0.95),
        "property_type": random.choice(["single_family", "condo", "multi_family"]),
        "property_state": random.choice(["CA", "TX", "FL", "NY", "PA"]),
        "application_timestamp": application_date.isoformat()
    }

    # HMDA demographic data (simplified codes)
    if applicant_type == "white":
        application.update({
            "hmda_ethnicity_code": "2",  # Not Hispanic or Latino
            "hmda_race_code": "5",       # White
            "hmda_sex_code": random.choice(["1", "2"])  # Male or Female
        })
    elif applicant_type == "black":
        application.update({
            "hmda_ethnicity_code": "2",  # Not Hispanic or Latino
            "hmda_race_code": "3",       # Black or African American
            "hmda_sex_code": random.choice(["1", "2"])
        })
    elif applicant_type == "hispanic":
        application.update({
            "hmda_ethnicity_code": "1",  # Hispanic or Latino
            "hmda_race_code": "5",       # White (commonly reported combination)
            "hmda_sex_code": random.choice(["1", "2"])
        })

    return application


def main():
    """
    Main execution function demonstrating mortgage fair lending workflow.
    """
    print("=== Briefcase AI Mortgage Underwriting & Fair Lending Example ===")
    print("Regulation: ECOA/HMDA/Reg B (OCC/CFPB/DOJ/HUD)")
    print("Workflow: Model version change tracking for disparate impact analysis\n")

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

    print("="*75)
    print("JANUARY APPLICATIONS (Model v1.0)")
    print("="*75)

    # Create January applications with model v1.0
    january_decisions = []
    january_applications = [
        ("white", 6),  # 6 months ago (January)
        ("white", 6),
        ("black", 6),
        ("black", 6),
        ("hispanic", 6)
    ]

    for demographic, months_ago in january_applications:
        app_data = create_hmda_application(demographic, months_ago)

        # Add model version and feature config
        app_data["model_version"] = "mortgage-model-v1.0"
        app_data["feature_config_hash"] = "sha256:abc123def456"

        print(f"\nProcessing {demographic} applicant application:")
        print(f"  Application ID: {app_data['application_id'][:12]}...")
        print(f"  Income: ${app_data['applicant_income']:,.0f}")
        print(f"  Loan Amount: ${app_data['loan_amount']:,.0f}")
        print(f"  LTV Ratio: {app_data['ltv_ratio']:.2f}")
        print(f"  HMDA Race Code: {app_data['hmda_race_code']}")

        # Run model v1.0
        result = simulate_mortgage_underwriting_model(app_data, "mortgage-model-v1.0")
        print(f"  Decision: {result['decision']}")

        # Create decision snapshot
        regulatory_metadata = {
            "regulation": "ECOA/HMDA/Reg B",
            "disparate_impact_monitoring": True,
            "full_cohort_replay_available": True,
            "doj_referral_risk": True,
            "demographic_profile": demographic
        }

        snapshot = backend.create_decision_snapshot(
            function_name="mortgage_underwriting_decision",
            inputs=app_data,
            outputs=result,
            metadata=regulatory_metadata
        )

        stored_id = db_backend.save_decision(snapshot)
        january_decisions.append((stored_id, demographic, result["decision"]))
        print(f"  SUCCESS: Stored: {stored_id[:12]}...")

    print("\n" + "="*75)
    print("AUGUST APPLICATIONS (Model v2.0 - Mid-Year Change)")
    print("="*75)

    # Create August applications with model v2.0
    august_decisions = []
    august_applications = [
        ("white", 1),  # 1 month ago (August)
        ("white", 1),
        ("black", 1),
        ("black", 1),
        ("hispanic", 1)
    ]

    for demographic, months_ago in august_applications:
        app_data = create_hmda_application(demographic, months_ago)

        # Add updated model version and feature config
        app_data["model_version"] = "mortgage-model-v2.0"
        app_data["feature_config_hash"] = "sha256:xyz789ghi012"

        print(f"\nProcessing {demographic} applicant application (Model v2.0):")
        print(f"  Application ID: {app_data['application_id'][:12]}...")
        print(f"  Income: ${app_data['applicant_income']:,.0f}")
        print(f"  Loan Amount: ${app_data['loan_amount']:,.0f}")

        # Run model v2.0
        result = simulate_mortgage_underwriting_model(app_data, "mortgage-model-v2.0")
        print(f"  Decision: {result['decision']}")

        # Create decision snapshot
        regulatory_metadata = {
            "regulation": "ECOA/HMDA/Reg B",
            "disparate_impact_monitoring": True,
            "full_cohort_replay_available": True,
            "doj_referral_risk": True,
            "demographic_profile": demographic
        }

        snapshot = backend.create_decision_snapshot(
            function_name="mortgage_underwriting_decision",
            inputs=app_data,
            outputs=result,
            metadata=regulatory_metadata
        )

        stored_id = db_backend.save_decision(snapshot)
        august_decisions.append((stored_id, demographic, result["decision"]))
        print(f"  SUCCESS: Stored: {stored_id[:12]}...")

    # Demonstrate DOJ/CFPB examiner query
    print("\n" + "="*75)
    print("DOJ/CFPB EXAMINER SIMULATION")
    print("="*75)

    examiner_query = "Provide all denial decisions for Black applicants between January and August of this year, and confirm which model version was active for each."
    print(f"EXAMINER QUERY: {examiner_query}")
    print()

    print("BLACK APPLICANT DECISIONS:")
    print("=" * 50)

    # Filter and display Black applicant decisions
    all_decisions = january_decisions + august_decisions
    black_applicant_decisions = [(decision_id, demo, decision) for decision_id, demo, decision in all_decisions if demo == "black"]

    for decision_id, demographic, decision in black_applicant_decisions:
        retrieved_decision = db_backend.load_decision(decision_id)
        if retrieved_decision:
            model_version = None
            application_date = None

            # Extract model version and date
            for inp in retrieved_decision.inputs:
                if inp.name == "model_version":
                    model_version = inp.value
                elif inp.name == "application_timestamp":
                    application_date = inp.value

            print(f"Decision ID: {decision_id}")
            print(f"  Demographics: {demographic.title()} applicant")
            print(f"  Decision: {decision}")
            print(f"  Model Version: {model_version}")
            print(f"  Application Date: {application_date[:10] if application_date else 'N/A'}")
            print()

    # Demonstrate side-by-side model version comparison
    print("="*75)
    print("MODEL VERSION COMPARISON ANALYSIS")
    print("="*75)

    # Analyze approval rates by demographics and model version
    january_stats = {"white": [], "black": [], "hispanic": []}
    august_stats = {"white": [], "black": [], "hispanic": []}

    # Collect January stats
    for decision_id, demographic, decision in january_decisions:
        january_stats[demographic].append(decision)

    # Collect August stats
    for decision_id, demographic, decision in august_decisions:
        august_stats[demographic].append(decision)

    print("APPROVAL RATE ANALYSIS:")
    print("-" * 40)
    for demo in ["white", "black", "hispanic"]:
        jan_approvals = sum(1 for d in january_stats[demo] if d == "approve")
        jan_total = len(january_stats[demo])
        jan_rate = jan_approvals / jan_total if jan_total > 0 else 0

        aug_approvals = sum(1 for d in august_stats[demo] if d == "approve")
        aug_total = len(august_stats[demo])
        aug_rate = aug_approvals / aug_total if aug_total > 0 else 0

        print(f"{demo.title()} Applicants:")
        print(f"  January (v1.0): {jan_approvals}/{jan_total} = {jan_rate:.1%}")
        print(f"  August (v2.0):  {aug_approvals}/{aug_total} = {aug_rate:.1%}")
        print(f"  Change: {aug_rate - jan_rate:+.1%}")
        print()

    # Regulatory compliance validation
    print("="*75)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*75)

    # Check one representative decision for completeness
    sample_decision = db_backend.load_decision(january_decisions[0][0])

    required_hmda_fields = [
        "regulation",
        "disparate_impact_monitoring",
        "full_cohort_replay_available",
        "doj_referral_risk"
    ]

    validation_result = backend.validate_regulatory_completeness(
        sample_decision,
        required_hmda_fields
    )

    print(f"HMDA Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Fields: {', '.join(validation_result['missing_fields'])}")

    # Summary of key capabilities
    print("="*75)
    print("BRIEFCASE AI VALUE FOR FAIR LENDING")
    print("="*75)
    print("SUCCESS: Complete model version history across demographic cohorts")
    print("SUCCESS: Immutable audit trail for disparate impact investigation")
    print("SUCCESS: Full historical replay capability for any date range")
    print("SUCCESS: DOJ/CFPB examination readiness")
    print("SUCCESS: Model change impact analysis")

    print(f"\nSUCCESS: Mortgage fair lending audit trail demonstration completed")
    print(f"Total decisions stored: {len(all_decisions)}")
    print("Model versions tracked: v1.0 (January), v2.0 (August)")


if __name__ == "__main__":
    main()