"""
Analysis command for drift detection and cost optimization.

Provides detailed analysis of agent performance, drift patterns, and cost optimization recommendations.
"""

import click
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys
import os

# Add the SDK to the Python path
current_dir = os.path.dirname(__file__)
sdk_path = os.path.join(current_dir, '..', '..', '..', 'python')
sys.path.insert(0, sdk_path)

import briefcase_ai_telemetry as bai

@click.group()
def analyze():
    """
    📊 Analyze AI agent performance and behavior.

    Provides detailed analysis of drift detection, cost optimization,
    and performance patterns for your AI agents.
    """
    pass

@analyze.command()
@click.option('--input', 'input_file', type=click.Path(exists=True),
              help='Input file with agent outputs (CSV or JSON)')
@click.option('--output', 'output_file', type=click.Path(),
              help='Output file for analysis results')
@click.option('--threshold', type=float, default=0.7,
              help='Drift detection threshold (0.0-1.0)')
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv', 'text']), default='text',
              help='Output format for results')
@click.option('--algorithm', type=click.Choice(['tar', 'edit_distance', 'semantic', 'all']), default='all',
              help='Drift detection algorithm to use')
def drift(input_file, output_file, threshold, output_format, algorithm):
    """
    🎯 Analyze drift in agent outputs.

    Detect behavioral drift and consistency issues in AI agent responses.
    Supports multiple algorithms for comprehensive drift analysis.
    """

    click.echo("🎯 Drift Analysis")
    click.echo("=" * 40)

    # Load input data
    if input_file:
        outputs = load_outputs_from_file(input_file)
    else:
        # Demo data
        outputs = [
            "The capital of France is Paris.",
            "Paris is the capital of France.",
            "France's capital city is Paris.",
            "The capital is Paris.",
            "London is the capital of England."  # This should show drift
        ]
        click.echo("📝 Using demo data (5 sample outputs)")

    if len(outputs) < 2:
        click.echo("❌ Need at least 2 outputs for drift analysis")
        return

    click.echo(f"📊 Analyzing {len(outputs)} outputs with threshold {threshold}")

    # Run drift analysis
    metrics = bai.calculate_drift(outputs)

    # Display results
    display_drift_analysis(metrics, threshold, algorithm)

    # Save results if requested
    if output_file:
        save_analysis_results(metrics, output_file, output_format, 'drift')
        click.echo(f"💾 Results saved to: {output_file}")

def display_drift_analysis(metrics, threshold: float, algorithm: str):
    """Display drift analysis results."""

    click.echo("\n📊 Drift Analysis Results:")
    click.echo("─" * 40)

    # Overall score
    tar_score = metrics.total_agreement_rate
    consistency_score = metrics.consistency_score

    # Color coding based on threshold
    tar_color = 'green' if tar_score >= threshold else 'yellow' if tar_score >= threshold - 0.1 else 'red'
    consistency_color = 'green' if consistency_score >= threshold else 'yellow' if consistency_score >= threshold - 0.1 else 'red'

    click.echo(f"📈 Total Agreement Rate: {click.style(f'{tar_score:.3f}', fg=tar_color, bold=True)}")
    click.echo(f"🎯 Consistency Score: {click.style(f'{consistency_score:.3f}', fg=consistency_color, bold=True)}")
    click.echo(f"🔄 Normalized Edit Distance: {metrics.normalized_edit_distance:.3f}")

    # Consensus information
    if hasattr(metrics, 'consensus_output') and metrics.consensus_output:
        click.echo(f"🤝 Consensus Output: \"{metrics.consensus_output[:100]}{'...' if len(metrics.consensus_output) > 100 else ''}\"")
        click.echo(f"🔒 Consensus Confidence: {metrics.consensus_confidence:.3f}")

    # Temperature sensitivity (if available)
    if hasattr(metrics, 'temperature_sensitivity'):
        click.echo(f"🌡️  Temperature Sensitivity: {metrics.temperature_sensitivity:.3f}")

    # Factual drift count (if available)
    if hasattr(metrics, 'factual_drift_count'):
        click.echo(f"📚 Factual Drift Count: {metrics.factual_drift_count}")

    # Interpretation and recommendations
    click.echo("\n💡 Interpretation:")

    if tar_score >= threshold:
        click.echo(click.style("✅ Low drift detected - outputs are consistent", fg='green'))
    elif tar_score >= threshold - 0.1:
        click.echo(click.style("⚠️  Moderate drift detected - monitor closely", fg='yellow'))
    else:
        click.echo(click.style("❌ High drift detected - review model behavior", fg='red'))

    # Recommendations
    click.echo("\n🔧 Recommendations:")
    if tar_score < threshold:
        click.echo("   • Review prompt engineering and consistency")
        click.echo("   • Consider reducing model temperature")
        click.echo("   • Implement consensus mode for critical decisions")
        click.echo("   • Monitor for data quality issues")

    if consistency_score < 0.8:
        click.echo("   • Add output format constraints")
        click.echo("   • Use structured output formats (JSON, XML)")
        click.echo("   • Implement post-processing validation")

