# LangChain Integration Guide

This guide provides comprehensive information on integrating Briefcase AI Telemetry SDK with LangChain applications.

## Overview

The LangChain integration automatically instruments LangChain components to capture:

- Chain executions (SimpleSequentialChain, SequentialChain, etc.)
- Agent runs and decision-making processes
- Tool usage and function calls
- Document retrieval and search operations
- Memory operations and context management
- Cost tracking across different LLM providers
- Performance metrics and execution traces

## Quick Start

### Basic Setup

```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from briefcase_ai_agent.integrations import langchain_integration

# Configure and enable automatic instrumentation
langchain_integration.configure(
    api_key="your-briefcase-api-key",
    default_agent_id=201,
    auto_capture_inputs=True,
    auto_capture_outputs=True,
    capture_chain_steps=True,
    auto_calculate_costs=True
)

# Enable instrumentation
langchain_integration.enable_instrumentation()

# Your existing LangChain code works unchanged
llm = OpenAI(openai_api_key="your-openai-key")

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a short article about {topic}"
)

chain = LLMChain(llm=llm, prompt=prompt)

# This execution will be automatically tracked
result = chain.run("artificial intelligence")
print(result)
```

### Environment Variables

Set these environment variables for easier configuration:

```bash
export BRIEFCASE_API_KEY="your-briefcase-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export BRIEFCASE_AGENT_ID="201"
export LANGCHAIN_TRACING_V2="true"  # Optional: Enable LangSmith
```

Then use simplified setup:

```python
from briefcase_ai_agent.integrations import langchain_integration

# Auto-configure from environment variables
langchain_integration.auto_configure()
langchain_integration.enable_instrumentation()
```

## Configuration Options

### InstrumentationConfig

```python
from briefcase_ai_agent.integrations.langchain_integration import LangChainInstrumentationConfig

config = LangChainInstrumentationConfig(
    auto_capture_inputs=True,        # Capture chain inputs
    auto_capture_outputs=True,       # Capture chain outputs
    auto_calculate_costs=True,       # Track LLM costs
    capture_chain_steps=True,        # Track individual chain steps
    capture_tool_usage=True,         # Track tool/function calls
    capture_retrieval_docs=False,    # Capture retrieved documents (can be large)
    capture_agent_thoughts=True,     # Capture agent reasoning
    default_agent_id=201,           # Default agent ID
    enabled=True,                   # Enable/disable instrumentation
    api_key="your-briefcase-key",   # Briefcase API key
    endpoint=None,                  # Custom endpoint (optional)
    max_input_length=10000,         # Max input text length
    max_output_length=10000         # Max output text length
)

langchain_integration.configure_from_object(config)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_capture_inputs` | bool | True | Capture chain/agent inputs |
| `auto_capture_outputs` | bool | True | Capture chain/agent outputs |
| `auto_calculate_costs` | bool | True | Calculate and track LLM costs |
| `capture_chain_steps` | bool | True | Track individual steps in chains |
| `capture_tool_usage` | bool | True | Track tool and function usage |
| `capture_retrieval_docs` | bool | False | Capture retrieved documents |
| `capture_agent_thoughts` | bool | True | Capture agent reasoning process |
| `default_agent_id` | int | None | Default agent ID for events |
| `enabled` | bool | True | Enable/disable instrumentation |
| `max_input_length` | int | 10000 | Maximum input text length |
| `max_output_length` | int | 10000 | Maximum output text length |

## Chain Types Support

### Simple Chains

```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from briefcase_ai_agent.integrations import langchain_integration

langchain_integration.enable_instrumentation()

llm = OpenAI()
prompt = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?"
)

# Simple chain - automatically tracked
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("colorful socks")
```

### Sequential Chains

```python
from langchain.chains import SimpleSequentialChain
from briefcase_ai_agent.integrations import langchain_integration

langchain_integration.enable_instrumentation()

# First chain
first_prompt = PromptTemplate(
    input_variables=["product"],
    template="What is the best name for a company that makes {product}?"
)
first_chain = LLMChain(llm=llm, prompt=first_prompt)

# Second chain
second_prompt = PromptTemplate(
    input_variables=["company_name"],
    template="Write a catchphrase for the following company: {company_name}"
)
second_chain = LLMChain(llm=llm, prompt=second_prompt)

# Sequential chain - each step tracked
overall_chain = SimpleSequentialChain(
    chains=[first_chain, second_chain],
    verbose=True
)

catchphrase = overall_chain.run("colorful socks")
```

