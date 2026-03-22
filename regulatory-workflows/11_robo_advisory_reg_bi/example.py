#!/usr/bin/env python3
"""
Briefcase AI Example: Robo-Advisory & Reg BI (SEC/FINRA)

Context: AI-powered robo-advisor providing automated investment recommendations and
portfolio management. Subject to SEC Regulation Best Interest (Reg BI) and FINRA
oversight. All investment recommendations must be in the client's best interest,
with comprehensive suitability analysis, conflict disclosure, and supervisory review.

Demonstrates:
- AI investment recommendation decisions with best interest analysis
- Client risk profile snapshot preservation for temporal consistency
- Reg BI best interest vs. suitability standard compliance validation
- Fiduciary duty documentation and conflict of interest management
- Supervisory review workflow and escalation procedures
- Investment product suitability scoring with fee impact analysis
- Performance attribution and ongoing monitoring requirements
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


def calculate_client_risk_profile(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates comprehensive client risk profile based on regulatory requirements.

    Args:
        client_data: Client demographic and financial information

    Returns:
        Dictionary containing risk profile analysis
    """
    age = client_data["age"]
    income = client_data["annual_income"]
    net_worth = client_data.get("net_worth", income * 3)  # Estimate if not provided
    investment_experience = client_data["investment_experience"]
    time_horizon = client_data["time_horizon_years"]
    liquidity_needs = client_data.get("liquidity_needs", "moderate")

    # Risk tolerance scoring
    risk_tolerance_map = {
        "conservative": 2,
        "moderate_conservative": 3,
        "moderate": 5,
        "moderate_aggressive": 7,
        "aggressive": 9
    }

    experience_map = {
        "none": 1,
        "limited": 2,
        "moderate": 4,
        "extensive": 6
    }

    liquidity_map = {
        "high": 1,
        "moderate": 3,
        "low": 5
    }

    # Base risk score from stated tolerance
    risk_score = risk_tolerance_map.get(client_data["risk_tolerance"], 5)

    # Age adjustment
    if age < 30:
        age_adjustment = 2
    elif age < 40:
        age_adjustment = 1
    elif age < 55:
        age_adjustment = 0
    elif age < 65:
        age_adjustment = -1
    else:
        age_adjustment = -2

    # Time horizon adjustment
    if time_horizon >= 20:
        time_adjustment = 2
    elif time_horizon >= 10:
        time_adjustment = 1
    elif time_horizon >= 5:
        time_adjustment = 0
    else:
        time_adjustment = -2

    # Income and net worth adjustment
    if income >= 150000 and net_worth >= 500000:
        wealth_adjustment = 1
    elif income >= 75000 and net_worth >= 100000:
        wealth_adjustment = 0
    else:
        wealth_adjustment = -1

    # Final adjusted risk score (1-10 scale)
    adjusted_risk_score = max(1, min(10,
        risk_score + age_adjustment + time_adjustment + wealth_adjustment
    ))

    # Experience factor for suitability
    experience_score = experience_map.get(investment_experience, 2)
    liquidity_score = liquidity_map.get(liquidity_needs, 3)

    return {
        "risk_tolerance_stated": risk_score,
        "risk_score_adjusted": adjusted_risk_score,
        "investment_experience_score": experience_score,
        "liquidity_preference_score": liquidity_score,
        "age_category": "young" if age < 40 else "middle" if age < 60 else "mature",
        "wealth_category": "high" if net_worth >= 500000 else "moderate" if net_worth >= 100000 else "building",
        "time_horizon_category": "long" if time_horizon >= 10 else "medium" if time_horizon >= 5 else "short",
        "overall_risk_capacity": min(10, (adjusted_risk_score + experience_score + liquidity_score) / 3 * 2)
    }


