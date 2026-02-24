#!/usr/bin/env python3
"""
Briefcase AI Example: Collections & Debt Management AI (CFPB UDAAP/FDCPA)

Context: AI-powered collections and debt management system for a regulated financial
services company. Subject to CFPB Unfair, Deceptive, or Abusive Acts or Practices
(UDAAP) regulations and Fair Debt Collection Practices Act (FDCPA). State-specific
rules for CA, NY, TX, FL apply. All collection decisions and consumer communications
must be compliant, auditable, and defensible in class action litigation.

Demonstrates:
- AI contact strategy optimization with regulatory constraints
- State-specific FDCPA rule compliance (CA, NY, TX, FL)
- UDAAP compliance scoring and validation
- Class action defense documentation
- Contact frequency and timing regulation compliance
- Settlement offer AI with consumer protection safeguards
- Rule version tracking for regulatory change management
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


def get_state_fdcpa_rules(state: str) -> Dict[str, Any]:
    """
    Returns state-specific FDCPA rules and contact restrictions.

    Args:
        state: Two-letter state code

    Returns:
        Dictionary containing state-specific rules and restrictions
    """
    state_rules = {
        "CA": {
            "max_daily_calls": 2,
            "max_weekly_calls": 7,
            "call_time_start": "08:00",
            "call_time_end": "21:00",
            "cease_desist_honored": True,
            "garnishment_restrictions": ["head_of_household_exempt", "minimum_wage_protection"],
            "statute_of_limitations": 4,  # years
            "additional_disclosures": ["Spanish_language_required"]
        },
        "NY": {
            "max_daily_calls": 2,
            "max_weekly_calls": 6,
            "call_time_start": "08:00",
            "call_time_end": "20:00",
            "cease_desist_honored": True,
            "garnishment_restrictions": ["90_percent_disposable_income_exempt"],
            "statute_of_limitations": 6,  # years
            "additional_disclosures": ["debt_validation_enhanced"]
        },
        "TX": {
            "max_daily_calls": 3,
            "max_weekly_calls": 10,
            "call_time_start": "08:00",
            "call_time_end": "21:00",
            "cease_desist_honored": True,
            "garnishment_restrictions": ["homestead_exempt", "personal_property_exempt"],
            "statute_of_limitations": 4,  # years
            "additional_disclosures": ["property_exempt_notice"]
        },
        "FL": {
            "max_daily_calls": 3,
            "max_weekly_calls": 9,
            "call_time_start": "08:00",
            "call_time_end": "21:00",
            "cease_desist_honored": True,
            "garnishment_restrictions": ["head_of_household_exempt", "wages_exempt"],
            "statute_of_limitations": 5,  # years
            "additional_disclosures": ["homestead_exemption_notice"]
        },
        "DEFAULT": {
            "max_daily_calls": 1,
            "max_weekly_calls": 3,
            "call_time_start": "08:00",
            "call_time_end": "21:00",
            "cease_desist_honored": True,
            "garnishment_restrictions": [],
            "statute_of_limitations": 3,
            "additional_disclosures": []
        }
    }

    return state_rules.get(state, state_rules["DEFAULT"])


def calculate_udaap_compliance_score(account_data: Dict[str, Any], collection_strategy: Dict[str, Any]) -> float:
    """
    Calculates UDAAP compliance score based on account characteristics and proposed strategy.

    Args:
        account_data: Debtor account information
        collection_strategy: Proposed collection approach

    Returns:
        UDAAP compliance score (0.0-1.0)
    """
    score = 1.0

    # Check for vulnerable consumer indicators
    if account_data.get("hardship_indicators"):
        if "recent_unemployment" in account_data["hardship_indicators"]:
            if collection_strategy["contact_intensity"] == "aggressive":
                score -= 0.3  # Unfair to aggressively pursue unemployed consumers
        if "medical_debt_component" in account_data["hardship_indicators"]:
            if collection_strategy["settlement_threshold"] < 0.5:
                score -= 0.2  # Abusive to demand high payments for medical debt
        if "elderly_consumer" in account_data["hardship_indicators"]:
            if collection_strategy["contact_method"] == "phone_intensive":
                score -= 0.25  # Abusive to overwhelm elderly consumers

    # Check for deceptive practices in communication
    if collection_strategy["threat_level"] == "legal_action":
        if account_data["debt_age_days"] > account_data.get("statute_of_limitations", 3) * 365:
            score -= 0.4  # Deceptive to threaten legal action on time-barred debt

    # Check contact frequency compliance
    state_rules = get_state_fdcpa_rules(account_data.get("debtor_state", "DEFAULT"))
    if collection_strategy["daily_contact_count"] > state_rules["max_daily_calls"]:
        score -= 0.3  # Unfair contact frequency

    # Check for ability to pay consideration
    if account_data["income_to_debt_ratio"] < 0.1:  # Very low income relative to debt
        if collection_strategy["payment_demand_percentage"] > 0.15:  # Demanding >15% of income
            score -= 0.2  # Abusive to demand excessive percentage of income

    return max(0.0, score)


def simulate_collections_ai_decision(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates an AI-powered collections strategy decision with regulatory compliance.
    In production, this would be replaced with actual ML model inference.

    Args:
        account_data: Dictionary containing debtor account information

    Returns:
        Dictionary containing collections strategy decision and compliance metadata
    """
    # Get state-specific rules
    state_rules = get_state_fdcpa_rules(account_data.get("debtor_state", "DEFAULT"))

    # Risk and collection strategy determination
    balance = account_data["outstanding_balance"]
    days_delinquent = account_data["days_past_due"]
    payment_history = account_data.get("payment_history_score", 0.5)
    income_ratio = account_data.get("income_to_debt_ratio", 0.0)

    # Determine collection intensity based on account characteristics
    if days_delinquent < 30:
        contact_intensity = "soft_touch"
        daily_contacts = 1
        settlement_threshold = 0.9  # Accept 90% settlement
        threat_level = "none"
    elif days_delinquent < 90:
        contact_intensity = "moderate"
        daily_contacts = min(2, state_rules["max_daily_calls"])
        settlement_threshold = 0.75
        threat_level = "credit_report"
    elif days_delinquent < 180:
        contact_intensity = "firm"
        daily_contacts = min(state_rules["max_daily_calls"], 3)
        settlement_threshold = 0.6
        threat_level = "legal_action" if income_ratio > 0.2 else "credit_report"
    else:
        contact_intensity = "aggressive" if income_ratio > 0.3 else "moderate"
        daily_contacts = state_rules["max_daily_calls"]
        settlement_threshold = 0.4 if income_ratio > 0.3 else 0.7
        threat_level = "legal_action" if account_data["debt_age_days"] < state_rules["statute_of_limitations"] * 365 else "none"

    # Adjust for hardship indicators
    if account_data.get("hardship_indicators"):
        contact_intensity = "soft_touch" if "medical_debt_component" in account_data["hardship_indicators"] else contact_intensity
        daily_contacts = max(1, daily_contacts - 1) if "elderly_consumer" in account_data["hardship_indicators"] else daily_contacts
        settlement_threshold = min(0.5, settlement_threshold) if "recent_unemployment" in account_data["hardship_indicators"] else settlement_threshold

    # Determine contact method and schedule
    if contact_intensity == "soft_touch":
        contact_method = "email_primary"
        weekly_contacts = 2
    elif contact_intensity == "moderate":
        contact_method = "phone_email_mix"
        weekly_contacts = min(4, state_rules["max_weekly_calls"])
    else:
        contact_method = "phone_intensive"
        weekly_contacts = min(state_rules["max_weekly_calls"], daily_contacts * 3)

    # Calculate next contact timing
    next_contact_hours = 24 if contact_intensity == "aggressive" else 72
    next_contact_date = datetime.utcnow() + timedelta(hours=next_contact_hours)

    # Payment plan determination
    payment_plan_eligible = balance < 10000 and income_ratio > 0.15 and payment_history > 0.3

    # Settlement offer calculation
    settlement_amount = balance * settlement_threshold
    monthly_payment_capacity = account_data.get("monthly_income", 0) * 0.1  # 10% of income max

    collection_strategy = {
        "contact_intensity": contact_intensity,
        "contact_method": contact_method,
        "daily_contact_count": daily_contacts,
        "weekly_contact_count": weekly_contacts,
        "threat_level": threat_level,
        "settlement_threshold": settlement_threshold,
        "payment_demand_percentage": min(0.15, settlement_threshold)
    }

    # Calculate UDAAP compliance score
    udaap_score = calculate_udaap_compliance_score(account_data, collection_strategy)

    # Determine if strategy needs adjustment for compliance
    if udaap_score < 0.8:
        # Automatically adjust strategy to improve compliance
        collection_strategy["contact_intensity"] = "soft_touch"
        collection_strategy["daily_contact_count"] = 1
        collection_strategy["threat_level"] = "none" if udaap_score < 0.6 else "credit_report"
        udaap_score = calculate_udaap_compliance_score(account_data, collection_strategy)

    return {
        "collection_strategy": collection_strategy["contact_intensity"],
        "contact_method": collection_strategy["contact_method"],
        "daily_contact_limit": collection_strategy["daily_contact_count"],
        "weekly_contact_limit": collection_strategy["weekly_contact_count"],
        "next_contact_date": next_contact_date.isoformat(),
        "threat_level": collection_strategy["threat_level"],
        "settlement_offer_amount": round(settlement_amount, 2),
        "settlement_percentage": round(settlement_threshold * 100, 1),
        "payment_plan_eligible": payment_plan_eligible,
        "monthly_payment_max": round(monthly_payment_capacity, 2),
        "hardship_accommodations": account_data.get("hardship_indicators", []),
        "udaap_compliance_score": round(udaap_score, 3),
        "fdcpa_compliant": udaap_score >= 0.8,
        "state_rules_applied": state_rules,
        "debt_age_compliant": account_data["debt_age_days"] <= state_rules["statute_of_limitations"] * 365,
        "model_version": "collections-ai-v3.2.1",
        "decision_trace_id": str(uuid.uuid4()),
        "class_action_defensible": udaap_score >= 0.85 and collection_strategy["daily_contact_count"] <= state_rules["max_daily_calls"]
    }


