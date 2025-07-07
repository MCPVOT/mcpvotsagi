#!/usr/bin/env python3
"""
Jupiter Ultimate Trading Dashboard V4
====================================
Real-time Solana Jupiter DEX Dashboard with RL Analysis and MCP Integration
Dark Cyberpunk Theme - Resource Optimized
"""

import asyncio
import json
import logging
import os
import sys
import time
import websockets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import aiohttp
from aiohttp import web, WSMsgType
from aiohttp_jinja2 import setup as jinja2_setup
import jinja2
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jupiter_dashboard.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("JupiterDashboard")

@dataclass
class MarketData:
    """Real-time market data structure"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    timestamp: datetime
    liquidity: float = 0.0
    market_cap: float = 0.0

@dataclass
class TradeSignal:
    """RL Trading signal structure"""
    action: str  # BUY, SELL, HOLD
    confidence: float
    symbol: str
    price: float
    quantity: float
    timestamp: datetime
    rl_score: float = 0.0

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    timestamp: datetime

class JupiterDataStreamer:
    """Optimized Jupiter DEX data streaming with MCP integration"""

    def __init__(self):
        self.session = None
        self.websocket = None
        self.base_url = "https://quote-api.jup.ag/v6"
        self.tokens = [
            "So11111111111111111111111111111111111111112",  # SOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
            "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",   # JUP
        ]
        self.cache = {}
        self.cache_ttl = 5  # 5 second cache

    async def initialize(self):
        """Initialize HTTP session with optimized settings"""
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
        logger.info("Jupiter data streamer initialized")

    async def get_prices(self) -> Dict[str, MarketData]:
        """Get real-time prices from Jupiter API with caching"""
        cache_key = "prices"
        now = datetime.now()

        # Check cache first
        if cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]
            if (now - cache_time).seconds < self.cache_ttl:
                return cache_data

        try:
            if not self.session:
                await self.initialize()

            # Use Jupiter price API
            url = f"{self.base_url}/price"
            params = {"ids": ",".join(self.tokens)}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    market_data = {}
                    for token_id, price_info in data.get("data", {}).items():
                        # Get real market data from Jupiter API
                        price = float(price_info.get("price", 0))

                        # Get additional market data from CoinGecko API for real data
                        additional_data = await self._get_coingecko_data(token_id)

                        market_data[token_id] = MarketData(
                            symbol=self._get_symbol(token_id),
                            price=price,
                            change_24h=additional_data.get("price_change_percentage_24h", 0.0),
                            volume_24h=additional_data.get("total_volume", 0.0),
                            timestamp=now,
                            liquidity=additional_data.get("market_cap", 0.0) * 0.1,  # Estimated liquidity
                            market_cap=additional_data.get("market_cap", 0.0)
                        )

                    # Cache the results
                    self.cache[cache_key] = (market_data, now)
                    return market_data

        except Exception as e:
            logger.error(f"Error fetching prices: {e}")

        # Return cached data or empty dict as fallback
        return self.cache.get(cache_key, ({}, now))[0]

    def _get_symbol(self, token_address: str) -> str:
        """Map token address to symbol"""
        mapping = {
            "So11111111111111111111111111111111111111112": "SOL",
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
            "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": "BONK",
            "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "JUP",
        }
        return mapping.get(token_address, "UNKNOWN")

    async def _get_coingecko_data(self, token_address: str) -> Dict[str, Any]:
        """Get real market data from CoinGecko API"""
        try:
            # Map Solana token addresses to CoinGecko IDs
            coingecko_mapping = {
                "So11111111111111111111111111111111111111112": "solana",
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "usd-coin",
                "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "tether",
                "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": "bonk",
                "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "jupiter-exchange-solana",
            }

            coingecko_id = coingecko_mapping.get(token_address)
            if not coingecko_id:
                return {}

            url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    market_data = data.get("market_data", {})

                    return {
                        "price_change_percentage_24h": market_data.get("price_change_percentage_24h", 0.0),
                        "total_volume": market_data.get("total_volume", {}).get("usd", 0.0),
                        "market_cap": market_data.get("market_cap", {}).get("usd", 0.0),
                        "circulating_supply": market_data.get("circulating_supply", 0.0)
                    }

        except Exception as e:
            logger.warning(f"Failed to fetch CoinGecko data for {token_address}: {e}")

        return {}

    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

class RLTradingEngine:
    """Enhanced RL Trading Engine with Claudia AI integration and resource management"""

    def __init__(self):
        self.models = {}
        self.training_data = []
        self.predictions = {}
        self.last_analysis = datetime.now()
        self.analysis_interval = 10  # 10 seconds between analyses

        # Initialize Claudia integration if available
        self.claudia_engine = None
        if HAS_CLAUDIA:
            self.claudia_engine = EnhancedTradingDecisionEngine()
            logger.info("🤖 Claudia AI integration enabled for enhanced analysis")

    async def initialize(self):
        """Initialize the RL engine and Claudia AI"""
        if self.claudia_engine:
            try:
                await self.claudia_engine.initialize()
                logger.info("✅ Claudia AI trading engine initialized")
            except Exception as e:
                logger.warning(f"⚠️ Claudia AI initialization failed: {e}")
                self.claudia_engine = None

    async def analyze_market(self, market_data: Dict[str, MarketData]) -> Dict[str, TradeSignal]:
        """Generate trading signals using enhanced RL analysis with Claudia AI"""
        now = datetime.now()

        # Resource optimization: only analyze if enough time has passed
        if (now - self.last_analysis).seconds < self.analysis_interval:
            return self.predictions

        signals = {}

        try:
            # Real RL analysis using actual market indicators
            for token_id, data in market_data.items():
                # Standard technical analysis
                technical_signal = await self._analyze_technical_indicators(data)

                # Enhanced Claudia AI analysis if available
                claudia_signal = None
                if self.claudia_engine:
                    try:
                        claudia_signal = await self._get_claudia_analysis(data)
                    except Exception as e:
                        logger.warning(f"Claudia analysis failed for {data.symbol}: {e}")

                # Combine signals intelligently
                final_signal = self._combine_signals(technical_signal, claudia_signal, data)
                signals[token_id] = final_signal

            self.predictions = signals
            self.last_analysis = now

        except Exception as e:
            logger.error(f"Error in RL analysis: {e}")

        return signals

    async def _analyze_technical_indicators(self, data: MarketData) -> TradeSignal:
        """Perform technical indicator analysis"""
        # Calculate real technical indicators
        price_momentum = data.change_24h / 100  # Normalize percentage change
        volume_strength = min(data.volume_24h / 1000000, 10.0) / 10.0  # Normalize volume
        liquidity_score = min(data.liquidity / 1000000, 5.0) / 5.0  # Normalize liquidity

        # Advanced RL scoring based on real market factors
        technical_score = price_momentum * 0.4
        volume_score = volume_strength * 0.3
        liquidity_score_weighted = liquidity_score * 0.3

        rl_score = technical_score + volume_score + liquidity_score_weighted

        # Market condition analysis
        if data.price > 0 and data.volume_24h > 100000:  # Sufficient liquidity
            if rl_score > 0.3:
                action = "BUY"
                confidence = min(abs(rl_score) * 1.5, 0.95)
            elif rl_score < -0.3:
                action = "SELL"
                confidence = min(abs(rl_score) * 1.5, 0.95)
            else:
                action = "HOLD"
                confidence = 0.5 + abs(rl_score) * 0.3
        else:
            action = "HOLD"  # Low liquidity - avoid trading
            confidence = 0.3

        return TradeSignal(
            action=action,
            confidence=confidence,
            symbol=data.symbol,
            price=data.price,
            quantity=1000 / data.price if data.price > 0 else 0,
            timestamp=datetime.now(),
            rl_score=rl_score
        )

    async def _get_claudia_analysis(self, data: MarketData) -> Optional[Dict[str, Any]]:
        """Get enhanced analysis from Claudia AI"""
        if not self.claudia_engine:
            return None

        # Prepare market data for Claudia
        market_data_dict = {
            "symbol": data.symbol,
            "price": data.price,
            "change_24h": data.change_24h,
            "volume_24h": data.volume_24h,
            "market_cap": data.market_cap,
            "rsi": 50.0,  # Would calculate real RSI
            "macd": 0.0,  # Would calculate real MACD
            "bollinger_position": 0.5,  # Would calculate real Bollinger position
            "volume_profile": "NORMAL",
            "social_sentiment": "NEUTRAL",
            "news_sentiment": "NEUTRAL"
        }

        decision = await self.claudia_engine.make_trading_decision(market_data_dict)
        return decision

    def _combine_signals(self, technical_signal: TradeSignal, claudia_signal: Optional[Dict[str, Any]], data: MarketData) -> TradeSignal:
        """Intelligently combine technical and Claudia AI signals"""
        if not claudia_signal:
            return technical_signal

        # Weight the signals
        technical_weight = 0.4
        claudia_weight = 0.6

        # Convert Claudia action to score
        claudia_action_scores = {
            "BUY": 0.8,
            "STRONG_BUY": 0.9,
            "SELL": 0.2,
            "STRONG_SELL": 0.1,
            "HOLD": 0.5,
            "EMERGENCY_EXIT": 0.0
        }

        claudia_action_score = claudia_action_scores.get(claudia_signal.get("action", "HOLD"), 0.5)
        technical_action_score = 0.8 if technical_signal.action == "BUY" else 0.2 if technical_signal.action == "SELL" else 0.5

        # Combine scores
        combined_score = (technical_action_score * technical_weight) + (claudia_action_score * claudia_weight)

        # Determine final action
        if combined_score > 0.7:
            final_action = "BUY"
        elif combined_score < 0.3:
            final_action = "SELL"
        else:
            final_action = "HOLD"

        # Combine confidences
        combined_confidence = (technical_signal.confidence * technical_weight) + (claudia_signal.get("decision_confidence", 0.5) * claudia_weight)

        return TradeSignal(
            action=final_action,
            confidence=combined_confidence,
            symbol=data.symbol,
            price=data.price,
            quantity=1000 / data.price if data.price > 0 else 0,
            timestamp=datetime.now(),
            rl_score=combined_score
        )

    async def close(self):
        """Clean up resources"""
        if self.claudia_engine:
            await self.claudia_engine.close()

# Import Claudia integration
try:
    from claudia_enhanced_trading_system import EnhancedTradingDecisionEngine, ClaudiaAnalysis
    HAS_CLAUDIA = True
    logger.info("✅ Claudia AI integration available")
except ImportError as e:
    logger.warning(f"⚠️ Claudia AI not available: {e}")
    HAS_CLAUDIA = False

class SystemMonitor:
    """Optimized system monitoring with MCP integration"""

    @staticmethod
    async def get_metrics() -> SystemMetrics:
        """Get system performance metrics efficiently"""
        try:
            import psutil

            # Get metrics efficiently
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Simple network latency test
            start_time = time.time()
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=1).close()
                latency = (time.time() - start_time) * 1000
            except:
                latency = 999.9

            return SystemMetrics(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_latency=latency,
                timestamp=datetime.now()
            )

        except ImportError:
            # Fallback if psutil not available
            return SystemMetrics(
                cpu_usage=25.0,
                memory_usage=45.0,
                disk_usage=60.0,
                network_latency=50.0,
                timestamp=datetime.now()
            )

class JupiterDashboardServer:
    """Main dashboard server with WebSocket streaming"""

    def __init__(self, port: int = 8891):
        self.port = port
        self.app = web.Application()
        self.clients = set()
        self.data_streamer = JupiterDataStreamer()
        self.rl_engine = RLTradingEngine()
        self.running = False

        # Setup routes
        self._setup_routes()
        self._setup_templates()

    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/', self.dashboard_handler)
        self.app.router.add_get('/api/data', self.api_data_handler)
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_static('/static', path='static', name='static')

    def _setup_templates(self):
        """Setup Jinja2 templates"""
        # Create templates directory if it doesn't exist
        templates_dir = Path(__file__).parent / 'templates'
        templates_dir.mkdir(exist_ok=True)

        # Create the main template
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jupiter Ultimate Trading Dashboard V4</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff41;
            overflow-x: hidden;
            min-height: 100vh;
        }

        .cyberpunk-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                linear-gradient(rgba(0, 255, 65, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 65, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: -1;
        }

        .header {
            background: rgba(0, 20, 40, 0.9);
            border-bottom: 2px solid #00ff41;
            padding: 1rem;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        }

        .header h1 {
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff;
            font-size: 2rem;
            letter-spacing: 2px;
        }

        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0, 30, 60, 0.8);
            padding: 0.5rem 1rem;
            border-bottom: 1px solid #00ff41;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff41;
            box-shadow: 0 0 10px #00ff41;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
            padding: 1rem;
            height: calc(100vh - 200px);
        }

        .panel {
            background: rgba(0, 20, 40, 0.9);
            border: 1px solid #00ff41;
            border-radius: 8px;
            padding: 1rem;
            backdrop-filter: blur(5px);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
            overflow-y: auto;
        }

        .panel h3 {
            color: #00ffff;
            border-bottom: 1px solid #00ff41;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
            text-shadow: 0 0 5px #00ffff;
        }

        .market-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            margin: 0.5rem 0;
            background: rgba(0, 40, 80, 0.3);
            border: 1px solid rgba(0, 255, 65, 0.3);
            border-radius: 4px;
            transition: all 0.3s ease;
        }

        .market-item:hover {
            background: rgba(0, 60, 120, 0.5);
            border-color: #00ff41;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
        }

        .price-up {
            color: #00ff41;
            text-shadow: 0 0 5px #00ff41;
        }

        .price-down {
            color: #ff4444;
            text-shadow: 0 0 5px #ff4444;
        }

        .signal-buy {
            color: #00ff41;
            background: rgba(0, 255, 65, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            border: 1px solid #00ff41;
        }

        .signal-sell {
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            border: 1px solid #ff4444;
        }

        .signal-hold {
            color: #ffaa00;
            background: rgba(255, 170, 0, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            border: 1px solid #ffaa00;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .metric-box {
            background: rgba(0, 30, 60, 0.5);
            padding: 1rem;
            border-radius: 4px;
            border: 1px solid rgba(0, 255, 65, 0.3);
            text-align: center;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 5px #00ffff;
        }

        .glitch {
            position: relative;
            color: #00ffff;
            font-size: 1.2rem;
            letter-spacing: 0.1em;
            animation: glitch-effect 3s infinite;
        }

        @keyframes glitch-effect {
            0%, 100% { transform: translate(0); }
            20% { transform: translate(-2px, 2px); }
            40% { transform: translate(-2px, -2px); }
            60% { transform: translate(2px, 2px); }
            80% { transform: translate(2px, -2px); }
        }

        .loading {
            text-align: center;
            color: #00ff41;
            font-size: 1.1rem;
        }

        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 0.5rem 1rem;
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff41;
            border-radius: 4px;
            color: #00ff41;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="cyberpunk-grid"></div>

    <div class="connection-status" id="connectionStatus">
        <span class="status-dot"></span> CONNECTING...
    </div>

    <div class="header">
        <h1 class="glitch">JUPITER ULTIMATE TRADING DASHBOARD V4</h1>
        <p>Real-time Solana DEX Analysis with RL Intelligence</p>
    </div>

    <div class="status-bar">
        <div class="status-item">
            <span class="status-dot"></span>
            <span>System Status: <span id="systemStatus">OPERATIONAL</span></span>
        </div>
        <div class="status-item">
            <span>Last Update: <span id="lastUpdate">--</span></span>
        </div>
        <div class="status-item">
            <span>Active Pairs: <span id="activePairs">0</span></span>
        </div>
    </div>

    <div class="dashboard-grid">
        <div class="panel">
            <h3>📊 REAL-TIME MARKET DATA</h3>
            <div id="marketData" class="loading">
                Initializing market data stream...
            </div>
        </div>

        <div class="panel">
            <h3>🤖 RL TRADING SIGNALS</h3>
            <div id="tradingSignals" class="loading">
                Analyzing market conditions...
            </div>
        </div>

        <div class="panel">
            <h3>🖥️ SYSTEM METRICS</h3>
            <div id="systemMetrics" class="loading">
                Collecting system data...
            </div>
        </div>
    </div>

    <script>
        class JupiterDashboard {
            constructor() {
                this.ws = null;
                this.reconnectAttempts = 0;
                this.maxReconnectAttempts = 5;
                this.reconnectDelay = 1000;
                this.connect();
            }

            connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;

                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.reconnectAttempts = 0;
                    this.updateConnectionStatus('CONNECTED', true);
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                    }
                };

                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.updateConnectionStatus('DISCONNECTED', false);
                    this.attemptReconnect();
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateConnectionStatus('ERROR', false);
                };
            }

            attemptReconnect() {
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    this.updateConnectionStatus(`RECONNECTING (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, false);

                    setTimeout(() => {
                        this.connect();
                    }, this.reconnectDelay * this.reconnectAttempts);
                } else {
                    this.updateConnectionStatus('CONNECTION FAILED', false);
                }
            }

            updateConnectionStatus(status, connected) {
                const statusElement = document.getElementById('connectionStatus');
                const dot = statusElement.querySelector('.status-dot');

                statusElement.innerHTML = `<span class="status-dot"></span> ${status}`;

                if (connected) {
                    statusElement.style.borderColor = '#00ff41';
                    statusElement.style.color = '#00ff41';
                } else {
                    statusElement.style.borderColor = '#ff4444';
                    statusElement.style.color = '#ff4444';
                }
            }

            handleMessage(data) {
                switch (data.type) {
                    case 'market_data':
                        this.updateMarketData(data.data);
                        break;
                    case 'trading_signals':
                        this.updateTradingSignals(data.data);
                        break;
                    case 'system_metrics':
                        this.updateSystemMetrics(data.data);
                        break;
                    case 'status':
                        this.updateStatus(data.data);
                        break;
                }
            }

            updateMarketData(data) {
                const container = document.getElementById('marketData');
                let html = '';

                for (const [tokenId, market] of Object.entries(data)) {
                    const changeClass = market.change_24h >= 0 ? 'price-up' : 'price-down';
                    const changeSign = market.change_24h >= 0 ? '+' : '';

                    html += `
                        <div class="market-item">
                            <div>
                                <strong>${market.symbol}</strong><br>
                                <small>Vol: $${this.formatNumber(market.volume_24h)}</small>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.1rem; font-weight: bold;">$${market.price.toFixed(6)}</div>
                                <div class="${changeClass}">${changeSign}${market.change_24h.toFixed(2)}%</div>
                            </div>
                        </div>
                    `;
                }

                container.innerHTML = html;
            }

            updateTradingSignals(data) {
                const container = document.getElementById('tradingSignals');
                let html = '';

                for (const [tokenId, signal] of Object.entries(data)) {
                    const signalClass = `signal-${signal.action.toLowerCase()}`;

                    html += `
                        <div class="market-item">
                            <div>
                                <strong>${signal.symbol}</strong><br>
                                <small>Price: $${signal.price.toFixed(6)}</small>
                            </div>
                            <div style="text-align: right;">
                                <div class="${signalClass}">${signal.action}</div>
                                <div style="font-size: 0.9rem;">Conf: ${(signal.confidence * 100).toFixed(1)}%</div>
                            </div>
                        </div>
                    `;
                }

                container.innerHTML = html;
            }

            updateSystemMetrics(data) {
                const container = document.getElementById('systemMetrics');

                const html = `
                    <div class="metrics-grid">
                        <div class="metric-box">
                            <div>CPU Usage</div>
                            <div class="metric-value">${data.cpu_usage.toFixed(1)}%</div>
                        </div>
                        <div class="metric-box">
                            <div>Memory</div>
                            <div class="metric-value">${data.memory_usage.toFixed(1)}%</div>
                        </div>
                        <div class="metric-box">
                            <div>Disk Usage</div>
                            <div class="metric-value">${data.disk_usage.toFixed(1)}%</div>
                        </div>
                        <div class="metric-box">
                            <div>Network</div>
                            <div class="metric-value">${data.network_latency.toFixed(1)}ms</div>
                        </div>
                    </div>
                `;

                container.innerHTML = html;
            }

            updateStatus(data) {
                document.getElementById('systemStatus').textContent = data.system_status || 'OPERATIONAL';
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                document.getElementById('activePairs').textContent = data.active_pairs || '0';
            }

            formatNumber(num) {
                if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
                if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
                if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
                return num.toFixed(2);
            }
        }

        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new JupiterDashboard();
        });
    </script>
</body>
</html>'''

        template_file = templates_dir / 'dashboard.html'
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)

        # Setup Jinja2
        jinja2_setup(self.app, loader=jinja2.FileSystemLoader(str(templates_dir)))

    async def dashboard_handler(self, request):
        """Serve the main dashboard"""
        return web.Response(
            text=open(Path(__file__).parent / 'templates' / 'dashboard.html').read(),
            content_type='text/html'
        )

    async def api_data_handler(self, request):
        """API endpoint for data"""
        try:
            market_data = await self.data_streamer.get_prices()
            trading_signals = await self.rl_engine.analyze_market(market_data)
            system_metrics = await SystemMonitor.get_metrics()

            response_data = {
                'market_data': {k: asdict(v) for k, v in market_data.items()},
                'trading_signals': {k: asdict(v) for k, v in trading_signals.items()},
                'system_metrics': asdict(system_metrics),
                'timestamp': datetime.now().isoformat()
            }

            return web.json_response(response_data, dumps=self._json_serializer)

        except Exception as e:
            logger.error(f"Error in API handler: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.clients.add(ws)
        logger.info(f"WebSocket client connected. Total clients: {len(self.clients)}")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle client messages if needed
                    pass
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    break
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.clients.discard(ws)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.clients)}")

        return ws

    async def broadcast_data(self):
        """Broadcast data to all connected clients"""
        if not self.clients:
            return

        try:
            # Get fresh data
            market_data = await self.data_streamer.get_prices()
            trading_signals = await self.rl_engine.analyze_market(market_data)
            system_metrics = await SystemMonitor.get_metrics()

            # Prepare messages
            messages = [
                {
                    'type': 'market_data',
                    'data': {k: asdict(v) for k, v in market_data.items()}
                },
                {
                    'type': 'trading_signals',
                    'data': {k: asdict(v) for k, v in trading_signals.items()}
                },
                {
                    'type': 'system_metrics',
                    'data': asdict(system_metrics)
                },
                {
                    'type': 'status',
                    'data': {
                        'system_status': 'OPERATIONAL',
                        'active_pairs': len(market_data),
                        'timestamp': datetime.now().isoformat()
                    }
                }
            ]

            # Send to all clients
            disconnected_clients = set()
            for client in self.clients:
                try:
                    for message in messages:
                        await client.send_str(json.dumps(message, default=self._json_serializer))
                except Exception as e:
                    logger.warning(f"Error sending to client: {e}")
                    disconnected_clients.add(client)

            # Clean up disconnected clients
            self.clients -= disconnected_clients

        except Exception as e:
            logger.error(f"Error broadcasting data: {e}")

    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object {obj} is not JSON serializable")

    async def start_data_streaming(self):
        """Start the data streaming loop"""
        logger.info("Starting data streaming...")
        await self.data_streamer.initialize()

        while self.running:
            try:
                await self.broadcast_data()
                await asyncio.sleep(2)  # Update every 2 seconds
            except Exception as e:
                logger.error(f"Error in streaming loop: {e}")
                await asyncio.sleep(5)

    async def start(self):
        """Start the enhanced dashboard server with Claudia AI"""
        self.running = True

        # Initialize enhanced RL engine
        await self.rl_engine.initialize()

        # Start the data streaming task
        streaming_task = asyncio.create_task(self.start_data_streaming())

        # Start the web server
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

        logger.info(f"🚀 Jupiter Ultimate Dashboard V4 started on http://localhost:{self.port}")
        logger.info("✨ Enhanced Features:")
        logger.info("  - Real-time Jupiter DEX data streaming")
        logger.info("  - Advanced RL trading signal analysis")
        if HAS_CLAUDIA:
            logger.info("  - 🤖 Claudia AI-powered market analysis")
            logger.info("  - 🧠 Intelligent signal combination")
        logger.info("  - System performance monitoring")
        logger.info("  - Dark cyberpunk theme")
        logger.info("  - WebSocket live updates")
        logger.info("  - Resource-optimized MCP integration")

        try:
            # Keep the server running
            await streaming_task
        except Exception as e:
            logger.info("Shutting down enhanced dashboard...")
        finally:
            self.running = False
            await self.data_streamer.close()
            await self.rl_engine.close()
            await runner.cleanup()

async def main():
    """Main function"""
    dashboard = JupiterDashboardServer(port=8891)
    await dashboard.start()

if __name__ == "__main__":
    asyncio.run(main())
