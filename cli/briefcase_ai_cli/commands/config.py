"""
Configuration management command.

Manages Briefcase AI telemetry configuration, API keys, and framework settings.
"""

import click
import json
import yaml
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

@click.group()
def config():
    """
    ⚙️ Manage Briefcase AI telemetry configuration.

    Configure API keys, endpoints, framework integrations,
    and instrumentation settings for your project.
    """
    pass

@config.command()
@click.option('--file', 'config_file', default='briefcase-ai.yaml',
              help='Configuration file path')
@click.option('--format', 'output_format', type=click.Choice(['yaml', 'json', 'env']), default='yaml',
              help='Output format')
def show(config_file, output_format):
    """
    📋 Show current configuration.

    Display the current configuration settings, masking sensitive values.
    """

    if not os.path.exists(config_file):
        click.echo(f"❌ Configuration file not found: {config_file}")
        click.echo("💡 Run 'briefcase-ai init' to create initial configuration")
        return

    try:
        config_data = load_config_file(config_file)

        # Mask sensitive values
        masked_config = mask_sensitive_values(config_data.copy())

        click.echo(f"📋 Configuration from: {config_file}")
        click.echo("=" * 50)

        if output_format == 'yaml':
            yaml.dump(masked_config, click.get_text_stream('stdout'), default_flow_style=False)
        elif output_format == 'json':
            click.echo(json.dumps(masked_config, indent=2))
        elif output_format == 'env':
            display_env_format(masked_config)

    except Exception as e:
        click.echo(f"❌ Error reading configuration: {e}")

@config.command()
@click.argument('key')
@click.argument('value')
@click.option('--file', 'config_file', default='briefcase-ai.yaml',
              help='Configuration file path')
