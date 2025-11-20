# Briefcase AI Development Server

🔭 Real-time monitoring and analytics dashboard for AI agent telemetry.

## Features

- **Real-time Dashboard**: Live monitoring of agent metrics, costs, and performance
- **Interactive Visualizations**: Charts and graphs for cost tracking and request volumes
- **Drift Detection Alerts**: Visual alerts when agent outputs show significant drift
- **Agent Performance Tracking**: Individual agent metrics and health monitoring
- **WebSocket Updates**: Real-time data streaming to the dashboard
- **SQLite Storage**: Local database for telemetry data persistence
- **REST API**: Full API for programmatic access to telemetry data

## Quick Start

### 1. Install Dependencies

```bash
cd dev_server
pip install -r requirements.txt
```

### 2. Start the Development Server

```bash
python app.py
```

The server will start at `http://127.0.0.1:8080` by default.

### 3. Open the Dashboard

Visit `http://127.0.0.1:8080` in your browser to see the live dashboard.

### 4. Integrate with Your Agents

Use the enhanced telemetry integration to send data to the development server:

```python
from dev_server.telemetry_integration import enable_dev_server_integration

# Enable integration
telemetry_client, config = enable_dev_server_integration(
    agent_id=101,
    briefcase_api_key="your-briefcase-ai-api-key",
    dev_server_url="http://127.0.0.1:8080"
)

# Use the enhanced agent instrument
from dev_server.telemetry_integration import EnhancedAgentInstrument

agent = EnhancedAgentInstrument(101, telemetry_client, config)
agent.start()
agent.add_input("Your prompt here")
# ... agent processing ...
agent.add_output("Agent response")
agent.end()
```

## Dashboard Features

### Overview Statistics
- **Total Agents**: Number of unique agents that have sent telemetry
- **24h Requests**: Total requests processed in the last 24 hours
- **24h Cost**: Total cost incurred in the last 24 hours
- **Avg Drift**: Average drift score across all agents

### Real-time Charts
- **Cost Over Time**: Line chart showing cost trends
- **Request Volume**: Bar chart showing request volume over time

### Agent List
Individual agent metrics including:
- Total requests processed
- Total cost incurred
- Average latency
- Error rate percentage
- Current drift score
- Last activity timestamp

### Live Updates
- Real-time WebSocket connection for instant updates
- Connection status indicator
- Automatic reconnection on disconnect

## API Endpoints

### Dashboard Data
- `GET /` - Main dashboard HTML page
- `GET /api/stats` - Overall dashboard statistics
- `GET /api/agents` - List all agents with metrics
- `GET /api/agents/{agent_id}` - Specific agent metrics

### Telemetry Ingestion
- `POST /api/telemetry` - Receive telemetry data from agents

### WebSocket
- `WS /ws` - Real-time updates stream

## Configuration Options

### Server Configuration

```bash
python app.py --host 0.0.0.0 --port 8080 --db telemetry.db
```

Options:
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 8080)
- `--db`: SQLite database path (default: telemetry.db)

### Environment Variables

```bash
export BRIEFCASE_DEV_SERVER_HOST=127.0.0.1
export BRIEFCASE_DEV_SERVER_PORT=8080
export BRIEFCASE_DEV_SERVER_DB=telemetry.db
```

## Database Schema

The development server uses SQLite with the following tables:

### `agent_sessions`
Stores individual agent execution sessions with metrics, costs, and performance data.

### `drift_events`
Records drift detection events with scores, thresholds, and sample responses.

### `cost_tracking`
Tracks cost data over time for analysis and optimization.

## Integration Examples

### Basic Integration

```python
from dev_server.telemetry_integration import example_basic_integration
example_basic_integration()
```

### Drift Monitoring

```python
from dev_server.telemetry_integration import example_drift_monitoring
example_drift_monitoring()
```

### Custom Integration

