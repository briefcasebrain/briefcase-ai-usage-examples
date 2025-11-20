# Drift Analysis Guide

Comprehensive guide to detecting and analyzing AI model output drift using the Briefcase AI Telemetry SDK.

## Overview

Model drift occurs when AI systems start producing outputs that differ from their expected behavior over time. This can happen due to:

- Model degradation
- Data distribution changes
- Environmental factors
- Model updates or fine-tuning
- Infrastructure changes

The SDK provides sophisticated drift detection algorithms to help you:

- **Detect Drift Early**: Identify consistency issues before they impact users
- **Quantify Changes**: Measure the extent and nature of drift
- **Monitor Trends**: Track drift patterns over time
- **Ensure Compliance**: Meet regulatory requirements for model consistency

## Quick Start

### Basic Drift Detection

```python
from briefcase_ai_telemetry import calculate_drift

# Compare model outputs
outputs = [
    "The capital of France is Paris.",
    "France's capital city is Paris.",
    "Paris is the capital of France."
]

metrics = calculate_drift(outputs)
print(f"Agreement rate: {metrics.total_agreement_rate:.1f}%")
print(f"Consensus confidence: {metrics.consensus_confidence}")
```

### Advanced Analysis

```python
from briefcase_ai_telemetry import DriftCalculator

calculator = DriftCalculator()

# Enhanced drift analysis
enhanced_metrics = calculator.calculate_enhanced_metrics(
    outputs,
    context="Geography question about France"
)

print(f"Ensemble drift score: {enhanced_metrics.ensemble_score:.3f}")
print(f"Semantic similarity: {enhanced_metrics.semantic_similarity:.3f}")
```

## Core Concepts

### Types of Drift

#### 1. **Lexical Drift**
Changes in exact wording while preserving meaning:
```python
outputs = [
    "The answer is 42.",
    "The answer is forty-two.",
    "42 is the answer."
]
# Same meaning, different words
```

#### 2. **Semantic Drift**
Changes in meaning or interpretation:
```python
outputs = [
    "The market will likely rise.",
    "The market will probably fall.",
    "The market direction is uncertain."
]
# Different meanings entirely
```

#### 3. **Structural Drift**
Changes in output format or structure:
```python
outputs = [
    "Result: 85%",
    "The result is 85 percent",
    "85% (calculated result)"
]
# Different formatting, same data
```

#### 4. **Factual Drift**
Changes in factual accuracy:
```python
outputs = [
    "Paris is the capital of France.",
    "London is the capital of France.",
    "Berlin is the capital of France."
]
# Factually incorrect variations
```

### Drift Metrics

#### Primary Metrics

1. **Total Agreement Rate**: Percentage of outputs that are identical (0-100%)
2. **Normalized Edit Distance**: String similarity measure (0-1, where 1 = identical)
3. **Consistency Score**: Overall reproducibility rating (0-100)
4. **Consensus Confidence**: Reliability level ('high', 'medium', 'low')

#### Advanced Metrics

1. **Ensemble Drift Score**: Combined metric from multiple algorithms
2. **Semantic Similarity**: Meaning-based similarity score
3. **Statistical Drift**: Statistical measures of variation
4. **Structural Drift**: Format and structure consistency

## Detailed Usage

### Basic Drift Calculation

```python
from briefcase_ai_telemetry import calculate_drift

# Identical outputs (no drift)
identical = ["Hello world"] * 3
metrics = calculate_drift(identical)
assert metrics.total_agreement_rate == 100.0
assert metrics.consensus_confidence == "high"

# Completely different outputs (high drift)
different = ["Hello", "Goodbye", "Maybe"]
metrics = calculate_drift(different)
assert metrics.total_agreement_rate < 50.0
assert metrics.consensus_confidence == "low"
```

### Enhanced Drift Analysis