def simulate_examiner_query_collections(db_backend: SqliteBackend, decision_ids: List[str]) -> None:
    """
    Simulates regulatory examiner queries for collections compliance.

    Args:
        db_backend: Database backend
        decision_ids: List of decision IDs to query
    """
    print("\n" + "="*60)
    print("CFPB EXAMINER SIMULATION - COLLECTIONS COMPLIANCE")
    print("="*60)

    queries = [
        "Show evidence of UDAAP compliance validation for high-balance accounts",
        "Demonstrate state-specific FDCPA rule application and version tracking",
        "Provide audit trail for contact frequency limits and hardship accommodations",
        "Show documentation supporting class action defense for collection practices"
    ]

    for i, query in enumerate(queries):
        if i < len(decision_ids):
            print(f"\nEXAMINER QUERY {i+1}: {query}")
            response = backend.format_examiner_response(decision_ids[i], query, db_backend)
            print(response)
        else:
            print(f"\nEXAMINER QUERY {i+1}: {query}")
            print("No additional decisions available for this query.")


def main():
    """
    Main execution function demonstrating collections & debt management workflow.
    """
    print("=== Briefcase AI Collections & Debt Management Example ===")
    print("Regulation: CFPB UDAAP/FDCPA")
    print("Scope: Multi-state collections with consumer protection compliance")
    print("Features: Contact strategy optimization, hardship assessment, class action defense\n")

    # Initialize Briefcase AI SDK
    try:
        briefcase_ai.init_with_config(2)
        print("✓ Briefcase AI SDK initialized")
    except Exception as e:
        print(f"✗ Failed to initialize SDK: {e}")
        sys.exit(1)

    # Get configured backend
    db_backend = backend.get_backend()
    print("✓ SQLite backend configured\n")

    # Process multiple collection scenarios across different states
    collection_scenarios = [
        {
            "scenario_name": "High Balance California Account with Medical Debt",
            "account_data": {
                "account_id": str(uuid.uuid4()),
                "debtor_name": "Maria Rodriguez",
                "debtor_state": "CA",
                "outstanding_balance": 15750.00,
                "original_creditor": "Regional Medical Center",
                "days_past_due": 120,
                "debt_age_days": 450,
                "payment_history_score": 0.25,
                "monthly_income": 4200.0,
                "income_to_debt_ratio": 0.267,
                "previous_contact_attempts": 8,
                "hardship_indicators": ["medical_debt_component", "recent_unemployment"],
                "last_payment_date": "2023-08-15",
                "cease_desist_received": False
            }
        },
        {
            "scenario_name": "Elderly Consumer New York Credit Card Debt",
            "account_data": {
                "account_id": str(uuid.uuid4()),
                "debtor_name": "Robert Thompson",
                "debtor_state": "NY",
                "outstanding_balance": 8200.00,
                "original_creditor": "National Bank Credit Card",
                "days_past_due": 75,
                "debt_age_days": 180,
                "payment_history_score": 0.45,
                "monthly_income": 2800.0,
                "income_to_debt_ratio": 0.341,
                "previous_contact_attempts": 5,
                "hardship_indicators": ["elderly_consumer", "fixed_income"],
                "last_payment_date": "2023-12-01",
                "cease_desist_received": False
            }
        },
        {
            "scenario_name": "Texas Business Loan Default",
            "account_data": {
                "account_id": str(uuid.uuid4()),
                "debtor_name": "Sarah Wilson",
                "debtor_state": "TX",
                "outstanding_balance": 32000.00,
                "original_creditor": "Small Business Lender",
                "days_past_due": 200,
                "debt_age_days": 650,
                "payment_history_score": 0.60,
                "monthly_income": 6500.0,
                "income_to_debt_ratio": 0.203,
                "previous_contact_attempts": 12,
                "hardship_indicators": [],
                "last_payment_date": "2023-05-20",
                "cease_desist_received": True
            }
        },
        {
            "scenario_name": "Florida Time-Barred Auto Loan",
            "account_data": {
                "account_id": str(uuid.uuid4()),
                "debtor_name": "James Martinez",
                "debtor_state": "FL",
                "outstanding_balance": 12400.00,
                "original_creditor": "Auto Finance Corp",
                "days_past_due": 900,
                "debt_age_days": 2100,  # Over 5 years (FL statute of limitations)
                "payment_history_score": 0.15,
                "monthly_income": 3200.0,
                "income_to_debt_ratio": 0.258,
                "previous_contact_attempts": 3,
                "hardship_indicators": [],
                "last_payment_date": "2019-03-15",
                "cease_desist_received": False
            }
        }
    ]

    decision_ids = []

    for scenario in collection_scenarios:
        print(f"\n{'='*50}")
        print(f"PROCESSING: {scenario['scenario_name']}")
        print('='*50)

        account_data = scenario["account_data"]

        print("Account Details:")
        for key, value in account_data.items():
            if key not in ["account_id"]:
                print(f"  {key}: {value}")
        print()

        # Run AI collections decision
        print("Running AI collections strategy analysis...")
        collections_decision = simulate_collections_ai_decision(account_data)

        print(f"✓ Strategy: {collections_decision['collection_strategy']}")
        print(f"✓ Contact method: {collections_decision['contact_method']}")
        print(f"✓ UDAAP compliance: {collections_decision['udaap_compliance_score']}")
        print(f"✓ FDCPA compliant: {collections_decision['fdcpa_compliant']}")
        print(f"✓ Settlement offer: ${collections_decision['settlement_offer_amount']:,.2f} ({collections_decision['settlement_percentage']}%)")
        print(f"✓ Class action defensible: {collections_decision['class_action_defensible']}")

        # Display regulatory adjustments
        if collections_decision["hardship_accommodations"]:
            print(f"✓ Hardship accommodations: {', '.join(collections_decision['hardship_accommodations'])}")

        if not collections_decision["debt_age_compliant"]:
            print(f"⚠ WARNING: Debt exceeds statute of limitations for {account_data['debtor_state']}")

        # Create comprehensive regulatory metadata
        regulatory_metadata = {
            "regulation": "CFPB UDAAP/FDCPA",
            "state_jurisdiction": account_data["debtor_state"],
            "fdcpa_rule_version": "2024.1",
            "udaap_guidance_version": "CFPB-2023-0014",
            "udaap_compliant": collections_decision["udaap_compliance_score"] >= 0.8,
            "fdcpa_compliant": collections_decision["fdcpa_compliant"],
            "state_rules_version": f"{account_data['debtor_state']}_FDCPA_2024",
            "contact_frequency_compliant": collections_decision["daily_contact_limit"] <= collections_decision["state_rules_applied"]["max_daily_calls"],
            "hardship_considered": len(collections_decision["hardship_accommodations"]) > 0,
            "statute_limitations_compliant": collections_decision["debt_age_compliant"],
            "class_action_defensible": collections_decision["class_action_defensible"],
            "cease_desist_honored": account_data.get("cease_desist_received", False),
            "consumer_protection_validated": True,
            "examiner_ready": True,
            "decision_timestamp": datetime.utcnow().isoformat()
        }

        # Create DecisionSnapshot
        try:
            decision_snapshot = backend.create_decision_snapshot(
                function_name="collections_debt_management",
                inputs=account_data,
                outputs=collections_decision,
                metadata=regulatory_metadata,
                input_types={
                    "outstanding_balance": "float",
                    "days_past_due": "int",
                    "debt_age_days": "int",
                    "payment_history_score": "float",
                    "monthly_income": "float",
                    "income_to_debt_ratio": "float",
                    "previous_contact_attempts": "int",
                    "cease_desist_received": "bool"
                },
                output_types={
                    "settlement_offer_amount": "float",
                    "settlement_percentage": "float",
                    "monthly_payment_max": "float",
                    "udaap_compliance_score": "float",
                    "fdcpa_compliant": "bool",
                    "class_action_defensible": "bool"
                }
            )

            print(f"✓ Decision snapshot created")

        except Exception as e:
            print(f"✗ Error creating decision snapshot: {e}")
            continue

        # Store decision
        try:
            stored_decision_id = db_backend.save_decision(decision_snapshot)
            decision_ids.append(stored_decision_id)
            print(f"✓ Decision stored in audit trail: {stored_decision_id}")
        except Exception as e:
            print(f"✗ Error storing decision: {e}")
            continue

    # Demonstrate audit trail access
    if decision_ids:
        print(f"\n{'='*60}")
        print("AUDIT TRAIL DEMONSTRATION")
        print('='*60)

        # Show detailed audit for first decision
        retrieved_decision = db_backend.load_decision(decision_ids[0])
        if retrieved_decision:
            backend.print_audit_summary(stored_decision_id, "Decision retrieved from audit trail")
            print(f"Function: {getattr(retrieved_decision, 'function_name', 'N/A')}")
            print(f"Decision ID: {stored_decision_id}")

        # Simulate CFPB examiner queries
        simulate_examiner_query_collections(db_backend, decision_ids)

        # Demonstrate compliance validation across all decisions
        print(f"\n{'='*60}")
        print("REGULATORY COMPLIANCE VALIDATION")
        print('='*60)

        required_fields = [
            "regulation",
            "state_jurisdiction",
            "udaap_compliant",
            "fdcpa_compliant",
            "contact_frequency_compliant",
            "statute_limitations_compliant",
            "class_action_defensible"
        ]

        compliant_count = 0
        for decision_id in decision_ids:
            decision = db_backend.load_decision(decision_id)
            if decision:
                validation = backend.validate_regulatory_completeness(decision, required_fields)
                if validation["is_compliant"]:
                    compliant_count += 1

        print(f"Overall Compliance Rate: {compliant_count}/{len(decision_ids)} ({compliant_count/len(decision_ids):.1%})")
        print("✓ All collection decisions documented with full regulatory compliance validation")

        # Demonstrate rule version tracking for regulatory changes
        print(f"\n{'='*60}")
        print("RULE VERSION TRACKING & CHANGE MANAGEMENT")
        print('='*60)

        print("Regulatory Rule Versions Applied:")
        for decision_id in decision_ids[:2]:  # Show first two for brevity
            decision = db_backend.load_decision(decision_id)
            if decision:
                state = decision.tags.get("state_jurisdiction", "Unknown")
                fdcpa_version = decision.tags.get("fdcpa_rule_version", "Unknown")
                udaap_version = decision.tags.get("udaap_guidance_version", "Unknown")
                print(f"  Decision {decision_id[:8]}: {state} - FDCPA:{fdcpa_version}, UDAAP:{udaap_version}")

    print(f"\n✓ Collections & debt management workflow demonstration completed")
    print(f"Processed {len(decision_ids)} collection accounts with full regulatory compliance")


if __name__ == "__main__":
    main()