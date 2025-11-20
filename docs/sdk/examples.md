# SDK Usage Examples

This guide provides practical examples demonstrating how to use the Briefcase AI Telemetry SDK in your applications.

## Quick Start Examples

### Basic Telemetry Tracking

#### Python
```python
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig
import asyncio

async def basic_tracking():
    # Initialize the SDK
    config = TelemetryConfig("your-api-key")
    client = TelemetryClient(config)

    # Track a simple event
    await client.track_event("user_action", {
        "action": "button_click",
        "page": "dashboard",
        "user_id": "user123"
    })

    # Flush events to ensure they're sent
    await client.flush()

# Run the example
asyncio.run(basic_tracking())
```

#### Rust
```rust
use briefcase_ai_telemetry::{TelemetryClient, TelemetryConfig, EventBuilder};
use tokio;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize the SDK
    let config = TelemetryConfig::new("your-api-key".to_string());
    let client = TelemetryClient::new(config)?;

    // Create and track an event
    let event = EventBuilder::new("user_action")
        .custom_data("action", serde_json::Value::String("button_click".to_string()))
        .custom_data("page", serde_json::Value::String("dashboard".to_string()))
        .custom_data("user_id", serde_json::Value::String("user123".to_string()))
        .build();

    client.track_event(event).await?;

    // Flush events
    client.flush().await?;

    Ok(())
}
```

### Configuration Options

#### Python Configuration
```python
from briefcase_ai_telemetry import TelemetryConfig
import time

# Basic configuration
config = TelemetryConfig("your-api-key")

# Advanced configuration
config = TelemetryConfig("your-api-key") \
    .with_endpoint("https://custom-endpoint.com/telemetry") \
    .with_timeout(30) \
    .with_retry_attempts(5) \
    .with_batch_size(50) \
    .with_flush_interval(10) \
    .with_enabled(True)

print(f"API Key: {config.api_key}")
print(f"Endpoint: {config.endpoint}")
print(f"Batch Size: {config.batch_size}")
print(f"Enabled: {config.enabled}")
```

#### Rust Configuration
```rust
use briefcase_ai_telemetry::TelemetryConfig;
use std::time::Duration;

// Basic configuration
let config = TelemetryConfig::new("your-api-key".to_string());

// Advanced configuration
let config = TelemetryConfig::new("your-api-key".to_string())
    .with_endpoint("https://custom-endpoint.com/telemetry".to_string())
    .with_timeout(Duration::from_secs(30))
    .with_retry_attempts(5)
    .with_batch_size(50)
    .with_flush_interval(Duration::from_secs(10))
    .with_enabled(true);

println!("API Key: {}", config.api_key);
println!("Endpoint: {}", config.endpoint);
println!("Batch Size: {}", config.batch_size);
println!("Enabled: {}", config.enabled);
```

## Agent Instrumentation

### Comprehensive Agent Monitoring

#### Python Agent Instrumentation
```python
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig
from briefcase_ai_telemetry.instrumentation import AgentInstrument, InstrumentationConfig
import asyncio
import openai

async def ai_agent_with_monitoring():
    # Configure telemetry
    telemetry_config = TelemetryConfig("your-api-key")
    client = TelemetryClient(telemetry_config)

    # Configure instrumentation
    instrumentation_config = InstrumentationConfig(
        auto_submit=True,
        consensus_mode=False,
        max_input_length=5000,
        max_output_length=5000,
        sanitization_enabled=True
    )

    # Create agent instrument
    instrument = AgentInstrument(
        agent_id=12345,
        client=client,
        config=instrumentation_config
    )

    # Start monitoring
    instrument.start()

    try:
        # Set input data
        user_query = "What are the benefits of renewable energy?"
        instrument.set_input(user_query)
        instrument.set_model_info("gpt-4", temperature=0.7)

        # Add reasoning steps
        instrument.add_reasoning_step("Analyzing user query about renewable energy")
        instrument.add_reasoning_step("Retrieving relevant information")

        # Simulate AI model call
        client = openai.Client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_query}],
            temperature=0.7
        )

        # Capture output and metrics
        output = response.choices[0].message.content
        instrument.set_output(output)
        instrument.set_token_usage(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens
        )
        instrument.set_cost(0.03)  # Calculate based on model pricing
        instrument.set_accuracy(95.0)

        # Add metadata
        instrument.set_metadata("model_version", "gpt-4-0613")
        instrument.set_metadata("use_case", "customer_support")

        print(f"Response: {output}")

    except Exception as e:
        # Capture errors
        instrument.set_error(str(e))
        raise

    finally:
        # Submit telemetry (automatically done if auto_submit=True)
        await instrument.submit_telemetry()

# Run the example
asyncio.run(ai_agent_with_monitoring())
```

