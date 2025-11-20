#!/usr/bin/env python3
"""
Cost Optimization Tool

Real-time cost tracking, analysis, and optimization recommendations for AI model usage.
Demonstrates automatic cost calculation, model comparison, and savings opportunities.

Features:
- Real-time cost tracking across providers
- Cost per query analysis
- Model comparison and recommendations
- Savings opportunity identification
- Cost alerts and budgeting
- Historical cost trends
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Tuple
import sys
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Add SDK path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
import briefcase_ai_telemetry as bai

@dataclass
class CostEntry:
    """Individual cost tracking entry."""
    timestamp: datetime
    model_name: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost: float
    query_type: str
    latency: float

@dataclass
class ModelStats:
    """Statistics for a specific model."""
    name: str
    provider: str
    total_cost: float
    total_queries: int
    total_tokens: int
    avg_cost_per_query: float
    avg_cost_per_1k_tokens: float
    avg_latency: float
    success_rate: float

@dataclass
class CostOptimizationResult:
    """Result of cost optimization analysis."""
    current_cost: float
    potential_savings: float
    savings_percentage: float
    recommendations: List[str]
    alternative_models: List[Dict[str, Any]]
    cost_trends: Dict[str, Any]

class CostOptimizationTool:
    """Tool for analyzing and optimizing AI model costs."""

    def __init__(self, briefcase_api_key: str):
        self.briefcase_api_key = briefcase_api_key
        self.cost_calculator = bai.CostCalculator()
        self.cost_history: deque = deque(maxlen=1000)  # Keep last 1000 entries
        self.model_stats: Dict[str, ModelStats] = {}
        self.daily_budgets: Dict[str, float] = {}  # Date -> budget mapping
        self.alerts_enabled = True
        self.cost_thresholds = {
            'query': 0.05,  # Alert if single query costs more than $0.05
            'daily': 10.0,  # Alert if daily cost exceeds $10
            'hourly': 2.0,  # Alert if hourly cost exceeds $2
        }

    def track_usage(self, model_name: str, provider: str, input_text: str, output_text: str,
                   input_tokens: Optional[int] = None, output_tokens: Optional[int] = None,
                   query_type: str = "general", latency: float = 0.0) -> CostEntry:
        """
        Track usage and calculate cost for a model interaction.

        Args:
            model_name: Name of the AI model
            provider: Provider (openai, anthropic, etc.)
            input_text: Input text to the model
            output_text: Output text from the model
            input_tokens: Actual input tokens (if known)
            output_tokens: Actual output tokens (if known)
            query_type: Type of query (general, coding, analysis, etc.)
            latency: Response latency in seconds

        Returns:
            CostEntry with cost and token information
        """

        # Calculate cost using Rust-based calculator
        cost_estimate = self.cost_calculator.estimate_cost(
            model_name, input_text, output_text, input_tokens, output_tokens
        )

        if cost_estimate:
            cost = cost_estimate.total_cost
            actual_input_tokens = input_tokens or cost_estimate.input_tokens
            actual_output_tokens = output_tokens or cost_estimate.output_tokens
        else:
            # Fallback estimation
            cost = 0.0
            actual_input_tokens = input_tokens or len(input_text.split()) * 1.3  # Rough estimate
            actual_output_tokens = output_tokens or len(output_text.split()) * 1.3

        # Create cost entry
        entry = CostEntry(
            timestamp=datetime.now(),
            model_name=model_name,
            provider=provider,
            input_tokens=int(actual_input_tokens),
            output_tokens=int(actual_output_tokens),
            cost=cost,
            query_type=query_type,
            latency=latency,
        )

        # Add to history
        self.cost_history.append(entry)

        # Update model statistics
        self._update_model_stats(entry)

        # Check for cost alerts
        if self.alerts_enabled:
            self._check_cost_alerts(entry)

        return entry

    def _update_model_stats(self, entry: CostEntry):
        """Update running statistics for a model."""
        model_key = f"{entry.provider}:{entry.model_name}"

        if model_key not in self.model_stats:
            self.model_stats[model_key] = ModelStats(
                name=entry.model_name,
                provider=entry.provider,
                total_cost=0.0,
                total_queries=0,
                total_tokens=0,
                avg_cost_per_query=0.0,
                avg_cost_per_1k_tokens=0.0,
                avg_latency=0.0,
                success_rate=1.0,  # Assume success if we got a cost entry
            )

        stats = self.model_stats[model_key]
        stats.total_cost += entry.cost
        stats.total_queries += 1
        stats.total_tokens += entry.input_tokens + entry.output_tokens
        stats.avg_cost_per_query = stats.total_cost / stats.total_queries
        stats.avg_cost_per_1k_tokens = (stats.total_cost / stats.total_tokens * 1000) if stats.total_tokens > 0 else 0
        stats.avg_latency = ((stats.avg_latency * (stats.total_queries - 1)) + entry.latency) / stats.total_queries

    def _check_cost_alerts(self, entry: CostEntry):
        """Check for cost alerts and warnings."""

        # Single query cost alert
        if entry.cost > self.cost_thresholds['query']:
            print(f"💸 HIGH COST ALERT: Query cost ${entry.cost:.4f} exceeds threshold ${self.cost_thresholds['query']:.4f}")
            print(f"   Model: {entry.model_name} | Tokens: {entry.input_tokens + entry.output_tokens}")

        # Daily cost alert
        today = datetime.now().date()
        today_costs = [e.cost for e in self.cost_history if e.timestamp.date() == today]
        daily_total = sum(today_costs)

        if daily_total > self.cost_thresholds['daily']:
            print(f"📅 DAILY BUDGET ALERT: Today's cost ${daily_total:.2f} exceeds threshold ${self.cost_thresholds['daily']:.2f}")

    def analyze_costs(self, timeframe_hours: int = 24) -> CostOptimizationResult:
        """
        Analyze costs and provide optimization recommendations.

        Args:
            timeframe_hours: Number of hours to analyze (default: 24)

        Returns:
            CostOptimizationResult with analysis and recommendations
        """

        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
        recent_entries = [e for e in self.cost_history if e.timestamp >= cutoff_time]

        if not recent_entries:
            return CostOptimizationResult(
                current_cost=0.0,
                potential_savings=0.0,
                savings_percentage=0.0,
                recommendations=["No usage data available for analysis"],
                alternative_models=[],
                cost_trends={},
            )

        current_cost = sum(e.cost for e in recent_entries)

        # Analyze usage patterns
        model_usage = defaultdict(list)
        query_type_usage = defaultdict(list)

        for entry in recent_entries:
            model_usage[f"{entry.provider}:{entry.model_name}"].append(entry)
            query_type_usage[entry.query_type].append(entry)

        # Generate optimization recommendations
        recommendations = []
        potential_savings = 0.0
        alternative_models = []

        # Recommendation 1: Model downgrade opportunities
        for model_key, entries in model_usage.items():
            if len(entries) < 5:  # Skip models with few queries
                continue

            provider, model_name = model_key.split(':', 1)
            model_cost = sum(e.cost for e in entries)
            model_percentage = (model_cost / current_cost * 100) if current_cost > 0 else 0

            # Check for expensive models that could be downgraded
            if model_percentage > 30 and model_cost > 1.0:  # Significant cost and usage
                if 'gpt-4' in model_name.lower():
                    potential_model_savings = model_cost * 0.7  # 70% potential savings
                    potential_savings += potential_model_savings
                    recommendations.append(
                        f"Consider GPT-3.5 for {len(entries)} queries using {model_name} "
                        f"(potential savings: ${potential_model_savings:.4f})"
                    )
                    alternative_models.append({
                        "current": model_name,
                        "alternative": "gpt-3.5-turbo",
                        "savings": potential_model_savings,
                        "queries": len(entries),
                    })

                elif 'claude-3-opus' in model_name.lower():
                    potential_model_savings = model_cost * 0.6  # 60% potential savings
                    potential_savings += potential_model_savings
                    recommendations.append(
                        f"Consider Claude-3-Sonnet for {len(entries)} queries using {model_name} "
                        f"(potential savings: ${potential_model_savings:.4f})"
                    )
                    alternative_models.append({
                        "current": model_name,
                        "alternative": "claude-3-sonnet",
                        "savings": potential_model_savings,
                        "queries": len(entries),
                    })

        # Recommendation 2: Prompt optimization
        long_input_queries = [e for e in recent_entries if e.input_tokens > 2000]
        if long_input_queries:
            long_input_cost = sum(e.cost for e in long_input_queries)
            prompt_savings = long_input_cost * 0.25  # 25% potential savings from prompt optimization
            potential_savings += prompt_savings
            recommendations.append(
                f"Optimize {len(long_input_queries)} long prompts (>2k tokens) "
                f"for potential savings of ${prompt_savings:.4f}"
            )

        # Recommendation 3: Caching opportunities
        if len(recent_entries) > 10:
            cache_savings = current_cost * 0.15  # 15% potential from caching
            potential_savings += cache_savings
            recommendations.append(
                f"Implement response caching for potential savings of ${cache_savings:.4f} "
                f"(15% of total spend)"
            )

        # Recommendation 4: Batch processing
        if len(recent_entries) > 20:
            batch_savings = current_cost * 0.1  # 10% potential from batching
            potential_savings += batch_savings
            recommendations.append(
                f"Use batch processing for {len(recent_entries)} queries "
                f"for potential savings of ${batch_savings:.4f}"
            )

        # Calculate savings percentage
        savings_percentage = (potential_savings / current_cost * 100) if current_cost > 0 else 0

        # Generate cost trends
        cost_trends = self._calculate_cost_trends(recent_entries, timeframe_hours)

        return CostOptimizationResult(
            current_cost=current_cost,
            potential_savings=potential_savings,
            savings_percentage=savings_percentage,
            recommendations=recommendations,
            alternative_models=alternative_models,
            cost_trends=cost_trends,
        )

    def _calculate_cost_trends(self, entries: List[CostEntry], timeframe_hours: int) -> Dict[str, Any]:
        """Calculate cost trends and patterns."""

        if len(entries) < 2:
            return {}

        # Group by hour
        hourly_costs = defaultdict(float)
        for entry in entries:
            hour_key = entry.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_costs[hour_key] += entry.cost

        # Calculate trend
        hours = sorted(hourly_costs.keys())
        costs = [hourly_costs[hour] for hour in hours]

        if len(costs) >= 2:
            recent_avg = sum(costs[-3:]) / min(3, len(costs))  # Last 3 hours average
            earlier_avg = sum(costs[:-3]) / max(1, len(costs) - 3) if len(costs) > 3 else costs[0]
            trend = "increasing" if recent_avg > earlier_avg * 1.1 else "decreasing" if recent_avg < earlier_avg * 0.9 else "stable"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "hourly_costs": dict(hourly_costs),
            "peak_hour": max(hourly_costs.items(), key=lambda x: x[1]) if hourly_costs else None,
            "avg_hourly_cost": sum(costs) / len(costs) if costs else 0,
        }

    def generate_cost_report(self, timeframe_hours: int = 24) -> str:
        """Generate a comprehensive cost report."""

        analysis = self.analyze_costs(timeframe_hours)

        report = f"""
