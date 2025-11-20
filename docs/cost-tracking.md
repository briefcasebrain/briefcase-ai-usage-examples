# Cost Tracking Guide

Comprehensive guide to tracking and optimizing AI model costs using the Briefcase AI Telemetry SDK.

## Overview

AI model costs can quickly escalate in production environments. The SDK provides sophisticated cost tracking and optimization tools to help you:

- **Track Real-Time Costs**: Monitor expenses as they occur
- **Compare Models**: Find the most cost-effective options for your use cases
- **Optimize Spending**: Identify opportunities for cost reduction
- **Budget Planning**: Project and plan future AI expenses
- **Cost Attribution**: Understand where your AI budget is being spent

## Quick Start

### Basic Cost Estimation

```python
from briefcase_ai_telemetry import estimate_cost

# Estimate cost for a simple query
cost = estimate_cost(
    model_name="gpt-4",
    input_text="What is machine learning?",
    output_text="Machine learning is a subset of artificial intelligence..."
)

if cost:
    print(f"Estimated cost: ${cost.total_cost:.6f}")
    print(f"Input tokens: {cost.input_tokens}")
    print(f"Output tokens: {cost.output_tokens}")
```

### Advanced Cost Analysis

```python
from briefcase_ai_telemetry import CostCalculator

calculator = CostCalculator()

# Find budget-friendly models
budget_models = calculator.get_models_under_cost(0.01)  # Under 1 cent
print(f"Budget-friendly models: {[m.name for m in budget_models]}")

# Get monthly cost projection
monthly_cost = calculator.calculate_monthly_cost(
    model_name="gpt-4",
    daily_requests=1000,
    avg_input_tokens=100,
    avg_output_tokens=150
)
print(f"Monthly cost: ${monthly_cost:.2f}")
```

## Core Concepts

### Cost Components

#### Token-Based Pricing
Most AI models charge based on token usage:
- **Input Tokens**: Cost for processing input text
- **Output Tokens**: Cost for generating output text
- **Total Cost**: Input cost + Output cost

#### Pricing Tiers
Models typically have different pricing structures:
- **Base Models**: Standard pricing
- **Fine-Tuned Models**: Premium pricing
- **Larger Models**: Higher per-token costs
- **Specialized Models**: Task-specific pricing

### Supported Models

The SDK includes pricing information for popular models:
- **OpenAI**: GPT-4, GPT-3.5-turbo, GPT-3.5-turbo-instruct
- **Anthropic**: Claude-3-sonnet, Claude-3-haiku, Claude-3-opus
- **Custom Models**: Add your own pricing

## Detailed Usage

### Basic Cost Estimation

```python
from briefcase_ai_telemetry import estimate_cost

# Example 1: Short interaction
short_cost = estimate_cost(
    model_name="gpt-3.5-turbo",
    input_text="Hello!",
    output_text="Hello! How can I help you today?"
)

# Example 2: Long analysis
long_input = "Please analyze this comprehensive business report..." * 100
long_output = "Based on the analysis, here are the key findings..." * 50

analysis_cost = estimate_cost(
    model_name="gpt-4",
    input_text=long_input,
    output_text=long_output
)

print(f"Short interaction: ${short_cost.total_cost:.6f}")
print(f"Long analysis: ${analysis_cost.total_cost:.6f}")
```

### Using Exact Token Counts

```python
# When you know exact token counts
precise_cost = estimate_cost(
    model_name="gpt-4",
    input_text="Sample input",
    output_text="Sample output",
    input_tokens=150,    # Exact count
    output_tokens=89     # Exact count
)

print(f"Precise cost: ${precise_cost.total_cost:.6f}")
```

### Model Comparison

```python
from briefcase_ai_telemetry import CostCalculator

calculator = CostCalculator()

# Compare costs across models
models_to_compare = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]
input_text = "Explain quantum computing in simple terms."
output_text = "Quantum computing uses quantum mechanics principles..."

comparison = {}
for model in models_to_compare:
    cost = estimate_cost(model, input_text, output_text)
    if cost:
        comparison[model] = {
            "total_cost": cost.total_cost,
            "cost_per_token": (cost.total_cost / (cost.input_tokens + cost.output_tokens)),
            "input_tokens": cost.input_tokens,
            "output_tokens": cost.output_tokens
        }

# Sort by total cost
sorted_models = sorted(comparison.items(), key=lambda x: x[1]["total_cost"])

print("Cost comparison (cheapest first):")
for model, data in sorted_models:
    print(f"{model}: ${data['total_cost']:.6f}")
```

