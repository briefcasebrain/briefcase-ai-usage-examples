#!/usr/bin/env python3
"""
Hugging Face Integration Example

Demonstrates Briefcase AI telemetry with Hugging Face Transformers across various tasks:
- Text generation (GPT models)
- Text classification (sentiment analysis, topic classification)
- Question answering
- Summarization
- Translation
- Named entity recognition
- Feature extraction

Features demonstrated:
- Automatic telemetry capture for all model types
- Cost estimation and token tracking
- Performance monitoring
- Error handling
- Model metadata collection
"""

import asyncio
import sys
import os
from typing import List, Dict, Any
import time

# Add SDK path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'instrumentation'))

import briefcase_ai_telemetry as bai
from briefcase_ai_agent.integrations.huggingface_integration import (
    enable_huggingface_integration,
    create_instrumented_pipeline,
    disable_huggingface_integration
)

class HuggingFaceDemo:
    """Demonstration of Hugging Face telemetry integration."""

    def __init__(self, briefcase_api_key: str, agent_id: int = 1):
        self.briefcase_api_key = briefcase_api_key
        self.agent_id = agent_id
        self.session_stats = {
            "total_inferences": 0,
            "total_cost": 0.0,
            "total_time": 0.0,
            "errors": []
        }

    def setup_telemetry(self):
        """Initialize Hugging Face telemetry integration."""
        print("🔭 Setting up Hugging Face telemetry integration...")

        try:
            enable_huggingface_integration(
                agent_id=self.agent_id,
                api_key=self.briefcase_api_key,
                auto_capture_inputs=True,
                auto_capture_outputs=True,
                auto_calculate_costs=True,
                capture_model_info=True,
                capture_inference_params=True,
            )
            print("✅ Hugging Face telemetry enabled")
            return True
        except Exception as e:
            print(f"❌ Failed to enable telemetry: {e}")
            return False

    def demo_text_generation(self):
        """Demonstrate text generation with telemetry."""
        print("\n📝 Text Generation Demo")
        print("=" * 40)

        try:
            # Create text generation pipeline
            generator = create_instrumented_pipeline(
                "text-generation",
                model="distilgpt2",  # Smaller model for demo
                max_length=100,
                temperature=0.7,
                do_sample=True
            )

            # Test prompts
            prompts = [
                "The future of artificial intelligence is",
                "In a world where robots and humans coexist,",
                "The most important lesson I learned is"
            ]

            for prompt in prompts:
                print(f"\n🤖 Prompt: {prompt}")
                start_time = time.time()

                result = generator(prompt, max_length=80, num_return_sequences=1)

                execution_time = time.time() - start_time
                generated_text = result[0]['generated_text']

                print(f"📄 Generated: {generated_text}")
                print(f"⏱️  Time: {execution_time:.2f}s")

                self.session_stats["total_inferences"] += 1
                self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ Text generation error: {e}")
            self.session_stats["errors"].append(f"text_generation: {e}")

    def demo_text_classification(self):
        """Demonstrate text classification with telemetry."""
        print("\n🏷️ Text Classification Demo")
        print("=" * 40)

        try:
            # Create sentiment analysis pipeline
            classifier = create_instrumented_pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )

            # Test texts
            texts = [
                "I love this new technology!",
                "This is really disappointing and frustrating.",
                "The weather is okay today, nothing special.",
                "Amazing breakthrough in AI research!",
                "I'm not sure how I feel about this."
            ]

            for text in texts:
                print(f"\n📝 Text: {text}")
                start_time = time.time()

                result = classifier(text)

                execution_time = time.time() - start_time
                label = result[0]['label']
                score = result[0]['score']

                print(f"🏷️  Classification: {label} (confidence: {score:.3f})")
                print(f"⏱️  Time: {execution_time:.2f}s")

                self.session_stats["total_inferences"] += 1
                self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ Text classification error: {e}")
            self.session_stats["errors"].append(f"text_classification: {e}")

    def demo_question_answering(self):
        """Demonstrate question answering with telemetry."""
        print("\n❓ Question Answering Demo")
        print("=" * 40)

        try:
            # Create QA pipeline
            qa_pipeline = create_instrumented_pipeline(
                "question-answering",
                model="distilbert-base-uncased-distilled-squad"
            )

            # Test QA pairs
            context = """
            Artificial Intelligence (AI) is intelligence demonstrated by machines,
            in contrast to the natural intelligence displayed by humans and animals.
            Leading AI textbooks define the field as the study of "intelligent agents":
            any device that perceives its environment and takes actions that maximize
            its chance of successfully achieving its goals. Machine learning is a subset
            of AI that focuses on algorithms that can learn from and make predictions
            or decisions based on data.
            """

            questions = [
                "What is artificial intelligence?",
                "How is AI different from natural intelligence?",
                "What is machine learning?",
                "What do intelligent agents do?"
            ]

            for question in questions:
                print(f"\n❓ Question: {question}")
                start_time = time.time()

                result = qa_pipeline(question=question, context=context)

                execution_time = time.time() - start_time
                answer = result['answer']
                confidence = result['score']

                print(f"💭 Answer: {answer}")
                print(f"🎯 Confidence: {confidence:.3f}")
                print(f"⏱️  Time: {execution_time:.2f}s")

                self.session_stats["total_inferences"] += 1
                self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ Question answering error: {e}")
            self.session_stats["errors"].append(f"question_answering: {e}")

    def demo_summarization(self):
        """Demonstrate text summarization with telemetry."""
        print("\n📋 Summarization Demo")
        print("=" * 40)

        try:
            # Create summarization pipeline
            summarizer = create_instrumented_pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                max_length=150,
                min_length=40
            )

            # Long text for summarization
            long_text = """
            Climate change refers to long-term shifts in global temperatures and weather patterns.
            While climate changes may be natural, since the 1800s, human activities have been the
            main driver of climate change, primarily due to the burning of fossil fuels like coal,
            oil and gas. Burning fossil fuels generates greenhouse gas emissions that act like a
            blanket wrapped around the Earth, trapping the sun's heat and raising temperatures.
            The main greenhouse gases that are causing climate change include carbon dioxide and
            methane. These come from using gasoline for driving a car or coal for heating a building,
            for example. Clearing land and cutting down forests can also release carbon dioxide.
            Agriculture, oil and gas operations are major sources of methane emissions. Energy,
            industry, transport, buildings, agriculture and land use are among the main sectors
            causing greenhouse gas emissions.
            """

            print(f"📄 Original text length: {len(long_text)} characters")
            start_time = time.time()

            result = summarizer(long_text)

            execution_time = time.time() - start_time
            summary = result[0]['summary_text']

            print(f"\n📝 Summary: {summary}")
            print(f"📊 Summary length: {len(summary)} characters")
            print(f"📉 Compression ratio: {len(summary)/len(long_text):.2%}")
            print(f"⏱️  Time: {execution_time:.2f}s")

            self.session_stats["total_inferences"] += 1
            self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ Summarization error: {e}")
            self.session_stats["errors"].append(f"summarization: {e}")

    def demo_translation(self):
        """Demonstrate translation with telemetry."""
        print("\n🌍 Translation Demo")
        print("=" * 40)

        try:
            # Create translation pipeline
            translator = create_instrumented_pipeline(
                "translation_en_to_fr",
                model="Helsinki-NLP/opus-mt-en-fr"
            )

            # English texts to translate
            english_texts = [
                "Hello, how are you today?",
                "The weather is beautiful.",
                "I love learning new languages.",
                "Technology is advancing rapidly."
            ]

            for text in english_texts:
                print(f"\n🇺🇸 English: {text}")
                start_time = time.time()

                result = translator(text)

                execution_time = time.time() - start_time
                french_text = result[0]['translation_text']

                print(f"🇫🇷 French: {french_text}")
                print(f"⏱️  Time: {execution_time:.2f}s")

                self.session_stats["total_inferences"] += 1
                self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ Translation error: {e}")
            self.session_stats["errors"].append(f"translation: {e}")

    def demo_named_entity_recognition(self):
        """Demonstrate named entity recognition with telemetry."""
        print("\n🏷️ Named Entity Recognition Demo")
        print("=" * 40)

        try:
            # Create NER pipeline
            ner = create_instrumented_pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )

            # Test texts with entities
            texts = [
                "Apple Inc. was founded by Steve Jobs in Cupertino, California.",
                "The meeting will be held in New York on January 15th, 2024.",
                "Microsoft's CEO Satya Nadella announced new AI features.",
                "The University of Oxford is located in England."
            ]

            for text in texts:
                print(f"\n📝 Text: {text}")
                start_time = time.time()

                result = ner(text)

                execution_time = time.time() - start_time

                print(f"🏷️  Entities found:")
                for entity in result:
                    entity_text = entity['word']
                    entity_label = entity['entity_group']
                    confidence = entity['score']
                    print(f"   • {entity_text} ({entity_label}, {confidence:.3f})")

                print(f"⏱️  Time: {execution_time:.2f}s")

                self.session_stats["total_inferences"] += 1
                self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ NER error: {e}")
            self.session_stats["errors"].append(f"ner: {e}")

    def demo_feature_extraction(self):
        """Demonstrate feature extraction with telemetry."""
        print("\n🔢 Feature Extraction Demo")
        print("=" * 40)

        try:
            # Create feature extraction pipeline
            feature_extractor = create_instrumented_pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )

            # Test sentences
            sentences = [
                "This is a sample sentence.",
                "Here is another example.",
                "Feature extraction converts text to vectors."
            ]

            for sentence in sentences:
                print(f"\n📝 Text: {sentence}")
                start_time = time.time()

                result = feature_extractor(sentence)

                execution_time = time.time() - start_time

                # Get feature vector information
                if result and len(result) > 0:
                    features = result[0]  # First result
                    if hasattr(features, 'shape'):
                        feature_shape = features.shape
                    elif isinstance(features, list):
                        feature_shape = (len(features),)
                    else:
                        feature_shape = "unknown"

                    print(f"🔢 Feature vector shape: {feature_shape}")
                    if isinstance(features, list) and len(features) > 0:
                        print(f"📊 Sample values: {features[:5]}...")

                print(f"⏱️  Time: {execution_time:.2f}s")

                self.session_stats["total_inferences"] += 1
                self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ Feature extraction error: {e}")
            self.session_stats["errors"].append(f"feature_extraction: {e}")

    def demo_custom_model_workflow(self):
        """Demonstrate custom model workflow with manual instrumentation."""
        print("\n🔧 Custom Model Workflow Demo")
        print("=" * 40)

        try:
            import torch
            from transformers import AutoTokenizer, AutoModel

            # Load model and tokenizer directly
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)

            # Text to process
            text = "This is a custom workflow example."
            print(f"📝 Processing: {text}")

            # Manual instrumentation
            agent = bai.AgentInstrument(self.agent_id,
                                      bai.TelemetryClient(self.briefcase_api_key),
                                      bai.InstrumentationConfig())

            agent.start()
            agent.add_input(text)

            start_time = time.time()

            # Tokenize
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

            # Forward pass
            with torch.no_grad():
                outputs = model(**inputs)

            # Get embeddings
            embeddings = outputs.last_hidden_state.mean(dim=1)

            execution_time = time.time() - start_time

            # Add results to telemetry
            agent.add_output(f"Embeddings shape: {embeddings.shape}")
            agent.add_metadata("model_info", {
                "model_name": model_name,
                "custom_workflow": True,
                "embedding_dim": embeddings.shape[1],
                "execution_time": execution_time
            })

            print(f"🔢 Embeddings shape: {embeddings.shape}")
            print(f"⏱️  Time: {execution_time:.2f}s")

            agent.end()

            self.session_stats["total_inferences"] += 1
            self.session_stats["total_time"] += execution_time

        except Exception as e:
            print(f"❌ Custom workflow error: {e}")
            self.session_stats["errors"].append(f"custom_workflow: {e}")

    def display_session_summary(self):
        """Display comprehensive session summary."""
        print("\n📊 Session Summary")
        print("=" * 50)

        print(f"🔍 Total Inferences: {self.session_stats['total_inferences']}")
        print(f"⏱️  Total Time: {self.session_stats['total_time']:.2f}s")

        if self.session_stats['total_inferences'] > 0:
            avg_time = self.session_stats['total_time'] / self.session_stats['total_inferences']
            print(f"📈 Average Time/Inference: {avg_time:.2f}s")

        if self.session_stats['total_cost'] > 0:
            print(f"💰 Total Cost: ${self.session_stats['total_cost']:.6f}")

        if self.session_stats['errors']:
            print(f"\n❌ Errors Encountered ({len(self.session_stats['errors'])}):")
            for error in self.session_stats['errors']:
                print(f"   • {error}")
        else:
            print("\n✅ All demos completed successfully!")

        print("\n🔭 Telemetry Integration Benefits:")
        print("   • Automatic cost tracking across all HF models")
        print("   • Performance monitoring and optimization")
        print("   • Error detection and debugging")
        print("   • Model usage analytics")
        print("   • Compliance and audit trails")

    def cleanup(self):
        """Clean up telemetry integration."""
        print("\n🧹 Cleaning up...")
        disable_huggingface_integration()
        print("✅ Hugging Face telemetry disabled")

async def main():
    """Main demonstration function."""
    print("🤗 Briefcase AI + Hugging Face Integration Demo")
    print("=" * 60)

    # Configuration
    BRIEFCASE_API_KEY = "your-briefcase-ai-api-key"  # Replace with your API key

    # Create demo instance
    demo = HuggingFaceDemo(BRIEFCASE_API_KEY, agent_id=789)

    # Setup telemetry
    if not demo.setup_telemetry():
        print("❌ Failed to setup telemetry, exiting...")
        return

    try:
        # Run all demos
        print("\n🚀 Starting Hugging Face telemetry demonstrations...")

        demo.demo_text_generation()
        await asyncio.sleep(1)

        demo.demo_text_classification()
        await asyncio.sleep(1)

        demo.demo_question_answering()
        await asyncio.sleep(1)

        demo.demo_summarization()
        await asyncio.sleep(1)

        demo.demo_translation()
        await asyncio.sleep(1)

        demo.demo_named_entity_recognition()
        await asyncio.sleep(1)

        demo.demo_feature_extraction()
        await asyncio.sleep(1)

        demo.demo_custom_model_workflow()

        # Display summary
        demo.display_session_summary()

    except Exception as e:
        print(f"❌ Demo failed: {e}")

    finally:
        demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main())