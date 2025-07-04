#!/usr/bin/env python3
"""
Oracle AGI V6 Real-Time Dashboard with F:\ Drive Integration
===========================================================
Enhanced unified dashboard with real-time data from F:\ drive storage
"""

import asyncio
import json
import logging
import sqlite3
import time
import psutil
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import aiohttp
from aiohttp import web
import websockets
import pandas as pd
import numpy as np
from collections import deque
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleAGIV6")

# F:\ Drive Configuration
F_DRIVE_ROOT = Path("F:/MCPVotsAGI_Data")
F_DRIVE_ENABLED = F_DRIVE_ROOT.exists()

class OracleAGIRealtimeDashboard:
    """Oracle AGI V6 Real-Time Dashboard with complete F:\ drive integration"""
    
    def __init__(self):
        self.workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
        self.workspace.mkdir(exist_ok=True)
        
        # F:\ Drive paths
        if F_DRIVE_ENABLED:
            self.data_root = F_DRIVE_ROOT
            self.rl_data_path = F_DRIVE_ROOT / "rl_training"
            self.market_data_path = F_DRIVE_ROOT / "market_data"
            self.trading_path = F_DRIVE_ROOT / "trading"
            self.metrics_path = F_DRIVE_ROOT / "metrics"
            self.logs_path = F_DRIVE_ROOT / "logs"
        else:
            self.data_root = self.workspace / "data"
            self.rl_data_path = self.data_root / "rl_training"
            self.market_data_path = self.data_root / "market_data"
            self.trading_path = self.data_root / "trading"
            self.metrics_path = self.data_root / "metrics"
            self.logs_path = self.data_root / "logs"
            
        # WebSocket connections
        self.websocket_connections: Set = set()
        
        # Real-time data buffers
        self.price_buffer = deque(maxlen=1000)
        self.metrics_buffer = deque(maxlen=500)
        self.trade_buffer = deque(maxlen=100)
        
        # Service endpoints with health monitoring
        self.services = {
            'deepseek_mcp': {
                'host': 'localhost', 
                'port': 3008, 
                'name': 'DeepSeek MCP',
                'health_endpoint': '/health',
                'critical': True
            },
            'deepseek_trading': {
                'host': 'localhost', 
                'port': 3009, 
                'name': 'DeepSeek Trading',
                'health_endpoint': '/health',
                'critical': True
            },
            'memory_mcp': {
                'host': 'localhost', 
                'port': 3002, 
                'name': 'Memory MCP',
                'health_endpoint': '/health',
                'critical': True
            },
            'solana_mcp': {
                'host': 'localhost', 
                'port': 3005, 
                'name': 'Solana MCP',
                'health_endpoint': '/health',
                'critical': False
            },
            'opencti_mcp': {
                'host': 'localhost', 
                'port': 3007, 
                'name': 'OpenCTI MCP',
                'health_endpoint': '/health',
                'critical': False
            },
            'ollama': {
                'host': 'localhost', 
                'port': 11434, 
                'name': 'Ollama Service',
                'health_endpoint': '/api/tags',
                'critical': True
            }
        }
        
        # Initialize database with real-time tables
        self._init_realtime_database()
        
        # Performance tracking
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    def _init_realtime_database(self):
        """Initialize database with real-time data tables"""
        db_path = self.metrics_path / 'realtime_metrics.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Real-time price data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                bid REAL,
                ask REAL,
                spread REAL,
                INDEX idx_timestamp (timestamp),
                INDEX idx_symbol (symbol)
            )
        ''')
        
        # Real-time trading signals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                deepseek_score REAL,
                rl_score REAL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                risk_reward REAL,
                INDEX idx_timestamp (timestamp)
            )
        ''')
        
        # System performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                memory_mb REAL,
                disk_usage_gb REAL,
                disk_free_gb REAL,
                network_mbps REAL,
                active_connections INTEGER,
                requests_per_minute REAL,
                avg_response_ms REAL,
                INDEX idx_timestamp (timestamp)
            )
        ''')
        
        # RL training metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rl_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                episode INTEGER,
                total_reward REAL,
                avg_reward REAL,
                epsilon REAL,
                loss REAL,
                q_value REAL,
                buffer_size INTEGER,
                training_time_ms REAL,
                INDEX idx_timestamp (timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def start_unified_system(self):
        """Start the complete real-time dashboard system"""
        logger.info("🚀 Starting Oracle AGI V6 Real-Time Dashboard...")
        
        try:
            # Phase 1: Check F:\ drive
            await self._check_f_drive()
            
            # Phase 2: Start data collectors
            await self._start_data_collectors()
            
            # Phase 3: Start metrics collection
            asyncio.create_task(self._collect_system_metrics())
            
            # Phase 4: Start real-time price feed
            asyncio.create_task(self._collect_price_data())
            
            # Phase 5: Start RL metrics monitoring
            asyncio.create_task(self._monitor_rl_training())
            
            # Phase 6: Web dashboard
            await self._start_web_dashboard()
            
            logger.info("✅ Oracle AGI V6 Real-Time System is OPERATIONAL!")
            logger.info("🌐 Dashboard: http://localhost:3011")
            logger.info("🔌 WebSocket: ws://localhost:3011/ws")
            logger.info(f"💾 F:\\ Drive: {'ENABLED' if F_DRIVE_ENABLED else 'DISABLED'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start real-time system: {e}")
            raise
            
    async def _check_f_drive(self):
        """Check F:\ drive availability and space"""
        if F_DRIVE_ENABLED:
            disk = psutil.disk_usage(str(F_DRIVE_ROOT))
            logger.info(f"💾 F:\\ Drive Status:")
            logger.info(f"   Total: {disk.total / (1024**3):.2f} GB")
            logger.info(f"   Used: {disk.used / (1024**3):.2f} GB ({disk.percent}%)")
            logger.info(f"   Free: {disk.free / (1024**3):.2f} GB")
            
            if disk.percent > 90:
                logger.warning("⚠️ F:\\ drive usage above 90%!")
        else:
            logger.warning("⚠️ F:\\ drive not available - using local storage")
            
    async def _start_data_collectors(self):
        """Start background data collection tasks"""
        logger.info("📊 Starting real-time data collectors...")
        
        # Create data directories
        for path in [self.rl_data_path, self.market_data_path, 
                     self.trading_path, self.metrics_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
            
    async def _collect_system_metrics(self):
        """Collect system performance metrics in real-time"""
        db_path = self.metrics_path / 'realtime_metrics.db'
        
        while True:
            try:
                # Collect metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage(str(self.data_root))
                network = psutil.net_io_counters()
                
                # Calculate request rate
                requests_per_minute = self.request_count * 60 / max(
                    (datetime.now() - self.start_time).total_seconds(), 1
                )
                
                # Store in database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO system_metrics 
                    (timestamp, cpu_percent, memory_percent, memory_mb, 
                     disk_usage_gb, disk_free_gb, network_mbps, 
                     active_connections, requests_per_minute)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    time.time(),
                    cpu_percent,
                    memory.percent,
                    memory.used / (1024**2),
                    disk.used / (1024**3),
                    disk.free / (1024**3),
                    (network.bytes_sent + network.bytes_recv) / (1024**2),
                    len(self.websocket_connections),
                    requests_per_minute
                ))
                
                conn.commit()
                conn.close()
                
                # Add to buffer for real-time updates
                self.metrics_buffer.append({
                    'timestamp': time.time(),
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'disk_free_gb': disk.free / (1024**3)
                })
                
                # Broadcast to WebSocket clients
                await self._broadcast_metrics_update()
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                
            await asyncio.sleep(5)  # Collect every 5 seconds
            
    async def _collect_price_data(self):
        """Collect real-time price data"""
        symbols = ['GLD', 'SLV', 'PPLT', 'PALL']  # Precious metals ETFs
        db_path = self.metrics_path / 'realtime_metrics.db'
        
        while True:
            try:
                for symbol in symbols:
                    # Fetch real price data
                    price_data = await self._fetch_real_price(symbol)
                    if not price_data:
                        continue
                        
                    price = price_data['price']
                    volume = price_data['volume']
                    spread = price_data['spread']
                    
                    price_data = {
                        'timestamp': time.time(),
                        'symbol': symbol,
                        'price': price,
                        'volume': volume,
                        'bid': price - spread/2,
                        'ask': price + spread/2,
                        'spread': spread
                    }
                    
                    # Store in database
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO realtime_prices 
                        (timestamp, symbol, price, volume, bid, ask, spread)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        price_data['timestamp'],
                        price_data['symbol'],
                        price_data['price'],
                        price_data['volume'],
                        price_data['bid'],
                        price_data['ask'],
                        price_data['spread']
                    ))
                    
                    conn.commit()
                    conn.close()
                    
                    # Add to buffer
                    self.price_buffer.append(price_data)
                    
                # Broadcast price updates
                await self._broadcast_price_update()
                
            except Exception as e:
                logger.error(f"Error collecting price data: {e}")
                
            await asyncio.sleep(1)  # Update every second
            

    async def _fetch_real_price(self, symbol: str) -> Optional[Dict]:
        """Fetch real price data from market data API or stored data"""
        try:
            # Try to get from stored market data first
            market_data_file = self.market_data_path / "price_history" / f"{symbol}_latest.json"
            
            if market_data_file.exists():
                # Use stored data if fresh (< 1 minute old)
                if (time.time() - market_data_file.stat().st_mtime) < 60:
                    with open(market_data_file, 'r') as f:
                        return json.load(f)
                        
            # Otherwise fetch from Yahoo Finance API
            async with aiohttp.ClientSession() as session:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                params = {
                    'interval': '1m',
                    'range': '1d',
                    'includePrePost': 'false'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data['chart']['result'][0]
                        quote = result['indicators']['quote'][0]
                        
                        # Get latest values
                        latest_idx = -1
                        while latest_idx >= -len(quote['close']) and quote['close'][latest_idx] is None:
                            latest_idx -= 1
                            
                        price_data = {
                            'symbol': symbol,
                            'price': quote['close'][latest_idx],
                            'volume': quote['volume'][latest_idx],
                            'high': quote['high'][latest_idx],
                            'low': quote['low'][latest_idx],
                            'open': quote['open'][latest_idx],
                            'spread': (quote['high'][latest_idx] - quote['low'][latest_idx]) / quote['close'][latest_idx],
                            'timestamp': result['timestamp'][latest_idx]
                        }
                        
                        # Cache the data
                        market_data_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(market_data_file, 'w') as f:
                            json.dump(price_data, f)
                            
                        return price_data
                        
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            
            # Fallback to last known price from database
            try:
                conn = sqlite3.connect(self.metrics_path / 'realtime_metrics.db')
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT price, volume, spread "
                    "FROM realtime_prices "
                    "WHERE symbol = ? "
                    "ORDER BY timestamp DESC "
                    "LIMIT 1",
                    (symbol,)
                )
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return {
                        'symbol': symbol,
                        'price': row[0],
                        'volume': row[1],
                        'spread': row[2]
                    }
                    
            except Exception as db_error:
                logger.error(f"Database fallback failed: {db_error}")
                
        return None

    async def _monitor_rl_training(self):
        """Monitor RL training progress from F:\ drive"""
        if not F_DRIVE_ENABLED:
            return
            
        rl_log_path = self.rl_data_path / "training_logs" / "latest.json"
        db_path = self.metrics_path / 'realtime_metrics.db'
        
        while True:
            try:
                if rl_log_path.exists():
                    async with aiofiles.open(rl_log_path, 'r') as f:
                        content = await f.read()
                        rl_data = json.loads(content)
                        
                    # Store in database
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO rl_metrics 
                        (timestamp, episode, total_reward, avg_reward, 
                         epsilon, loss, q_value, buffer_size)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        time.time(),
                        rl_data.get('episode', 0),
                        rl_data.get('total_reward', 0),
                        rl_data.get('avg_reward', 0),
                        rl_data.get('epsilon', 1.0),
                        rl_data.get('loss', 0),
                        rl_data.get('q_value', 0),
                        rl_data.get('buffer_size', 0)
                    ))
                    
                    conn.commit()
                    conn.close()
                    
                    # Broadcast RL update
                    await self._broadcast_rl_update(rl_data)
                    
            except Exception as e:
                logger.error(f"Error monitoring RL training: {e}")
                
            await asyncio.sleep(10)  # Check every 10 seconds
            
    async def _broadcast_metrics_update(self):
        """Broadcast metrics to WebSocket clients"""
        if self.websocket_connections:
            update = {
                'type': 'metrics_update',
                'timestamp': time.time(),
                'data': list(self.metrics_buffer)[-10:]  # Last 10 metrics
            }
            
            await self._broadcast_to_all(update)
            
    async def _broadcast_price_update(self):
        """Broadcast price updates to WebSocket clients"""
        if self.websocket_connections:
            # Get latest prices for each symbol
            latest_prices = {}
            for item in reversed(self.price_buffer):
                if item['symbol'] not in latest_prices:
                    latest_prices[item['symbol']] = item
                if len(latest_prices) == 4:  # All symbols covered
                    break
                    
            update = {
                'type': 'price_update',
                'timestamp': time.time(),
                'data': latest_prices
            }
            
            await self._broadcast_to_all(update)
            
    async def _broadcast_rl_update(self, rl_data):
        """Broadcast RL training updates"""
        if self.websocket_connections:
            update = {
                'type': 'rl_update',
                'timestamp': time.time(),
                'data': rl_data
            }
            
            await self._broadcast_to_all(update)
            
    async def _broadcast_to_all(self, message):
        """Broadcast message to all WebSocket connections"""
        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except:
                disconnected.add(ws)
                
        self.websocket_connections -= disconnected
        
    async def _start_web_dashboard(self):
        """Start the enhanced web dashboard server"""
        app = web.Application()
        
        # Configure routes
        app.router.add_get('/', self.handle_index)
        app.router.add_get('/api/status', self.handle_status)
        app.router.add_get('/api/realtime/prices', self.handle_realtime_prices)
        app.router.add_get('/api/realtime/metrics', self.handle_realtime_metrics)
        app.router.add_get('/api/realtime/signals', self.handle_realtime_signals)
        app.router.add_get('/api/realtime/rl', self.handle_realtime_rl)
        app.router.add_post('/api/execute', self.handle_execute)
        app.router.add_get('/ws', self.handle_websocket)
        
        # Serve static files
        static_path = self.workspace / 'static'
        static_path.mkdir(exist_ok=True)
        app.router.add_static('/', static_path)
        
        # Create the enhanced dashboard HTML
        await self._create_enhanced_dashboard_html()
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 3011)
        await site.start()
        
    async def handle_index(self, request):
        """Serve the main dashboard"""
        self.request_count += 1
        html_path = self.workspace / 'static' / 'index.html'
        return web.FileResponse(html_path)
        
    async def handle_status(self, request):
        """Get comprehensive system status"""
        self.request_count += 1
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'f_drive_enabled': F_DRIVE_ENABLED,
            'services': {},
            'storage': {},
            'performance': {
                'requests_total': self.request_count,
                'errors_total': self.error_count,
                'websocket_connections': len(self.websocket_connections)
            }
        }
        
        # Check all services
        for service_id, config in self.services.items():
            health = await self._check_service_health(config['host'], config['port'])
            status['services'][service_id] = {
                'name': config['name'],
                'healthy': health,
                'port': config['port'],
                'critical': config.get('critical', False)
            }
            
        # Check storage
        if F_DRIVE_ENABLED:
            disk = psutil.disk_usage(str(F_DRIVE_ROOT))
            status['storage'] = {
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3),
                'percent_used': disk.percent
            }
            
        return web.json_response(status)
        
    async def handle_realtime_prices(self, request):
        """Get real-time price data"""
        self.request_count += 1
        
        # Get last N prices from buffer
        limit = int(request.query.get('limit', 100))
        prices = list(self.price_buffer)[-limit:]
        
        return web.json_response({
            'timestamp': time.time(),
            'count': len(prices),
            'data': prices
        })
        
    async def handle_realtime_metrics(self, request):
        """Get real-time system metrics"""
        self.request_count += 1
        
        # Get metrics from database
        db_path = self.metrics_path / 'realtime_metrics.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get last hour of metrics
        one_hour_ago = time.time() - 3600
        cursor.execute('''
            SELECT timestamp, cpu_percent, memory_percent, disk_free_gb,
                   requests_per_minute, active_connections
            FROM system_metrics
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 720
        ''', (one_hour_ago,))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'timestamp': row[0],
                'cpu': row[1],
                'memory': row[2],
                'disk_free_gb': row[3],
                'requests_per_minute': row[4],
                'connections': row[5]
            })
            
        conn.close()
        
        return web.json_response({
            'timestamp': time.time(),
            'count': len(metrics),
            'data': metrics
        })
        
    async def handle_realtime_signals(self, request):
        """Get real-time trading signals"""
        self.request_count += 1
        
        db_path = self.metrics_path / 'realtime_metrics.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, symbol, action, confidence, deepseek_score,
                   rl_score, entry_price, stop_loss, take_profit, risk_reward
            FROM realtime_signals
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'timestamp': row[0],
                'symbol': row[1],
                'action': row[2],
                'confidence': row[3],
                'deepseek_score': row[4],
                'rl_score': row[5],
                'entry_price': row[6],
                'stop_loss': row[7],
                'take_profit': row[8],
                'risk_reward': row[9]
            })
            
        conn.close()
        
        return web.json_response({
            'timestamp': time.time(),
            'count': len(signals),
            'data': signals
        })
        
    async def handle_realtime_rl(self, request):
        """Get real-time RL training metrics"""
        self.request_count += 1
        
        db_path = self.metrics_path / 'realtime_metrics.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, episode, total_reward, avg_reward,
                   epsilon, loss, q_value, buffer_size
            FROM rl_metrics
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'timestamp': row[0],
                'episode': row[1],
                'total_reward': row[2],
                'avg_reward': row[3],
                'epsilon': row[4],
                'loss': row[5],
                'q_value': row[6],
                'buffer_size': row[7]
            })
            
        conn.close()
        
        return web.json_response({
            'timestamp': time.time(),
            'count': len(metrics),
            'data': metrics
        })
        
    async def handle_execute(self, request):
        """Execute commands via MCP tools"""
        self.request_count += 1
        
        try:
            data = await request.json()
            tool = data.get('tool')
            method = data.get('method')
            params = data.get('params', {})
            
            # Execute based on tool
            result = await self._execute_mcp_command(tool, method, params)
            
            return web.json_response({
                'success': True,
                'result': result
            })
            
        except Exception as e:
            self.error_count += 1
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
            
    async def handle_websocket(self, request):
        """Handle WebSocket connections for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websocket_connections.add(ws)
        
        try:
            # Send initial data
            await ws.send_json({
                'type': 'connection',
                'status': 'connected',
                'timestamp': time.time()
            })
            
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self._process_websocket_message(ws, data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    
        finally:
            self.websocket_connections.remove(ws)
            
        return ws
        
    async def _process_websocket_message(self, ws, data):
        """Process incoming WebSocket messages"""
        msg_type = data.get('type')
        
        if msg_type == 'subscribe':
            channels = data.get('channels', [])
            await ws.send_json({
                'type': 'subscribed',
                'channels': channels,
                'timestamp': time.time()
            })
            
        elif msg_type == 'command':
            command = data.get('command')
            params = data.get('params', {})
            result = await self._execute_mcp_command(
                command.get('tool'),
                command.get('method'),
                params
            )
            await ws.send_json({
                'type': 'command_result',
                'result': result,
                'timestamp': time.time()
            })
            
    async def _check_service_health(self, host: str, port: int) -> bool:
        """Check if a service is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{host}:{port}/health"
                async with session.get(url, timeout=5) as response:
                    return response.status == 200
        except:
            return False
            
    async def _execute_mcp_command(self, tool: str, method: str, params: Dict) -> Any:
        """Execute command via MCP tools"""
        # Map tool to service
        tool_map = {
            'deepseek': {'host': 'localhost', 'port': 3008},
            'memory': {'host': 'localhost', 'port': 3002},
            'solana': {'host': 'localhost', 'port': 3005},
            'opencti': {'host': 'localhost', 'port': 3007}
        }
        
        if tool not in tool_map:
            raise ValueError(f"Unknown tool: {tool}")
            
        service = tool_map[tool]
        
        # Send request to MCP server
        async with aiohttp.ClientSession() as session:
            url = f"http://{service['host']}:{service['port']}/execute"
            payload = {
                'method': method,
                'params': params
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"MCP command failed: {response.status}")
                    
    async def _create_enhanced_dashboard_html(self):
        """Create the enhanced real-time dashboard HTML"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle AGI V6 - Real-Time Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
        }
        
        .pulse-animate {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        .neon-glow {
            text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88;
        }
        
        .cyber-border {
            border: 1px solid rgba(0, 255, 136, 0.5);
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }
        
        .data-stream {
            background: linear-gradient(180deg, transparent, rgba(0, 255, 136, 0.1), transparent);
            background-size: 100% 200%;
            animation: dataflow 3s ease-in-out infinite;
        }
        
        @keyframes dataflow {
            0% { background-position: 0% 0%; }
            50% { background-position: 0% 100%; }
            100% { background-position: 0% 0%; }
        }
    </style>
</head>
<body class="bg-gray-900 text-white overflow-hidden">
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect, useRef } = React;
        
        function OracleAGIRealtimeDashboard() {
            const [systemStatus, setSystemStatus] = useState(null);
            const [priceData, setPriceData] = useState({});
            const [systemMetrics, setSystemMetrics] = useState([]);
            const [tradingSignals, setTradingSignals] = useState([]);
            const [rlMetrics, setRlMetrics] = useState(null);
            const [connected, setConnected] = useState(false);
            const wsRef = useRef(null);
            const chartsRef = useRef({});
            
            useEffect(() => {
                // Initial data fetch
                fetchInitialData();
                
                // Setup WebSocket for real-time updates
                setupWebSocket();
                
                // Setup charts
                setupCharts();
                
                return () => {
                    if (wsRef.current) {
                        wsRef.current.close();
                    }
                };
            }, []);
            
            const fetchInitialData = async () => {
                try {
                    // Fetch system status
                    const statusRes = await fetch('/api/status');
                    const status = await statusRes.json();
                    setSystemStatus(status);
                    
                    // Fetch recent data
                    const pricesRes = await fetch('/api/realtime/prices?limit=100');
                    const prices = await pricesRes.json();
                    processPriceData(prices.data);
                    
                    const metricsRes = await fetch('/api/realtime/metrics?limit=100');
                    const metrics = await metricsRes.json();
                    setSystemMetrics(metrics.data);
                    
                    const signalsRes = await fetch('/api/realtime/signals');
                    const signals = await signalsRes.json();
                    setTradingSignals(signals.data);
                    
                } catch (error) {
                    console.error('Failed to fetch initial data:', error);
                }
            };
            
            const setupWebSocket = () => {
                wsRef.current = new WebSocket('ws://localhost:3011/ws');
                
                wsRef.current.onopen = () => {
                    setConnected(true);
                    console.log('WebSocket connected');
                    
                    // Subscribe to all channels
                    wsRef.current.send(JSON.stringify({
                        type: 'subscribe',
                        channels: ['prices', 'metrics', 'signals', 'rl']
                    }));
                };
                
                wsRef.current.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    
                    switch (data.type) {
                        case 'price_update':
                            processPriceData(Object.values(data.data));
                            break;
                            
                        case 'metrics_update':
                            setSystemMetrics(prev => [...prev, ...data.data].slice(-100));
                            updateMetricsChart(data.data);
                            break;
                            
                        case 'rl_update':
                            setRlMetrics(data.data);
                            break;
                            
                        case 'signal_update':
                            setTradingSignals(prev => [data.data, ...prev].slice(0, 50));
                            break;
                    }
                };
                
                wsRef.current.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    setConnected(false);
                };
                
                wsRef.current.onclose = () => {
                    setConnected(false);
                    // Reconnect after 5 seconds
                    setTimeout(setupWebSocket, 5000);
                };
            };
            
            const processPriceData = (prices) => {
                const latest = {};
                prices.forEach(price => {
                    if (!latest[price.symbol] || price.timestamp > latest[price.symbol].timestamp) {
                        latest[price.symbol] = price;
                    }
                });
                setPriceData(latest);
            };
            
            const setupCharts = () => {
                // Setup system metrics chart
                const metricsCanvas = document.getElementById('metricsChart');
                if (metricsCanvas) {
                    chartsRef.current.metrics = new Chart(metricsCanvas, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'CPU %',
                                data: [],
                                borderColor: 'rgb(255, 99, 132)',
                                tension: 0.1
                            }, {
                                label: 'Memory %',
                                data: [],
                                borderColor: 'rgb(54, 162, 235)',
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100
                                }
                            }
                        }
                    });
                }
            };
            
            const updateMetricsChart = (newData) => {
                if (chartsRef.current.metrics) {
                    const chart = chartsRef.current.metrics;
                    
                    newData.forEach(metric => {
                        const time = new Date(metric.timestamp * 1000).toLocaleTimeString();
                        chart.data.labels.push(time);
                        chart.data.datasets[0].data.push(metric.cpu);
                        chart.data.datasets[1].data.push(metric.memory);
                        
                        // Keep only last 50 points
                        if (chart.data.labels.length > 50) {
                            chart.data.labels.shift();
                            chart.data.datasets.forEach(dataset => dataset.data.shift());
                        }
                    });
                    
                    chart.update('none'); // Update without animation
                }
            };
            
            const executeCommand = async (tool, method, params = {}) => {
                try {
                    const response = await fetch('/api/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ tool, method, params })
                    });
                    const result = await response.json();
                    console.log('Command result:', result);
                } catch (error) {
                    console.error('Command execution failed:', error);
                }
            };
            
            return (
                <div className="h-screen flex flex-col bg-gray-900">
                    {/* Header */}
                    <div className="bg-gray-800 border-b border-gray-700 p-4">
                        <div className="flex justify-between items-center">
                            <div className="flex items-center space-x-4">
                                <h1 className="text-2xl font-bold neon-glow">
                                    🔮 Oracle AGI V6
                                </h1>
                                <span className="text-sm text-gray-400">
                                    Real-Time Dashboard
                                </span>
                            </div>
                            <div className="flex items-center space-x-4">
                                <div className="flex items-center space-x-2">
                                    <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500 pulse-animate' : 'bg-red-500'}`}></div>
                                    <span className="text-sm">
                                        {connected ? 'Connected' : 'Disconnected'}
                                    </span>
                                </div>
                                {systemStatus && systemStatus.f_drive_enabled && (
                                    <div className="text-sm">
                                        💾 F:\\ Drive: {systemStatus.storage.free_gb?.toFixed(1)} GB free
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                    
                    {/* Main Content */}
                    <div className="flex-1 overflow-hidden">
                        <div className="h-full grid grid-cols-12 gap-4 p-4">
                            {/* Left Panel - Services Status */}
                            <div className="col-span-3 space-y-4">
                                <div className="bg-gray-800 rounded-lg p-4 cyber-border">
                                    <h2 className="text-lg font-semibold mb-3">System Services</h2>
                                    <div className="space-y-2">
                                        {systemStatus && Object.entries(systemStatus.services).map(([id, service]) => (
                                            <div key={id} className="flex justify-between items-center p-2 bg-gray-700 rounded">
                                                <span className="text-sm">{service.name}</span>
                                                <div className={`w-2 h-2 rounded-full ${service.healthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                
                                {/* RL Training Status */}
                                {rlMetrics && (
                                    <div className="bg-gray-800 rounded-lg p-4 cyber-border">
                                        <h2 className="text-lg font-semibold mb-3">RL Training</h2>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span>Episode:</span>
                                                <span className="font-mono">{rlMetrics.episode}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Avg Reward:</span>
                                                <span className="font-mono">{rlMetrics.avg_reward?.toFixed(2)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Epsilon:</span>
                                                <span className="font-mono">{rlMetrics.epsilon?.toFixed(3)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Buffer Size:</span>
                                                <span className="font-mono">{rlMetrics.buffer_size?.toLocaleString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                            
                            {/* Center Panel - Price Data & Charts */}
                            <div className="col-span-6 space-y-4">
                                {/* Real-time Prices */}
                                <div className="bg-gray-800 rounded-lg p-4 cyber-border">
                                    <h2 className="text-lg font-semibold mb-3">Real-Time Prices</h2>
                                    <div className="grid grid-cols-2 gap-3">
                                        {Object.entries(priceData).map(([symbol, data]) => (
                                            <div key={symbol} className="bg-gray-700 rounded p-3 data-stream">
                                                <div className="flex justify-between items-center mb-1">
                                                    <span className="font-semibold">{symbol}</span>
                                                    <span className="text-xs text-gray-400">
                                                        {new Date(data.timestamp * 1000).toLocaleTimeString()}
                                                    </span>
                                                </div>
                                                <div className="text-2xl font-mono">
                                                    ${data.price?.toFixed(2)}
                                                </div>
                                                <div className="text-xs text-gray-400">
                                                    Spread: {(data.spread * 100).toFixed(2)}%
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                
                                {/* System Metrics Chart */}
                                <div className="bg-gray-800 rounded-lg p-4 cyber-border">
                                    <h2 className="text-lg font-semibold mb-3">System Performance</h2>
                                    <div className="h-64">
                                        <canvas id="metricsChart"></canvas>
                                    </div>
                                </div>
                            </div>
                            
                            {/* Right Panel - Trading Signals */}
                            <div className="col-span-3">
                                <div className="bg-gray-800 rounded-lg p-4 cyber-border h-full overflow-y-auto">
                                    <h2 className="text-lg font-semibold mb-3">Trading Signals</h2>
                                    <div className="space-y-3">
                                        {tradingSignals.map((signal, idx) => (
                                            <div key={idx} className="bg-gray-700 rounded p-3 hover:bg-gray-600 transition-all">
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="font-semibold">{signal.symbol}</span>
                                                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                                                        signal.action === 'BUY' ? 'bg-green-600' : 
                                                        signal.action === 'SELL' ? 'bg-red-600' : 'bg-yellow-600'
                                                    }`}>
                                                        {signal.action}
                                                    </span>
                                                </div>
                                                <div className="text-sm space-y-1">
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-400">Confidence:</span>
                                                        <span>{(signal.confidence * 100).toFixed(1)}%</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-gray-400">R:R:</span>
                                                        <span>{signal.risk_reward?.toFixed(2)}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {/* Footer Status Bar */}
                    <div className="bg-gray-800 border-t border-gray-700 p-2">
                        <div className="flex justify-between items-center text-xs text-gray-400">
                            <div className="flex space-x-4">
                                <span>Uptime: {systemStatus && Math.floor(systemStatus.uptime_seconds / 3600)}h</span>
                                <span>Requests: {systemStatus?.performance.requests_total}</span>
                                <span>WS Clients: {systemStatus?.performance.websocket_connections}</span>
                            </div>
                            <div>
                                Oracle AGI V6 © 2024 | F:\\ Drive Integration Active
                            </div>
                        </div>
                    </div>
                </div>
            );
        }
        
        ReactDOM.render(<OracleAGIRealtimeDashboard />, document.getElementById('root'));
    </script>
</body>
</html>'''
        
        # Save HTML file
        html_path = self.workspace / 'static' / 'index.html'
        html_path.parent.mkdir(exist_ok=True)
        
        with open(html_path, 'w') as f:
            f.write(html_content)

async def main():
    """Main entry point"""
    dashboard = OracleAGIRealtimeDashboard()
    await dashboard.start_unified_system()
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down Oracle AGI V6...")

if __name__ == "__main__":
    asyncio.run(main())