🏦 AI Cost Optimization Report
═══════════════════════════════════════

⏰ Analysis Period: Last {timeframe_hours} hours
💰 Total Cost: ${analysis.current_cost:.6f}
💡 Potential Savings: ${analysis.potential_savings:.6f} ({analysis.savings_percentage:.1f}%)

📊 Model Usage Breakdown:
─────────────────────────────────────────
"""

        # Add model statistics
        for model_key, stats in sorted(self.model_stats.items(), key=lambda x: x[1].total_cost, reverse=True):
            percentage = (stats.total_cost / analysis.current_cost * 100) if analysis.current_cost > 0 else 0
            report += f"""
🤖 {stats.name} ({stats.provider}):
   💰 Cost: ${stats.total_cost:.6f} ({percentage:.1f}%)
   📊 Queries: {stats.total_queries}
   💵 Avg/Query: ${stats.avg_cost_per_query:.6f}
   🔤 Cost/1K Tokens: ${stats.avg_cost_per_1k_tokens:.6f}
   ⚡ Avg Latency: {stats.avg_latency:.2f}s
"""

        report += f"""
💡 Optimization Recommendations:
─────────────────────────────────────────
"""

        for i, rec in enumerate(analysis.recommendations, 1):
            report += f"{i}. {rec}\n"

        # Add cost trends
        if analysis.cost_trends:
            trend = analysis.cost_trends.get('trend', 'unknown')
            peak_hour = analysis.cost_trends.get('peak_hour')
            avg_hourly = analysis.cost_trends.get('avg_hourly_cost', 0)

            report += f"""
