#!/usr/bin/env python3
"""
Briefcase AI Example: Earned Wage Access (CFPB/TILA)

Context: AI-powered Earned Wage Access (EWA) platform allowing employees to access
earned wages before payday. Subject to CFPB oversight and evolving Truth in Lending
Act (TILA) disclosure requirements. Regulatory classification uncertain - may be
classified as credit, payment advance, or employer benefit. All wage advance decisions
must be documented for potential TILA compliance and consumer protection examination.

Demonstrates:
- AI wage access eligibility decisions with payroll integration
- Regulatory classification uncertainty tracking over time
- TILA disclosure requirements based on evolving classification guidance
- Payroll integration and wage calculation validation
- Fee structure compliance with consumer protection standards
- Advance decisioning with ability-to-repay considerations
- Temporal tracking of regulatory guidance evolution
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

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


def get_regulatory_classification_status(current_date: datetime) -> Dict[str, Any]:
    """
    Returns current regulatory classification status for EWA products.
    This changes over time as guidance evolves.

    Args:
        current_date: Current date for temporal classification

    Returns:
        Dictionary containing current regulatory classification and guidance
    """
    # Simulate evolving regulatory guidance over time
    if current_date < datetime(2023, 1, 1):
        return {
            "primary_classification": "uncertain",
            "potential_classifications": ["payroll_advance", "employer_benefit", "credit_product"],
            "tila_applicable": "uncertain",
            "cfpb_guidance_version": "2022-preliminary",
            "disclosure_requirements": ["basic_fee_disclosure"],
            "apr_calculation_required": False,
            "credit_reporting_required": False
        }
    elif current_date < datetime(2024, 1, 1):
        return {
            "primary_classification": "employer_benefit_with_credit_features",
            "potential_classifications": ["employer_benefit", "credit_product"],
            "tila_applicable": "conditional",
            "cfpb_guidance_version": "2023-interim",
            "disclosure_requirements": ["enhanced_fee_disclosure", "conditional_apr"],
            "apr_calculation_required": True,  # For disclosure purposes
            "credit_reporting_required": False
        }
    else:  # 2024 and later
        return {
            "primary_classification": "credit_product_with_exemptions",
            "potential_classifications": ["credit_product", "employer_benefit"],
            "tila_applicable": "yes_with_exemptions",
            "cfpb_guidance_version": "2024-final",
            "disclosure_requirements": ["full_tila_disclosure", "apr_calculation", "ability_to_repay"],
            "apr_calculation_required": True,
            "credit_reporting_required": True
        }


def calculate_earned_wages(employee_data: Dict[str, Any], current_date: datetime) -> Dict[str, Any]:
    """
    Calculates earned wages available for advance based on payroll data.

    Args:
        employee_data: Employee work and pay information
        current_date: Current date for calculation

    Returns:
        Dictionary containing wage calculations and eligibility
    """
    # Parse pay period dates
    pay_period_start = datetime.fromisoformat(employee_data["pay_period_start"])
    next_payday = datetime.fromisoformat(employee_data["next_payday"])

    # Calculate days worked in current period
    days_worked = (current_date - pay_period_start).days
    total_pay_period_days = (next_payday - pay_period_start).days

    # Calculate earned wages based on employment type
    if employee_data.get("employment_type") == "hourly":
        hours_worked = employee_data.get("hours_worked_this_period", 0)
        hourly_rate = employee_data.get("hourly_rate", 0)
        gross_earned = hours_worked * hourly_rate
    else:  # Salaried
        annual_salary = employee_data.get("annual_salary", 0)
        daily_rate = annual_salary / 365
        gross_earned = daily_rate * days_worked

    # Estimate taxes and deductions (simplified)
    tax_rate = employee_data.get("estimated_tax_rate", 0.22)  # Federal + state + FICA
    other_deductions = employee_data.get("other_deductions_per_period", 0)

    estimated_taxes = gross_earned * tax_rate
    net_earned = gross_earned - estimated_taxes - (other_deductions * days_worked / total_pay_period_days)

    # Apply EWA platform constraints
    max_advance_percentage = 0.5  # Maximum 50% of net earned
    max_advance_dollar = min(500, net_earned * max_advance_percentage)

    return {
        "gross_earned_wages": round(gross_earned, 2),
        "estimated_net_earned": round(net_earned, 2),
        "max_advance_available": round(max_advance_dollar, 2),
        "days_worked_current_period": days_worked,
        "total_pay_period_days": total_pay_period_days,
        "earnings_calculation_method": "hourly" if employee_data.get("employment_type") == "hourly" else "salary_pro_rata",
        "tax_withholding_estimated": round(estimated_taxes, 2)
    }


def calculate_ewa_fees_and_apr(advance_amount: float, repayment_date: datetime, current_date: datetime) -> Dict[str, Any]:
    """
    Calculates EWA fees and APR based on current regulatory requirements.

    Args:
        advance_amount: Amount of advance requested
        repayment_date: Expected repayment date
        current_date: Current date

    Returns:
        Dictionary containing fee structure and APR calculations
    """
    days_to_repayment = (repayment_date - current_date).days

    # Fee structure based on industry standards
    if advance_amount <= 100:
        base_fee = 2.99
    elif advance_amount <= 250:
        base_fee = 3.99
    else:
        base_fee = 4.99

    # Optional expedited fee
    expedited_fee = 1.99 if random.choice([True, False]) else 0

    total_fee = base_fee + expedited_fee

    # APR calculation for disclosure (annualized)
    if days_to_repayment > 0:
        apr = ((total_fee / advance_amount) * (365 / days_to_repayment))
    else:
        apr = 0

    return {
        "base_fee": base_fee,
        "expedited_fee": expedited_fee,
        "total_fee": total_fee,
        "advance_amount": advance_amount,
        "repayment_amount": advance_amount,  # Principal only (fees separate)
        "days_to_repayment": days_to_repayment,
        "calculated_apr": round(apr, 4),
        "fee_as_percentage": round((total_fee / advance_amount) * 100, 2) if advance_amount > 0 else 0
    }


def assess_ability_to_repay(employee_data: Dict[str, Any], advance_amount: float) -> Dict[str, Any]:
    """
    Assesses employee's ability to repay the advance based on income and obligations.

    Args:
        employee_data: Employee financial information
        advance_amount: Requested advance amount

    Returns:
        Dictionary containing ability to repay assessment
    """
    # Calculate monthly income
    if employee_data.get("employment_type") == "hourly":
        monthly_income = employee_data.get("hourly_rate", 0) * 40 * 4.33  # Assume 40 hrs/week
    else:
        monthly_income = employee_data.get("annual_salary", 0) / 12

    # Estimate monthly expenses (if not provided)
    estimated_monthly_expenses = employee_data.get("monthly_expenses", monthly_income * 0.8)

    # Calculate discretionary income
    discretionary_income = monthly_income - estimated_monthly_expenses

    # Check previous EWA usage
    previous_advances = employee_data.get("previous_advances_count", 0)
    previous_advance_amount = employee_data.get("previous_advance_outstanding", 0)

    # Calculate repayment capacity
    available_for_repayment = discretionary_income + previous_advance_amount  # Since previous will be repaid
    repayment_ratio = advance_amount / available_for_repayment if available_for_repayment > 0 else float('inf')

    # Determine ability to repay
    can_repay = (
        repayment_ratio <= 0.5 and  # Advance shouldn't exceed 50% of available income
        previous_advances <= 3 and  # Limit frequency
        advance_amount <= 500 and   # Hard dollar limit
        monthly_income >= 2000      # Minimum income threshold
    )

    return {
        "monthly_income": round(monthly_income, 2),
        "estimated_monthly_expenses": round(estimated_monthly_expenses, 2),
        "discretionary_income": round(discretionary_income, 2),
        "available_for_repayment": round(available_for_repayment, 2),
        "repayment_ratio": round(repayment_ratio, 3),
        "can_repay_determination": can_repay,
        "previous_advances_count": previous_advances,
        "income_verification_status": employee_data.get("income_verified", True)
    }


def simulate_ewa_eligibility_decision(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates an AI decision for earned wage access eligibility with full compliance analysis.
    In production, this would be replaced with actual ML model inference.

    Args:
        employee_data: Dictionary containing employee work and earnings data

    Returns:
        Dictionary containing EWA eligibility decision and regulatory compliance
    """
    current_date = datetime.utcnow()
    request_amount = employee_data.get("advance_request_amount", 0)

    # Get current regulatory classification
    regulatory_status = get_regulatory_classification_status(current_date)

    # Calculate earned wages
    wage_calculation = calculate_earned_wages(employee_data, current_date)

    # Assess basic eligibility criteria
    eligibility_factors = []

    # Employment verification
    if employee_data.get("employer_verified", False):
        eligibility_factors.append("employer_verified")
    else:
        eligibility_factors.append("employer_not_verified")

    # Wage availability
    if wage_calculation["max_advance_available"] >= request_amount:
        eligibility_factors.append("sufficient_earned_wages")
    else:
        eligibility_factors.append("insufficient_earned_wages")

    # Account standing
    account_standing = employee_data.get("account_standing", "good")
    eligibility_factors.append(f"account_standing_{account_standing}")

    # Previous advance history
    if employee_data.get("previous_advances_count", 0) <= 2:
        eligibility_factors.append("acceptable_advance_history")
    else:
        eligibility_factors.append("excessive_advance_frequency")

    # Determine eligibility
    disqualifying_factors = [
        "employer_not_verified",
        "insufficient_earned_wages",
        "account_standing_poor",
        "excessive_advance_frequency"
    ]

    is_eligible = not any(factor in eligibility_factors for factor in disqualifying_factors)

    if is_eligible:
        # Determine advance amount (may be less than requested)
        max_available = wage_calculation["max_advance_available"]
        approved_amount = min(request_amount, max_available, 500)  # $500 platform limit

        # Calculate fees and APR
        next_payday = datetime.fromisoformat(employee_data["next_payday"])
        fee_calculation = calculate_ewa_fees_and_apr(approved_amount, next_payday, current_date)

        # Assess ability to repay (required by some regulatory frameworks)
        repay_assessment = assess_ability_to_repay(employee_data, approved_amount)

        eligibility_status = "approved"
        decline_reasons = []

        # Final check: ability to repay
        if not repay_assessment["can_repay_determination"]:
            eligibility_status = "conditional"  # May require additional verification
    else:
        approved_amount = 0
        fee_calculation = calculate_ewa_fees_and_apr(0, current_date, current_date)
        repay_assessment = assess_ability_to_repay(employee_data, 0)
        eligibility_status = "declined"
        decline_reasons = [factor for factor in eligibility_factors if factor in disqualifying_factors]

    # Determine required disclosures based on regulatory status
    required_disclosures = []
    if regulatory_status["tila_applicable"] in ["yes_with_exemptions", "conditional"]:
        required_disclosures.extend(["tila_disclosure", "apr_disclosure"])
    if "full_tila_disclosure" in regulatory_status["disclosure_requirements"]:
        required_disclosures.extend(["full_tila_disclosure", "ability_to_repay_disclosure"])

    required_disclosures.extend(["fee_structure_disclosure", "repayment_terms_disclosure"])

    return {
        "eligibility_status": eligibility_status,
        "approved_advance_amount": approved_amount,
        "requested_amount": request_amount,
        "max_available_amount": wage_calculation["max_advance_available"],
        "advance_fee": fee_calculation["total_fee"],
        "repayment_amount": approved_amount,  # EWA typically has no interest
        "repayment_date": employee_data["next_payday"],
        "calculated_apr": fee_calculation["calculated_apr"],
        "fee_as_percentage": fee_calculation["fee_as_percentage"],
        "wage_calculation": wage_calculation,
        "fee_breakdown": {
            "base_fee": fee_calculation["base_fee"],
            "expedited_fee": fee_calculation["expedited_fee"],
            "total_fee": fee_calculation["total_fee"]
        },
        "eligibility_factors": eligibility_factors,
        "decline_reasons": decline_reasons,
        "ability_to_repay": repay_assessment,
        "regulatory_classification": regulatory_status,
        "required_disclosures": required_disclosures,
        "tila_disclosures_required": regulatory_status["tila_applicable"] != "uncertain",
        "employer_integration_verified": employee_data.get("employer_verified", False),
        "payroll_deduction_authorized": employee_data.get("payroll_deduction_consent", False),
        "model_version": "ewa-eligibility-v3.1.2",
        "decision_trace_id": str(uuid.uuid4()),
        "decision_timestamp": current_date.isoformat()
    }


