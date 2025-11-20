# Hugging Face Integration Guide

This guide provides comprehensive information on integrating Briefcase AI Telemetry SDK with Hugging Face transformers and related libraries.

## Overview

The Hugging Face integration automatically instruments Hugging Face components to capture:

- Model inference calls (transformers, pipeline, etc.)
- Dataset loading and processing operations
- Training and fine-tuning metrics
- Token usage and computational costs
- Model performance metrics
- Error tracking and debugging information
- Memory and GPU usage monitoring

## Quick Start

### Basic Setup

```python
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration

# Configure and enable automatic instrumentation
huggingface_integration.configure(
    api_key="your-briefcase-api-key",
    default_agent_id=401,
    auto_capture_inputs=True,
    auto_capture_outputs=True,
    track_model_performance=True
)

# Enable instrumentation
huggingface_integration.enable_instrumentation()

# Your existing Hugging Face code works unchanged
classifier = pipeline("sentiment-analysis")

result = classifier("I love using this SDK!")
print(result)
```

### Environment Variables

Set these environment variables for easier configuration:

```bash
export BRIEFCASE_API_KEY="your-briefcase-api-key"
export HF_TOKEN="your-huggingface-token"  # Optional: for private models
export BRIEFCASE_AGENT_ID="401"
```

Then use simplified setup:

```python
from briefcase_ai_agent.integrations import huggingface_integration

# Auto-configure from environment variables
huggingface_integration.auto_configure()
huggingface_integration.enable_instrumentation()
```

## Configuration Options

### InstrumentationConfig

```python
from briefcase_ai_agent.integrations.huggingface_integration import HuggingFaceInstrumentationConfig

config = HuggingFaceInstrumentationConfig(
    auto_capture_inputs=True,          # Capture model inputs
    auto_capture_outputs=True,         # Capture model outputs
    track_model_performance=True,      # Track performance metrics
    track_memory_usage=True,          # Monitor memory usage
    track_gpu_usage=True,             # Monitor GPU usage (if available)
    capture_model_info=True,          # Capture model metadata
    capture_dataset_info=True,        # Capture dataset information
    default_agent_id=401,            # Default agent ID for tracking
    enabled=True,                    # Enable/disable instrumentation
    api_key="your-briefcase-key",    # Briefcase API key
    endpoint=None,                   # Custom endpoint (optional)
    max_input_length=5000,           # Max input text length
    max_output_length=5000,          # Max output text length
    sample_rate=1.0                  # Sample rate for tracking (0.0-1.0)
)

huggingface_integration.configure_from_object(config)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_capture_inputs` | bool | True | Automatically capture model inputs |
| `auto_capture_outputs` | bool | True | Automatically capture model outputs |
| `track_model_performance` | bool | True | Track inference timing and performance |
| `track_memory_usage` | bool | True | Monitor memory usage during inference |
| `track_gpu_usage` | bool | True | Monitor GPU usage (if available) |
| `capture_model_info` | bool | True | Capture model metadata and configuration |
| `capture_dataset_info` | bool | True | Capture dataset information |
| `default_agent_id` | int | None | Default agent ID for events |
| `enabled` | bool | True | Enable/disable instrumentation |
| `max_input_length` | int | 5000 | Maximum input text length |
| `max_output_length` | int | 5000 | Maximum output text length |
| `sample_rate` | float | 1.0 | Sampling rate for tracking (0.0-1.0) |

## Pipeline Support

### Text Classification

```python
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration

huggingface_integration.enable_instrumentation()

# Sentiment analysis
sentiment_pipeline = pipeline("sentiment-analysis")
result = sentiment_pipeline("This product is amazing!")

# Zero-shot classification
classifier = pipeline("zero-shot-classification")
result = classifier(
    "This is a course about the Python programming language",
    candidate_labels=["education", "politics", "business"]
)

# Token classification (NER)
ner_pipeline = pipeline("ner", aggregation_strategy="simple")
result = ner_pipeline("My name is Wolfgang and I live in Berlin")
```

### Text Generation

```python
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration

huggingface_integration.enable_instrumentation()

# Text generation
generator = pipeline("text-generation", model="gpt2")
result = generator(
    "The future of artificial intelligence is",
    max_length=100,
    num_return_sequences=2
)

# Conversational AI
chatbot = pipeline("conversational")
conversation = chatbot("Going to the movies tonight - any suggestions?")
```

