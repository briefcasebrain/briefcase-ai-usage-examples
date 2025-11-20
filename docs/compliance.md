# Compliance Guide

Comprehensive guide to ensuring regulatory compliance for AI systems using the Briefcase AI Telemetry SDK.

## Overview

Regulatory compliance is critical for AI systems deployed in regulated industries. The SDK provides built-in compliance checking for major frameworks:

- **GDPR** (General Data Protection Regulation) - European data protection
- **SOC 2** (Service Organization Control 2) - Security and availability controls
- **FSB** (Financial Services Board) - Financial industry regulations
- **Custom Frameworks** - Your organization's specific requirements

## Quick Start

### Basic Compliance Checking

```python
from briefcase_ai_telemetry import DriftCalculator, ComplianceFramework

calculator = DriftCalculator()

# Check GDPR compliance
gdpr_check = calculator.check_compliance(
    consistency_score=92.0,
    temperature=0.0,
    has_audit_trail=True,
    framework=ComplianceFramework.Gdpr
)

print(f"GDPR Compliant: {gdpr_check.compliant}")
print(f"Score: {gdpr_check.score:.1f}%")
```

### Automated Compliance Monitoring

```python
def monitor_ai_compliance(model_outputs, temperature, audit_enabled):
    """Monitor compliance across multiple frameworks."""

    calculator = DriftCalculator()

    # Calculate consistency metrics
    metrics = calculator.calculate_metrics(model_outputs)

    # Check all frameworks
    frameworks = [
        (ComplianceFramework.Gdpr, "GDPR"),
        (ComplianceFramework.Soc2, "SOC 2"),
        (ComplianceFramework.Fsb, "FSB")
    ]

    results = {}
    for framework, name in frameworks:
        check = calculator.check_compliance(
            consistency_score=metrics.consistency_score,
            temperature=temperature,
            has_audit_trail=audit_enabled,
            framework=framework
        )
        results[name] = check

    return results
```

## Compliance Frameworks

### GDPR (General Data Protection Regulation)

GDPR compliance for AI systems focuses on data protection and user rights.

#### Requirements
- **Minimum Consistency**: 85% model consistency
- **Audit Trail**: Complete logging of AI decisions
- **Data Protection**: No processing of personal data without consent
- **Explainability**: Ability to explain automated decisions

#### Implementation

```python
class GDPRComplianceManager:
    def __init__(self):
        self.calculator = DriftCalculator()
        self.audit_log = []

    def check_gdpr_compliance(self, model_outputs, user_consent=False):
        """Check GDPR compliance for AI system."""

        # Calculate model consistency
        metrics = self.calculator.calculate_metrics(model_outputs)

        # Check compliance
        compliance_check = self.calculator.check_compliance(
            consistency_score=metrics.consistency_score,
            temperature=0.0,  # Deterministic for explainability
            has_audit_trail=True,
            framework=ComplianceFramework.Gdpr
        )

        # Additional GDPR checks
        gdpr_specific = {
            "user_consent": user_consent,
            "data_minimization": self._check_data_minimization(),
            "purpose_limitation": self._check_purpose_limitation(),
            "accuracy_requirement": metrics.consistency_score >= 85.0,
            "explainability": self._check_explainability()
        }

        # Log compliance check
        self._log_compliance_check("GDPR", compliance_check, gdpr_specific)

        return {
            "basic_compliance": compliance_check,
            "gdpr_specific": gdpr_specific,
            "overall_compliant": compliance_check.compliant and all(gdpr_specific.values())
        }

    def _check_data_minimization(self):
        """Check if only necessary data is processed."""
        # Implementation depends on your data processing
        return True  # Simplified for example

    def _check_purpose_limitation(self):
        """Check if data is used only for stated purposes."""
        return True  # Simplified for example

    def _check_explainability(self):
        """Check if AI decisions can be explained."""
        return True  # Requires implementation of explainability features

    def _log_compliance_check(self, framework, check_result, additional_data):
        """Log compliance check for audit purposes."""
        log_entry = {
            "timestamp": datetime.now(),
            "framework": framework,
            "compliant": check_result.compliant,
            "score": check_result.score,
            "additional_checks": additional_data
        }
        self.audit_log.append(log_entry)

# Usage
gdpr_manager = GDPRComplianceManager()

model_outputs = [
    "User account status: Active",
    "User account status: Active",
    "Account status: Active"
]

gdpr_result = gdpr_manager.check_gdpr_compliance(
    model_outputs=model_outputs,
    user_consent=True
)

print(f"GDPR Compliant: {gdpr_result['overall_compliant']}")
```

