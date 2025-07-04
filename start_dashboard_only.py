#!/usr/bin/env python3
"""
Oracle AGI V5 - Dashboard Only Mode
==================================
Starts just the unified dashboard with mock data for testing
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from aiohttp import web
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DashboardOnly")

class MockOracleAGIDashboard:
    """Mock version of Oracle AGI Dashboard for testing"""
    
    def __init__(self):
        self.workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
        self.workspace.mkdir(exist_ok=True)
        
    async def start(self):
        """Start dashboard with mock data"""
        logger.info("🚀 Starting Oracle AGI V5 Dashboard (Mock Mode)...")
        
        app = web.Application()
        
        # Configure routes
        app.router.add_get('/', self.handle_index)
        app.router.add_get('/api/status', self.handle_mock_status)
        app.router.add_get('/api/trading/signals', self.handle_mock_signals)
        app.router.add_post('/api/chat', self.handle_mock_chat)
        app.router.add_get('/api/metrics', self.handle_mock_metrics)
        app.router.add_get('/ws', self.handle_websocket)
        
        # Serve static files
        static_path = self.workspace / 'static'
        static_path.mkdir(exist_ok=True)
        
        # Create the dashboard HTML if it doesn't exist
        await self._create_dashboard_html()
        
        app.router.add_static('/', static_path)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 3002)
        await site.start()
        
        logger.info("✅ Dashboard started successfully!")
        logger.info("🌐 Access the dashboard at: http://localhost:3002")
        logger.info("📝 This is running in MOCK MODE - no real services required")
        logger.info("Press Ctrl+C to stop")
        
        # Keep running
        await asyncio.Event().wait()
        
    async def handle_index(self, request):
        """Serve the main dashboard"""
        html_path = self.workspace / 'static' / 'index.html'
        if html_path.exists():
            return web.FileResponse(html_path)
        else:
            return web.Response(text="Dashboard HTML not found. Creating...", status=404)
            
    async def handle_mock_status(self, request):
        """Return mock system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'services': {
                'oracle_agi_core': {
                    'name': 'Oracle AGI Core',
                    'healthy': True,
                    'port': 8888
                },
                'trilogy_brain': {
                    'name': 'Trilogy Oracle Brain',
                    'healthy': True,
                    'port': 8887
                },
                'dgm_voltagents': {
                    'name': 'DGM Voltagents',
                    'healthy': random.choice([True, False]),
                    'port': 8886
                },
                'trading_system': {
                    'name': 'Trading System',
                    'healthy': True,
                    'port': 8889
                },
                'deepseek': {
                    'name': 'DeepSeek R1',
                    'healthy': random.choice([True, False]),
                    'port': 11434
                },
                'gemini_cli': {
                    'name': 'Gemini CLI',
                    'healthy': True,
                    'port': 8080
                }
            },
            'ai_models': {
                'gemini': {
                    'name': 'Gemini 2.5',
                    'capabilities': ['reasoning', 'code', 'analysis'],
                    'available': True
                },
                'deepseek': {
                    'name': 'DeepSeek R1',
                    'capabilities': ['trading', 'patterns', 'optimization'],
                    'available': True
                },
                'claude': {
                    'name': 'Claude 3.7',
                    'capabilities': ['agents', 'workflows', 'integration'],
                    'available': True
                },
                'gpt4': {
                    'name': 'GPT-4 Turbo',
                    'capabilities': ['general', 'creative', 'planning'],
                    'available': True
                }
            },
            'performance': {
                'success_rate': 94.2 + random.uniform(-2, 2),
                'avg_confidence': 0.87 + random.uniform(-0.05, 0.05),
                'decisions_per_day': 147 + random.randint(-10, 10),
                'active_models': 5
            }
        }
        return web.json_response(status)
        
    async def handle_mock_signals(self, request):
        """Return mock trading signals"""
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT']
        actions = ['BUY', 'SELL', 'HOLD']
        
        signals = []
        for i in range(10):
            symbol = random.choice(symbols)
            action = random.choice(actions)
            base_price = {
                'BTC/USDT': 95000,
                'ETH/USDT': 3200,
                'SOL/USDT': 180,
                'ADA/USDT': 1.2,
                'DOT/USDT': 7.5
            }[symbol]
            
            signals.append({
                'symbol': symbol,
                'action': action,
                'confidence': random.uniform(0.6, 0.95),
                'consensus': f"{random.choice(['Strong', 'Moderate', 'Weak'])} consensus from {random.randint(3, 5)} models",
                'entry': base_price * random.uniform(0.98, 1.02),
                'stop_loss': base_price * 0.95,
                'take_profit': base_price * 1.05,
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat()
            })
            
        return web.json_response({'signals': signals})
        
    async def handle_mock_chat(self, request):
        """Handle mock chat requests"""
        data = await request.json()
        message = data.get('message', '')
        model = data.get('model', 'gemini')
        
        # Generate mock response based on model
        responses = {
            'gemini': f"[Gemini] Analyzing your query: '{message}'. Based on current market conditions, I recommend a cautious approach with focus on risk management.",
            'deepseek': f"[DeepSeek] Pattern analysis for '{message}' shows 87% correlation with historical bull patterns. Consider DCA strategy.",
            'claude': f"[Claude] I've created a workflow to address '{message}'. The multi-agent system suggests diversification across 3-5 assets.",
            'gpt4': f"[GPT-4] Regarding '{message}', here's a comprehensive analysis: Market sentiment is bullish with key support levels holding."
        }
        
        response = {
            'model': model,
            'response': responses.get(model, f"[{model}] Processing: {message}"),
            'timestamp': datetime.now().isoformat()
        }
        
        return web.json_response(response)
        
    async def handle_mock_metrics(self, request):
        """Return mock performance metrics"""
        metrics = []
        
        metric_types = ['accuracy', 'latency', 'throughput', 'consensus_rate']
        components = ['oracle_core', 'trading_system', 'ai_models', 'mcp_tools']
        
        for _ in range(20):
            metrics.append({
                'type': random.choice(metric_types),
                'value': random.uniform(0.5, 1.0) if 'rate' in metric_types else random.uniform(10, 100),
                'component': random.choice(components),
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat()
            })
            
        return web.json_response({'metrics': metrics})
        
    async def handle_websocket(self, request):
        """Handle WebSocket connections with mock data"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        try:
            # Send initial connection message
            await ws.send_json({
                'type': 'connected',
                'message': 'Connected to Oracle AGI V5 (Mock Mode)'
            })
            
            # Start sending periodic updates
            async def send_updates():
                while not ws.closed:
                    await ws.send_json({
                        'type': 'system_update',
                        'timestamp': datetime.now().isoformat(),
                        'data': {
                            'cpu_usage': random.uniform(20, 80),
                            'memory_usage': random.uniform(30, 70),
                            'active_connections': random.randint(5, 20)
                        }
                    })
                    await asyncio.sleep(5)
                    
            update_task = asyncio.create_task(send_updates())
            
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get('type') == 'ping':
                        await ws.send_json({'type': 'pong'})
                        
            update_task.cancel()
            
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            
        return ws
        
    async def _create_dashboard_html(self):
        """Create the dashboard HTML file"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle AGI V5 - Dashboard (Mock Mode)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulse { animation: pulse 2s infinite; }
        .cyber-grid {
            background-image: 
                linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
        }
    </style>