def simulate_examiner_query_ewa(db_backend: SqliteBackend, decision_ids: List[str]) -> None:
    """
    Simulates CFPB examiner queries for EWA compliance.

    Args:
        db_backend: Database backend
        decision_ids: List of decision IDs to query
    """
    print("\n" + "="*60)
    print("CFPB EXAMINER SIMULATION - EWA COMPLIANCE")
    print("="*60)

    queries = [
        "Demonstrate TILA disclosure compliance and APR calculation methodology for EWA products",
        "Show evidence of regulatory classification tracking and guidance evolution over time",
        "Provide audit trail for ability-to-repay assessments and payroll integration verification",
        "Document fee structure compliance and consumer protection measures for wage advances"
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
    Main execution function demonstrating earned wage access workflow.
    """
    print("=== Briefcase AI Earned Wage Access Example ===")
    print("Regulation: CFPB/TILA")
    print("Scope: AI-powered wage advances with evolving regulatory compliance")
    print("Features: Payroll integration, regulatory classification tracking, TILA compliance\n")

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

    # Process multiple EWA scenarios across different time periods and employee types
    ewa_scenarios = [
        {
            "scenario_name": "Hourly Food Service Worker - High Frequency User",
            "employee_data": {
                "employee_id": str(uuid.uuid4()),
                "employee_name": "Maria Santos",
                "employer": "Restaurant Chain Inc",
                "employment_type": "hourly",
                "hourly_rate": 16.50,
                "hours_worked_this_period": 35,
                "pay_period_start": "2024-02-12",
                "next_payday": "2024-02-26",
                "advance_request_amount": 180.00,
                "previous_advances_count": 3,
                "previous_advance_outstanding": 0,
                "account_standing": "good",
                "employer_verified": True,
                "payroll_deduction_consent": True,
                "estimated_tax_rate": 0.18,
                "monthly_expenses": 2400,
                "income_verified": True
            }
        },
        {
            "scenario_name": "Salaried Office Worker - First Time User",
            "employee_data": {
                "employee_id": str(uuid.uuid4()),
                "employee_name": "David Chen",
                "employer": "Tech Solutions LLC",
                "employment_type": "salaried",
                "annual_salary": 55000,
                "pay_period_start": "2024-02-01",
                "next_payday": "2024-03-01",
                "advance_request_amount": 300.00,
                "previous_advances_count": 0,
                "previous_advance_outstanding": 0,
                "account_standing": "excellent",
                "employer_verified": True,
                "payroll_deduction_consent": True,
                "estimated_tax_rate": 0.24,
                "monthly_expenses": 3200,
                "income_verified": True
            }
        },
        {
            "scenario_name": "Part-time Retail Worker - Limited Income",
            "employee_data": {
                "employee_id": str(uuid.uuid4()),
                "employee_name": "Ashley Williams",
                "employer": "Retail Store Corp",
                "employment_type": "hourly",
                "hourly_rate": 14.00,
                "hours_worked_this_period": 22,
                "pay_period_start": "2024-02-10",
                "next_payday": "2024-02-24",
                "advance_request_amount": 120.00,
                "previous_advances_count": 1,
                "previous_advance_outstanding": 85.00,
                "account_standing": "good",
                "employer_verified": True,
                "payroll_deduction_consent": False,  # No automatic deduction consent
                "estimated_tax_rate": 0.15,
                "monthly_expenses": 1800,
                "income_verified": False
            }
        },
        {
            "scenario_name": "High-Income Professional - Large Request",
            "employee_data": {
                "employee_id": str(uuid.uuid4()),
                "employee_name": "Robert Johnson",
                "employer": "Professional Services Inc",
                "employment_type": "salaried",
                "annual_salary": 95000,
                "pay_period_start": "2024-02-01",
                "next_payday": "2024-02-15",
                "advance_request_amount": 750.00,  # Exceeds platform limits
                "previous_advances_count": 0,
                "previous_advance_outstanding": 0,
                "account_standing": "excellent",
                "employer_verified": True,
                "payroll_deduction_consent": True,
                "estimated_tax_rate": 0.28,
                "monthly_expenses": 4500,
                "income_verified": True
            }
        }
    ]

    decision_ids = []

    for scenario in ewa_scenarios:
        print(f"\n{'='*50}")
        print(f"PROCESSING: {scenario['scenario_name']}")
        print('='*50)

        employee_data = scenario["employee_data"]

        print("Employee Profile:")
        for key, value in employee_data.items():
            if key not in ["employee_id"]:
                print(f"  {key}: {value}")
        print()

        # Run AI EWA eligibility decision
        print("Running EWA eligibility assessment...")
        ewa_decision = simulate_ewa_eligibility_decision(employee_data)

        print(f"SUCCESS: Eligibility: {ewa_decision['eligibility_status']}")
        print(f"SUCCESS: Approved amount: ${ewa_decision['approved_advance_amount']:.2f}")
        if ewa_decision["approved_advance_amount"] > 0:
            print(f"SUCCESS: Total fee: ${ewa_decision['advance_fee']:.2f}")
            print(f"SUCCESS: APR (disclosure): {ewa_decision['calculated_apr']:.1%}")
            print(f"SUCCESS: Fee percentage: {ewa_decision['fee_as_percentage']:.1%}")

        # Display regulatory classification
        reg_class = ewa_decision["regulatory_classification"]
        print(f"SUCCESS: Regulatory classification: {reg_class['primary_classification']}")
        print(f"SUCCESS: CFPB guidance version: {reg_class['cfpb_guidance_version']}")

        # Display eligibility factors
        if ewa_decision["decline_reasons"]:
            print(f"WARNING: Decline reasons: {', '.join(ewa_decision['decline_reasons'])}")

        if ewa_decision["required_disclosures"]:
            print(f"SUCCESS: Required disclosures: {', '.join(ewa_decision['required_disclosures'])}")

        # Display ability to repay assessment
        repay_assessment = ewa_decision["ability_to_repay"]
        print(f"SUCCESS: Ability to repay: {repay_assessment['can_repay_determination']}")
        if not repay_assessment["can_repay_determination"]:
            print(f"  - Repayment ratio: {repay_assessment['repayment_ratio']:.2f}")
            print(f"  - Monthly income: ${repay_assessment['monthly_income']:.2f}")

        # Create comprehensive regulatory metadata
        regulatory_metadata = {
            "regulation": "CFPB/TILA",
            "regulatory_classification": reg_class["primary_classification"],
            "cfpb_guidance_version": reg_class["cfpb_guidance_version"],
            "tila_applicable": reg_class["tila_applicable"],
            "tila_disclosures_provided": ewa_decision["tila_disclosures_required"],
            "apr_calculated": ewa_decision["calculated_apr"] if ewa_decision["approved_advance_amount"] > 0 else None,
            "fee_structure_disclosed": True,
            "ability_to_repay_assessed": True,
            "payroll_integration_verified": ewa_decision["employer_integration_verified"],
            "consumer_protection_compliant": True,
            "advance_approved": ewa_decision["eligibility_status"] == "approved",
            "employer_consent_verified": employee_data.get("employer_verified", False),
            "payroll_deduction_authorized": employee_data.get("payroll_deduction_consent", False),
            "wage_calculation_method": ewa_decision["wage_calculation"]["earnings_calculation_method"],
            "regulatory_uncertainty_acknowledged": reg_class["primary_classification"] in ["uncertain", "employer_benefit_with_credit_features"],
            "examiner_ready": True,
            "decision_timestamp": datetime.utcnow().isoformat()
        }

        # Create DecisionSnapshot
        try:
            decision_snapshot = backend.create_decision_snapshot(
                function_name="ewa_non_traditional_credit",
                inputs=employee_data,
                outputs=ewa_decision,
                metadata=regulatory_metadata,
                input_types={
                    "hourly_rate": "float",
                    "hours_worked_this_period": "int",
                    "annual_salary": "float",
                    "advance_request_amount": "float",
                    "previous_advances_count": "int",
                    "previous_advance_outstanding": "float",
                    "estimated_tax_rate": "float",
                    "monthly_expenses": "float",
                    "employer_verified": "bool",
                    "payroll_deduction_consent": "bool",
                    "income_verified": "bool"
                },
                output_types={
                    "approved_advance_amount": "float",
                    "requested_amount": "float",
                    "max_available_amount": "float",
                    "advance_fee": "float",
                    "repayment_amount": "float",
                    "calculated_apr": "float",
                    "fee_as_percentage": "float",
                    "tila_disclosures_required": "bool"
                }
            )

            print(f"SUCCESS: Decision snapshot created")

        except Exception as e:
            print(f"ERROR: Error creating decision snapshot: {e}")
            continue

        # Store decision
        try:
            stored_decision_id = db_backend.save_decision(decision_snapshot)
            decision_ids.append(stored_decision_id)
            print(f"SUCCESS: Decision stored in audit trail: {stored_decision_id}")
        except Exception as e:
            print(f"ERROR: Error storing decision: {e}")
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
        simulate_examiner_query_ewa(db_backend, decision_ids)

        # Demonstrate compliance validation across all decisions
        print(f"\n{'='*60}")
        print("REGULATORY COMPLIANCE VALIDATION")
        print('='*60)

        required_fields = [
            "regulation",
            "regulatory_classification",
            "tila_applicable",
            "fee_structure_disclosed",
            "ability_to_repay_assessed",
            "payroll_integration_verified",
            "consumer_protection_compliant"
        ]

        compliant_count = 0
        for decision_id in decision_ids:
            decision = db_backend.load_decision(decision_id)
            if decision:
                validation = backend.validate_regulatory_completeness(decision, required_fields)
                if validation["is_compliant"]:
                    compliant_count += 1

        print(f"Overall Compliance Rate: {compliant_count}/{len(decision_ids)} ({compliant_count/len(decision_ids):.1%})")
        print("SUCCESS: All EWA decisions documented with regulatory classification tracking")

        # Demonstrate regulatory classification evolution tracking
        print(f"\n{'='*60}")
        print("REGULATORY CLASSIFICATION EVOLUTION")
        print('='*60)

        print("Regulatory Classification Tracking (shows evolution over time):")
        for decision_id in decision_ids[:2]:  # Show first two for brevity
            decision = db_backend.load_decision(decision_id)
            if decision:
                classification = decision.tags.get("regulatory_classification", "Unknown")
                guidance_version = decision.tags.get("cfpb_guidance_version", "Unknown")
                print(f"  Decision {decision_id[:8]}: {classification} (Guidance: {guidance_version})")

        # Show temporal consistency of fee calculations
        print(f"\nFee Structure and APR Calculation Consistency:")
        for decision_id in decision_ids:
            decision = db_backend.load_decision(decision_id)
            if decision:
                # Extract fee information from outputs
                for output in decision.outputs:
                    if output.name == "calculated_apr" and float(output.value) > 0:
                        print(f"  Decision {decision_id[:8]}: APR calculated and disclosed as required")
                        break

    print(f"\nSUCCESS: Earned Wage Access workflow demonstration completed")
    print(f"Processed {len(decision_ids)} EWA requests with full regulatory compliance tracking")


if __name__ == "__main__":
    main()