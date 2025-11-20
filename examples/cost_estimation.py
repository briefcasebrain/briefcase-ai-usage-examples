#!/usr/bin/env python3
"""
Cost Estimation Example

This example demonstrates AI model cost tracking including:
- Basic cost estimation for various models
- Token counting and pricing
- Model comparison and selection
- Budget optimization
- Monthly cost projection
"""

from briefcase_ai_telemetry import (
    estimate_cost, CostCalculator, CostEstimate
)


def basic_cost_examples():
    """Basic cost estimation for different models."""
    print("=== Basic Cost Estimation ===")

    # Sample texts of different lengths
    short_input = "What is AI?"
    short_output = "AI is artificial intelligence."

    medium_input = "Explain machine learning in detail."
    medium_output = """Machine learning is a subset of artificial intelligence that enables
    computers to learn and improve from experience without being explicitly programmed.
    It uses algorithms and statistical models to analyze and draw insights from data patterns."""

    long_input = """Write a comprehensive analysis of the impact of artificial intelligence
    on modern society, including its benefits, challenges, and future implications
    across different sectors like healthcare, education, finance, and transportation."""

    long_output = """Artificial intelligence has fundamentally transformed modern society across
    multiple dimensions. In healthcare, AI has revolutionized diagnostic accuracy through medical
    imaging analysis, drug discovery acceleration, and personalized treatment recommendations.
    Educational technology now leverages AI for adaptive learning systems, automated grading,
    and personalized curricula that adapt to individual student needs and learning styles.

    The financial sector has embraced AI for fraud detection, algorithmic trading, risk assessment,
    and customer service automation through chatbots and virtual assistants. Transportation has
    seen remarkable advances with autonomous vehicles, traffic optimization systems, and predictive
    maintenance for public transit networks.

    However, these benefits come with significant challenges including job displacement concerns,
    privacy and data security issues, algorithmic bias, and the need for robust regulatory frameworks.
    The future implications suggest an increasingly interconnected world where AI systems become
    more sophisticated, requiring careful consideration of ethical guidelines, transparency in
    decision-making processes, and ensuring equitable access to AI benefits across all
    socioeconomic segments of society."""

    models_to_test = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]
    text_scenarios = [
        ("Short", short_input, short_output),
        ("Medium", medium_input, medium_output),
        ("Long", long_input, long_output)
    ]

    print("\nCost comparison across models and text lengths:")
    print("-" * 80)
    print(f"{'Scenario':<10} {'Model':<15} {'Input Tokens':<12} {'Output Tokens':<13} {'Cost ($)':<10}")
    print("-" * 80)

    for scenario_name, input_text, output_text in text_scenarios:
        for model in models_to_test:
            cost = estimate_cost(model, input_text, output_text)
            if cost:
                print(f"{scenario_name:<10} {model:<15} {cost.input_tokens:<12} {cost.output_tokens:<13} ${cost.total_cost:<9.6f}")
            else:
                print(f"{scenario_name:<10} {model:<15} {'N/A':<12} {'N/A':<13} {'N/A':<10}")


def advanced_cost_analysis():
    """Advanced cost analysis and optimization."""
    print("\n=== Advanced Cost Analysis ===")

    calculator = CostCalculator()

    # Find models within budget
    budget_limits = [0.001, 0.01, 0.1]  # Different budget levels

    for budget in budget_limits:
        models_in_budget = calculator.get_models_under_cost(budget)
        print(f"\nModels under ${budget} per request:")
        for model in models_in_budget:
            print(f"   {model.name}: Input ${model.input_cost_per_token:.8f}/token, "
                  f"Output ${model.output_cost_per_token:.8f}/token")

    # Find cheapest models
    cheapest_overall = calculator.get_cheapest_model()
    cheapest_by_provider = calculator.list_models_by_provider()

    print(f"\nCheapest model overall: {cheapest_overall.name if cheapest_overall else 'N/A'}")

    print(f"\nModels by provider:")
    for provider, models in cheapest_by_provider.items():
        print(f"   {provider}: {len(models)} models")
        if models:
            cheapest = min(models, key=lambda m: m.input_cost_per_token + m.output_cost_per_token)
            print(f"     Cheapest: {cheapest.name}")