### SOC 2 (Service Organization Control 2)

SOC 2 compliance focuses on security, availability, and operational controls.

#### Requirements
- **Minimum Consistency**: 95% model consistency
- **Audit Trail**: Comprehensive logging and monitoring
- **Access Controls**: Proper authentication and authorization
- **Data Integrity**: Protection against unauthorized changes

#### Implementation

```python
class SOC2ComplianceManager:
    def __init__(self):
        self.calculator = DriftCalculator()
        self.security_log = []

    def check_soc2_compliance(self, model_outputs, security_controls):
        """Check SOC 2 compliance for AI system."""

        metrics = self.calculator.calculate_metrics(model_outputs)

        compliance_check = self.calculator.check_compliance(
            consistency_score=metrics.consistency_score,
            temperature=0.0,
            has_audit_trail=True,
            framework=ComplianceFramework.Soc2
        )

        # SOC 2 specific controls
        soc2_controls = {
            "security": self._check_security_controls(security_controls),
            "availability": self._check_availability(),
            "processing_integrity": metrics.consistency_score >= 95.0,
            "confidentiality": self._check_confidentiality(),
            "privacy": self._check_privacy_controls()
        }

        self._log_security_event("SOC2_COMPLIANCE_CHECK", compliance_check, soc2_controls)

        return {
            "basic_compliance": compliance_check,
            "soc2_controls": soc2_controls,
            "overall_compliant": compliance_check.compliant and all(soc2_controls.values())
        }

    def _check_security_controls(self, controls):
        """Check security control implementation."""
        required_controls = [
            "authentication",
            "authorization",
            "encryption",
            "access_logging"
        ]

        return all(control in controls for control in required_controls)

    def _check_availability(self):
        """Check system availability requirements."""
        # Check uptime, redundancy, etc.
        return True  # Simplified for example

    def _check_confidentiality(self):
        """Check data confidentiality measures."""
        return True  # Simplified for example

    def _check_privacy_controls(self):
        """Check privacy control implementation."""
        return True  # Simplified for example

    def _log_security_event(self, event_type, compliance_result, controls):
        """Log security events for SOC 2 reporting."""
        log_entry = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "compliance_status": compliance_result.compliant,
            "controls_status": controls,
            "risk_level": self._assess_risk_level(compliance_result, controls)
        }
        self.security_log.append(log_entry)

    def _assess_risk_level(self, compliance_result, controls):
        """Assess overall risk level."""
        if not compliance_result.compliant or not all(controls.values()):
            return "HIGH"
        elif compliance_result.score < 98.0:
            return "MEDIUM"
        else:
            return "LOW"

# Usage
soc2_manager = SOC2ComplianceManager()

security_controls = [
    "authentication",
    "authorization",
    "encryption",
    "access_logging",
    "intrusion_detection"
]

soc2_result = soc2_manager.check_soc2_compliance(
    model_outputs=model_outputs,
    security_controls=security_controls
)
```

### FSB (Financial Services Board)

FSB compliance for financial AI systems requires the highest standards.

#### Requirements
- **Minimum Consistency**: 99% model consistency
- **Temperature**: Must be 0.0 (deterministic outputs)
- **Audit Trail**: Complete transaction and decision logging
- **Cross-Provider Validation**: Multi-model validation for critical decisions

#### Implementation