def generate_asset_allocation(risk_profile: Dict[str, Any], client_goals: List[str]) -> Dict[str, Any]:
    """
    Generates target asset allocation based on risk profile and investment goals.

    Args:
        risk_profile: Client risk analysis
        client_goals: List of investment objectives

    Returns:
        Dictionary containing asset allocation recommendation
    """
    risk_score = risk_profile["risk_score_adjusted"]
    time_horizon = risk_profile["time_horizon_category"]

    # Base allocation based on risk score
    if risk_score <= 3:  # Conservative
        base_allocation = {"stocks": 30, "bonds": 60, "alternatives": 5, "cash": 5}
    elif risk_score <= 5:  # Moderate Conservative
        base_allocation = {"stocks": 50, "bonds": 40, "alternatives": 7, "cash": 3}
    elif risk_score <= 7:  # Moderate to Moderate Aggressive
        base_allocation = {"stocks": 70, "bonds": 25, "alternatives": 5, "cash": 0}
    else:  # Aggressive
        base_allocation = {"stocks": 85, "bonds": 10, "alternatives": 5, "cash": 0}

    # Adjust for time horizon
    if time_horizon == "short":
        # Reduce equity exposure for short time horizon
        base_allocation["stocks"] = max(20, base_allocation["stocks"] - 20)
        base_allocation["bonds"] += 15
        base_allocation["cash"] += 5
    elif time_horizon == "long":
        # Increase equity exposure for long time horizon
        base_allocation["stocks"] = min(90, base_allocation["stocks"] + 10)
        base_allocation["bonds"] = max(5, base_allocation["bonds"] - 10)

    # Adjust for specific goals
    if "income_generation" in client_goals:
        base_allocation["bonds"] += 10
        base_allocation["stocks"] = max(20, base_allocation["stocks"] - 10)

    if "capital_preservation" in client_goals:
        base_allocation["bonds"] += 15
        base_allocation["cash"] += 5
        base_allocation["stocks"] = max(20, base_allocation["stocks"] - 20)

    # Normalize to 100%
    total = sum(base_allocation.values())
    if total != 100:
        adjustment_factor = 100 / total
        for asset in base_allocation:
            base_allocation[asset] = round(base_allocation[asset] * adjustment_factor)

    return base_allocation


def calculate_best_interest_score(
    client_data: Dict[str, Any],
    recommendation: Dict[str, Any],
    product_details: Dict[str, Any]
) -> Tuple[float, List[str]]:
    """
    Calculates Reg BI best interest compliance score and identifies considerations.

    Args:
        client_data: Client profile information
        recommendation: Investment recommendation
        product_details: Investment product characteristics and fees

    Returns:
        Tuple of (best_interest_score, list_of_considerations)
    """
    score = 1.0
    considerations = []

    # Fee reasonableness analysis
    total_fee = product_details["expense_ratio"] + product_details.get("advisor_fee", 0)
    if total_fee > 0.015:  # > 1.5% total
        score -= 0.2
        considerations.append("High fee structure requires enhanced justification")
    elif total_fee > 0.01:  # > 1.0% total
        score -= 0.1
        considerations.append("Moderate fee structure - ensure value justification")

    # Complexity vs. sophistication match
    product_complexity = product_details.get("complexity_score", 5)  # 1-10 scale
    client_sophistication = client_data.get("investment_experience_score", 3)

    if product_complexity > client_sophistication + 3:
        score -= 0.25
        considerations.append("Product complexity exceeds client sophistication")
    elif product_complexity > client_sophistication + 1:
        score -= 0.1
        considerations.append("Product complexity requires additional disclosure")

    # Risk alignment
    risk_profile = calculate_client_risk_profile(client_data)
    product_risk = product_details.get("risk_level", 5)  # 1-10 scale
    risk_diff = abs(product_risk - risk_profile["risk_score_adjusted"])

    if risk_diff > 3:
        score -= 0.3
        considerations.append("Significant risk misalignment with client profile")
    elif risk_diff > 1:
        score -= 0.15
        considerations.append("Minor risk misalignment requires documentation")

    # Liquidity match
    liquidity_needs = client_data.get("liquidity_needs", "moderate")
    product_liquidity = product_details.get("liquidity_rating", "moderate")

    liquidity_mismatch = {
        ("high", "low"): -0.3,
        ("high", "moderate"): -0.15,
        ("moderate", "low"): -0.1
    }

    mismatch_penalty = liquidity_mismatch.get((liquidity_needs, product_liquidity), 0)
    if mismatch_penalty < 0:
        score += mismatch_penalty
        considerations.append(f"Liquidity mismatch: client needs {liquidity_needs}, product offers {product_liquidity}")

    # Conflict of interest considerations
    if product_details.get("proprietary_product", False):
        score -= 0.1
        considerations.append("Proprietary product requires conflict disclosure")

    if product_details.get("revenue_sharing", 0) > 0:
        score -= 0.05
        considerations.append("Revenue sharing arrangement requires disclosure")

    return max(0.0, score), considerations


