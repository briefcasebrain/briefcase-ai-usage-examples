#!/usr/bin/env python3
"""
Briefcase AI Example: Consumer Fintech — High-Velocity Release Monitoring

Context: Sponsor bank audit readiness. Fintech ships 1–2 releases per week.
Bundled deploys can trigger cascading KYC failures across new user cohorts.
Current response is manual war room taking hours. Briefcase AI detects
cohort-level drift automatically and produces pre-packaged root cause analysis.

Demonstrates:
- Automated drift detection for high-velocity release cycles
- Cohort-level failure pattern recognition
- Pre-packaged RCA for sponsor bank compliance
- Real-time monitoring of KYC/onboarding performance
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


def simulate_kyc_onboarding_decision(user_data: Dict[str, Any], release_config: Dict[str, str]) -> Dict[str, Any]:
    """
    Simulates a KYC/onboarding AI decision for a fintech user.
    Performance varies by release version to demonstrate drift detection.

    Args:
        user_data: User onboarding data
        release_config: Release version and model configuration

    Returns:
        Dictionary containing KYC decision and performance metrics
    """
    release_version = release_config["release_version"]
    model_version = release_config["model_version"]

    # Extract user profile information
    document_type = user_data.get("document_type", "drivers_license")
    age = user_data.get("user_age", 25)
    device_quality = user_data.get("device_quality_score", 0.5)

    # Base KYC scoring
    confidence = 0.75

    # Document type impact
    if document_type == "passport":
        confidence += 0.15
    elif document_type == "drivers_license":
        confidence += 0.10
    elif document_type == "state_id":
        confidence += 0.05

    # Age-based scoring
    if age >= 25:
        confidence += 0.05
    elif age < 21:
        confidence -= 0.10

    # Device quality impact
    confidence += (device_quality - 0.5) * 0.3

    # Release-specific model behavior (simulate regression in v2.14.3)
    if release_version == "v2.14.2":
        # Stable release with good performance
        model_version = "kyc-v7.1"
        confidence *= 1.0  # No change
        failure_rate_multiplier = 1.0
    elif release_version == "v2.14.3":
        # Problematic release with model regression
        model_version = "kyc-v7.2"
        confidence *= 0.45  # Significant degradation
        failure_rate_multiplier = 4.0
    else:
        # Default behavior
        confidence *= 0.95
        failure_rate_multiplier = 1.2

    # Add randomness
    confidence += random.uniform(-0.05, 0.05)
    confidence = max(0.0, min(1.0, confidence))

    # Decision logic with release-specific failure rates
    pass_threshold = 0.70
    base_failure_chance = 0.05
    adjusted_failure_chance = min(0.90, base_failure_chance * failure_rate_multiplier)

    if confidence >= pass_threshold and random.random() > adjusted_failure_chance:
        result = "pass"
        failure_reason = None
    else:
        result = "fail"
        # Common failure reasons vary by release
        if release_version == "v2.14.3":
            failure_reasons = [
                "document_quality_insufficient",
                "face_match_confidence_low",
                "liveness_detection_failed",
                "document_authentication_error"
            ]
        else:
            failure_reasons = [
                "document_expired",
                "face_match_confidence_low",
                "duplicate_identity_detected"
            ]
        failure_reason = random.choice(failure_reasons)

    return {
        "kyc_result": result,
        "failure_reason": failure_reason,
        "confidence_score": round(confidence, 3),
        "model_version": model_version,
        "processing_time_ms": random.randint(800, 2200),
        "device_risk_score": round(1.0 - device_quality, 3),
        "onboarding_timestamp": datetime.utcnow().isoformat()
    }


def create_user_onboarding(session_num: int, release_version: str) -> Dict[str, Any]:
    """
    Creates simulated user onboarding session data.

    Args:
        session_num: Session number for unique identification
        release_version: Fintech release version

    Returns:
        Dictionary containing user session data
    """
    session_id = str(uuid.uuid4())

    # Simulate diverse user profiles
    profiles = [
        {
            "user_age": random.randint(22, 35),
            "document_type": "drivers_license",
            "device_quality_score": random.uniform(0.7, 0.9)
        },
        {
            "user_age": random.randint(18, 25),
            "document_type": "state_id",
            "device_quality_score": random.uniform(0.5, 0.8)
        },
        {
            "user_age": random.randint(26, 45),
            "document_type": "passport",
            "device_quality_score": random.uniform(0.8, 0.95)
        }
    ]

    profile = random.choice(profiles)

    return {
        "session_id": session_id,
        "release_version": release_version,
        "user_id_hash": f"user_{session_num}_{hash(session_id) % 10000}",
        "user_age": profile["user_age"],
        "document_type": profile["document_type"],
        "device_quality_score": profile["device_quality_score"],
        "onboarding_timestamp": datetime.utcnow().isoformat(),
        "user_agent": f"FinTechApp/{release_version} iOS/16.0",
        "geolocation_state": random.choice(["CA", "NY", "TX", "FL", "IL"])
    }


def analyze_cohort_performance(decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes cohort performance and detects anomalies for RCA generation.

    Args:
        decisions: List of decision records grouped by some criteria

    Returns:
        Dictionary containing cohort analysis and drift detection results
    """
    if not decisions:
        return {"error": "No decisions to analyze"}

    # Group by release version
    cohorts = {}
    for decision in decisions:
        release = decision.get("release_version", "unknown")
        if release not in cohorts:
            cohorts[release] = {
                "decisions": [],
                "pass_count": 0,
                "fail_count": 0,
                "total_count": 0,
                "confidence_scores": [],
                "processing_times": []
            }

        cohorts[release]["decisions"].append(decision)
        cohorts[release]["total_count"] += 1

        # Extract decision result
        kyc_result = decision.get("kyc_result", "unknown")
        if kyc_result == "pass":
            cohorts[release]["pass_count"] += 1
        elif kyc_result == "fail":
            cohorts[release]["fail_count"] += 1

        # Extract metrics
        confidence = decision.get("confidence_score", 0.0)
        processing_time = decision.get("processing_time_ms", 0)

        cohorts[release]["confidence_scores"].append(confidence)
        cohorts[release]["processing_times"].append(processing_time)

    # Calculate cohort statistics
    cohort_stats = {}
    for release, data in cohorts.items():
        total = data["total_count"]
        if total > 0:
            failure_rate = data["fail_count"] / total
            avg_confidence = sum(data["confidence_scores"]) / len(data["confidence_scores"])
            avg_processing_time = sum(data["processing_times"]) / len(data["processing_times"])

            cohort_stats[release] = {
                "total_decisions": total,
                "failure_rate": round(failure_rate, 3),
                "pass_rate": round((total - data["fail_count"]) / total, 3),
                "avg_confidence": round(avg_confidence, 3),
                "avg_processing_time_ms": round(avg_processing_time),
                "decisions": data["decisions"]
            }

    # Detect anomalies
    anomalies = []
    if len(cohort_stats) >= 2:
        releases = list(cohort_stats.keys())
        releases.sort()

        for i in range(1, len(releases)):
            current = cohort_stats[releases[i]]
            previous = cohort_stats[releases[i-1]]

            # Detect significant failure rate increase
            failure_rate_increase = current["failure_rate"] - previous["failure_rate"]
            if failure_rate_increase > 0.20:  # 20% increase threshold
                anomalies.append({
                    "type": "failure_rate_spike",
                    "severity": "high",
                    "release": releases[i],
                    "previous_release": releases[i-1],
                    "failure_rate_change": f"+{failure_rate_increase:.1%}",
                    "current_failure_rate": f"{current['failure_rate']:.1%}",
                    "previous_failure_rate": f"{previous['failure_rate']:.1%}"
                })

            # Detect confidence drop
            confidence_drop = previous["avg_confidence"] - current["avg_confidence"]
            if confidence_drop > 0.20:  # 20% drop threshold
                anomalies.append({
                    "type": "confidence_degradation",
                    "severity": "high",
                    "release": releases[i],
                    "previous_release": releases[i-1],
                    "confidence_drop": round(confidence_drop, 3),
                    "current_confidence": current["avg_confidence"],
                    "previous_confidence": previous["avg_confidence"]
                })

    return {
        "cohort_stats": cohort_stats,
        "anomalies": anomalies,
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "drift_detected": len(anomalies) > 0
    }