#### Rust Agent Instrumentation
```rust
use briefcase_ai_telemetry::{TelemetryClient, TelemetryConfig};
use briefcase_ai_telemetry::instrumentation::{
    AgentInstrument, InstrumentationConfig, AgentMetrics
};
use std::collections::HashMap;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Configure telemetry
    let telemetry_config = TelemetryConfig::new("your-api-key".to_string());
    let client = TelemetryClient::new(telemetry_config)?;

    // Configure instrumentation
    let instrumentation_config = InstrumentationConfig {
        auto_submit: true,
        consensus_mode: false,
        consensus_runs: 3,
        consensus_threshold: 80.0,
        max_input_length: 5000,
        max_output_length: 5000,
        sanitization_enabled: true,
    };

    // Create agent instrument
    let mut instrument = AgentInstrument::new(12345, client, instrumentation_config);

    // Start monitoring
    instrument.start();

    // Set input and model info
    let user_query = "What are the benefits of renewable energy?";
    instrument.set_input(user_query.to_string());
    instrument.set_model_info("gpt-4".to_string(), Some(0.7));

    // Add reasoning steps
    instrument.add_reasoning_step("Analyzing user query about renewable energy".to_string());
    instrument.add_reasoning_step("Retrieving relevant information".to_string());

    // Simulate AI processing and capture results
    let output = "Renewable energy offers numerous benefits including environmental protection, economic advantages, and energy security...";
    instrument.set_output(output.to_string());
    instrument.set_token_usage(150, 75);  // input_tokens, output_tokens
    instrument.set_cost(0.03);
    instrument.set_accuracy(95.0);

    // Add tool call
    let mut tool_args = HashMap::new();
    tool_args.insert("query".to_string(), serde_json::Value::String(user_query.to_string()));
    instrument.add_tool_call(
        "knowledge_retrieval".to_string(),
        tool_args,
        Some(serde_json::Value::String("Retrieved 5 relevant articles".to_string()))
    );

    // Add metadata
    instrument.set_metadata("model_version".to_string(), serde_json::Value::String("gpt-4-0613".to_string()));
    instrument.set_metadata("use_case".to_string(), serde_json::Value::String("customer_support".to_string()));

    // Submit telemetry
    instrument.submit_telemetry().await?;

    println!("Response: {}", output);

    Ok(())
}
```

## Cost Estimation

### Multi-Model Cost Tracking