## Agent Support

### ReAct Agents

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from briefcase_ai_agent.integrations import langchain_integration

langchain_integration.configure(
    api_key="your-briefcase-key",
    capture_agent_thoughts=True,
    capture_tool_usage=True
)
langchain_integration.enable_instrumentation()

# Define tools
def search_tool(query: str) -> str:
    return f"Search results for: {query}"

def calculator_tool(expression: str) -> str:
    try:
        return str(eval(expression))
    except:
        return "Invalid expression"

tools = [
    Tool(
        name="Search",
        func=search_tool,
        description="Search for information"
    ),
    Tool(
        name="Calculator",
        func=calculator_tool,
        description="Calculate mathematical expressions"
    )
]

# Create agent
agent = create_react_agent(
    llm=OpenAI(),
    tools=tools,
    prompt=PromptTemplate.from_template("""
    Answer the following questions as best you can.
    You have access to the following tools: {tools}

    Question: {input}
    {agent_scratchpad}
    """)
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Agent execution - fully tracked including tool usage
result = agent_executor.invoke({
    "input": "What is 25 * 4 and then search for information about that number?"
})
```

### Custom Agents

```python
from langchain.agents import BaseSingleActionAgent
from briefcase_ai_agent.integrations import langchain_integration
import briefcase_ai_telemetry as bai

class CustomAgent(BaseSingleActionAgent):
    def plan(self, intermediate_steps, **kwargs):
        # Custom agent logic - will be automatically tracked
        return AgentAction(tool="search", tool_input="custom query", log="Custom reasoning")

langchain_integration.enable_instrumentation()

# Custom agents are automatically tracked
custom_agent = CustomAgent()
agent_executor = AgentExecutor(agent=custom_agent, tools=tools)
result = agent_executor.run("Some query")
```

## Retrieval-Augmented Generation (RAG)

### Document Retrieval

```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from briefcase_ai_agent.integrations import langchain_integration

langchain_integration.configure(
    api_key="your-briefcase-key",
    capture_retrieval_docs=True  # Enable document capture
)
langchain_integration.enable_instrumentation()

# Load and split documents
loader = TextLoader("path/to/document.txt")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

# Create retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# Query - retrieval and generation tracked
result = qa_chain({"query": "What is the main topic of the document?"})
```

### Custom Retrievers

```python
from langchain.retrievers import BaseRetriever
from langchain.schema import Document
from briefcase_ai_agent.integrations import langchain_integration

class CustomRetriever(BaseRetriever):
    def get_relevant_documents(self, query: str) -> List[Document]:
        # Custom retrieval logic - automatically tracked
        return [Document(page_content=f"Relevant content for: {query}")]

langchain_integration.enable_instrumentation()

retriever = CustomRetriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=retriever
)

result = qa_chain({"query": "Custom retrieval query"})
```

## Memory and Context Management

### Conversation Memory

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from briefcase_ai_agent.integrations import langchain_integration

langchain_integration.enable_instrumentation()

# Memory operations are automatically tracked
memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=OpenAI(),
    memory=memory,
    verbose=True
)

# Each turn tracked with memory context
conversation.predict(input="Hi there!")
conversation.predict(input="What did I just say?")
```

### Custom Memory

```python
from langchain.memory.base import BaseMemory
from briefcase_ai_agent.integrations import langchain_integration

class CustomMemory(BaseMemory):
    def save_context(self, inputs, outputs):
        # Memory operations tracked automatically
        pass

    def load_memory_variables(self, inputs):
        return {}

langchain_integration.enable_instrumentation()
memory = CustomMemory()
```

## Advanced Usage

### Manual Event Tracking