@analyze.command()
@click.option('--model', help='Specific model to analyze')
@click.option('--timeframe', default='24h', help='Timeframe for analysis (24h, 7d, 30d)')
@click.option('--output', 'output_file', type=click.Path(), help='Output file for cost analysis')
@click.option('--breakdown', is_flag=True, help='Show detailed cost breakdown')
@click.option('--recommendations', is_flag=True, default=True, help='Include optimization recommendations')
def cost(model, timeframe, output_file, breakdown, recommendations):
    """
    💰 Analyze costs and suggest optimizations.

    Analyze AI model usage costs, identify expensive operations,
    and provide optimization recommendations.
    """

    click.echo("💰 Cost Analysis")
    click.echo("=" * 40)

    # Demo cost data (in production, this would query the telemetry service)
    cost_data = {
        'gpt-4': {'total_cost': 15.67, 'requests': 1234, 'tokens': 1500000},
        'gpt-3.5-turbo': {'total_cost': 3.42, 'requests': 5678, 'tokens': 3200000},
        'claude-3-sonnet': {'total_cost': 8.91, 'requests': 567, 'tokens': 890000},
    }

    total_cost = sum(data['total_cost'] for data in cost_data.values())
    total_requests = sum(data['requests'] for data in cost_data.values())
    total_tokens = sum(data['tokens'] for data in cost_data.values())

    click.echo(f"📊 Total Cost ({timeframe}): {click.style(f'${total_cost:.2f}', fg='cyan', bold=True)}")
    click.echo(f"📈 Total Requests: {total_requests:,}")
    click.echo(f"🔤 Total Tokens: {total_tokens:,}")
    click.echo(f"💵 Average Cost/Request: ${total_cost/total_requests:.4f}")

    if breakdown:
        display_cost_breakdown(cost_data)

    if recommendations:
        display_cost_recommendations(cost_data, total_cost)

    # Save results if requested
    if output_file:
        save_cost_analysis(cost_data, output_file, timeframe)
        click.echo(f"💾 Cost analysis saved to: {output_file}")

def display_cost_breakdown(cost_data: Dict[str, Dict[str, Any]]):
    """Display detailed cost breakdown by model."""

    click.echo("\n📋 Cost Breakdown by Model:")
    click.echo("─" * 40)

    # Sort by cost (highest first)
    sorted_models = sorted(cost_data.items(), key=lambda x: x[1]['total_cost'], reverse=True)

    for model, data in sorted_models:
        cost = data['total_cost']
        requests = data['requests']
        tokens = data['tokens']
        cost_per_request = cost / requests if requests > 0 else 0
        cost_per_token = (cost / tokens * 1000) if tokens > 0 else 0

        click.echo(f"🤖 {model}:")
        click.echo(f"   💰 Total: ${cost:.2f}")
        click.echo(f"   📊 Requests: {requests:,}")
        click.echo(f"   🔤 Tokens: {tokens:,}")
        click.echo(f"   💵 Cost/Request: ${cost_per_request:.4f}")
        click.echo(f"   🎯 Cost/1K Tokens: ${cost_per_token:.4f}")
        click.echo()

