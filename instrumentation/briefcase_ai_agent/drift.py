"""
Drift detection and consistency metrics calculation.

Based on the LLM Output Drift research and Briefcase AI platform algorithms.
Implements Total Agreement Rate (TAR), normalized edit distance, and compliance checking.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from enum import Enum

class ModelTier(Enum):
    """Model parameter tiers with expected consistency characteristics."""
    TIER_1 = 1  # 7-8B parameters, 100% consistency
    TIER_2 = 2  # 40-70B parameters, 56-100% consistency
    TIER_3 = 3  # 120B+ parameters, 12.5% consistency

class TaskType(Enum):
    """AI task types with temperature sensitivity characteristics."""
    RAG = "rag"
    SQL = "sql"
    SUMMARIZATION = "summarization"
    CODE_GENERATION = "code_generation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    OTHER = "other"

class ComplianceFramework(Enum):
    """Regulatory compliance frameworks with specific requirements."""
    FSB = "fsb"  # Financial Stability Board
    BIS = "bis"  # Bank for International Settlements
    CFTC = "cftc"  # Commodity Futures Trading Commission
    GDPR = "gdpr"  # General Data Protection Regulation
    SOC2 = "soc2"  # SOC 2 Type II
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act

@dataclass
class DriftMetrics:
    """Comprehensive drift and consistency metrics."""
    total_agreement_rate: float  # 0-100: % of runs producing identical outputs
    normalized_edit_distance: float  # 0-1: average string similarity (1 = identical)
    factual_drift_count: int  # count of numeric/citation mismatches
    consistency_score: float  # 0-100: overall reproducibility rating
    temperature_sensitivity: float  # consistency degradation per temperature unit
    consensus_confidence: str  # 'high', 'medium', 'low'
    consensus_output: str = None  # agreed-upon output if consensus reached

@dataclass
class ComplianceCheck:
    """Result of compliance framework validation."""
    framework: ComplianceFramework
    compliant: bool
    score: float
    requirements: Dict[str, bool]
    issues: List[str]

class DriftCalculator:
    """Main class for calculating drift metrics and compliance."""

    def __init__(self):
        # Model tier characteristics (from research paper)
        self.model_tiers = {
            ModelTier.TIER_1: {
                "parameter_range": "7-8B",
                "expected_consistency": 100,
                "compliance_status": "full",
            },
            ModelTier.TIER_2: {
                "parameter_range": "40-70B",
                "expected_consistency": 78,  # Average of 56-100%
                "compliance_status": "limited",
            },
            ModelTier.TIER_3: {
                "parameter_range": "120B+",
                "expected_consistency": 12.5,
                "compliance_status": "requires_validation",
            }
        }

        # Task type sensitivity (from research)
        self.task_types = {
            TaskType.RAG: {
                "temp_sensitivity": "high",
                "recommended_temp": 0.0,
                "consistency_at_t0": 100,
                "consistency_at_t02": 56,
            },
            TaskType.SQL: {
                "temp_sensitivity": "none",
                "recommended_temp": 0.0,
                "consistency_at_t0": 100,
                "consistency_at_t02": 100,
            },
            TaskType.SUMMARIZATION: {
                "temp_sensitivity": "none",
                "recommended_temp": 0.0,
                "consistency_at_t0": 100,
                "consistency_at_t02": 100,
            },
            TaskType.CODE_GENERATION: {
                "temp_sensitivity": "medium",
                "recommended_temp": 0.0,
                "consistency_at_t0": 95,
                "consistency_at_t02": 75,
            },
            TaskType.CLASSIFICATION: {
                "temp_sensitivity": "low",
                "recommended_temp": 0.0,
                "consistency_at_t0": 100,
                "consistency_at_t02": 95,
            },
            TaskType.EXTRACTION: {
                "temp_sensitivity": "low",
                "recommended_temp": 0.0,
                "consistency_at_t0": 100,
                "consistency_at_t02": 90,
            },
            TaskType.OTHER: {
                "temp_sensitivity": "high",
                "recommended_temp": 0.0,
                "consistency_at_t0": None,
                "consistency_at_t02": None,
            }
        }

        # Compliance framework requirements
        self.compliance_frameworks = {
            ComplianceFramework.FSB: {
                "name": "Financial Stability Board",
                "min_consistency": 100,
                "requires_audit_trail": True,
                "requires_cross_provider_validation": True,
                "requires_temperature_t0": True,
            },
            ComplianceFramework.BIS: {
                "name": "Bank for International Settlements",
                "min_consistency": 100,
                "requires_audit_trail": True,
                "requires_cross_provider_validation": False,
                "requires_temperature_t0": True,
            },
            ComplianceFramework.CFTC: {
                "name": "Commodity Futures Trading Commission",
                "min_consistency": 100,
                "requires_audit_trail": True,
                "requires_cross_provider_validation": False,
                "requires_temperature_t0": True,
            },
            ComplianceFramework.GDPR: {
                "name": "General Data Protection Regulation",
                "min_consistency": 95,
                "requires_audit_trail": True,
                "requires_cross_provider_validation": False,
                "requires_temperature_t0": False,
            },
            ComplianceFramework.SOC2: {
                "name": "SOC 2 Type II",
                "min_consistency": 95,
                "requires_audit_trail": True,
                "requires_cross_provider_validation": False,
                "requires_temperature_t0": False,
            },
            ComplianceFramework.HIPAA: {
                "name": "Health Insurance Portability and Accountability Act",
                "min_consistency": 100,
                "requires_audit_trail": True,
                "requires_cross_provider_validation": False,
                "requires_temperature_t0": True,
            },
        }

    def calculate_levenshtein_distance(self, str1: str, str2: str) -> int:
        """Calculate Levenshtein edit distance between two strings."""
        len1, len2 = len(str1), len(str2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if str1[i - 1] == str2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,      # deletion
                    matrix[i][j - 1] + 1,      # insertion
                    matrix[i - 1][j - 1] + cost  # substitution
                )

        return matrix[len1][len2]

    def calculate_normalized_edit_distance(self, str1: str, str2: str) -> float:
        """Calculate normalized edit distance (0-1, where 1 = identical)."""
        if str1 == str2:
            return 1.0
        if len(str1) == 0 and len(str2) == 0:
            return 1.0

        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0

        distance = self.calculate_levenshtein_distance(str1, str2)
        return 1 - (distance / max_len)

    def calculate_total_agreement_rate(self, outputs: List[str]) -> float:
        """Calculate Total Agreement Rate from multiple outputs."""
        if not outputs:
            return 0.0
        if len(outputs) == 1:
            return 100.0

        # Find the most common output
        output_counts = {}
        for output in outputs:
            output_counts[output] = output_counts.get(output, 0) + 1

        max_count = max(output_counts.values())
        return (max_count / len(outputs)) * 100

    def detect_factual_drift(self, outputs: List[str]) -> int:
        """Detect numeric and factual inconsistencies between outputs."""
        if len(outputs) < 2:
            return 0

        drift_count = 0

        # Extract numbers from all outputs
        number_patterns = []
        for output in outputs:
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', output)
            number_patterns.append(set(numbers))

        # Check for numeric inconsistencies
        reference_numbers = number_patterns[0]
        for pattern in number_patterns[1:]:
            if pattern != reference_numbers:
                drift_count += len(reference_numbers.symmetric_difference(pattern))

        # Extract dates/citations (basic pattern matching)
        citation_patterns = []
        for output in outputs:
            citations = re.findall(r'\b(?:19|20)\d{2}\b|\b[A-Z][a-z]+ et al\.\b', output)
            citation_patterns.append(set(citations))

        # Check for citation inconsistencies
        reference_citations = citation_patterns[0]
        for pattern in citation_patterns[1:]:
            if pattern != reference_citations:
                drift_count += len(reference_citations.symmetric_difference(pattern))

        return drift_count

    def calculate_consensus_confidence(self, agreement_rate: float) -> str:
        """Determine consensus confidence level based on agreement rate."""
        if agreement_rate >= 90:
            return "high"
        elif agreement_rate >= 70:
            return "medium"
        else:
            return "low"

    def find_consensus_output(self, outputs: List[str]) -> str:
        """Find the most common output as consensus result."""
        if not outputs:
            return None

        output_counts = {}
        for output in outputs:
            output_counts[output] = output_counts.get(output, 0) + 1

        # Return the most frequent output
        return max(output_counts, key=output_counts.get)

    def calculate_temperature_sensitivity(
        self,
        outputs_t0: List[str],
        outputs_t02: List[str]
    ) -> float:
        """Calculate consistency degradation per temperature unit."""
        if not outputs_t0 or not outputs_t02:
            return 0.0

        tar_t0 = self.calculate_total_agreement_rate(outputs_t0)
        tar_t02 = self.calculate_total_agreement_rate(outputs_t02)

        # Calculate degradation per 0.1 temperature unit
        temp_diff = 0.2  # From T=0.0 to T=0.2
        consistency_diff = tar_t0 - tar_t02

        return consistency_diff / (temp_diff * 10)  # Per 0.1 unit

    def calculate_metrics(self, outputs: List[str]) -> DriftMetrics:
        """Calculate comprehensive drift metrics for a set of outputs."""
        if not outputs:
            return DriftMetrics(0, 0, 0, 0, 0, "low")

        # Total Agreement Rate
        tar = self.calculate_total_agreement_rate(outputs)

        # Average normalized edit distance
        total_ned = 0
        comparison_count = 0
        for i in range(len(outputs)):
            for j in range(i + 1, len(outputs)):
                ned = self.calculate_normalized_edit_distance(outputs[i], outputs[j])
                total_ned += ned
                comparison_count += 1

        avg_ned = total_ned / comparison_count if comparison_count > 0 else 1.0

        # Factual drift detection
        factual_drift = self.detect_factual_drift(outputs)

        # Overall consistency score (weighted combination)
        consistency_score = (tar * 0.6 + avg_ned * 100 * 0.3 + max(0, 100 - factual_drift * 10) * 0.1)

        # Consensus confidence and output
        confidence = self.calculate_consensus_confidence(tar)
        consensus_output = self.find_consensus_output(outputs)

        return DriftMetrics(
            total_agreement_rate=tar,
            normalized_edit_distance=avg_ned,
            factual_drift_count=factual_drift,
            consistency_score=consistency_score,
            temperature_sensitivity=0,  # Would need multiple temperature runs
            consensus_confidence=confidence,
            consensus_output=consensus_output
        )

    def check_compliance(
        self,
        consistency_score: float,
        temperature: float,
        has_audit_trail: bool,
        framework: ComplianceFramework
    ) -> ComplianceCheck:
        """Check if agent meets compliance requirements for given framework."""
        req = self.compliance_frameworks[framework]
        issues = []
        requirements = {}

        # Check minimum consistency
        meets_consistency = consistency_score >= req["min_consistency"]
        requirements["min_consistency"] = meets_consistency
        if not meets_consistency:
            issues.append(
                f"Consistency score {consistency_score:.1f}% below required {req['min_consistency']}%"
            )

        # Check temperature requirement
        meets_temp = not req["requires_temperature_t0"] or temperature == 0.0
        requirements["temperature_t0"] = meets_temp
        if not meets_temp:
            issues.append(
                f"Temperature must be 0.0 for {req['name']} compliance (current: {temperature})"
            )

        # Check audit trail
        meets_audit = not req["requires_audit_trail"] or has_audit_trail
        requirements["audit_trail"] = meets_audit
        if not meets_audit:
            issues.append(f"Audit trail required for {req['name']} compliance")

        # Calculate overall compliance score
        passed_checks = sum(requirements.values())
        total_checks = len(requirements)
        score = (passed_checks / total_checks) * 100

        return ComplianceCheck(
            framework=framework,
            compliant=len(issues) == 0,
            score=score,
            requirements=requirements,
            issues=issues
        )

    def get_model_tier_from_params(self, parameters: int) -> ModelTier:
        """Determine model tier based on parameter count."""
        if parameters <= 8_000_000_000:  # 8B
            return ModelTier.TIER_1
        elif parameters <= 70_000_000_000:  # 70B
            return ModelTier.TIER_2
        else:
            return ModelTier.TIER_3

    def get_expected_consistency(
        self,
        task_type: TaskType,
        temperature: float,
        model_tier: ModelTier
    ) -> float:
        """Get expected consistency for given task type, temperature, and model."""
        task_info = self.task_types[task_type]

        if temperature == 0.0:
            base_consistency = task_info["consistency_at_t0"]
        elif temperature == 0.2:
            base_consistency = task_info["consistency_at_t02"]
        else:
            # Linear interpolation
            t0_consistency = task_info["consistency_at_t0"]
            t02_consistency = task_info["consistency_at_t02"]
            if t0_consistency is None or t02_consistency is None:
                return None

            ratio = temperature / 0.2
            base_consistency = t0_consistency * (1 - ratio) + t02_consistency * ratio

        if base_consistency is None:
            return None

        # Apply model tier adjustment
        tier_info = self.model_tiers[model_tier]
        tier_multiplier = tier_info["expected_consistency"] / 100

        return base_consistency * tier_multiplier


# Convenience functions
def calculate_drift_metrics(outputs: List[str]) -> DriftMetrics:
    """Calculate drift metrics for a list of outputs."""
    calculator = DriftCalculator()
    return calculator.calculate_metrics(outputs)

def check_compliance(
    consistency_score: float,
    temperature: float,
    has_audit_trail: bool,
    framework: ComplianceFramework
) -> ComplianceCheck:
    """Check compliance for a specific framework."""
    calculator = DriftCalculator()
    return calculator.check_compliance(consistency_score, temperature, has_audit_trail, framework)