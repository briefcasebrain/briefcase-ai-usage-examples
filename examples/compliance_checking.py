#!/usr/bin/env python3
"""
Compliance Checking Example

This example demonstrates regulatory compliance checking including:
- GDPR compliance verification
- SOC2 compliance assessment
- FSB (Financial Services) compliance
- Custom compliance frameworks
- Audit trail requirements
- Temperature and consistency requirements
"""

from briefcase_ai_telemetry import (
    DriftCalculator, ComplianceFramework, calculate_drift
)


def gdpr_compliance_examples():
    """GDPR compliance checking examples."""
    print("=== GDPR Compliance Examples ===")

    calculator = DriftCalculator()

    # Example 1: GDPR Compliant System
    print("\n1. GDPR Compliant System:")
    gdpr_pass = calculator.check_compliance(
        consistency_score=92.0,  # Above 85% threshold
        temperature=0.0,         # Deterministic outputs
        has_audit_trail=True,    # Audit trail enabled
        framework=ComplianceFramework.Gdpr
    )

    print(f"   Compliant: {gdpr_pass.compliant}")
    print(f"   Score: {gdpr_pass.score:.1f}%")
    print(f"   Framework: {gdpr_pass.framework}")
    print(f"   Requirements met:")
    for req, status in gdpr_pass.requirements.items():
        print(f"     {req}: {'✓' if status else '✗'}")

    if gdpr_pass.issues:
        print(f"   Issues: {gdpr_pass.issues}")

    # Example 2: GDPR Non-Compliant System
    print("\n2. GDPR Non-Compliant System:")
    gdpr_fail = calculator.check_compliance(
        consistency_score=80.0,   # Below 85% threshold
        temperature=0.5,          # Non-deterministic
        has_audit_trail=False,    # No audit trail
        framework=ComplianceFramework.Gdpr
    )

    print(f"   Compliant: {gdpr_fail.compliant}")
    print(f"   Score: {gdpr_fail.score:.1f}%")
    print(f"   Requirements met:")
    for req, status in gdpr_fail.requirements.items():
        print(f"     {req}: {'✓' if status else '✗'}")

    print(f"   Issues:")
    for issue in gdpr_fail.issues:
        print(f"     - {issue}")


def soc2_compliance_examples():
    """SOC2 compliance checking examples."""
    print("\n=== SOC2 Compliance Examples ===")

    calculator = DriftCalculator()

    # Example 1: SOC2 Compliant System
    print("\n1. SOC2 Compliant System:")
    soc2_pass = calculator.check_compliance(
        consistency_score=96.0,   # Above 95% threshold
        temperature=0.0,          # Deterministic
        has_audit_trail=True,     # Required audit trail
        framework=ComplianceFramework.Soc2
    )

    print(f"   Compliant: {soc2_pass.compliant}")
    print(f"   Score: {soc2_pass.score:.1f}%")
    print(f"   Framework: {soc2_pass.framework}")
    print(f"   Requirements met:")
    for req, status in soc2_pass.requirements.items():
        print(f"     {req}: {'✓' if status else '✗'}")

    # Example 2: SOC2 Marginal System
    print("\n2. SOC2 Marginal System:")
    soc2_marginal = calculator.check_compliance(
        consistency_score=94.0,   # Just below 95% threshold
        temperature=0.1,          # Slight randomness
        has_audit_trail=True,     # Has audit trail
        framework=ComplianceFramework.Soc2
    )

    print(f"   Compliant: {soc2_marginal.compliant}")
    print(f"   Score: {soc2_marginal.score:.1f}%")
    print(f"   Requirements met:")
    for req, status in soc2_marginal.requirements.items():
        print(f"     {req}: {'✓' if status else '✗'}")

    if soc2_marginal.issues:
        print(f"   Issues:")
        for issue in soc2_marginal.issues:
            print(f"     - {issue}")