```python
from briefcase_ai_agent.integrations import langchain_integration
import briefcase_ai_telemetry as bai
import time

langchain_integration.configure(api_key="your-briefcase-key")

# Manual chain tracking
def tracked_chain_execution(chain, inputs):
    start_time = time.time()

    try:
        result = chain.run(inputs)

        # Track successful execution
        event = bai.EventBuilder("langchain_chain_success")
            .level(bai.EventLevel.info())
            .agent_id(201)
            .duration_ms(int((time.time() - start_time) * 1000))
            .tag("chain_type", type(chain).__name__)
            .tag("status", "success")
            .custom_data("inputs", inputs)
            .custom_data("output_length", len(result))
            .build()

        langchain_integration.get_telemetry_client().track_event(event)
        return result

    except Exception as e:
        # Track errors
        error_event = bai.EventBuilder("langchain_chain_error")
            .level(bai.EventLevel.error())
            .agent_id(201)
            .error(str(e))
            .tag("chain_type", type(chain).__name__)
            .tag("status", "error")
            .build()

        langchain_integration.get_telemetry_client().track_event(error_event)
        raise

# Usage
result = tracked_chain_execution(my_chain, "input text")
```

### Cost Tracking

```python
from briefcase_ai_agent.integrations import langchain_integration
import briefcase_ai_telemetry as bai

langchain_integration.configure(auto_calculate_costs=True)
langchain_integration.enable_instrumentation()

# Automatic cost tracking for supported LLMs
llm = OpenAI(model_name="gpt-4")
chain = LLMChain(llm=llm, prompt=prompt)

# Costs automatically calculated and tracked
result = chain.run("Expensive GPT-4 query")

# Manual cost calculation if needed
cost_calc = bai.CostCalculator()
cost = cost_calc.calculate_openai_cost(
    model="gpt-4",
    prompt_tokens=100,
    completion_tokens=50
)
```

### Performance Monitoring

```python
from briefcase_ai_agent.integrations import langchain_integration
import briefcase_ai_telemetry as bai

langchain_integration.enable_instrumentation()

# Set up performance monitoring
def monitor_chain_performance(chain, inputs, threshold_ms=5000):
    start_time = time.time()
    result = chain.run(inputs)
    duration_ms = int((time.time() - start_time) * 1000)

    if duration_ms > threshold_ms:
        # Track slow chains
        slow_event = bai.EventBuilder("langchain_slow_chain")
            .level(bai.EventLevel.warning())
            .tag("chain_type", type(chain).__name__)
            .duration_ms(duration_ms)
            .custom_data("threshold_ms", threshold_ms)
            .build()

        langchain_integration.get_telemetry_client().track_event(slow_event)

    return result
```

## Best Practices

### 1. Environment-Based Configuration

```python
import os
from briefcase_ai_agent.integrations import langchain_integration

environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    langchain_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY"),
        capture_agent_thoughts=False,    # Reduce data in production
        capture_retrieval_docs=False,    # Don't capture docs in production
        max_input_length=5000,          # Limit data size
        max_output_length=5000,
        endpoint="https://observe.briefcasebrain.io/api/v1/telemetry"
    )
else:
    langchain_integration.configure(
        api_key=os.getenv("BRIEFCASE_API_KEY_DEV"),
        capture_agent_thoughts=True,     # Full tracking in dev
        capture_retrieval_docs=True,
        endpoint="https://api-dev.briefcase.ai/telemetry"
    )

langchain_integration.enable_instrumentation()
```

### 2. Selective Instrumentation

```python
from briefcase_ai_agent.integrations import langchain_integration

# Enable for specific chains only
class InstrumentedChain(LLMChain):
    def run(self, *args, **kwargs):
        langchain_integration.enable_instrumentation()
        try:
            return super().run(*args, **kwargs)
        finally:
            langchain_integration.disable_instrumentation()

# Use normal chains without instrumentation
normal_chain = LLMChain(llm=llm, prompt=prompt)

# Use instrumented chain with tracking
instrumented_chain = InstrumentedChain(llm=llm, prompt=prompt)
```

### 3. Memory Management

```python
from briefcase_ai_agent.integrations import langchain_integration

# Configure memory-conscious settings for large applications
langchain_integration.configure(
    api_key="your-briefcase-key",
    max_input_length=1000,      # Limit input size
    max_output_length=1000,     # Limit output size
    capture_retrieval_docs=False # Don't capture large documents
)
```

### 4. Error Resilience