```python
from briefcase_ai_telemetry import DriftCalculator

calculator = DriftCalculator()

outputs = [
    "Machine learning is a subset of AI.",
    "ML is part of artificial intelligence.",
    "Artificial intelligence includes machine learning."
]

enhanced = calculator.calculate_enhanced_metrics(
    outputs,
    context="Relationship between ML and AI"
)

print(f"Ensemble score: {enhanced.ensemble_score:.3f}")
print(f"Semantic similarity: {enhanced.semantic_similarity:.3f}")
print(f"Drift severity: {enhanced.drift_severity}")
print(f"Recommendations: {enhanced.recommendations}")
```

### Temperature Sensitivity Analysis

```python
# Compare outputs at different temperatures
outputs_t0 = [
    "2 + 2 = 4",
    "2 + 2 = 4",
    "2 + 2 = 4"
]  # Temperature = 0.0 (deterministic)

outputs_t05 = [
    "2 + 2 = 4",
    "2 + 2 equals 4",
    "The sum of 2 and 2 is 4"
]  # Temperature = 0.5 (more variation)

sensitivity = calculator.calculate_temperature_sensitivity(
    outputs_t0,
    outputs_t05
)

print(f"Sensitivity per 0.1 temp unit: {sensitivity:.2f}%")
```

## Real-World Applications

### 1. Code Generation Monitoring

```python
class CodeGenerationMonitor:
    def __init__(self):
        self.calculator = DriftCalculator()
        self.baseline_outputs = []

    def monitor_code_generation(self, prompt, current_outputs):
        """Monitor drift in code generation tasks."""

        # Calculate drift from baseline
        if self.baseline_outputs:
            all_outputs = self.baseline_outputs + current_outputs
            metrics = self.calculator.calculate_metrics(all_outputs)

            if metrics.total_agreement_rate < 70.0:
                return {
                    "alert": "DRIFT_DETECTED",
                    "agreement_rate": metrics.total_agreement_rate,
                    "confidence": metrics.consensus_confidence,
                    "recommendation": "Review model configuration"
                }

        return {"status": "OK", "metrics": metrics}

# Usage
monitor = CodeGenerationMonitor()

# Set baseline (first week of deployment)
baseline = [
    "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)"
]
monitor.baseline_outputs = baseline

# Check current outputs
current = [
    "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)",
    "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
]

result = monitor.monitor_code_generation("fibonacci function", current)
```

### 2. Customer Service Chatbot

```python
class ChatbotDriftMonitor:
    def __init__(self):
        self.calculator = DriftCalculator()

    def analyze_responses(self, question, responses, expected_quality):
        """Analyze chatbot response consistency."""

        metrics = self.calculator.calculate_metrics(responses)

        # Check for concerning drift patterns
        alerts = []

        if metrics.total_agreement_rate < 60.0:
            alerts.append("Low agreement rate - responses vary significantly")

        if metrics.consistency_score < 80.0:
            alerts.append("Consistency below threshold")

        if metrics.consensus_confidence == "low":
            alerts.append("No clear consensus in responses")

        return {
            "metrics": metrics,
            "alerts": alerts,
            "quality_score": self._calculate_quality_score(metrics)
        }

    def _calculate_quality_score(self, metrics):
        """Calculate overall quality score."""
        return (
            metrics.total_agreement_rate * 0.4 +
            metrics.consistency_score * 0.6
        )

# Usage
monitor = ChatbotDriftMonitor()

responses = [
    "I can help you with your account balance. Please provide your account number.",
    "I can assist with checking your account balance. Could you share your account number?",
    "To check your balance, I'll need your account number. Can you provide it?"
]

analysis = monitor.analyze_responses(
    "How can I check my account balance?",
    responses,
    expected_quality=0.9
)
```

### 3. Financial Model Monitoring