def fsb_compliance_examples():
    """FSB (Financial Services) compliance examples."""
    print("\n=== FSB Compliance Examples ===")

    calculator = DriftCalculator()

    # Example 1: FSB Compliant System (Strict Requirements)
    print("\n1. FSB Compliant System:")
    fsb_pass = calculator.check_compliance(
        consistency_score=99.2,   # Above 99% threshold
        temperature=0.0,          # Exactly 0 temperature
        has_audit_trail=True,     # Required audit trail
        framework=ComplianceFramework.Fsb
    )

    print(f"   Compliant: {fsb_pass.compliant}")
    print(f"   Score: {fsb_pass.score:.1f}%")
    print(f"   Framework: {fsb_pass.framework}")
    print(f"   Requirements met:")
    for req, status in fsb_pass.requirements.items():
        print(f"     {req}: {'✓' if status else '✗'}")

    # Example 2: FSB Non-Compliant (Temperature)
    print("\n2. FSB Non-Compliant (Temperature Issue):")
    fsb_fail_temp = calculator.check_compliance(
        consistency_score=99.5,   # High consistency
        temperature=0.1,          # But temperature > 0
        has_audit_trail=True,     # Has audit trail
        framework=ComplianceFramework.Fsb
    )

    print(f"   Compliant: {fsb_fail_temp.compliant}")
    print(f"   Score: {fsb_fail_temp.score:.1f}%")
    print(f"   Requirements met:")
    for req, status in fsb_fail_temp.requirements.items():
        print(f"     {req}: {'✓' if status else '✗'}")

    if fsb_fail_temp.issues:
        print(f"   Issues:")
        for issue in fsb_fail_temp.issues:
            print(f"     - {issue}")

    # Example 3: FSB Non-Compliant (Consistency)
    print("\n3. FSB Non-Compliant (Consistency Issue):")
    fsb_fail_consistency = calculator.check_compliance(
        consistency_score=98.5,   # Below 99% threshold
        temperature=0.0,          # Good temperature
        has_audit_trail=True,     # Has audit trail
        framework=ComplianceFramework.Fsb
    )

    print(f"   Compliant: {fsb_fail_consistency.compliant}")
    print(f"   Score: {fsb_fail_consistency.score:.1f}%")
    print(f"   Requirements met:")
    for req, status in fsb_fail_consistency.requirements.items():
        print(f"     {req}: {'✓' if status else '✗'}")

    if fsb_fail_consistency.issues:
        print(f"   Issues:")
        for issue in fsb_fail_consistency.issues:
            print(f"     - {issue}")


def real_world_compliance_scenario():
    """Real-world compliance checking scenario."""
    print("\n=== Real-World Compliance Scenario ===")

    # Simulate a financial AI system
    print("\n1. Financial AI System Compliance Check:")

    # Generate some test outputs for a financial model
    financial_outputs = [
        "Credit risk assessment: High risk (score: 8.2/10)",
        "Credit risk assessment: High risk (score: 8.2/10)",
        "Credit risk assessment: High risk (score: 8.2/10)"
    ]

    # Calculate drift metrics
    drift_metrics = calculate_drift(financial_outputs)

    print(f"   Model outputs: {len(financial_outputs)} predictions")
    print(f"   Agreement rate: {drift_metrics.total_agreement_rate:.1f}%")
    print(f"   Consensus confidence: {drift_metrics.consensus_confidence}")
    print(f"   Consistency score: {drift_metrics.consistency_score:.1f}")

    # Check against multiple frameworks
    frameworks_to_test = [
        (ComplianceFramework.Gdpr, "GDPR"),
        (ComplianceFramework.Soc2, "SOC2"),
        (ComplianceFramework.Fsb, "FSB")
    ]

    calculator = DriftCalculator()

    print(f"\n   Compliance Assessment:")
    print(f"   {'Framework':<12} {'Compliant':<10} {'Score':<8} {'Issues'}")
    print(f"   {'-'*50}")

    for framework, name in frameworks_to_test:
        check = calculator.check_compliance(
            consistency_score=drift_metrics.consistency_score,
            temperature=0.0,  # Assuming deterministic model
            has_audit_trail=True,  # Assuming audit trail is implemented
            framework=framework
        )

        issues_count = len(check.issues)
        print(f"   {name:<12} {'✓' if check.compliant else '✗':<10} {check.score:<7.1f}% {issues_count} issues")

    # Detailed analysis for financial compliance
    print(f"\n2. Financial Compliance Requirements:")

    # Check FSB compliance in detail
    fsb_check = calculator.check_compliance(
        consistency_score=drift_metrics.consistency_score,
        temperature=0.0,
        has_audit_trail=True,
        framework=ComplianceFramework.Fsb
    )

    print(f"   FSB Compliance Status: {'PASS' if fsb_check.compliant else 'FAIL'}")
    print(f"   Key Requirements:")
    print(f"     Minimum Consistency (99%): {'✓' if drift_metrics.consistency_score >= 99.0 else '✗'}")
    print(f"     Temperature = 0: {'✓' if True else '✗'}")  # Assuming T=0
    print(f"     Audit Trail: {'✓'}")  # Assuming enabled
    print(f"     Cross-Provider Validation: {'✓'}")  # Assuming implemented

    if not fsb_check.compliant:
        print(f"   Remediation Required:")
        for issue in fsb_check.issues:
            print(f"     - {issue}")


