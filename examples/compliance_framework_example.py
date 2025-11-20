#!/usr/bin/env python3
"""
Compliance Framework Example

Demonstrates comprehensive compliance checking for AI agent deployments
across multiple regulatory frameworks including GDPR, SOC2, and HIPAA.

Features demonstrated:
- Multi-framework compliance assessment
- Automated compliance checking
- Audit trail generation
- Risk assessment and reporting
- Violation detection and remediation
- Compliance monitoring dashboard
"""

import sys
import os
from typing import List, Dict, Any
import time
from datetime import datetime

# Add SDK path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import briefcase_ai_telemetry as bai

class ComplianceDemo:
    """Demonstration of compliance framework capabilities."""

    def __init__(self, briefcase_api_key: str):
        self.briefcase_api_key = briefcase_api_key
        self.compliance_manager = None

    def setup_compliance_framework(self):
        """Initialize compliance framework with multiple standards."""
        print("🔒 Setting up Compliance Framework")
        print("=" * 50)

        # Create compliance configuration
        config = bai.ComplianceConfig()

        # Configure multiple compliance frameworks
        config.set_frameworks(["gdpr", "soc2", "hipaa"])

        print(f"📋 Configured frameworks: {config.frameworks}")
        print(f"🔍 Audit logging: {config.enable_audit_logging}")
        print(f"📅 Data retention: {config.data_retention_days} days")
        print(f"🔐 Anonymization: {config.anonymization_enabled}")

        # Create compliance manager
        self.compliance_manager = bai.ComplianceManager(config)

        print("✅ Compliance manager initialized")
        return True

    def demo_gdpr_compliance(self):
        """Demonstrate GDPR compliance checking."""
        print("\n🇪🇺 GDPR Compliance Assessment")
        print("=" * 40)

        # Create compliance context for personal data processing
        context = bai.ComplianceContext(
            agent_id=101,
            data_categories=["personal_data", "sensitive_personal_data"],
            processing_purpose="AI model training and inference",
            user_id="user_123"
        )

        print(f"👤 Agent ID: {context.agent_id}")
        print(f"📂 Data categories: {context.data_categories}")
        print(f"🎯 Purpose: {context.processing_purpose}")

        # Run compliance check
        reports = self.compliance_manager.check_compliance(context)

        # Find GDPR report
        gdpr_report = next((r for r in reports if r.framework == "gdpr"), None)

        if gdpr_report:
            print(f"\n📊 GDPR Assessment Results:")
            print(f"   Status: {gdpr_report.overall_status}")
            print(f"   Score: {gdpr_report.compliance_score:.2%}")
            print(f"   Requirements checked: {gdpr_report.requirements_checked}")
            print(f"   Requirements met: {gdpr_report.requirements_met}")
            print(f"   Violations: {gdpr_report.violations_count}")
            print(f"   Recommendations: {gdpr_report.recommendations_count}")

            # Display status with appropriate emoji
            if gdpr_report.overall_status == "compliant":
                print("   ✅ GDPR Compliant")
            elif gdpr_report.overall_status == "requires_review":
                print("   ⚠️  Requires Review")
            else:
                print("   ❌ Non-Compliant")

        return gdpr_report

    def demo_soc2_compliance(self):
        """Demonstrate SOC2 compliance checking."""
        print("\n🏢 SOC2 Compliance Assessment")
        print("=" * 40)

        # Create compliance context focused on system security
        context = bai.ComplianceContext(
            agent_id=102,
            data_categories=["non_personal_data", "financial_data"],
            processing_purpose="Financial data analysis and reporting"
        )

        print(f"🏗️  Agent ID: {context.agent_id}")
        print(f"📂 Data categories: {context.data_categories}")
        print(f"🎯 Purpose: {context.processing_purpose}")

        # Run compliance check
        reports = self.compliance_manager.check_compliance(context)

        # Find SOC2 report
        soc2_report = next((r for r in reports if r.framework == "soc2"), None)

        if soc2_report:
            print(f"\n📊 SOC2 Assessment Results:")
            print(f"   Status: {soc2_report.overall_status}")
            print(f"   Score: {soc2_report.compliance_score:.2%}")
            print(f"   Requirements checked: {soc2_report.requirements_checked}")
            print(f"   Requirements met: {soc2_report.requirements_met}")
            print(f"   Violations: {soc2_report.violations_count}")

            if soc2_report.overall_status == "compliant":
                print("   ✅ SOC2 Compliant")
            elif soc2_report.overall_status == "requires_review":
                print("   ⚠️  Requires Review")
            else:
                print("   ❌ Non-Compliant")

        return soc2_report

    def demo_hipaa_compliance(self):
        """Demonstrate HIPAA compliance checking."""
        print("\n🏥 HIPAA Compliance Assessment")
        print("=" * 40)

        # Create compliance context for health data
        context = bai.ComplianceContext(
            agent_id=103,
            data_categories=["health_data", "personal_data"],
            processing_purpose="Medical record analysis and diagnosis assistance",
            user_id="patient_456"
        )

        print(f"🩺 Agent ID: {context.agent_id}")
        print(f"📂 Data categories: {context.data_categories}")
        print(f"🎯 Purpose: {context.processing_purpose}")

        # Run compliance check
        reports = self.compliance_manager.check_compliance(context)

        # Find HIPAA report
        hipaa_report = next((r for r in reports if r.framework == "hipaa"), None)

        if hipaa_report:
            print(f"\n📊 HIPAA Assessment Results:")
            print(f"   Status: {hipaa_report.overall_status}")
            print(f"   Score: {hipaa_report.compliance_score:.2%}")
            print(f"   Requirements checked: {hipaa_report.requirements_checked}")
            print(f"   Requirements met: {hipaa_report.requirements_met}")
            print(f"   Violations: {hipaa_report.violations_count}")

            if hipaa_report.overall_status == "compliant":
                print("   ✅ HIPAA Compliant")
            elif hipaa_report.overall_status == "requires_review":
                print("   ⚠️  Requires Review")
            else:
                print("   ❌ Non-Compliant")

        return hipaa_report

    def demo_multi_framework_assessment(self):
        """Demonstrate assessment across multiple frameworks simultaneously."""
        print("\n🌐 Multi-Framework Compliance Assessment")
        print("=" * 50)

        # Create comprehensive compliance context
        context = bai.ComplianceContext(
            agent_id=999,
            data_categories=["personal_data", "health_data", "financial_data"],
            processing_purpose="Comprehensive AI healthcare and financial analysis platform",
            user_id="enterprise_client_789"
        )

        print(f"🏢 Enterprise Agent ID: {context.agent_id}")
        print(f"📂 Data categories: {context.data_categories}")
        print(f"🎯 Purpose: {context.processing_purpose}")

        # Run compliance check across all frameworks
        start_time = time.time()
        reports = self.compliance_manager.check_compliance(context)
        assessment_time = time.time() - start_time

        print(f"\n📊 Multi-Framework Results (completed in {assessment_time:.2f}s):")
        print("─" * 60)

        framework_results = {}
        total_score = 0
        compliant_count = 0

        for report in reports:
            framework = report.framework.upper()
            status = report.overall_status
            score = report.compliance_score

            framework_results[framework] = {
                'status': status,
                'score': score,
                'violations': report.violations_count,
                'requirements_met': report.requirements_met,
                'requirements_total': report.requirements_checked
            }

            total_score += score
            if status == "compliant":
                compliant_count += 1

            # Display individual framework results
            status_icon = "✅" if status == "compliant" else "⚠️" if status == "requires_review" else "❌"
            print(f"{status_icon} {framework}: {score:.1%} ({report.requirements_met}/{report.requirements_checked} requirements)")

        # Calculate overall compliance metrics
        avg_score = total_score / len(reports) if reports else 0
        compliance_percentage = (compliant_count / len(reports)) * 100 if reports else 0

        print(f"\n📈 Overall Compliance Summary:")
        print(f"   Average Score: {avg_score:.1%}")
        print(f"   Frameworks Compliant: {compliant_count}/{len(reports)} ({compliance_percentage:.0f}%)")

        # Determine overall status
        if compliance_percentage == 100:
            print("   🎉 All frameworks compliant!")
        elif compliance_percentage >= 66:
            print("   ⚠️  Mostly compliant - some issues to address")
        else:
            print("   ❌ Significant compliance gaps - immediate action required")

        return framework_results

    def demo_compliance_monitoring(self):
        """Demonstrate ongoing compliance monitoring."""
        print("\n📊 Compliance Monitoring Dashboard")
        print("=" * 50)

        # Generate compliance summary
        summary = self.compliance_manager.generate_summary()

        print(f"📋 Compliance Overview:")
        print(f"   Total frameworks: {summary.total_frameworks}")
        print(f"   Compliant frameworks: {summary.compliant_frameworks}")
        print(f"   Non-compliant frameworks: {summary.non_compliant_frameworks}")
        print(f"   Audit events: {summary.audit_events_count}")

        # Calculate compliance percentage
        if summary.total_frameworks > 0:
            compliance_rate = (summary.compliant_frameworks / summary.total_frameworks) * 100
            print(f"   Compliance rate: {compliance_rate:.1f}%")

            if compliance_rate == 100:
                print("   Status: 🟢 Full Compliance")
            elif compliance_rate >= 80:
                print("   Status: 🟡 Mostly Compliant")
            elif compliance_rate >= 60:
                print("   Status: 🟠 Partial Compliance")
            else:
                print("   Status: 🔴 Non-Compliant")

        # Display monitoring recommendations
        print(f"\n💡 Monitoring Recommendations:")

        if summary.compliant_frameworks == summary.total_frameworks:
            print("   • Continue regular compliance assessments")
            print("   • Monitor for configuration changes")
            print("   • Review audit logs periodically")
        else:
            print("   • Address non-compliant frameworks immediately")
            print("   • Implement remediation plans")
            print("   • Increase monitoring frequency")

        return summary

    def demo_compliance_scenarios(self):
        """Demonstrate various compliance scenarios."""
        print("\n🎭 Compliance Scenario Testing")
        print("=" * 50)

        scenarios = [
            {
                "name": "E-commerce Platform",
                "agent_id": 201,
                "data_categories": ["personal_data", "financial_data"],
                "purpose": "Customer behavior analysis and payment processing",
                "expected_frameworks": ["gdpr", "soc2"]
            },
            {
                "name": "Healthcare AI Assistant",
                "agent_id": 202,
                "data_categories": ["health_data", "personal_data", "sensitive_personal_data"],
                "purpose": "Medical diagnosis support and patient care optimization",
                "expected_frameworks": ["hipaa", "gdpr"]
            },
            {
                "name": "Financial Trading Bot",
                "agent_id": 203,
                "data_categories": ["financial_data", "personal_data"],
                "purpose": "Automated trading decisions and risk assessment",
                "expected_frameworks": ["soc2", "gdpr"]
            },
            {
                "name": "HR Analytics Platform",
                "agent_id": 204,
                "data_categories": ["personal_data", "sensitive_personal_data"],
                "purpose": "Employee performance analysis and hiring optimization",
                "expected_frameworks": ["gdpr", "soc2"]
            }
        ]

        scenario_results = {}

        for scenario in scenarios:
            print(f"\n🔍 Testing: {scenario['name']}")
            print("─" * 30)

            # Create context for scenario
            context = bai.ComplianceContext(
                agent_id=scenario["agent_id"],
                data_categories=scenario["data_categories"],
                processing_purpose=scenario["purpose"]
            )

            # Run compliance assessment
            reports = self.compliance_manager.check_compliance(context)

            # Analyze results
            scenario_result = {
                "total_frameworks": len(reports),
                "compliant_frameworks": 0,
                "average_score": 0,
                "critical_violations": 0
            }

            total_score = 0
            for report in reports:
                total_score += report.compliance_score
                if report.overall_status == "compliant":
                    scenario_result["compliant_frameworks"] += 1

            scenario_result["average_score"] = total_score / len(reports) if reports else 0

            # Display scenario results
            print(f"   Score: {scenario_result['average_score']:.1%}")
            print(f"   Compliant: {scenario_result['compliant_frameworks']}/{scenario_result['total_frameworks']}")

            if scenario_result["average_score"] >= 0.9:
                print("   Status: ✅ Excellent compliance")
            elif scenario_result["average_score"] >= 0.8:
                print("   Status: 🟢 Good compliance")
            elif scenario_result["average_score"] >= 0.6:
                print("   Status: 🟡 Needs improvement")
            else:
                print("   Status: 🔴 Requires immediate attention")

            scenario_results[scenario["name"]] = scenario_result

        return scenario_results

    def demo_compliance_best_practices(self):
        """Demonstrate compliance best practices and recommendations."""
        print("\n💡 Compliance Best Practices")
        print("=" * 50)

        best_practices = {
            "GDPR": [
                "Implement explicit consent mechanisms",
                "Enable data subject rights (access, deletion, portability)",
                "Conduct privacy impact assessments",
                "Implement data minimization principles",
                "Ensure lawful basis for all processing",
                "Maintain detailed processing records"
            ],
            "SOC2": [
                "Implement strong access controls",
                "Monitor and log all system activities",
                "Conduct regular security assessments",
                "Implement incident response procedures",
                "Maintain system availability and reliability",
                "Document security policies and procedures"
            ],
            "HIPAA": [
                "Encrypt all PHI at rest and in transit",
                "Implement minimum necessary standards",
                "Conduct workforce training on HIPAA",
                "Maintain audit logs of PHI access",
                "Implement physical safeguards",
                "Sign business associate agreements"
            ]
        }

        for framework, practices in best_practices.items():
            print(f"\n🔒 {framework} Best Practices:")
            for i, practice in enumerate(practices, 1):
                print(f"   {i}. {practice}")

        print(f"\n🎯 Universal Compliance Recommendations:")
        universal_practices = [
            "Regular compliance assessments and monitoring",
            "Automated compliance checking in CI/CD pipelines",
            "Staff training on data protection and privacy",
            "Clear data governance policies and procedures",
            "Regular third-party compliance audits",
            "Incident response and breach notification procedures",
            "Data retention and deletion policies",
            "Privacy by design in system architecture"
        ]

        for i, practice in enumerate(universal_practices, 1):
            print(f"   {i}. {practice}")

