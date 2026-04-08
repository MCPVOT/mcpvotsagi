#!/usr/bin/env python3
"""
Ultimate Trading Dashboard V3 - Fixed Version
=============================================
🚀 Real-time trading dashboard with Unicode-safe logging
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Set
import traceback

# Web framework
try:
    from aiohttp import web, WSMsgType
    import aiohttp_cors
    import jinja2
    import aiohttp_jinja2
    HAS_WEB_DEPS = True
except ImportError:
    HAS_WEB_DEPS = False

# Import our components
try:
    from ultimate_trading_system_v3 import UltimateTradingSystemV3
    from jupiter_rl_integration import JupiterRLIntegration
    from jupiter_api_wrapper import JupiterAPIWrapper
    HAS_TRADING_COMPONENTS = True
except ImportError as e:
    logging.warning(f"Trading components not available: {e}")
    HAS_TRADING_COMPONENTS = False

# Configure Unicode-safe logging
class UnicodeStreamHandler(logging.StreamHandler):
    """Custom stream handler that handles Unicode characters safely"""

    def emit(self, record):
        try:
            if hasattr(record, 'msg'):
                record.msg = self._make_safe(str(record.msg))
            super().emit(record)
        except UnicodeEncodeError:
            record.msg = self._ascii_safe(str(record.msg))
            super().emit(record)

    def _make_safe(self, text):
        """Replace emojis with safe equivalents"""
        replacements = {
            '🚀': '[ROCKET]', '📁': '[FOLDER]', '🔍': '[SEARCH]', '🪐': '[PLANET]',
            '✅': '[OK]', '❌': '[ERROR]', '🔧': '[TOOLS]', '📊': '[CHART]',
            '🧠': '[BRAIN]', '💰': '[MONEY]', '📈': '[STATS]', '🎨': '[ART]',
            '🌐': '[WEB]', '🔗': '[LINK]', '⚡': '[BOLT]', '🔄': '[REFRESH]'
        }
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
        return text

    def _ascii_safe(self, text):
        """Remove non-ASCII characters as last resort"""
        return ''.join(char for char in text if ord(char) < 128)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('F:/ULTIMATE_AGI_DATA/RL_TRADING/dashboard.log', encoding='utf-8'),
        UnicodeStreamHandler()
    ]
)
logger = logging.getLogger("TradingDashboard")

class UltimateTradingDashboard:
    """Advanced trading dashboard with real-time updates and AI integration"""

    def __init__(self, port: int = 8050, host: str = 'localhost'):
        self.port = port
        self.host = host
        self.app = None
        self.websocket_clients: Set = set()
        self.start_time = None
        self.f_drive_path = "F:/ULTIMATE_AGI_DATA/RL_TRADING/"

        # Create required directories
        self.static_dir = os.path.join(self.f_drive_path, "dashboard_static")
        self.templates_dir = os.path.join(self.f_drive_path, "dashboard_templates")
        self._create_directories()

        # Initialize trading components
        self.trading_system = UltimateTradingSystemV3() if HAS_TRADING_COMPONENTS else None
        self.jupiter_rl = JupiterRLIntegration() if HAS_TRADING_COMPONENTS else None
        self.jupiter_api = JupiterAPIWrapper() if HAS_TRADING_COMPONENTS else None

        # Dashboard state
        self.data = {
            "timestamp": datetime.now().isoformat(),
            "portfolio": {},
            "positions": {},
            "signals": [],
            "performance": {},
            "market_data": {},
            "rl_metrics": {},
            "system_status": "initializing"
        }

        # Setup web application if dependencies are available
        if HAS_WEB_DEPS:
            self._setup_routes()
            self._setup_templates()
            self._setup_cors()
        else:
            logger.error("[ERROR] Web dependencies not available. Install aiohttp, aiohttp-cors, aiohttp-jinja2")

        logger.info(f"[ROCKET] Ultimate Trading Dashboard V3 initialized on port {self.port}")

    def _create_directories(self):
        """Create required directories for dashboard"""
        try:
            os.makedirs(self.static_dir, exist_ok=True)
            os.makedirs(self.templates_dir, exist_ok=True)

            # Create static files and templates
            self._create_static_files()
            self._create_templates()

            logger.info("[FOLDER] Dashboard directories created successfully")

        except Exception as e:
            logger.error(f"Error creating directories: {e}")

    def _create_static_files(self):
        """Create basic static files"""
        try:
            # Create CSS file
            css_content = """