def compliance_monitoring_workflow():
    """Complete compliance monitoring workflow."""
    print("\n=== Compliance Monitoring Workflow ===")

    calculator = DriftCalculator()

    # Simulate daily compliance checks
    daily_scenarios = [
        {"day": "Monday", "consistency": 98.5, "temp": 0.0, "audit": True},
        {"day": "Tuesday", "consistency": 99.1, "temp": 0.0, "audit": True},
        {"day": "Wednesday", "consistency": 97.8, "temp": 0.05, "audit": True},
        {"day": "Thursday", "consistency": 99.3, "temp": 0.0, "audit": True},
        {"day": "Friday", "consistency": 96.2, "temp": 0.0, "audit": False},
    ]

    print(f"\n1. Weekly Compliance Monitoring (FSB Framework):")
    print(f"   {'Day':<12} {'Consistency':<12} {'Temperature':<12} {'Audit':<8} {'Compliant'}")
    print(f"   {'-'*60}")

    compliance_issues = []

    for scenario in daily_scenarios:
        check = calculator.check_compliance(
            consistency_score=scenario["consistency"],
            temperature=scenario["temp"],
            has_audit_trail=scenario["audit"],
            framework=ComplianceFramework.Fsb
        )

        status = "✓" if check.compliant else "✗"
        print(f"   {scenario['day']:<12} {scenario['consistency']:<11.1f}% {scenario['temp']:<12.1f} {'✓' if scenario['audit'] else '✗':<8} {status}")

        if not check.compliant:
            compliance_issues.extend(check.issues)

    print(f"\n2. Weekly Compliance Summary:")
    compliant_days = sum(1 for s in daily_scenarios if calculator.check_compliance(
        s["consistency"], s["temp"], s["audit"], ComplianceFramework.Fsb
    ).compliant)

    print(f"   Compliant days: {compliant_days}/5")
    print(f"   Compliance rate: {compliant_days/5*100:.1f}%")

    if compliance_issues:
        print(f"   Issues identified:")
        unique_issues = list(set(compliance_issues))
        for issue in unique_issues:
            print(f"     - {issue}")

    print(f"\n3. Recommendations:")
    if compliant_days < 5:
        print(f"   - Implement automated compliance monitoring")
        print(f"   - Review model configuration for consistency")
        print(f"   - Ensure audit trail is always enabled")
        print(f"   - Consider model retraining if consistency drops")
    else:
        print(f"   - Compliance status is excellent")
        print(f"   - Continue current monitoring procedures")


def framework_comparison():
    """Compare requirements across compliance frameworks."""
    print("\n=== Compliance Framework Comparison ===")

    calculator = DriftCalculator()

    # Test system configuration
    test_config = {
        "consistency_score": 95.0,
        "temperature": 0.0,
        "has_audit_trail": True
    }

    frameworks = [
        (ComplianceFramework.Gdpr, "GDPR", "European data protection"),
        (ComplianceFramework.Soc2, "SOC2", "Security controls"),
        (ComplianceFramework.Fsb, "FSB", "Financial services")
    ]

    print(f"\nTest Configuration:")
    print(f"   Consistency Score: {test_config['consistency_score']:.1f}%")
    print(f"   Temperature: {test_config['temperature']}")
    print(f"   Audit Trail: {'Enabled' if test_config['has_audit_trail'] else 'Disabled'}")

    print(f"\n{'Framework':<8} {'Description':<20} {'Compliant':<10} {'Score':<8} {'Requirements Met'}")
    print(f"{'-'*75}")

    for framework, name, description in frameworks:
        check = calculator.check_compliance(
            consistency_score=test_config["consistency_score"],
            temperature=test_config["temperature"],
            has_audit_trail=test_config["has_audit_trail"],
            framework=framework
        )

        met_count = sum(1 for status in check.requirements.values() if status)
        total_count = len(check.requirements)

        print(f"{name:<8} {description:<20} {'✓' if check.compliant else '✗':<10} {check.score:<7.1f}% {met_count}/{total_count}")

    print(f"\nFramework-Specific Requirements:")
    print(f"   GDPR: Minimum 85% consistency, audit trail")
    print(f"   SOC2: Minimum 95% consistency, audit trail")
    print(f"   FSB: Minimum 99% consistency, temperature=0, audit trail")


if __name__ == "__main__":
    try:
        gdpr_compliance_examples()
        soc2_compliance_examples()
        fsb_compliance_examples()
        real_world_compliance_scenario()
        compliance_monitoring_workflow()
        framework_comparison()

        print("\n🎉 All compliance checking examples completed successfully!")
        print("\n🔒 Compliance Best Practices:")
        print("   - Regularly monitor consistency scores")
        print("   - Maintain deterministic outputs (temperature=0) for critical systems")
        print("   - Always enable audit trails for regulated environments")
        print("   - Implement automated compliance checking in your deployment pipeline")
        print("   - Document compliance procedures and maintain evidence")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()