### Translation and Summarization

```python
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration

huggingface_integration.enable_instrumentation()

# Translation
translator = pipeline("translation", model="t5-base")
result = translator("translate English to French: Hello, how are you?")

# Summarization
summarizer = pipeline("summarization")
text = """
The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building,
and the tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side.
"""
summary = summarizer(text, max_length=50, min_length=10, do_sample=False)
```

### Question Answering

```python
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration

huggingface_integration.enable_instrumentation()

# Question answering
qa_pipeline = pipeline("question-answering")
context = "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France."
question = "Where is the Eiffel Tower located?"

result = qa_pipeline(question=question, context=context)
```

## Model Training and Fine-tuning

### Training Loop Instrumentation

```python
import torch
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification
from briefcase_ai_agent.integrations import huggingface_integration
import briefcase_ai_telemetry as bai

huggingface_integration.enable_instrumentation()

class InstrumentedTrainer(Trainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.training_session_id = bai.generate_uuid()

    def log(self, logs):
        super().log(logs)

        # Track training metrics
        if "loss" in logs:
            training_event = bai.EventBuilder("hf_training_step")
                .level(bai.EventLevel.info())
                .agent_id(401)
                .tag("session_id", self.training_session_id)
                .tag("model", self.model.config.model_type)
                .custom_data("loss", logs["loss"])
                .custom_data("learning_rate", logs.get("learning_rate", 0))
                .custom_data("epoch", logs.get("epoch", 0))
                .build()

            huggingface_integration.get_telemetry_client().track_event(training_event)

# Usage
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    logging_steps=10
)

trainer = InstrumentedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()
```

### Fine-tuning with Automatic Tracking

```python
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from briefcase_ai_agent.integrations import huggingface_integration
import briefcase_ai_telemetry as bai

huggingface_integration.enable_instrumentation()

def fine_tune_model(model_name, train_dataset, eval_dataset):
    """Fine-tune a model with automatic tracking."""

    # Track fine-tuning start
    start_event = bai.EventBuilder("hf_finetuning_start")
        .level(bai.EventLevel.info())
        .agent_id(401)
        .tag("base_model", model_name)
        .custom_data("train_size", len(train_dataset))
        .custom_data("eval_size", len(eval_dataset))
        .build()

    huggingface_integration.get_telemetry_client().track_event(start_event)

    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./fine_tuned_model",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=100,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
    )

    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )

    # Train model (automatically tracked)
    trainer.train()

    # Track completion
    completion_event = bai.EventBuilder("hf_finetuning_complete")
        .level(bai.EventLevel.info())
        .agent_id(401)
        .tag("base_model", model_name)
        .tag("status", "success")
        .build()

    huggingface_integration.get_telemetry_client().track_event(completion_event)

    return trainer

# Usage
trainer = fine_tune_model("distilbert-base-uncased", train_dataset, eval_dataset)
```

## Dataset Operations

### Dataset Loading and Processing

```python
from datasets import load_dataset, Dataset
from briefcase_ai_agent.integrations import huggingface_integration
import briefcase_ai_telemetry as bai

huggingface_integration.enable_instrumentation()

# Load dataset (automatically tracked)
dataset = load_dataset("imdb", split="train")

# Process dataset with tracking
def preprocess_with_tracking(dataset, tokenizer, agent_id=401):
    """Preprocess dataset with automatic tracking."""

    start_event = bai.EventBuilder("hf_dataset_preprocessing_start")
        .level(bai.EventLevel.info())
        .agent_id(agent_id)
        .custom_data("dataset_size", len(dataset))
        .build()

    huggingface_integration.get_telemetry_client().track_event(start_event)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    # Process dataset
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Track completion
    completion_event = bai.EventBuilder("hf_dataset_preprocessing_complete")
        .level(bai.EventLevel.info())
        .agent_id(agent_id)
        .custom_data("original_size", len(dataset))
        .custom_data("processed_size", len(tokenized_dataset))
        .build()

    huggingface_integration.get_telemetry_client().track_event(completion_event)

    return tokenized_dataset

# Usage
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
processed_dataset = preprocess_with_tracking(dataset, tokenizer)
```

