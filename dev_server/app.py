#!/usr/bin/env python3
"""
Briefcase AI Development Server with Web Dashboard

Real-time monitoring and analytics dashboard for AI agent telemetry.
Provides interactive visualizations for costs, drift, performance, and errors.
"""

import asyncio
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import sqlite3
import threading
from dataclasses import dataclass, asdict

# FastAPI and web components
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from pydantic import BaseModel

# Add SDK path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
import briefcase_ai_telemetry as bai

# Data models for API
class AgentMetricsResponse(BaseModel):
    agent_id: int
    total_requests: int
    total_cost: float
    avg_latency: float
    error_rate: float
    last_activity: datetime
    drift_score: Optional[float] = None

class DashboardStats(BaseModel):
    total_agents: int
    active_agents: int
    total_requests_24h: int
    total_cost_24h: float
    avg_drift_score: float
    error_count_24h: int

class TelemetryEvent(BaseModel):
    timestamp: datetime
    agent_id: int
    event_type: str  # start, end, error, drift_alert
    data: Dict[str, Any]

@dataclass
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    active_connections: List[WebSocket]

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)

class TelemetryDatabase:
    """SQLite database for storing telemetry data."""

    def __init__(self, db_path: str = "telemetry.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                input_text TEXT,
                output_text TEXT,
                model_name TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                latency_seconds REAL DEFAULT 0.0,
                error_message TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drift_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                drift_type TEXT NOT NULL,
                drift_score REAL NOT NULL,
                threshold REAL NOT NULL,
                responses JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                model_name TEXT NOT NULL,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_id ON agent_sessions(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON agent_sessions(start_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_drift_agent ON drift_events(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cost_agent ON cost_tracking(agent_id)')

        conn.commit()
        conn.close()

    def record_session(self, session_data: Dict[str, Any]):
        """Record an agent session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO agent_sessions
            (agent_id, session_id, start_time, end_time, input_text, output_text,
             model_name, input_tokens, output_tokens, total_cost, latency_seconds,
             error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data.get('agent_id'),
            session_data.get('session_id'),
            session_data.get('start_time'),
            session_data.get('end_time'),
            session_data.get('input_text'),
            session_data.get('output_text'),
            session_data.get('model_name'),
            session_data.get('input_tokens', 0),
            session_data.get('output_tokens', 0),
            session_data.get('total_cost', 0.0),
            session_data.get('latency_seconds', 0.0),
            session_data.get('error_message'),
            json.dumps(session_data.get('metadata', {}))
        ))

        conn.commit()
        conn.close()

    def record_drift_event(self, drift_data: Dict[str, Any]):
        """Record a drift detection event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO drift_events (agent_id, timestamp, drift_type, drift_score, threshold, responses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            drift_data.get('agent_id'),
            drift_data.get('timestamp'),
            drift_data.get('drift_type'),
            drift_data.get('drift_score'),
            drift_data.get('threshold'),
            json.dumps(drift_data.get('responses', []))
        ))

        conn.commit()
        conn.close()

    def get_dashboard_stats(self, hours_back: int = 24) -> DashboardStats:
        """Get dashboard statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        # Total agents
        cursor.execute('SELECT COUNT(DISTINCT agent_id) FROM agent_sessions')
        total_agents = cursor.fetchone()[0] or 0

        # Active agents (last 24h)
        cursor.execute('''
            SELECT COUNT(DISTINCT agent_id)
            FROM agent_sessions
            WHERE start_time > ?
        ''', (cutoff_time,))
        active_agents = cursor.fetchone()[0] or 0

        # Total requests (24h)
        cursor.execute('''
            SELECT COUNT(*)
            FROM agent_sessions
            WHERE start_time > ?
        ''', (cutoff_time,))
        total_requests_24h = cursor.fetchone()[0] or 0

        # Total cost (24h)
        cursor.execute('''
            SELECT COALESCE(SUM(total_cost), 0)
            FROM agent_sessions
            WHERE start_time > ?
        ''', (cutoff_time,))
        total_cost_24h = cursor.fetchone()[0] or 0.0

        # Average drift score (24h)
        cursor.execute('''
            SELECT AVG(drift_score)
            FROM drift_events
            WHERE timestamp > ?
        ''', (cutoff_time,))
        avg_drift_result = cursor.fetchone()[0]
        avg_drift_score = avg_drift_result if avg_drift_result else 0.0

        # Error count (24h)
        cursor.execute('''
            SELECT COUNT(*)
            FROM agent_sessions
            WHERE start_time > ? AND error_message IS NOT NULL
        ''', (cutoff_time,))
        error_count_24h = cursor.fetchone()[0] or 0

        conn.close()

        return DashboardStats(
            total_agents=total_agents,
            active_agents=active_agents,
            total_requests_24h=total_requests_24h,
            total_cost_24h=total_cost_24h,
            avg_drift_score=avg_drift_score,
            error_count_24h=error_count_24h
        )

    def get_agent_metrics(self, agent_id: Optional[int] = None) -> List[AgentMetricsResponse]:
        """Get metrics for specific agent or all agents."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if agent_id:
            where_clause = "WHERE agent_id = ?"
            params = (agent_id,)
        else:
            where_clause = ""
            params = ()

        cursor.execute(f'''
            SELECT
                agent_id,
                COUNT(*) as total_requests,
                COALESCE(SUM(total_cost), 0) as total_cost,
                COALESCE(AVG(latency_seconds), 0) as avg_latency,
                COALESCE(
                    SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                    0
                ) as error_rate,
                MAX(start_time) as last_activity
            FROM agent_sessions
            {where_clause}
            GROUP BY agent_id
            ORDER BY last_activity DESC
        ''', params)

        results = []
        for row in cursor.fetchall():
            # Get drift score for agent
            cursor.execute('''
                SELECT AVG(drift_score)
                FROM drift_events
                WHERE agent_id = ? AND timestamp > ?
            ''', (row[0], datetime.now() - timedelta(hours=24)))

            drift_result = cursor.fetchone()
            drift_score = drift_result[0] if drift_result and drift_result[0] else None

            results.append(AgentMetricsResponse(
                agent_id=row[0],
                total_requests=row[1],
                total_cost=row[2],
                avg_latency=row[3],
                error_rate=row[4],
                last_activity=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                drift_score=drift_score
            ))

        conn.close()
        return results

class DevelopmentServer:
    """Main development server class."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.app = FastAPI(title="Briefcase AI Development Dashboard", version="1.0.0")
        self.host = host
        self.port = port
        self.db = TelemetryDatabase()
        self.connection_manager = ConnectionManager()

        # Setup routes
        self._setup_routes()
        self._setup_static_files()

    def _setup_routes(self):
        """Setup API routes."""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Serve the main dashboard page."""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Briefcase AI Dashboard</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <script src="https://cdn.tailwindcss.com"></script>
                <style>
                    .metric-card { transition: transform 0.2s; }
                    .metric-card:hover { transform: scale(1.02); }
                    .status-indicator { animation: pulse 2s infinite; }
                </style>
            </head>
            <body class="bg-gray-100 min-h-screen">
                <div id="app"></div>
                <script src="/static/dashboard.js"></script>
            </body>
            </html>
            """

        @self.app.get("/api/stats")
        async def get_dashboard_stats():
            """Get overall dashboard statistics."""
            stats = self.db.get_dashboard_stats()
            return stats

        @self.app.get("/api/agents")
        async def get_all_agents():
            """Get metrics for all agents."""
            agents = self.db.get_agent_metrics()
            return agents

        @self.app.get("/api/agents/{agent_id}")
        async def get_agent_metrics(agent_id: int):
            """Get metrics for a specific agent."""
            agents = self.db.get_agent_metrics(agent_id)
            if not agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            return agents[0]

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await self.connection_manager.connect(websocket)
            try:
                while True:
                    # Keep connection alive and send periodic updates
                    stats = self.db.get_dashboard_stats()
                    await self.connection_manager.send_personal_message(
                        json.dumps({"type": "stats_update", "data": asdict(stats)}),
                        websocket
                    )
                    await asyncio.sleep(5)  # Update every 5 seconds
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)

        @self.app.post("/api/telemetry")
        async def receive_telemetry(data: Dict[str, Any]):
            """Receive telemetry data from agents."""
            # Store in database
            if data.get('type') == 'session':
                self.db.record_session(data)
            elif data.get('type') == 'drift_event':
                self.db.record_drift_event(data)

            # Broadcast to connected clients
            await self.connection_manager.broadcast(
                json.dumps({"type": "telemetry_event", "data": data})
            )

            return {"status": "received"}

    def _setup_static_files(self):
        """Setup static file serving."""
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)

        # Create dashboard JavaScript
        dashboard_js = '''
// Briefcase AI Dashboard JavaScript
class Dashboard {
    constructor() {
        this.ws = null;
        this.charts = {};
        this.init();
    }

    init() {
        this.createLayout();
        this.connectWebSocket();
        this.loadInitialData();
        this.setupCharts();
    }

    createLayout() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-4xl font-bold text-gray-800 mb-8">
                    🔭 Briefcase AI Dashboard
                </h1>

                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div class="metric-card bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-lg font-semibold text-gray-600">Total Agents</h3>
                        <p id="total-agents" class="text-3xl font-bold text-blue-600">-</p>
                    </div>
                    <div class="metric-card bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-lg font-semibold text-gray-600">24h Requests</h3>
                        <p id="total-requests" class="text-3xl font-bold text-green-600">-</p>
                    </div>
                    <div class="metric-card bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-lg font-semibold text-gray-600">24h Cost</h3>
                        <p id="total-cost" class="text-3xl font-bold text-yellow-600">-</p>
                    </div>
                    <div class="metric-card bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-lg font-semibold text-gray-600">Avg Drift</h3>
                        <p id="avg-drift" class="text-3xl font-bold text-red-600">-</p>
                    </div>
                </div>

                <!-- Charts -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-xl font-semibold mb-4">Cost Over Time</h3>
                        <canvas id="cost-chart"></canvas>
                    </div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h3 class="text-xl font-semibold mb-4">Request Volume</h3>
                        <canvas id="requests-chart"></canvas>
                    </div>
                </div>

                <!-- Agent List -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h3 class="text-xl font-semibold mb-4">Active Agents</h3>
                    <div id="agents-list" class="space-y-4">
                        <!-- Agents will be populated here -->
                    </div>
                </div>

                <!-- Connection Status -->
                <div class="fixed bottom-4 right-4">
                    <div id="connection-status" class="bg-green-500 text-white px-4 py-2 rounded-lg">
                        <span class="status-indicator inline-block w-2 h-2 bg-white rounded-full mr-2"></span>
                        Connected
                    </div>
                </div>
            </div>
        `;
    }

    connectWebSocket() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${location.host}/ws`);

        this.ws.onopen = () => {
            document.getElementById('connection-status').className =
                'bg-green-500 text-white px-4 py-2 rounded-lg';
            document.getElementById('connection-status').innerHTML = `
                <span class="status-indicator inline-block w-2 h-2 bg-white rounded-full mr-2"></span>
                Connected
            `;
        };

        this.ws.onclose = () => {
            document.getElementById('connection-status').className =
                'bg-red-500 text-white px-4 py-2 rounded-lg';
            document.getElementById('connection-status').innerHTML = `
                <span class="inline-block w-2 h-2 bg-white rounded-full mr-2"></span>
                Disconnected
            `;
            // Reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'stats_update') {
                this.updateStats(message.data);
            } else if (message.type === 'telemetry_event') {
                this.handleTelemetryEvent(message.data);
            }
        };
    }

    async loadInitialData() {
        try {
            const [statsResponse, agentsResponse] = await Promise.all([
                fetch('/api/stats'),
                fetch('/api/agents')
            ]);

            const stats = await statsResponse.json();
            const agents = await agentsResponse.json();

            this.updateStats(stats);
            this.updateAgentsList(agents);
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    updateStats(stats) {
        document.getElementById('total-agents').textContent = stats.total_agents;
        document.getElementById('total-requests').textContent = stats.total_requests_24h;
        document.getElementById('total-cost').textContent = `$${stats.total_cost_24h.toFixed(4)}`;
        document.getElementById('avg-drift').textContent = stats.avg_drift_score.toFixed(3);
    }

    updateAgentsList(agents) {
        const agentsList = document.getElementById('agents-list');

        if (agents.length === 0) {
            agentsList.innerHTML = '<p class="text-gray-500">No active agents</p>';
            return;
        }

        agentsList.innerHTML = agents.map(agent => `
            <div class="border rounded-lg p-4">
                <div class="flex justify-between items-center">
                    <h4 class="text-lg font-semibold">Agent ${agent.agent_id}</h4>
                    <span class="text-sm text-gray-500">
                        Last active: ${new Date(agent.last_activity).toLocaleTimeString()}
                    </span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                    <div>
                        <span class="text-sm text-gray-600">Requests:</span>
                        <span class="font-semibold">${agent.total_requests}</span>
                    </div>
                    <div>
                        <span class="text-sm text-gray-600">Cost:</span>
                        <span class="font-semibold">$${agent.total_cost.toFixed(4)}</span>
                    </div>
                    <div>
                        <span class="text-sm text-gray-600">Latency:</span>
                        <span class="font-semibold">${agent.avg_latency.toFixed(2)}s</span>
                    </div>
                    <div>
                        <span class="text-sm text-gray-600">Error Rate:</span>
                        <span class="font-semibold ${agent.error_rate > 5 ? 'text-red-600' : 'text-green-600'}">
                            ${agent.error_rate.toFixed(1)}%
                        </span>
                    </div>
                </div>
                ${agent.drift_score !== null ? `
                    <div class="mt-2">
                        <span class="text-sm text-gray-600">Drift Score:</span>
                        <span class="font-semibold ${agent.drift_score < 0.7 ? 'text-red-600' : 'text-green-600'}">
                            ${agent.drift_score.toFixed(3)}
                        </span>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    setupCharts() {
        // Cost chart
        const costCtx = document.getElementById('cost-chart').getContext('2d');
        this.charts.cost = new Chart(costCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Cost ($)',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Requests chart
        const requestsCtx = document.getElementById('requests-chart').getContext('2d');
        this.charts.requests = new Chart(requestsCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Requests',
                    data: [],
                    backgroundColor: 'rgba(34, 197, 94, 0.5)',
                    borderColor: 'rgb(34, 197, 94)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    handleTelemetryEvent(event) {
        // Handle real-time telemetry events
        console.log('Telemetry event:', event);
        // Add visual notifications for new events
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
        '''

        with open(static_dir / "dashboard.js", "w") as f:
            f.write(dashboard_js)

        self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def run(self):
        """Run the development server."""
        print(f"🔭 Starting Briefcase AI Development Server")
        print(f"📊 Dashboard: http://{self.host}:{self.port}")
        print(f"📡 WebSocket: ws://{self.host}:{self.port}/ws")
        print(f"🗃️  Database: {self.db.db_path}")
        print("=" * 50)

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )

def main():
    """Main entry point for development server."""
    import argparse

    parser = argparse.ArgumentParser(description="Briefcase AI Development Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--db", default="telemetry.db", help="SQLite database path")

    args = parser.parse_args()

    server = DevelopmentServer(host=args.host, port=args.port)
    server.run()

if __name__ == "__main__":
    main()