</head>
<body class="bg-gray-900 text-white cyber-grid">
    <div class="container mx-auto p-6">
        <div class="text-center mb-8">
            <h1 class="text-5xl font-bold mb-2 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                🔮 Oracle AGI V5
            </h1>
            <p class="text-xl text-gray-400">Mock Mode - Testing Dashboard</p>
            <p class="text-sm text-yellow-500 mt-2">⚠️ Running with simulated data</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 class="text-lg font-semibold mb-2">System Status</h3>
                <div class="flex items-center">
                    <div class="w-3 h-3 bg-green-500 rounded-full pulse mr-2"></div>
                    <span>All Systems Operational</span>
                </div>
            </div>
            
            <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 class="text-lg font-semibold mb-2">Active Models</h3>
                <div class="text-2xl font-bold text-green-400">5/5</div>
            </div>
            
            <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 class="text-lg font-semibold mb-2">Success Rate</h3>
                <div class="text-2xl font-bold text-blue-400">94.2%</div>
            </div>
            
            <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 class="text-lg font-semibold mb-2">Decisions/Day</h3>
                <div class="text-2xl font-bold text-yellow-400">147</div>
            </div>
        </div>
        
        <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 class="text-2xl font-bold mb-4">📊 Mock Data Dashboard</h2>
            <p class="text-gray-400 mb-4">
                This dashboard is running in mock mode. All data shown is simulated for testing purposes.
            </p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <h3 class="text-xl font-semibold mb-2">✅ Available Features</h3>
                    <ul class="list-disc list-inside text-gray-300">
                        <li>System status monitoring</li>
                        <li>Trading signal simulation</li>
                        <li>AI chat interface (mock responses)</li>
                        <li>Performance metrics</li>
                        <li>WebSocket real-time updates</li>
                    </ul>
                </div>
                <div>
                    <h3 class="text-xl font-semibold mb-2">🚀 Next Steps</h3>
                    <ul class="list-disc list-inside text-gray-300">
                        <li>Start full system: <code class="bg-gray-700 px-2 py-1 rounded">python launch_oracle_agi_v5.py</code></li>
                        <li>Run system test: <code class="bg-gray-700 px-2 py-1 rounded">python test_oracle_agi_v5.py</code></li>
                        <li>Check the README for complete setup</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="mt-8 text-center text-gray-500">
            <p>Oracle AGI V5 - Mock Dashboard | <a href="https://github.com/kabrony/MCPVots" class="text-blue-400 hover:underline">GitHub</a></p>
        </div>
    </div>
    
    <script>
        // Simple WebSocket connection for testing
        const ws = new WebSocket('ws://localhost:3002/ws');
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            ws.send(JSON.stringify({ type: 'ping' }));
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('WebSocket message:', data);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        // Auto-refresh data
        setInterval(() => {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => console.log('Status update:', data))
                .catch(err => console.error('Status fetch error:', err));
        }, 5000);
    </script>
</body>
</html>'''
        
        # Save HTML file
        html_path = self.workspace / 'static' / 'index.html'
        html_path.parent.mkdir(exist_ok=True)
        
        with open(html_path, 'w') as f:
            f.write(html_content)
            
        logger.info("✓ Dashboard HTML created")

async def main():
    """Main entry point"""
    dashboard = MockOracleAGIDashboard()
    await dashboard.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nDashboard stopped by user")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise