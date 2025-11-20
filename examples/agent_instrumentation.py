#!/usr/bin/env python3
"""
Agent Instrumentation Example

This example demonstrates AI agent monitoring including:
- Basic agent instrumentation setup
- Session management and timing
- Reasoning step tracking
- Tool call monitoring
- Consensus mode and multi-run analysis
- Performance and accuracy tracking
"""

import time
import json
from briefcase_ai_telemetry import (
    create_client, create_agent_instrument,
    InstrumentationConfig, AgentInstrument
)


def basic_agent_instrumentation():
    """Basic agent instrumentation setup."""
    print("=== Basic Agent Instrumentation ===")

    # Create client and instrumentation
    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(
        agent_id=12345,
        client=client
    )

    # Start a session
    session = instrument.start()
    print("✓ Agent session started")

    # Set basic information
    session.set_input_output(
        input="What are the key factors for successful project management?",
        output="""Key factors for successful project management include:
        1. Clear objectives and scope definition
        2. Effective communication and stakeholder engagement
        3. Proper resource allocation and team management
        4. Risk assessment and mitigation planning
        5. Regular monitoring and progress tracking"""
    )

    session.set_model_info("gpt-4", temperature=0.1)
    session.set_accuracy(0.95)

    # Finish the session
    session.finish()
    print("✓ Basic agent session completed")


def advanced_instrumentation_with_config():
    """Advanced instrumentation with detailed configuration."""
    print("\n=== Advanced Instrumentation Configuration ===")

    # Create configuration
    config = InstrumentationConfig()
    config.with_consensus_mode(True, runs=3, threshold=0.8)
    config.with_input_output_truncation(True, max_input_length=1000, max_output_length=2000)
    config.with_sensitive_data_sanitization(True)

    print("✓ Instrumentation configuration created")

    # Create client and instrument
    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(
        agent_id=67890,
        client=client,
        config=config
    )

    # Start session with detailed tracking
    session = instrument.start()

    # Set comprehensive information
    session.set_input_output(
        input="Analyze the market trends for renewable energy in 2024",
        output="""Market analysis for renewable energy in 2024:

        Growth Trends:
        - Solar energy: 25% YoY growth expected
        - Wind energy: 18% YoY growth projected
        - Battery storage: 40% expansion anticipated

        Key Drivers:
        - Government incentives and policies
        - Declining technology costs
        - Corporate sustainability commitments
        - Energy security concerns

        Regional Analysis:
        - Asia-Pacific leading in solar installations
        - Europe advancing in offshore wind
        - North America focusing on grid modernization

        Investment Outlook:
        - $2.8 trillion expected investment globally
        - Focus on grid infrastructure and storage
        - Emerging technologies gaining traction"""
    )

    session.set_model_info("gpt-4", temperature=0.2)
    session.set_token_usage(245, 180)
    session.set_accuracy(0.92)
    session.set_cost(0.0156)

    # Add metadata
    session.set_metadata("task_type", "market_analysis")
    session.set_metadata("domain", "renewable_energy")
    session.set_metadata("complexity", "high")

    session.finish()
    print("✓ Advanced agent session completed")


def multi_step_reasoning_example():
    """Agent with multi-step reasoning tracking."""
    print("\n=== Multi-Step Reasoning Tracking ===")

    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(agent_id=11111, client=client)

    session = instrument.start()

    # Complex problem requiring multiple reasoning steps
    session.set_input_output(
        input="A company has 1000 employees. 60% work remotely, 25% work in office, and the rest are hybrid. If they want to reduce office space by 30%, how many desks should they maintain?",
        output="Let me work through this step by step: Current office workers: 25% of 1000 = 250. Hybrid workers (assumed to need desks sometimes): 15% of 1000 = 150. Total desk need: 250 + 150 = 400 desks currently. With 30% reduction: 400 - (400 × 0.3) = 400 - 120 = 280 desks should be maintained."
    )

    session.set_model_info("gpt-4", temperature=0.0)

    # Track reasoning steps
    session.add_reasoning_step("Calculated remote workers: 60% of 1000 = 600")
    session.add_reasoning_step("Calculated office workers: 25% of 1000 = 250")
    session.add_reasoning_step("Calculated hybrid workers: 100% - 60% - 25% = 15% = 150")
    session.add_reasoning_step("Determined total desk requirement: 250 + 150 = 400")
    session.add_reasoning_step("Applied 30% reduction: 400 × 0.3 = 120")
    session.add_reasoning_step("Final answer: 400 - 120 = 280 desks")

    session.set_accuracy(1.0)  # Correct mathematical solution
    session.finish()

    print("✓ Multi-step reasoning session completed with 6 reasoning steps")


def tool_calling_agent_example():
    """Agent that uses multiple tools."""
    print("\n=== Tool-Calling Agent Example ===")

    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(agent_id=22222, client=client)

    session = instrument.start()

    session.set_input_output(
        input="What's the weather forecast for New York and what should I wear?",
        output="Based on the weather forecast, it will be 68°F and sunny in New York today. I recommend wearing light layers - a t-shirt with a light jacket that you can remove if it gets warmer."
    )

    session.set_model_info("gpt-4", temperature=0.3)

    # Track tool usage
    session.add_tool_call("weather_api", {
        "location": "New York, NY",
        "date": "2024-01-15",
        "units": "fahrenheit"
    })

    session.add_tool_call("clothing_recommender", {
        "temperature": 68,
        "conditions": "sunny",
        "activity": "general"
    })

    # Add reasoning about the tools
    session.add_reasoning_step("Called weather API to get current conditions for New York")
    session.add_reasoning_step("Retrieved temperature (68°F) and conditions (sunny)")
    session.add_reasoning_step("Used clothing recommender with weather data")
    session.add_reasoning_step("Generated layered clothing suggestion for variable conditions")

    session.set_accuracy(0.95)
    session.set_cost(0.0089)
    session.finish()

    print("✓ Tool-calling agent session completed with 2 tool calls")


def consensus_mode_example():
    """Demonstrate consensus mode with multiple runs."""
    print("\n=== Consensus Mode Example ===")

    # Configure for consensus mode
    config = InstrumentationConfig()
    config.with_consensus_mode(True, runs=3, threshold=0.8)

    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(
        agent_id=33333,
        client=client,
        config=config
    )

    # Simulate multiple runs of the same query
    query = "What is 15% of 240?"

    # Run 1
    session1 = instrument.start()
    session1.set_input_output(
        input=query,
        output="To find 15% of 240: 15/100 × 240 = 0.15 × 240 = 36"
    )
    session1.set_model_info("gpt-4", temperature=0.0)
    session1.set_accuracy(1.0)
    session1.finish()

    # Run 2
    session2 = instrument.start()
    session2.set_input_output(
        input=query,
        output="15% of 240 = 15 × 240 ÷ 100 = 3600 ÷ 100 = 36"
    )
    session2.set_model_info("gpt-4", temperature=0.0)
    session2.set_accuracy(1.0)
    session2.finish()

    # Run 3
    session3 = instrument.start()
    session3.set_input_output(
        input=query,
        output="15% of 240 equals 36 (calculated as 240 × 0.15)"
    )
    session3.set_model_info("gpt-4", temperature=0.0)
    session3.set_accuracy(1.0)
    session3.finish()

    print("✓ Consensus mode completed with 3 runs (all reaching answer: 36)")


def error_handling_example():
    """Agent instrumentation with error handling."""
    print("\n=== Error Handling Example ===")

    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(agent_id=44444, client=client)

    session = instrument.start()

    try:
        # Simulate an agent that encounters an error
        session.set_input_output(
            input="Translate this to French: 'Hello, how are you today?'",
            output="Error: Translation service temporarily unavailable"
        )

        session.set_model_info("gpt-4", temperature=0.1)

        # Track the error
        session.add_reasoning_step("Attempted to access translation service")
        session.add_reasoning_step("Translation service returned error 503")
        session.add_reasoning_step("Provided fallback error message to user")

        session.set_error("Translation service unavailable (HTTP 503)")
        session.set_accuracy(0.0)  # Failed to complete the task

        # Add metadata about the failure
        session.set_metadata("error_type", "service_unavailable")
        session.set_metadata("service", "translation_api")
        session.set_metadata("retry_attempted", "false")

        session.finish()

        print("✓ Error handling session completed")

    except Exception as e:
        print(f"   Session error: {e}")
        session.finish()


def performance_monitoring_example():
    """Monitor agent performance over multiple sessions."""
    print("\n=== Performance Monitoring Example ===")

    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(agent_id=55555, client=client)

    # Simulate multiple sessions with varying performance
    performance_scenarios = [
        {"task": "Simple Q&A", "accuracy": 0.98, "cost": 0.0045, "tokens": (50, 30)},
        {"task": "Complex Analysis", "accuracy": 0.92, "cost": 0.0234, "tokens": (200, 150)},
        {"task": "Code Generation", "accuracy": 0.89, "cost": 0.0156, "tokens": (120, 180)},
        {"task": "Data Summarization", "accuracy": 0.95, "cost": 0.0089, "tokens": (300, 100)},
        {"task": "Creative Writing", "accuracy": 0.87, "cost": 0.0198, "tokens": (80, 220)}
    ]

    total_cost = 0
    total_sessions = len(performance_scenarios)

    for i, scenario in enumerate(performance_scenarios, 1):
        session = instrument.start()

        session.set_input_output(
            input=f"Task {i}: {scenario['task']}",
            output=f"Completed {scenario['task']} successfully"
        )

        session.set_model_info("gpt-4", temperature=0.2)
        session.set_token_usage(scenario["tokens"][0], scenario["tokens"][1])
        session.set_accuracy(scenario["accuracy"])
        session.set_cost(scenario["cost"])
        session.set_metadata("task_category", scenario["task"].lower().replace(" ", "_"))

        session.finish()
        total_cost += scenario["cost"]

        print(f"   Session {i}: {scenario['task']} - Accuracy: {scenario['accuracy']:.1%}, Cost: ${scenario['cost']:.4f}")

    print(f"\n✓ Performance monitoring completed:")
    print(f"   Total sessions: {total_sessions}")
    print(f"   Total cost: ${total_cost:.4f}")
    print(f"   Average cost per session: ${total_cost/total_sessions:.4f}")
    print(f"   Average accuracy: {sum(s['accuracy'] for s in performance_scenarios)/total_sessions:.1%}")


def sanitization_example():
    """Example with sensitive data sanitization."""
    print("\n=== Sensitive Data Sanitization ===")

    # Enable sanitization
    config = InstrumentationConfig()
    config.with_sensitive_data_sanitization(True)

    client = create_client("demo-api-key", enabled=False)
    instrument = create_agent_instrument(
        agent_id=66666,
        client=client,
        config=config
    )

    session = instrument.start()

    # Input containing sensitive data (would be sanitized)
    sensitive_input = """
    Please analyze this customer data:
    Name: John Smith
    SSN: 123-45-6789
    Email: john.smith@email.com
    Credit Card: 4532-1234-5678-9012
    Phone: (555) 123-4567
    API Key: sk-1234567890abcdef
    """

    sanitized_output = """
    Customer data analysis:
    - Customer profile identified
    - Contact information verified
    - Payment method on file
    - Account in good standing
    (Note: Sensitive data redacted for security)
    """

    session.set_input_output(
        input=sensitive_input,
        output=sanitized_output
    )

    session.set_model_info("gpt-4", temperature=0.0)
    session.add_reasoning_step("Detected sensitive data in input")
    session.add_reasoning_step("Applied data sanitization protocols")
    session.add_reasoning_step("Generated analysis without exposing sensitive information")

    session.set_metadata("data_sanitization", "enabled")
    session.set_metadata("sensitive_data_detected", "true")
    session.set_accuracy(0.98)

    session.finish()

    print("✓ Sensitive data sanitization example completed")


if __name__ == "__main__":
    try:
        basic_agent_instrumentation()
        advanced_instrumentation_with_config()
        multi_step_reasoning_example()
        tool_calling_agent_example()
        consensus_mode_example()
        error_handling_example()
        performance_monitoring_example()
        sanitization_example()

        print("\n🎉 All agent instrumentation examples completed successfully!")
        print("\n💡 Key Benefits:")
        print("   - Track agent reasoning and decision-making")
        print("   - Monitor performance and accuracy over time")
        print("   - Implement consensus mechanisms for reliability")
        print("   - Automatically sanitize sensitive data")
        print("   - Detailed cost and token usage tracking")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()