def main():
    """
    Main execution function demonstrating fintech release monitoring workflow.
    """
    print("=== Briefcase AI Fintech Release Monitoring Example ===")
    print("Regulation: Sponsor Bank Audit Readiness")
    print("Workflow: Automated drift detection with pre-packaged RCA for high-velocity releases\n")

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

    print("="*85)
    print("RELEASE v2.14.2 - BASELINE PERFORMANCE")
    print("="*85)

    # Simulate stable release v2.14.2
    stable_release_config = {
        "release_version": "v2.14.2",
        "model_version": "kyc-v7.1",
        "deployment_timestamp": (datetime.utcnow() - timedelta(days=7)).isoformat(),
        "stability_status": "stable"
    }

    stable_decisions = []

    print(f"Processing onboarding sessions for release {stable_release_config['release_version']}:")

    for i in range(5):
        # Create user session
        user_data = create_user_onboarding(i, stable_release_config["release_version"])

        print(f"\nSession {i+1}:")
        print(f"  User ID: {user_data['user_id_hash']}")
        print(f"  Document: {user_data['document_type']}")
        print(f"  Device Quality: {user_data['device_quality_score']:.2f}")

        # Process KYC decision
        kyc_result = simulate_kyc_onboarding_decision(user_data, stable_release_config)
        print(f"  SUCCESS: KYC Result: {kyc_result['kyc_result']}")
        print(f"  SUCCESS: Confidence: {kyc_result['confidence_score']}")

        # Store decision in audit trail
        regulatory_metadata = {
            "regulation": "Sponsor Bank Audit Readiness",
            "drift_detection_enabled": True,
            "rca_automation": True,
            "high_velocity_release": True,
            "release_metadata": stable_release_config
        }

        snapshot = backend.create_decision_snapshot(
            function_name="fintech_kyc_onboarding",
            inputs=user_data,
            outputs=kyc_result,
            metadata=regulatory_metadata
        )

        stored_id = db_backend.save_decision(snapshot)
        stable_decisions.append({
            "decision_id": stored_id,
            "release_version": stable_release_config["release_version"],
            "kyc_result": kyc_result["kyc_result"],
            "confidence_score": kyc_result["confidence_score"],
            "processing_time_ms": kyc_result["processing_time_ms"]
        })
        print(f"  SUCCESS: Stored: {stored_id[:12]}...")

    print(f"\nSUCCESS: Baseline release {stable_release_config['release_version']} processing complete")
    stable_pass_rate = sum(1 for d in stable_decisions if d["kyc_result"] == "pass") / len(stable_decisions)
    print(f"SUCCESS: Pass rate: {stable_pass_rate:.1%}")

    # Simulate problematic release v2.14.3
    print("\n" + "="*85)
    print("RELEASE v2.14.3 - REGRESSION SIMULATION")
    print("="*85)

    problem_release_config = {
        "release_version": "v2.14.3",
        "model_version": "kyc-v7.2",
        "deployment_timestamp": datetime.utcnow().isoformat(),
        "stability_status": "unstable"
    }

    problem_decisions = []

    print(f"Processing onboarding sessions for release {problem_release_config['release_version']}:")

    for i in range(5):
        # Create user session
        user_data = create_user_onboarding(i + 100, problem_release_config["release_version"])

        print(f"\nSession {i+1}:")
        print(f"  User ID: {user_data['user_id_hash']}")
        print(f"  Document: {user_data['document_type']}")
        print(f"  Device Quality: {user_data['device_quality_score']:.2f}")

        # Process KYC decision (with regression)
        kyc_result = simulate_kyc_onboarding_decision(user_data, problem_release_config)
        print(f"  SUCCESS: KYC Result: {kyc_result['kyc_result']}")
        print(f"  SUCCESS: Confidence: {kyc_result['confidence_score']}")

        if kyc_result["failure_reason"]:
            print(f"  WARNING: Failure Reason: {kyc_result['failure_reason']}")

        # Store decision in audit trail
        regulatory_metadata = {
            "regulation": "Sponsor Bank Audit Readiness",
            "drift_detection_enabled": True,
            "rca_automation": True,
            "high_velocity_release": True,
            "release_metadata": problem_release_config
        }

        snapshot = backend.create_decision_snapshot(
            function_name="fintech_kyc_onboarding",
            inputs=user_data,
            outputs=kyc_result,
            metadata=regulatory_metadata
        )

        stored_id = db_backend.save_decision(snapshot)
        problem_decisions.append({
            "decision_id": stored_id,
            "release_version": problem_release_config["release_version"],
            "kyc_result": kyc_result["kyc_result"],
            "confidence_score": kyc_result["confidence_score"],
            "processing_time_ms": kyc_result["processing_time_ms"],
            "failure_reason": kyc_result["failure_reason"]
        })
        print(f"  SUCCESS: Stored: {stored_id[:12]}...")

    print(f"\nWARNING: Release {problem_release_config['release_version']} showing degraded performance")
    problem_pass_rate = sum(1 for d in problem_decisions if d["kyc_result"] == "pass") / len(problem_decisions)
    print(f"WARNING: Pass rate: {problem_pass_rate:.1%}")

    # Automated drift detection and RCA
    print("\n" + "="*85)
    print("AUTOMATED DRIFT DETECTION & ROOT CAUSE ANALYSIS")
    print("="*85)

    # Combine all decisions for cohort analysis
    all_decisions = stable_decisions + problem_decisions

    print("Running automated cohort analysis...")
    cohort_analysis = analyze_cohort_performance(all_decisions)

    if cohort_analysis.get("drift_detected", False):
        print("🚨 DRIFT DETECTED - Generating automated RCA")

        print("\nCOHORT PERFORMANCE COMPARISON:")
        print("-" * 50)
        for release, stats in cohort_analysis["cohort_stats"].items():
            print(f"Release {release}:")
            print(f"  Total Decisions: {stats['total_decisions']}")
            print(f"  Pass Rate: {stats['pass_rate']:.1%}")
            print(f"  Failure Rate: {stats['failure_rate']:.1%}")
            print(f"  Avg Confidence: {stats['avg_confidence']:.3f}")
            print()

        print("ANOMALY DETECTION RESULTS:")
        print("-" * 50)
        for anomaly in cohort_analysis.get("anomalies", []):
            print(f"🚨 {anomaly['type'].upper()} ({anomaly['severity']} severity)")
            print(f"   Release: {anomaly['release']} vs {anomaly['previous_release']}")

            if anomaly["type"] == "failure_rate_spike":
                print(f"   Failure Rate: {anomaly['previous_failure_rate']} → {anomaly['current_failure_rate']}")
                print(f"   Change: {anomaly['failure_rate_change']}")
            elif anomaly["type"] == "confidence_degradation":
                print(f"   Confidence: {anomaly['previous_confidence']:.3f} → {anomaly['current_confidence']:.3f}")
                print(f"   Drop: {anomaly['confidence_drop']:.3f}")
            print()

        # Generate automated RCA
        print("="*85)
        print("PRE-PACKAGED ROOT CAUSE ANALYSIS")
        print("="*85)

        # Find model version change
        model_versions = set()
        for release, stats in cohort_analysis["cohort_stats"].items():
            # Get model version from first decision in cohort
            if stats["decisions"]:
                first_decision_id = stats["decisions"][0]["decision_id"]
                retrieved = db_backend.load_decision(first_decision_id)
                if retrieved:
                    for output in retrieved.outputs:
                        if output.name == "model_version":
                            model_versions.add(f"{release}: {output.value}")

        print("AUTOMATED RCA REPORT:")
        print("=" * 40)
        print("ISSUE: KYC onboarding failure rate spike detected")
        print()
        print("ROOT CAUSE ANALYSIS:")
        print("1. Release comparison:")
        for mv in sorted(model_versions):
            print(f"   {mv}")
        print()

        # Find the specific release that introduced the issue
        worst_release = None
        worst_failure_rate = 0
        for release, stats in cohort_analysis["cohort_stats"].items():
            if stats["failure_rate"] > worst_failure_rate:
                worst_failure_rate = stats["failure_rate"]
                worst_release = release

        if worst_release:
            print(f"2. Release {worst_release} introduced performance degradation")
            print(f"   Failure rate increased to {worst_failure_rate:.1%}")
            print()

        print("3. Model version change detected between releases")
        print("4. Confidence score degradation correlates with model version change")
        print()

        print("RECOMMENDED ACTIONS:")
        print("- Rollback to previous release version immediately")
        print("- Investigate model training data for version kyc-v7.2")
        print("- Review model validation results before production deployment")
        print("- Implement automated release gates based on KYC performance metrics")

    else:
        print("SUCCESS: No significant drift detected between releases")

    # Demonstrate sponsor bank audit readiness
    print("\n" + "="*85)
    print("SPONSOR BANK AUDIT READINESS")
    print("="*85)

    audit_query = "Provide evidence that fintech partner KYC performance is continuously monitored and regressions are detected automatically."
    print(f"SPONSOR BANK AUDITOR QUERY: {audit_query}")
    print()

    print("SPONSOR BANK RESPONSE:")
    print("-" * 60)
    print("1. CONTINUOUS MONITORING:")
    print(f"   - Total KYC decisions tracked: {len(all_decisions)}")
    print(f"   - Release versions monitored: {len(cohort_analysis['cohort_stats'])}")
    print(f"   - Automated drift detection: {'ENABLED' if cohort_analysis.get('drift_detected') else 'ENABLED (no drift detected)'}")
    print()

    print("2. REGRESSION DETECTION:")
    if cohort_analysis.get("drift_detected"):
        print(f"   - Anomalies detected: {len(cohort_analysis.get('anomalies', []))}")
        print("   - Root cause analysis: AUTOMATED")
        print("   - Sponsor bank notification: IMMEDIATE")
    else:
        print("   - Performance stable across releases")
    print()

    print("3. AUDIT TRAIL COMPLETENESS:")
    print(f"   - Decision records stored: {len(all_decisions)}")
    print("   - Model version tracking: COMPLETE")
    print("   - Release correlation: DOCUMENTED")
    print("   - Historical reconstruction: AVAILABLE")

    # Regulatory validation
    print("\n" + "="*85)
    print("REGULATORY COMPLIANCE VALIDATION")
    print("="*85)

    sample_decision_id = stable_decisions[0]["decision_id"]
    sample_decision = db_backend.load_decision(sample_decision_id)

    required_monitoring_fields = [
        "regulation",
        "drift_detection_enabled",
        "rca_automation",
        "high_velocity_release"
    ]

    validation_result = backend.validate_regulatory_completeness(
        sample_decision,
        required_monitoring_fields
    )

    print(f"Monitoring Compliance: {'COMPLIANT' if validation_result['is_compliant'] else 'NON-COMPLIANT'}")
    print(f"Completeness Score: {validation_result['completeness_score']:.1%}")

    if validation_result['missing_fields']:
        print(f"Missing Fields: {', '.join(validation_result['missing_fields'])}")

    # Summary
    print("\n" + "="*85)
    print("BRIEFCASE AI VALUE FOR FINTECH RELEASE MONITORING")
    print("="*85)
    print("SUCCESS: Automated drift detection for high-velocity releases (1-2x per week)")
    print("SUCCESS: Pre-packaged root cause analysis without manual war room")
    print("SUCCESS: Real-time sponsor bank audit trail for regulatory readiness")
    print("SUCCESS: Model version correlation with performance degradation")
    print("SUCCESS: Cohort-level analysis preventing systemic KYC failures")

    print(f"\nSUCCESS: Fintech release monitoring demonstration completed")
    print(f"Releases analyzed: {len(cohort_analysis['cohort_stats'])}")
    print(f"Drift detected: {'YES' if cohort_analysis.get('drift_detected') else 'NO'}")
    print(f"RCA automation: {'TRIGGERED' if cohort_analysis.get('drift_detected') else 'STANDBY'}")


if __name__ == "__main__":
    main()