### Budget Analysis

```python
# Find models within budget
max_budget = 0.01  # 1 cent per request
affordable_models = calculator.get_models_under_cost(max_budget)

print(f"Models under ${max_budget}:")
for model in affordable_models:
    print(f"  {model.name}: Input ${model.input_cost_per_token:.8f}/token, "
          f"Output ${model.output_cost_per_token:.8f}/token")

# Find the cheapest model overall
cheapest = calculator.get_cheapest_model()
if cheapest:
    print(f"Cheapest model: {cheapest.name}")
```

## Real-World Applications

### 1. Cost-Aware Model Selection

```python
class CostAwareModelSelector:
    def __init__(self):
        self.calculator = CostCalculator()

    def select_model(self, input_text, quality_requirement, budget_limit):
        """Select optimal model based on cost and quality requirements."""

        # Get available models within budget
        affordable_models = self.calculator.get_models_under_cost(budget_limit)

        if not affordable_models:
            return {
                "error": "No models within budget",
                "budget": budget_limit,
                "cheapest_available": self.calculator.get_cheapest_model().name
            }

        # Score models based on quality vs cost
        model_scores = []
        for model in affordable_models:
            quality_score = self._get_quality_score(model.name, quality_requirement)
            cost_score = budget_limit - self._estimate_model_cost(model, input_text)

            # Combined score (higher is better)
            combined_score = (quality_score * 0.7) + (cost_score * 0.3)

            model_scores.append({
                "model": model.name,
                "quality_score": quality_score,
                "estimated_cost": self._estimate_model_cost(model, input_text),
                "combined_score": combined_score
            })

        # Select best model
        best_model = max(model_scores, key=lambda x: x["combined_score"])

        return {
            "selected_model": best_model["model"],
            "estimated_cost": best_model["estimated_cost"],
            "quality_score": best_model["quality_score"],
            "alternatives": model_scores
        }

    def _get_quality_score(self, model_name, requirement):
        """Get quality score for model (simplified)."""
        quality_ratings = {
            "gpt-4": 0.95,
            "gpt-3.5-turbo": 0.85,
            "claude-3-sonnet": 0.90,
            "claude-3-haiku": 0.80
        }

        base_score = quality_ratings.get(model_name, 0.75)

        # Adjust based on requirement
        if requirement == "high":
            return base_score
        elif requirement == "medium":
            return min(base_score + 0.1, 1.0)
        else:  # low requirement
            return min(base_score + 0.2, 1.0)

    def _estimate_model_cost(self, model_info, input_text):
        """Estimate cost for model with given input."""
        # Estimate tokens (simplified)
        estimated_input_tokens = len(input_text.split()) * 1.3
        estimated_output_tokens = estimated_input_tokens * 0.5

        return (
            estimated_input_tokens * model_info.input_cost_per_token +
            estimated_output_tokens * model_info.output_cost_per_token
        )

# Usage
selector = CostAwareModelSelector()

selection = selector.select_model(
    input_text="Write a detailed analysis of market trends",
    quality_requirement="high",
    budget_limit=0.05  # 5 cents
)

print(f"Selected model: {selection['selected_model']}")
print(f"Estimated cost: ${selection['estimated_cost']:.6f}")
```

### 2. Usage Monitoring and Alerts

