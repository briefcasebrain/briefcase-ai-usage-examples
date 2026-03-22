#!/usr/bin/env python3
"""
Briefcase AI Example: Algorithmic Trading & Market Surveillance

Context: SEC Rule 17a-4 (all orders and business records must be retained).
FINRA surveillance monitors for spoofing and layering under Dodd-Frank § 747.
Decision must be made and executed in milliseconds.

Demonstrates:
- Millisecond-precision order generation audit trail
- Spoofing pattern detection and investigation support
- SEC Rule 17a-4 business records compliance
- Complete order book reconstruction capability
"""

import sys
import os
import uuid
import random
import time
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


def simulate_trading_algorithm_decision(market_data: Dict[str, Any], algo_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates a high-frequency trading algorithm order decision.

    Args:
        market_data: Current market signal data
        algo_config: Algorithm version and risk parameters

    Returns:
        Dictionary containing order decision
    """
    start_time = time.time()

    signal_value = market_data["signal_value"]
    signal_type = market_data["market_signal_type"]
    instrument = market_data["instrument"]
    max_position = algo_config["max_position_limit"]

    # Simple momentum-based algorithm simulation
    if signal_type == "momentum":
        if signal_value > 0.7:
            # Strong upward momentum leads to Buy
            order_action = "submit"
            order_quantity = min(100, int(max_position * 0.1))
            order_type = "limit"
            # Set limit price slightly above current (simulated)
            limit_price = 150.0 + (signal_value * 2)
        elif signal_value < -0.7:
            # Strong downward momentum leads to Sell
            order_action = "submit"
            order_quantity = -min(100, int(max_position * 0.1))
            order_type = "limit"
            limit_price = 150.0 + (signal_value * 2)
        else:
            # Weak signal leads to No action
            order_action = "no_action"
            order_quantity = 0
            order_type = None
            limit_price = None

    elif signal_type == "mean_reversion":
        # Mean reversion strategy
        if abs(signal_value) > 0.5:
            order_action = "submit"
            # Trade against the signal
            order_quantity = -int(signal_value * 50)
            order_type = "market"
            limit_price = None
        else:
            order_action = "no_action"
            order_quantity = 0
            order_type = None
            limit_price = None

    else:
        order_action = "no_action"
        order_quantity = 0
        order_type = None
        limit_price = None

    # Simulate execution (if order submitted)
    execution_price = None
    if order_action == "submit":
        # Simulate partial or full execution
        if random.random() > 0.3:  # 70% fill rate
            execution_price = limit_price if limit_price else (150.0 + random.uniform(-0.5, 0.5))

    # Calculate latency
    end_time = time.time()
    latency_ms = int((end_time - start_time) * 1000000)  # Microseconds to simulate HFT

    return {
        "order_action": order_action,
        "order_quantity": order_quantity,
        "order_type": order_type,
        "limit_price": limit_price,
        "execution_price": execution_price,
        "execution_timestamp": datetime.utcnow().isoformat(),
        "execution_latency_ms": max(1, latency_ms // 1000),  # Convert to milliseconds
        "order_record_type": "new_order"
    }


def create_spoofing_pattern_simulation() -> List[Dict[str, Any]]:
    """
    Creates a sequence of orders that could indicate spoofing behavior.
    Used to demonstrate surveillance capabilities.

    Returns:
        List of order dictionaries representing a potential spoofing pattern
    """
    base_time = datetime.utcnow()
    orders = []

    # Pattern: Submit 4 large orders, cancel them, then execute 1 small order
    # This is a classic spoofing indicator

    for i in range(4):
        # Large limit orders that will be cancelled
        order_time = base_time + timedelta(microseconds=i * 1000)
        market_data = {
            "order_id": str(uuid.uuid4()),
            "instrument": "AAPL",
            "market_signal_type": "layering_pattern",
            "signal_value": 0.8,
            "signal_timestamp": order_time.isoformat(),
            "algo_version": "sor-v12.4.1",
            "risk_config_version": "risk-config-v8.2.3",
            "max_position_limit": 10000.0,
            "order_quantity": 500,  # Large order
            "order_type": "limit",
            "limit_price": 152.50,
            "intended_action": "cancel_after_submission"
        }

        # These will be submitted then cancelled
        order_result = {
            "order_action": "submit",
            "order_quantity": 500,
            "order_type": "limit",
            "limit_price": 152.50,
            "execution_price": None,  # Not executed
            "execution_timestamp": order_time.isoformat(),
            "execution_latency_ms": random.randint(5, 25),
            "order_record_type": "new_order",
            "subsequent_action": "cancel",
            "cancel_timestamp": (order_time + timedelta(milliseconds=100)).isoformat()
        }

        orders.append((market_data, order_result))

    # Final order: Small market order that actually executes
    final_time = base_time + timedelta(milliseconds=500)
    final_market_data = {
        "order_id": str(uuid.uuid4()),
        "instrument": "AAPL",
        "market_signal_type": "execution_after_layering",
        "signal_value": 0.3,
        "signal_timestamp": final_time.isoformat(),
        "algo_version": "sor-v12.4.1",
        "risk_config_version": "risk-config-v8.2.3",
        "max_position_limit": 10000.0,
        "order_quantity": 50,  # Much smaller order
        "order_type": "market",
        "limit_price": None
    }

    final_order_result = {
        "order_action": "submit",
        "order_quantity": 50,
        "order_type": "market",
        "limit_price": None,
        "execution_price": 152.25,  # Executed
        "execution_timestamp": final_time.isoformat(),
        "execution_latency_ms": 15,
        "order_record_type": "new_order",
        "subsequent_action": "executed"
    }

    orders.append((final_market_data, final_order_result))

    return orders


def main():
    """
    Main execution function demonstrating algorithmic trading surveillance workflow.
    """
    print("=== Briefcase AI Algorithmic Trading Surveillance Example ===")
    print("Regulation: SEC Rule 17a-4 / FINRA Rule 4370 / Dodd-Frank § 747")
    print("Workflow: High-frequency order audit trail with spoofing detection\n")

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

    # Normal trading example
    print("="*80)
    print("NORMAL TRADING ALGORITHM EXECUTION")
    print("="*80)

    # Simulate normal market signal and order
    normal_market_data = {
        "order_id": str(uuid.uuid4()),
        "instrument": "AAPL",
        "market_signal_type": "momentum",
        "signal_value": 0.85,
        "signal_timestamp": datetime.utcnow().isoformat(),
        "algo_version": "sor-v12.4.1",
        "risk_config_version": "risk-config-v8.2.3",
        "max_position_limit": 10000.0
    }

    algo_config = {
        "max_position_limit": normal_market_data["max_position_limit"],
        "version": normal_market_data["algo_version"]
    }

    print("Processing market signal:")
    print(f"  Instrument: {normal_market_data['instrument']}")
    print(f"  Signal Type: {normal_market_data['market_signal_type']}")
    print(f"  Signal Value: {normal_market_data['signal_value']}")
    print(f"  Algorithm: {normal_market_data['algo_version']}")

    # Execute trading algorithm
    order_result = simulate_trading_algorithm_decision(normal_market_data, algo_config)
    print(f"  SUCCESS: Order action: {order_result['order_action']}")
    print(f"  SUCCESS: Order quantity: {order_result['order_quantity']}")
    print(f"  SUCCESS: Execution latency: {order_result['execution_latency_ms']}ms")

    if order_result["execution_price"]:
        print(f"  SUCCESS: Executed at: ${order_result['execution_price']:.2f}")

    # Create decision snapshot for normal order
    regulatory_metadata = {
        "regulation": "SEC Rule 17a-4 / FINRA Rule 4370 / Dodd-Frank § 747",
        "record_type": "business_records_17a4",
        "spoofing_layering_defensible": True,
        "order_book_reconstructable": True
    }

    normal_snapshot = backend.create_decision_snapshot(
        function_name="algorithmic_order_generation",
        inputs=normal_market_data,
        outputs=order_result,
        metadata=regulatory_metadata
    )

    normal_stored_id = db_backend.save_decision(normal_snapshot)
    print(f"  SUCCESS: Order record stored: {normal_stored_id[:12]}...")

    # Spoofing pattern simulation
    print("\n" + "="*80)
    print("SPOOFING PATTERN SIMULATION")
    print("="*80)

    print("Generating suspicious order pattern:")
    print("- 4 large limit orders (to be cancelled)")
    print("- 1 small market order (actual execution)")
    print("This pattern may indicate spoofing behavior\n")

    spoofing_orders = create_spoofing_pattern_simulation()
    spoofing_decision_ids = []

    for i, (market_data, order_result) in enumerate(spoofing_orders):
        print(f"Order {i+1}:")
        print(f"  ID: {market_data['order_id'][:12]}...")
        print(f"  Quantity: {order_result['order_quantity']}")
        print(f"  Type: {order_result['order_type']}")
        print(f"  Action: {order_result.get('subsequent_action', 'pending')}")

        if order_result.get("execution_price"):
            print(f"  Executed: ${order_result['execution_price']:.2f}")

        # Create snapshot for each order
        spoofing_metadata = {
            "regulation": "SEC Rule 17a-4 / FINRA Rule 4370 / Dodd-Frank § 747",
            "record_type": "business_records_17a4",
            "spoofing_layering_defensible": True,
            "order_book_reconstructable": True,
            "pattern_sequence_number": i + 1,
            "total_pattern_orders": len(spoofing_orders),
            "surveillance_flag": i < 4  # Flag first 4 orders as suspicious
        }

        snapshot = backend.create_decision_snapshot(
            function_name="algorithmic_order_generation",
            inputs=market_data,
            outputs=order_result,
            metadata=spoofing_metadata
        )

        stored_id = db_backend.save_decision(snapshot)
        spoofing_decision_ids.append(stored_id)
        print(f"  SUCCESS: Stored: {stored_id[:12]}...")
        print()

    # Simulate FINRA inquiry
    print("="*80)
    print("FINRA SURVEILLANCE INQUIRY SIMULATION")
    print("="*80)

    time_start = spoofing_orders[0][0]["signal_timestamp"]
    time_end = spoofing_orders[-1][0]["signal_timestamp"]
    order_ids_str = ", ".join([oid[:8] + "..." for oid in spoofing_decision_ids])

    finra_query = f"Explain the pattern of orders {order_ids_str} executed by your algorithm between {time_start} and {time_end}."
    print(f"FINRA INQUIRY: {finra_query}")
    print()

    # Retrieve and analyze all orders in the pattern
    print("ORDER BOOK RECONSTRUCTION:")
    print("-" * 50)

    for i, decision_id in enumerate(spoofing_decision_ids):
        retrieved = db_backend.load_decision(decision_id)
        if retrieved:
            order_action = None
            quantity = None
            order_type = None
            execution_price = None
            algo_version = None

            for inp in retrieved.inputs:
                if inp.name == "algo_version":
                    algo_version = inp.value

            for out in retrieved.outputs:
                if out.name == "order_action":
                    order_action = out.value
                elif out.name == "order_quantity":
                    quantity = out.value
                elif out.name == "order_type":
                    order_type = out.value
                elif out.name == "execution_price":
                    execution_price = out.value

            surveillance_flag = retrieved.tags.get("surveillance_flag", False)
            flag_indicator = " WARNING: SURVEILLANCE FLAG" if surveillance_flag else " SUCCESS: EXECUTED"

            print(f"Order {i+1}: {order_action} {quantity} shares ({order_type})")
            print(f"  Algorithm: {algo_version}")
            print(f"  Execution: {execution_price if execution_price else 'Not executed'}{flag_indicator}")

    # Pattern analysis
    print("\n" + "="*80)
    print("PATTERN ANALYSIS")
    print("="*80)

    flagged_orders = sum(1 for oid in spoofing_decision_ids if db_backend.load_decision(oid).tags.get("surveillance_flag", False))
    executed_orders = sum(1 for oid in spoofing_decision_ids if any(out.value for out in db_backend.load_decision(oid).outputs if out.name == "execution_price"))

    print(f"Total orders in pattern: {len(spoofing_decision_ids)}")
    print(f"Orders flagged for surveillance: {flagged_orders}")
    print(f"Orders actually executed: {executed_orders}")
    print(f"Pattern classification: {'POTENTIAL SPOOFING' if flagged_orders > executed_orders else 'LEGITIMATE TRADING'}")

    print("\nAUDIT TRAIL COMPLETENESS:")
    print("SUCCESS: All order decisions preserved with exact algorithm version")
    print("SUCCESS: Risk configuration documented per order")
    print("SUCCESS: Complete order book reconstruction available")
    print("SUCCESS: Surveillance flags maintained for investigation")

    # Regulatory compliance validation
    print("="*80)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*80)

    sample_decision = db_backend.load_decision(spoofing_decision_ids[0])

    required_trading_fields = [
        "regulation",
        "record_type",
        "spoofing_layering_defensible",
        "order_book_reconstructable"
    ]

    validation_result = backend.validate_regulatory_completeness(
        sample_decision,
        required_trading_fields
    )

    print(f"Trading Compliance Status: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Fields: {', '.join(validation_result['missing_fields'])}")

    # Summary
    print("="*80)
    print("BRIEFCASE AI VALUE FOR ALGORITHMIC TRADING")
    print("="*80)
    print("SUCCESS: Millisecond-precision order decision audit trail")
    print("SUCCESS: Complete algorithm version and risk config preservation")
    print("SUCCESS: Spoofing/layering pattern detection support")
    print("SUCCESS: SEC Rule 17a-4 business records compliance")
    print("SUCCESS: FINRA surveillance investigation readiness")

    all_decision_ids = [normal_stored_id] + spoofing_decision_ids
    print(f"\nSUCCESS: Algorithmic trading surveillance audit trail demonstration completed")
    print(f"Total order records: {len(all_decision_ids)}")
    print(f"Spoofing pattern orders: {len(spoofing_decision_ids)}")


if __name__ == "__main__":
    main()