#!/usr/bin/env python3
"""
Multi-Model Chat Application with Consensus Mode

Demonstrates how to use multiple AI providers (OpenAI, Anthropic) with consensus mode
for critical decisions, automatic cost tracking, and drift detection.

Features:
- Consensus mode with multiple models
- Real-time cost tracking across providers
- Drift detection for response consistency
- Automatic telemetry capture
- Performance comparison
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional
import sys
import os
from dataclasses import dataclass, asdict

# Add SDK path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'instrumentation'))

import briefcase_ai_telemetry as bai
from briefcase_ai_agent.integrations.openai_integration import enable_openai_integration
from briefcase_ai_agent.integrations.anthropic_integration import enable_anthropic_integration

@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    name: str
    provider: str
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    enabled: bool = True

@dataclass
class ConsensusResult:
    """Result of consensus mode execution."""
    question: str
    responses: List[Dict[str, Any]]
    consensus_response: str
    drift_metrics: Any
    total_cost: float
    execution_time: float
    confidence_score: float

class MultiModelChat:
    """Multi-model chat application with consensus mode."""

    def __init__(self, briefcase_api_key: str, agent_id: int = 1):
        self.briefcase_api_key = briefcase_api_key
        self.agent_id = agent_id
        self.models = []
        self.cost_calculator = bai.CostCalculator()
        self.drift_calculator = bai.DriftCalculator()

        # Initialize telemetry
        self._setup_telemetry()

    def _setup_telemetry(self):
        """Set up telemetry integrations."""
        print("🔭 Setting up telemetry integrations...")

        # Enable framework integrations
        try:
            enable_openai_integration(
                agent_id=self.agent_id,
                api_key=self.briefcase_api_key
            )
            print("✅ OpenAI integration enabled")
        except Exception as e:
            print(f"⚠️  OpenAI integration failed: {e}")

        try:
            enable_anthropic_integration(
                agent_id=self.agent_id,
                api_key=self.briefcase_api_key
            )
            print("✅ Anthropic integration enabled")
        except Exception as e:
            print(f"⚠️  Anthropic integration failed: {e}")

    def add_model(self, config: ModelConfig):
        """Add a model to the consensus ensemble."""
        if config.enabled:
            self.models.append(config)
            print(f"➕ Added model: {config.name} ({config.provider})")

    async def query_openai_model(self, question: str, model_config: ModelConfig) -> Dict[str, Any]:
        """Query an OpenAI model."""
        try:
            import openai

            # Set API key
            client = openai.OpenAI(api_key=model_config.api_key)

            start_time = time.time()

            response = client.chat.completions.create(
                model=model_config.model_id,
                messages=[{"role": "user", "content": question}],
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
            )

            execution_time = time.time() - start_time
            response_text = response.choices[0].message.content

            # Calculate cost
            cost_estimate = self.cost_calculator.estimate_cost(
                model_config.model_id,
                question,
                response_text,
                response.usage.prompt_tokens if response.usage else None,
                response.usage.completion_tokens if response.usage else None,
            )

            return {
                "model": model_config.name,
                "provider": model_config.provider,
                "response": response_text,
                "execution_time": execution_time,
                "tokens": {
                    "input": response.usage.prompt_tokens if response.usage else 0,
                    "output": response.usage.completion_tokens if response.usage else 0,
                },
                "cost": cost_estimate.total_cost if cost_estimate else 0.0,
                "success": True,
            }

        except Exception as e:
            return {
                "model": model_config.name,
                "provider": model_config.provider,
                "response": f"Error: {str(e)}",
                "execution_time": 0.0,
                "tokens": {"input": 0, "output": 0},
                "cost": 0.0,
                "success": False,
                "error": str(e),
            }

    async def query_anthropic_model(self, question: str, model_config: ModelConfig) -> Dict[str, Any]:
        """Query an Anthropic model."""
        try:
            import anthropic

            # Set API key
            client = anthropic.Anthropic(api_key=model_config.api_key)

            start_time = time.time()

            response = client.messages.create(
                model=model_config.model_id,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                messages=[{"role": "user", "content": question}]
            )

            execution_time = time.time() - start_time
            response_text = response.content[0].text if response.content else ""

            # Calculate cost
            cost_estimate = self.cost_calculator.estimate_cost(
                model_config.model_id,
                question,
                response_text,
                response.usage.input_tokens if response.usage else None,
                response.usage.output_tokens if response.usage else None,
            )

            return {
                "model": model_config.name,
                "provider": model_config.provider,
                "response": response_text,
                "execution_time": execution_time,
                "tokens": {
                    "input": response.usage.input_tokens if response.usage else 0,
                    "output": response.usage.output_tokens if response.usage else 0,
                },
                "cost": cost_estimate.total_cost if cost_estimate else 0.0,
                "success": True,
            }

        except Exception as e:
            return {
                "model": model_config.name,
                "provider": model_config.provider,
                "response": f"Error: {str(e)}",
                "execution_time": 0.0,
                "tokens": {"input": 0, "output": 0},
                "cost": 0.0,
                "success": False,
                "error": str(e),
            }

    async def query_model(self, question: str, model_config: ModelConfig) -> Dict[str, Any]:
        """Query a model based on its provider."""
        if model_config.provider.lower() == "openai":
            return await self.query_openai_model(question, model_config)
        elif model_config.provider.lower() == "anthropic":
            return await self.query_anthropic_model(question, model_config)
        else:
            return {
                "model": model_config.name,
                "provider": model_config.provider,
                "response": f"Provider {model_config.provider} not supported",
                "execution_time": 0.0,
                "tokens": {"input": 0, "output": 0},
                "cost": 0.0,
                "success": False,
                "error": f"Provider {model_config.provider} not supported",
            }

    async def consensus_query(self, question: str, min_agreement: float = 0.8) -> ConsensusResult:
        """
        Query all models and return consensus result with drift analysis.

        Args:
            question: The question to ask all models
            min_agreement: Minimum agreement threshold for consensus

        Returns:
            ConsensusResult with consensus response and metrics
        """
        print(f"\n🤔 Consensus Query: {question}")
        print("=" * 60)

        start_time = time.time()

        # Query all models in parallel
        tasks = []
        for model_config in self.models:
            if model_config.enabled:
                task = self.query_model(question, model_config)
                tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # Filter successful responses
        successful_responses = [r for r in responses if r.get("success", False)]
        response_texts = [r["response"] for r in successful_responses]

        if not response_texts:
            raise ValueError("No successful responses from any model")

        # Calculate drift metrics
        drift_metrics = self.drift_calculator.calculate_metrics(response_texts)

        # Determine consensus response
        consensus_response = self._determine_consensus(successful_responses, drift_metrics)

        # Calculate total cost and time
        total_cost = sum(r["cost"] for r in responses)
        execution_time = time.time() - start_time

        # Calculate confidence score based on agreement
        confidence_score = drift_metrics.total_agreement_rate

        # Display results
        self._display_consensus_results(responses, drift_metrics, total_cost, execution_time)

        return ConsensusResult(
            question=question,
            responses=responses,
            consensus_response=consensus_response,
            drift_metrics=drift_metrics,
            total_cost=total_cost,
            execution_time=execution_time,
            confidence_score=confidence_score,
        )

    def _determine_consensus(self, responses: List[Dict[str, Any]], drift_metrics) -> str:
        """Determine the consensus response based on agreement metrics."""

        if drift_metrics.total_agreement_rate >= 0.8:
            # High agreement - use the most common response pattern
            if hasattr(drift_metrics, 'consensus_output') and drift_metrics.consensus_output:
                return drift_metrics.consensus_output

        # Fallback to longest response (often most detailed)
        return max(responses, key=lambda r: len(r["response"]))["response"]

    def _display_consensus_results(self, responses: List[Dict[str, Any]], drift_metrics, total_cost: float, execution_time: float):
        """Display detailed consensus results."""

        print("\n📊 Model Responses:")
        print("─" * 60)

        for i, response in enumerate(responses, 1):
            status = "✅" if response["success"] else "❌"
            model_name = response["model"]
            cost = response["cost"]
            exec_time = response["execution_time"]

            print(f"{status} {model_name}:")
            print(f"   💰 Cost: ${cost:.6f}")
            print(f"   ⏱️  Time: {exec_time:.2f}s")

            if response["success"]:
                response_preview = response["response"][:100] + "..." if len(response["response"]) > 100 else response["response"]
                print(f"   💬 Response: {response_preview}")
            else:
                print(f"   ❌ Error: {response.get('error', 'Unknown error')}")
            print()

        print("📈 Consensus Analysis:")
        print("─" * 60)

        # Agreement metrics
        tar_score = drift_metrics.total_agreement_rate
        consistency_score = drift_metrics.consistency_score

        tar_color = "🟢" if tar_score >= 0.8 else "🟡" if tar_score >= 0.6 else "🔴"
        consistency_color = "🟢" if consistency_score >= 0.8 else "🟡" if consistency_score >= 0.6 else "🔴"

        print(f"{tar_color} Total Agreement Rate: {tar_score:.3f}")
        print(f"{consistency_color} Consistency Score: {consistency_score:.3f}")
        print(f"📏 Edit Distance: {drift_metrics.normalized_edit_distance:.3f}")

        if hasattr(drift_metrics, 'consensus_confidence'):
            print(f"🎯 Consensus Confidence: {drift_metrics.consensus_confidence:.3f}")

        print(f"\n💰 Total Cost: ${total_cost:.6f}")
        print(f"⏱️  Total Time: {execution_time:.2f}s")

        # Recommendations
        print("\n💡 Recommendations:")
        if tar_score < 0.7:
            print("   • High drift detected - review model outputs carefully")
            print("   • Consider adjusting temperature or prompt engineering")
        elif tar_score >= 0.8:
            print("   • Good consensus - responses are consistent")
            print("   • Consider using faster/cheaper models for similar queries")

    async def interactive_chat(self):
        """Start an interactive chat session with consensus mode."""
        print("\n🤖 Multi-Model Consensus Chat")
        print("=" * 60)
        print(f"Active Models: {', '.join(m.name for m in self.models if m.enabled)}")
        print("Type 'quit' to exit, 'models' to list models, 'cost' for cost summary")
        print()

        total_session_cost = 0.0
        conversation_history = []

        while True:
            try:
                question = input("💭 Your question: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    break
                elif question.lower() == 'models':
                    self._display_model_status()
                    continue
                elif question.lower() == 'cost':
                    self._display_cost_summary(total_session_cost, conversation_history)
                    continue
                elif not question:
                    continue

                # Get consensus response
                result = await self.consensus_query(question)
                total_session_cost += result.total_cost

                # Store conversation history
                conversation_history.append(result)

                # Display consensus response
                print(f"\n🤝 Consensus Response (Confidence: {result.confidence_score:.1%}):")
                print("─" * 60)
                print(result.consensus_response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        # Final summary
        print(f"\n📊 Session Summary:")
        print(f"💰 Total Cost: ${total_session_cost:.6f}")
        print(f"📝 Questions Asked: {len(conversation_history)}")
        print("👋 Thank you for using Multi-Model Chat!")

    def _display_model_status(self):
        """Display current model configuration."""
        print("\n🤖 Configured Models:")
        print("─" * 40)

        for model in self.models:
            status = "🟢" if model.enabled else "🔴"
            print(f"{status} {model.name}")
            print(f"   Provider: {model.provider}")
            print(f"   Model ID: {model.model_id}")
            print(f"   Temperature: {model.temperature}")
            print()

    def _display_cost_summary(self, total_cost: float, history: List[ConsensusResult]):
        """Display cost analysis summary."""
        print("\n💰 Cost Analysis:")
        print("─" * 40)

        print(f"Total Session Cost: ${total_cost:.6f}")

        if history:
            avg_cost_per_query = total_cost / len(history)
            print(f"Average Cost/Query: ${avg_cost_per_query:.6f}")

            # Cost by model
            model_costs = {}
            for result in history:
                for response in result.responses:
                    model_name = response["model"]
                    model_costs[model_name] = model_costs.get(model_name, 0) + response["cost"]

            print("\nCost by Model:")
            for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                print(f"  {model}: ${cost:.6f} ({percentage:.1f}%)")

async def main():
    """Main demonstration function."""
    print("🔭 Briefcase AI Multi-Model Chat Demo")
    print("=" * 50)

    # Configuration
    BRIEFCASE_API_KEY = "your-briefcase-ai-api-key"  # Replace with your API key
    OPENAI_API_KEY = "your-openai-api-key"  # Replace with your OpenAI key
    ANTHROPIC_API_KEY = "your-anthropic-api-key"  # Replace with your Anthropic key

    # Create chat instance
    chat = MultiModelChat(BRIEFCASE_API_KEY, agent_id=123)

    # Configure models
    chat.add_model(ModelConfig(
        name="GPT-4",
        provider="openai",
        model_id="gpt-4",
        temperature=0.7,
        api_key=OPENAI_API_KEY,
        enabled=True  # Set to False to disable
    ))

    chat.add_model(ModelConfig(
        name="GPT-3.5 Turbo",
        provider="openai",
        model_id="gpt-3.5-turbo",
        temperature=0.7,
        api_key=OPENAI_API_KEY,
        enabled=True  # Set to False to disable
    ))

    chat.add_model(ModelConfig(
        name="Claude 3 Sonnet",
        provider="anthropic",
        model_id="claude-3-sonnet-20240229",
        temperature=0.7,
        api_key=ANTHROPIC_API_KEY,
        enabled=True  # Set to False to disable
    ))

    # Demo questions
    demo_questions = [
        "What are the key benefits of renewable energy?",
        "Explain quantum computing in simple terms.",
        "What are the pros and cons of remote work?",
    ]

    # Run demo queries
    print("\n🎯 Running Demo Queries...")
    for question in demo_questions:
        try:
            result = await chat.consensus_query(question)
            print(f"\n✅ Consensus achieved with {result.confidence_score:.1%} confidence")
        except Exception as e:
            print(f"❌ Demo query failed: {e}")

    # Optional: Start interactive chat
    # await chat.interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())