```python
class FSBComplianceManager:
    def __init__(self):
        self.calculator = DriftCalculator()
        self.transaction_log = []
        self.model_validations = []

    def check_fsb_compliance(self, model_outputs, temperature, cross_validation_results=None):
        """Check FSB compliance for financial AI system."""

        metrics = self.calculator.calculate_metrics(model_outputs)

        compliance_check = self.calculator.check_compliance(
            consistency_score=metrics.consistency_score,
            temperature=temperature,
            has_audit_trail=True,
            framework=ComplianceFramework.Fsb
        )

        # FSB specific requirements
        fsb_requirements = {
            "ultra_high_consistency": metrics.consistency_score >= 99.0,
            "deterministic_outputs": abs(temperature) < 1e-6,  # Temperature must be 0.0
            "cross_validation": self._check_cross_validation(cross_validation_results),
            "risk_controls": self._check_risk_controls(),
            "regulatory_reporting": self._check_regulatory_reporting(),
            "stress_testing": self._check_stress_testing()
        }

        self._log_financial_transaction("FSB_COMPLIANCE_CHECK", compliance_check, fsb_requirements)

        return {
            "basic_compliance": compliance_check,
            "fsb_requirements": fsb_requirements,
            "overall_compliant": compliance_check.compliant and all(fsb_requirements.values()),
            "risk_assessment": self._assess_financial_risk(metrics, fsb_requirements)
        }

    def _check_cross_validation(self, validation_results):
        """Check cross-model validation for critical decisions."""
        if not validation_results:
            return False

        # Require agreement between multiple models
        agreement_threshold = 0.95
        return validation_results.get("agreement_score", 0) >= agreement_threshold

    def _check_risk_controls(self):
        """Check financial risk control implementation."""
        required_controls = [
            "position_limits",
            "exposure_monitoring",
            "stress_testing",
            "scenario_analysis"
        ]
        # Implementation would check actual risk controls
        return True  # Simplified for example

    def _check_regulatory_reporting(self):
        """Check regulatory reporting capabilities."""
        return True  # Simplified for example

    def _check_stress_testing(self):
        """Check stress testing implementation."""
        return True  # Simplified for example

    def _assess_financial_risk(self, metrics, requirements):
        """Assess financial risk level."""
        if not all(requirements.values()):
            return "CRITICAL"
        elif metrics.consistency_score < 99.5:
            return "HIGH"
        elif metrics.consensus_confidence != "high":
            return "MEDIUM"
        else:
            return "LOW"

    def _log_financial_transaction(self, transaction_type, compliance_result, requirements):
        """Log financial AI transactions for regulatory reporting."""
        log_entry = {
            "timestamp": datetime.now(),
            "transaction_type": transaction_type,
            "compliance_status": compliance_result.compliant,
            "consistency_score": compliance_result.score,
            "requirements_met": requirements,
            "regulatory_flags": self._identify_regulatory_flags(compliance_result, requirements)
        }
        self.transaction_log.append(log_entry)

    def _identify_regulatory_flags(self, compliance_result, requirements):
        """Identify potential regulatory issues."""
        flags = []

        if not requirements["ultra_high_consistency"]:
            flags.append("CONSISTENCY_BELOW_THRESHOLD")

        if not requirements["deterministic_outputs"]:
            flags.append("NON_DETERMINISTIC_OUTPUTS")

        if not requirements["cross_validation"]:
            flags.append("INSUFFICIENT_VALIDATION")

        return flags

# Usage
fsb_manager = FSBComplianceManager()

# Financial model outputs (must be highly consistent)
financial_outputs = [
    "Credit risk score: 7.85, Recommendation: Decline",
    "Credit risk score: 7.85, Recommendation: Decline",
    "Credit risk score: 7.85, Recommendation: Decline"
]

cross_validation = {
    "agreement_score": 0.98,
    "models_used": ["primary_model", "validation_model_1", "validation_model_2"],
    "consensus_reached": True
}

fsb_result = fsb_manager.check_fsb_compliance(
    model_outputs=financial_outputs,
    temperature=0.0,
    cross_validation_results=cross_validation
)
```

## Real-World Implementation

### Automated Compliance Pipeline

