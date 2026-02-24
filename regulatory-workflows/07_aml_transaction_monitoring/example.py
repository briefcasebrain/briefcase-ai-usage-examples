#!/usr/bin/env python3
"""
Briefcase AI Example: AML Transaction Monitoring & SAR Filing

Context: FinCEN/OCC examination. Rules engine + ML model generates alerts for
analyst review. Analysts clear alerts or file SARs with FinCEN. Rule or threshold
change mid-year creates retroactive exam liability.

Demonstrates:
- AML alert generation with rule version tracking
- Mid-year threshold change impact tracking
- SAR filing decision audit trail
- OCC/FinCEN examination readiness
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
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


def simulate_aml_alert_scoring(transaction_data: Dict[str, Any], rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates AML alert generation and scoring.

    Args:
        transaction_data: Transaction details
        rule_config: AML rule configuration and thresholds

    Returns:
        Dictionary containing alert decision and scoring
    """
    transaction_amount = transaction_data["transaction_amount"]
    transaction_type = transaction_data["transaction_type"]
    alert_rule_id = transaction_data["alert_rule_id"]

    # Base alert score calculation
    alert_score = 0.0

    # Amount-based scoring
    if alert_rule_id == "large_cash_transaction":
        # $10K+ cash transactions (CTR threshold)
        if transaction_amount >= 10000:
            alert_score = min(1.0, transaction_amount / 50000)
    elif alert_rule_id == "structuring_pattern":
        # Multiple transactions just under $10K
        if transaction_amount >= 9000 and transaction_amount < 10000:
            alert_score = 0.7 + random.uniform(0.0, 0.2)
    elif alert_rule_id == "wire_to_high_risk_country":
        # International wires to high-risk countries
        if transaction_type == "wire" and transaction_amount > 5000:
            alert_score = 0.6 + random.uniform(0.0, 0.3)

    # Add randomness to simulate complex rule interactions
    alert_score += random.uniform(-0.05, 0.1)
    alert_score = max(0.0, min(1.0, alert_score))

    # Apply threshold from rule configuration
    threshold = rule_config["alert_thresholds"][alert_rule_id]

    # Generate alert if score exceeds threshold
    if alert_score >= threshold:
        return {
            "alert_generated": True,
            "alert_score": round(alert_score, 3),
            "threshold_at_alert_time": threshold,
            "alert_rule_version": rule_config["version"]
        }
    else:
        return {
            "alert_generated": False,
            "alert_score": round(alert_score, 3),
            "threshold_at_alert_time": threshold,
            "alert_rule_version": rule_config["version"]
        }