```python
import time
from datetime import datetime, timedelta
from briefcase_ai_telemetry import estimate_cost

class CostMonitor:
    def __init__(self, daily_budget=10.0):
        self.daily_budget = daily_budget
        self.usage_log = []
        self.alerts_sent = set()

    def track_usage(self, model_name, input_text, output_text, user_id=None):
        """Track a model usage event."""
        cost_estimate = estimate_cost(model_name, input_text, output_text)

        if cost_estimate:
            usage_entry = {
                "timestamp": datetime.now(),
                "model": model_name,
                "cost": cost_estimate.total_cost,
                "input_tokens": cost_estimate.input_tokens,
                "output_tokens": cost_estimate.output_tokens,
                "user_id": user_id
            }

            self.usage_log.append(usage_entry)

            # Check for budget alerts
            self._check_budget_alerts()

            return usage_entry

        return None

    def get_daily_usage(self, date=None):
        """Get usage for a specific day."""
        if date is None:
            date = datetime.now().date()

        daily_usage = [
            entry for entry in self.usage_log
            if entry["timestamp"].date() == date
        ]

        total_cost = sum(entry["cost"] for entry in daily_usage)
        total_tokens = sum(
            entry["input_tokens"] + entry["output_tokens"]
            for entry in daily_usage
        )

        return {
            "date": date.isoformat(),
            "total_cost": total_cost,
            "total_requests": len(daily_usage),
            "total_tokens": total_tokens,
            "average_cost_per_request": total_cost / len(daily_usage) if daily_usage else 0,
            "budget_used_percentage": (total_cost / self.daily_budget) * 100,
            "requests": daily_usage
        }

    def _check_budget_alerts(self):
        """Check if budget alerts should be triggered."""
        today_usage = self.get_daily_usage()
        usage_percentage = today_usage["budget_used_percentage"]

        alert_key = f"{datetime.now().date()}"

        # 80% budget alert
        if usage_percentage >= 80 and f"{alert_key}_80" not in self.alerts_sent:
            self._send_alert("BUDGET_80_PERCENT", today_usage)
            self.alerts_sent.add(f"{alert_key}_80")

        # 100% budget alert
        elif usage_percentage >= 100 and f"{alert_key}_100" not in self.alerts_sent:
            self._send_alert("BUDGET_EXCEEDED", today_usage)
            self.alerts_sent.add(f"{alert_key}_100")

    def _send_alert(self, alert_type, usage_data):
        """Send budget alert."""
        if alert_type == "BUDGET_80_PERCENT":
            print(f"🟡 BUDGET WARNING: 80% of daily budget used")
            print(f"   Current usage: ${usage_data['total_cost']:.2f} / ${self.daily_budget:.2f}")
            print(f"   Requests today: {usage_data['total_requests']}")

        elif alert_type == "BUDGET_EXCEEDED":
            print(f"🔴 BUDGET EXCEEDED: Daily budget limit reached")
            print(f"   Current usage: ${usage_data['total_cost']:.2f} / ${self.daily_budget:.2f}")
            print(f"   Overage: ${usage_data['total_cost'] - self.daily_budget:.2f}")

    def get_usage_analytics(self, days=7):
        """Get usage analytics for the past N days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_usage = [
            entry for entry in self.usage_log
            if entry["timestamp"] >= cutoff_date
        ]

        # Group by model
        model_usage = {}
        for entry in recent_usage:
            model = entry["model"]
            if model not in model_usage:
                model_usage[model] = {"cost": 0, "requests": 0, "tokens": 0}

            model_usage[model]["cost"] += entry["cost"]
            model_usage[model]["requests"] += 1
            model_usage[model]["tokens"] += entry["input_tokens"] + entry["output_tokens"]

        # Group by user
        user_usage = {}
        for entry in recent_usage:
            user = entry["user_id"] or "anonymous"
            if user not in user_usage:
                user_usage[user] = {"cost": 0, "requests": 0}

            user_usage[user]["cost"] += entry["cost"]
            user_usage[user]["requests"] += 1

        return {
            "period_days": days,
            "total_cost": sum(entry["cost"] for entry in recent_usage),
            "total_requests": len(recent_usage),
            "model_breakdown": model_usage,
            "user_breakdown": user_usage,
            "daily_average": sum(entry["cost"] for entry in recent_usage) / days
        }

# Usage
monitor = CostMonitor(daily_budget=25.0)

# Track some usage
monitor.track_usage("gpt-4", "Hello", "Hello! How can I help?", user_id="user123")
monitor.track_usage("gpt-3.5-turbo", "Explain AI", "AI is...", user_id="user456")

# Get analytics
daily_stats = monitor.get_daily_usage()
weekly_analytics = monitor.get_usage_analytics(days=7)

print(f"Today's usage: ${daily_stats['total_cost']:.4f}")
print(f"Weekly analytics: {weekly_analytics}")
```

### 3. Monthly Budget Planning