```python
class CompliancePipeline:
    def __init__(self):
        self.gdpr_manager = GDPRComplianceManager()
        self.soc2_manager = SOC2ComplianceManager()
        self.fsb_manager = FSBComplianceManager()
        self.compliance_history = []

    def run_compliance_check(self, ai_system_data):
        """Run comprehensive compliance check."""

        timestamp = datetime.now()
        results = {}

        # Determine applicable frameworks based on system type
        frameworks = self._determine_applicable_frameworks(ai_system_data)

        for framework in frameworks:
            if framework == "GDPR":
                result = self.gdpr_manager.check_gdpr_compliance(
                    model_outputs=ai_system_data["outputs"],
                    user_consent=ai_system_data.get("user_consent", False)
                )
            elif framework == "SOC2":
                result = self.soc2_manager.check_soc2_compliance(
                    model_outputs=ai_system_data["outputs"],
                    security_controls=ai_system_data.get("security_controls", [])
                )
            elif framework == "FSB":
                result = self.fsb_manager.check_fsb_compliance(
                    model_outputs=ai_system_data["outputs"],
                    temperature=ai_system_data.get("temperature", 0.0),
                    cross_validation_results=ai_system_data.get("cross_validation")
                )

            results[framework] = result

        # Aggregate results
        overall_compliance = self._assess_overall_compliance(results)

        # Store in compliance history
        compliance_record = {
            "timestamp": timestamp,
            "system_id": ai_system_data.get("system_id"),
            "frameworks_checked": frameworks,
            "results": results,
            "overall_compliant": overall_compliance["compliant"],
            "risk_level": overall_compliance["risk_level"],
            "action_required": overall_compliance["action_required"]
        }

        self.compliance_history.append(compliance_record)

        # Trigger alerts if non-compliant
        if not overall_compliance["compliant"]:
            self._trigger_compliance_alert(compliance_record)

        return compliance_record

    def _determine_applicable_frameworks(self, system_data):
        """Determine which compliance frameworks apply."""
        frameworks = []

        # Check based on system type and location
        system_type = system_data.get("type", "")
        deployment_region = system_data.get("region", "")

        if deployment_region in ["EU", "UK"] or system_data.get("processes_eu_data"):
            frameworks.append("GDPR")

        if system_data.get("requires_soc2") or system_type in ["saas", "cloud"]:
            frameworks.append("SOC2")

        if system_type in ["financial", "banking", "trading"]:
            frameworks.append("FSB")

        return frameworks

    def _assess_overall_compliance(self, framework_results):
        """Assess overall compliance across all frameworks."""
        all_compliant = all(
            result["overall_compliant"]
            for result in framework_results.values()
        )

        # Determine risk level
        risk_levels = []
        for result in framework_results.values():
            if "risk_assessment" in result:
                risk_levels.append(result["risk_assessment"])

        overall_risk = "LOW"
        if "CRITICAL" in risk_levels:
            overall_risk = "CRITICAL"
        elif "HIGH" in risk_levels:
            overall_risk = "HIGH"
        elif "MEDIUM" in risk_levels:
            overall_risk = "MEDIUM"

        # Determine required actions
        action_required = []
        if not all_compliant:
            action_required.append("IMMEDIATE_REMEDIATION")
        if overall_risk in ["HIGH", "CRITICAL"]:
            action_required.append("RISK_MITIGATION")

        return {
            "compliant": all_compliant,
            "risk_level": overall_risk,
            "action_required": action_required
        }

    def _trigger_compliance_alert(self, compliance_record):
        """Trigger alerts for compliance issues."""
        print(f"🚨 COMPLIANCE ALERT: System {compliance_record['system_id']}")
        print(f"   Risk Level: {compliance_record['risk_level']}")
        print(f"   Actions Required: {compliance_record['action_required']}")

        # Send to monitoring systems, email alerts, etc.

    def generate_compliance_report(self, days=30):
        """Generate compliance report for specified period."""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_records = [
            record for record in self.compliance_history
            if record["timestamp"] >= cutoff_date
        ]

        # Calculate compliance statistics
        total_checks = len(recent_records)
        compliant_checks = len([r for r in recent_records if r["overall_compliant"]])
        compliance_rate = (compliant_checks / total_checks * 100) if total_checks else 0

        # Risk distribution
        risk_distribution = {}
        for record in recent_records:
            risk_level = record["risk_level"]
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1

        # Framework-specific compliance
        framework_compliance = {}
        for record in recent_records:
            for framework, result in record["results"].items():
                if framework not in framework_compliance:
                    framework_compliance[framework] = {"total": 0, "compliant": 0}

                framework_compliance[framework]["total"] += 1
                if result["overall_compliant"]:
                    framework_compliance[framework]["compliant"] += 1

        return {
            "period_days": days,
            "total_checks": total_checks,
            "compliance_rate": compliance_rate,
            "risk_distribution": risk_distribution,
            "framework_compliance": framework_compliance,
            "trend_analysis": self._analyze_compliance_trends(recent_records)
        }

    def _analyze_compliance_trends(self, records):
        """Analyze compliance trends over time."""
        if len(records) < 10:
            return {"status": "insufficient_data"}

        # Sort by timestamp
        sorted_records = sorted(records, key=lambda x: x["timestamp"])

        # Split into first and second half
        mid_point = len(sorted_records) // 2
        first_half = sorted_records[:mid_point]
        second_half = sorted_records[mid_point:]

        # Calculate compliance rates
        first_half_rate = len([r for r in first_half if r["overall_compliant"]]) / len(first_half) * 100
        second_half_rate = len([r for r in second_half if r["overall_compliant"]]) / len(second_half) * 100

        trend = "stable"
        if second_half_rate > first_half_rate + 5:
            trend = "improving"
        elif second_half_rate < first_half_rate - 5:
            trend = "declining"

        return {
            "trend": trend,
            "early_period_rate": first_half_rate,
            "recent_period_rate": second_half_rate,
            "change": second_half_rate - first_half_rate
        }

# Usage
pipeline = CompliancePipeline()

# AI system data
system_data = {
    "system_id": "credit_scoring_v2",
    "type": "financial",
    "region": "EU",
    "processes_eu_data": True,
    "requires_soc2": True,
    "outputs": [
        "Credit approved: Score 8.5/10",
        "Credit approved: Score 8.5/10",
        "Credit approved: Score 8.5/10"
    ],
    "temperature": 0.0,
    "user_consent": True,
    "security_controls": ["authentication", "authorization", "encryption", "access_logging"],
    "cross_validation": {
        "agreement_score": 0.99,
        "models_used": ["primary", "backup", "validator"],
        "consensus_reached": True
    }
}

# Run compliance check
compliance_result = pipeline.run_compliance_check(system_data)

# Generate report
report = pipeline.generate_compliance_report(days=30)
print(f"Compliance Rate: {report['compliance_rate']:.1f}%")
print(f"Trend: {report['trend_analysis']['trend']}")
```

