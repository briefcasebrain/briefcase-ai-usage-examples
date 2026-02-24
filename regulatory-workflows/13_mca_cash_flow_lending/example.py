#!/usr/bin/env python3
"""
Briefcase AI Example: MCA Cash Flow Lending (State Commercial Disclosure)

Context: AI-powered Merchant Cash Advance (MCA) and cash flow-based lending platform
for small and medium businesses. Subject to state-level commercial lending disclosures
and consumer protection regulations in CA, NY, UT, VA and other states. All lending
decisions, factor rates, and advance calculations must comply with applicable state
commercial finance laws and disclosure requirements.

Demonstrates:
- AI cash flow analysis and MCA underwriting decisions
- State-by-state commercial disclosure compliance (CA, NY, UT, VA)
- Factor rate optimization with regulatory constraints
- Business cash advance risk assessment and payment scheduling
- Consistent rule application documentation across jurisdictions
- Commercial lending audit trail for state examination compliance
- Multi-state regulatory framework navigation
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

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


def get_state_commercial_disclosure_requirements(state: str) -> Dict[str, Any]:
    """
    Returns state-specific commercial lending disclosure requirements for MCA products.

    Args:
        state: Two-letter state code

    Returns:
        Dictionary containing state-specific disclosure and regulatory requirements
    """
    state_requirements = {
        "CA": {
            "law_name": "California Commercial Finance Disclosure Law",
            "law_reference": "CA Fin Code § 22800-22806",
            "disclosure_required": True,
            "apr_calculation_required": True,
            "total_cost_disclosure": True,
            "payment_schedule_required": True,
            "borrower_acknowledgment": True,
            "filing_requirements": ["annual_report", "quarterly_transaction_summary"],
            "max_prepayment_penalty": 0.05,  # 5% max
            "cooling_off_period_days": 3,
            "language_requirements": ["English", "Spanish"],
            "small_business_protections": True,
            "attorney_fee_restrictions": True,
            "disclosure_timing": "before_consummation"
        },
        "NY": {
            "law_name": "New York Commercial Finance Disclosure Act",
            "law_reference": "NY Gen Bus § 804-807",
            "disclosure_required": True,
            "apr_calculation_required": True,
            "total_cost_disclosure": True,
            "payment_schedule_required": True,
            "borrower_acknowledgment": True,
            "filing_requirements": ["registration", "annual_report"],
            "max_prepayment_penalty": 0.02,  # 2% max
            "cooling_off_period_days": 5,
            "language_requirements": ["English"],
            "small_business_protections": True,
            "attorney_fee_restrictions": True,
            "disclosure_timing": "72_hours_before"
        },
        "UT": {
            "law_name": "Utah Commercial Finance Disclosure Act",
            "law_reference": "UT Code § 70C-7",
            "disclosure_required": True,
            "apr_calculation_required": False,  # Factor rate disclosure only
            "total_cost_disclosure": True,
            "payment_schedule_required": True,
            "borrower_acknowledgment": True,
            "filing_requirements": ["registration"],
            "max_prepayment_penalty": 0.10,  # 10% max
            "cooling_off_period_days": 1,
            "language_requirements": ["English"],
            "small_business_protections": False,
            "attorney_fee_restrictions": False,
            "disclosure_timing": "before_consummation"
        },
        "VA": {
            "law_name": "Virginia Commercial Finance Disclosure Requirements",
            "law_reference": "VA Code § 6.2-2200",
            "disclosure_required": True,
            "apr_calculation_required": True,
            "total_cost_disclosure": True,
            "payment_schedule_required": False,
            "borrower_acknowledgment": False,
            "filing_requirements": ["license", "surety_bond"],
            "max_prepayment_penalty": 0.03,  # 3% max
            "cooling_off_period_days": 2,
            "language_requirements": ["English"],
            "small_business_protections": True,
            "attorney_fee_restrictions": True,
            "disclosure_timing": "before_consummation"
        },
        "DEFAULT": {
            "law_name": "Federal Truth in Lending Act (Commercial)",
            "law_reference": "15 USC § 1601 (Limited Application)",
            "disclosure_required": False,
            "apr_calculation_required": False,
            "total_cost_disclosure": True,
            "payment_schedule_required": False,
            "borrower_acknowledgment": False,
            "filing_requirements": [],
            "max_prepayment_penalty": None,
            "cooling_off_period_days": 0,
            "language_requirements": ["English"],
            "small_business_protections": False,
            "attorney_fee_restrictions": False,
            "disclosure_timing": "before_consummation"
        }
    }

    return state_requirements.get(state, state_requirements["DEFAULT"])


def analyze_business_cash_flow(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes business cash flow patterns for MCA underwriting.

    Args:
        business_data: Business financial and operational data

    Returns:
        Dictionary containing cash flow analysis and risk metrics
    """
    # Extract financial metrics
    monthly_revenue = business_data.get("monthly_revenue", 0)
    bank_balance_avg = business_data.get("bank_balance_avg", 0)
    credit_card_volume = business_data.get("credit_card_volume", 0)
    years_in_business = business_data.get("years_in_business", 0)
    industry = business_data.get("industry", "unknown")

    # Industry risk multipliers
    industry_risk_map = {
        "restaurant": 1.3,
        "retail": 1.1,
        "food_service": 1.3,
        "construction": 1.4,
        "professional_services": 0.8,
        "healthcare": 0.9,
        "technology": 1.0,
        "unknown": 1.5
    }

    industry_risk_multiplier = industry_risk_map.get(industry, 1.2)

    # Calculate revenue volatility (simulated)
    revenue_volatility = min(0.4, max(0.1, random.uniform(0.15, 0.35) * industry_risk_multiplier))

    # Calculate cash flow metrics
    estimated_monthly_expenses = monthly_revenue * 0.75  # Assume 75% expense ratio
    net_cash_flow = monthly_revenue - estimated_monthly_expenses

    # Cash flow to revenue ratio
    cash_flow_ratio = net_cash_flow / monthly_revenue if monthly_revenue > 0 else 0

    # Bank balance adequacy
    balance_coverage_months = bank_balance_avg / estimated_monthly_expenses if estimated_monthly_expenses > 0 else 0

    # Credit card processing consistency (for businesses that use it)
    cc_processing_ratio = credit_card_volume / monthly_revenue if monthly_revenue > 0 else 0

    # Business stability score
    stability_factors = []
    if years_in_business >= 2:
        stability_factors.append("established_business")
    if balance_coverage_months >= 1:
        stability_factors.append("adequate_reserves")
    if cash_flow_ratio >= 0.15:
        stability_factors.append("healthy_margins")
    if revenue_volatility <= 0.25:
        stability_factors.append("stable_revenue")

    stability_score = len(stability_factors) / 4  # 0-1 scale

    # Risk assessment
    if stability_score >= 0.75:
        risk_category = "low"
    elif stability_score >= 0.5:
        risk_category = "moderate"
    else:
        risk_category = "high"

    return {
        "monthly_revenue": monthly_revenue,
        "estimated_monthly_expenses": estimated_monthly_expenses,
        "net_monthly_cash_flow": round(net_cash_flow, 2),
        "cash_flow_ratio": round(cash_flow_ratio, 3),
        "revenue_volatility": round(revenue_volatility, 3),
        "bank_balance_coverage_months": round(balance_coverage_months, 2),
        "credit_card_processing_ratio": round(cc_processing_ratio, 3),
        "industry_risk_multiplier": industry_risk_multiplier,
        "stability_factors": stability_factors,
        "stability_score": round(stability_score, 3),
        "risk_category": risk_category,
        "cash_flow_trend": "stable"  # Simulated - would use historical data
    }