```python
from briefcase_ai_agent.integrations import langchain_integration

try:
    langchain_integration.enable_instrumentation()
except Exception as e:
    print(f"Instrumentation failed: {e}")
    # Continue without instrumentation

# Graceful degradation
def safe_chain_run(chain, inputs):
    try:
        return chain.run(inputs)
    except Exception as e:
        # Log error but continue
        print(f"Chain execution failed: {e}")
        return None
```

## Integration Examples

### Web Application with FastAPI

```python
from fastapi import FastAPI, BackgroundTasks
from briefcase_ai_agent.integrations import langchain_integration
from langchain.chains import LLMChain
from langchain.llms import OpenAI

app = FastAPI()

@app.on_event("startup")
async def startup():
    langchain_integration.configure(api_key="your-briefcase-key")
    langchain_integration.enable_instrumentation()

@app.post("/chat")
async def chat_endpoint(message: str, background_tasks: BackgroundTasks):
    llm = OpenAI()
    chain = LLMChain(llm=llm, prompt=chat_prompt)

    # Chain execution automatically tracked
    response = chain.run(message)

    return {"response": response}

@app.on_event("shutdown")
async def shutdown():
    client = langchain_integration.get_telemetry_client()
    if client:
        client.flush()
```

### Batch Processing

```python
import asyncio
from briefcase_ai_agent.integrations import langchain_integration
from langchain.chains import LLMChain

langchain_integration.enable_instrumentation()

async def process_batch(chains_and_inputs):
    """Process multiple chains in parallel - all tracked."""
    tasks = []

    for chain, inputs in chains_and_inputs:
        task = asyncio.create_task(
            asyncio.to_thread(chain.run, inputs)
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Usage
batch_data = [
    (summarization_chain, "Long text to summarize"),
    (translation_chain, "Text to translate"),
    (qa_chain, "Question to answer")
]

results = asyncio.run(process_batch(batch_data))
```

### Custom Tools with Tracking

```python
from langchain.tools import BaseTool
from briefcase_ai_agent.integrations import langchain_integration
import briefcase_ai_telemetry as bai

class TrackedTool(BaseTool):
    name = "tracked_tool"
    description = "A tool that tracks its usage"

    def _run(self, query: str) -> str:
        # Manual tracking within tools
        start_time = time.time()

        try:
            # Tool logic here
            result = f"Processed: {query}"

            # Track successful tool use
            event = bai.EventBuilder("custom_tool_success")
                .level(bai.EventLevel.info())
                .tag("tool_name", self.name)
                .duration_ms(int((time.time() - start_time) * 1000))
                .custom_data("query", query)
                .custom_data("result_length", len(result))
                .build()

            langchain_integration.get_telemetry_client().track_event(event)
            return result

        except Exception as e:
            # Track tool errors
            error_event = bai.EventBuilder("custom_tool_error")
                .level(bai.EventLevel.error())
                .error(str(e))
                .tag("tool_name", self.name)
                .build()

            langchain_integration.get_telemetry_client().track_event(error_event)
            raise

langchain_integration.enable_instrumentation()

# Use with agents
tools = [TrackedTool()]
agent = create_react_agent(llm=OpenAI(), tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

## Troubleshooting

### Common Issues

1. **Missing chain steps**: Ensure `capture_chain_steps=True`
2. **Large memory usage**: Set `capture_retrieval_docs=False` and reduce `max_input_length`
3. **Performance impact**: Disable verbose logging and reduce tracked data

### Debug Mode

```python
import logging
from briefcase_ai_agent.integrations import langchain_integration

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("briefcase_ai_agent.integrations.langchain_integration")
logger.setLevel(logging.DEBUG)

langchain_integration.enable_instrumentation()
```

### Health Check

```python
from briefcase_ai_agent.integrations import langchain_integration

# Verify integration status
print(f"Instrumentation enabled: {langchain_integration.is_instrumentation_enabled()}")
print(f"Telemetry client: {langchain_integration.get_telemetry_client() is not None}")

# Test with simple chain
if langchain_integration.is_instrumentation_enabled():
    test_chain = LLMChain(llm=OpenAI(), prompt=PromptTemplate.from_template("Say hello"))
    result = test_chain.run({})
    print(f"Test successful: {result}")
```

This LangChain integration provides comprehensive tracking of your AI agent workflows with minimal code changes.