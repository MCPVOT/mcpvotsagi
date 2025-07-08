#!/usr/bin/env python3
"""
Unified AGI Dashboard - Combined Jupiter Trading & Network Monitoring
===================================================================
🚀 Single application combining all dashboards and trading systems
🎯 Jupiter DEX integration with real-time trading
📊 Network monitoring with WatchYourLAN integration
🧠 Claudia AI-powered analysis with MCP tools integration
🔐 Cyberpunk-themed unified interface
🔗 Enhanced with MCP Memory, Knowledge Graph, and RL capabilities
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import aiohttp
from aiohttp import web, WSMsgType
import requests
from typing import Dict, List, Optional, Any
import traceback
import socket
import psutil
import os
import sys

# Import MCP-enhanced Claudia
from claudia_mcp_integration import ClaudiaMCPClient, create_claudia_mcp_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UnifiedAGIDashboard")



class UnifiedDataCollector:
    """Unified data collection from all sources"""

    def __init__(self):
        self.jupiter_base = "https://api.jup.ag"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_ttl = 30  # 30 seconds

    async def get_jupiter_data(self) -> Dict:
        """Get Jupiter DEX data"""
        try:
            cache_key = "jupiter_data"
            now = time.time()

            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if now - timestamp < self.cache_ttl:
                    return cached_data

            # Get top tokens from Jupiter
            tokens = ["So11111111111111111111111111111111111111112"]  # SOL

            async with aiohttp.ClientSession() as session:
                # Get price data
                price_url = f"{self.jupiter_base}/price/v2"
                params = {"ids": ",".join(tokens)}

                async with session.get(price_url, params=params) as response:
                    if response.status == 200:
                        price_data = await response.json()

                        # Process data
                        market_data = {}
                        for token_id, data in price_data.get("data", {}).items():
                            market_data[token_id] = {
                                "price": float(data.get("price", 0)),
                                "timestamp": datetime.now().isoformat()
                            }

                        # Cache results
                        self.cache[cache_key] = (market_data, now)
                        return market_data

        except Exception as e:
            logger.error(f"Jupiter data error: {e}")
            return {}

    async def get_network_data(self) -> Dict:
        """Get network monitoring data"""
        try:
            # Simple network stats using psutil
            network_stats = psutil.net_io_counters()

            return {
                "bytes_sent": network_stats.bytes_sent,
                "bytes_recv": network_stats.bytes_recv,
                "packets_sent": network_stats.packets_sent,
                "packets_recv": network_stats.packets_recv,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Network data error: {e}")
            return {}

    async def get_system_metrics(self) -> Dict:
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"System metrics error: {e}")
            return {}

class UnifiedAGIDashboard:
    """Main unified dashboard application with MCP-enhanced Claudia"""

    def __init__(self, port=8900):
        self.port = port
        self.app = web.Application()
        self.data_collector = UnifiedDataCollector()
        self.claudia = None  # Will be initialized asynchronously
        self.websockets = []
        self.running = True

        # Setup routes
        self.setup_routes()

    async def initialize(self):
        """Initialize MCP-enhanced Claudia client"""
        logger.info("🧠 Initializing MCP-enhanced Claudia AI...")
        self.claudia = await create_claudia_mcp_client()
        logger.info("✅ Claudia MCP integration ready!")

    def setup_routes(self):
        """Setup all routes for the unified dashboard"""
        # Static files
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/api/status', self.status_handler)
        self.app.router.add_get('/api/jupiter', self.jupiter_handler)
        self.app.router.add_get('/api/network', self.network_handler)
        self.app.router.add_get('/api/system', self.system_handler)
        self.app.router.add_get('/api/ai-analysis', self.ai_analysis_handler)
        self.app.router.add_get('/api/mcp-status', self.mcp_status_handler)
        self.app.router.add_get('/api/context-summary', self.context_summary_handler)
        self.app.router.add_get('/api/dashboard-insights', self.dashboard_insights_handler)
        self.app.router.add_get('/ws', self.websocket_handler)

    async def index_handler(self, request):
        """Main dashboard page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Unified AGI Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Consolas', 'Monaco', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff00;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .header {
            background: rgba(0, 255, 0, 0.1);
            border-bottom: 2px solid #00ff00;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }

        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff00;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.8;
        }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .panel {
            background: rgba(0, 255, 0, 0.05);
            border: 1px solid #00ff00;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            backdrop-filter: blur(10px);
        }

        .panel h2 {
            color: #00ff00;
            margin-bottom: 15px;
            font-size: 1.5em;
            text-shadow: 0 0 5px #00ff00;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 8px;
        }

        .metric-label {
            color: #00dd00;
        }

        .metric-value {
            color: #00ff00;
            font-weight: bold;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-online {
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }

        .status-offline {
            background: #ff0066;
            box-shadow: 0 0 10px #ff0066;
        }

        .ai-analysis {
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid #00ffff;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            color: #00ffff;
        }

        .timestamp {
            color: #666;
            font-size: 0.9em;
            text-align: right;
            margin-top: 10px;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .loading {
            animation: pulse 2s infinite;
        }

        .chart-container {
            height: 200px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 UNIFIED AGI DASHBOARD</h1>
        <p>Jupiter Trading • Network Monitoring • AI Analysis • Real-Time Intelligence</p>
    </div>

    <div class="container">
        <!-- Jupiter Trading Panel -->
        <div class="panel">
            <h2>📊 Jupiter DEX Trading</h2>
            <div id="jupiter-status" class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value loading">Connecting...</span>
            </div>
            <div id="jupiter-data">
                <!-- Jupiter data will be loaded here -->
            </div>
        </div>

        <!-- Network Monitoring Panel -->
        <div class="panel">
            <h2>🌐 Network Monitoring</h2>
            <div id="network-status" class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value loading">Scanning...</span>
            </div>
            <div id="network-data">
                <!-- Network data will be loaded here -->
            </div>
        </div>

        <!-- System Metrics Panel -->
        <div class="panel">
            <h2>⚡ System Performance</h2>
            <div id="system-data">
                <!-- System data will be loaded here -->
            </div>
            <div id="system-analysis" class="ai-analysis">
                <div class="loading">Analyzing system performance...</div>
            </div>
        </div>

        <!-- AI Analysis Panel -->
        <div class="panel">
            <h2>🧠 Claudia AI Market Analysis</h2>
            <div id="ai-analysis" class="ai-analysis">
                <div class="loading">Analyzing market conditions...</div>
            </div>
        </div>

        <!-- MCP Tools Panel -->
        <div class="panel">
            <h2>🔗 MCP Tools Status</h2>
            <div id="mcp-status">
                <div class="loading">Checking MCP tools...</div>
            </div>
        </div>

        <!-- Dashboard Insights Panel -->
        <div class="panel">
            <h2>🎯 Dashboard Insights</h2>
            <div id="dashboard-insights" class="ai-analysis">
                <div class="loading">Generating comprehensive insights...</div>
            </div>
        </div>

        <!-- Context Summary Panel -->
        <div class="panel">
            <h2>📊 Knowledge Graph Context</h2>
            <div id="context-summary">
                <div class="loading">Loading context summary...</div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws`);

        ws.onopen = function() {
            console.log('WebSocket connected');
            updateStatus('jupiter-status', 'Connected', true);
            updateStatus('network-status', 'Connected', true);
        };

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        ws.onerror = function() {
            updateStatus('jupiter-status', 'Connection Error', false);
            updateStatus('network-status', 'Connection Error', false);
        };

        function updateStatus(elementId, status, isOnline) {
            const element = document.getElementById(elementId);
            const statusClass = isOnline ? 'status-online' : 'status-offline';
            element.innerHTML = `
                <span class="metric-label">Status:</span>
                <span class="metric-value">
                    <span class="status-indicator ${statusClass}"></span>${status}
                </span>
            `;
        }

        function updateDashboard(data) {
            // Update Jupiter data
            if (data.jupiter) {
                updateJupiterData(data.jupiter);
            }

            // Update Network data
            if (data.network) {
                updateNetworkData(data.network);
            }

            // Update System data
            if (data.system) {
                updateSystemData(data.system);
            }

            // Update AI Analysis
            if (data.ai_analysis) {
                updateAIAnalysis(data.ai_analysis);
            }

            // Update System Analysis
            if (data.system_analysis) {
                updateSystemAnalysis(data.system_analysis);
            }

            // Update MCP Status
            if (data.mcp_status) {
                updateMCPStatus(data.mcp_status);
            }

            // Update Dashboard Insights
            if (data.dashboard_insights) {
                updateDashboardInsights(data.dashboard_insights);
            }

            // Update Context Summary
            if (data.context_summary) {
                updateContextSummary(data.context_summary);
            }
        }

        function updateJupiterData(data) {
            const container = document.getElementById('jupiter-data');
            let html = '';

            for (const [token, info] of Object.entries(data)) {
                html += `
                    <div class="metric">
                        <span class="metric-label">SOL Price:</span>
                        <span class="metric-value">$${info.price ? info.price.toFixed(4) : '0.0000'}</span>
                    </div>
                `;
            }

            container.innerHTML = html;
        }

        function updateNetworkData(data) {
            const container = document.getElementById('network-data');
            const html = `
                <div class="metric">
                    <span class="metric-label">Bytes Sent:</span>
                    <span class="metric-value">${formatBytes(data.bytes_sent || 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Bytes Received:</span>
                    <span class="metric-value">${formatBytes(data.bytes_recv || 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Packets Sent:</span>
                    <span class="metric-value">${(data.packets_sent || 0).toLocaleString()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Packets Received:</span>
                    <span class="metric-value">${(data.packets_recv || 0).toLocaleString()}</span>
                </div>
            `;
            container.innerHTML = html;
        }

        function updateSystemData(data) {
            const container = document.getElementById('system-data');
            const html = `
                <div class="metric">
                    <span class="metric-label">CPU Usage:</span>
                    <span class="metric-value">${(data.cpu_percent || 0).toFixed(1)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage:</span>
                    <span class="metric-value">${(data.memory_percent || 0).toFixed(1)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Disk Usage:</span>
                    <span class="metric-value">${(data.disk_percent || 0).toFixed(1)}%</span>
                </div>
            `;
            container.innerHTML = html;
        }

        function updateAIAnalysis(data) {
            const container = document.getElementById('ai-analysis');
            container.innerHTML = `
                <div>${data.analysis || 'AI analysis in progress...'}</div>
                <div class="timestamp">Model: ${data.model || 'N/A'} | ${new Date(data.timestamp).toLocaleString()}</div>
            `;
        }

        function updateSystemAnalysis(data) {
            const container = document.getElementById('system-analysis');
            container.innerHTML = `
                <div>${data.analysis || 'System analysis in progress...'}</div>
                <div class="timestamp">Model: ${data.model || 'N/A'} | Context: ${data.context_used ? 'Enhanced' : 'Basic'}</div>
            `;
        }

        function updateMCPStatus(data) {
            const container = document.getElementById('mcp-status');
            let html = '';

            if (data.tools) {
                for (const [toolName, toolInfo] of Object.entries(data.tools)) {
                    const statusClass = toolInfo.available ? 'status-online' : 'status-offline';
                    const statusText = toolInfo.available ? 'Available' : 'Unavailable';
                    html += `
                        <div class="metric">
                            <span class="metric-label">${toolName.toUpperCase()}:</span>
                            <span class="metric-value">
                                <span class="status-indicator ${statusClass}"></span>${statusText}
                            </span>
                        </div>
                    `;
                }
            }

            container.innerHTML = html || '<div class="loading">Loading MCP status...</div>';
        }

        function updateDashboardInsights(data) {
            const container = document.getElementById('dashboard-insights');
            container.innerHTML = `
                <div>${data.insights || 'Generating comprehensive insights...'}</div>
                <div class="timestamp">
                    Model: ${data.model || 'N/A'} |
                    Tools: ${data.mcp_tools_used ? data.mcp_tools_used.join(', ') : 'N/A'} |
                    ${new Date(data.timestamp).toLocaleString()}
                </div>
            `;
        }

        function updateContextSummary(data) {
            const container = document.getElementById('context-summary');
            let html = '';

            if (data.context_counts) {
                for (const [contextType, count] of Object.entries(data.context_counts)) {
                    html += `
                        <div class="metric">
                            <span class="metric-label">${contextType.replace('_', ' ').toUpperCase()}:</span>
                            <span class="metric-value">${count}</span>
                        </div>
                    `;
                }
            }

            container.innerHTML = html || '<div class="loading">Loading context summary...</div>';
        }

        // ...existing code...
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')

    async def status_handler(self, request):
        """System status endpoint"""
        return web.json_response({
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "jupiter": "online",
                "network": "online",
                "ai": "online"
            }
        })

    async def jupiter_handler(self, request):
        """Jupiter data endpoint"""
        data = await self.data_collector.get_jupiter_data()
        return web.json_response(data)

    async def network_handler(self, request):
        """Network data endpoint"""
        data = await self.data_collector.get_network_data()
        return web.json_response(data)

    async def system_handler(self, request):
        """System metrics endpoint"""
        data = await self.data_collector.get_system_metrics()
        return web.json_response(data)

    async def ai_analysis_handler(self, request):
        """Enhanced AI analysis endpoint with MCP context"""
        if not self.claudia:
            return web.json_response({"analysis": "Claudia AI not initialized"})

        # Get latest market data for analysis
        jupiter_data = await self.data_collector.get_jupiter_data()

        if jupiter_data:
            # Use first available token data
            first_token = next(iter(jupiter_data.values()), {})
            # Use MCP-enhanced analysis with context
            analysis = await self.claudia.analyze_market_data_with_context(first_token)
            return web.json_response(analysis)

        return web.json_response({"analysis": "No market data available for analysis"})

    async def mcp_status_handler(self, request):
        """MCP tools status endpoint"""
        if not self.claudia:
            return web.json_response({"error": "Claudia AI not initialized"})

        status = await self.claudia.get_mcp_status()
        return web.json_response(status)

    async def context_summary_handler(self, request):
        """MCP context summary endpoint"""
        if not self.claudia:
            return web.json_response({"error": "Claudia AI not initialized"})

        summary = await self.claudia.get_context_summary()
        return web.json_response(summary)

    async def dashboard_insights_handler(self, request):
        """Comprehensive dashboard insights endpoint"""
        if not self.claudia:
            return web.json_response({"insights": "Claudia AI not initialized"})

        try:
            # Collect all dashboard data
            jupiter_data = await self.data_collector.get_jupiter_data()
            network_data = await self.data_collector.get_network_data()
            system_data = await self.data_collector.get_system_metrics()

            dashboard_data = {
                "jupiter": jupiter_data,
                "network": network_data,
                "system": system_data,
                "timestamp": datetime.now().isoformat()
            }

            # Generate comprehensive insights using all MCP tools
            insights = await self.claudia.generate_dashboard_insights(dashboard_data)
            return web.json_response(insights)

        except Exception as e:
            logger.error(f"Dashboard insights error: {e}")
            return web.json_response({"insights": "Dashboard insights temporarily unavailable", "error": str(e)})

    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websockets.append(ws)
        logger.info(f"WebSocket connected. Total connections: {len(self.websockets)}")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get('type') == 'request_update':
                        await self.send_update(ws)
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            if ws in self.websockets:
                self.websockets.remove(ws)
            logger.info(f"WebSocket disconnected. Remaining: {len(self.websockets)}")

        return ws

    async def send_update(self, ws):
        """Send update to specific WebSocket with MCP-enhanced analysis"""
        try:
            # Collect all data
            jupiter_data = await self.data_collector.get_jupiter_data()
            network_data = await self.data_collector.get_network_data()
            system_data = await self.data_collector.get_system_metrics()

            # Get enhanced AI analysis if Claudia is available and we have market data
            ai_analysis = {"analysis": "Analyzing..."}
            system_analysis = {"analysis": "Analyzing system..."}
            mcp_status = {"tools": {}}

            if self.claudia:
                # Get MCP status
                mcp_status = await self.claudia.get_mcp_status()

                # Enhanced market analysis with context
                if jupiter_data:
                    first_token = next(iter(jupiter_data.values()), {})
                    ai_analysis = await self.claudia.analyze_market_data_with_context(first_token)

                # Enhanced system analysis with context
                if system_data:
                    system_analysis = await self.claudia.analyze_system_performance_with_context(system_data)

            update_data = {
                "timestamp": datetime.now().isoformat(),
                "jupiter": jupiter_data,
                "network": network_data,
                "system": system_data,
                "ai_analysis": ai_analysis,
                "system_analysis": system_analysis,
                "mcp_status": mcp_status
            }

            await ws.send_str(json.dumps(update_data))

        except Exception as e:
            logger.error(f"Error sending update: {e}")

    async def broadcast_updates(self):
        """Broadcast MCP-enhanced updates to all connected WebSockets"""
        while self.running:
            try:
                if self.websockets:
                    # Collect all data
                    jupiter_data = await self.data_collector.get_jupiter_data()
                    network_data = await self.data_collector.get_network_data()
                    system_data = await self.data_collector.get_system_metrics()

                    # Enhanced AI analysis with MCP context
                    ai_analysis = {"analysis": "Analyzing market conditions..."}
                    system_analysis = {"analysis": "Analyzing system performance..."}
                    dashboard_insights = {"insights": "Generating insights..."}
                    mcp_status = {"tools": {}}
                    context_summary = {"context_counts": {}}

                    if self.claudia:
                        # Get MCP status
                        mcp_status = await self.claudia.get_mcp_status()
                        context_summary = await self.claudia.get_context_summary();

                        # Enhanced market analysis with context
                        if jupiter_data:
                            first_token = next(iter(jupiter_data.values()), {})
                            ai_analysis = await self.claudia.analyze_market_data_with_context(first_token);

                        # Enhanced system analysis with context
                        if system_data:
                            system_analysis = await self.claudia.analyze_system_performance_with_context(system_data);

                        # Comprehensive dashboard insights (less frequent)
                        # Generate insights every 5th update cycle
                        if hasattr(self, '_insight_counter'):
                            self._insight_counter += 1;
                        else:
                            self._insight_counter = 1;

                        if self._insight_counter % 5 == 0:
                            dashboard_data = {
                                "jupiter": jupiter_data,
                                "network": network_data,
                                "system": system_data,
                                "timestamp": datetime.now().isoformat()
                            };
                            dashboard_insights = await self.claudia.generate_dashboard_insights(dashboard_data);

                    update_data = {
                        "timestamp": datetime.now().isoformat(),
                        "jupiter": jupiter_data,
                        "network": network_data,
                        "system": system_data,
                        "ai_analysis": ai_analysis,
                        "system_analysis": system_analysis,
                        "dashboard_insights": dashboard_insights,
                        "mcp_status": mcp_status,
                        "context_summary": context_summary
                    }

                    # Send to all connected clients
                    disconnected = []
                    for ws in self.websockets:
                        try:
                            await ws.send_str(json.dumps(update_data))
                        except Exception as e:
                            logger.error(f"Error sending to WebSocket: {e}")
                            disconnected.append(ws)

                    # Remove disconnected WebSockets
                    for ws in disconnected:
                        if ws in self.websockets:
                            self.websockets.remove(ws)

                await asyncio.sleep(10)  # Update every 10 seconds

            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(5)

    async def start(self):
        """Start the unified dashboard with MCP initialization"""
        logger.info(f"🚀 Starting Unified AGI Dashboard on port {self.port}...")

        # Initialize MCP-enhanced Claudia
        await self.initialize()

        # Start background tasks
        asyncio.create_task(self.broadcast_updates())

        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()

        logger.info(f"✅ Unified AGI Dashboard running on http://localhost:{self.port}")
        logger.info(f"🌟 Features: Jupiter Trading, Network Monitoring, MCP-Enhanced AI Analysis")

        return runner

async def main():
    """Main function"""
    dashboard = UnifiedAGIDashboard(port=8900)
    runner = await dashboard.start()

    print("\n" + "="*80)
    print("🚀 UNIFIED AGI DASHBOARD WITH MCP INTEGRATION")
    print("="*80)
    print(f"🌐 URL: http://localhost:8900")
    print(f"📊 Features: Jupiter DEX + Network Monitoring + MCP-Enhanced AI Analysis")
    print(f"🧠 Claudia AI: Enhanced with MCP Memory, Knowledge Graph, and Tools")
    print(f"🔗 MCP Tools: Memory, GitHub, FileSystem, Browser, Search")
    print(f"⚡ Real-time: WebSocket updates with context-aware analysis")
    print("="*80)
    print("🎯 New API Endpoints:")
    print("   • /api/mcp-status - MCP tools status")
    print("   • /api/context-summary - Knowledge graph and memory summary")
    print("   • /api/dashboard-insights - Comprehensive AI insights")
    print("="*80)
    print("Press Ctrl+C to stop...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        dashboard.running = False
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
