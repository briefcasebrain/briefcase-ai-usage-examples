"""
Project initialization command.

Creates configuration files, example integrations, and sets up the development environment.
"""

import click
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any

@click.command()
@click.option('--framework', type=click.Choice(['openai', 'langchain', 'anthropic', 'huggingface', 'custom']),
              help='Primary AI framework to configure')
@click.option('--api-key', help='Briefcase AI API key')
@click.option('--endpoint', help='Custom telemetry endpoint (optional)')
@click.option('--agent-id', type=int, help='Default agent ID')
@click.option('--config-format', type=click.Choice(['yaml', 'json']), default='yaml',
              help='Configuration file format')
@click.option('--examples', is_flag=True, default=True, help='Generate example code')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
def init(framework, api_key, endpoint, agent_id, config_format, examples, force):
    """
    🚀 Initialize a new Briefcase AI telemetry project.

    Sets up configuration files, integration examples, and development environment
    for AI agent observability and monitoring.
    """

    current_dir = Path.cwd()
    config_file = current_dir / f"briefcase-ai.{config_format}"

    # Check if config already exists
    if config_file.exists() and not force:
        click.echo(f"❌ Configuration file {config_file.name} already exists. Use --force to overwrite.")
        return

    click.echo("🔭 Briefcase AI Telemetry Project Initialization")
    click.echo("=" * 50)

    # Collect configuration interactively if not provided
    if not api_key:
        api_key = click.prompt("📋 Enter your Briefcase AI API key", hide_input=True)

    if not agent_id:
        agent_id = click.prompt("🤖 Enter default agent ID", type=int, default=1)

    if not framework:
        framework = click.prompt(
            "🔧 Choose your primary AI framework",
            type=click.Choice(['openai', 'langchain', 'anthropic', 'huggingface', 'custom']),
            default='openai'
        )

    # Create configuration
    config = create_config(api_key, endpoint, agent_id, framework)

    # Write configuration file
    write_config(config_file, config, config_format)
    click.echo(f"✅ Created configuration file: {config_file.name}")

    # Create examples if requested
    if examples:
        create_examples(current_dir, framework, agent_id, api_key)
        click.echo("✅ Generated example code")

    # Create .gitignore entries
    create_gitignore_entries(current_dir)
    click.echo("✅ Updated .gitignore")

    # Success message
    click.echo("\n" + "=" * 50)
    click.echo("🎉 Project initialized successfully!")
    click.echo(f"📁 Configuration: {config_file.name}")
    click.echo(f"🔧 Framework: {framework}")
    click.echo(f"🤖 Agent ID: {agent_id}")

    if examples:
        click.echo(f"📂 Examples: examples/")

    click.echo("\n💡 Next steps:")
    click.echo("   1. Review and customize your configuration")
    click.echo("   2. Run 'briefcase-ai monitor' to start monitoring")
    click.echo("   3. Check out the examples/ directory for integration guides")

def create_config(api_key: str, endpoint: str, agent_id: int, framework: str) -> Dict[str, Any]:
    """Create the base configuration dictionary."""

    config = {
        "briefcase_ai": {
            "api_key": api_key,
            "agent_id": agent_id,
            "enabled": True,
            "auto_submit": True,
            "endpoint": endpoint or "https://observe.briefcasebrain.io/api/v1/telemetry"
        },
        "instrumentation": {
            "auto_capture_inputs": True,
            "auto_capture_outputs": True,
            "auto_calculate_costs": True,
            "max_input_length": 10000,
            "max_output_length": 10000,
            "consensus_mode": {
                "enabled": False,
                "runs": 3,
                "threshold": 0.8
            },
            "drift_detection": {
                "enabled": True,
                "algorithms": ["total_agreement_rate", "normalized_edit_distance"],
                "alert_threshold": 0.7
            }
        },
        "frameworks": {}
    }

    # Add framework-specific configuration
    if framework == "openai":
        config["frameworks"]["openai"] = {
            "enabled": True,
            "capture_function_calls": True,
            "capture_system_messages": False
        }
    elif framework == "langchain":
        config["frameworks"]["langchain"] = {
            "enabled": True,
            "capture_chain_steps": True,
            "capture_tool_usage": True,
            "capture_agent_thoughts": True,
            "capture_retrieval_docs": False
        }
    elif framework == "anthropic":
        config["frameworks"]["anthropic"] = {
            "enabled": True,
            "capture_tool_use": True,
            "capture_thinking": False
        }

    return config