def main():
    """Main demonstration function."""
    print("🔒 Briefcase AI Compliance Framework Demo")
    print("=" * 60)

    # Configuration
    BRIEFCASE_API_KEY = "your-briefcase-ai-api-key"  # Replace with your API key

    # Create demo instance
    demo = ComplianceDemo(BRIEFCASE_API_KEY)

    try:
        # Setup compliance framework
        if not demo.setup_compliance_framework():
            print("❌ Failed to setup compliance framework")
            return

        # Run individual framework demos
        demo.demo_gdpr_compliance()
        demo.demo_soc2_compliance()
        demo.demo_hipaa_compliance()

        # Multi-framework assessment
        framework_results = demo.demo_multi_framework_assessment()

        # Compliance monitoring
        summary = demo.demo_compliance_monitoring()

        # Scenario testing
        scenario_results = demo.demo_compliance_scenarios()

        # Best practices
        demo.demo_compliance_best_practices()

        # Final summary
        print(f"\n📊 Demo Summary")
        print("=" * 40)
        print(f"✅ Compliance frameworks tested: {len(framework_results)}")
        print(f"✅ Scenarios evaluated: {len(scenario_results)}")
        print(f"✅ Total frameworks configured: {summary.total_frameworks}")
        print(f"📋 Audit events generated: {summary.audit_events_count}")

    except Exception as e:
        print(f"❌ Demo failed: {e}")

    print("\n💡 Next Steps:")
    print("   1. Configure your specific compliance requirements")
    print("   2. Integrate compliance checks into your AI agent workflows")
    print("   3. Set up automated compliance monitoring")
    print("   4. Implement remediation procedures for violations")
    print("   5. Train your team on compliance best practices")

if __name__ == "__main__":
    main()