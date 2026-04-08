#!/usr/bin/env python3
"""
Ultimate MCP Resource Manager V4
===============================
Advanced MCP server resource management with intelligent node reuse,
performance optimization, and dark cyberpunk monitoring interface
"""

import asyncio
import json
import logging
import os
import sys
import time
import psutil
import websockets
import socket
from datetime import datetime, timedelta
from pathlib import Path
from typing import Set, Tuple
from dataclasses import dataclass, asdict
import aiohttp
from aiohttp import web, WSMsgType
from aiohttp_jinja2 import setup as jinja2_setup
import jinja2
import subprocess
import threading
import weakref

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_resource_manager.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MCPResourceManager")

@dataclass
class MCPNode:
    """Enhanced MCP Node configuration with performance tracking"""
    name: str
    type: str  # server, client, proxy, bridge
    port: int
    status: str  # active, idle, stopped, error
    last_used: datetime
    memory_usage: float
    cpu_usage: float
    connections: int
    tools: list[str]
    process_id: Optional[int] = None
    health_score: float = 1.0
    request_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    uptime: float = 0.0
    node_id: str = ""

@dataclass
class ResourcePool:
    """Enhanced resource pool for MCP nodes with intelligent allocation"""
    active_nodes: dict[str, MCPNode]
    idle_nodes: set[str]
    failed_nodes: set[str]
    node_registry: dict[str, Dict[str, Any]]
    tool_mapping: dict[str, List[str]]  # tool -> nodes that provide it
    load_balancer: dict[str, int]  # node -> current load

@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    total_nodes: int
    active_nodes: int
    idle_nodes: int
    failed_nodes: int
    total_memory: float
    total_cpu: float
    total_requests: int
    avg_response_time: float
    uptime: float
    timestamp: datetime