#### Python Cost Analysis
```python
from briefcase_ai_telemetry.cost import (
    CostCalculator, estimate_cost, get_model_info, format_cost
)

def cost_analysis_example():
    # Initialize cost calculator
    calculator = CostCalculator()

    # Get model information
    gpt4_info = calculator.get_model_info("gpt-4")
    print(f"GPT-4 Info: {gpt4_info.name} - ${gpt4_info.input_cost_per_1k}/1K input tokens")

    # Estimate cost for a specific interaction
    input_text = "Analyze the following data and provide insights: " + "data" * 100
    output_text = "Based on the analysis, here are the key insights: " + "insight" * 50

    cost_estimate = estimate_cost("gpt-4", input_text, output_text)
    if cost_estimate:
        print(f"Estimated cost: {format_cost(cost_estimate.total_cost)}")
        print(f"Input tokens: {cost_estimate.input_tokens}")
        print(f"Output tokens: {cost_estimate.output_tokens}")

    # Compare costs across models
    models_to_compare = ["gpt-4", "gpt-4o-mini", "claude-3-5-sonnet-20241022"]
    comparisons = calculator.compare_models(models_to_compare, 1000, 500)

    print("\n--- Model Cost Comparison (1000 input, 500 output tokens) ---")
    for comparison in sorted(comparisons, key=lambda x: x.total_cost):
        print(f"{comparison.model_name}: {format_cost(comparison.total_cost)}")

    # Monthly cost projection
    daily_input_tokens = 50000
    daily_output_tokens = 25000

    monthly_cost = calculator.calculate_monthly_cost(
        "gpt-4o-mini", daily_input_tokens, daily_output_tokens
    )
    if monthly_cost:
        print(f"\nProjected monthly cost (GPT-4o-mini): {format_cost(monthly_cost)}")

    # Find cheapest model
    cheapest = calculator.get_cheapest_model()
    if cheapest:
        print(f"Cheapest model: {cheapest.name} ({cheapest.provider})")

    # Find models under budget
    budget_models = calculator.get_models_under_cost(0.001)  # Under $0.001/1K tokens
    print(f"\nModels under $0.001/1K tokens: {len(budget_models)} found")
    for model in budget_models[:3]:  # Show first 3
        print(f"  - {model.name} ({model.provider})")

# Run the example
cost_analysis_example()
```

#### Rust Cost Analysis
```rust
use briefcase_ai_telemetry::cost::{CostCalculator, estimate_cost, format_cost};

fn main() {
    // Initialize cost calculator
    let calculator = CostCalculator::new();

    // Get model information
    if let Some(gpt4_info) = calculator.get_model_info("gpt-4") {
        println!("GPT-4 Info: {} - ${:.4}/1K input tokens",
                 gpt4_info.name,
                 gpt4_info.input_cost_per_1k.unwrap_or(0.0));
    }

    // Estimate cost for a specific interaction
    let input_text = format!("Analyze the following data and provide insights: {}", "data".repeat(100));
    let output_text = format!("Based on the analysis, here are the key insights: {}", "insight".repeat(50));

    if let Some(cost_estimate) = estimate_cost("gpt-4", &input_text, &output_text, None) {
        println!("Estimated cost: {}", format_cost(cost_estimate.total_cost));
        println!("Input tokens: {}", cost_estimate.input_tokens);
        println!("Output tokens: {}", cost_estimate.output_tokens);
    }

    // Compare costs across models
    let models_to_compare = vec!["gpt-4", "gpt-4o-mini", "claude-3-5-sonnet-20241022"];
    let mut comparisons = calculator.compare_models(&models_to_compare, 1000, 500);
    comparisons.sort_by(|a, b| a.total_cost.partial_cmp(&b.total_cost).unwrap());

    println!("\n--- Model Cost Comparison (1000 input, 500 output tokens) ---");
    for comparison in comparisons {
        println!("{}: {}", comparison.model_name, format_cost(comparison.total_cost));
    }

    // Monthly cost projection
    let daily_input_tokens = 50000;
    let daily_output_tokens = 25000;

    if let Some(monthly_cost) = calculator.calculate_monthly_cost(
        "gpt-4o-mini", daily_input_tokens, daily_output_tokens
    ) {
        println!("\nProjected monthly cost (GPT-4o-mini): {}", format_cost(monthly_cost));
    }

    // Find cheapest model
    if let Some(cheapest) = calculator.get_cheapest_model() {
        println!("Cheapest model: {} ({})", cheapest.name, cheapest.provider);
    }

    // Find models under budget
    let budget_models = calculator.get_models_under_cost(0.001);  // Under $0.001/1K tokens
    println!("\nModels under $0.001/1K tokens: {} found", budget_models.len());
    for model in budget_models.iter().take(3) {  // Show first 3
        println!("  - {} ({})", model.name, model.provider);
    }
}
```