```python
from dev_server.telemetry_integration import DevServerTelemetryClient, EnhancedAgentInstrument
import briefcase_ai_telemetry as bai

# Create enhanced client
client = DevServerTelemetryClient(
    briefcase_api_key="your-key",
    dev_server_url="http://127.0.0.1:8080"
)

# Create config
config = bai.InstrumentationConfig(
    auto_capture_inputs=True,
    auto_capture_outputs=True,
    auto_calculate_costs=True
)

# Create and use agent
agent = EnhancedAgentInstrument(123, client, config)

try:
    agent.start()
    agent.add_input("What is machine learning?")
    agent.add_output("Machine learning is...")
    agent.add_metadata("model_info", {"model": "gpt-4"})
    agent.end()
finally:
    client.close()
```

## Framework Integrations

The development server works with all Briefcase AI framework integrations:

### OpenAI Integration

```python
from briefcase_ai_agent.integrations.openai_integration import enable_openai_integration
from dev_server.telemetry_integration import enable_dev_server_integration

# Enable both integrations
enable_openai_integration(agent_id=101, api_key="briefcase-key")
enable_dev_server_integration(agent_id=101, briefcase_api_key="briefcase-key")

# Use OpenAI normally - telemetry goes to both Briefcase AI and dev server
import openai
client = openai.OpenAI(api_key="openai-key")
response = client.chat.completions.create(...)
```

### LangChain Integration

```python
from briefcase_ai_agent.integrations.langchain_integration import enable_langchain_integration
from dev_server.telemetry_integration import enable_dev_server_integration

# Enable integrations
enable_langchain_integration(agent_id=102, api_key="briefcase-key")
enable_dev_server_integration(agent_id=102, briefcase_api_key="briefcase-key")

# Use LangChain with automatic telemetry
from langchain.llms import OpenAI
from langchain.chains import LLMChain
# ... LangChain code ...
```

## Troubleshooting

### Connection Issues

**Problem**: Dashboard shows "Disconnected" status
**Solution**:
1. Check if the development server is running
2. Verify WebSocket connection isn't blocked by firewall
3. Check browser console for WebSocket errors

**Problem**: Telemetry data not appearing
**Solution**:
1. Verify the agent is using `EnhancedAgentInstrument`
2. Check server logs for telemetry reception
3. Ensure correct dev server URL in integration

### Performance Issues

**Problem**: Dashboard loading slowly
**Solution**:
1. Check database size and consider archiving old data
2. Reduce WebSocket update frequency
3. Limit number of agents being monitored

### Database Issues

**Problem**: SQLite database locked
**Solution**:
1. Ensure no other processes are accessing the database
2. Check file permissions
3. Restart the development server

## Advanced Usage

### Custom Dashboard Extensions

The dashboard can be extended with custom visualizations by modifying `static/dashboard.js`.

### API Integration

Access telemetry data programmatically:

```python
import aiohttp
import asyncio

async def get_agent_stats():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8080/api/stats') as response:
            return await response.json()

stats = asyncio.run(get_agent_stats())
print(f"Total cost: ${stats['total_cost_24h']}")
```

### Data Export

Export telemetry data for analysis:

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('telemetry.db')

# Query sessions
df = pd.read_sql_query('''
    SELECT agent_id, model_name, total_cost, latency_seconds, start_time
    FROM agent_sessions
    WHERE start_time > datetime('now', '-7 days')
''', conn)

# Analyze data
print(df.groupby('model_name')['total_cost'].sum())
```

## Production Considerations

⚠️ **Note**: This development server is designed for local development and testing. For production monitoring, use the main Briefcase AI platform.

### Security
- The server runs on localhost by default
- No authentication is implemented
- Use only in trusted development environments

### Scalability
- SQLite is suitable for development workloads
- For high-volume testing, consider database optimization
- Monitor disk usage for long-running servers

### Integration
- Telemetry is sent to both Briefcase AI and the dev server
- The dev server provides immediate local feedback
- Production telemetry should use the main Briefcase AI platform

## Support

For issues with the development server:
1. Check the server logs for error messages
2. Verify all dependencies are installed correctly
3. Test with the provided examples
4. Report issues in the main repository

## Next Steps

1. **Start Monitoring**: Run the server and integrate with your agents
2. **Customize Dashboard**: Modify the frontend for your specific needs
3. **Analyze Data**: Use the API to build custom analytics
4. **Production Setup**: Move to the full Briefcase AI platform for production monitoring