def write_config(config_file: Path, config: Dict[str, Any], format_type: str):
    """Write configuration to file."""

    with open(config_file, 'w') as f:
        if format_type == 'yaml':
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        else:
            json.dump(config, f, indent=2)

def create_examples(project_dir: Path, framework: str, agent_id: int, api_key: str):
    """Create example integration files."""

    examples_dir = project_dir / "examples"
    examples_dir.mkdir(exist_ok=True)

    # Create README
    readme_content = f"""# Briefcase AI Telemetry Examples

This directory contains examples for integrating Briefcase AI telemetry with {framework}.

## Files

- `basic_example.py` - Basic telemetry usage
- `{framework}_example.py` - {framework.title()}-specific integration
- `advanced_example.py` - Advanced features (consensus mode, drift detection)

## Usage

1. Ensure you have the Briefcase AI SDK installed:
   ```bash
   pip install briefcase-ai-telemetry-sdk
   ```

2. Update your API key in the configuration if needed

3. Run any example:
   ```bash
   python examples/basic_example.py
   ```

## Documentation

Visit https://docs.briefcasebrain.com for comprehensive guides and API documentation.
"""

    with open(examples_dir / "README.md", 'w') as f:
        f.write(readme_content)

    # Create basic example
    basic_example = f'''#!/usr/bin/env python3
"""
Basic Briefcase AI telemetry example.
"""

import briefcase_ai_telemetry as bai

def main():
    # Create telemetry client
    client = bai.create_client("{api_key}")

    # Create agent instrument
    config = bai.InstrumentationConfig()
    config.with_auto_submit(True)

    agent = bai.create_agent_instrument({agent_id}, client, config)

    # Track agent execution
    agent.start()
    agent.set_input("What is the capital of France?")
    agent.set_model_info("gpt-4", 0.7)
    agent.set_output("The capital of France is Paris.")
    agent.set_token_usage(15, 8)
    agent.finish()

    print("✅ Telemetry sent successfully!")

if __name__ == "__main__":
    main()
'''

    with open(examples_dir / "basic_example.py", 'w') as f:
        f.write(basic_example)

    # Create framework-specific example
    if framework == "openai":
        openai_example = f'''#!/usr/bin/env python3
"""
OpenAI integration with Briefcase AI telemetry.
"""

import openai
from briefcase_ai_agent.integrations.openai_integration import enable_openai_integration

def main():
    # Enable automatic OpenAI instrumentation
    enable_openai_integration(
        agent_id={agent_id},
        api_key="{api_key}"
    )

    # Set your OpenAI API key
    openai.api_key = "your-openai-api-key"

    # Use OpenAI normally - telemetry is captured automatically
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {{"role": "user", "content": "What is the capital of France?"}}
        ]
    )

    print("Response:", response.choices[0].message.content)
    print("✅ Telemetry captured automatically!")

if __name__ == "__main__":
    main()
'''

        with open(examples_dir / f"{framework}_example.py", 'w') as f:
            f.write(openai_example)

    elif framework == "langchain":
        langchain_example = f'''#!/usr/bin/env python3
"""
LangChain integration with Briefcase AI telemetry.
"""

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from briefcase_ai_agent.integrations.langchain_integration import enable_langchain_integration

def main():
    # Enable automatic LangChain instrumentation
    enable_langchain_integration(
        agent_id={agent_id},
        api_key="{api_key}"
    )

    # Create LangChain components
    llm = OpenAI(temperature=0.7)

    prompt = PromptTemplate(
        input_variables=["topic"],
        template="Tell me a fascinating fact about {{topic}}."
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    # Use LangChain normally - telemetry is captured automatically
    result = chain.run(topic="artificial intelligence")

    print("Result:", result)
    print("✅ Telemetry captured automatically!")

if __name__ == "__main__":
    main()
'''

        with open(examples_dir / f"{framework}_example.py", 'w') as f:
            f.write(langchain_example)

    elif framework == "huggingface":
        huggingface_example = f'''#!/usr/bin/env python3
"""
Hugging Face integration with Briefcase AI telemetry.
"""

from transformers import pipeline
from briefcase_ai_agent.integrations.huggingface_integration import enable_huggingface_integration

def main():
    # Enable automatic Hugging Face instrumentation
    enable_huggingface_integration(
        agent_id={agent_id},
        api_key="{api_key}"
    )

    # Create a text generation pipeline
    generator = pipeline("text-generation", model="distilgpt2")

    # Use Hugging Face normally - telemetry is captured automatically
    prompt = "The future of AI is"
    result = generator(prompt, max_length=50, num_return_sequences=1)

    print("Generated text:", result[0]['generated_text'])
    print("✅ Telemetry captured automatically!")

    # Try text classification
    classifier = pipeline("sentiment-analysis")
    sentiment_result = classifier("I love this integration!")

    print("Sentiment:", sentiment_result[0]['label'])
    print("Confidence:", sentiment_result[0]['score'])

if __name__ == "__main__":
    main()
'''

        with open(examples_dir / f"{framework}_example.py", 'w') as f:
            f.write(huggingface_example)

    # Create advanced example
    advanced_example = f'''#!/usr/bin/env python3
"""
Advanced Briefcase AI telemetry features example.
"""

import briefcase_ai_telemetry as bai

def main():
    print("🔬 Advanced Telemetry Features Demo")
    print("=" * 40)

    # 1. Drift Detection
    print("\\n1. Drift Detection Analysis")
    outputs = [
        "The capital of France is Paris.",
        "Paris is the capital of France.",
        "The capital city of France is Paris.",
        "London is the capital of England."  # This will show drift
    ]

    metrics = bai.calculate_drift(outputs)
    print(f"   Total Agreement Rate: {{metrics.total_agreement_rate:.3f}}")
    print(f"   Consistency Score: {{metrics.consistency_score:.3f}}")

    # 2. Cost Estimation
    print("\\n2. Cost Estimation")
    cost = bai.estimate_cost(
        "gpt-4",
        "What is the capital of France?",
        "The capital of France is Paris."
    )
    if cost:
        print(f"   Estimated cost: ${{cost.total_cost:.6f}}")
        print(f"   Input tokens: {{cost.input_tokens}}")
        print(f"   Output tokens: {{cost.output_tokens}}")

    # 3. Consensus Mode Simulation
    print("\\n3. Consensus Mode Configuration")
    config = bai.InstrumentationConfig()
    config.with_consensus_mode(enabled=True, runs=3, threshold=0.8)
    config.with_auto_submit(True)

    print(f"   Consensus runs: 3")
    print(f"   Agreement threshold: 0.8")
    print(f"   Configuration ready for production use")

    print("\\n✅ Advanced features demo completed!")

if __name__ == "__main__":
    main()
'''

    with open(examples_dir / "advanced_example.py", 'w') as f:
        f.write(advanced_example)

def create_gitignore_entries(project_dir: Path):
    """Add Briefcase AI specific entries to .gitignore."""

    gitignore_file = project_dir / ".gitignore"

    entries = [
        "# Briefcase AI Telemetry",
        "briefcase-ai.yaml",
        "briefcase-ai.json",
        ".briefcase-ai/",
        "*.briefcase-ai.log",
    ]

    existing_content = ""
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            existing_content = f.read()

    # Only add entries that don't already exist
    new_entries = []
    for entry in entries:
        if entry not in existing_content:
            new_entries.append(entry)

    if new_entries:
        with open(gitignore_file, 'a') as f:
            f.write("\n" + "\n".join(new_entries) + "\n")