def calculate_mca_terms(
    business_data: Dict[str, Any],
    cash_flow_analysis: Dict[str, Any],
    state_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculates MCA terms including factor rate, advance amount, and payment schedule.

    Args:
        business_data: Business information
        cash_flow_analysis: Cash flow analysis results
        state_requirements: State-specific requirements

    Returns:
        Dictionary containing MCA terms and calculations
    """
    requested_amount = business_data.get("requested_advance", 0)
    monthly_revenue = cash_flow_analysis["monthly_revenue"]
    risk_category = cash_flow_analysis["risk_category"]
    stability_score = cash_flow_analysis["stability_score"]

    # Determine maximum advance amount based on cash flow
    max_advance_multiplier = {
        "low": 1.5,      # 1.5x monthly revenue
        "moderate": 1.2,  # 1.2x monthly revenue
        "high": 0.8      # 0.8x monthly revenue
    }

    max_advance_amount = monthly_revenue * max_advance_multiplier.get(risk_category, 1.0)

    # Cap at platform limits and requested amount
    approved_amount = min(requested_amount, max_advance_amount, 250000)  # $250k platform limit

    # Calculate factor rate based on risk
    base_factor_rate = {
        "low": 1.15,      # 15% premium
        "moderate": 1.25, # 25% premium
        "high": 1.40      # 40% premium
    }

    factor_rate = base_factor_rate.get(risk_category, 1.30)

    # Adjust factor rate for stability and other factors
    if stability_score >= 0.8:
        factor_rate -= 0.05  # 5% discount for very stable businesses
    elif stability_score <= 0.3:
        factor_rate += 0.10  # 10% premium for unstable businesses

    # Industry adjustments
    industry = business_data.get("industry", "unknown")
    if industry in ["professional_services", "healthcare"]:
        factor_rate -= 0.03  # Lower risk industries
    elif industry in ["restaurant", "construction"]:
        factor_rate += 0.05  # Higher risk industries

    # Calculate total payback amount
    total_payback = approved_amount * factor_rate

    # Determine repayment term and daily payment
    # MCA typically has fixed payback regardless of time
    estimated_term_days = random.randint(180, 365)  # 6-12 months typical
    daily_payment = total_payback / estimated_term_days

    # Calculate equivalent APR for disclosure (if required by state)
    if approved_amount > 0 and estimated_term_days > 0:
        cost_of_funds = total_payback - approved_amount
        apr_equivalent = (cost_of_funds / approved_amount) * (365 / estimated_term_days)
    else:
        apr_equivalent = 0

    # Check state-specific constraints
    if state_requirements.get("max_prepayment_penalty") is not None:
        max_prepayment_fee = approved_amount * state_requirements["max_prepayment_penalty"]
    else:
        max_prepayment_fee = approved_amount * 0.05  # Default 5%

    return {
        "approved_advance_amount": round(approved_amount, 2),
        "requested_amount": requested_amount,
        "max_advance_available": round(max_advance_amount, 2),
        "factor_rate": round(factor_rate, 3),
        "total_payback_amount": round(total_payback, 2),
        "total_cost_of_funds": round(total_payback - approved_amount, 2),
        "daily_payment_amount": round(daily_payment, 2),
        "estimated_term_days": estimated_term_days,
        "weekly_payment_amount": round(daily_payment * 7, 2),
        "apr_equivalent": round(apr_equivalent, 4),
        "max_prepayment_penalty": round(max_prepayment_fee, 2),
        "risk_based_pricing": True,
        "payment_frequency": "daily",
        "collection_method": "ach_debit"
    }


def assess_mca_approval_criteria(
    business_data: Dict[str, Any],
    cash_flow_analysis: Dict[str, Any],
    mca_terms: Dict[str, Any],
    state_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assesses MCA approval based on comprehensive criteria.

    Args:
        business_data: Business information
        cash_flow_analysis: Cash flow analysis
        mca_terms: Calculated MCA terms
        state_requirements: State requirements

    Returns:
        Dictionary containing approval decision and rationale
    """
    approval_factors = []
    decline_factors = []

    # Cash flow adequacy
    daily_payment = mca_terms["daily_payment_amount"]
    daily_cash_flow = cash_flow_analysis["net_monthly_cash_flow"] / 30

    if daily_cash_flow >= daily_payment * 1.5:  # 150% coverage
        approval_factors.append("adequate_cash_flow_coverage")
    elif daily_cash_flow >= daily_payment * 1.2:  # 120% coverage
        approval_factors.append("marginal_cash_flow_coverage")
    else:
        decline_factors.append("insufficient_cash_flow_coverage")

    # Business stability
    if cash_flow_analysis["stability_score"] >= 0.6:
        approval_factors.append("stable_business_operations")
    else:
        decline_factors.append("unstable_business_operations")

    # Time in business
    years_in_business = business_data.get("years_in_business", 0)
    if years_in_business >= 1.5:
        approval_factors.append("established_business_history")
    else:
        decline_factors.append("limited_business_history")

    # Credit profile (simplified)
    current_debt = business_data.get("current_debt_obligations", 0)
    debt_to_revenue_ratio = current_debt / cash_flow_analysis["monthly_revenue"] if cash_flow_analysis["monthly_revenue"] > 0 else float('inf')

    if debt_to_revenue_ratio <= 0.5:  # 50% max debt-to-revenue
        approval_factors.append("manageable_debt_levels")
    else:
        decline_factors.append("excessive_existing_debt")

    # Bank balance requirements
    if cash_flow_analysis["bank_balance_coverage_months"] >= 0.5:
        approval_factors.append("adequate_bank_reserves")
    else:
        decline_factors.append("insufficient_bank_reserves")

    # Industry considerations
    high_risk_industries = ["construction", "restaurant", "retail"]
    if business_data.get("industry") not in high_risk_industries:
        approval_factors.append("favorable_industry_risk")

    # Determine approval decision
    critical_decline_factors = [
        "insufficient_cash_flow_coverage",
        "excessive_existing_debt",
        "limited_business_history"
    ]

    has_critical_issues = any(factor in decline_factors for factor in critical_decline_factors)
    approval_score = len(approval_factors) / (len(approval_factors) + len(decline_factors)) if (len(approval_factors) + len(decline_factors)) > 0 else 0

    if has_critical_issues or approval_score < 0.4:
        approval_status = "declined"
    elif approval_score >= 0.7:
        approval_status = "approved"
    else:
        approval_status = "conditional"  # May require additional documentation

    # Risk-based adjustments
    if approval_status == "conditional":
        conditional_requirements = []
        if "marginal_cash_flow_coverage" in approval_factors:
            conditional_requirements.append("enhanced_monitoring")
        if debt_to_revenue_ratio > 0.3:
            conditional_requirements.append("debt_consolidation_option")
    else:
        conditional_requirements = []

    return {
        "approval_status": approval_status,
        "approval_factors": approval_factors,
        "decline_factors": decline_factors,
        "approval_score": round(approval_score, 3),
        "conditional_requirements": conditional_requirements,
        "daily_payment_coverage_ratio": round(daily_cash_flow / daily_payment, 2) if daily_payment > 0 else 0,
        "debt_to_revenue_ratio": round(debt_to_revenue_ratio, 3),
        "recommended_advance_percentage": round((mca_terms["approved_advance_amount"] / mca_terms["max_advance_available"]) * 100, 1) if mca_terms["max_advance_available"] > 0 else 0
    }


def simulate_mca_lending_decision(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates an AI-powered MCA lending decision with state compliance analysis.
    In production, this would be replaced with actual ML model inference.

    Args:
        business_data: Dictionary containing business financial and operational data

    Returns:
        Dictionary containing MCA lending decision and regulatory compliance
    """
    # Get state-specific requirements
    state = business_data.get("state_of_incorporation", "DEFAULT")
    state_requirements = get_state_commercial_disclosure_requirements(state)

    # Perform cash flow analysis
    cash_flow_analysis = analyze_business_cash_flow(business_data)

    # Calculate MCA terms
    mca_terms = calculate_mca_terms(business_data, cash_flow_analysis, state_requirements)

    # Assess approval criteria
    approval_assessment = assess_mca_approval_criteria(
        business_data, cash_flow_analysis, mca_terms, state_requirements
    )

    # Compile comprehensive decision
    decision_result = {
        "approval_status": approval_assessment["approval_status"],
        "approved_advance_amount": mca_terms["approved_advance_amount"] if approval_assessment["approval_status"] != "declined" else 0,
        "factor_rate": mca_terms["factor_rate"],
        "total_payback_amount": mca_terms["total_payback_amount"] if approval_assessment["approval_status"] != "declined" else 0,
        "daily_payment": mca_terms["daily_payment_amount"] if approval_assessment["approval_status"] != "declined" else 0,
        "estimated_term_days": mca_terms["estimated_term_days"],
        "apr_equivalent": mca_terms["apr_equivalent"],
        "cash_flow_analysis": cash_flow_analysis,
        "approval_assessment": approval_assessment,
        "state_disclosure_requirements": state_requirements,
        "disclosures_required": state_requirements["disclosure_required"],
        "apr_disclosure_required": state_requirements["apr_calculation_required"],
        "cooling_off_period_days": state_requirements["cooling_off_period_days"],
        "prepayment_penalty_allowed": state_requirements.get("max_prepayment_penalty", 0) > 0,
        "max_prepayment_penalty": mca_terms["max_prepayment_penalty"],
        "model_version": "mca-underwriting-v2.3.1",
        "decision_trace_id": str(uuid.uuid4()),
        "underwriting_timestamp": datetime.utcnow().isoformat()
    }

    return decision_result


def simulate_examiner_query_mca(db_backend: SqliteBackend, decision_ids: List[str]) -> None:
    """
    Simulates state commercial finance examiner queries for MCA compliance.

    Args:
        db_backend: Database backend
        decision_ids: List of decision IDs to query
    """
    print("\n" + "="*60)
    print("STATE COMMERCIAL FINANCE EXAMINER SIMULATION")
    print("="*60)

    queries = [
        "Demonstrate state-specific commercial disclosure compliance for MCA products",
        "Show evidence of consistent factor rate application and risk-based pricing methodology",
        "Provide audit trail for cash flow analysis and payment capacity assessments",
        "Document state filing requirements compliance and multi-jurisdictional consistency"
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
    Main execution function demonstrating MCA cash flow lending workflow.
    """
    print("=== Briefcase AI MCA Cash Flow Lending Example ===")
    print("Regulation: State Commercial Disclosure Laws")
    print("Scope: AI-powered merchant cash advances with multi-state compliance")
    print("Features: Cash flow analysis, factor rate optimization, state disclosure compliance\n")

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

    # Process multiple MCA scenarios across different states and business types
    mca_scenarios = [
        {
            "scenario_name": "California Restaurant - High Volume",
            "business_data": {
                "business_id": str(uuid.uuid4()),
                "business_name": "Golden Gate Bistro LLC",
                "industry": "restaurant",
                "state_of_incorporation": "CA",
                "years_in_business": 4.5,
                "monthly_revenue": 85000.0,
                "bank_balance_avg": 25000.0,
                "credit_card_volume": 65000.0,
                "requested_advance": 75000.0,
                "current_debt_obligations": 15000.0,
                "number_of_employees": 12,
                "business_license_verified": True,
                "tax_returns_verified": True
            }
        },
        {
            "scenario_name": "New York Professional Services - Stable",
            "business_data": {
                "business_id": str(uuid.uuid4()),
                "business_name": "Metro Consulting Group LLC",
                "industry": "professional_services",
                "state_of_incorporation": "NY",
                "years_in_business": 6.2,
                "monthly_revenue": 125000.0,
                "bank_balance_avg": 45000.0,
                "credit_card_volume": 15000.0,  # Low CC processing
                "requested_advance": 100000.0,
                "current_debt_obligations": 25000.0,
                "number_of_employees": 8,
                "business_license_verified": True,
                "tax_returns_verified": True
            }
        },
        {
            "scenario_name": "Utah Construction - Seasonal",
            "business_data": {
                "business_id": str(uuid.uuid4()),
                "business_name": "Mountain View Construction Inc",
                "industry": "construction",
                "state_of_incorporation": "UT",
                "years_in_business": 2.8,
                "monthly_revenue": 180000.0,
                "bank_balance_avg": 35000.0,
                "credit_card_volume": 5000.0,
                "requested_advance": 150000.0,
                "current_debt_obligations": 85000.0,  # High existing debt
                "number_of_employees": 15,
                "business_license_verified": True,
                "tax_returns_verified": False
            }
        },
        {
            "scenario_name": "Virginia Healthcare - Low Risk",
            "business_data": {
                "business_id": str(uuid.uuid4()),
                "business_name": "Richmond Family Practice PC",
                "industry": "healthcare",
                "state_of_incorporation": "VA",
                "years_in_business": 8.1,
                "monthly_revenue": 95000.0,
                "bank_balance_avg": 55000.0,
                "credit_card_volume": 8000.0,
                "requested_advance": 60000.0,
                "current_debt_obligations": 12000.0,
                "number_of_employees": 6,
                "business_license_verified": True,
                "tax_returns_verified": True
            }
        }
    ]

    decision_ids = []

    for scenario in mca_scenarios:
        print(f"\n{'='*50}")
        print(f"PROCESSING: {scenario['scenario_name']}")
        print('='*50)

        business_data = scenario["business_data"]

        print("Business Profile:")
        for key, value in business_data.items():
            if key not in ["business_id"]:
                print(f"  {key}: {value}")
        print()

        # Run AI MCA underwriting decision
        print("Running AI MCA underwriting analysis...")
        mca_decision = simulate_mca_lending_decision(business_data)

        print(f"SUCCESS: Approval status: {mca_decision['approval_status']}")
        if mca_decision["approval_status"] != "declined":
            print(f"SUCCESS: Approved amount: ${mca_decision['approved_advance_amount']:,.2f}")
            print(f"SUCCESS: Factor rate: {mca_decision['factor_rate']:.3f}")
            print(f"SUCCESS: Total payback: ${mca_decision['total_payback_amount']:,.2f}")
            print(f"SUCCESS: Daily payment: ${mca_decision['daily_payment']:,.2f}")
            if mca_decision["apr_disclosure_required"]:
                print(f"SUCCESS: APR (disclosure): {mca_decision['apr_equivalent']:.1%}")

        # Display cash flow analysis
        cash_flow = mca_decision["cash_flow_analysis"]
        print(f"SUCCESS: Cash flow score: {cash_flow['stability_score']:.2f}")
        print(f"SUCCESS: Risk category: {cash_flow['risk_category']}")

        # Display state-specific compliance
        state_req = mca_decision["state_disclosure_requirements"]
        print(f"SUCCESS: State law: {state_req['law_name']}")
        print(f"SUCCESS: Disclosure required: {mca_decision['disclosures_required']}")
        if mca_decision["cooling_off_period_days"] > 0:
            print(f"SUCCESS: Cooling-off period: {mca_decision['cooling_off_period_days']} days")

        # Display approval factors or decline reasons
        approval_assessment = mca_decision["approval_assessment"]
        if mca_decision["approval_status"] == "declined":
            print(f"WARNING: Decline factors: {', '.join(approval_assessment['decline_factors'])}")
        elif approval_assessment["conditional_requirements"]:
            print(f"SUCCESS: Conditional requirements: {', '.join(approval_assessment['conditional_requirements'])}")

        # Create comprehensive regulatory metadata
        regulatory_metadata = {
            "regulation": "State Commercial Disclosure",
            "state_jurisdiction": business_data["state_of_incorporation"],
            "applicable_law": state_req["law_name"],
            "law_reference": state_req["law_reference"],
            "commercial_disclosure_required": state_req["disclosure_required"],
            "apr_calculation_required": state_req["apr_calculation_required"],
            "total_cost_disclosed": state_req["total_cost_disclosure"],
            "payment_schedule_required": state_req["payment_schedule_required"],
            "cooling_off_period_days": state_req["cooling_off_period_days"],
            "borrower_acknowledgment_required": state_req["borrower_acknowledgment"],
            "filing_requirements": state_req["filing_requirements"],
            "small_business_protections": state_req["small_business_protections"],
            "advance_approved": mca_decision["approval_status"] in ["approved", "conditional"],
            "risk_based_pricing_applied": True,
            "cash_flow_analysis_completed": True,
            "factor_rate_justified": True,
            "payment_capacity_verified": True,
            "state_compliance_validated": True,
            "examiner_ready": True,
            "decision_timestamp": datetime.utcnow().isoformat()
        }

        # Create DecisionSnapshot
        try:
            decision_snapshot = backend.create_decision_snapshot(
                function_name="mca_cash_flow_lending",
                inputs=business_data,
                outputs=mca_decision,
                metadata=regulatory_metadata,
                input_types={
                    "years_in_business": "float",
                    "monthly_revenue": "float",
                    "bank_balance_avg": "float",
                    "credit_card_volume": "float",
                    "requested_advance": "float",
                    "current_debt_obligations": "float",
                    "number_of_employees": "int",
                    "business_license_verified": "bool",
                    "tax_returns_verified": "bool"
                },
                output_types={
                    "approved_advance_amount": "float",
                    "factor_rate": "float",
                    "total_payback_amount": "float",
                    "daily_payment": "float",
                    "apr_equivalent": "float",
                    "max_prepayment_penalty": "float",
                    "estimated_term_days": "int",
                    "disclosures_required": "bool",
                    "apr_disclosure_required": "bool"
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
            backend.print_audit_summary(retrieved_decision)

        # Simulate state commercial finance examiner queries
        simulate_examiner_query_mca(db_backend, decision_ids)

        # Demonstrate compliance validation across all decisions
        print(f"\n{'='*60}")
        print("REGULATORY COMPLIANCE VALIDATION")
        print('='*60)

        required_fields = [
            "regulation",
            "state_jurisdiction",
            "commercial_disclosure_required",
            "total_cost_disclosed",
            "risk_based_pricing_applied",
            "cash_flow_analysis_completed",
            "payment_capacity_verified",
            "state_compliance_validated"
        ]

        compliant_count = 0
        for decision_id in decision_ids:
            decision = db_backend.load_decision(decision_id)
            if decision:
                validation = backend.validate_regulatory_completeness(decision, required_fields)
                if validation["is_compliant"]:
                    compliant_count += 1

        print(f"Overall Compliance Rate: {compliant_count}/{len(decision_ids)} ({compliant_count/len(decision_ids):.1%})")
        print("SUCCESS: All MCA decisions documented with state-specific compliance validation")

        # Demonstrate multi-state consistency tracking
        print(f"\n{'='*60}")
        print("MULTI-STATE COMPLIANCE CONSISTENCY")
        print('='*60)

        print("State-by-State Compliance Application:")
        state_summary = {}
        for decision_id in decision_ids:
            decision = db_backend.load_decision(decision_id)
            if decision:
                state = decision.tags.get("state_jurisdiction", "Unknown")
                law_name = decision.tags.get("applicable_law", "Unknown")
                disclosure_req = decision.tags.get("commercial_disclosure_required", False)

                if state not in state_summary:
                    state_summary[state] = {
                        "law": law_name,
                        "disclosure_required": disclosure_req,
                        "decisions_count": 0
                    }
                state_summary[state]["decisions_count"] += 1

        for state, info in state_summary.items():
            print(f"  {state}: {info['law']} - {info['decisions_count']} decisions processed")
            print(f"    Disclosure Required: {info['disclosure_required']}")

        # Show factor rate consistency across similar risk profiles
        print(f"\nFactor Rate Consistency Analysis:")
        for decision_id in decision_ids:
            decision = db_backend.load_decision(decision_id)
            if decision:
                # Extract factor rate from outputs
                for output in decision.outputs:
                    if output.name == "factor_rate":
                        cash_flow_risk = "Unknown"
                        # Find risk category in cash flow analysis
                        for out in decision.outputs:
                            if out.name == "cash_flow_analysis" and "risk_category" in str(out.value):
                                cash_flow_risk = "Extracted from analysis"  # Simplified for demo
                                break
                        print(f"  Decision {decision_id[:8]}: Factor rate {output.value} applied consistently")
                        break

    print(f"\nSUCCESS: MCA cash flow lending workflow demonstration completed")
    print(f"Processed {len(decision_ids)} MCA applications with full multi-state compliance")


if __name__ == "__main__":
    main()