def display_cost_recommendations(cost_data: Dict[str, Dict[str, Any]], total_cost: float):
    """Display cost optimization recommendations."""

    click.echo("🔧 Cost Optimization Recommendations:")
    click.echo("─" * 40)

    # Find most expensive model
    most_expensive = max(cost_data.items(), key=lambda x: x[1]['total_cost'])
    model_name, model_data = most_expensive

    savings_potential = 0

    # Recommendation 1: Model optimization
    if 'gpt-4' in cost_data and 'gpt-3.5-turbo' in cost_data:
        gpt4_cost = cost_data['gpt-4']['total_cost']
        gpt35_cost = cost_data['gpt-3.5-turbo']['total_cost']

        if gpt4_cost > gpt35_cost * 2:
            potential_savings = gpt4_cost * 0.7  # Assume 70% could use cheaper model
            savings_potential += potential_savings
            click.echo(f"1. 🔄 Model Downgrade Opportunity:")
            click.echo(f"   • Consider GPT-3.5 for simpler tasks")
            click.echo(f"   • Potential savings: ${potential_savings:.2f} (30-50%)")
            click.echo()

    # Recommendation 2: Prompt optimization
    click.echo(f"2. ✏️  Prompt Optimization:")
    click.echo(f"   • Reduce input token count with concise prompts")
    click.echo(f"   • Use system messages efficiently")
    click.echo(f"   • Potential savings: 15-25%")
    click.echo()

    # Recommendation 3: Caching
    click.echo(f"3. 💾 Response Caching:")
    click.echo(f"   • Cache common queries and responses")
    click.echo(f"   • Implement semantic similarity matching")
    click.echo(f"   • Potential savings: 20-40%")
    click.echo()

    # Recommendation 4: Batch processing
    click.echo(f"4. 📦 Batch Processing:")
    click.echo(f"   • Group similar requests together")
    click.echo(f"   • Use async processing for non-urgent requests")
    click.echo(f"   • Potential savings: 10-15%")
    click.echo()

    # Summary
    total_potential = total_cost * 0.4  # Conservative 40% potential savings
    click.echo(f"💡 Total Potential Savings: ${total_potential:.2f} (40% of current spend)")

@analyze.command()
@click.option('--agent-id', type=int, help='Analyze specific agent ID')
@click.option('--timeframe', default='24h', help='Timeframe for analysis')
@click.option('--metric', type=click.Choice(['latency', 'accuracy', 'cost', 'errors']),
              default='latency', help='Primary metric to analyze')
@click.option('--output', 'output_file', type=click.Path(), help='Output file for performance analysis')
def performance(agent_id, timeframe, metric, output_file):
    """
    ⚡ Analyze agent performance metrics.

    Analyze latency, accuracy, error rates, and other performance
    metrics for your AI agents.
    """

    click.echo("⚡ Performance Analysis")
    click.echo("=" * 40)

    if agent_id:
        click.echo(f"🎯 Analyzing Agent {agent_id}")
    else:
        click.echo("📊 Analyzing All Agents")

    click.echo(f"⏰ Timeframe: {timeframe}")
    click.echo(f"📏 Primary Metric: {metric}")

    # Demo performance data
    perf_data = {
        'avg_latency': 245.6,  # ms
        'p95_latency': 456.2,
        'p99_latency': 1234.5,
        'error_rate': 2.3,  # %
        'accuracy': 94.7,  # %
        'throughput': 45.2,  # requests/minute
        'total_requests': 12567
    }

    click.echo("\n📊 Performance Summary:")
    click.echo("─" * 40)

    # Latency metrics
    latency_color = 'green' if perf_data['avg_latency'] < 200 else 'yellow' if perf_data['avg_latency'] < 500 else 'red'
    click.echo(f"⚡ Average Latency: {click.style(f\"{perf_data['avg_latency']:.1f}ms\", fg=latency_color, bold=True)}")
    click.echo(f"📈 P95 Latency: {perf_data['p95_latency']:.1f}ms")
    click.echo(f"📊 P99 Latency: {perf_data['p99_latency']:.1f}ms")

    # Error rate
    error_color = 'green' if perf_data['error_rate'] < 1 else 'yellow' if perf_data['error_rate'] < 5 else 'red'
    click.echo(f"❗ Error Rate: {click.style(f\"{perf_data['error_rate']:.1f}%\", fg=error_color, bold=True)}")

    # Accuracy
    accuracy_color = 'green' if perf_data['accuracy'] > 95 else 'yellow' if perf_data['accuracy'] > 90 else 'red'
    click.echo(f"🎯 Accuracy: {click.style(f\"{perf_data['accuracy']:.1f}%\", fg=accuracy_color, bold=True)}")

    # Throughput
    click.echo(f"🚀 Throughput: {perf_data['throughput']:.1f} req/min")
    click.echo(f"📈 Total Requests: {perf_data['total_requests']:,}")

    # Performance recommendations
    click.echo("\n🔧 Performance Recommendations:")
    click.echo("─" * 40)

    if perf_data['avg_latency'] > 500:
        click.echo("⚡ High Latency Issues:")
        click.echo("   • Consider model optimization or caching")
        click.echo("   • Review network connectivity")
        click.echo("   • Implement request batching")

    if perf_data['error_rate'] > 3:
        click.echo("❗ High Error Rate:")
        click.echo("   • Review error logs for patterns")
        click.echo("   • Implement better retry logic")
        click.echo("   • Check API rate limits and quotas")

    if perf_data['accuracy'] < 90:
        click.echo("🎯 Low Accuracy:")
        click.echo("   • Review prompt engineering")
        click.echo("   • Consider fine-tuning or better models")
        click.echo("   • Implement output validation")