## Drift Detection

### Output Consistency Monitoring

#### Python Drift Analysis
```python
from briefcase_ai_telemetry.drift import (
    calculate_drift_metrics, calculate_enhanced_drift_metrics,
    check_compliance, ComplianceFramework
)

def drift_detection_example():
    # Simulate multiple AI model outputs for the same input
    model_outputs = [
        "The capital of France is Paris, a beautiful city known for its culture.",
        "France's capital city is Paris, famous for its art and architecture.",
        "Paris serves as the capital of France and is renowned for its museums.",
        "The capital city of France is Paris, celebrated for its rich history.",
        "Paris is France's capital, well-known for its cuisine and landmarks."
    ]

    # Calculate basic drift metrics
    basic_metrics = calculate_drift_metrics(model_outputs)

    print("=== Basic Drift Analysis ===")
    print(f"Agreement Rate: {basic_metrics.total_agreement_rate:.1f}%")
    print(f"Edit Distance Similarity: {basic_metrics.normalized_edit_distance:.3f}")
    print(f"Consistency Score: {basic_metrics.consistency_score:.1f}")
    print(f"Consensus Confidence: {basic_metrics.consensus_confidence}")
    print(f"Factual Drift Count: {basic_metrics.factual_drift_count}")

    if basic_metrics.consensus_output:
        print(f"Consensus Output: {basic_metrics.consensus_output}")

    # Enhanced drift analysis with multiple algorithms
    enhanced_metrics = calculate_enhanced_drift_metrics(
        model_outputs,
        context="Geography question about capital cities"
    )

    print("\n=== Enhanced Drift Analysis ===")
    print(f"Semantic Similarity: {enhanced_metrics.semantic_similarity:.3f}")
    print(f"Ensemble Score: {enhanced_metrics.ensemble_score:.1f}")
    print(f"Drift Severity: {enhanced_metrics.drift_severity}")
    print(f"Confidence Interval: [{enhanced_metrics.confidence_interval.lower_bound:.3f}, "
          f"{enhanced_metrics.confidence_interval.upper_bound:.3f}]")

    print("\nStatistical Drift:")
    print(f"  Mean Length Change: {enhanced_metrics.statistical_drift.mean_length_change:.2f}")
    print(f"  Variance Change: {enhanced_metrics.statistical_drift.variance_change:.2f}")
    print(f"  Outlier Count: {enhanced_metrics.statistical_drift.outlier_count}")

    print("\nStructural Drift:")
    print(f"  Format Consistency: {enhanced_metrics.structural_drift.format_consistency:.3f}")
    print(f"  Entity Drift: {enhanced_metrics.structural_drift.entity_drift:.3f}")
    print(f"  Sentiment Drift: {enhanced_metrics.structural_drift.sentiment_drift:.3f}")

    if enhanced_metrics.recommendations:
        print("\nRecommendations:")
        for rec in enhanced_metrics.recommendations:
            print(f"  - {rec}")

    # Compliance checking
    print("\n=== Compliance Analysis ===")

    compliance_checks = [
        (ComplianceFramework.GDPR, "GDPR"),
        (ComplianceFramework.SOC2, "SOC 2"),
        (ComplianceFramework.HIPAA, "HIPAA"),
        (ComplianceFramework.FSB, "Financial Services Board")
    ]

    for framework, name in compliance_checks:
        check = check_compliance(
            consistency_score=basic_metrics.consistency_score,
            temperature=0.0,
            has_audit_trail=True,
            framework=framework
        )

        status = "✅ COMPLIANT" if check.compliant else "❌ NON-COMPLIANT"
        print(f"{name}: {status} (Score: {check.score:.1f})")

        if not check.compliant and check.issues:
            print(f"  Issues: {', '.join(check.issues)}")

# Run the example
drift_detection_example()
```