## Advanced Usage

### Custom Model Instrumentation

```python
import torch
import torch.nn as nn
from briefcase_ai_agent.integrations import huggingface_integration
import briefcase_ai_telemetry as bai
import time

huggingface_integration.enable_instrumentation()

class InstrumentedModel(nn.Module):
    def __init__(self, base_model, agent_id=401):
        super().__init__()
        self.base_model = base_model
        self.agent_id = agent_id
        self.inference_count = 0

    def forward(self, *args, **kwargs):
        """Forward pass with automatic tracking."""
        self.inference_count += 1
        start_time = time.time()

        # Memory tracking
        if torch.cuda.is_available():
            start_memory = torch.cuda.memory_allocated()

        try:
            # Forward pass
            outputs = self.base_model(*args, **kwargs)

            # Calculate metrics
            inference_time = int((time.time() - start_time) * 1000)

            memory_used = 0
            if torch.cuda.is_available():
                memory_used = torch.cuda.memory_allocated() - start_memory

            # Track successful inference
            inference_event = bai.EventBuilder("hf_model_inference")
                .level(bai.EventLevel.info())
                .agent_id(self.agent_id)
                .duration_ms(inference_time)
                .tag("model_type", self.base_model.__class__.__name__)
                .custom_data("inference_count", self.inference_count)
                .custom_data("memory_used_bytes", memory_used)
                .custom_data("input_shape", str(args[0].shape) if args else "unknown")
                .build()

            huggingface_integration.get_telemetry_client().track_event(inference_event)

            return outputs

        except Exception as e:
            # Track inference errors
            error_event = bai.EventBuilder("hf_model_inference_error")
                .level(bai.EventLevel.error())
                .agent_id(self.agent_id)
                .error(str(e))
                .tag("model_type", self.base_model.__class__.__name__)
                .build()

            huggingface_integration.get_telemetry_client().track_event(error_event)
            raise

# Usage
from transformers import AutoModel
base_model = AutoModel.from_pretrained("bert-base-uncased")
instrumented_model = InstrumentedModel(base_model)
```

### Batch Processing with Performance Tracking

```python
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration
import briefcase_ai_telemetry as bai
import time

huggingface_integration.enable_instrumentation()

def batch_inference_with_tracking(pipeline_obj, texts, batch_size=8, agent_id=401):
    """Process texts in batches with performance tracking."""

    total_texts = len(texts)
    total_start_time = time.time()

    # Track batch job start
    batch_event = bai.EventBuilder("hf_batch_inference_start")
        .level(bai.EventLevel.info())
        .agent_id(agent_id)
        .custom_data("total_texts", total_texts)
        .custom_data("batch_size", batch_size)
        .tag("pipeline_task", pipeline_obj.task)
        .build()

    huggingface_integration.get_telemetry_client().track_event(batch_event)

    results = []

    # Process in batches
    for i in range(0, total_texts, batch_size):
        batch_start_time = time.time()
        batch_texts = texts[i:i+batch_size]

        try:
            # Process batch
            batch_results = pipeline_obj(batch_texts)
            results.extend(batch_results)

            # Track batch completion
            batch_time = int((time.time() - batch_start_time) * 1000)

            batch_complete_event = bai.EventBuilder("hf_batch_processed")
                .level(bai.EventLevel.info())
                .agent_id(agent_id)
                .duration_ms(batch_time)
                .custom_data("batch_index", i // batch_size)
                .custom_data("batch_size", len(batch_texts))
                .custom_data("texts_per_second", len(batch_texts) / (batch_time / 1000))
                .build()

            huggingface_integration.get_telemetry_client().track_event(batch_complete_event)

        except Exception as e:
            # Track batch errors
            error_event = bai.EventBuilder("hf_batch_error")
                .level(bai.EventLevel.error())
                .agent_id(agent_id)
                .error(str(e))
                .custom_data("batch_index", i // batch_size)
                .build()

            huggingface_integration.get_telemetry_client().track_event(error_event)
            continue

    # Track overall completion
    total_time = int((time.time() - total_start_time) * 1000)

    completion_event = bai.EventBuilder("hf_batch_inference_complete")
        .level(bai.EventLevel.info())
        .agent_id(agent_id)
        .duration_ms(total_time)
        .custom_data("total_processed", len(results))
        .custom_data("success_rate", len(results) / total_texts)
        .custom_data("throughput", len(results) / (total_time / 1000))
        .tag("pipeline_task", pipeline_obj.task)
        .build()

    huggingface_integration.get_telemetry_client().track_event(completion_event)

    return results

# Usage
classifier = pipeline("sentiment-analysis")
texts = ["I love this!", "This is terrible.", "It's okay.", "Amazing work!"]
results = batch_inference_with_tracking(classifier, texts, batch_size=2)
```