```python
class FinancialModelMonitor:
    def __init__(self):
        self.calculator = DriftCalculator()

    def monitor_risk_assessments(self, assessments):
        """Monitor consistency of financial risk assessments."""

        # Extract risk scores and classifications
        risk_scores = [self._extract_score(assessment) for assessment in assessments]
        risk_classifications = [self._extract_classification(assessment) for assessment in assessments]

        # Analyze textual consistency
        text_metrics = self.calculator.calculate_metrics(assessments)

        # Analyze numerical consistency
        score_variance = self._calculate_variance(risk_scores)

        return {
            "text_consistency": text_metrics.consistency_score,
            "agreement_rate": text_metrics.total_agreement_rate,
            "numerical_variance": score_variance,
            "risk_level": self._assess_risk_level(text_metrics, score_variance),
            "compliance_status": self._check_compliance(text_metrics)
        }

    def _extract_score(self, assessment):
        """Extract numerical score from assessment."""
        import re
        match = re.search(r'score[:\s]+(\d+\.?\d*)', assessment, re.IGNORECASE)
        return float(match.group(1)) if match else None

    def _extract_classification(self, assessment):
        """Extract risk classification."""
        classifications = ['low', 'medium', 'high', 'critical']
        assessment_lower = assessment.lower()
        for classification in classifications:
            if classification in assessment_lower:
                return classification
        return 'unknown'

    def _calculate_variance(self, scores):
        """Calculate variance in numerical scores."""
        scores = [s for s in scores if s is not None]
        if len(scores) < 2:
            return 0.0

        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / (len(scores) - 1)
        return variance

    def _assess_risk_level(self, text_metrics, numerical_variance):
        """Assess overall drift risk level."""
        if text_metrics.consistency_score < 95.0 or numerical_variance > 1.0:
            return "HIGH"
        elif text_metrics.consistency_score < 98.0 or numerical_variance > 0.5:
            return "MEDIUM"
        else:
            return "LOW"

    def _check_compliance(self, metrics):
        """Check financial compliance requirements."""
        # Financial models often require high consistency
        return metrics.consistency_score >= 99.0

# Usage
monitor = FinancialModelMonitor()

assessments = [
    "Credit risk assessment: High risk (score: 8.2/10). Recommend manual review.",
    "Credit risk evaluation: High risk (score: 8.1/10). Requires manual review.",
    "Risk assessment: High risk level (score: 8.3/10). Manual review recommended."
]

result = monitor.monitor_risk_assessments(assessments)
```

## Monitoring Workflows

### Continuous Monitoring