def simulate_analyst_review(alert_data: Dict[str, Any], transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates analyst review of an AML alert.

    Args:
        alert_data: Alert scoring information
        transaction_data: Original transaction data

    Returns:
        Dictionary containing analyst decision
    """
    alert_score = alert_data["alert_score"]
    transaction_amount = transaction_data["transaction_amount"]

    # Simulate analyst decision-making
    if alert_score >= 0.8 and transaction_amount >= 25000:
        # High-risk, large amount → file SAR
        decision = "file_sar"
        sar_filed = True
        sar_id = f"SAR-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        rationale = f"High-risk transaction: Score {alert_score}, Amount ${transaction_amount:,.0f}"
    elif alert_score >= 0.5:
        # Medium risk → additional monitoring but clear for now
        decision = "clear"
        sar_filed = False
        sar_id = None
        rationale = f"Medium risk cleared: Score {alert_score}, monitoring continues"
    else:
        # Low risk → clear
        decision = "clear"
        sar_filed = False
        sar_id = None
        rationale = f"Low risk cleared: Score {alert_score}"

    return {
        "analyst_decision": decision,
        "sar_filed": sar_filed,
        "sar_id": sar_id,
        "decision_rationale": rationale,
        "decision_timestamp": datetime.utcnow().isoformat(),
        "analyst_id": "analyst_" + str(random.randint(100, 999))
    }


def main():
    """
    Main execution function demonstrating AML transaction monitoring workflow.
    """
    print("=== Briefcase AI AML Transaction Monitoring Example ===")
    print("Regulation: BSA/AML / FinCEN SAR Requirements")
    print("Workflow: Alert generation, analyst review, and SAR filing audit trail\n")

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

    # AML Rule Configuration v4.1 (before threshold change)
    aml_rules_v41 = {
        "version": "aml-rules-v4.1",
        "alert_thresholds": {
            "large_cash_transaction": 0.5,
            "structuring_pattern": 0.6,
            "wire_to_high_risk_country": 0.7
        },
        "effective_date": datetime.utcnow() - timedelta(days=60)
    }

    print("="*70)
    print("TRANSACTION MONITORING (Rules v4.1)")
    print("="*70)

    # Process first transaction with rules v4.1
    alert_id_1 = str(uuid.uuid4())
    transaction_id_1 = str(uuid.uuid4())

    transaction_data_1 = {
        "alert_id": alert_id_1,
        "transaction_id": transaction_id_1,
        "customer_id": str(uuid.uuid4()),
        "transaction_amount": 27500.0,
        "transaction_type": "wire",
        "alert_rule_id": "wire_to_high_risk_country",
        "alert_rule_version": aml_rules_v41["version"],
        "analyst_id": "analyst_205"
    }

    print("Processing high-value wire transaction:")
    print(f"  Transaction ID: {transaction_id_1[:12]}...")
    print(f"  Amount: ${transaction_data_1['transaction_amount']:,.0f}")
    print(f"  Type: {transaction_data_1['transaction_type']}")
    print(f"  Rule: {transaction_data_1['alert_rule_id']}")
    print(f"  Rule Version: {aml_rules_v41['version']}")

    # Generate alert using rules v4.1
    alert_result_1 = simulate_aml_alert_scoring(transaction_data_1, aml_rules_v41)
    print(f"  SUCCESS: Alert score: {alert_result_1['alert_score']}")
    print(f"  SUCCESS: Threshold: {alert_result_1['threshold_at_alert_time']}")
    print(f"  SUCCESS: Alert generated: {alert_result_1['alert_generated']}")

    if alert_result_1["alert_generated"]:
        # Analyst review
        analyst_result_1 = simulate_analyst_review(alert_result_1, transaction_data_1)
        print(f"  SUCCESS: Analyst decision: {analyst_result_1['analyst_decision']}")
        if analyst_result_1["sar_filed"]:
            print(f"  SUCCESS: SAR filed: {analyst_result_1['sar_id']}")

        # Create decision snapshot
        regulatory_metadata_1 = {
            "regulation": "BSA/AML / FinCEN SAR Requirements",
            "rule_version_history_preserved": True,
            "mra_protection": True,
            "threshold_at_decision_time": alert_result_1["threshold_at_alert_time"]
        }

        snapshot_1 = backend.create_decision_snapshot(
            function_name="aml_alert_analysis",
            inputs=transaction_data_1,
            outputs={**alert_result_1, **analyst_result_1},
            metadata=regulatory_metadata_1
        )

        stored_id_1 = db_backend.save_decision(snapshot_1)
        print(f"  SUCCESS: Decision stored: {stored_id_1[:12]}...")

    # Simulate mid-year rule change
    print("\n" + "="*70)
    print("MID-YEAR RULE CHANGE (Rules v4.2)")
    print("="*70)

    # AML Rule Configuration v4.2 (after threshold change)
    aml_rules_v42 = {
        "version": "aml-rules-v4.2",
        "alert_thresholds": {
            "large_cash_transaction": 0.4,  # Lowered threshold (more sensitive)
            "structuring_pattern": 0.5,     # Lowered threshold
            "wire_to_high_risk_country": 0.6  # Lowered threshold
        },
        "effective_date": datetime.utcnow()
    }

    print("Rule configuration updated:")
    print(f"  Version: {aml_rules_v42['version']}")
    print("  Threshold changes:")
    for rule_id in aml_rules_v41["alert_thresholds"]:
        old_threshold = aml_rules_v41["alert_thresholds"][rule_id]
        new_threshold = aml_rules_v42["alert_thresholds"][rule_id]
        print(f"    {rule_id}: {old_threshold} → {new_threshold} ({new_threshold - old_threshold:+.1f})")

    # Process second transaction with rules v4.2
    alert_id_2 = str(uuid.uuid4())
    transaction_id_2 = str(uuid.uuid4())

    transaction_data_2 = {
        "alert_id": alert_id_2,
        "transaction_id": transaction_id_2,
        "customer_id": str(uuid.uuid4()),
        "transaction_amount": 15000.0,  # Lower amount than first transaction
        "transaction_type": "wire",
        "alert_rule_id": "wire_to_high_risk_country",
        "alert_rule_version": aml_rules_v42["version"],
        "analyst_id": "analyst_207"
    }

    print(f"\nProcessing wire transaction under new rules:")
    print(f"  Transaction ID: {transaction_id_2[:12]}...")
    print(f"  Amount: ${transaction_data_2['transaction_amount']:,.0f}")
    print(f"  Rule Version: {aml_rules_v42['version']}")

    # Generate alert using rules v4.2
    alert_result_2 = simulate_aml_alert_scoring(transaction_data_2, aml_rules_v42)
    print(f"  SUCCESS: Alert score: {alert_result_2['alert_score']}")
    print(f"  SUCCESS: New threshold: {alert_result_2['threshold_at_alert_time']}")
    print(f"  SUCCESS: Alert generated: {alert_result_2['alert_generated']}")

    if alert_result_2["alert_generated"]:
        analyst_result_2 = simulate_analyst_review(alert_result_2, transaction_data_2)
        print(f"  SUCCESS: Analyst decision: {analyst_result_2['analyst_decision']}")

        # Create decision snapshot
        regulatory_metadata_2 = {
            "regulation": "BSA/AML / FinCEN SAR Requirements",
            "rule_version_history_preserved": True,
            "mra_protection": True,
            "threshold_at_decision_time": alert_result_2["threshold_at_alert_time"]
        }

        snapshot_2 = backend.create_decision_snapshot(
            function_name="aml_alert_analysis",
            inputs=transaction_data_2,
            outputs={**alert_result_2, **analyst_result_2},
            metadata=regulatory_metadata_2
        )

        stored_id_2 = db_backend.save_decision(snapshot_2)
        print(f"  SUCCESS: Decision stored: {stored_id_2[:12]}...")

    # Simulate OCC/FinCEN examiner query
    print("\n" + "="*70)
    print("OCC/FINCEN EXAMINER SIMULATION")
    print("="*70)

    if 'stored_id_1' in locals() and alert_result_1.get("alert_generated"):
        sar_id = analyst_result_1.get("sar_id")
        examiner_query = f"What was the AML threshold in effect for rule {transaction_data_1['alert_rule_id']} at the time SAR {sar_id} was filed?"
        print(f"EXAMINER QUERY: {examiner_query}")

        examiner_response = backend.format_examiner_response(
            stored_id_1,
            examiner_query,
            db_backend
        )
        print(examiner_response)

        # Additional threshold verification
        retrieved_decision = db_backend.load_decision(stored_id_1)
        if retrieved_decision:
            threshold_at_decision = retrieved_decision.tags.get("threshold_at_decision_time")
            rule_version = None
            for inp in retrieved_decision.inputs:
                if inp.name == "alert_rule_version":
                    rule_version = inp.value
                    break

            print(f"THRESHOLD VERIFICATION:")
            print(f"  Rule Version at SAR Filing: {rule_version}")
            print(f"  Threshold in Effect: {threshold_at_decision}")
            print(f"  Current Threshold (v4.2): {aml_rules_v42['alert_thresholds']['wire_to_high_risk_country']}")

    # Demonstrate rule version impact analysis
    print("="*70)
    print("RULE VERSION IMPACT ANALYSIS")
    print("="*70)

    print("IMPACT OF THRESHOLD CHANGES:")
    print("- Transaction 1 under v4.1 rules:")
    if 'alert_result_1' in locals():
        print(f"  Amount: ${transaction_data_1['transaction_amount']:,.0f}")
        print(f"  Threshold: {alert_result_1['threshold_at_alert_time']}")
        print(f"  Alert: {alert_result_1['alert_generated']}")

    print("- Transaction 2 under v4.2 rules:")
    if 'alert_result_2' in locals():
        print(f"  Amount: ${transaction_data_2['transaction_amount']:,.0f}")
        print(f"  Threshold: {alert_result_2['threshold_at_alert_time']}")
        print(f"  Alert: {alert_result_2['alert_generated']}")

    print("\nSUCCESS: Rule version changes tracked immutably")
    print("SUCCESS: Historical threshold reconstruction available")

    # Regulatory compliance validation
    print("="*70)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*70)

    if 'stored_id_1' in locals():
        sample_decision = db_backend.load_decision(stored_id_1)

        required_aml_fields = [
            "regulation",
            "rule_version_history_preserved",
            "mra_protection",
            "threshold_at_decision_time"
        ]

        validation_result = backend.validate_regulatory_completeness(
            sample_decision,
            required_aml_fields
        )

        print(f"AML Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
        print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

        if validation_result['missing_fields']:
            print(f"Missing Fields: {', '.join(validation_result['missing_fields'])}")

    # Summary of capabilities
    print("="*70)
    print("BRIEFCASE AI VALUE FOR AML MONITORING")
    print("="*70)
    print("SUCCESS: Complete rule version history preservation")
    print("SUCCESS: Threshold-in-effect tracking for each alert")
    print("SUCCESS: SAR filing audit trail with decision rationale")
    print("SUCCESS: MRA (Matter Requiring Attention) protection")
    print("SUCCESS: OCC/FinCEN examination readiness")

    decision_ids = []
    if 'stored_id_1' in locals():
        decision_ids.append(stored_id_1)
    if 'stored_id_2' in locals():
        decision_ids.append(stored_id_2)

    print(f"\nSUCCESS: AML transaction monitoring audit trail demonstration completed")
    print(f"Decisions stored: {len(decision_ids)}")
    print(f"Rule versions tracked: v4.1, v4.2")


if __name__ == "__main__":
    main()