```python
class BudgetPlanner:
    def __init__(self):
        self.calculator = CostCalculator()

    def project_monthly_costs(self, usage_scenarios):
        """Project monthly costs for different usage scenarios."""

        projections = {}

        for scenario_name, scenario_data in usage_scenarios.items():
            model = scenario_data["model"]
            daily_requests = scenario_data["daily_requests"]
            avg_input_tokens = scenario_data["avg_input_tokens"]
            avg_output_tokens = scenario_data["avg_output_tokens"]

            monthly_cost = self.calculator.calculate_monthly_cost(
                model_name=model,
                daily_requests=daily_requests,
                avg_input_tokens=avg_input_tokens,
                avg_output_tokens=avg_output_tokens
            )

            projections[scenario_name] = {
                "monthly_cost": monthly_cost,
                "daily_cost": monthly_cost / 30 if monthly_cost else 0,
                "cost_per_request": (monthly_cost / (daily_requests * 30)) if monthly_cost and daily_requests else 0,
                "model": model,
                "daily_requests": daily_requests
            }

        return projections

    def optimize_for_budget(self, target_monthly_budget, usage_requirements):
        """Find optimal model mix within budget."""

        models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]
        optimizations = []

        for model in models:
            daily_requests = usage_requirements["daily_requests"]
            avg_input = usage_requirements["avg_input_tokens"]
            avg_output = usage_requirements["avg_output_tokens"]

            monthly_cost = self.calculator.calculate_monthly_cost(
                model_name=model,
                daily_requests=daily_requests,
                avg_input_tokens=avg_input,
                avg_output_tokens=avg_output
            )

            if monthly_cost and monthly_cost <= target_monthly_budget:
                optimizations.append({
                    "model": model,
                    "monthly_cost": monthly_cost,
                    "daily_requests_possible": daily_requests,
                    "budget_utilization": (monthly_cost / target_monthly_budget) * 100
                })

            # Also calculate max requests possible within budget
            if monthly_cost:
                cost_per_request = monthly_cost / (daily_requests * 30)
                max_requests_per_month = target_monthly_budget / cost_per_request
                max_daily_requests = max_requests_per_month / 30

                optimizations.append({
                    "model": f"{model} (max requests)",
                    "monthly_cost": target_monthly_budget,
                    "daily_requests_possible": int(max_daily_requests),
                    "budget_utilization": 100.0
                })

        return sorted(optimizations, key=lambda x: x["daily_requests_possible"], reverse=True)

# Usage
planner = BudgetPlanner()

# Define usage scenarios
scenarios = {
    "conservative": {
        "model": "gpt-3.5-turbo",
        "daily_requests": 500,
        "avg_input_tokens": 100,
        "avg_output_tokens": 150
    },
    "moderate": {
        "model": "gpt-4",
        "daily_requests": 200,
        "avg_input_tokens": 200,
        "avg_output_tokens": 300
    },
    "premium": {
        "model": "gpt-4",
        "daily_requests": 1000,
        "avg_input_tokens": 300,
        "avg_output_tokens": 500
    }
}

# Project costs
projections = planner.project_monthly_costs(scenarios)

print("Monthly Cost Projections:")
for scenario, data in projections.items():
    print(f"{scenario}: ${data['monthly_cost']:.2f}/month "
          f"(${data['daily_cost']:.2f}/day, ${data['cost_per_request']:.4f}/request)")

# Optimize for budget
budget_optimizations = planner.optimize_for_budget(
    target_monthly_budget=100.0,
    usage_requirements={
        "daily_requests": 300,
        "avg_input_tokens": 150,
        "avg_output_tokens": 200
    }
)

print("\nBudget Optimizations (within $100/month):")
for opt in budget_optimizations[:3]:  # Top 3 options
    print(f"{opt['model']}: {opt['daily_requests_possible']:.0f} daily requests "
          f"(${opt['monthly_cost']:.2f}/month)")
```

### 4. Custom Model Integration

