#!/usr/bin/env python3
"""
Telemetry Integration for Development Server

Connects the Briefcase AI telemetry SDK to the development server
for real-time monitoring and analytics.
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import aiohttp
import threading
import queue

# Add SDK path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
import briefcase_ai_telemetry as bai

class DevServerTelemetryClient:
    """Enhanced telemetry client that sends data to development server."""

    def __init__(self,
                 briefcase_api_key: str,
                 dev_server_url: str = "http://127.0.0.1:8080",
                 endpoint: str = "https://observe.briefcasebrain.io/api/v1/telemetry"):
        self.briefcase_api_key = briefcase_api_key
        self.dev_server_url = dev_server_url
        self.endpoint = endpoint

        # Create original client
        self.original_client = bai.TelemetryClient(briefcase_api_key, endpoint)

        # Queue for dev server communication
        self.event_queue = queue.Queue()
        self.running = True

        # Start background thread for dev server communication
        self.dev_thread = threading.Thread(target=self._dev_server_worker, daemon=True)
        self.dev_thread.start()

    def _dev_server_worker(self):
        """Background worker to send data to development server."""
        async def send_to_dev_server():
            async with aiohttp.ClientSession() as session:
                while self.running:
                    try:
                        # Check for events to send
                        if not self.event_queue.empty():
                            event_data = self.event_queue.get_nowait()

                            try:
                                async with session.post(
                                    f"{self.dev_server_url}/api/telemetry",
                                    json=event_data,
                                    timeout=aiohttp.ClientTimeout(total=5)
                                ) as response:
                                    if response.status == 200:
                                        print(f"📊 Sent telemetry to dev server: {event_data.get('type', 'unknown')}")
                                    else:
                                        print(f"⚠️ Dev server responded with status {response.status}")
                            except Exception as e:
                                print(f"⚠️ Failed to send to dev server: {e}")

                        await asyncio.sleep(0.1)  # Short sleep to prevent busy waiting

                    except Exception as e:
                        print(f"❌ Dev server worker error: {e}")
                        await asyncio.sleep(1)

        # Run the async function
        try:
            asyncio.run(send_to_dev_server())
        except Exception as e:
            print(f"❌ Dev server worker failed: {e}")

    def send_session_data(self, session_data: Dict[str, Any]):
        """Send session data to both Briefcase AI and dev server."""
        # Send to original Briefcase AI endpoint
        try:
            # This would normally go through the Rust core
            # For now, we'll simulate the call
            print(f"📡 Sending session data to Briefcase AI")
        except Exception as e:
            print(f"⚠️ Failed to send to Briefcase AI: {e}")

        # Send to development server
        dev_event = {
            "type": "session",
            "timestamp": datetime.now().isoformat(),
            **session_data
        }

        try:
            self.event_queue.put_nowait(dev_event)
        except queue.Full:
            print("⚠️ Dev server event queue is full")

    def send_drift_event(self, drift_data: Dict[str, Any]):
        """Send drift detection event to dev server."""
        dev_event = {
            "type": "drift_event",
            "timestamp": datetime.now().isoformat(),
            **drift_data
        }

        try:
            self.event_queue.put_nowait(dev_event)
        except queue.Full:
            print("⚠️ Dev server event queue is full")

    def close(self):
        """Close the telemetry client and stop background worker."""
        self.running = False
        if self.dev_thread.is_alive():
            self.dev_thread.join(timeout=5)

class EnhancedAgentInstrument:
    """Enhanced agent instrument that integrates with development server."""

    def __init__(self, agent_id: int, telemetry_client: DevServerTelemetryClient, config: bai.InstrumentationConfig):
        self.agent_id = agent_id
        self.telemetry_client = telemetry_client
        self.config = config

        # Create original instrument
        self.original_instrument = bai.AgentInstrument(agent_id, telemetry_client.original_client, config)

        # Session tracking
        self.session_id = f"session_{int(time.time())}_{agent_id}"
        self.start_time = None
        self.end_time = None
        self.input_text = ""
        self.output_text = ""
        self.model_name = ""
        self.metadata = {}
        self.error_message = None

    def start(self):
        """Start the agent session."""
        self.start_time = datetime.now()
        self.original_instrument.start()
        print(f"🚀 Started agent {self.agent_id} session: {self.session_id}")

    def add_input(self, input_text: str):
        """Add input text to the session."""
        self.input_text = input_text
        self.original_instrument.add_input(input_text)

    def add_output(self, output_text: str):
        """Add output text to the session."""
        self.output_text = output_text
        self.original_instrument.add_output(output_text)

    def add_metadata(self, key: str, value: Any):
        """Add metadata to the session."""
        self.metadata[key] = value
        self.original_instrument.add_metadata(key, value)

    def add_error(self, error_message: str):
        """Add error to the session."""
        self.error_message = error_message
        self.original_instrument.add_error(error_message)

    def end(self):
        """End the agent session and send telemetry."""
        self.end_time = datetime.now()
        self.original_instrument.end()

        # Calculate session metrics
        latency_seconds = (self.end_time - self.start_time).total_seconds() if self.start_time else 0.0

        # Extract cost info from metadata
        cost_info = self.metadata.get('cost_estimate', {})
        input_tokens = cost_info.get('input_tokens', 0)
        output_tokens = cost_info.get('output_tokens', 0)
        total_cost = cost_info.get('cost', 0.0)

        # Extract model info
        model_info = self.metadata.get('model_info', {})
        model_name = model_info.get('model_name', self.model_name or 'unknown')

        # Prepare session data
        session_data = {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "input_text": self.input_text,
            "output_text": self.output_text,
            "model_name": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_cost": total_cost,
            "latency_seconds": latency_seconds,
            "error_message": self.error_message,
            "metadata": self.metadata
        }

        # Send to development server
        self.telemetry_client.send_session_data(session_data)

        print(f"✅ Ended agent {self.agent_id} session: {self.session_id}")

class EnhancedDriftDetector:
    """Enhanced drift detector that sends alerts to development server."""

    def __init__(self, telemetry_client: DevServerTelemetryClient):
        self.telemetry_client = telemetry_client
        self.original_calculator = bai.DriftCalculator()

    def calculate_and_alert(self, agent_id: int, responses: list, threshold: float = 0.8) -> bai.DriftMetrics:
        """Calculate drift metrics and send alerts if needed."""
        metrics = self.original_calculator.calculate_metrics(responses)

        # Check if we should alert
        if metrics.total_agreement_rate < threshold:
            drift_data = {
                "agent_id": agent_id,
                "drift_type": "total_agreement_rate",
                "drift_score": metrics.total_agreement_rate,
                "threshold": threshold,
                "responses": responses[:5]  # Limit response size
            }

            self.telemetry_client.send_drift_event(drift_data)
            print(f"🚨 Drift alert for agent {agent_id}: TAR={metrics.total_agreement_rate:.3f}")

        return metrics

def enable_dev_server_integration(
    agent_id: int,
    briefcase_api_key: str,
    dev_server_url: str = "http://127.0.0.1:8080",
    auto_capture_inputs: bool = True,
    auto_capture_outputs: bool = True,
    auto_calculate_costs: bool = True
):
    """Enable development server integration for telemetry."""

    # Create enhanced telemetry client
    telemetry_client = DevServerTelemetryClient(briefcase_api_key, dev_server_url)

    # Create instrumentation config
    config = bai.InstrumentationConfig(
        auto_capture_inputs=auto_capture_inputs,
        auto_capture_outputs=auto_capture_outputs,
        auto_calculate_costs=auto_calculate_costs
    )

    print(f"🔭 Enabled development server integration")
    print(f"   Agent ID: {agent_id}")
    print(f"   Dev Server: {dev_server_url}")
    print(f"   Dashboard: {dev_server_url}/")

    return telemetry_client, config

# Example usage functions
def example_basic_integration():
    """Example of basic development server integration."""
    print("🔬 Basic Development Server Integration Example")
    print("=" * 50)

    # Enable integration
    telemetry_client, config = enable_dev_server_integration(
        agent_id=101,
        briefcase_api_key="your-briefcase-ai-api-key"
    )

    # Create enhanced agent instrument
    agent = EnhancedAgentInstrument(101, telemetry_client, config)

    try:
        # Simulate agent workflow
        agent.start()
        agent.add_input("What is the capital of France?")
        agent.add_metadata("model_info", {"model_name": "gpt-4", "provider": "openai"})

        # Simulate some processing time
        time.sleep(0.5)

        agent.add_output("The capital of France is Paris.")
        agent.add_metadata("cost_estimate", {
            "input_tokens": 7,
            "output_tokens": 8,
            "cost": 0.0015
        })
        agent.end()

    except Exception as e:
        agent.add_error(str(e))
        agent.end()
    finally:
        telemetry_client.close()

def example_drift_monitoring():
    """Example of drift monitoring with development server."""
    print("🔬 Drift Monitoring Example")
    print("=" * 50)

    # Enable integration
    telemetry_client, config = enable_dev_server_integration(
        agent_id=102,
        briefcase_api_key="your-briefcase-ai-api-key"
    )

    # Create drift detector
    drift_detector = EnhancedDriftDetector(telemetry_client)

    try:
        # Simulate responses with drift
        responses = [
            "The capital of France is Paris.",
            "Paris is the capital of France.",
            "London is the capital of England."  # This creates drift
        ]

        metrics = drift_detector.calculate_and_alert(102, responses, threshold=0.8)
        print(f"📊 Drift metrics: TAR={metrics.total_agreement_rate:.3f}")

    finally:
        telemetry_client.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Development server integration examples")
    parser.add_argument("--example", choices=["basic", "drift"], default="basic",
                       help="Example to run")

    args = parser.parse_args()

    if args.example == "basic":
        example_basic_integration()
    elif args.example == "drift":
        example_drift_monitoring()

    print("\n💡 Next steps:")
    print("   1. Start the development server: python dev_server/app.py")
    print("   2. Open the dashboard: http://127.0.0.1:8080")
    print("   3. Run this script to see real-time telemetry")