#### Rust Drift Analysis
```rust
use briefcase_ai_telemetry::drift::{
    calculate_drift_metrics, calculate_enhanced_drift_metrics,
    check_compliance, ComplianceFramework, DriftSeverity
};

fn main() {
    // Simulate multiple AI model outputs for the same input
    let model_outputs = vec![
        "The capital of France is Paris, a beautiful city known for its culture.".to_string(),
        "France's capital city is Paris, famous for its art and architecture.".to_string(),
        "Paris serves as the capital of France and is renowned for its museums.".to_string(),
        "The capital city of France is Paris, celebrated for its rich history.".to_string(),
        "Paris is France's capital, well-known for its cuisine and landmarks.".to_string(),
    ];

    // Calculate basic drift metrics
    let basic_metrics = calculate_drift_metrics(&model_outputs);

    println!("=== Basic Drift Analysis ===");
    println!("Agreement Rate: {:.1}%", basic_metrics.total_agreement_rate);
    println!("Edit Distance Similarity: {:.3}", basic_metrics.normalized_edit_distance);
    println!("Consistency Score: {:.1}", basic_metrics.consistency_score);
    println!("Consensus Confidence: {}", basic_metrics.consensus_confidence);
    println!("Factual Drift Count: {}", basic_metrics.factual_drift_count);

    if let Some(ref consensus) = basic_metrics.consensus_output {
        println!("Consensus Output: {}", consensus);
    }

    // Enhanced drift analysis
    let enhanced_metrics = calculate_enhanced_drift_metrics(
        &model_outputs,
        Some("Geography question about capital cities")
    );

    println!("\n=== Enhanced Drift Analysis ===");
    println!("Semantic Similarity: {:.3}", enhanced_metrics.semantic_similarity);
    println!("Ensemble Score: {:.1}", enhanced_metrics.ensemble_score);
    println!("Drift Severity: {:?}", enhanced_metrics.drift_severity);
    println!("Confidence Interval: [{:.3}, {:.3}]",
             enhanced_metrics.confidence_interval.lower_bound,
             enhanced_metrics.confidence_interval.upper_bound);

    println!("\nStatistical Drift:");
    println!("  Mean Length Change: {:.2}", enhanced_metrics.statistical_drift.mean_length_change);
    println!("  Variance Change: {:.2}", enhanced_metrics.statistical_drift.variance_change);
    println!("  Outlier Count: {}", enhanced_metrics.statistical_drift.outlier_count);

    println!("\nStructural Drift:");
    println!("  Format Consistency: {:.3}", enhanced_metrics.structural_drift.format_consistency);
    println!("  Entity Drift: {:.3}", enhanced_metrics.structural_drift.entity_drift);
    println!("  Sentiment Drift: {:.3}", enhanced_metrics.structural_drift.sentiment_drift);

    if !enhanced_metrics.recommendations.is_empty() {
        println!("\nRecommendations:");
        for rec in &enhanced_metrics.recommendations {
            println!("  - {}", rec);
        }
    }

    // Compliance checking
    println!("\n=== Compliance Analysis ===");

    let compliance_frameworks = vec![
        (ComplianceFramework::Gdpr, "GDPR"),
        (ComplianceFramework::Soc2, "SOC 2"),
        (ComplianceFramework::Hipaa, "HIPAA"),
        (ComplianceFramework::Fsb, "Financial Services Board"),
    ];

    for (framework, name) in compliance_frameworks {
        let check = check_compliance(
            basic_metrics.consistency_score,
            0.0,  // temperature
            true, // has_audit_trail
            framework
        );

        let status = if check.compliant { "✅ COMPLIANT" } else { "❌ NON-COMPLIANT" };
        println!("{}: {} (Score: {:.1})", name, status, check.score);

        if !check.compliant && !check.issues.is_empty() {
            println!("  Issues: {}", check.issues.join(", "));
        }
    }
}
```

## Integration Examples

