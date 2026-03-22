#!/usr/bin/env python3
"""
Briefcase AI Example: Neobank / BaaS Sponsor Bank Layer

Context: OCC/Federal Reserve examination. Neobank makes AI decisions (account opening,
fraud, credit) under the sponsor bank's charter. Bank carries exam liability for
neobank AI decisions it did not directly make. Bank must produce audit evidence
without neobank cooperation.

Demonstrates:
- Multi-neobank partner decision tracking under single sponsor charter
- Sponsor bank audit trail independence from neobank systems
- OCC examination readiness without neobank cooperation
- Charter liability documentation and defense
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
    from backend import briefcase, DecisionSnapshot, Input, Output, SqliteBackend
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please check the shared backend module is available")
    sys.exit(1)


def simulate_neobank_ai_decision(application_data: Dict[str, Any], neobank_config: Dict[str, str]) -> Dict[str, Any]:
    """
    Simulates an AI decision made by a neobank partner under the sponsor bank's charter.
    In production, this would be received from the neobank's AI systems via API.

    Args:
        application_data: Account application data from neobank customer
        neobank_config: Configuration for the specific neobank partner

    Returns:
        Dictionary containing neobank AI decision and supporting data
    """
    neobank_id = neobank_config["neobank_id"]
    model_version = neobank_config["neobank_model_version"]

    # Simulate neobank-specific AI model behavior
    income = application_data.get("annual_income", 0)
    age = application_data.get("customer_age", 25)
    state = application_data.get("customer_state", "CA")

    # Base scoring
    risk_score = 0.5

    # Income-based adjustments
    if income >= 75000:
        risk_score += 0.3
    elif income >= 50000:
        risk_score += 0.15
    elif income >= 30000:
        risk_score += 0.05
    else:
        risk_score -= 0.2

    # Age-based adjustments
    if age >= 25 and age <= 45:
        risk_score += 0.1
    elif age < 21:
        risk_score -= 0.1

    # Neobank-specific model variations
    if neobank_id == "neobank-partner-alpha":
        # Alpha is focused on young professionals
        if age <= 35 and income >= 60000:
            risk_score += 0.2
        risk_score *= 1.05  # Slightly more aggressive
    elif neobank_id == "neobank-partner-beta":
        # Beta focuses on broader demographics
        if state in ["CA", "NY", "TX"]:
            risk_score += 0.1
        risk_score *= 0.95  # Slightly more conservative
    elif neobank_id == "neobank-partner-gamma":
        # Gamma has strict requirements
        if income < 40000:
            risk_score -= 0.3
        risk_score *= 0.90  # More conservative

    # Add model uncertainty
    risk_score += random.uniform(-0.1, 0.1)
    risk_score = max(0.0, min(1.0, risk_score))

    # Decision thresholds (vary by neobank)
    approval_threshold = neobank_config.get("approval_threshold", 0.6)

    if risk_score >= approval_threshold:
        decision = "approve"
    elif risk_score >= 0.4:
        decision = "manual_review"
    else:
        decision = "decline"

    # Generate neobank-specific KYC and fraud scores
    kyc_score = min(1.0, risk_score + random.uniform(0.0, 0.2))
    fraud_score = max(0.0, 1.0 - risk_score + random.uniform(-0.1, 0.1))
    credit_score = int(300 + (risk_score * 500) + random.uniform(-50, 50))

    return {
        "neobank_decision": decision,
        "neobank_kyc_score": round(kyc_score, 3),
        "neobank_fraud_score": round(fraud_score, 3),
        "neobank_credit_score": credit_score,
        "decision_timestamp": datetime.utcnow().isoformat(),
        "neobank_model_version": model_version,
        "bank_audit_record_id": str(uuid.uuid4()),
        "sponsor_bank_id": "SPONSOR_BANK_001",
        "exam_ready_flag": True
    }


def create_neobank_application(neobank_id: str, customer_profile: str) -> Dict[str, Any]:
    """
    Creates a simulated neobank customer application.

    Args:
        neobank_id: Which neobank partner this application came from
        customer_profile: Type of customer profile to simulate

    Returns:
        Dictionary containing application data
    """
    application_id = str(uuid.uuid4())

    if customer_profile == "young_professional":
        customer_data = {
            "account_application_id": application_id,
            "neobank_id": neobank_id,
            "customer_age": random.randint(25, 35),
            "annual_income": random.uniform(60000, 120000),
            "customer_state": random.choice(["CA", "NY", "TX", "FL"]),
            "employment_status": "employed",
            "account_type": "checking",
            "initial_deposit": random.uniform(500, 5000)
        }
    elif customer_profile == "student":
        customer_data = {
            "account_application_id": application_id,
            "neobank_id": neobank_id,
            "customer_age": random.randint(18, 24),
            "annual_income": random.uniform(15000, 35000),
            "customer_state": random.choice(["CA", "NY", "MA", "IL"]),
            "employment_status": "student",
            "account_type": "student_checking",
            "initial_deposit": random.uniform(50, 1000)
        }
    elif customer_profile == "gig_worker":
        customer_data = {
            "account_application_id": application_id,
            "neobank_id": neobank_id,
            "customer_age": random.randint(25, 45),
            "annual_income": random.uniform(25000, 55000),
            "customer_state": random.choice(["CA", "TX", "FL", "AZ"]),
            "employment_status": "gig_worker",
            "account_type": "gig_checking",
            "initial_deposit": random.uniform(100, 2000)
        }
    else:
        # Default profile
        customer_data = {
            "account_application_id": application_id,
            "neobank_id": neobank_id,
            "customer_age": random.randint(21, 65),
            "annual_income": random.uniform(30000, 80000),
            "customer_state": random.choice(["CA", "NY", "TX", "FL", "IL"]),
            "employment_status": "employed",
            "account_type": "checking",
            "initial_deposit": random.uniform(250, 3000)
        }

    return customer_data


def main():
    """
    Main execution function demonstrating neobank BaaS sponsor bank workflow.
    """
    print("=== Briefcase AI Neobank / BaaS Sponsor Bank Example ===")
    print("Regulation: OCC Third-Party Risk Management Guidance / Federal Reserve SR 11-7")
    print("Workflow: Multi-neobank charter liability tracking with sponsor bank audit trail\n")

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

    # Configure multiple neobank partners
    neobank_partners = {
        "neobank-partner-alpha": {
            "neobank_id": "neobank-partner-alpha",
            "neobank_name": "FinTech Alpha",
            "neobank_model_version": "alpha-underwriting-v2.1.4",
            "approval_threshold": 0.65,
            "target_demographic": "young_professionals"
        },
        "neobank-partner-beta": {
            "neobank_id": "neobank-partner-beta",
            "neobank_name": "Digital Beta Bank",
            "neobank_model_version": "beta-ai-v3.0.2",
            "approval_threshold": 0.60,
            "target_demographic": "broad_market"
        },
        "neobank-partner-gamma": {
            "neobank_id": "neobank-partner-gamma",
            "neobank_name": "Secure Banking Co",
            "neobank_model_version": "gamma-conservative-v1.8.1",
            "approval_threshold": 0.70,
            "target_demographic": "risk_averse"
        }
    }

    print("Configured neobank partners under sponsor charter:")
    for partner_id, config in neobank_partners.items():
        print(f"  - {config['neobank_name']} ({partner_id})")
        print(f"    Model: {config['neobank_model_version']}")
        print(f"    Target: {config['target_demographic']}")
    print()

    # Process applications from multiple neobank partners
    all_decisions = []

    print("="*80)
    print("PROCESSING APPLICATIONS FROM MULTIPLE NEOBANK PARTNERS")
    print("="*80)

    # Alpha neobank applications
    print(f"\n--- {neobank_partners['neobank-partner-alpha']['neobank_name']} Applications ---")

    for i in range(2):
        # Create application
        app_data = create_neobank_application("neobank-partner-alpha", "young_professional")

        print(f"\nApplication {i+1} from Alpha:")
        print(f"  Application ID: {app_data['account_application_id'][:12]}...")
        print(f"  Customer Age: {app_data['customer_age']}")
        print(f"  Annual Income: ${app_data['annual_income']:,.0f}")
        print(f"  State: {app_data['customer_state']}")

        # Process with Alpha's AI model
        alpha_config = neobank_partners["neobank-partner-alpha"]
        alpha_decision = simulate_neobank_ai_decision(app_data, alpha_config)

        print(f"  SUCCESS: Alpha AI Decision: {alpha_decision['neobank_decision']}")
        print(f"  SUCCESS: KYC Score: {alpha_decision['neobank_kyc_score']}")

        # Create sponsor bank audit record
        regulatory_metadata = {
            "regulation": "OCC Third-Party Risk Management Guidance / Federal Reserve SR 11-7",
            "bank_carries_charter_liability": True,
            "neobank_cooperation_required": False,
            "sponsor_bank_controlled": True,
            "neobank_partner": alpha_config["neobank_name"],
            "partner_id": alpha_config["neobank_id"]
        }

        snapshot = backend.create_decision_snapshot(
            function_name="neobank_account_opening_decision",
            inputs=app_data,
            outputs=alpha_decision,
            metadata=regulatory_metadata
        )

        stored_id = db_backend.save_decision(snapshot)
        all_decisions.append((stored_id, "alpha", alpha_decision["neobank_decision"]))
        print(f"  SUCCESS: Sponsor bank audit record: {stored_id[:12]}...")

    # Beta neobank applications
    print(f"\n--- {neobank_partners['neobank-partner-beta']['neobank_name']} Applications ---")

    for i in range(2):
        # Create application
        app_data = create_neobank_application("neobank-partner-beta", "gig_worker")

        print(f"\nApplication {i+1} from Beta:")
        print(f"  Application ID: {app_data['account_application_id'][:12]}...")
        print(f"  Customer Age: {app_data['customer_age']}")
        print(f"  Annual Income: ${app_data['annual_income']:,.0f}")
        print(f"  Employment: {app_data['employment_status']}")

        # Process with Beta's AI model
        beta_config = neobank_partners["neobank-partner-beta"]
        beta_decision = simulate_neobank_ai_decision(app_data, beta_config)

        print(f"  SUCCESS: Beta AI Decision: {beta_decision['neobank_decision']}")
        print(f"  SUCCESS: Fraud Score: {beta_decision['neobank_fraud_score']}")

        # Create sponsor bank audit record
        regulatory_metadata = {
            "regulation": "OCC Third-Party Risk Management Guidance / Federal Reserve SR 11-7",
            "bank_carries_charter_liability": True,
            "neobank_cooperation_required": False,
            "sponsor_bank_controlled": True,
            "neobank_partner": beta_config["neobank_name"],
            "partner_id": beta_config["neobank_id"]
        }

        snapshot = backend.create_decision_snapshot(
            function_name="neobank_account_opening_decision",
            inputs=app_data,
            outputs=beta_decision,
            metadata=regulatory_metadata
        )

        stored_id = db_backend.save_decision(snapshot)
        all_decisions.append((stored_id, "beta", beta_decision["neobank_decision"]))
        print(f"  SUCCESS: Sponsor bank audit record: {stored_id[:12]}...")

    # Gamma neobank application
    print(f"\n--- {neobank_partners['neobank-partner-gamma']['neobank_name']} Applications ---")

    app_data = create_neobank_application("neobank-partner-gamma", "student")

    print(f"\nApplication from Gamma:")
    print(f"  Application ID: {app_data['account_application_id'][:12]}...")
    print(f"  Customer Age: {app_data['customer_age']}")
    print(f"  Annual Income: ${app_data['annual_income']:,.0f}")
    print(f"  Account Type: {app_data['account_type']}")

    # Process with Gamma's AI model
    gamma_config = neobank_partners["neobank-partner-gamma"]
    gamma_decision = simulate_neobank_ai_decision(app_data, gamma_config)

    print(f"  SUCCESS: Gamma AI Decision: {gamma_decision['neobank_decision']}")
    print(f"  SUCCESS: Credit Score: {gamma_decision['neobank_credit_score']}")

    # Create sponsor bank audit record
    regulatory_metadata = {
        "regulation": "OCC Third-Party Risk Management Guidance / Federal Reserve SR 11-7",
        "bank_carries_charter_liability": True,
        "neobank_cooperation_required": False,
        "sponsor_bank_controlled": True,
        "neobank_partner": gamma_config["neobank_name"],
        "partner_id": gamma_config["neobank_id"]
    }

    snapshot = backend.create_decision_snapshot(
        function_name="neobank_account_opening_decision",
        inputs=app_data,
        outputs=gamma_decision,
        metadata=regulatory_metadata
    )

    stored_id = db_backend.save_decision(snapshot)
    all_decisions.append((stored_id, "gamma", gamma_decision["neobank_decision"]))
    print(f"  ✓ Sponsor bank audit record: {stored_id[:12]}...")

    # Demonstrate OCC examiner query
    print("\n" + "="*80)
    print("OCC EXAMINER SIMULATION")
    print("="*80)

    examiner_query = "Provide audit evidence for all AI-driven account opening decisions made under your charter in the past 30 days across all neobank partners."
    print(f"EXAMINER QUERY: {examiner_query}")
    print()

    print("SPONSOR BANK AUDIT RESPONSE:")
    print("-" * 60)

    for i, (decision_id, partner, decision) in enumerate(all_decisions):
        retrieved = db_backend.load_decision(decision_id)
        if retrieved:
            partner_name = retrieved.tags.get("neobank_partner", "Unknown")
            partner_id = retrieved.tags.get("partner_id", "Unknown")

            application_id = None
            model_version = None

            for inp in retrieved.inputs:
                if inp.name == "account_application_id":
                    application_id = inp.value[:12] + "..."

            for out in retrieved.outputs:
                if out.name == "neobank_model_version":
                    model_version = out.value

            print(f"Record {i+1}: {decision_id}")
            print(f"  Neobank Partner: {partner_name} ({partner_id})")
            print(f"  Application ID: {application_id}")
            print(f"  Decision: {decision}")
            print(f"  Model Version: {model_version}")
            print(f"  Audit Timestamp: {getattr(retrieved, 'created_at', 'N/A')}")
            print()

    # Demonstrate charter liability analysis
    print("="*80)
    print("CHARTER LIABILITY ANALYSIS")
    print("="*80)

    # Count decisions by partner and outcome
    decision_stats = {}
    for decision_id, partner, decision in all_decisions:
        if partner not in decision_stats:
            decision_stats[partner] = {"approve": 0, "decline": 0, "manual_review": 0, "total": 0}
        decision_stats[partner][decision] += 1
        decision_stats[partner]["total"] += 1

    print("CHARTER LIABILITY SUMMARY:")
    print("-" * 40)
    total_decisions = len(all_decisions)
    print(f"Total decisions under charter: {total_decisions}")

    for partner, stats in decision_stats.items():
        partner_name = None
        for p_id, config in neobank_partners.items():
            if partner in p_id:
                partner_name = config["neobank_name"]
                break

        if partner_name:
            approval_rate = (stats["approve"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            print(f"\n{partner_name}:")
            print(f"  Total: {stats['total']}")
            print(f"  Approved: {stats['approve']} ({approval_rate:.1f}%)")
            print(f"  Manual Review: {stats['manual_review']}")
            print(f"  Declined: {stats['decline']}")

    # Demonstrate sponsor bank independence
    print("\n" + "="*80)
    print("SPONSOR BANK INDEPENDENCE DEMONSTRATION")
    print("="*80)

    print("SCENARIO: All neobank partners systems are unavailable")
    print("SPONSOR BANK CAPABILITY: Complete audit trail still accessible\n")

    # Retrieve one decision to show independence
    sample_decision = db_backend.load_decision(all_decisions[0][0])
    if sample_decision:
        print("SUCCESS: Sample audit record retrieved without neobank cooperation:")
        print(f"  Decision ID: {all_decisions[0][0]}")
        print(f"  Partner: {sample_decision.tags.get('neobank_partner', 'N/A')}")
        print(f"  Charter Liability: {sample_decision.tags.get('bank_carries_charter_liability', False)}")
        print(f"  Sponsor Bank Controlled: {sample_decision.tags.get('sponsor_bank_controlled', False)}")

    # Regulatory validation
    print("\n" + "="*80)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*80)

    sample_decision = db_backend.load_decision(all_decisions[0][0])

    required_sponsor_fields = [
        "regulation",
        "bank_carries_charter_liability",
        "neobank_cooperation_required",
        "sponsor_bank_controlled"
    ]

    validation_result = backend.validate_regulatory_completeness(
        sample_decision,
        required_sponsor_fields
    )

    print(f"Sponsor Bank Compliance: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Fields: {', '.join(validation_result['missing_fields'])}")

    # Summary of capabilities
    print("\n" + "="*80)
    print("BRIEFCASE AI VALUE FOR SPONSOR BANKS")
    print("="*80)
    print("SUCCESS: Multi-neobank partner audit trail consolidation")
    print("SUCCESS: Charter liability documentation and defense")
    print("SUCCESS: OCC examination readiness without neobank cooperation")
    print("SUCCESS: Third-party risk management compliance")
    print("SUCCESS: Model version tracking across all partner AI systems")
    print("SUCCESS: Business continuity during neobank partner changes")

    print(f"\nSUCCESS: Neobank BaaS sponsor bank audit trail demonstration completed")
    print(f"Total decisions under charter: {len(all_decisions)}")
    print(f"Neobank partners tracked: {len(neobank_partners)}")
    print(f"All decisions retrievable without neobank cooperation: SUCCESS")


if __name__ == "__main__":
    main()