## Best Practices

### 1. Proactive Compliance Monitoring

```python
# Set up continuous compliance monitoring
def setup_compliance_monitoring():
    scheduler = ComplianceScheduler()

    # Daily compliance checks
    scheduler.schedule_daily(
        func=run_daily_compliance_check,
        hour=9,  # Run at 9 AM
        frameworks=["GDPR", "SOC2"]
    )

    # Weekly comprehensive audits
    scheduler.schedule_weekly(
        func=run_comprehensive_audit,
        day="monday",
        hour=8,
        frameworks=["GDPR", "SOC2", "FSB"]
    )
```

### 2. Compliance Documentation

```python
def generate_compliance_documentation(framework):
    """Generate compliance documentation for audits."""

    documentation = {
        "policies": get_compliance_policies(framework),
        "procedures": get_compliance_procedures(framework),
        "controls": get_implemented_controls(framework),
        "evidence": get_compliance_evidence(framework),
        "audit_logs": get_audit_logs(framework, days=365)
    }

    return documentation
```

### 3. Incident Response

```python
def handle_compliance_incident(incident_type, severity, details):
    """Handle compliance incidents according to framework requirements."""

    incident_record = {
        "timestamp": datetime.now(),
        "type": incident_type,
        "severity": severity,
        "details": details,
        "response_actions": []
    }

    if severity == "critical":
        # Immediate actions for critical incidents
        incident_record["response_actions"].extend([
            "notify_compliance_team",
            "isolate_affected_systems",
            "begin_forensic_analysis"
        ])

    return incident_record
```

### 4. Regular Framework Updates

```python
def update_compliance_frameworks():
    """Keep compliance frameworks current with regulatory changes."""

    # Check for regulatory updates
    updates = check_regulatory_updates()

    for framework, changes in updates.items():
        if changes:
            print(f"Regulatory updates for {framework}: {changes}")
            # Update compliance rules accordingly
```

## Troubleshooting

### Common Compliance Issues

#### 1. Consistency Below Threshold
```python
if consistency_score < required_threshold:
    remediation_steps = [
        "Review model configuration",
        "Check for data drift",
        "Consider model retraining",
        "Implement additional validation"
    ]
```

#### 2. Missing Audit Trail
```python
if not has_audit_trail:
    remediation_steps = [
        "Enable comprehensive logging",
        "Implement decision tracking",
        "Set up audit trail monitoring",
        "Review data retention policies"
    ]
```

#### 3. Temperature Violations
```python
if temperature > 0.0 and framework == "FSB":
    remediation_steps = [
        "Set temperature to 0.0",
        "Review deterministic requirements",
        "Test output consistency",
        "Update deployment configuration"
    ]
```

For detailed implementation examples, see the [examples directory](../examples/compliance_checking.py) and [API reference](api-reference.md).