📈 Cost Trends:
─────────────────────────────────────────
Trend: {trend.upper()}
Average hourly cost: ${avg_hourly:.6f}
"""
            if peak_hour:
                report += f"Peak hour: {peak_hour[0]} (${peak_hour[1]:.6f})\n"

        # Alternative models
        if analysis.alternative_models:
            report += f"""
🔄 Alternative Model Recommendations:
─────────────────────────────────────────
"""
            for alt in analysis.alternative_models:
                report += f"""
Replace {alt['current']} → {alt['alternative']}
   Affected queries: {alt['queries']}
   Potential savings: ${alt['savings']:.6f}
"""

        return report

    def simulate_model_replacement(self, current_model: str, new_model: str, timeframe_hours: int = 24) -> Dict[str, Any]:
        """
        Simulate the cost impact of replacing one model with another.

        Args:
            current_model: Current model name
            new_model: New model to simulate
            timeframe_hours: Hours of data to simulate

        Returns:
            Dictionary with simulation results
        """

        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
        relevant_entries = [
            e for e in self.cost_history
            if e.timestamp >= cutoff_time and current_model in e.model_name
        ]

        if not relevant_entries:
            return {"error": f"No usage data found for {current_model}"}

        current_cost = sum(e.cost for e in relevant_entries)

        # Simulate new costs
        simulated_cost = 0.0
        for entry in relevant_entries:
            # Reconstruct approximate input/output for cost calculation
            input_text = "x" * entry.input_tokens  # Approximate
            output_text = "x" * entry.output_tokens  # Approximate

            new_cost_estimate = self.cost_calculator.estimate_cost(
                new_model, input_text, output_text, entry.input_tokens, entry.output_tokens
            )

            if new_cost_estimate:
                simulated_cost += new_cost_estimate.total_cost
            else:
                simulated_cost += entry.cost  # Fallback to original cost

        savings = current_cost - simulated_cost
        savings_percentage = (savings / current_cost * 100) if current_cost > 0 else 0

        return {
            "current_model": current_model,
            "new_model": new_model,
            "queries_affected": len(relevant_entries),
            "current_cost": current_cost,
            "simulated_cost": simulated_cost,
            "savings": savings,
            "savings_percentage": savings_percentage,
            "recommendation": "beneficial" if savings > 0 else "not_recommended",
        }

    def set_budget(self, daily_budget: float):
        """Set daily cost budget."""
        today = datetime.now().date().isoformat()
        self.daily_budgets[today] = daily_budget
        self.cost_thresholds['daily'] = daily_budget
        print(f"💰 Daily budget set to ${daily_budget:.2f}")

    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        today = datetime.now().date()
        today_costs = [e.cost for e in self.cost_history if e.timestamp.date() == today]
        daily_total = sum(today_costs)

        daily_budget = self.cost_thresholds.get('daily', 0)

        return {
            "daily_budget": daily_budget,
            "current_spend": daily_total,
            "remaining_budget": max(0, daily_budget - daily_total),
            "budget_used_percentage": (daily_total / daily_budget * 100) if daily_budget > 0 else 0,
            "queries_today": len(today_costs),
        }

async def demo_cost_optimization():
    """Demonstration of the cost optimization tool."""

    print("🏦 AI Cost Optimization Tool Demo")
    print("=" * 50)

    # Initialize the tool
    tool = CostOptimizationTool("your-briefcase-ai-api-key")

    # Set a daily budget
    tool.set_budget(5.0)  # $5 daily budget

    # Simulate some usage data
    print("\n📊 Simulating AI model usage...")

    # Sample interactions with different models
    interactions = [
        ("gpt-4", "openai", "Write a detailed analysis of renewable energy trends", "Renewable energy has seen significant growth...", "analysis"),
        ("gpt-3.5-turbo", "openai", "What is 2+2?", "2+2 equals 4.", "simple"),
        ("claude-3-sonnet", "anthropic", "Explain quantum computing", "Quantum computing is a revolutionary technology...", "explanation"),
        ("gpt-4", "openai", "Create a comprehensive business plan for a startup", "Executive Summary: This business plan outlines...", "business"),
        ("claude-3-opus", "anthropic", "Analyze this complex dataset", "Based on the statistical analysis of the dataset...", "analysis"),
        ("gpt-3.5-turbo", "openai", "Hello", "Hello! How can I help you today?", "greeting"),
        ("gpt-4", "openai", "Debug this Python code with detailed explanation", "I can see several issues in your code...", "coding"),
    ]

    for model, provider, input_text, output_text, query_type in interactions:
        # Simulate latency
        latency = 0.5 + (len(output_text) / 1000)  # Rough latency simulation

        entry = tool.track_usage(
            model_name=model,
            provider=provider,
            input_text=input_text,
            output_text=output_text,
            query_type=query_type,
            latency=latency,
        )

        print(f"💰 {model}: ${entry.cost:.6f} ({entry.input_tokens + entry.output_tokens} tokens)")

    print(f"\n📊 Total Usage: {len(tool.cost_history)} queries")

    # Generate optimization analysis
    print("\n🔍 Analyzing costs and generating recommendations...")
    analysis = tool.analyze_costs(timeframe_hours=24)

    print(f"\n💰 Current Cost: ${analysis.current_cost:.6f}")
    print(f"💡 Potential Savings: ${analysis.potential_savings:.6f} ({analysis.savings_percentage:.1f}%)")

    print("\n💡 Top Recommendations:")
    for i, rec in enumerate(analysis.recommendations[:3], 1):
        print(f"{i}. {rec}")

    # Show budget status
    budget_status = tool.get_budget_status()
    print(f"\n💳 Budget Status:")
    print(f"Daily Budget: ${budget_status['daily_budget']:.2f}")
    print(f"Current Spend: ${budget_status['current_spend']:.6f}")
    print(f"Budget Used: {budget_status['budget_used_percentage']:.1f}%")

    # Simulate model replacement
    print("\n🔄 Simulating GPT-4 → GPT-3.5 replacement...")
    simulation = tool.simulate_model_replacement("gpt-4", "gpt-3.5-turbo")

    if "error" not in simulation:
        print(f"Queries Affected: {simulation['queries_affected']}")
        print(f"Current Cost: ${simulation['current_cost']:.6f}")
        print(f"Simulated Cost: ${simulation['simulated_cost']:.6f}")
        print(f"Potential Savings: ${simulation['savings']:.6f} ({simulation['savings_percentage']:.1f}%)")
        print(f"Recommendation: {simulation['recommendation']}")

    # Generate full report
    print("\n📋 Generating comprehensive cost report...")
    report = tool.generate_cost_report()

    # Save report to file
    with open("cost_optimization_report.txt", "w") as f:
        f.write(report)

    print("💾 Report saved to: cost_optimization_report.txt")
    print("\n✅ Cost optimization analysis complete!")

if __name__ == "__main__":
    asyncio.run(demo_cost_optimization())