```python
class CustomModelManager:
    def __init__(self):
        self.calculator = CostCalculator()

    def add_company_models(self):
        """Add company-specific model pricing."""

        # Fine-tuned GPT model
        self.calculator.add_custom_model(
            name="company-gpt-customer-support",
            provider="OpenAI",
            input_cost_per_token=0.00003,  # $0.03 per 1k tokens
            output_cost_per_token=0.00006,  # $0.06 per 1k tokens
            context_length=4096,
            supports_function_calling=True,
            multimodal=False
        )

        # Custom Claude fine-tune
        self.calculator.add_custom_model(
            name="company-claude-legal-analysis",
            provider="Anthropic",
            input_cost_per_token=0.000025,  # $0.025 per 1k tokens
            output_cost_per_token=0.000125,  # $0.125 per 1k tokens
            context_length=8192,
            supports_function_calling=False,
            multimodal=True
        )

        # In-house model (hosted on-premise)
        self.calculator.add_custom_model(
            name="company-internal-classifier",
            provider="Internal",
            input_cost_per_token=0.000001,  # Very low cost for internal
            output_cost_per_token=0.000002,
            context_length=512,
            supports_function_calling=False,
            multimodal=False
        )

    def compare_custom_models(self, input_text, output_text):
        """Compare costs across custom models."""

        custom_models = [
            "company-gpt-customer-support",
            "company-claude-legal-analysis",
            "company-internal-classifier"
        ]

        results = {}

        for model in custom_models:
            cost = estimate_cost(model, input_text, output_text)
            if cost:
                results[model] = {
                    "total_cost": cost.total_cost,
                    "input_tokens": cost.input_tokens,
                    "output_tokens": cost.output_tokens,
                    "cost_breakdown": {
                        "input_cost": cost.input_cost,
                        "output_cost": cost.output_cost
                    }
                }

        return results

    def recommend_model_for_task(self, task_type, volume_per_day):
        """Recommend best model for specific task and volume."""

        task_recommendations = {
            "customer_support": [
                "company-gpt-customer-support",
                "gpt-3.5-turbo"
            ],
            "legal_analysis": [
                "company-claude-legal-analysis",
                "gpt-4"
            ],
            "classification": [
                "company-internal-classifier",
                "gpt-3.5-turbo"
            ]
        }

        models_to_test = task_recommendations.get(task_type, ["gpt-3.5-turbo"])

        # Test with sample data for the task
        sample_inputs = {
            "customer_support": "I have an issue with my order",
            "legal_analysis": "Review this contract for compliance issues",
            "classification": "Classify: This is urgent"
        }

        sample_outputs = {
            "customer_support": "I'd be happy to help with your order. Can you provide your order number?",
            "legal_analysis": "Contract analysis: 3 compliance issues identified...",
            "classification": "Category: urgent, Confidence: 0.95"
        }

        input_text = sample_inputs.get(task_type, "Sample input")
        output_text = sample_outputs.get(task_type, "Sample output")

        recommendations = []

        for model in models_to_test:
            cost = estimate_cost(model, input_text, output_text)
            if cost:
                daily_cost = cost.total_cost * volume_per_day
                monthly_cost = daily_cost * 30

                recommendations.append({
                    "model": model,
                    "cost_per_request": cost.total_cost,
                    "daily_cost": daily_cost,
                    "monthly_cost": monthly_cost,
                    "tokens_per_request": cost.input_tokens + cost.output_tokens
                })

        return sorted(recommendations, key=lambda x: x["monthly_cost"])

# Usage
manager = CustomModelManager()
manager.add_company_models()

# Compare custom models
comparison = manager.compare_custom_models(
    "Analyze customer feedback",
    "Customer sentiment: Positive. Key themes: product quality, fast delivery."
)

print("Custom Model Comparison:")
for model, data in comparison.items():
    print(f"{model}: ${data['total_cost']:.6f}")

# Get recommendations
recommendations = manager.recommend_model_for_task("customer_support", 1000)

print("\nRecommendations for customer support (1000 requests/day):")
for rec in recommendations:
    print(f"{rec['model']}: ${rec['monthly_cost']:.2f}/month")
```

## Advanced Cost Optimization

### Token Optimization Strategies

```python
def optimize_token_usage(input_text, model_name):
    """Optimize token usage to reduce costs."""

    # Strategy 1: Input compression
    compressed_input = compress_input_text(input_text)

    # Strategy 2: Smart truncation
    truncated_input = smart_truncate(input_text, max_tokens=1000)

    # Strategy 3: Preprocessing
    preprocessed_input = preprocess_for_efficiency(input_text)

    # Compare costs
    strategies = {
        "original": input_text,
        "compressed": compressed_input,
        "truncated": truncated_input,
        "preprocessed": preprocessed_input
    }

    results = {}
    for strategy, text in strategies.items():
        # Estimate tokens (simplified)
        estimated_tokens = len(text.split()) * 1.3
        results[strategy] = {
            "text": text,
            "estimated_input_tokens": estimated_tokens,
            "potential_savings": len(input_text) - len(text) if text else 0
        }

    return results

def compress_input_text(text):
    """Compress input text while preserving meaning."""
    # Remove unnecessary words, abbreviate, etc.
    # This is a simplified example
    compressed = text.replace("the ", "").replace(" and ", " & ")
    return compressed

def smart_truncate(text, max_tokens=1000):
    """Intelligently truncate text to stay within token limits."""
    words = text.split()
    estimated_tokens = len(words) * 1.3

    if estimated_tokens <= max_tokens:
        return text

    # Keep important sentences (simplified logic)
    sentences = text.split('.')
    important_sentences = [s for s in sentences if len(s.split()) > 5][:3]

    return '. '.join(important_sentences) + '.'

def preprocess_for_efficiency(text):
    """Preprocess text for better efficiency."""
    # Remove redundancy, format consistently, etc.
    lines = text.split('\n')
    unique_lines = list(dict.fromkeys(lines))  # Remove duplicates
    return '\n'.join(unique_lines)
```