## Best Practices

### 1. Environment-Based Configuration

```python
import os
from briefcase_ai_agent.integrations import huggingface_integration

environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    huggingface_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY"),
        auto_capture_inputs=False,      # Don't capture inputs in production
        auto_capture_outputs=False,     # Don't capture outputs in production
        track_model_performance=True,   # But do track performance
        max_input_length=1000,         # Limit data size
        sample_rate=0.1,               # Sample only 10% of requests
        endpoint="https://observe.briefcasebrain.io/api/v1/telemetry"
    )
else:
    huggingface_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY_DEV"),
        auto_capture_inputs=True,       # Full tracking in dev
        auto_capture_outputs=True,
        sample_rate=1.0,               # Track everything in dev
        endpoint="https://api-dev.briefcase.ai/telemetry"
    )

huggingface_integration.enable_instrumentation()
```

### 2. Memory-Conscious Configuration

```python
from briefcase_ai_agent.integrations import huggingface_integration

# For resource-constrained environments
huggingface_integration.configure(
    api_key="your-briefcase-key",
    track_memory_usage=False,       # Disable memory tracking if overhead is concern
    track_gpu_usage=False,          # Disable GPU tracking if not needed
    max_input_length=500,           # Limit captured text
    max_output_length=500,
    sample_rate=0.5                 # Sample 50% of requests
)
```

### 3. Model Lifecycle Tracking

```python
from transformers import AutoModel
from briefcase_ai_agent.integrations import huggingface_integration
import briefcase_ai_telemetry as bai

huggingface_integration.enable_instrumentation()

class ModelManager:
    def __init__(self, model_name, agent_id=401):
        self.model_name = model_name
        self.agent_id = agent_id
        self.model = None
        self.load_count = 0

    def load_model(self):
        """Load model with tracking."""
        start_time = time.time()

        try:
            self.model = AutoModel.from_pretrained(self.model_name)
            self.load_count += 1

            # Track successful load
            load_event = bai.EventBuilder("hf_model_loaded")
                .level(bai.EventLevel.info())
                .agent_id(self.agent_id)
                .duration_ms(int((time.time() - start_time) * 1000))
                .tag("model_name", self.model_name)
                .custom_data("load_count", self.load_count)
                .build()

            huggingface_integration.get_telemetry_client().track_event(load_event)

        except Exception as e:
            # Track load errors
            error_event = bai.EventBuilder("hf_model_load_error")
                .level(bai.EventLevel.error())
                .agent_id(self.agent_id)
                .error(str(e))
                .tag("model_name", self.model_name)
                .build()

            huggingface_integration.get_telemetry_client().track_event(error_event)
            raise

    def unload_model(self):
        """Unload model with tracking."""
        if self.model:
            # Track model unload
            unload_event = bai.EventBuilder("hf_model_unloaded")
                .level(bai.EventLevel.info())
                .agent_id(self.agent_id)
                .tag("model_name", self.model_name)
                .build()

            huggingface_integration.get_telemetry_client().track_event(unload_event)

            del self.model
            self.model = None

# Usage
model_manager = ModelManager("bert-base-uncased")
model_manager.load_model()
# ... use model ...
model_manager.unload_model()
```

## Integration Examples

### Web API with Model Serving

```python
from fastapi import FastAPI, HTTPException
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration

app = FastAPI()

@app.on_event("startup")
async def startup():
    huggingface_integration.configure(api_key="your-briefcase-key")
    huggingface_integration.enable_instrumentation()

    # Load models
    app.sentiment_classifier = pipeline("sentiment-analysis")
    app.summarizer = pipeline("summarization")

@app.post("/sentiment")
async def analyze_sentiment(text: str):
    try:
        result = app.sentiment_classifier(text)
        return {"sentiment": result[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize_text(text: str, max_length: int = 100):
    try:
        result = app.summarizer(text, max_length=max_length, min_length=10)
        return {"summary": result[0]["summary_text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown():
    client = huggingface_integration.get_telemetry_client()
    if client:
        client.flush()
```

### Multi-Model Ensemble

```python
from transformers import pipeline
from briefcase_ai_agent.integrations import huggingface_integration
import briefcase_ai_telemetry as bai

huggingface_integration.enable_instrumentation()

class ModelEnsemble:
    def __init__(self, models, task="sentiment-analysis", agent_id=401):
        self.task = task
        self.agent_id = agent_id
        self.ensemble_id = bai.generate_uuid()

        # Load multiple models
        self.models = {}
        for name, model_name in models.items():
            self.models[name] = pipeline(task, model=model_name)

    def predict(self, text):
        """Get predictions from all models."""
        start_time = time.time()
        predictions = {}

        # Track ensemble start
        ensemble_event = bai.EventBuilder("hf_ensemble_prediction_start")
            .level(bai.EventLevel.info())
            .agent_id(self.agent_id)
            .tag("ensemble_id", self.ensemble_id)
            .custom_data("model_count", len(self.models))
            .build()

        huggingface_integration.get_telemetry_client().track_event(ensemble_event)

        # Get predictions from each model
        for model_name, model in self.models.items():
            try:
                prediction = model(text)
                predictions[model_name] = prediction
            except Exception as e:
                print(f"Error with model {model_name}: {e}")

        # Track ensemble completion
        completion_event = bai.EventBuilder("hf_ensemble_prediction_complete")
            .level(bai.EventLevel.info())
            .agent_id(self.agent_id)
            .tag("ensemble_id", self.ensemble_id)
            .duration_ms(int((time.time() - start_time) * 1000))
            .custom_data("successful_models", len(predictions))
            .build()

        huggingface_integration.get_telemetry_client().track_event(completion_event)

        return predictions

    def consensus_predict(self, text):
        """Get consensus prediction across models."""
        predictions = self.predict(text)

        # Simple majority voting for sentiment analysis
        positive_count = sum(1 for pred in predictions.values()
                           if pred[0]["label"] == "POSITIVE")

        consensus = "POSITIVE" if positive_count > len(predictions) / 2 else "NEGATIVE"
        confidence = positive_count / len(predictions)

        return {
            "consensus": consensus,
            "confidence": confidence,
            "individual_predictions": predictions
        }

# Usage
ensemble = ModelEnsemble({
    "distilbert": "distilbert-base-uncased-finetuned-sst-2-english",
    "roberta": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "bert": "nlptown/bert-base-multilingual-uncased-sentiment"
})

result = ensemble.consensus_predict("I love this new feature!")
```

## Troubleshooting

### Common Issues

1. **High memory usage**: Reduce `max_input_length` and `max_output_length`
2. **Performance impact**: Set `sample_rate` < 1.0 or disable input/output capture
3. **GPU tracking issues**: Ensure CUDA is available when `track_gpu_usage=True`

### Debug Mode

```python
import logging
from briefcase_ai_agent.integrations import huggingface_integration

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("briefcase_ai_agent.integrations.huggingface_integration")
logger.setLevel(logging.DEBUG)

huggingface_integration.enable_instrumentation()
```

### Health Check

```python
from briefcase_ai_agent.integrations import huggingface_integration
from transformers import pipeline

# Check integration status
print(f"Instrumentation enabled: {huggingface_integration.is_instrumentation_enabled()}")
print(f"Telemetry client: {huggingface_integration.get_telemetry_client() is not None}")

# Test basic functionality
try:
    classifier = pipeline("sentiment-analysis")
    result = classifier("Test message")
    print("✅ Basic pipeline test successful")
except Exception as e:
    print(f"❌ Basic pipeline test failed: {e}")
```

This Hugging Face integration provides comprehensive tracking of your transformer models and ML workflows with minimal code changes.