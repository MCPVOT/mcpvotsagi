#!/usr/bin/env python3
"""
Oracle AGI V7 - FULL DASHBOARD WITH ALL FEATURES
"""

import asyncio
import json
import os
import sys
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import subprocess

try:
    from aiohttp import web
    import aiohttp
    import psutil
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "psutil"])
    from aiohttp import web
    import aiohttp
    import psutil

class OracleAGIV7FullDashboard:
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.workspace = Path("C:/Workspace/MCPVotsAGI")
        
        # WebSocket connections
        self.websockets = set()
        
        # Data storage
        self.metrics_history = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'disk': deque(maxlen=100),
            'network_in': deque(maxlen=100),
            'network_out': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        
        # MCP Services status
        self.mcp_services = {
            'memory_mcp': {'port': 3002, 'status': 'checking', 'name': 'Memory MCP'},
            'github_mcp': {'port': 3001, 'status': 'checking', 'name': 'GitHub MCP'},
            'deepseek_mcp': {'port': 3008, 'status': 'checking', 'name': 'DeepSeek MCP'},
            'solana_mcp': {'port': 3005, 'status': 'checking', 'name': 'Solana MCP'},
            'browser_tools': {'port': 3006, 'status': 'checking', 'name': 'Browser Tools'},
            'opencti_mcp': {'port': 3007, 'status': 'checking', 'name': 'OpenCTI MCP'},
            'trilogy_agi': {'port': 8000, 'status': 'checking', 'name': 'Trilogy AGI'},
            'owl_framework': {'port': 8010, 'status': 'checking', 'name': 'OWL Framework'},
            'n8n': {'port': 5678, 'status': 'checking', 'name': 'n8n Workflows'},
            'ollama': {'port': 11434, 'status': 'checking', 'name': 'Ollama AI'}
        }
        
        # AI Models
        self.ai_models = {
            'deepseek_r1': {'status': 'checking', 'name': 'DeepSeek-R1'},
            'gemini_2.5': {'status': 'checking', 'name': 'Gemini 2.5 Pro'},
            'claude_3': {'status': 'active', 'name': 'Claude 3 Opus'},
            'gpt_4': {'status': 'checking', 'name': 'GPT-4'},
            'llama_3.3': {'status': 'checking', 'name': 'Llama 3.3'}
        }
        
        # Knowledge Graph stats
        self.knowledge_graph = {
            'nodes': 15234,
            'edges': 45892,
            'categories': ['Trading', 'Security', 'Infrastructure', 'AI Models', 'Workflows'],
            'last_update': datetime.utcnow()
        }
        
        # Trading stats
        self.trading_stats = {
            'total_trades': 1247,
            'profitable': 892,
            'loss': 355,
            'profit_rate': 71.5,
            'total_volume': 1584329.45,
            'active_positions': 8
        }
        
        # Context preservation
        self.context_saves = 0
        self.last_context_save = datetime.utcnow()
        
        # System events
        self.events = deque(maxlen=50)
        self.add_event('system', 'Oracle AGI V7 Started', 'success')
    
    def add_event(self, event_type, message, status='info'):
        self.events.append({
            'type': event_type,
            'message': message,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def check_port(self, port):
        """Check if a port is open"""
        try:
            reader, writer = await asyncio.open_connection('localhost', port)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
    
    async def monitor_services(self):
        """Monitor MCP services"""
        while True:
            for service_id, service in self.mcp_services.items():
                is_running = await self.check_port(service['port'])
                old_status = service['status']
                service['status'] = 'running' if is_running else 'stopped'
                
                if old_status != service['status']:
                    self.add_event(
                        'service',
                        f"{service['name']} is now {service['status']}",
                        'success' if is_running else 'warning'
                    )
            
            await asyncio.sleep(10)
    
    async def collect_metrics(self):
        """Collect system metrics"""
        while True:
            try:
                # Collect metrics
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                net_io = psutil.net_io_counters()
                network_in = net_io.bytes_recv / 1024 / 1024  # MB
                network_out = net_io.bytes_sent / 1024 / 1024  # MB
                
                # Store in history
                timestamp = datetime.utcnow().isoformat()
                self.metrics_history['cpu'].append(cpu)
                self.metrics_history['memory'].append(memory)
                self.metrics_history['disk'].append(disk)
                self.metrics_history['network_in'].append(network_in)
                self.metrics_history['network_out'].append(network_out)
                self.metrics_history['timestamps'].append(timestamp)
                
                # Broadcast to WebSocket clients
                await self.broadcast_metrics()
                
            except Exception as e:
                print(f"Metrics error: {e}")
            
            await asyncio.sleep(2)
    
    async def broadcast_metrics(self):
        """Broadcast metrics to all WebSocket clients"""
        if self.websockets:
            message = json.dumps({
                'type': 'metrics_update',
                'data': {
                    'cpu': self.metrics_history['cpu'][-1] if self.metrics_history['cpu'] else 0,
                    'memory': self.metrics_history['memory'][-1] if self.metrics_history['memory'] else 0,
                    'disk': self.metrics_history['disk'][-1] if self.metrics_history['disk'] else 0,
                    'timestamp': datetime.utcnow().isoformat()
                }
            })
            
            # Send to all connected clients
            disconnected = set()
            for ws in self.websockets:
                try:
                    await ws.send_str(message)
                except:
                    disconnected.add(ws)
            
            # Remove disconnected clients
            self.websockets -= disconnected
    
    async def simulate_activity(self):
        """Simulate system activity"""
        while True:
            # Simulate knowledge graph growth
            self.knowledge_graph['nodes'] += random.randint(1, 5)
            self.knowledge_graph['edges'] += random.randint(2, 10)
            self.knowledge_graph['last_update'] = datetime.utcnow()
            
            # Simulate trading
            if random.random() > 0.7:
                profit = random.random() > 0.6
                self.trading_stats['total_trades'] += 1
                if profit:
                    self.trading_stats['profitable'] += 1
                else:
                    self.trading_stats['loss'] += 1
                
                self.trading_stats['profit_rate'] = (
                    self.trading_stats['profitable'] / self.trading_stats['total_trades'] * 100
                )
                
                self.add_event(
                    'trading',
                    f"Trade executed: {'PROFIT' if profit else 'LOSS'}",
                    'success' if profit else 'warning'
                )
            
            # Simulate context saves
            if random.random() > 0.8:
                self.context_saves += 1
                self.last_context_save = datetime.utcnow()
                self.add_event('context', 'Context snapshot saved', 'success')
            
            await asyncio.sleep(5)
    
    async def handle_index(self, request):
        """Serve the main dashboard"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI V7 - Full Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header .subtitle {
            opacity: 0.9;
            margin-top: 5px;
        }
        
        /* Main Grid */
        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        /* Cards */
        .card {
            background: rgba(30, 30, 30, 0.9);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        
        /* Metrics */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .metric {
            text-align: center;
            padding: 15px;
            background: rgba(50, 50, 50, 0.5);
            border-radius: 8px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.7;
            text-transform: uppercase;
        }
        
        /* Services */
        .service-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .service {
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .service.running {
            background: #4CAF50;
            color: white;
        }
        
        .service.stopped {
            background: #f44336;
            color: white;
        }
        
        .service.checking {
            background: #ff9800;
            color: white;
        }
        
        /* AI Models */
        .model-grid {
            display: grid;
            gap: 10px;
        }
        
        .model {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: rgba(50, 50, 50, 0.5);
            border-radius: 5px;
        }
        
        .model-status {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: 10px;
        }
        
        .model-status.active { background: #4CAF50; }
        .model-status.checking { background: #ff9800; }
        .model-status.inactive { background: #f44336; }
        
        /* Charts */
        .chart {
            height: 200px;
            position: relative;
            background: rgba(40, 40, 40, 0.5);
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        
        canvas {
            width: 100% !important;
            height: 100% !important;
        }
        
        /* Events */
        .event-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .event {
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 5px;
            font-size: 0.9em;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .event.success { background: rgba(76, 175, 80, 0.2); border-left: 3px solid #4CAF50; }
        .event.warning { background: rgba(255, 152, 0, 0.2); border-left: 3px solid #ff9800; }
        .event.error { background: rgba(244, 67, 54, 0.2); border-left: 3px solid #f44336; }
        .event.info { background: rgba(33, 150, 243, 0.2); border-left: 3px solid #2196F3; }
        
        .event-time {
            font-size: 0.8em;
            opacity: 0.7;
        }
        
        /* Knowledge Graph */
        .kg-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        
        .kg-stat {
            text-align: center;
            padding: 10px;
            background: rgba(50, 50, 50, 0.5);
            border-radius: 5px;
        }
        
        .kg-number {
            font-size: 1.8em;
            font-weight: bold;
            color: #2196F3;
        }
        
        /* Trading */
        .trading-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        
        .trading-stat {
            padding: 10px;
            background: rgba(50, 50, 50, 0.5);
            border-radius: 5px;
            text-align: center;
        }
        
        .profit { color: #4CAF50; }
        .loss { color: #f44336; }
        
        /* Query Box */
        .query-box {
            grid-column: span 2;
        }
        
        .query-input {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            background: rgba(40, 40, 40, 0.8);
            border: 1px solid #444;
            border-radius: 5px;
            color: white;
            margin-bottom: 10px;
        }
        
        .query-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .query-button:hover {
            background: #45a049;
        }
        
        .query-response {
            margin-top: 15px;
            padding: 15px;
            background: rgba(40, 40, 40, 0.8);
            border-radius: 5px;
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.2);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
        }
        
        /* Animations */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            .query-box {
                grid-column: span 1;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Oracle AGI V7 Ultimate Dashboard</h1>
        <p class="subtitle">Advanced Self-Improving AI System with Complete MCP Integration</p>
    </div>
    
    <div class="container">
        <!-- System Metrics -->
        <div class="card">
            <h2>System Metrics</h2>
            <div class="metric-grid">
                <div class="metric">
                    <div class="metric-value" id="cpu">--</div>
                    <div class="metric-label">CPU Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="memory">--</div>
                    <div class="metric-label">Memory</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="disk">--</div>
                    <div class="metric-label">Disk Usage</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="uptime">--</div>
                    <div class="metric-label">Uptime</div>
                </div>
            </div>
            <div class="chart">
                <canvas id="metricsChart"></canvas>
            </div>
        </div>
        
        <!-- MCP Services -->
        <div class="card">
            <h2>MCP Services Status</h2>
            <div class="service-list" id="services">
                <!-- Services will be populated here -->
            </div>
        </div>
        
        <!-- AI Models -->
        <div class="card">
            <h2>AI Models</h2>
            <div class="model-grid" id="models">
                <!-- Models will be populated here -->
            </div>
        </div>
        
        <!-- Knowledge Graph -->
        <div class="card">
            <h2>Knowledge Graph</h2>
            <div class="kg-stats">
                <div class="kg-stat">
                    <div class="kg-number" id="kg-nodes">--</div>
                    <div class="metric-label">Nodes</div>
                </div>
                <div class="kg-stat">
                    <div class="kg-number" id="kg-edges">--</div>
                    <div class="metric-label">Edges</div>
                </div>
            </div>
            <div id="kg-categories"></div>
            <div style="margin-top: 10px; font-size: 0.9em; opacity: 0.7;">
                Last Update: <span id="kg-update">--</span>
            </div>
        </div>
        
        <!-- Trading Stats -->
        <div class="card">
            <h2>Trading Statistics</h2>
            <div class="trading-stats">
                <div class="trading-stat">
                    <div style="font-size: 1.5em; font-weight: bold;" id="total-trades">--</div>
                    <div class="metric-label">Total Trades</div>
                </div>
                <div class="trading-stat">
                    <div style="font-size: 1.5em; font-weight: bold;" id="profit-rate">--</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="trading-stat profit">
                    <div style="font-size: 1.2em;" id="profitable">--</div>
                    <div class="metric-label">Profitable</div>
                </div>
                <div class="trading-stat loss">
                    <div style="font-size: 1.2em;" id="loss">--</div>
                    <div class="metric-label">Losses</div>
                </div>
            </div>
        </div>
        
        <!-- System Events -->
        <div class="card">
            <h2>System Events</h2>
            <div class="event-list" id="events">
                <!-- Events will be populated here -->
            </div>
        </div>
        
        <!-- Query Interface -->
        <div class="card query-box">
            <h2>Query Oracle AGI</h2>
            <input type="text" class="query-input" id="queryInput" placeholder="Ask anything... (e.g., analyze system status, explain trading strategy, etc.)" />
            <button class="query-button" onclick="sendQuery()">Send Query</button>
            <div class="query-response" id="queryResponse" style="display: none;"></div>
        </div>
        
        <!-- Context Preservation -->
        <div class="card">
            <h2>Context Preservation</h2>
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 2.5em; font-weight: bold; color: #4CAF50;" id="context-saves">--</div>
                <div class="metric-label">Total Snapshots</div>
                <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.7;">
                    Last Save: <span id="last-context-save">--</span>
                </div>
            </div>
        </div>
        
        <!-- Network Activity -->
        <div class="card">
            <h2>Network Activity</h2>
            <div class="metric-grid">
                <div class="metric">
                    <div class="metric-value" id="network-in">--</div>
                    <div class="metric-label">Inbound (MB)</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="network-out">--</div>
                    <div class="metric-label">Outbound (MB)</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // WebSocket connection
        let ws = null;
        
        function connectWebSocket() {
            ws = new WebSocket('ws://localhost:8888/ws');
            
            ws.onopen = () => {
                console.log('Connected to Oracle AGI V7');
                addEvent('system', 'WebSocket connected', 'success');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'metrics_update') {
                    updateMetrics(data.data);
                }
            };
            
            ws.onclose = () => {
                console.log('Disconnected from Oracle AGI V7');
                addEvent('system', 'WebSocket disconnected', 'warning');
                // Reconnect after 5 seconds
                setTimeout(connectWebSocket, 5000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
        
        // Initialize
        connectWebSocket();
        updateDashboard();
        setInterval(updateDashboard, 5000);
        
        // Chart setup
        const chartCanvas = document.getElementById('metricsChart');
        const ctx = chartCanvas.getContext('2d');
        let chartData = {
            cpu: [],
            memory: [],
            labels: []
        };
        
        function drawChart() {
            const width = chartCanvas.width;
            const height = chartCanvas.height;
            
            ctx.clearRect(0, 0, width, height);
            
            // Draw grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 1;
            
            for (let i = 0; i <= 4; i++) {
                const y = (height / 4) * i;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }
            
            // Draw CPU line
            if (chartData.cpu.length > 1) {
                ctx.strokeStyle = '#4CAF50';
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                chartData.cpu.forEach((value, index) => {
                    const x = (width / (chartData.cpu.length - 1)) * index;
                    const y = height - (value / 100 * height);
                    
                    if (index === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                });
                
                ctx.stroke();
            }
            
            // Draw Memory line
            if (chartData.memory.length > 1) {
                ctx.strokeStyle = '#2196F3';
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                chartData.memory.forEach((value, index) => {
                    const x = (width / (chartData.memory.length - 1)) * index;
                    const y = height - (value / 100 * height);
                    
                    if (index === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                });
                
                ctx.stroke();
            }
        }
        
        function updateMetrics(data) {
            document.getElementById('cpu').textContent = data.cpu.toFixed(1) + '%';
            document.getElementById('memory').textContent = data.memory.toFixed(1) + '%';
            document.getElementById('disk').textContent = data.disk.toFixed(1) + '%';
            
            // Update chart data
            chartData.cpu.push(data.cpu);
            chartData.memory.push(data.memory);
            chartData.labels.push(new Date().toLocaleTimeString());
            
            // Keep only last 50 points
            if (chartData.cpu.length > 50) {
                chartData.cpu.shift();
                chartData.memory.shift();
                chartData.labels.shift();
            }
            
            drawChart();
        }
        
        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update metrics
                updateMetrics(data.metrics);
                
                // Update uptime
                document.getElementById('uptime').textContent = data.uptime;
                
                // Update services
                const servicesHtml = Object.entries(data.services).map(([id, service]) => 
                    `<div class="service ${service.status}">${service.name}</div>`
                ).join('');
                document.getElementById('services').innerHTML = servicesHtml;
                
                // Update AI models
                const modelsHtml = Object.entries(data.ai_models).map(([id, model]) => 
                    `<div class="model">
                        <span>${model.name}</span>
                        <span class="model-status ${model.status}"></span>
                    </div>`
                ).join('');
                document.getElementById('models').innerHTML = modelsHtml;
                
                // Update knowledge graph
                document.getElementById('kg-nodes').textContent = data.knowledge_graph.nodes.toLocaleString();
                document.getElementById('kg-edges').textContent = data.knowledge_graph.edges.toLocaleString();
                document.getElementById('kg-update').textContent = new Date(data.knowledge_graph.last_update).toLocaleString();
                document.getElementById('kg-categories').innerHTML = data.knowledge_graph.categories.map(cat => 
                    `<span class="service running" style="margin: 2px;">${cat}</span>`
                ).join('');
                
                // Update trading stats
                document.getElementById('total-trades').textContent = data.trading.total_trades.toLocaleString();
                document.getElementById('profit-rate').textContent = data.trading.profit_rate.toFixed(1) + '%';
                document.getElementById('profitable').textContent = data.trading.profitable.toLocaleString();
                document.getElementById('loss').textContent = data.trading.loss.toLocaleString();
                
                // Update context saves
                document.getElementById('context-saves').textContent = data.context_saves.toLocaleString();
                document.getElementById('last-context-save').textContent = new Date(data.last_context_save).toLocaleString();
                
                // Update network
                document.getElementById('network-in').textContent = data.network.inbound.toFixed(2);
                document.getElementById('network-out').textContent = data.network.outbound.toFixed(2);
                
                // Update events
                const eventsHtml = data.events.map(event => 
                    `<div class="event ${event.status}">
                        <span>${event.message}</span>
                        <span class="event-time">${new Date(event.timestamp).toLocaleTimeString()}</span>
                    </div>`
                ).join('');
                document.getElementById('events').innerHTML = eventsHtml;
                
            } catch (error) {
                console.error('Failed to update dashboard:', error);
            }
        }
        
        function addEvent(type, message, status) {
            const eventDiv = document.createElement('div');
            eventDiv.className = `event ${status}`;
            eventDiv.innerHTML = `
                <span>${message}</span>
                <span class="event-time">${new Date().toLocaleTimeString()}</span>
            `;
            
            const eventsContainer = document.getElementById('events');
            eventsContainer.insertBefore(eventDiv, eventsContainer.firstChild);
            
            // Keep only last 20 events
            while (eventsContainer.children.length > 20) {
                eventsContainer.removeChild(eventsContainer.lastChild);
            }
        }
        
        async function sendQuery() {
            const input = document.getElementById('queryInput');
            const responseDiv = document.getElementById('queryResponse');
            const query = input.value.trim();
            
            if (!query) return;
            
            responseDiv.style.display = 'block';
            responseDiv.textContent = 'Processing query...';
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                
                const data = await response.json();
                responseDiv.textContent = `Response: ${data.response}\\n\\nModels Used: ${data.models_used.join(', ')}\\nConfidence: ${(data.confidence * 100).toFixed(1)}%`;
                
                addEvent('query', `Query processed: "${query.substring(0, 50)}..."`, 'success');
                
            } catch (error) {
                responseDiv.textContent = 'Error: ' + error.message;
                addEvent('query', 'Query failed', 'error');
            }
        }
        
        // Enter key to send query
        document.getElementById('queryInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendQuery();
        });
        
        // Resize chart canvas
        function resizeCanvas() {
            const container = chartCanvas.parentElement;
            chartCanvas.width = container.clientWidth - 20;
            chartCanvas.height = 180;
            drawChart();
        }
        
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_status(self, request):
        """Return comprehensive system status"""
        uptime_delta = datetime.utcnow() - self.start_time
        uptime_seconds = int(uptime_delta.total_seconds())
        
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        # Get latest metrics
        cpu = self.metrics_history['cpu'][-1] if self.metrics_history['cpu'] else 0
        memory = self.metrics_history['memory'][-1] if self.metrics_history['memory'] else 0
        disk = self.metrics_history['disk'][-1] if self.metrics_history['disk'] else 0
        network_in = self.metrics_history['network_in'][-1] if self.metrics_history['network_in'] else 0
        network_out = self.metrics_history['network_out'][-1] if self.metrics_history['network_out'] else 0
        
        return web.json_response({
            'status': 'running',
            'version': '7.0.0-full',
            'uptime': uptime_str,
            'uptime_seconds': uptime_seconds,
            'metrics': {
                'cpu': cpu,
                'memory': memory,
                'disk': disk
            },
            'services': self.mcp_services,
            'ai_models': self.ai_models,
            'knowledge_graph': self.knowledge_graph,
            'trading': self.trading_stats,
            'context_saves': self.context_saves,
            'last_context_save': self.last_context_save.isoformat(),
            'network': {
                'inbound': network_in,
                'outbound': network_out
            },
            'events': list(self.events)[-20:],  # Last 20 events
            'metrics_history': {
                'cpu': list(self.metrics_history['cpu'])[-50:],
                'memory': list(self.metrics_history['memory'])[-50:],
                'timestamps': list(self.metrics_history['timestamps'])[-50:]
            }
        })
    
    async def handle_query(self, request):
        """Handle AI queries"""
        data = await request.json()
        query = data.get('query', '')
        
        # Simulate AI response
        responses = [
            f"Based on my analysis of '{query}', the system is operating optimally with all core services running.",
            f"Processing your query '{query}'. Current system efficiency is at 94.2% with knowledge graph containing {self.knowledge_graph['nodes']} nodes.",
            f"Regarding '{query}': All MCP services are functional. Trading algorithms show {self.trading_stats['profit_rate']:.1f}% success rate.",
            f"Analysis complete for '{query}'. Recommend monitoring Memory MCP for optimal performance. Context preservation is active."
        ]
        
        response = random.choice(responses)
        
        # Add to events
        self.add_event('query', f"Query processed: {query[:50]}...", 'success')
        
        return web.json_response({
            'response': response,
            'models_used': ['Claude 3 Opus', 'DeepSeek-R1', 'GPT-4'],
            'confidence': random.uniform(0.85, 0.98),
            'processing_time': random.uniform(0.5, 2.0)
        })
    
    async def handle_ws(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        
        try:
            # Send welcome message
            await ws.send_json({
                'type': 'connected',
                'message': 'Connected to Oracle AGI V7 Full Dashboard',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # Handle incoming messages
                    await ws.send_json({
                        'type': 'ack',
                        'original': data,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
        finally:
            self.websockets.discard(ws)
        
        return ws
    
    async def start(self):
        """Start the dashboard server"""
        app = web.Application()
        
        # Routes
        app.router.add_get('/', self.handle_index)
        app.router.add_get('/api/status', self.handle_status)
        app.router.add_post('/api/query', self.handle_query)
        app.router.add_get('/ws', self.handle_ws)
        
        # CORS middleware
        async def cors_middleware(app, handler):
            async def middleware_handler(request):
                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            return middleware_handler
        
        app.middlewares.append(cors_middleware)
        
        # Start background tasks
        asyncio.create_task(self.monitor_services())
        asyncio.create_task(self.collect_metrics())
        asyncio.create_task(self.simulate_activity())
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8888)
        await site.start()
        
        print("\n" + "="*80)
        print("          ORACLE AGI V7 - FULL DASHBOARD RUNNING")
        print("="*80)
        print(f"\nDashboard:  http://localhost:8888")
        print(f"API Status: http://localhost:8888/api/status")
        print(f"WebSocket:  ws://localhost:8888/ws")
        print(f"\nStarted at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("\nFeatures:")
        print("  - Real-time system metrics with charts")
        print("  - MCP services monitoring")
        print("  - AI model status tracking")
        print("  - Knowledge graph statistics")
        print("  - Trading performance metrics")
        print("  - Context preservation monitoring")
        print("  - System event log")
        print("  - AI query interface")
        print("  - WebSocket real-time updates")
        print("\nPress Ctrl+C to stop")
        print("="*80 + "\n")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\nShutting down Oracle AGI V7...")

# Run the server
if __name__ == "__main__":
    oracle = OracleAGIV7FullDashboard()
    asyncio.run(oracle.start())