def cost_with_explicit_tokens():
    """Cost estimation with known token counts."""
    print("\n=== Cost with Explicit Token Counts ===")

    # Scenarios where you already know the exact token counts
    scenarios = [
        ("GPT-4", "gpt-4", "Analyze this data", "Analysis complete", 100, 50),
        ("GPT-3.5", "gpt-3.5-turbo", "Simple question", "Simple answer", 25, 15),
        ("Claude", "claude-3-sonnet", "Complex reasoning", "Detailed explanation", 200, 300),
    ]

    print(f"{'Model':<12} {'Input':<15} {'Output':<20} {'Tokens (I/O)':<15} {'Cost ($)':<10}")
    print("-" * 75)

    for name, model, input_text, output_text, input_tokens, output_tokens in scenarios:
        cost = estimate_cost(
            model_name=model,
            input_text=input_text,
            output_text=output_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        if cost:
            tokens_str = f"{input_tokens}/{output_tokens}"
            print(f"{name:<12} {input_text[:14]:<15} {output_text[:19]:<20} {tokens_str:<15} ${cost.total_cost:<9.6f}")


def monthly_cost_projection():
    """Project monthly costs based on usage patterns."""
    print("\n=== Monthly Cost Projection ===")

    calculator = CostCalculator()

    # Define usage scenarios
    usage_scenarios = [
        {
            "name": "Light Usage",
            "requests_per_day": 100,
            "avg_input_tokens": 50,
            "avg_output_tokens": 30
        },
        {
            "name": "Medium Usage",
            "requests_per_day": 1000,
            "avg_input_tokens": 150,
            "avg_output_tokens": 100
        },
        {
            "name": "Heavy Usage",
            "requests_per_day": 10000,
            "avg_input_tokens": 300,
            "avg_output_tokens": 200
        }
    ]

    models_to_analyze = ["gpt-4", "gpt-3.5-turbo"]

    print(f"{'Scenario':<15} {'Model':<15} {'Daily Requests':<15} {'Monthly Cost ($)':<15}")
    print("-" * 65)

    for scenario in usage_scenarios:
        for model in models_to_analyze:
            monthly_cost = calculator.calculate_monthly_cost(
                model_name=model,
                daily_requests=scenario["requests_per_day"],
                avg_input_tokens=scenario["avg_input_tokens"],
                avg_output_tokens=scenario["avg_output_tokens"]
            )

            if monthly_cost:
                print(f"{scenario['name']:<15} {model:<15} {scenario['requests_per_day']:<15} ${monthly_cost:<14.2f}")


def model_comparison_for_task():
    """Compare models for a specific task."""
    print("\n=== Model Comparison for Specific Task ===")

    calculator = CostCalculator()

    # Define a specific task
    task_description = "Code review and bug detection"
    sample_input = """
    def calculate_average(numbers):
        total = 0
        for num in numbers:
            total += num
        return total / len(numbers)
    """

    sample_output = """
    Issues found:
    1. No handling for empty list (division by zero)
    2. No type checking for non-numeric values
    3. Consider using built-in sum() function

    Suggested fix:
    def calculate_average(numbers):
        if not numbers:
            return 0
        return sum(numbers) / len(numbers)
    """

    models_to_compare = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]

    print(f"\nTask: {task_description}")
    print(f"Input length: ~{len(sample_input)} characters")
    print(f"Output length: ~{len(sample_output)} characters")

    comparison_results = []

    for model in models_to_compare:
        cost = estimate_cost(model, sample_input, sample_output)
        if cost:
            comparison_results.append({
                'model': model,
                'cost': cost.total_cost,
                'input_tokens': cost.input_tokens,
                'output_tokens': cost.output_tokens,
                'cost_per_input_token': cost.input_cost_per_token,
                'cost_per_output_token': cost.output_cost_per_token
            })

    # Sort by cost
    comparison_results.sort(key=lambda x: x['cost'])

    print(f"\nModel comparison (sorted by cost):")
    print(f"{'Rank':<5} {'Model':<15} {'Total Cost':<12} {'Input Tokens':<13} {'Output Tokens':<14}")
    print("-" * 65)

    for i, result in enumerate(comparison_results, 1):
        print(f"{i:<5} {result['model']:<15} ${result['cost']:<11.6f} {result['input_tokens']:<13} {result['output_tokens']:<14}")

    if comparison_results:
        cheapest = comparison_results[0]
        most_expensive = comparison_results[-1]
        savings = most_expensive['cost'] - cheapest['cost']
        savings_percent = (savings / most_expensive['cost']) * 100

        print(f"\nCost Analysis:")
        print(f"   Cheapest: {cheapest['model']} (${cheapest['cost']:.6f})")
        print(f"   Most Expensive: {most_expensive['model']} (${most_expensive['cost']:.6f})")
        print(f"   Potential Savings: ${savings:.6f} ({savings_percent:.1f}%)")


def custom_model_example():
    """Example of adding and using custom model pricing."""
    print("\n=== Custom Model Example ===")

    calculator = CostCalculator()

    # Add a custom model (example: company's fine-tuned model)
    custom_model = calculator.add_custom_model(
        name="custom-gpt-company",
        provider="OpenAI",
        input_cost_per_token=0.00002,  # $0.02 per 1k tokens
        output_cost_per_token=0.00006,  # $0.06 per 1k tokens
        context_length=8192,
        supports_function_calling=True,
        multimodal=False
    )

    print(f"Added custom model: {custom_model.name}")
    print(f"   Provider: {custom_model.provider}")
    print(f"   Input cost: ${custom_model.input_cost_per_token:.8f}/token")
    print(f"   Output cost: ${custom_model.output_cost_per_token:.8f}/token")
    print(f"   Context length: {custom_model.context_length}")

    # Test cost with custom model
    test_input = "What is the best approach for this business problem?"
    test_output = "Based on analysis, I recommend a three-phase approach focusing on customer engagement, operational efficiency, and technology integration."

    custom_cost = estimate_cost("custom-gpt-company", test_input, test_output)
    if custom_cost:
        print(f"\nCost estimate for custom model:")
        print(f"   Input tokens: {custom_cost.input_tokens}")
        print(f"   Output tokens: {custom_cost.output_tokens}")
        print(f"   Total cost: ${custom_cost.total_cost:.6f}")


if __name__ == "__main__":
    try:
        basic_cost_examples()
        advanced_cost_analysis()
        cost_with_explicit_tokens()
        monthly_cost_projection()
        model_comparison_for_task()
        custom_model_example()

        print("\n🎉 All cost estimation examples completed successfully!")
        print("\n💡 Tips:")
        print("   - Use cost estimation to optimize your AI budget")
        print("   - Compare models for your specific use case")
        print("   - Monitor costs over time to detect usage spikes")
        print("   - Consider token-efficient prompt engineering")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()