# Briefcase AI Telemetry CLI

🔭 Developer tools for AI agent observability, monitoring, and configuration.

## Installation

```bash
pip install briefcase-ai-cli
```

Or install from source:

```bash
cd cli
pip install -e .
```

## Quick Start

### 1. Initialize a New Project

```bash
briefcase-ai init --framework openai --api-key your-api-key
```

This creates:
- Configuration file (`briefcase-ai.yaml`)
- Example integration code
- Development environment setup

### 2. Monitor in Real-Time

```bash
briefcase-ai monitor
```

Live dashboard showing:
- Active agents and request counts
- Latency, costs, and error rates
- Drift detection scores
- Performance trends

### 3. Analyze Performance

```bash
# Drift analysis
briefcase-ai analyze drift --input outputs.csv --threshold 0.8

# Cost analysis
briefcase-ai analyze cost --timeframe 7d --breakdown

# Performance analysis
briefcase-ai analyze performance --metric latency
```

### 4. Manage Configuration

```bash
# Show current config
briefcase-ai config show

# Set values
briefcase-ai config set briefcase_ai.api_key your-new-key

# Configure frameworks
briefcase-ai config framework --framework langchain

# Validate settings
briefcase-ai config validate
```

## Commands

### `briefcase-ai init`
Initialize a new telemetry project with configuration and examples.

**Options:**
- `--framework` - Primary AI framework (openai, langchain, anthropic)
- `--api-key` - Briefcase AI API key
- `--agent-id` - Default agent ID
- `--examples` - Generate example code (default: true)

**Example:**
```bash
briefcase-ai init --framework langchain --api-key sk-xxx --agent-id 123
```

### `briefcase-ai monitor`
Real-time telemetry monitoring dashboard.

**Options:**
- `--refresh` - Refresh interval in seconds (default: 5.0)
- `--config` - Configuration file path
- `--agent-id` - Monitor specific agent only
- `--simple` - Minimal output mode

**Example:**
```bash
briefcase-ai monitor --refresh 2 --agent-id 123
```

### `briefcase-ai analyze`

#### `analyze drift`
Analyze drift in agent outputs.

**Options:**
- `--input` - Input file (CSV/JSON)
- `--threshold` - Drift threshold (0.0-1.0)
- `--algorithm` - Algorithm (tar, edit_distance, semantic, all)
- `--output` - Save results to file

**Example:**
```bash
briefcase-ai analyze drift --input responses.csv --threshold 0.85 --output drift-report.json
```

#### `analyze cost`
Analyze costs and optimization opportunities.

**Options:**
- `--model` - Specific model to analyze
- `--timeframe` - Analysis period (24h, 7d, 30d)
- `--breakdown` - Detailed cost breakdown
- `--output` - Save analysis to file

**Example:**
```bash
briefcase-ai analyze cost --timeframe 7d --breakdown --output cost-analysis.json
```

#### `analyze performance`
Analyze latency, accuracy, and error metrics.

**Options:**
- `--agent-id` - Specific agent to analyze
- `--metric` - Primary metric (latency, accuracy, cost, errors)
- `--timeframe` - Analysis period
- `--output` - Save results to file

**Example:**
```bash
briefcase-ai analyze performance --metric latency --timeframe 24h
```

### `briefcase-ai config`

#### `config show`
Display current configuration.

**Options:**
- `--file` - Configuration file path
- `--format` - Output format (yaml, json, env)

#### `config set/get`
Set or get configuration values.

**Examples:**
```bash
briefcase-ai config set briefcase_ai.api_key sk-new-key
briefcase-ai config get instrumentation.auto_capture_inputs
```

#### `config framework`
Configure framework-specific settings.

**Example:**
```bash
briefcase-ai config framework --framework openai
```

#### `config validate`
Validate configuration and test connectivity.

## Configuration

Configuration is stored in `briefcase-ai.yaml` (or `.json`):

```yaml
briefcase_ai:
  api_key: "your-api-key"
  agent_id: 1
  enabled: true
  endpoint: "https://telemetry.briefcasebrain.com/api"

instrumentation:
  auto_capture_inputs: true
  auto_capture_outputs: true
  auto_calculate_costs: true
  max_input_length: 10000
  max_output_length: 10000
  consensus_mode:
    enabled: false
    runs: 3
    threshold: 0.8
  drift_detection:
    enabled: true
    algorithms: ["total_agreement_rate", "normalized_edit_distance"]
    alert_threshold: 0.7

frameworks:
  openai:
    enabled: true
    capture_function_calls: true
    capture_system_messages: false
  langchain:
    enabled: true
    capture_chain_steps: true
    capture_tool_usage: true
    capture_agent_thoughts: true
    capture_retrieval_docs: false
```

## Examples

### Basic Monitoring Workflow

```bash
# 1. Initialize project
briefcase-ai init --framework openai

# 2. Validate configuration
briefcase-ai config validate

# 3. Start monitoring
briefcase-ai monitor --refresh 3

# 4. Analyze results (in another terminal)
briefcase-ai analyze drift --threshold 0.8
briefcase-ai analyze cost --timeframe 24h --breakdown
```

### Drift Detection Pipeline

```bash
# Collect outputs to CSV file, then analyze
briefcase-ai analyze drift \
  --input agent_outputs.csv \
  --threshold 0.85 \
  --algorithm all \
  --output drift_analysis.json

# Review recommendations
cat drift_analysis.json | jq '.recommendations'
```

### Cost Optimization

```bash
# Get detailed cost breakdown
briefcase-ai analyze cost --timeframe 30d --breakdown

# Monitor specific expensive model
briefcase-ai monitor --simple | grep gpt-4
```

## Integration Examples

The CLI generates framework-specific examples:

- `examples/basic_example.py` - Basic telemetry usage
- `examples/openai_example.py` - OpenAI integration
- `examples/langchain_example.py` - LangChain integration
- `examples/advanced_example.py` - Advanced features

## Development

```bash
# Install in development mode
cd cli
pip install -e .

# Run tests
pytest tests/

# Format code
black briefcase_ai_cli/
isort briefcase_ai_cli/
```

## Documentation

- [Briefcase AI Documentation](https://docs.briefcasebrain.com)
- [SDK Reference](https://docs.briefcasebrain.com/sdk)
- [Integration Guides](https://docs.briefcasebrain.com/integrations)
- [API Reference](https://docs.briefcasebrain.com/api)

## Support

- GitHub Issues: [Report bugs](https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues)
- Documentation: [docs.briefcasebrain.com](https://docs.briefcasebrain.com)
- Community: [Discord](https://discord.gg/briefcase-ai)