/* Ultimate Trading Dashboard V3 - Cyberpunk Theme */
:root {
    --cyber-primary: #00ff41;
    --cyber-secondary: #ff0080;
    --cyber-bg: #0a0a0a;
    --cyber-surface: #1a1a1a;
    --cyber-text: #ffffff;
    --cyber-text-dim: #888888;
    --cyber-border: #333333;
    --cyber-danger: #ff3333;
    --cyber-warning: #ffaa00;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Courier New', monospace;
    background: var(--cyber-bg);
    color: var(--cyber-text);
    line-height: 1.6;
    overflow-x: hidden;
}

.dashboard {
    min-height: 100vh;
    padding: 20px;
    background: linear-gradient(135deg, var(--cyber-bg) 0%, #001a0a 100%);
}

.header {
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 2px solid var(--cyber-primary);
    padding-bottom: 20px;
}

.title {
    font-size: 2.5rem;
    color: var(--cyber-primary);
    text-shadow: 0 0 20px var(--cyber-primary);
    margin-bottom: 10px;
}

.subtitle {
    color: var(--cyber-text-dim);
    font-size: 1.1rem;
}

.status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--cyber-surface);
    border: 1px solid var(--cyber-border);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 30px;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--cyber-danger);
    animation: pulse 2s infinite;
}

.status-active {
    background: var(--cyber-primary);
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: var(--cyber-surface);
    border: 1px solid var(--cyber-border);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0, 255, 65, 0.1);
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    border-color: var(--cyber-primary);
    box-shadow: 0 15px 40px rgba(0, 255, 65, 0.2);
}

.card-title {
    color: var(--cyber-primary);
    font-size: 1.3rem;
    margin-bottom: 15px;
    text-align: center;
    border-bottom: 1px solid var(--cyber-border);
    padding-bottom: 10px;
}

.metric {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    padding: 8px 0;
    border-bottom: 1px dotted var(--cyber-border);
}

.metric-value {
    color: var(--cyber-primary);
    font-weight: bold;
}

.btn {
    background: linear-gradient(45deg, var(--cyber-primary), var(--cyber-secondary));
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    cursor: pointer;
    font-family: inherit;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
}

.loading {
    text-align: center;
    color: var(--cyber-text-dim);
    font-style: italic;
}

.error {
    color: var(--cyber-danger);
    text-align: center;
    padding: 20px;
    border: 1px solid var(--cyber-danger);
    border-radius: 10px;
    background: rgba(255, 51, 51, 0.1);
}
"""

            css_file = os.path.join(self.static_dir, "style.css")
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)

            # Create JavaScript file
            js_content = """