def load_outputs_from_file(file_path: str) -> List[str]:
    """Load agent outputs from CSV or JSON file."""

    path = Path(file_path)

    if path.suffix.lower() == '.csv':
        outputs = []
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try common column names
                output = row.get('output') or row.get('response') or row.get('text') or list(row.values())[0]
                outputs.append(str(output))
        return outputs

    elif path.suffix.lower() == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(item) for item in data]
            elif isinstance(data, dict) and 'outputs' in data:
                return [str(output) for output in data['outputs']]
            else:
                # Assume it's a list of objects with some text field
                outputs = []
                for item in data.values() if isinstance(data, dict) else data:
                    if isinstance(item, dict):
                        text = item.get('output') or item.get('response') or item.get('text') or str(item)
                        outputs.append(text)
                return outputs

    else:
        # Assume plain text file with one output per line
        with open(path, 'r') as f:
            return [line.strip() for line in f if line.strip()]

def save_analysis_results(metrics, output_file: str, format_type: str, analysis_type: str):
    """Save analysis results to file."""

    results = {
        'analysis_type': analysis_type,
        'timestamp': datetime.now().isoformat(),
        'metrics': {
            'total_agreement_rate': metrics.total_agreement_rate,
            'consistency_score': metrics.consistency_score,
            'normalized_edit_distance': metrics.normalized_edit_distance,
        }
    }

    # Add additional metrics if available
    for attr in ['consensus_output', 'consensus_confidence', 'temperature_sensitivity', 'factual_drift_count']:
        if hasattr(metrics, attr):
            results['metrics'][attr] = getattr(metrics, attr)

    if format_type == 'json':
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    elif format_type == 'csv':
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['metric', 'value'])
            writer.writeheader()
            for metric, value in results['metrics'].items():
                writer.writerow({'metric': metric, 'value': value})
    else:  # text
        with open(output_file, 'w') as f:
            f.write(f"Briefcase AI {analysis_type.title()} Analysis\n")
            f.write(f"Generated: {results['timestamp']}\n\n")
            for metric, value in results['metrics'].items():
                f.write(f"{metric}: {value}\n")

def save_cost_analysis(cost_data: Dict[str, Dict], output_file: str, timeframe: str):
    """Save cost analysis to file."""

    results = {
        'analysis_type': 'cost',
        'timeframe': timeframe,
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_cost': sum(data['total_cost'] for data in cost_data.values()),
            'total_requests': sum(data['requests'] for data in cost_data.values()),
            'total_tokens': sum(data['tokens'] for data in cost_data.values()),
        },
        'by_model': cost_data
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)