```python
import time
from datetime import datetime
from briefcase_ai_telemetry import DriftCalculator

class ContinuousDriftMonitor:
    def __init__(self, window_size=100):
        self.calculator = DriftCalculator()
        self.window_size = window_size
        self.output_history = []
        self.drift_history = []

    def add_output(self, output, metadata=None):
        """Add a new output for monitoring."""
        self.output_history.append({
            'output': output,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        })

        # Keep only recent outputs
        if len(self.output_history) > self.window_size:
            self.output_history.pop(0)

        # Analyze if we have enough data
        if len(self.output_history) >= 10:
            self._analyze_current_window()

    def _analyze_current_window(self):
        """Analyze current window of outputs."""
        recent_outputs = [item['output'] for item in self.output_history[-10:]]

        metrics = self.calculator.calculate_metrics(recent_outputs)

        drift_entry = {
            'timestamp': datetime.now(),
            'agreement_rate': metrics.total_agreement_rate,
            'consistency_score': metrics.consistency_score,
            'confidence': metrics.consensus_confidence,
            'sample_size': len(recent_outputs)
        }

        self.drift_history.append(drift_entry)

        # Check for alerts
        self._check_alerts(drift_entry)

    def _check_alerts(self, current_metrics):
        """Check if alerts should be triggered."""
        if current_metrics['agreement_rate'] < 70.0:
            self._trigger_alert("LOW_AGREEMENT", current_metrics)

        if current_metrics['confidence'] == 'low':
            self._trigger_alert("LOW_CONFIDENCE", current_metrics)

        # Trend analysis
        if len(self.drift_history) >= 5:
            recent_scores = [entry['consistency_score'] for entry in self.drift_history[-5:]]
            if self._is_declining_trend(recent_scores):
                self._trigger_alert("DECLINING_TREND", current_metrics)

    def _is_declining_trend(self, scores):
        """Check if there's a declining trend in scores."""
        if len(scores) < 3:
            return False

        # Simple trend detection: each score lower than previous
        declining_count = 0
        for i in range(1, len(scores)):
            if scores[i] < scores[i-1]:
                declining_count += 1

        return declining_count >= len(scores) - 1

    def _trigger_alert(self, alert_type, metrics):
        """Trigger an alert."""
        print(f"🚨 DRIFT ALERT: {alert_type}")
        print(f"   Agreement Rate: {metrics['agreement_rate']:.1f}%")
        print(f"   Consistency: {metrics['consistency_score']:.1f}")
        print(f"   Confidence: {metrics['confidence']}")
        print(f"   Sample Size: {metrics['sample_size']}")

    def get_drift_summary(self):
        """Get summary of drift patterns."""
        if not self.drift_history:
            return {"status": "No data"}

        recent = self.drift_history[-10:] if len(self.drift_history) >= 10 else self.drift_history

        avg_agreement = sum(entry['agreement_rate'] for entry in recent) / len(recent)
        avg_consistency = sum(entry['consistency_score'] for entry in recent) / len(recent)

        return {
            "average_agreement_rate": avg_agreement,
            "average_consistency": avg_consistency,
            "total_samples": len(self.output_history),
            "monitoring_duration_hours": (
                (datetime.now() - self.drift_history[0]['timestamp']).total_seconds() / 3600
                if self.drift_history else 0
            ),
            "trend": self._assess_overall_trend()
        }

    def _assess_overall_trend(self):
        """Assess overall trend in drift metrics."""
        if len(self.drift_history) < 5:
            return "INSUFFICIENT_DATA"

        recent_scores = [entry['consistency_score'] for entry in self.drift_history[-5:]]
        older_scores = [entry['consistency_score'] for entry in self.drift_history[-10:-5]] if len(self.drift_history) >= 10 else []

        if not older_scores:
            return "INSUFFICIENT_DATA"

        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)

        if recent_avg > older_avg + 2:
            return "IMPROVING"
        elif recent_avg < older_avg - 2:
            return "DECLINING"
        else:
            return "STABLE"

# Usage
monitor = ContinuousDriftMonitor(window_size=50)

# Simulate model outputs over time
outputs = [
    "The answer is 42.",
    "The answer is 42.",
    "42 is the answer.",
    "The answer is forty-two.",
    "Forty-two is the answer.",
    # ... more outputs over time
]

for output in outputs:
    monitor.add_output(output)
    time.sleep(0.1)  # Simulate time passage

summary = monitor.get_drift_summary()
print(f"Drift Summary: {summary}")
```

## Advanced Techniques

### Semantic Drift Detection

```python
from briefcase_ai_telemetry import DriftCalculator

def detect_semantic_drift(outputs, context=None):
    """Advanced semantic drift detection."""
    calculator = DriftCalculator()

    # Use enhanced metrics for semantic analysis
    enhanced_metrics = calculator.calculate_enhanced_metrics(outputs, context)

    semantic_drift_score = 1.0 - enhanced_metrics.semantic_similarity

    # Classify drift severity
    if semantic_drift_score < 0.1:
        severity = "MINIMAL"
    elif semantic_drift_score < 0.3:
        severity = "MODERATE"
    elif semantic_drift_score < 0.6:
        severity = "HIGH"
    else:
        severity = "SEVERE"

    return {
        "semantic_drift_score": semantic_drift_score,
        "severity": severity,
        "ensemble_score": enhanced_metrics.ensemble_score,
        "recommendations": enhanced_metrics.recommendations
    }

# Example: Medical diagnosis drift
medical_outputs = [
    "Diagnosis: Acute bronchitis. Recommend rest and fluids.",
    "Patient has acute bronchitis. Treatment: rest, fluids, monitor symptoms.",
    "Condition: acute respiratory infection. Likely bronchitis. Conservative treatment advised."
]

semantic_analysis = detect_semantic_drift(
    medical_outputs,
    context="Medical diagnosis for respiratory symptoms"
)
```

### Multi-Model Drift Comparison

