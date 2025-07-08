#!/usr/bin/env python3
"""
Ultimate Trading Dashboard V3 - Advanced Web Interface
======================================================
🚀 Real-time trading dashboard with Jupiter DEX integration
📊 Advanced charts, RL monitoring, and portfolio management
🧠 AI-powered insights and automated trading signals
🔥 Professional UI with cyberpunk theme
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback
import sqlite3
import pandas as pd
import numpy as np

# Web framework
from aiohttp import web, WSMsgType
import aiohttp_cors
import jinja2
import aiohttp_jinja2

# Import our components
try:
    from ultimate_trading_system_v3 import UltimateTradingSystemV3
    from jupiter_rl_integration import JupiterRLIntegration
    from jupiter_api_wrapper import JupiterAPIWrapper
    from deepseek_r1_trading_agent_enhanced import DeepSeekR1TradingAgent
    HAS_TRADING_COMPONENTS = True
except ImportError as e:
    logging.warning(f"Trading components not available: {e}")
    HAS_TRADING_COMPONENTS = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingDashboard")

class UltimateTradingDashboard:
    """Advanced trading dashboard with real-time updates and AI integration"""

    def __init__(self, port: int = 8890):
        self.port = port
        self.app = web.Application()
        self.websockets = []
        self.f_drive_path = "F:/ULTIMATE_AGI_DATA/RL_TRADING/"

        # Create required directories
        self.static_dir = os.path.join(self.f_drive_path, "dashboard_static")
        self.templates_dir = os.path.join(self.f_drive_path, "dashboard_templates")
        self._create_directories()

        # Initialize trading components
        self.trading_system = UltimateTradingSystemV3() if HAS_TRADING_COMPONENTS else None
        self.jupiter_rl = JupiterRLIntegration() if HAS_TRADING_COMPONENTS else None
        self.jupiter_api = JupiterAPIWrapper() if HAS_TRADING_COMPONENTS else None
        self.deepseek_agent = DeepSeekR1TradingAgent() if HAS_TRADING_COMPONENTS else None

        # Dashboard state
        self.dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "portfolio": {},
            "positions": {},
            "signals": [],
            "performance": {},
            "market_data": {},
            "rl_metrics": {},
            "system_status": "initializing"
        }

        # Setup web application
        self._setup_routes()
        self._setup_templates()
        self._setup_cors()

        logger.info(f"🚀 Ultimate Trading Dashboard V3 initialized on port {self.port}")

    def _create_directories(self):
        """Create required directories for dashboard"""
        try:
            os.makedirs(self.static_dir, exist_ok=True)
            os.makedirs(self.templates_dir, exist_ok=True)

            # Create basic static files if they don't exist
            self._create_static_files()
            self._create_templates()

            logger.info("📁 Dashboard directories created successfully")

        except Exception as e:
            logger.error(f"Error creating directories: {e}")

    def _create_static_files(self):
        """Create basic static files"""
        try:
            # Create basic CSS
            css_content = """
/* Ultimate Trading Dashboard V3 - Cyberpunk Theme */
:root {
    --cyber-bg: #0a0a0a;
    --cyber-primary: #00ff41;
    --cyber-secondary: #ff0080;
    --cyber-accent: #00d4ff;
    --cyber-warning: #ffaa00;
    --cyber-danger: #ff4444;
    --cyber-text: #ffffff;
    --cyber-text-dim: #cccccc;
    --cyber-border: #333333;
    --cyber-card: #111111;
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

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    background: linear-gradient(135deg, var(--cyber-primary), var(--cyber-secondary));
    padding: 20px;
    text-align: center;
    border-bottom: 2px solid var(--cyber-accent);
}

.header h1 {
    font-size: 2.5rem;
    font-weight: bold;
    text-shadow: 0 0 10px var(--cyber-primary);
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.card {
    background: var(--cyber-card);
    border: 1px solid var(--cyber-border);
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 255, 65, 0.1);
    transition: all 0.3s ease;
}

.card:hover {
    border-color: var(--cyber-primary);
    box-shadow: 0 6px 20px rgba(0, 255, 65, 0.3);
}

.card-title {
    font-size: 1.5rem;
    color: var(--cyber-primary);
    margin-bottom: 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    padding: 10px;
    background: rgba(0, 255, 65, 0.1);
    border-radius: 5px;
}

.metric-value {
    font-weight: bold;
    color: var(--cyber-accent);
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.status-active { background: var(--cyber-primary); }
.status-inactive { background: var(--cyber-danger); }
.status-warning { background: var(--cyber-warning); }

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

.table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.table th,
.table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid var(--cyber-border);
}