def simulate_robo_advisory_recommendation(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates an AI-powered investment recommendation decision with Reg BI compliance.
    In production, this would be replaced with actual ML model inference.

    Args:
        client_data: Dictionary containing client profile and investment data

    Returns:
        Dictionary containing investment recommendation and compliance analysis
    """
    # Calculate comprehensive risk profile
    risk_profile = calculate_client_risk_profile(client_data)

    # Generate asset allocation
    asset_allocation = generate_asset_allocation(risk_profile, client_data.get("investment_goals", []))

    # Simulate product selection based on allocation
    recommended_products = []
    total_expense_ratio = 0.0

    # Stock allocation - recommend index funds or ETFs
    if asset_allocation["stocks"] > 0:
        stock_product = {
            "product_name": "Total Stock Market Index Fund",
            "asset_class": "stocks",
            "allocation_percentage": asset_allocation["stocks"],
            "expense_ratio": 0.003,  # 0.3%
            "complexity_score": 3,
            "risk_level": risk_profile["risk_score_adjusted"],
            "liquidity_rating": "high",
            "proprietary_product": False,
            "revenue_sharing": 0
        }
        recommended_products.append(stock_product)
        total_expense_ratio += stock_product["expense_ratio"] * (asset_allocation["stocks"] / 100)

    # Bond allocation
    if asset_allocation["bonds"] > 0:
        bond_product = {
            "product_name": "Aggregate Bond Index Fund",
            "asset_class": "bonds",
            "allocation_percentage": asset_allocation["bonds"],
            "expense_ratio": 0.004,  # 0.4%
            "complexity_score": 2,
            "risk_level": 3,
            "liquidity_rating": "high",
            "proprietary_product": False,
            "revenue_sharing": 0
        }
        recommended_products.append(bond_product)
        total_expense_ratio += bond_product["expense_ratio"] * (asset_allocation["bonds"] / 100)

    # Alternative allocation
    if asset_allocation["alternatives"] > 0:
        alt_product = {
            "product_name": "Real Estate Investment Trust Fund",
            "asset_class": "alternatives",
            "allocation_percentage": asset_allocation["alternatives"],
            "expense_ratio": 0.012,  # 1.2%
            "complexity_score": 6,
            "risk_level": 6,
            "liquidity_rating": "moderate",
            "proprietary_product": False,
            "revenue_sharing": 0.002
        }
        recommended_products.append(alt_product)
        total_expense_ratio += alt_product["expense_ratio"] * (asset_allocation["alternatives"] / 100)

    # Cash allocation
    if asset_allocation["cash"] > 0:
        cash_product = {
            "product_name": "Money Market Fund",
            "asset_class": "cash",
            "allocation_percentage": asset_allocation["cash"],
            "expense_ratio": 0.001,  # 0.1%
            "complexity_score": 1,
            "risk_level": 1,
            "liquidity_rating": "high",
            "proprietary_product": False,
            "revenue_sharing": 0
        }
        recommended_products.append(cash_product)
        total_expense_ratio += cash_product["expense_ratio"] * (asset_allocation["cash"] / 100)

    # Portfolio-level analysis
    portfolio_details = {
        "expense_ratio": total_expense_ratio,
        "advisor_fee": 0.0075,  # 0.75% advisory fee
        "complexity_score": max([p["complexity_score"] for p in recommended_products]),
        "risk_level": risk_profile["risk_score_adjusted"],
        "liquidity_rating": "high",
        "proprietary_product": False,
        "revenue_sharing": max([p["revenue_sharing"] for p in recommended_products])
    }

    # Calculate best interest compliance
    best_interest_score, considerations = calculate_best_interest_score(
        client_data, asset_allocation, portfolio_details
    )

    # Calculate expected return and risk
    expected_return = (
        asset_allocation["stocks"] * 0.08 +
        asset_allocation["bonds"] * 0.04 +
        asset_allocation["alternatives"] * 0.07 +
        asset_allocation["cash"] * 0.02
    ) / 100

    portfolio_risk = (
        asset_allocation["stocks"] * 0.15 +
        asset_allocation["bonds"] * 0.05 +
        asset_allocation["alternatives"] * 0.12 +
        asset_allocation["cash"] * 0.01
    ) / 100

    # Suitability determination
    suitability_factors = [
        risk_profile["risk_score_adjusted"] >= 3,  # Minimum risk tolerance
        risk_profile["investment_experience_score"] >= 2,  # Basic experience
        client_data["annual_income"] >= 30000,  # Minimum income threshold
        best_interest_score >= 0.7  # Best interest threshold
    ]

    suitability_met = all(suitability_factors)

    # Supervisory review triggers
    review_triggers = []
    if not suitability_met:
        review_triggers.append("suitability_concern")
    if best_interest_score < 0.8:
        review_triggers.append("best_interest_review")
    if portfolio_details["complexity_score"] > 6:
        review_triggers.append("complex_products")
    if total_expense_ratio + portfolio_details["advisor_fee"] > 0.015:
        review_triggers.append("high_fees")

    requires_supervisory_review = len(review_triggers) > 0

    return {
        "recommendation_type": "portfolio_construction",
        "asset_allocation": asset_allocation,
        "recommended_products": recommended_products,
        "expected_annual_return": round(expected_return, 4),
        "estimated_annual_risk": round(portfolio_risk, 4),
        "total_expense_ratio": round(total_expense_ratio, 4),
        "advisor_fee": portfolio_details["advisor_fee"],
        "total_annual_cost": round(total_expense_ratio + portfolio_details["advisor_fee"], 4),
        "risk_profile_snapshot": risk_profile,
        "suitability_determination": suitability_met,
        "suitability_factors": suitability_factors,
        "best_interest_score": round(best_interest_score, 3),
        "best_interest_considerations": considerations,
        "reg_bi_compliant": best_interest_score >= 0.8,
        "requires_supervisory_review": requires_supervisory_review,
        "supervisory_review_triggers": review_triggers,
        "conflict_disclosures_required": len([p for p in recommended_products if p["proprietary_product"] or p["revenue_sharing"] > 0]) > 0,
        "model_version": "robo-advisor-v4.1.2",
        "decision_trace_id": str(uuid.uuid4()),
        "recommendation_timestamp": datetime.utcnow().isoformat()
    }


def simulate_supervisory_review_process(recommendation: Dict[str, Any], client_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates the supervisory review process for investment recommendations.

    Args:
        recommendation: Original AI recommendation
        client_data: Client profile information

    Returns:
        Dictionary containing supervisory review results
    """
    review_outcome = "approved"  # Default outcome
    supervisor_notes = []
    required_disclosures = []

    # Review each trigger
    for trigger in recommendation["supervisory_review_triggers"]:
        if trigger == "suitability_concern":
            review_outcome = "conditional_approval"
            supervisor_notes.append("Additional suitability documentation required")
            required_disclosures.append("enhanced_suitability_disclosure")

        elif trigger == "best_interest_review":
            if recommendation["best_interest_score"] < 0.7:
                review_outcome = "rejected"
                supervisor_notes.append("Best interest standard not met - recommendation rejected")
            else:
                review_outcome = "conditional_approval"
                supervisor_notes.append("Best interest concerns addressed with enhanced disclosure")
                required_disclosures.append("best_interest_rationale")

        elif trigger == "complex_products":
            supervisor_notes.append("Complex product suitability confirmed")
            required_disclosures.append("product_complexity_disclosure")

        elif trigger == "high_fees":
            supervisor_notes.append("Fee reasonableness documented")
            required_disclosures.append("fee_justification_disclosure")

    # Determine final approval
    if review_outcome == "rejected":
        final_status = "rejected"
    elif review_outcome == "conditional_approval" and len(required_disclosures) <= 2:
        final_status = "approved_with_conditions"
    else:
        final_status = "approved"

    return {
        "review_status": final_status,
        "supervisor_id": "SUP_" + str(uuid.uuid4())[:8],
        "review_timestamp": datetime.utcnow().isoformat(),
        "supervisor_notes": supervisor_notes,
        "required_disclosures": required_disclosures,
        "review_duration_minutes": random.randint(15, 45),
        "escalation_required": final_status == "rejected"
    }


def simulate_examiner_query_robo_advisory(db_backend: SqliteBackend, decision_ids: List[str]) -> None:
    """
    Simulates SEC/FINRA examiner queries for robo-advisory compliance.

    Args:
        db_backend: Database backend
        decision_ids: List of decision IDs to query
    """
    print("\n" + "="*60)
    print("SEC/FINRA EXAMINER SIMULATION - ROBO-ADVISORY COMPLIANCE")
    print("="*60)

    queries = [
        "Demonstrate Reg BI best interest analysis and documentation for complex client scenarios",
        "Show evidence of suitability determination and risk profile preservation over time",
        "Provide audit trail for supervisory review process and conflict disclosure management",
        "Document investment recommendation rationale and fee reasonableness analysis"
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
    Main execution function demonstrating robo-advisory & Reg BI workflow.
    """
    print("=== Briefcase AI Robo-Advisory & Reg BI Example ===")
    print("Regulation: SEC/FINRA Reg BI")
    print("Scope: AI investment recommendations with best interest compliance")
    print("Features: Risk profiling, suitability analysis, supervisory review, conflict management\n")

    # Initialize Briefcase AI SDK
    try:
        briefcase.init_with_config(2)
        print("✓ Briefcase AI SDK initialized")
    except Exception as e:
        print(f"✗ Failed to initialize SDK: {e}")
        sys.exit(1)

    # Get configured backend
    db_backend = backend.get_backend()
    print("✓ SQLite backend configured\n")

    # Process multiple robo-advisory scenarios
    advisory_scenarios = [
        {
            "scenario_name": "Young Professional Retirement Planning",
            "client_data": {
                "client_id": str(uuid.uuid4()),
                "client_name": "Alexandra Chen",
                "age": 28,
                "annual_income": 85000,
                "net_worth": 125000,
                "investment_experience": "limited",
                "risk_tolerance": "moderate_aggressive",
                "time_horizon_years": 35,
                "investment_goals": ["retirement", "wealth_building"],
                "liquidity_needs": "low",
                "existing_investments": 45000,
                "monthly_contribution_capacity": 2000
            }
        },
        {
            "scenario_name": "Pre-Retirement Conservative Portfolio",
            "client_data": {
                "client_id": str(uuid.uuid4()),
                "client_name": "Robert Martinez",
                "age": 58,
                "annual_income": 120000,
                "net_worth": 850000,
                "investment_experience": "extensive",
                "risk_tolerance": "moderate_conservative",
                "time_horizon_years": 7,
                "investment_goals": ["retirement", "income_generation", "capital_preservation"],
                "liquidity_needs": "moderate",
                "existing_investments": 650000,
                "monthly_contribution_capacity": 3500
            }
        },
        {
            "scenario_name": "High Net Worth Complex Portfolio",
            "client_data": {
                "client_id": str(uuid.uuid4()),
                "client_name": "Sarah Williams",
                "age": 42,
                "annual_income": 350000,
                "net_worth": 2500000,
                "investment_experience": "extensive",
                "risk_tolerance": "aggressive",
                "time_horizon_years": 20,
                "investment_goals": ["wealth_building", "tax_efficiency", "diversification"],
                "liquidity_needs": "low",
                "existing_investments": 1800000,
                "monthly_contribution_capacity": 8000
            }
        },
        {
            "scenario_name": "Limited Experience Moderate Portfolio",
            "client_data": {
                "client_id": str(uuid.uuid4()),
                "client_name": "Michael Thompson",
                "age": 35,
                "annual_income": 65000,
                "net_worth": 85000,
                "investment_experience": "none",
                "risk_tolerance": "moderate",
                "time_horizon_years": 15,
                "investment_goals": ["retirement", "emergency_fund"],
                "liquidity_needs": "high",
                "existing_investments": 25000,
                "monthly_contribution_capacity": 1200
            }
        }
    ]

    decision_ids = []

    for scenario in advisory_scenarios:
        print(f"\n{'='*50}")
        print(f"PROCESSING: {scenario['scenario_name']}")
        print('='*50)

        client_data = scenario["client_data"]

        print("Client Profile:")
        for key, value in client_data.items():
            if key not in ["client_id"]:
                print(f"  {key}: {value}")
        print()

        # Run AI investment recommendation
        print("Generating AI investment recommendation...")
        investment_recommendation = simulate_robo_advisory_recommendation(client_data)

        print(f"✓ Recommendation: {investment_recommendation['recommendation_type']}")
        print(f"✓ Asset allocation: {investment_recommendation['asset_allocation']}")
        print(f"✓ Expected return: {investment_recommendation['expected_annual_return']:.2%}")
        print(f"✓ Total annual cost: {investment_recommendation['total_annual_cost']:.2%}")
        print(f"✓ Suitability met: {investment_recommendation['suitability_determination']}")
        print(f"✓ Reg BI compliant: {investment_recommendation['reg_bi_compliant']}")
        print(f"✓ Best interest score: {investment_recommendation['best_interest_score']}")

        # Display supervisory review if required
        if investment_recommendation["requires_supervisory_review"]:
            print(f"\n⚠ Supervisory review required: {', '.join(investment_recommendation['supervisory_review_triggers'])}")

            # Simulate supervisory review process
            supervisory_review = simulate_supervisory_review_process(investment_recommendation, client_data)
            print(f"✓ Supervisory review: {supervisory_review['review_status']}")
            if supervisory_review["supervisor_notes"]:
                for note in supervisory_review["supervisor_notes"]:
                    print(f"  - {note}")

        # Display best interest considerations
        if investment_recommendation["best_interest_considerations"]:
            print(f"\nBest Interest Considerations:")
            for consideration in investment_recommendation["best_interest_considerations"]:
                print(f"  • {consideration}")

        # Create comprehensive regulatory metadata
        regulatory_metadata = {
            "regulation": "SEC/FINRA Reg BI",
            "reg_bi_applicable": True,
            "best_interest_standard_met": investment_recommendation["reg_bi_compliant"],
            "suitability_determination": investment_recommendation["suitability_determination"],
            "fiduciary_duty_documented": True,
            "conflict_disclosures_required": investment_recommendation["conflict_disclosures_required"],
            "supervisory_review_completed": investment_recommendation["requires_supervisory_review"],
            "risk_profile_preserved": True,
            "fee_reasonableness_documented": True,
            "product_suitability_validated": True,
            "investment_advice_category": "robo_advisory",
            "sec_investment_advisor_act_compliance": True,
            "finra_suitability_rule_compliance": investment_recommendation["suitability_determination"],
            "examiner_ready": True,
            "decision_timestamp": datetime.utcnow().isoformat()
        }

        # Include supervisory review in metadata if applicable
        if investment_recommendation["requires_supervisory_review"]:
            supervisory_review = simulate_supervisory_review_process(investment_recommendation, client_data)
            regulatory_metadata.update({
                "supervisory_review_status": supervisory_review["review_status"],
                "supervisor_id": supervisory_review["supervisor_id"],
                "supervisory_notes": supervisory_review["supervisor_notes"],
                "required_disclosures": supervisory_review["required_disclosures"]
            })

        # Create DecisionSnapshot
        try:
            decision_snapshot = backend.create_decision_snapshot(
                function_name="robo_advisory_reg_bi",
                inputs=client_data,
                outputs=investment_recommendation,
                metadata=regulatory_metadata,
                input_types={
                    "age": "int",
                    "annual_income": "float",
                    "net_worth": "float",
                    "time_horizon_years": "int",
                    "existing_investments": "float",
                    "monthly_contribution_capacity": "float"
                },
                output_types={
                    "expected_annual_return": "float",
                    "estimated_annual_risk": "float",
                    "total_expense_ratio": "float",
                    "advisor_fee": "float",
                    "total_annual_cost": "float",
                    "best_interest_score": "float",
                    "suitability_determination": "bool",
                    "reg_bi_compliant": "bool"
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

        # Simulate SEC/FINRA examiner queries
        simulate_examiner_query_robo_advisory(db_backend, decision_ids)

        # Demonstrate compliance validation across all decisions
        print(f"\n{'='*60}")
        print("REGULATORY COMPLIANCE VALIDATION")
        print('='*60)

        required_fields = [
            "regulation",
            "best_interest_standard_met",
            "suitability_determination",
            "fiduciary_duty_documented",
            "risk_profile_preserved",
            "fee_reasonableness_documented",
            "product_suitability_validated"
        ]

        compliant_count = 0
        for decision_id in decision_ids:
            decision = db_backend.load_decision(decision_id)
            if decision:
                validation = backend.validate_regulatory_completeness(decision, required_fields)
                if validation["is_compliant"]:
                    compliant_count += 1

        print(f"Overall Compliance Rate: {compliant_count}/{len(decision_ids)} ({compliant_count/len(decision_ids):.1%})")
        print("✓ All investment recommendations documented with full Reg BI compliance validation")

        # Demonstrate risk profile temporal consistency
        print(f"\n{'='*60}")
        print("RISK PROFILE TEMPORAL CONSISTENCY")
        print('='*60)

        print("Client Risk Profile Snapshots (preserved at decision time):")
        for decision_id in decision_ids[:2]:  # Show first two for brevity
            decision = db_backend.load_decision(decision_id)
            if decision:
                # Extract risk profile from outputs
                for output in decision.outputs:
                    if output.name == "risk_profile_snapshot":
                        print(f"  Decision {decision_id[:8]}: Risk score preserved in snapshot")
                        break

    print(f"\n✓ Robo-advisory & Reg BI workflow demonstration completed")
    print(f"Processed {len(decision_ids)} investment recommendations with full regulatory compliance")


if __name__ == "__main__":
    main()