```python
def compare_model_drift(model_outputs_dict):
    """Compare drift across multiple models."""
    calculator = DriftCalculator()
    results = {}

    for model_name, outputs in model_outputs_dict.items():
        metrics = calculator.calculate_metrics(outputs)
        results[model_name] = {
            "agreement_rate": metrics.total_agreement_rate,
            "consistency_score": metrics.consistency_score,
            "confidence": metrics.consensus_confidence
        }

    # Find most and least consistent models
    most_consistent = max(results, key=lambda m: results[m]["consistency_score"])
    least_consistent = min(results, key=lambda m: results[m]["consistency_score"])

    return {
        "model_results": results,
        "most_consistent": most_consistent,
        "least_consistent": least_consistent,
        "consistency_ranking": sorted(
            results.keys(),
            key=lambda m: results[m]["consistency_score"],
            reverse=True
        )
    }

# Example usage
model_comparisons = {
    "gpt-4": [
        "The capital of France is Paris.",
        "Paris is the capital of France.",
        "France's capital city is Paris."
    ],
    "gpt-3.5-turbo": [
        "The capital of France is Paris.",
        "The capital of France is Paris.",
        "France's capital is Paris."
    ],
    "claude-3": [
        "Paris is the capital of France.",
        "The capital of France is Paris.",
        "Paris serves as France's capital."
    ]
}

comparison_result = compare_model_drift(model_comparisons)
```

## Best Practices

### 1. Establish Baselines
```python
# Set baseline during model deployment
baseline_outputs = collect_initial_outputs(model, test_cases)
baseline_metrics = calculate_drift(baseline_outputs)

# Store for future comparison
save_baseline(model_id, baseline_metrics)
```

### 2. Regular Monitoring
```python
# Daily drift check
def daily_drift_check():
    today_outputs = get_outputs_from_last_24_hours()
    if len(today_outputs) >= 10:
        metrics = calculate_drift(today_outputs)
        if metrics.consistency_score < threshold:
            trigger_alert("DRIFT_DETECTED", metrics)
```

### 3. Context-Aware Analysis
```python
# Include context for better semantic analysis
enhanced_metrics = calculator.calculate_enhanced_metrics(
    outputs,
    context=f"Task: {task_type}, Domain: {domain}, Expected_format: {format}"
)
```

### 4. Trend Analysis
```python
# Track trends over time
def analyze_drift_trends(drift_history):
    windows = [drift_history[i:i+7] for i in range(0, len(drift_history)-6, 7)]
    weekly_averages = [sum(w) / len(w) for w in windows]

    # Detect trends
    if len(weekly_averages) >= 3:
        recent_trend = weekly_averages[-3:]
        if all(recent_trend[i] < recent_trend[i-1] for i in range(1, len(recent_trend))):
            return "DECLINING"

    return "STABLE"
```

### 5. Automated Remediation
```python
def automated_drift_response(drift_metrics):
    """Automated response to drift detection."""
    if drift_metrics.consistency_score < 80:
        # Severe drift detected
        actions = [
            "Switch to backup model",
            "Increase temperature to 0.0",
            "Trigger model retraining",
            "Alert ML team"
        ]
        return execute_actions(actions)
    elif drift_metrics.consistency_score < 90:
        # Moderate drift
        return {"action": "monitor_closely", "frequency": "hourly"}
    else:
        return {"action": "continue_monitoring"}
```

## Troubleshooting

### Common Issues

#### 1. False Positives
High drift alerts for semantically similar outputs:

**Solution**: Use enhanced metrics with context
```python
# Instead of basic calculation
metrics = calculate_drift(outputs)

# Use enhanced analysis
enhanced = calculator.calculate_enhanced_metrics(outputs, context)
```

#### 2. Insufficient Data
Drift calculations on too few samples:

**Solution**: Wait for adequate sample size
```python
if len(outputs) < 10:
    return {"status": "insufficient_data", "required": 10, "current": len(outputs)}
```

#### 3. Noisy Outputs
High variance due to legitimate variation:

**Solution**: Filter by task type or use task-specific thresholds
```python
def get_drift_threshold(task_type):
    thresholds = {
        "creative_writing": 60.0,  # Lower threshold for creative tasks
        "mathematical": 95.0,      # Higher threshold for exact tasks
        "classification": 85.0     # Medium threshold for classification
    }
    return thresholds.get(task_type, 80.0)
```

For more examples and advanced usage patterns, see the [examples directory](../examples/) and [API reference](api-reference.md).