// Ultimate Trading Dashboard V3 - JavaScript
class TradingDashboard {
    constructor() {
        this.websocket = null;
        this.reconnectInterval = 5000;
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.updateStatus();
        setInterval(() => this.updateTimestamp(), 1000);
    }

    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('[LINK] WebSocket connected');
                this.updateConnectionStatus(true);
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                console.log('[ERROR] WebSocket disconnected');
                this.updateConnectionStatus(false);
                setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
        }
    }

    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'init':
            case 'update':
                this.updateDashboard(data.data);
                break;
            case 'pong':
                // Handle ping/pong
                break;
            case 'error':
                console.error('WebSocket error:', data.message);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    updateDashboard(data) {
        // Update timestamp
        if (data.timestamp) {
            const timestampEl = document.getElementById('timestamp');
            if (timestampEl) {
                timestampEl.textContent = new Date(data.timestamp).toLocaleString();
            }
        }

        // Update system status
        if (data.system_status) {
            const statusEl = document.getElementById('system-status');
            if (statusEl) {
                statusEl.textContent = data.system_status;
                statusEl.className = `status-indicator ${data.system_status === 'active' ? 'status-active' : ''}`;
            }
        }

        // Update metrics
        this.updateMetrics('trading-metrics', data.trading_metrics || {});
        this.updateMetrics('market-data', data.market_data || {});
        this.updateMetrics('rl-metrics', data.rl_metrics || {});
    }

    updateMetrics(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        Object.entries(data).forEach(([key, value]) => {
            const metricEl = container.querySelector(`[data-metric="${key}"]`);
            if (metricEl) {
                metricEl.textContent = typeof value === 'number' ? value.toFixed(4) : value;
            }
        });
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `status-indicator ${connected ? 'status-active' : ''}`;
        }
    }

    updateStatus() {
        // Fetch status from API
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                this.updateDashboard(data);
            })
            .catch(error => {
                console.error('Error fetching status:', error);
            });
    }

    updateTimestamp() {
        const timestampEl = document.getElementById('current-time');
        if (timestampEl) {
            timestampEl.textContent = new Date().toLocaleString();
        }
    }

    setupEventListeners() {
        // Add any button click handlers here
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('btn')) {
                console.log('Button clicked:', event.target.textContent);
            }
        });
    }

    sendWebSocketMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TradingDashboard();
});
"""

            js_file = os.path.join(self.static_dir, "dashboard.js")
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(js_content)

            logger.info("[ART] Static files created successfully")

        except Exception as e:
            logger.error(f"Error creating static files: {e}")

    def _create_templates(self):
        """Create HTML templates"""
        try:
            dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Trading Dashboard V3</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="dashboard">
        <!-- Header -->
        <header class="header">
            <h1 class="title">[ROCKET] ULTIMATE TRADING DASHBOARD V3</h1>
            <p class="subtitle">Real-time AI-powered trading interface</p>
        </header>

        <!-- Status Bar -->
        <div class="status-bar">
            <div class="status-item">
                <span class="status-indicator" id="connection-status"></span>
                <span>Connection</span>
            </div>
            <div class="status-item">
                <span class="status-indicator status-active" id="system-status"></span>
                <span>System Status</span>
            </div>
            <div class="status-item">
                <span>[CHART] Last Update:</span>
                <span id="current-time"></span>
            </div>
        </div>

        <!-- Main Grid -->
        <div class="grid">
            <!-- Trading Metrics Card -->
            <div class="card">
                <h3 class="card-title">[MONEY] Trading Metrics</h3>
                <div id="trading-metrics">
                    <div class="metric">
                        <span>Portfolio Value:</span>
                        <span class="metric-value" data-metric="portfolio_value">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Daily P&L:</span>
                        <span class="metric-value" data-metric="daily_pnl">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Total Trades:</span>
                        <span class="metric-value" data-metric="total_trades">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Win Rate:</span>
                        <span class="metric-value" data-metric="win_rate">Loading...</span>
                    </div>
                </div>
            </div>

            <!-- Market Data Card -->
            <div class="card">
                <h3 class="card-title">[PLANET] Market Data</h3>
                <div id="market-data">
                    <div class="metric">
                        <span>SOL/USDC:</span>
                        <span class="metric-value" data-metric="sol_price">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>24h Volume:</span>
                        <span class="metric-value" data-metric="volume_24h">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Best Route:</span>
                        <span class="metric-value" data-metric="best_route">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Liquidity:</span>
                        <span class="metric-value" data-metric="liquidity">Loading...</span>
                    </div>
                </div>
            </div>

            <!-- RL Metrics Card -->
            <div class="card">
                <h3 class="card-title">[BRAIN] RL Metrics</h3>
                <div id="rl-metrics">
                    <div class="metric">
                        <span>Model Performance:</span>
                        <span class="metric-value" data-metric="model_performance">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Learning Rate:</span>
                        <span class="metric-value" data-metric="learning_rate">0.001</span>
                    </div>
                    <div class="metric">
                        <span>Episode:</span>
                        <span class="metric-value" data-metric="episode">0</span>
                    </div>
                    <div class="metric">
                        <span>Reward:</span>
                        <span class="metric-value" data-metric="total_reward">Loading...</span>
                    </div>
                </div>
            </div>

            <!-- System Info Card -->
            <div class="card">
                <h3 class="card-title">[TOOLS] System Info</h3>
                <div id="system-info">
                    <div class="metric">
                        <span>Uptime:</span>
                        <span class="metric-value" data-metric="uptime">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Memory Usage:</span>
                        <span class="metric-value" data-metric="memory">Loading...</span>
                    </div>
                    <div class="metric">
                        <span>Active Connections:</span>
                        <span class="metric-value" data-metric="connections">0</span>
                    </div>
                    <div class="metric">
                        <span>API Calls:</span>
                        <span class="metric-value" data-metric="api_calls">0</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Control Panel -->
        <div class="card" style="max-width: 600px; margin: 0 auto;">
            <h3 class="card-title">[BOLT] Control Panel</h3>
            <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                <button class="btn" onclick="dashboard.updateStatus()">Refresh Status</button>
                <button class="btn" onclick="window.open('/api/metrics', '_blank')">View API</button>
                <button class="btn" onclick="dashboard.sendWebSocketMessage({type: 'ping'})">Test Connection</button>
            </div>
        </div>
    </div>

    <script src="/static/dashboard.js"></script>
</body>
</html>"""

            template_file = os.path.join(self.templates_dir, "dashboard.html")
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)

            logger.info("[ART] Templates created successfully")

        except Exception as e:
            logger.error(f"Error creating templates: {e}")

    def _setup_routes(self):
        """Setup web application routes"""
        if not HAS_WEB_DEPS:
            return

        try:
            # Create web application
            self.app = web.Application()

            # Add routes
            self.app.router.add_get('/', self._handle_dashboard)
            self.app.router.add_get('/api/status', self._handle_api_status)
            self.app.router.add_get('/api/metrics', self._handle_api_metrics)
            self.app.router.add_get('/api/trades', self._handle_api_trades)
            self.app.router.add_post('/api/trade', self._handle_api_trade)
            self.app.router.add_get('/ws', self._handle_websocket)

            # Static files
            self.app.router.add_static('/static', self.static_dir)

            logger.info("[LINK] Routes setup completed")

        except Exception as e:
            logger.error(f"Error setting up routes: {e}")

    def _setup_templates(self):
        """Setup template engine"""
        if not HAS_WEB_DEPS or not self.app:
            return

        try:
            # Setup Jinja2 templates
            aiohttp_jinja2.setup(
                self.app,
                loader=jinja2.FileSystemLoader(self.templates_dir)
            )

            logger.info("[ART] Template engine setup completed")

        except Exception as e:
            logger.error(f"Error setting up templates: {e}")

    def _setup_cors(self):
        """Setup CORS for API access"""
        if not HAS_WEB_DEPS or not self.app:
            return

        try:
            # Setup CORS
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })

            # Add CORS to all routes
            for route in list(self.app.router.routes()):
                cors.add(route)

            logger.info("[WEB] CORS setup completed")

        except Exception as e:
            logger.error(f"Error setting up CORS: {e}")

    async def _handle_dashboard(self, request):
        """Handle dashboard page"""
        try:
            return aiohttp_jinja2.render_template(
                'dashboard.html',
                request,
                {
                    'title': 'Ultimate Trading Dashboard V3',
                    'status': self.data['system_status']
                }
            )
        except Exception as e:
            logger.error(f"Error handling dashboard: {e}")
            return web.Response(text=f"Dashboard Error: {e}", status=500)

    async def _handle_api_status(self, request):
        """Handle API status endpoint"""
        try:
            return web.json_response({
                'status': 'online',
                'timestamp': datetime.now().isoformat(),
                'system': self.data['system_status'],
                'components': {
                    'trading_system': 'active' if self.trading_system else 'inactive',
                    'jupiter_rl': 'active' if self.jupiter_rl else 'inactive',
                    'jupiter_api': 'active' if self.jupiter_api else 'inactive'
                }
            })
        except Exception as e:
            logger.error(f"Error handling status API: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def _handle_api_metrics(self, request):
        """Handle API metrics endpoint"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'trading_metrics': self.data.get('trading_metrics', {}),
                'market_data': self.data.get('market_data', {}),
                'rl_metrics': self.data.get('rl_metrics', {}),
                'performance': {
                    'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00',
                    'memory_usage': f"{os.getpid()} MB",
                    'cpu_usage': "0%"
                }
            }

            return web.json_response(metrics)

        except Exception as e:
            logger.error(f"Error handling metrics API: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def _handle_api_trades(self, request):
        """Handle API trades endpoint"""
        try:
            trades = [
                {
                    'id': '1',
                    'timestamp': datetime.now().isoformat(),
                    'pair': 'SOL/USDC',
                    'type': 'buy',
                    'amount': '1.0',
                    'price': '100.50',
                    'status': 'completed'
                }
            ]

            return web.json_response({'trades': trades})

        except Exception as e:
            logger.error(f"Error handling trades API: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def _handle_api_trade(self, request):
        """Handle API trade execution endpoint"""
        try:
            data = await request.json()

            # Validate trade request
            required_fields = ['pair', 'type', 'amount']
            for field in required_fields:
                if field not in data:
                    return web.json_response({'error': f'Missing field: {field}'}, status=400)

            # Execute trade (demo mode)
            trade_result = {
                'id': f"trade_{int(time.time())}",
                'timestamp': datetime.now().isoformat(),
                'pair': data['pair'],
                'type': data['type'],
                'amount': data['amount'],
                'status': 'pending',
                'message': 'Trade submitted successfully (demo mode)'
            }

            return web.json_response(trade_result)

        except Exception as e:
            logger.error(f"Error handling trade API: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def _handle_websocket(self, request):
        """Handle WebSocket connections"""
        try:
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            # Add to connected clients
            self.websocket_clients.add(ws)
            logger.info(f"WebSocket client connected. Total: {len(self.websocket_clients)}")

            try:
                # Send initial data
                await ws.send_str(json.dumps({
                    'type': 'init',
                    'data': self.data
                }))

                # Handle messages
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            await self._handle_websocket_message(ws, data)
                        except json.JSONDecodeError:
                            await ws.send_str(json.dumps({
                                'type': 'error',
                                'message': 'Invalid JSON'
                            }))
                    elif msg.type == WSMsgType.ERROR:
                        logger.error(f'WebSocket error: {ws.exception()}')
                        break

            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                # Remove from connected clients
                self.websocket_clients.discard(ws)
                logger.info(f"WebSocket client disconnected. Total: {len(self.websocket_clients)}")

            return ws

        except Exception as e:
            logger.error(f"Error handling WebSocket: {e}")
            return web.Response(text=f"WebSocket Error: {e}", status=500)

    async def _handle_websocket_message(self, ws, data):
        """Handle incoming WebSocket messages"""
        try:
            message_type = data.get('type')

            if message_type == 'ping':
                await ws.send_str(json.dumps({'type': 'pong'}))
            elif message_type == 'subscribe':
                feed = data.get('feed', 'all')
                await ws.send_str(json.dumps({
                    'type': 'subscribed',
                    'feed': feed
                }))
            elif message_type == 'get_status':
                await ws.send_str(json.dumps({
                    'type': 'status',
                    'data': self.data
                }))
            else:
                await ws.send_str(json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await ws.send_str(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def start_server(self):
        """Start the dashboard server"""
        try:
            if not HAS_WEB_DEPS:
                logger.error("[ERROR] Web dependencies not available")
                return False

            if not self.app:
                logger.error("[ERROR] Web application not initialized")
                return False

            self.start_time = datetime.now()

            # Create server
            runner = web.AppRunner(self.app)
            await runner.setup()

            site = web.TCPSite(runner, self.host, self.port)
            await site.start()

            logger.info(f"[ROCKET] Dashboard server started on http://{self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False

    async def stop_server(self):
        """Stop the dashboard server"""
        try:
            # Close all WebSocket connections
            for ws in self.websocket_clients.copy():
                await ws.close()
            self.websocket_clients.clear()

            logger.info("[OK] Dashboard server stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            return False

# Standalone server for testing
async def main():
    """Main entry point for standalone server"""
    dashboard = UltimateTradingDashboard()

    try:
        if await dashboard.start_server():
            logger.info("[OK] Dashboard server is running")
            logger.info("[WEB] Visit http://localhost:8050 to view the dashboard")
            logger.info("[STOP] Press Ctrl+C to stop")

            # Keep running
            while True:
                await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("[STOP] Received stop signal")
        await dashboard.stop_server()
    except Exception as e:
        logger.error(f"[ERROR] Server error: {e}")
        await dashboard.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