### Framework Integration Examples

#### LangChain Integration (Python)
```python
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig
from briefcase_ai_telemetry.instrumentation import AgentInstrument, InstrumentationConfig
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import asyncio

class TelemetryLangChain:
    def __init__(self, api_key: str, telemetry_api_key: str):
        # Setup telemetry
        telemetry_config = TelemetryConfig(telemetry_api_key)
        self.telemetry_client = TelemetryClient(telemetry_config)

        # Setup LangChain
        self.llm = OpenAI(api_key=api_key, temperature=0.7)

        # Instrumentation config
        self.instrumentation_config = InstrumentationConfig(
            auto_submit=True,
            sanitization_enabled=True
        )

    async def run_chain_with_telemetry(self, input_text: str, agent_id: int = 1):
        # Create instrumentation
        instrument = AgentInstrument(
            agent_id=agent_id,
            client=self.telemetry_client,
            config=self.instrumentation_config
        )

        instrument.start()

        try:
            # Setup prompt and chain
            prompt = PromptTemplate(
                input_variables=["question"],
                template="Answer the following question: {question}"
            )

            chain = LLMChain(llm=self.llm, prompt=prompt)

            # Track input
            instrument.set_input(input_text)
            instrument.set_model_info("text-davinci-003", temperature=0.7)

            # Add reasoning step
            instrument.add_reasoning_step("Processing question with LangChain")

            # Run the chain
            result = chain.run(question=input_text)

            # Track output and metrics
            instrument.set_output(result)
            instrument.set_accuracy(90.0)  # You might calculate this based on evaluation

            # Add metadata
            instrument.set_metadata("framework", "langchain")
            instrument.set_metadata("chain_type", "llm_chain")

            print(f"Result: {result}")
            return result

        except Exception as e:
            instrument.set_error(str(e))
            raise
        finally:
            await instrument.submit_telemetry()

# Usage example
async def langchain_example():
    telemetry_chain = TelemetryLangChain(
        api_key="your-openai-key",
        telemetry_api_key="your-briefcase-key"
    )

    await telemetry_chain.run_chain_with_telemetry(
        "What are the main advantages of renewable energy?",
        agent_id=12345
    )

# Run the example
asyncio.run(langchain_example())
```

#### Anthropic Integration (Python)
```python
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig
from briefcase_ai_telemetry.instrumentation import AgentInstrument, InstrumentationConfig
import anthropic
import asyncio

async def anthropic_with_telemetry():
    # Setup telemetry
    telemetry_config = TelemetryConfig("your-briefcase-api-key")
    telemetry_client = TelemetryClient(telemetry_config)

    # Setup Anthropic client
    anthropic_client = anthropic.Client(api_key="your-anthropic-key")

    # Create instrumentation
    instrumentation_config = InstrumentationConfig(auto_submit=True)
    instrument = AgentInstrument(
        agent_id=67890,
        client=telemetry_client,
        config=instrumentation_config
    )

    instrument.start()

    try:
        # Prepare input
        user_message = "Explain quantum computing in simple terms"
        instrument.set_input(user_message)
        instrument.set_model_info("claude-3-5-sonnet-20241022", temperature=0.7)

        # Add reasoning steps
        instrument.add_reasoning_step("Preparing prompt for Claude")
        instrument.add_reasoning_step("Sending request to Anthropic API")

        # Make API call
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": user_message}]
        )

        # Extract response
        output = response.content[0].text

        # Track metrics
        instrument.set_output(output)
        instrument.set_token_usage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )

        # Calculate cost (example rates)
        input_cost = (response.usage.input_tokens / 1000) * 0.003
        output_cost = (response.usage.output_tokens / 1000) * 0.015
        instrument.set_cost(input_cost + output_cost)

        # Add metadata
        instrument.set_metadata("provider", "anthropic")
        instrument.set_metadata("model_version", "claude-3-5-sonnet-20241022")

        print(f"Response: {output}")
        return output

    except Exception as e:
        instrument.set_error(str(e))
        raise
    finally:
        await instrument.submit_telemetry()

# Run the example
asyncio.run(anthropic_with_telemetry())
```

## Best Practices

### Error Handling and Resilience

```python
from briefcase_ai_telemetry import TelemetryClient, TelemetryConfig
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilientTelemetryClient:
    def __init__(self, api_key: str):
        config = TelemetryConfig(api_key) \
            .with_retry_attempts(3) \
            .with_timeout(30) \
            .with_enabled(True)  # Can be disabled for testing

        self.client = TelemetryClient(config)

    async def track_event_safely(self, event_name: str, data: dict):
        """Track an event with proper error handling."""
        try:
            await self.client.track_event(event_name, data)
            logger.info(f"Successfully tracked event: {event_name}")
        except Exception as e:
            logger.error(f"Failed to track event {event_name}: {e}")
            # Don't let telemetry failures break your application

    async def flush_safely(self):
        """Flush events with error handling."""
        try:
            await self.client.flush()
            logger.info("Successfully flushed telemetry events")
        except Exception as e:
            logger.error(f"Failed to flush telemetry: {e}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.flush_safely()

# Usage with context manager
async def resilient_example():
    async with ResilientTelemetryClient("your-api-key") as telemetry:
        # Track events safely
        await telemetry.track_event_safely("user_login", {"user_id": "123"})
        await telemetry.track_event_safely("page_view", {"page": "dashboard"})

        # Telemetry will be flushed automatically when exiting context

asyncio.run(resilient_example())
```

### Performance Optimization

```python
from briefcase_ai_telemetry import TelemetryConfig, TelemetryClient
import asyncio

# Optimized configuration for high-throughput applications
def create_optimized_telemetry_client(api_key: str) -> TelemetryClient:
    config = TelemetryConfig(api_key) \
        .with_batch_size(200) \        # Larger batches for efficiency
        .with_flush_interval(30) \     # Less frequent flushes
        .with_timeout(60) \            # Longer timeout for large batches
        .with_retry_attempts(2)        # Fewer retries for speed

    return TelemetryClient(config)

async def high_throughput_example():
    client = create_optimized_telemetry_client("your-api-key")

    # Track many events quickly
    tasks = []
    for i in range(1000):
        task = client.track_event(f"batch_event_{i}", {"index": i})
        tasks.append(task)

    # Process in batches to avoid overwhelming the system
    batch_size = 50
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        await asyncio.gather(*batch)

        # Small delay between batches
        await asyncio.sleep(0.1)

    # Final flush
    await client.flush()
    print("Completed high-throughput telemetry")

asyncio.run(high_throughput_example())
```

## Testing and Development

### Local Development Setup

```python
from briefcase_ai_telemetry import TelemetryConfig, TelemetryClient
import os

def create_dev_telemetry_client():
    # Use environment variables for configuration
    api_key = os.getenv("BRIEFCASE_AI_API_KEY", "dev-key")
    endpoint = os.getenv("BRIEFCASE_AI_ENDPOINT", "http://localhost:8080/telemetry")

    config = TelemetryConfig(api_key) \
        .with_endpoint(endpoint) \
        .with_enabled(os.getenv("TELEMETRY_ENABLED", "true").lower() == "true")

    return TelemetryClient(config)

# For testing, you might want to disable telemetry
def create_test_telemetry_client():
    config = TelemetryConfig("test-key").with_enabled(False)
    return TelemetryClient(config)

# Usage in tests
async def test_my_function():
    telemetry_client = create_test_telemetry_client()  # Won't send real data

    # Your test code here
    await telemetry_client.track_event("test_event", {"test": True})

    # No actual network calls are made when enabled=False
```

---

**Ready to implement?** Start with the [Basic Telemetry Tracking](#basic-telemetry-tracking) example and gradually add more advanced features as needed. For more detailed API documentation, see our [API Reference](api-reference.md).