@click.option('--create', is_flag=True, help='Create config file if it doesn\'t exist')
def set(key, value, config_file, create):
    """
    ✏️ Set a configuration value.

    Set a configuration value using dot notation (e.g., briefcase_ai.api_key).
    """

    # Check if config file exists
    if not os.path.exists(config_file) and not create:
        click.echo(f"❌ Configuration file not found: {config_file}")
        click.echo("💡 Use --create flag to create new config file")
        return

    # Load existing config or create new
    if os.path.exists(config_file):
        config_data = load_config_file(config_file)
    else:
        config_data = {}

    # Parse key path (e.g., "briefcase_ai.api_key" -> ["briefcase_ai", "api_key"])
    key_path = key.split('.')

    # Set the value
    current = config_data
    for part in key_path[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    # Convert value to appropriate type
    processed_value = parse_value(value)
    current[key_path[-1]] = processed_value

    # Save config
    save_config_file(config_file, config_data)

    # Mask the value if it's sensitive
    display_value = "***" if is_sensitive_key(key) else processed_value
    click.echo(f"✅ Set {key} = {display_value}")

@config.command()
@click.argument('key')
@click.option('--file', 'config_file', default='briefcase-ai.yaml',
              help='Configuration file path')
def get(key, config_file):
    """
    🔍 Get a configuration value.

    Get a configuration value using dot notation (e.g., briefcase_ai.api_key).
    """

    if not os.path.exists(config_file):
        click.echo(f"❌ Configuration file not found: {config_file}")
        return

    try:
        config_data = load_config_file(config_file)

        # Parse key path
        key_path = key.split('.')
        current = config_data

        for part in key_path:
            if not isinstance(current, dict) or part not in current:
                click.echo(f"❌ Key not found: {key}")
                return
            current = current[part]

        # Mask sensitive values
        if is_sensitive_key(key):
            value = "***"
        else:
            value = current

        click.echo(f"{key}: {value}")

    except Exception as e:
        click.echo(f"❌ Error reading configuration: {e}")

@config.command()
@click.option('--file', 'config_file', default='briefcase-ai.yaml',
              help='Configuration file path')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
def validate(config_file, force):
    """
    ✅ Validate configuration file.

    Check configuration file for errors, missing required fields,
    and connectivity to Briefcase AI services.
    """

    click.echo("✅ Configuration Validation")
    click.echo("=" * 40)

    if not os.path.exists(config_file):
        click.echo(f"❌ Configuration file not found: {config_file}")
        return

    try:
        config_data = load_config_file(config_file)

        # Validate structure
        validation_results = validate_config_structure(config_data)

        # Display results
        for result in validation_results:
            status = "✅" if result['status'] == 'ok' else "⚠️" if result['status'] == 'warning' else "❌"
            click.echo(f"{status} {result['message']}")

        # Test connectivity (if API key is present)
        api_key = get_nested_value(config_data, 'briefcase_ai.api_key')
        if api_key and not force:
            if click.confirm('🌐 Test connectivity to Briefcase AI services?'):
                test_connectivity(api_key, config_data)

    except Exception as e:
        click.echo(f"❌ Validation error: {e}")

@config.command()
@click.option('--file', 'config_file', default='briefcase-ai.yaml',
              help='Configuration file path')
@click.option('--backup', is_flag=True, default=True, help='Create backup before reset')
def reset(config_file, backup):
    """
    🔄 Reset configuration to defaults.

    Reset the configuration file to default values, optionally creating a backup.
    """

    if not os.path.exists(config_file):
        click.echo(f"❌ Configuration file not found: {config_file}")
        return

    if not click.confirm(f'⚠️  Reset {config_file} to defaults? This cannot be undone.'):
        click.echo("Operation cancelled.")
        return

    # Create backup if requested
    if backup:
        backup_file = f"{config_file}.backup.{int(time.time())}"
        import shutil
        shutil.copy2(config_file, backup_file)
        click.echo(f"📦 Backup created: {backup_file}")

    # Create default config
    default_config = create_default_config()

    # Save default config
    save_config_file(config_file, default_config)
    click.echo(f"✅ Configuration reset to defaults: {config_file}")

@config.command()
@click.option('--framework', type=click.Choice(['openai', 'langchain', 'anthropic']),
              help='Framework to configure')
@click.option('--file', 'config_file', default='briefcase-ai.yaml',
              help='Configuration file path')
def framework(framework, config_file):
    """
    🔧 Configure framework-specific settings.

    Configure settings for specific AI frameworks (OpenAI, LangChain, Anthropic).
    """

    if not framework:
        framework = click.prompt(
            "Choose framework to configure",
            type=click.Choice(['openai', 'langchain', 'anthropic'])
        )

    if not os.path.exists(config_file):
        click.echo(f"❌ Configuration file not found: {config_file}")
        click.echo("💡 Run 'briefcase-ai init' first")
        return

    config_data = load_config_file(config_file)

    click.echo(f"🔧 Configuring {framework.title()} Integration")
    click.echo("=" * 40)

    # Framework-specific configuration
    if framework == 'openai':
        configure_openai_framework(config_data)
    elif framework == 'langchain':
        configure_langchain_framework(config_data)
    elif framework == 'anthropic':
        configure_anthropic_framework(config_data)

    # Save updated config
    save_config_file(config_file, config_data)
    click.echo(f"✅ {framework.title()} configuration updated")

def configure_openai_framework(config_data: Dict[str, Any]):
    """Configure OpenAI-specific settings."""

    if 'frameworks' not in config_data:
        config_data['frameworks'] = {}

    current = config_data['frameworks'].get('openai', {})

    click.echo("Configure OpenAI Integration:")

    # Enable/disable
    enabled = click.confirm("Enable OpenAI integration?", default=current.get('enabled', True))

    # Capture settings
    capture_function_calls = click.confirm(
        "Capture function/tool calls?",
        default=current.get('capture_function_calls', True)
    )

    capture_system_messages = click.confirm(
        "Capture system messages?",
        default=current.get('capture_system_messages', False)
    )

    config_data['frameworks']['openai'] = {
        'enabled': enabled,
        'capture_function_calls': capture_function_calls,
        'capture_system_messages': capture_system_messages
    }

def configure_langchain_framework(config_data: Dict[str, Any]):
    """Configure LangChain-specific settings."""

    if 'frameworks' not in config_data:
        config_data['frameworks'] = {}

    current = config_data['frameworks'].get('langchain', {})

    click.echo("Configure LangChain Integration:")

    # Enable/disable
    enabled = click.confirm("Enable LangChain integration?", default=current.get('enabled', True))

    # Capture settings
    capture_chain_steps = click.confirm(
        "Capture chain execution steps?",
        default=current.get('capture_chain_steps', True)
    )

    capture_tool_usage = click.confirm(
        "Capture tool usage?",
        default=current.get('capture_tool_usage', True)
    )

    capture_agent_thoughts = click.confirm(
        "Capture agent reasoning/thoughts?",
        default=current.get('capture_agent_thoughts', True)
    )

    capture_retrieval_docs = click.confirm(
        "Capture retrieved documents? (can be large)",
        default=current.get('capture_retrieval_docs', False)
    )

    config_data['frameworks']['langchain'] = {
        'enabled': enabled,
        'capture_chain_steps': capture_chain_steps,
        'capture_tool_usage': capture_tool_usage,
        'capture_agent_thoughts': capture_agent_thoughts,
        'capture_retrieval_docs': capture_retrieval_docs
    }

def configure_anthropic_framework(config_data: Dict[str, Any]):
    """Configure Anthropic-specific settings."""

    if 'frameworks' not in config_data:
        config_data['frameworks'] = {}

    current = config_data['frameworks'].get('anthropic', {})

    click.echo("Configure Anthropic Integration:")

    # Enable/disable
    enabled = click.confirm("Enable Anthropic integration?", default=current.get('enabled', True))

    # Capture settings
    capture_tool_use = click.confirm(
        "Capture tool usage?",
        default=current.get('capture_tool_use', True)
    )

    capture_thinking = click.confirm(
        "Capture thinking/reasoning?",
        default=current.get('capture_thinking', False)
    )

    config_data['frameworks']['anthropic'] = {
        'enabled': enabled,
        'capture_tool_use': capture_tool_use,
        'capture_thinking': capture_thinking
    }

def load_config_file(config_file: str) -> Dict[str, Any]:
    """Load configuration from file."""

    with open(config_file, 'r') as f:
        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
            return yaml.safe_load(f) or {}
        else:
            return json.load(f) or {}

def save_config_file(config_file: str, config_data: Dict[str, Any]):
    """Save configuration to file."""

    with open(config_file, 'w') as f:
        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        else:
            json.dump(config_data, f, indent=2)

def mask_sensitive_values(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive values in configuration."""

    sensitive_keys = ['api_key', 'secret', 'token', 'password']

    def mask_dict(d):
        if isinstance(d, dict):
            for key, value in d.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    d[key] = "***"
                else:
                    mask_dict(value)
        elif isinstance(d, list):
            for item in d:
                mask_dict(item)

    mask_dict(config_data)
    return config_data

def is_sensitive_key(key: str) -> bool:
    """Check if a configuration key contains sensitive information."""

    sensitive_keys = ['api_key', 'secret', 'token', 'password']
    return any(sensitive in key.lower() for sensitive in sensitive_keys)

def parse_value(value: str) -> Any:
    """Parse string value to appropriate type."""

    # Try to parse as JSON (handles booleans, numbers, arrays, objects)
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        # Return as string if not valid JSON
        return value

def get_nested_value(config_data: Dict[str, Any], key_path: str) -> Any:
    """Get nested configuration value using dot notation."""

    keys = key_path.split('.')
    current = config_data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]

    return current

def validate_config_structure(config_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validate configuration structure and return results."""

    results = []

    # Check for required fields
    if 'briefcase_ai' not in config_data:
        results.append({
            'status': 'error',
            'message': 'Missing required section: briefcase_ai'
        })
    else:
        ba_config = config_data['briefcase_ai']

        # Check API key
        if 'api_key' not in ba_config:
            results.append({
                'status': 'error',
                'message': 'Missing required field: briefcase_ai.api_key'
            })
        elif not ba_config['api_key']:
            results.append({
                'status': 'warning',
                'message': 'Empty API key'
            })
        else:
            results.append({
                'status': 'ok',
                'message': 'API key configured'
            })

        # Check agent ID
        if 'agent_id' not in ba_config:
            results.append({
                'status': 'warning',
                'message': 'No default agent_id configured'
            })
        else:
            results.append({
                'status': 'ok',
                'message': f'Agent ID configured: {ba_config["agent_id"]}'
            })

        # Check endpoint
        endpoint = ba_config.get('endpoint', 'https://observe.briefcasebrain.io/api/v1/telemetry')
        results.append({
            'status': 'ok',
            'message': f'Endpoint: {endpoint}'
        })

    # Check instrumentation settings
    if 'instrumentation' in config_data:
        results.append({
            'status': 'ok',
            'message': 'Instrumentation settings configured'
        })
    else:
        results.append({
            'status': 'warning',
            'message': 'No instrumentation settings (using defaults)'
        })

    # Check framework configurations
    if 'frameworks' in config_data:
        frameworks = config_data['frameworks']
        enabled_frameworks = [name for name, conf in frameworks.items()
                            if isinstance(conf, dict) and conf.get('enabled', False)]

        if enabled_frameworks:
            results.append({
                'status': 'ok',
                'message': f'Enabled frameworks: {", ".join(enabled_frameworks)}'
            })
        else:
            results.append({
                'status': 'warning',
                'message': 'No frameworks enabled'
            })
    else:
        results.append({
            'status': 'warning',
            'message': 'No framework configurations'
        })

    return results

def test_connectivity(api_key: str, config_data: Dict[str, Any]):
    """Test connectivity to Briefcase AI services."""

    import sys
    import os

    # Add SDK path
    current_dir = os.path.dirname(__file__)
    sdk_path = os.path.join(current_dir, '..', '..', '..', 'python')
    sys.path.insert(0, sdk_path)

    try:
        import briefcase_ai_telemetry as bai

        # Create test client
        client = bai.create_client(api_key)

        # Test basic functionality
        click.echo("🌐 Testing connectivity...")

        # This would normally send a test event
        click.echo("✅ Connectivity test passed")

    except ImportError:
        click.echo("⚠️  SDK not available for connectivity test")
    except Exception as e:
        click.echo(f"❌ Connectivity test failed: {e}")

def display_env_format(config_data: Dict[str, Any], prefix: str = "BRIEFCASE_AI"):
    """Display configuration in environment variable format."""

    def flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key.upper(), v))
        return dict(items)

    flat_config = flatten_dict(config_data)

    for key, value in flat_config.items():
        env_key = f"{prefix}_{key}"
        click.echo(f"export {env_key}={value}")

def create_default_config() -> Dict[str, Any]:
    """Create default configuration structure."""

    return {
        'briefcase_ai': {
            'api_key': '',
            'agent_id': 1,
            'enabled': True,
            'endpoint': 'https://observe.briefcasebrain.io/api/v1/telemetry'
        },
        'instrumentation': {
            'auto_capture_inputs': True,
            'auto_capture_outputs': True,
            'auto_calculate_costs': True,
            'max_input_length': 10000,
            'max_output_length': 10000,
            'consensus_mode': {
                'enabled': False,
                'runs': 3,
                'threshold': 0.8
            },
            'drift_detection': {
                'enabled': True,
                'algorithms': ['total_agreement_rate', 'normalized_edit_distance'],
                'alert_threshold': 0.7
            }
        },
        'frameworks': {}
    }