class MCPResourceManager:
    """Advanced MCP Resource Manager with intelligent node management"""

    def __init__(self):
        self.resource_pool = ResourcePool(
            active_nodes={},
            idle_nodes=set(),
            failed_nodes=set(),
            node_registry={},
            tool_mapping={},
            load_balancer={}
        )
        self.metrics_history = []
        self.websocket_clients = set()
        self.monitoring_active = False
        self.reuse_threshold = 0.8  # CPU threshold for node reuse
        self.idle_timeout = 300  # 5 minutes idle timeout
        self.health_check_interval = 30  # 30 seconds
        self.max_nodes_per_tool = 3
        self.app = None
        self.session = None

    async def initialize(self):
        """Initialize the MCP resource manager"""
        logger.info("🚀 Initializing Ultimate MCP Resource Manager V4...")

        # Initialize HTTP session
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )

        # Setup web application
        self.app = web.Application()
        self.setup_routes()

        # Setup templates
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)

        # Create MCP dashboard template
        await self.create_dashboard_template()

        jinja2_setup(self.app, loader=jinja2.FileSystemLoader(str(template_dir)))

        # Start background monitoring
        asyncio.create_task(self.monitor_resources())
        asyncio.create_task(self.health_check_loop())
        asyncio.create_task(self.cleanup_idle_nodes())

        logger.info("✅ MCP Resource Manager initialized successfully")

    def setup_routes(self):
        """Setup web application routes"""
        self.app.router.add_get('/', self.dashboard_handler)
        self.app.router.add_get('/api/metrics', self.metrics_handler)
        self.app.router.add_get('/api/nodes', self.nodes_handler)
        self.app.router.add_post('/api/nodes/{node_id}/restart', self.restart_node_handler)
        self.app.router.add_post('/api/nodes/{node_id}/stop', self.stop_node_handler)
        self.app.router.add_get('/api/tools', self.tools_handler)
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_static('/static', Path(__file__).parent / "static")

    async def create_dashboard_template(self):
        """Create the dark cyberpunk dashboard template"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Resource Manager - Dark Cyberpunk Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a, #1a1a2e, #16213e);
            color: #00ffff;
            overflow-x: hidden;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(0, 255, 255, 0.1);
            border: 2px solid #00ffff;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }

        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ffff;
            margin-bottom: 10px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #00ffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.5);
        }

        .card h2 {
            color: #00ffff;
            margin-bottom: 15px;
            text-shadow: 0 0 5px #00ffff;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 8px;
            background: rgba(0, 255, 255, 0.1);
            border-radius: 5px;
        }

        .metric-value {
            font-weight: bold;
            color: #00ff00;
            text-shadow: 0 0 5px #00ff00;
        }

        .status-active {
            color: #00ff00;
            text-shadow: 0 0 5px #00ff00;
        }

        .status-idle {
            color: #ffff00;
            text-shadow: 0 0 5px #ffff00;
        }

        .status-error {
            color: #ff0000;
            text-shadow: 0 0 5px #ff0000;
        }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ffff, #00ff00);
            transition: width 0.3s ease;
        }

        .node-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .node-item {
            padding: 10px;
            margin-bottom: 10px;
            background: rgba(0, 255, 255, 0.1);
            border-left: 4px solid #00ffff;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .node-item:hover {
            background: rgba(0, 255, 255, 0.2);
            transform: translateX(5px);
        }

        .btn {
            padding: 8px 16px;
            margin: 5px;
            background: linear-gradient(45deg, #00ffff, #0099cc);
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .btn:hover {
            background: linear-gradient(45deg, #00cccc, #007799);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 255, 0.4);
        }

        .btn-danger {
            background: linear-gradient(45deg, #ff0000, #cc0000);
            color: #fff;
        }

        .btn-danger:hover {
            background: linear-gradient(45deg, #cc0000, #990000);
        }

        .real-time-chart {
            width: 100%;
            height: 200px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            margin-top: 10px;
        }

        .timestamp {
            font-size: 0.8em;
            color: #888;
            text-align: center;
            margin-top: 20px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        .glow {
            text-shadow: 0 0 10px currentColor;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="glow">🛡️ MCP RESOURCE MANAGER</h1>
            <p>Advanced Node Management & Resource Optimization</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>System Metrics</h2>
                <div class="metric">
                    <span>Total Nodes:</span>
                    <span class="metric-value" id="total-nodes">0</span>
                </div>
                <div class="metric">
                    <span>Active Nodes:</span>
                    <span class="metric-value status-active" id="active-nodes">0</span>
                </div>
                <div class="metric">
                    <span>Idle Nodes:</span>
                    <span class="metric-value status-idle" id="idle-nodes">0</span>
                </div>
                <div class="metric">
                    <span>Failed Nodes:</span>
                    <span class="metric-value status-error" id="failed-nodes">0</span>
                </div>
                <div class="metric">
                    <span>System CPU:</span>
                    <span class="metric-value" id="system-cpu">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                </div>
                <div class="metric">
                    <span>System Memory:</span>
                    <span class="metric-value" id="system-memory">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                </div>
            </div>

            <div class="card">
                <h2>Performance Metrics</h2>
                <div class="metric">
                    <span>Total Requests:</span>
                    <span class="metric-value" id="total-requests">0</span>
                </div>
                <div class="metric">
                    <span>Avg Response Time:</span>
                    <span class="metric-value" id="avg-response-time">0ms</span>
                </div>
                <div class="metric">
                    <span>System Uptime:</span>
                    <span class="metric-value" id="system-uptime">0h 0m</span>
                </div>
                <div class="metric">
                    <span>Node Efficiency:</span>
                    <span class="metric-value" id="node-efficiency">100%</span>
                </div>
                <div class="real-time-chart" id="performance-chart"></div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Active MCP Nodes</h2>
                <div class="node-list" id="active-nodes-list">
                    <!-- Active nodes will be populated here -->
                </div>
            </div>

            <div class="card">
                <h2>Tool Registry</h2>
                <div class="node-list" id="tool-registry-list">
                    <!-- Tool registry will be populated here -->
                </div>
            </div>
        </div>

        <div class="timestamp">
            Last updated: <span id="last-update">Never</span>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://localhost:8891/ws');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };

        function updateDashboard(data) {
            // Update system metrics
            document.getElementById('total-nodes').textContent = data.total_nodes || 0;
            document.getElementById('active-nodes').textContent = data.active_nodes || 0;
            document.getElementById('idle-nodes').textContent = data.idle_nodes || 0;
            document.getElementById('failed-nodes').textContent = data.failed_nodes || 0;

            // Update performance metrics
            const cpuUsage = data.total_cpu || 0;
            const memoryUsage = data.total_memory || 0;

            document.getElementById('system-cpu').textContent = cpuUsage.toFixed(1) + '%';
            document.getElementById('system-memory').textContent = memoryUsage.toFixed(1) + '%';
            document.getElementById('cpu-progress').style.width = cpuUsage + '%';
            document.getElementById('memory-progress').style.width = memoryUsage + '%';

            document.getElementById('total-requests').textContent = data.total_requests || 0;
            document.getElementById('avg-response-time').textContent = (data.avg_response_time || 0).toFixed(2) + 'ms';

            // Update uptime
            const uptimeHours = Math.floor((data.uptime || 0) / 3600);
            const uptimeMinutes = Math.floor(((data.uptime || 0) % 3600) / 60);
            document.getElementById('system-uptime').textContent = uptimeHours + 'h ' + uptimeMinutes + 'm';

            // Update node efficiency
            const efficiency = data.active_nodes > 0 ? ((data.active_nodes / data.total_nodes) * 100) : 100;
            document.getElementById('node-efficiency').textContent = efficiency.toFixed(1) + '%';

            // Update active nodes list
            updateNodesList(data.nodes || []);

            // Update tool registry
            updateToolRegistry(data.tools || {});

            // Update timestamp
            document.getElementById('last-update').textContent = new Date().toLocaleString();
        }

        function updateNodesList(nodes) {
            const container = document.getElementById('active-nodes-list');
            container.innerHTML = '';

            nodes.forEach(node => {
                const nodeElement = document.createElement('div');
                nodeElement.className = 'node-item';
                nodeElement.innerHTML = `
                    <strong>${node.name}</strong> (${node.type})
                    <br>
                    <small>Status: <span class="status-${node.status}">${node.status}</span></small>
                    <br>
                    <small>CPU: ${node.cpu_usage.toFixed(1)}% | Memory: ${node.memory_usage.toFixed(1)}MB</small>
                    <br>
                    <small>Tools: ${node.tools.join(', ')}</small>
                    <div>
                        <button class="btn" onclick="restartNode('${node.node_id}')">Restart</button>
                        <button class="btn btn-danger" onclick="stopNode('${node.node_id}')">Stop</button>
                    </div>
                `;
                container.appendChild(nodeElement);
            });
        }

        function updateToolRegistry(tools) {
            const container = document.getElementById('tool-registry-list');
            container.innerHTML = '';

            Object.entries(tools).forEach(([tool, nodes]) => {
                const toolElement = document.createElement('div');
                toolElement.className = 'node-item';
                toolElement.innerHTML = `
                    <strong>${tool}</strong>
                    <br>
                    <small>Available on: ${nodes.join(', ')}</small>
                `;
                container.appendChild(toolElement);
            });
        }

        function restartNode(nodeId) {
            fetch(`/api/nodes/${nodeId}/restart`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log('Node restart response:', data);
                })
                .catch(error => {
                    console.error('Error restarting node:', error);
                });
        }

        function stopNode(nodeId) {
            if (confirm('Are you sure you want to stop this node?')) {
                fetch(`/api/nodes/${nodeId}/stop`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Node stop response:', data);
                    })
                    .catch(error => {
                        console.error('Error stopping node:', error);
                    });
            }
        }

        // Initial data load
        fetch('/api/metrics')
            .then(response => response.json())
            .then(data => updateDashboard(data))
            .catch(error => console.error('Error loading initial data:', error));
    </script>
</body>
</html>
        """

        template_path = Path(__file__).parent / "templates" / "mcp_dashboard.html"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)

    async def get_optimal_node(self, tool_name: str) -> [MCPNode]:
        """Get the optimal node for a specific tool with intelligent load balancing"""
        available_nodes = self.resource_pool.tool_mapping.get(tool_name, [])

        if not available_nodes:
            # Create a new node if none available
            return await self.create_node_for_tool(tool_name)

        # Find the node with lowest load and highest health score
        best_node = None
        best_score = -1

        for node_name in available_nodes:
            if node_name in self.resource_pool.active_nodes:
                node = self.resource_pool.active_nodes[node_name]

                # Calculate node score based on CPU, memory, and health
                load_score = 1.0 - (node.cpu_usage / 100.0)
                memory_score = 1.0 - (node.memory_usage / 1000.0)  # Normalize memory
                health_score = node.health_score

                combined_score = (load_score * 0.4 + memory_score * 0.3 + health_score * 0.3)

                if combined_score > best_score:
                    best_score = combined_score
                    best_node = node

        # If existing nodes are overloaded, create a new one
        if best_node and best_node.cpu_usage > (self.reuse_threshold * 100):
            if len(available_nodes) < self.max_nodes_per_tool:
                return await self.create_node_for_tool(tool_name)

        return best_node

    async def create_node_for_tool(self, tool_name: str) -> [MCPNode]:
        """Create a new MCP node for a specific tool"""
        try:
            # Find available port
            port = await self.find_available_port()

            node_id = f"{tool_name}_{port}_{int(time.time())}"

            # Create node configuration
            node = MCPNode(
                name=f"{tool_name}_node_{port}",
                type="server",
                port=port,
                status="active",
                last_used=datetime.now(),
                memory_usage=0.0,
                cpu_usage=0.0,
                connections=0,
                tools=[tool_name],
                node_id=node_id,
                health_score=1.0
            )

            # Start the node process (implementation depends on MCP server type)
            process = await self.start_mcp_server(node)
            if process:
                node.process_id = process.pid

                # Register the node
                self.resource_pool.active_nodes[node_id] = node

                # Update tool mapping
                if tool_name not in self.resource_pool.tool_mapping:
                    self.resource_pool.tool_mapping[tool_name] = []
                self.resource_pool.tool_mapping[tool_name].append(node_id)

                logger.info(f"Created new MCP node: {node_id} for tool: {tool_name}")
                return node

        except Exception as e:
            logger.error(f"Failed to create node for tool {tool_name}: {e}")

        return None

    async def start_mcp_server(self, node: MCPNode) -> [subprocess.Popen]:
        """Start an MCP server process"""
        try:
            # This is a simplified implementation
            # In practice, you'd start the actual MCP server based on node configuration

            # For demonstration, we'll simulate a process
            cmd = [
                sys.executable, "-c",
                f"import time; import sys; print('MCP Server {node.name} started on port {node.port}'); time.sleep(3600)"
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a moment to ensure it starts
            await asyncio.sleep(1)

            return process

        except Exception as e:
            logger.error(f"Failed to start MCP server for node {node.name}: {e}")
            return None

    async def find_available_port(self) -> int:
        """Find an available port for a new MCP node"""
        for port in range(8900, 9000):
            if port not in [node.port for node in self.resource_pool.active_nodes.values()]:
                # Check if port is actually available
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        return port
                except OSError:
                    continue

        # Fallback to random port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            return s.getsockname()[1]

    async def monitor_resources(self):
        """Monitor system resources and node performance"""
        self.monitoring_active = True

        while self.monitoring_active:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                # Update node metrics
                for node_id, node in self.resource_pool.active_nodes.items():
                    if node.process_id:
                        try:
                            process = psutil.Process(node.process_id)
                            node.cpu_usage = process.cpu_percent()
                            node.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                            node.last_used = datetime.now()
                        except psutil.NoSuchProcess:
                            # Process has died, mark as failed
                            node.status = "error"
                            self.resource_pool.failed_nodes.add(node_id)
                            logger.warning(f"Node {node_id} process died")

                # Create system metrics
                metrics = SystemMetrics(
                    total_nodes=len(self.resource_pool.active_nodes) + len(self.resource_pool.idle_nodes),
                    active_nodes=len([n for n in self.resource_pool.active_nodes.values() if n.status == "active"]),
                    idle_nodes=len(self.resource_pool.idle_nodes),
                    failed_nodes=len(self.resource_pool.failed_nodes),
                    total_memory=memory.percent,
                    total_cpu=cpu_percent,
                    total_requests=sum(node.request_count for node in self.resource_pool.active_nodes.values()),
                    avg_response_time=sum(node.avg_response_time for node in self.resource_pool.active_nodes.values()) / max(len(self.resource_pool.active_nodes), 1),
                    uptime=time.time() - self.start_time if hasattr(self, 'start_time') else 0,
                    timestamp=datetime.now()
                )

                # Store metrics history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 1000:  # Keep last 1000 entries
                    self.metrics_history.pop(0)

                # Send to websocket clients
                await self.broadcast_metrics(metrics)

                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(10)

    async def broadcast_metrics(self, metrics: SystemMetrics):
        """Broadcast metrics to all connected websocket clients"""
        if not self.websocket_clients:
            return

        # Prepare data for broadcast
        data = {
            "total_nodes": metrics.total_nodes,
            "active_nodes": metrics.active_nodes,
            "idle_nodes": metrics.idle_nodes,
            "failed_nodes": metrics.failed_nodes,
            "total_memory": metrics.total_memory,
            "total_cpu": metrics.total_cpu,
            "total_requests": metrics.total_requests,
            "avg_response_time": metrics.avg_response_time,
            "uptime": metrics.uptime,
            "timestamp": metrics.timestamp.isoformat(),
            "nodes": [asdict(node) for node in self.resource_pool.active_nodes.values()],
            "tools": self.resource_pool.tool_mapping
        }

        message = json.dumps(data)

        # Send to all connected clients
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send_str(message)
            except Exception as e:
                disconnected_clients.add(client)

        # Remove disconnected clients
        self.websocket_clients -= disconnected_clients

    async def health_check_loop(self):
        """Periodic health check for all nodes"""
        while self.monitoring_active:
            try:
                for node_id, node in list(self.resource_pool.active_nodes.items()):
                    await self.health_check_node(node)

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)

    async def health_check_node(self, node: MCPNode):
        """Perform health check on a specific node"""
        try:
            # Check if process is still running
            if node.process_id:
                try:
                    process = psutil.Process(node.process_id)
                    if not process.is_running():
                        node.status = "error"
                        node.health_score = 0.0
                        return
                except psutil.NoSuchProcess:
                    node.status = "error"
                    node.health_score = 0.0
                    return

            # Perform a simple health check (ping the node)
            try:
                if self.session:
                    async with self.session.get(f"http://localhost:{node.port}/health", timeout=5) as response:
                        if response.status == 200:
                            node.health_score = min(1.0, node.health_score + 0.1)
                            node.status = "active"
                        else:
                            node.health_score = max(0.0, node.health_score - 0.1)
                            if node.health_score < 0.3:
                                node.status = "error"
            except Exception:
                node.health_score = max(0.0, node.health_score - 0.2)
                if node.health_score < 0.3:
                    node.status = "error"

        except Exception as e:
            logger.error(f"Error in health check for node {node.name}: {e}")
            node.status = "error"
            node.health_score = 0.0

    async def cleanup_idle_nodes(self):
        """Clean up idle nodes that haven't been used recently"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                nodes_to_remove = []

                for node_id, node in self.resource_pool.active_nodes.items():
                    # Check if node has been idle for too long
                    idle_time = (current_time - node.last_used).total_seconds()

                    if idle_time > self.idle_timeout and node.status == "idle":
                        nodes_to_remove.append(node_id)

                # Remove idle nodes
                for node_id in nodes_to_remove:
                    await self.remove_node(node_id)
                    logger.info(f"Removed idle node: {node_id}")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in cleanup idle nodes: {e}")
                await asyncio.sleep(120)

    async def remove_node(self, node_id: str):
        """Remove a node from the resource pool"""
        try:
            if node_id in self.resource_pool.active_nodes:
                node = self.resource_pool.active_nodes[node_id]

                # Stop the process
                if node.process_id:
                    try:
                        process = psutil.Process(node.process_id)
                        process.terminate()
                        process.wait(timeout=5)
                    except Exception as e:
                        logger.warning(f"Error stopping process for node {node_id}: {e}")

                # Remove from active nodes
                del self.resource_pool.active_nodes[node_id]

                # Update tool mapping
                for tool, nodes in self.resource_pool.tool_mapping.items():
                    if node_id in nodes:
                        nodes.remove(node_id)

                # Remove from load balancer
                if node_id in self.resource_pool.load_balancer:
                    del self.resource_pool.load_balancer[node_id]

                logger.info(f"Successfully removed node: {node_id}")

        except Exception as e:
            logger.error(f"Error removing node {node_id}: {e}")

    # Web handlers
    async def dashboard_handler(self, request):
        """Serve the main dashboard"""
        return aiohttp.web.Response(
            text=open(Path(__file__).parent / "templates" / "mcp_dashboard.html").read(),
            content_type="text/html"
        )

    async def metrics_handler(self, request):
        """API endpoint for current metrics"""
        if self.metrics_history:
            latest_metrics = self.metrics_history[-1]
            data = {
                "total_nodes": latest_metrics.total_nodes,
                "active_nodes": latest_metrics.active_nodes,
                "idle_nodes": latest_metrics.idle_nodes,
                "failed_nodes": latest_metrics.failed_nodes,
                "total_memory": latest_metrics.total_memory,
                "total_cpu": latest_metrics.total_cpu,
                "total_requests": latest_metrics.total_requests,
                "avg_response_time": latest_metrics.avg_response_time,
                "uptime": latest_metrics.uptime,
                "timestamp": latest_metrics.timestamp.isoformat(),
                "nodes": [asdict(node) for node in self.resource_pool.active_nodes.values()],
                "tools": self.resource_pool.tool_mapping
            }
        else:
            data = {"error": "No metrics available"}

        return web.json_response(data)

    async def nodes_handler(self, request):
        """API endpoint for node information"""
        nodes_data = []
        for node in self.resource_pool.active_nodes.values():
            nodes_data.append(asdict(node))

        return web.json_response({"nodes": nodes_data})

    async def restart_node_handler(self, request):
        """API endpoint to restart a specific node"""
        node_id = request.match_info['node_id']

        if node_id in self.resource_pool.active_nodes:
            node = self.resource_pool.active_nodes[node_id]

            # Stop the current process
            if node.process_id:
                try:
                    process = psutil.Process(node.process_id)
                    process.terminate()
                    process.wait(timeout=5)
                except Exception as e:
                    logger.warning(f"Error stopping process for node {node_id}: {e}")

            # Start a new process
            new_process = await self.start_mcp_server(node)
            if new_process:
                node.process_id = new_process.pid
                node.status = "active"
                node.health_score = 1.0
                return web.json_response({"success": True, "message": f"Node {node_id} restarted"})
            else:
                return web.json_response({"success": False, "message": "Failed to restart node"})

        return web.json_response({"success": False, "message": "Node not found"})

    async def stop_node_handler(self, request):
        """API endpoint to stop a specific node"""
        node_id = request.match_info['node_id']

        if node_id in self.resource_pool.active_nodes:
            await self.remove_node(node_id)
            return web.json_response({"success": True, "message": f"Node {node_id} stopped"})

        return web.json_response({"success": False, "message": "Node not found"})

    async def tools_handler(self, request):
        """API endpoint for tool registry"""
        return web.json_response({"tools": self.resource_pool.tool_mapping})

    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websocket_clients.add(ws)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle websocket messages if needed
                    pass
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    break
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.websocket_clients.discard(ws)

        return ws

    async def start_server(self, host='localhost', port=8891):
        """Start the MCP resource manager server"""
        self.start_time = time.time()

        # Create static directory
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"🚀 MCP Resource Manager running at http://{host}:{port}")
        logger.info(f"🌐 Dashboard: http://{host}:{port}")
        logger.info(f"📊 API: http://{host}:{port}/api/metrics")

        return runner

    async def shutdown(self):
        """Shutdown the resource manager"""
        logger.info("Shutting down MCP Resource Manager...")

        self.monitoring_active = False

        # Stop all nodes
        for node_id in list(self.resource_pool.active_nodes.keys()):
            await self.remove_node(node_id)

        # Close HTTP session
        if self.session:
            await self.session.close()

        logger.info("MCP Resource Manager shutdown complete")

async def main():
    """Main function to run the MCP Resource Manager"""
    manager = MCPResourceManager()

    try:
        await manager.initialize()

        # Start the web server
        runner = await manager.start_server()

        # Create some demo nodes
        demo_tools = ["brave-search", "github", "filesystem", "memory", "browser"]
        for tool in demo_tools:
            await manager.create_node_for_tool(tool)

        logger.info("🎯 MCP Resource Manager is running with demo nodes!")
        logger.info("🔧 Visit http://localhost:8891 to access the dashboard")

        # Keep running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Received shutdown signal...")

    except Exception as e:
        logger.error(f"Error running MCP Resource Manager: {e}")
    finally:
        await manager.shutdown()
        if 'runner' in locals():
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