## Best Practices

### 1. Set Up Cost Monitoring

```python
# Always monitor costs in production
monitor = CostMonitor(daily_budget=50.0)

def track_ai_usage(model, input_text, output_text, user_id):
    # Your AI logic here
    result = your_ai_function(model, input_text)

    # Track the cost
    monitor.track_usage(model, input_text, result, user_id)

    return result
```

### 2. Regular Cost Analysis

```python
# Weekly cost review
def weekly_cost_review():
    analytics = monitor.get_usage_analytics(days=7)

    print(f"Weekly spending: ${analytics['total_cost']:.2f}")

    # Check if any model is unexpectedly expensive
    for model, data in analytics['model_breakdown'].items():
        avg_cost_per_request = data['cost'] / data['requests']
        if avg_cost_per_request > expected_cost_per_request:
            print(f"⚠️ {model} costs higher than expected: "
                  f"${avg_cost_per_request:.4f} per request")
```

### 3. Model Selection Strategy

```python
def select_model_by_task(task_type, quality_requirement, budget_constraint):
    """Strategic model selection based on requirements."""

    if task_type == "simple_qa" and quality_requirement == "medium":
        return "gpt-3.5-turbo"  # Cost-effective for simple tasks

    elif task_type == "complex_analysis" and quality_requirement == "high":
        return "gpt-4"  # Higher cost but better quality

    elif task_type == "classification" and budget_constraint == "tight":
        return "company-internal-classifier"  # Custom model for cost savings

    # Default fallback
    return "gpt-3.5-turbo"
```

### 4. Budget Alerts and Controls

```python
# Implement spending controls
def check_budget_before_request(estimated_cost, daily_budget_remaining):
    if estimated_cost > daily_budget_remaining:
        return {
            "allow": False,
            "reason": "Daily budget exceeded",
            "suggested_action": "Use cheaper model or wait until tomorrow"
        }

    return {"allow": True}
```

### 5. Cost Attribution

```python
# Track costs by user, department, or project
def attribute_costs(cost_data, attribution_metadata):
    """Attribute costs to different cost centers."""

    attributions = {}

    for entry in cost_data:
        user_id = entry.get("user_id")
        department = attribution_metadata.get(user_id, {}).get("department", "unknown")
        project = attribution_metadata.get(user_id, {}).get("project", "general")

        key = f"{department}:{project}"

        if key not in attributions:
            attributions[key] = {"cost": 0, "requests": 0}

        attributions[key]["cost"] += entry["cost"]
        attributions[key]["requests"] += 1

    return attributions
```

## Troubleshooting

### Common Cost Issues

#### 1. Unexpectedly High Costs
```python
# Analyze high-cost requests
def analyze_expensive_requests(cost_threshold=0.10):
    expensive_requests = [
        entry for entry in usage_log
        if entry["cost"] > cost_threshold
    ]

    for request in expensive_requests:
        print(f"High cost request: ${request['cost']:.4f}")
        print(f"  Model: {request['model']}")
        print(f"  Tokens: {request['input_tokens']} + {request['output_tokens']}")
        print(f"  User: {request.get('user_id', 'unknown')}")
```

#### 2. Token Count Mismatches
```python
# Compare estimated vs actual token counts
def validate_token_estimates():
    for entry in recent_usage:
        estimated_tokens = len(entry["input_text"].split()) * 1.3
        actual_tokens = entry["input_tokens"]

        if abs(estimated_tokens - actual_tokens) > actual_tokens * 0.2:
            print(f"Token estimate off by >20%: "
                  f"estimated {estimated_tokens}, actual {actual_tokens}")
```

#### 3. Budget Overruns
```python
# Analyze budget overrun patterns
def analyze_budget_overruns():
    daily_usage = get_daily_usage_history(days=30)

    overrun_days = [
        day for day in daily_usage
        if day["total_cost"] > daily_budget
    ]

    if overrun_days:
        avg_overrun = sum(day["total_cost"] - daily_budget for day in overrun_days) / len(overrun_days)
        print(f"Budget overruns: {len(overrun_days)}/30 days")
        print(f"Average overrun: ${avg_overrun:.2f}")
```

For more examples and implementation details, see the [examples directory](../examples/) and [API reference](api-reference.md).