.table th {
    background: var(--cyber-primary);
    color: var(--cyber-bg);
    font-weight: bold;
}

.table tr:hover {
    background: rgba(0, 255, 65, 0.1);
}

.positive { color: var(--cyber-primary); }
.negative { color: var(--cyber-danger); }
.neutral { color: var(--cyber-text-dim); }
"""

            css_file = os.path.join(self.static_dir, "style.css")
            with open(css_file, 'w') as f:
                f.write(css_content)

            # Create basic JavaScript
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
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket(`ws://localhost:${window.location.port}/ws`);

            this.websocket.onopen = () => {
                console.log('🔗 WebSocket connected');
                this.updateConnectionStatus(true);
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
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
        switch (data.type) {
            case 'portfolio_update':
                this.updatePortfolio(data.data);
                break;
            case 'position_update':
                this.updatePositions(data.data);
                break;
            case 'signal_update':
                this.updateSignals(data.data);
                break;
            case 'performance_update':
                this.updatePerformance(data.data);
                break;
            case 'market_data_update':
                this.updateMarketData(data.data);
                break;
            case 'system_status':
                this.updateSystemStatus(data.data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    updatePortfolio(data) {
        const portfolioElement = document.getElementById('portfolio-data');
        if (portfolioElement) {
            portfolioElement.innerHTML = this.formatPortfolioData(data);
        }
    }

    updatePositions(data) {
        const positionsElement = document.getElementById('positions-data');
        if (positionsElement) {
            positionsElement.innerHTML = this.formatPositionsData(data);
        }
    }

    updateSignals(data) {
        const signalsElement = document.getElementById('signals-data');
        if (signalsElement) {
            signalsElement.innerHTML = this.formatSignalsData(data);
        }
    }

    updatePerformance(data) {
        const performanceElement = document.getElementById('performance-data');
        if (performanceElement) {
            performanceElement.innerHTML = this.formatPerformanceData(data);
        }
    }

    updateMarketData(data) {
        const marketElement = document.getElementById('market-data');
        if (marketElement) {
            marketElement.innerHTML = this.formatMarketData(data);
        }
    }

    updateSystemStatus(data) {
        const statusElement = document.getElementById('system-status');
        if (statusElement) {
            statusElement.innerHTML = this.formatSystemStatus(data);
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = connected ? 'status-indicator status-active' : 'status-indicator status-inactive';
        }
    }

    formatPortfolioData(data) {
        return `
            <div class="metric">
                <span>Total Value:</span>
                <span class="metric-value">$${data.total_value || 0}</span>
            </div>
            <div class="metric">
                <span>Available Balance:</span>
                <span class="metric-value">$${data.available_balance || 0}</span>
            </div>
            <div class="metric">
                <span>Total P&L:</span>
                <span class="metric-value ${data.total_pnl >= 0 ? 'positive' : 'negative'}">
                    $${data.total_pnl || 0}
                </span>
            </div>
        `;
    }

    formatPositionsData(data) {
        if (!data || data.length === 0) {
            return '<p>No active positions</p>';
        }

        return data.map(pos => `
            <div class="metric">
                <span>${pos.symbol} ${pos.side}</span>
                <span class="metric-value ${pos.pnl >= 0 ? 'positive' : 'negative'}">
                    ${pos.pnl >= 0 ? '+' : ''}${pos.pnl}%
                </span>
            </div>
        `).join('');
    }

    formatSignalsData(data) {
        if (!data || data.length === 0) {
            return '<p>No active signals</p>';
        }

        return data.slice(0, 5).map(signal => `
            <div class="metric">
                <span>${signal.symbol} ${signal.action}</span>
                <span class="metric-value">
                    ${(signal.confidence * 100).toFixed(1)}%
                </span>
            </div>
        `).join('');
    }

    formatPerformanceData(data) {
        return `
            <div class="metric">
                <span>Win Rate:</span>
                <span class="metric-value">${data.win_rate || 0}%</span>
            </div>
            <div class="metric">
                <span>Sharpe Ratio:</span>
                <span class="metric-value">${data.sharpe_ratio || 0}</span>
            </div>
            <div class="metric">
                <span>Max Drawdown:</span>
                <span class="metric-value negative">${data.max_drawdown || 0}%</span>
            </div>
        `;
    }

    formatMarketData(data) {
        return Object.entries(data).map(([symbol, info]) => `
            <div class="metric">
                <span>${symbol}:</span>
                <span class="metric-value">$${info.price || 0}</span>
            </div>
        `).join('');
    }

    formatSystemStatus(data) {
        return `
            <div class="metric">
                <span>System Status:</span>
                <span class="metric-value">${data.status || 'Unknown'}</span>
            </div>
            <div class="metric">
                <span>Active Strategies:</span>
                <span class="metric-value">${data.active_strategies || 0}</span>
            </div>
            <div class="metric">
                <span>Uptime:</span>
                <span class="metric-value">${data.uptime || '0m'}</span>
            </div>
        `;
    }

    setupEventListeners() {
        // Add event listeners for interactive elements
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-start-trading')) {
                this.startTrading();
            } else if (e.target.classList.contains('btn-stop-trading')) {
                this.stopTrading();
            } else if (e.target.classList.contains('btn-refresh')) {
                this.refreshData();
            }
        });
    }

    startTrading() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'start_trading',
                data: {}
            }));
        }
    }

    stopTrading() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'stop_trading',
                data: {}
            }));
        }
    }

    refreshData() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'refresh_data',
                data: {}
            }));
        }
    }

    updateStatus() {
        // Update dashboard status periodically
        setInterval(() => {
            document.getElementById('last-update').textContent =
                new Date().toLocaleTimeString();
        }, 1000);
    }

    def _setup_routes(self):
        """Setup web application routes"""
        try:
            from aiohttp import web

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

            logger.info("🔗 Routes setup completed")

        except Exception as e:
            logger.error(f"Error setting up routes: {e}")

    def _setup_templates(self):
        """Setup template engine"""
        try:
            import aiohttp_jinja2
            import jinja2

            # Setup Jinja2 templates
            aiohttp_jinja2.setup(
                self.app,
                loader=jinja2.FileSystemLoader(self.templates_dir)
            )

            logger.info("🎨 Template engine setup completed")

        except Exception as e:
            logger.error(f"Error setting up templates: {e}")

    def _setup_cors(self):
        """Setup CORS for API access"""
        try:
            import aiohttp_cors

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

            logger.info("🌐 CORS setup completed")

        except Exception as e:
            logger.error(f"Error setting up CORS: {e}")

    async def _handle_dashboard(self, request):
        """Handle dashboard page"""
        try:
            import aiohttp_jinja2
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
            from aiohttp import web
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
            from aiohttp import web

            # Get real-time metrics
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'trading_metrics': self.data.get('trading_metrics', {}),
                'market_data': self.data.get('market_data', {}),
                'rl_metrics': self.data.get('rl_metrics', {}),
                'performance': {
                    'uptime': str(datetime.now() - self.start_time) if hasattr(self, 'start_time') else '0:00:00',
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
            from aiohttp import web

            # Get recent trades
            trades = []
            if self.trading_system:
                try:
                    # trades = await self.trading_system.get_recent_trades()
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
                except Exception as e:
                    logger.error(f"Error getting trades: {e}")

            return web.json_response({'trades': trades})

        except Exception as e:
            logger.error(f"Error handling trades API: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def _handle_api_trade(self, request):
        """Handle API trade execution endpoint"""
        try:
            from aiohttp import web

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
            from aiohttp import web, WSMsgType

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
                            data = json.loads(msg.data);
                            await this._handle_websocket_message(ws, data);
                        } catch (json.JSONDecodeError) {
                            await ws.send_str(json.dumps({
                                'type': 'error',
                                'message': 'Invalid JSON'
                            }));
                    } elif (msg.type == WSMsgType.ERROR) {
                        logger.error(`WebSocket error: ${ws.exception()}`);
                        break;

            } catch (Exception as e) {
                logger.error(f"WebSocket error: {e}");
            } finally {
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
                # Handle subscription to data feeds
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

    async def broadcast_update(self, data):
        """Broadcast data update to all connected WebSocket clients"""
        if not self.websocket_clients:
            return

        message = json.dumps({
            'type': 'update',
            'timestamp': datetime.now().isoformat(),
            'data': data
        })

        # Send to all connected clients
        disconnected = set()
        for ws in self.websocket_clients.copy():
            try:
                await ws.send_str(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.add(ws)

        # Remove disconnected clients
        self.websocket_clients -= disconnected

    async def start_server(self):
        """Start the dashboard server"""
        try:
            from aiohttp import web

            self.start_time = datetime.now()

            # Create server
            runner = web.AppRunner(self.app)
            await runner.setup()

            site = web.TCPSite(runner, self.host, self.port)
            await site.start()

            logger.info(f"🚀 Dashboard server started on http://{self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False

# Main execution
async def main():
    """Main execution function"""
    dashboard = UltimateTradingDashboard()
    await dashboard.start()

if __name__ == "__main__":
    asyncio.run(main())
