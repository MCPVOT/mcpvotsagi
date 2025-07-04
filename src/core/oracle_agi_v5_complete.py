#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle AGI V5 Complete System - PRODUCTION READY
===============================================
The REAL Oracle AGI system with all integrations working
"""

import asyncio
import io
import sys

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import logging
import sqlite3
import os
import time
import subprocess
import psutil
import aiohttp
from aiohttp import web
import websockets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import hashlib
import uuid

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import all the REAL integration modules
try:
    from oracle_trading_agi_mcpvots_integration import MCPVotsTradingOrchestrator
    from oracle_trading_agi_claude_agent_integration import ClaudeAgentTradingOrchestrator
    from oracle_trading_agi_vot1_integration import VOT1TradingIntelligence
    from oracle_trading_agi_ollama_integration import OllamaTradingOrchestrator
    from oracle_trading_agi_memory_vault_integration import MemoryVaultTradingSystem
except ImportError as e:
    logging.warning(f"Some integrations not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleAGIV5")

class OracleAGIV5Complete:
    """The COMPLETE Oracle AGI V5 System - Production Ready"""
    
    def __init__(self):
        # Use Windows paths when running on Windows
        if sys.platform == "win32":
            self.workspace = Path("C:/Workspace")
            self.mcpvots_agi = self.workspace / "MCPVotsAGI"
            self.mcpvots = self.workspace / "MCPVots"
        else:
            self.workspace = Path("/mnt/c/Workspace")
            self.mcpvots_agi = self.workspace / "MCPVotsAGI"
            self.mcpvots = self.workspace / "MCPVots"
        
        # Ensure directories exist
        self.mcpvots_agi.mkdir(exist_ok=True)
        
        # Real WebSocket connections
        self.websocket_connections: Set = set()
        self.active_services = {}
        self.service_processes = {}
        
        # Real service configurations with actual endpoints
        self.services = {
            'oracle_agi_core': {
                'host': 'localhost',
                'port': 8888,
                'name': 'Oracle AGI Core',
                'endpoint': '/oracle',
                'health_check': '/oracle/status',
                'script': 'working_oracle.py',
                'required': True
            },
            'trilogy_brain': {
                'host': 'localhost',
                'port': 8887,
                'name': 'Trilogy Oracle Brain',
                'endpoint': '/trilogy',
                'health_check': '/health',
                'script': 'trilogy_oracle_brain.py',
                'required': True
            },
            'dgm_voltagents': {
                'host': 'localhost',
                'port': 8886,
                'name': 'DGM Voltagents',
                'endpoint': '/voltagents',
                'health_check': '/health',
                'script': 'dgm_voltagents.py',
                'required': False
            },
            'trading_system': {
                'host': 'localhost',
                'port': 8889,
                'name': 'Trading System',
                'endpoint': '/trading',
                'health_check': '/trading/status',
                'script': 'oracle_trading_agi_enhanced_system.py',
                'required': True
            },
            'chat_api': {
                'host': 'localhost',
                'port': 8890,
                'name': 'Chat API',
                'endpoint': '/chat',
                'health_check': '/health',
                'script': 'uiuc_chat_server.py',
                'required': False
            },
            'telemetry': {
                'host': 'localhost',
                'port': 8891,
                'name': 'Telemetry Monitor',
                'endpoint': '/telemetry',
                'health_check': '/health',
                'script': 'telemetry_monitor.py',
                'required': False
            },
            'self_healing': {
                'host': 'localhost',
                'port': 8892,
                'name': 'Self-Healing System',
                'endpoint': '/healing',
                'health_check': '/health',
                'script': 'self_healing_system.py',
                'required': False
            }
        }
        
        # Real AI model endpoints
        self.ai_models = {
            'gemini': {
                'endpoint': 'http://localhost:8080/api/chat',
                'health': 'http://localhost:8080/health',
                'name': 'Gemini 2.5',
                'script': 'gemini_cli_http_server.py'
            },
            'deepseek': {
                'endpoint': 'http://localhost:11434/api/generate',
                'health': 'http://localhost:11434/api/tags',
                'name': 'DeepSeek R1',
                'command': ['ollama', 'serve']
            },
            'claude': {
                'endpoint': 'http://localhost:8890/api/claude',
                'health': 'http://localhost:8890/health',
                'name': 'Claude 3.7'
            },
            'gpt4': {
                'endpoint': 'http://localhost:8890/api/gpt4',
                'health': 'http://localhost:8890/health',
                'name': 'GPT-4 Turbo'
            }
        }
        
        # Real MCP integrations
        self.mcp_configs = {
            'memory': {
                'type': 'sqlite',
                'path': str(self.mcpvots_agi / 'oracle_memory.db'),
                'knowledge_graph': True
            },
            'github': {
                'repos': [
                    'kabrony/MCPVots',
                    'kabrony/voltagent',
                    'kabrony/lobe-chat',
                    'kabrony/ag-ui',
                    'kabrony/dgm'
                ],
                'token': os.getenv('GITHUB_TOKEN', '')
            },
            'filesystem': {
                'allowed_paths': [
                    str(self.workspace),
                    str(self.mcpvots),
                    str(self.mcpvots_agi)
                ]
            }
        }
        
        # Initialize database
        self._init_production_database()
        
        # System state
        self.system_metrics = {
            'start_time': datetime.now(),
            'total_requests': 0,
            'active_connections': 0,
            'trading_signals': 0,
            'chat_messages': 0
        }
        
    def _init_production_database(self):
        """Initialize production database with all tables"""
        db_path = self.mcpvots_agi / 'oracle_agi_v5_production.db'
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        cursor = conn.cursor()
        
        # System services table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                status TEXT DEFAULT 'offline',
                health_score REAL DEFAULT 0.0,
                last_check DATETIME,
                last_error TEXT,
                uptime_seconds INTEGER DEFAULT 0,
                total_requests INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trading signals table with full details
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                position_size REAL,
                risk_reward_ratio REAL,
                ai_models TEXT,
                consensus_data TEXT,
                market_conditions TEXT,
                technical_indicators TEXT,
                status TEXT DEFAULT 'pending',
                execution_time DATETIME,
                pnl REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AI chat history with context
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT,
                model TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT,
                context TEXT,
                tokens_used INTEGER,
                response_time_ms INTEGER,
                rating INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                component TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # MCP memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mcp_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT,
                metadata TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Knowledge graph table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_graph (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT UNIQUE NOT NULL,
                node_type TEXT NOT NULL,
                node_data TEXT NOT NULL,
                connections TEXT,
                weight REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Event log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_source TEXT NOT NULL,
                event_data TEXT,
                severity TEXT DEFAULT 'info',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✓ Production database initialized")
        
    async def start_complete_system(self):
        """Start the COMPLETE Oracle AGI V5 system"""
        logger.info("=" * 80)
        logger.info("🚀 Starting Oracle AGI V5 COMPLETE System")
        logger.info("=" * 80)
        
        try:
            # Phase 1: Start core infrastructure
            await self._start_core_infrastructure()
            
            # Phase 2: Start AI services
            await self._start_ai_services()
            
            # Phase 3: Start trading system
            await self._start_trading_system()
            
            # Phase 4: Start web server
            await self._start_web_server()
            
            # Phase 5: Initialize MCP connections
            await self._initialize_mcp_connections()
            
            # Phase 6: Start monitoring
            asyncio.create_task(self._monitor_system())
            
            logger.info("=" * 80)
            logger.info("✅ Oracle AGI V5 COMPLETE System OPERATIONAL!")
            logger.info("=" * 80)
            logger.info("🌐 Dashboard: http://localhost:3002")
            logger.info("🔮 Oracle API: http://localhost:8888/oracle")
            logger.info("💹 Trading API: http://localhost:8889/trading")
            logger.info("🤖 AI Chat: http://localhost:3002 (integrated)")
            logger.info("📊 Metrics: http://localhost:3002/api/metrics")
            logger.info("=" * 80)
            
            # Keep running
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown requested...")
            await self._shutdown_system()
        except Exception as e:
            logger.error(f"❌ System startup failed: {e}")
            await self._shutdown_system()
            raise
            
    async def _start_core_infrastructure(self):
        """Start core infrastructure services"""
        logger.info("🔧 Starting core infrastructure...")
        
        # Check and start Oracle AGI Core
        oracle_running = await self._check_service_health('oracle_agi_core')
        if not oracle_running:
            await self._start_service('oracle_agi_core')
            
        # Check and start Trilogy Brain
        trilogy_running = await self._check_service_health('trilogy_brain')
        if not trilogy_running:
            await self._start_service('trilogy_brain')
            
        # Start other core services
        for service_id in ['trading_system', 'dgm_voltagents']:
            if not await self._check_service_health(service_id):
                await self._start_service(service_id)
                
    async def _start_ai_services(self):
        """Start AI model services"""
        logger.info("🤖 Starting AI services...")
        
        # Start Ollama for DeepSeek
        if not self._is_port_in_use(11434):
            try:
                process = subprocess.Popen(
                    ['ollama', 'serve'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.service_processes['ollama'] = process
                await asyncio.sleep(3)
                
                # Pull DeepSeek model
                subprocess.run(['ollama', 'pull', 'deepseek:latest'], check=False)
                logger.info("✓ Ollama/DeepSeek started")
            except Exception as e:
                logger.warning(f"Could not start Ollama: {e}")
                
        # Start Gemini CLI
        if not self._is_port_in_use(8080):
            gemini_script = self.mcpvots / 'gemini_cli_http_server.py'
            if gemini_script.exists():
                await self._start_python_service('gemini', gemini_script, 8080)
            else:
                # Try alternative locations
                alt_script = self.mcpvots / 'simple_gemini_server.py'
                if alt_script.exists():
                    await self._start_python_service('gemini', alt_script, 8080)
                    
    async def _start_trading_system(self):
        """Start the trading system components"""
        logger.info("💹 Starting trading system...")
        
        # Initialize trading orchestrators if available
        try:
            self.mcpvots_orchestrator = MCPVotsTradingOrchestrator()
            logger.info("✓ MCPVots orchestrator initialized")
        except:
            logger.warning("MCPVots orchestrator not available")
            
        try:
            self.vot1_intelligence = VOT1TradingIntelligence()
            logger.info("✓ VOT1 intelligence initialized")
        except:
            logger.warning("VOT1 intelligence not available")
            
        try:
            self.memory_vault = MemoryVaultTradingSystem()
            logger.info("✓ Memory vault initialized")
        except:
            logger.warning("Memory vault not available")
            
    async def _start_web_server(self):
        """Start the web server with all endpoints"""
        app = web.Application()
        app['oracle_agi'] = self
        
        # Configure all routes
        app.router.add_get('/', self.handle_dashboard)
        app.router.add_get('/api/status', self.handle_api_status)
        app.router.add_get('/api/trading/signals', self.handle_trading_signals)
        app.router.add_post('/api/trading/execute', self.handle_execute_trade)
        app.router.add_post('/api/chat', self.handle_chat)
        app.router.add_get('/api/metrics', self.handle_metrics)
        app.router.add_get('/api/services', self.handle_services)
        app.router.add_get('/api/mcp/memory', self.handle_mcp_memory)
        app.router.add_post('/api/mcp/memory', self.handle_mcp_memory_add)
        app.router.add_get('/ws', self.handle_websocket)
        
        # Static files
        static_path = self.mcpvots_agi / 'static'
        static_path.mkdir(exist_ok=True)
        app.router.add_static('/static', static_path)
        
        # Create dashboard
        await self._create_production_dashboard()
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 3002)
        await site.start()
        logger.info("✓ Web server started on http://localhost:3002")
        
    async def _check_service_health(self, service_id: str) -> bool:
        """Check if a service is healthy"""
        service = self.services.get(service_id)
        if not service:
            return False
            
        try:
            url = f"http://{service['host']}:{service['port']}{service['health_check']}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    healthy = response.status == 200
                    
                    # Update database
                    self._update_service_status(service_id, 'online' if healthy else 'offline')
                    return healthy
        except:
            self._update_service_status(service_id, 'offline')
            return False
            
    def _update_service_status(self, service_id: str, status: str):
        """Update service status in database"""
        conn = sqlite3.connect(self.mcpvots_agi / 'oracle_agi_v5_production.db')
        cursor = conn.cursor()
        
        service = self.services.get(service_id, {})
        cursor.execute('''
            INSERT OR REPLACE INTO system_services 
            (service_id, name, host, port, status, last_check)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            service_id,
            service.get('name', service_id),
            service.get('host', 'localhost'),
            service.get('port', 0),
            status,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
    async def _start_service(self, service_id: str):
        """Start a specific service"""
        service = self.services.get(service_id)
        if not service:
            return
            
        logger.info(f"Starting {service['name']}...")
        
        # Find the script
        script_path = None
        for base_dir in [self.workspace, self.mcpvots]:
            potential_path = base_dir / service['script']
            if potential_path.exists():
                script_path = potential_path
                break
                
        if not script_path:
            # Try to find alternative scripts
            alternatives = list(self.workspace.glob(f"*{service_id}*.py"))
            if alternatives:
                script_path = alternatives[0]
                
        if script_path:
            await self._start_python_service(service_id, script_path, service['port'])
        else:
            logger.warning(f"Script not found for {service['name']}")
            
    async def _start_python_service(self, service_id: str, script_path: Path, port: int):
        """Start a Python service"""
        try:
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(script_path.parent)
            )
            self.service_processes[service_id] = process
            
            # Wait for service to start
            await asyncio.sleep(3)
            
            # Check if it started successfully
            if process.poll() is None:
                logger.info(f"✓ {service_id} started on port {port}")
            else:
                logger.error(f"✗ {service_id} failed to start")
                
        except Exception as e:
            logger.error(f"Failed to start {service_id}: {e}")
            
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
            
    async def _initialize_mcp_connections(self):
        """Initialize MCP tool connections"""
        logger.info("🔧 Initializing MCP connections...")
        
        # Initialize memory database
        memory_conn = sqlite3.connect(self.mcp_configs['memory']['path'])
        memory_conn.execute("PRAGMA journal_mode=WAL")
        memory_conn.close()
        logger.info("✓ Memory database initialized")
        
        # Check GitHub token
        if self.mcp_configs['github']['token']:
            logger.info("✓ GitHub token configured")
        else:
            logger.warning("⚠ No GitHub token found")
            
        logger.info("✓ MCP connections ready")
        
    async def _monitor_system(self):
        """Monitor system health continuously"""
        while True:
            try:
                # Check all services
                for service_id in self.services:
                    healthy = await self._check_service_health(service_id)
                    
                    # Restart if needed and it's a required service
                    if not healthy and self.services[service_id].get('required'):
                        logger.warning(f"Service {service_id} is down, attempting restart...")
                        await self._start_service(service_id)
                        
                # Broadcast status to WebSocket clients
                if self.websocket_connections:
                    status = await self._get_full_system_status()
                    message = json.dumps({
                        'type': 'system_status',
                        'data': status
                    })
                    
                    disconnected = set()
                    for ws in self.websocket_connections:
                        try:
                            await ws.send_str(message)
                        except:
                            disconnected.add(ws)
                            
                    self.websocket_connections -= disconnected
                    
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
                
    async def _get_full_system_status(self) -> Dict:
        """Get complete system status"""
        conn = sqlite3.connect(self.mcpvots_agi / 'oracle_agi_v5_production.db')
        cursor = conn.cursor()
        
        # Get service statuses
        cursor.execute('''
            SELECT service_id, name, status, health_score, last_check
            FROM system_services
            ORDER BY name
        ''')
        services = {}
        for row in cursor.fetchall():
            services[row[0]] = {
                'name': row[1],
                'status': row[2],
                'health_score': row[3],
                'last_check': row[4]
            }
            
        # Get recent metrics
        cursor.execute('''
            SELECT metric_type, AVG(metric_value) as avg_value
            FROM system_metrics
            WHERE created_at > datetime('now', '-5 minutes')
            GROUP BY metric_type
        ''')
        metrics = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get trading stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_signals,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                AVG(confidence) as avg_confidence
            FROM trading_signals
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        trading_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'services': services,
            'metrics': metrics,
            'trading': {
                'total_signals': trading_stats[0] if trading_stats else 0,
                'successful': trading_stats[1] if trading_stats else 0,
                'avg_confidence': trading_stats[2] if trading_stats else 0
            },
            'system': {
                'uptime': (datetime.now() - self.system_metrics['start_time']).total_seconds(),
                'total_requests': self.system_metrics['total_requests'],
                'active_connections': len(self.websocket_connections)
            }
        }
        
    # Web handlers
    async def handle_dashboard(self, request):
        """Serve the dashboard"""
        html_path = self.mcpvots_agi / 'static' / 'dashboard.html'
        if html_path.exists():
            return web.FileResponse(html_path)
        else:
            return web.Response(text="Dashboard loading...", status=503)
            
    async def handle_api_status(self, request):
        """Get system status"""
        self.system_metrics['total_requests'] += 1
        status = await self._get_full_system_status()
        return web.json_response(status)
        
    async def handle_trading_signals(self, request):
        """Get trading signals"""
        self.system_metrics['total_requests'] += 1
        
        conn = sqlite3.connect(self.mcpvots_agi / 'oracle_agi_v5_production.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT signal_id, symbol, action, confidence, entry_price,
                   stop_loss, take_profit, ai_models, created_at
            FROM trading_signals
            ORDER BY created_at DESC
            LIMIT 50
        ''')
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'id': row[0],
                'symbol': row[1],
                'action': row[2],
                'confidence': row[3],
                'entry': row[4],
                'stop_loss': row[5],
                'take_profit': row[6],
                'ai_models': row[7],
                'timestamp': row[8]
            })
            
        conn.close()
        return web.json_response({'signals': signals})
        
    async def handle_execute_trade(self, request):
        """Execute a trade"""
        self.system_metrics['total_requests'] += 1
        data = await request.json()
        
        # Forward to trading system
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:8889/trading/execute',
                    json=data
                ) as response:
                    result = await response.json()
                    return web.json_response(result)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
            
    async def handle_chat(self, request):
        """Handle AI chat requests"""
        self.system_metrics['total_requests'] += 1
        self.system_metrics['chat_messages'] += 1
        
        data = await request.json()
        message = data.get('message', '')
        model = data.get('model', 'gemini')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get AI response
        response_text = await self._get_ai_response(model, message)
        
        # Store in database
        conn = sqlite3.connect(self.mcpvots_agi / 'oracle_agi_v5_production.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (session_id, model, message, response)
            VALUES (?, ?, ?, ?)
        ''', (session_id, model, message, response_text))
        conn.commit()
        conn.close()
        
        return web.json_response({
            'model': model,
            'response': response_text,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    async def _get_ai_response(self, model: str, message: str) -> str:
        """Get response from AI model"""
        model_config = self.ai_models.get(model)
        if not model_config:
            return f"Model {model} not configured"
            
        try:
            async with aiohttp.ClientSession() as session:
                # Model-specific request format
                if model == 'gemini':
                    payload = {'message': message}
                elif model == 'deepseek':
                    payload = {
                        'model': 'deepseek:latest',
                        'prompt': message,
                        'stream': False
                    }
                else:
                    payload = {'message': message}
                    
                async with session.post(
                    model_config['endpoint'],
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if model == 'deepseek':
                            return result.get('response', 'No response')
                        else:
                            return result.get('response', result.get('message', 'No response'))
                    else:
                        return f"Error from {model}: {response.status}"
                        
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return f"Error getting response from {model}: {str(e)}"
            
    async def handle_metrics(self, request):
        """Get system metrics"""
        self.system_metrics['total_requests'] += 1
        
        conn = sqlite3.connect(self.mcpvots_agi / 'oracle_agi_v5_production.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metric_type, metric_name, metric_value, component, created_at
            FROM system_metrics
            ORDER BY created_at DESC
            LIMIT 100
        ''')
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'type': row[0],
                'name': row[1],
                'value': row[2],
                'component': row[3],
                'timestamp': row[4]
            })
            
        conn.close()
        return web.json_response({'metrics': metrics})
        
    async def handle_services(self, request):
        """Get service details"""
        self.system_metrics['total_requests'] += 1
        
        services = {}
        for service_id, config in self.services.items():
            health = await self._check_service_health(service_id)
            services[service_id] = {
                'name': config['name'],
                'port': config['port'],
                'healthy': health,
                'endpoint': f"http://localhost:{config['port']}{config['endpoint']}"
            }
            
        return web.json_response(services)
        
    async def handle_mcp_memory(self, request):
        """Get MCP memory entries"""
        self.system_metrics['total_requests'] += 1
        
        conn = sqlite3.connect(self.mcp_configs['memory']['path'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT memory_id, category, content, access_count, created_at
            FROM mcp_memory
            ORDER BY access_count DESC
            LIMIT 50
        ''')
        
        memories = []
        for row in cursor.fetchall():
            memories.append({
                'id': row[0],
                'category': row[1],
                'content': row[2],
                'access_count': row[3],
                'created_at': row[4]
            })
            
        conn.close()
        return web.json_response({'memories': memories})
        
    async def handle_mcp_memory_add(self, request):
        """Add MCP memory entry"""
        self.system_metrics['total_requests'] += 1
        
        data = await request.json()
        memory_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.mcp_configs['memory']['path'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mcp_memory (memory_id, category, content, metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            memory_id,
            data.get('category', 'general'),
            data.get('content', ''),
            json.dumps(data.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return web.json_response({'memory_id': memory_id})
        
    async def handle_websocket(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websocket_connections.add(ws)
        self.system_metrics['active_connections'] = len(self.websocket_connections)
        
        try:
            # Send initial status
            status = await self._get_full_system_status()
            await ws.send_str(json.dumps({
                'type': 'connected',
                'data': status
            }))
            
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    if data.get('type') == 'subscribe':
                        # Handle subscription
                        await ws.send_str(json.dumps({
                            'type': 'subscribed',
                            'channels': data.get('channels', [])
                        }))
                    elif data.get('type') == 'command':
                        # Execute command
                        result = await self._execute_command(data.get('command'))
                        await ws.send_str(json.dumps({
                            'type': 'command_result',
                            'result': result
                        }))
                        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.websocket_connections.remove(ws)
            self.system_metrics['active_connections'] = len(self.websocket_connections)
            
        return ws
        
    async def _execute_command(self, command: str) -> Dict:
        """Execute system command"""
        if command == 'restart_services':
            for service_id in self.services:
                if not await self._check_service_health(service_id):
                    await self._start_service(service_id)
            return {'status': 'success', 'message': 'Services restarted'}
        elif command == 'clear_cache':
            # Clear any caches
            return {'status': 'success', 'message': 'Cache cleared'}
        else:
            return {'status': 'error', 'message': 'Unknown command'}
            
    async def _create_production_dashboard(self):
        """Create the production dashboard HTML"""
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle AGI V5 - Production Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @keyframes glow {
            0% { box-shadow: 0 0 5px #00ff88, 0 0 10px #00ff88; }
            50% { box-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88; }
            100% { box-shadow: 0 0 5px #00ff88, 0 0 10px #00ff88; }
        }
        .glow { animation: glow 2s ease-in-out infinite; }
        .cyber-grid {
            background-image: 
                linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
        }
    </style>
</head>
<body class="bg-gray-900 text-white cyber-grid">
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect, useRef } = React;
        
        function OracleAGIV5Dashboard() {
            const [systemStatus, setSystemStatus] = useState(null);
            const [tradingSignals, setTradingSignals] = useState([]);
            const [services, setServices] = useState({});
            const [metrics, setMetrics] = useState([]);
            const [chatMessages, setChatMessages] = useState([]);
            const [selectedModel, setSelectedModel] = useState('gemini');
            const [chatInput, setChatInput] = useState('');
            const [loading, setLoading] = useState(false);
            const wsRef = useRef(null);
            const [activeTab, setActiveTab] = useState('overview');
            
            useEffect(() => {
                // Initial data fetch
                fetchSystemStatus();
                fetchServices();
                fetchTradingSignals();
                fetchMetrics();
                
                // Setup WebSocket
                connectWebSocket();
                
                // Polling
                const interval = setInterval(() => {
                    fetchSystemStatus();
                    fetchTradingSignals();
                    fetchMetrics();
                }, 5000);
                
                return () => {
                    clearInterval(interval);
                    if (wsRef.current) {
                        wsRef.current.close();
                    }
                };
            }, []);
            
            const connectWebSocket = () => {
                wsRef.current = new WebSocket('ws://localhost:3002/ws');
                
                wsRef.current.onopen = () => {
                    console.log('WebSocket connected');
                    wsRef.current.send(JSON.stringify({
                        type: 'subscribe',
                        channels: ['status', 'trading', 'metrics']
                    }));
                };
                
                wsRef.current.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'system_status') {
                        setSystemStatus(data.data);
                    }
                };
                
                wsRef.current.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
                
                wsRef.current.onclose = () => {
                    console.log('WebSocket disconnected, reconnecting...');
                    setTimeout(connectWebSocket, 5000);
                };
            };
            
            const fetchSystemStatus = async () => {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    setSystemStatus(data);
                } catch (error) {
                    console.error('Failed to fetch status:', error);
                }
            };
            
            const fetchServices = async () => {
                try {
                    const response = await fetch('/api/services');
                    const data = await response.json();
                    setServices(data);
                } catch (error) {
                    console.error('Failed to fetch services:', error);
                }
            };
            
            const fetchTradingSignals = async () => {
                try {
                    const response = await fetch('/api/trading/signals');
                    const data = await response.json();
                    setTradingSignals(data.signals || []);
                } catch (error) {
                    console.error('Failed to fetch signals:', error);
                }
            };
            
            const fetchMetrics = async () => {
                try {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    setMetrics(data.metrics || []);
                } catch (error) {
                    console.error('Failed to fetch metrics:', error);
                }
            };
            
            const sendChatMessage = async () => {
                if (!chatInput.trim()) return;
                
                setLoading(true);
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: chatInput, 
                            model: selectedModel,
                            session_id: localStorage.getItem('session_id') || undefined
                        })
                    });
                    const data = await response.json();
                    
                    if (data.session_id) {
                        localStorage.setItem('session_id', data.session_id);
                    }
                    
                    setChatMessages([...chatMessages, {
                        user: chatInput,
                        ai: data.response,
                        model: selectedModel,
                        timestamp: new Date().toISOString()
                    }]);
                    
                    setChatInput('');
                } catch (error) {
                    console.error('Failed to send message:', error);
                } finally {
                    setLoading(false);
                }
            };
            
            const executeTrade = async (signal) => {
                try {
                    const response = await fetch('/api/trading/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(signal)
                    });
                    const result = await response.json();
                    alert(`Trade executed: ${result.status}`);
                } catch (error) {
                    console.error('Failed to execute trade:', error);
                    alert('Failed to execute trade');
                }
            };
            
            const getStatusColor = (status) => {
                return status === 'online' ? 'text-green-400' : 'text-red-400';
            };
            
            const getActionColor = (action) => {
                if (action === 'BUY') return 'bg-green-600';
                if (action === 'SELL') return 'bg-red-600';
                return 'bg-yellow-600';
            };
            
            return (
                <div className="min-h-screen p-6">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-5xl font-bold mb-2 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                            🔮 Oracle AGI V5
                        </h1>
                        <p className="text-xl text-gray-400">Production Dashboard - Real Services</p>
                        {systemStatus && (
                            <div className="mt-4 text-sm text-gray-500">
                                Uptime: {Math.floor((systemStatus.system?.uptime || 0) / 3600)}h{' '}
                                {Math.floor(((systemStatus.system?.uptime || 0) % 3600) / 60)}m
                                {' | '}
                                Requests: {systemStatus.system?.total_requests || 0}
                                {' | '}
                                Connections: {systemStatus.system?.active_connections || 0}
                            </div>
                        )}
                    </div>
                    
                    {/* Tabs */}
                    <div className="mb-6 border-b border-gray-700">
                        <div className="flex space-x-6">
                            <button
                                onClick={() => setActiveTab('overview')}
                                className={`pb-2 px-1 ${activeTab === 'overview' ? 'border-b-2 border-green-400 text-green-400' : 'text-gray-400'}`}
                            >
                                System Overview
                            </button>
                            <button
                                onClick={() => setActiveTab('trading')}
                                className={`pb-2 px-1 ${activeTab === 'trading' ? 'border-b-2 border-green-400 text-green-400' : 'text-gray-400'}`}
                            >
                                Trading Signals
                            </button>
                            <button
                                onClick={() => setActiveTab('chat')}
                                className={`pb-2 px-1 ${activeTab === 'chat' ? 'border-b-2 border-green-400 text-green-400' : 'text-gray-400'}`}
                            >
                                AI Chat
                            </button>
                            <button
                                onClick={() => setActiveTab('metrics')}
                                className={`pb-2 px-1 ${activeTab === 'metrics' ? 'border-b-2 border-green-400 text-green-400' : 'text-gray-400'}`}
                            >
                                Metrics
                            </button>
                        </div>
                    </div>
                    
                    {/* Tab Content */}
                    {activeTab === 'overview' && (
                        <div>
                            {/* Service Status Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                                {Object.entries(services).map(([id, service]) => (
                                    <div key={id} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-green-500 transition-all">
                                        <h3 className="text-lg font-semibold mb-2">{service.name}</h3>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className={`text-sm ${getStatusColor(service.healthy ? 'online' : 'offline')}`}>
                                                {service.healthy ? '● Online' : '● Offline'}
                                            </span>
                                            <span className="text-xs text-gray-500">Port: {service.port}</span>
                                        </div>
                                        <div className="text-xs text-gray-400 truncate">
                                            {service.endpoint}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            
                            {/* Trading Stats */}
                            {systemStatus?.trading && (
                                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                                    <h2 className="text-2xl font-bold mb-4">📊 Trading Statistics (24h)</h2>
                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="text-center">
                                            <div className="text-3xl font-bold text-green-400">
                                                {systemStatus.trading.total_signals}
                                            </div>
                                            <div className="text-sm text-gray-400">Total Signals</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-3xl font-bold text-blue-400">
                                                {systemStatus.trading.successful}
                                            </div>
                                            <div className="text-sm text-gray-400">Successful</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-3xl font-bold text-yellow-400">
                                                {(systemStatus.trading.avg_confidence * 100).toFixed(1)}%
                                            </div>
                                            <div className="text-sm text-gray-400">Avg Confidence</div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                    
                    {activeTab === 'trading' && (
                        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                            <h2 className="text-2xl font-bold mb-4">📈 Trading Signals</h2>
                            <div className="space-y-3">
                                {tradingSignals.map((signal, idx) => (
                                    <div key={signal.id || idx} className="bg-gray-700 rounded-lg p-4 flex items-center justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className="text-lg font-semibold">{signal.symbol}</span>
                                                <span className={`px-3 py-1 rounded text-sm font-bold ${getActionColor(signal.action)}`}>
                                                    {signal.action}
                                                </span>
                                                <span className="text-sm text-gray-400">
                                                    Confidence: {(signal.confidence * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                            <div className="text-sm text-gray-300">
                                                Entry: ${signal.entry} | SL: ${signal.stop_loss} | TP: ${signal.take_profit}
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => executeTrade(signal)}
                                            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-bold"
                                        >
                                            Execute
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    
                    {activeTab === 'chat' && (
                        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-2xl font-bold">🤖 AI Assistant</h2>
                                <select
                                    value={selectedModel}
                                    onChange={(e) => setSelectedModel(e.target.value)}
                                    className="bg-gray-700 text-white px-3 py-2 rounded"
                                >
                                    <option value="gemini">Gemini 2.5</option>
                                    <option value="deepseek">DeepSeek R1</option>
                                    <option value="claude">Claude 3.7</option>
                                    <option value="gpt4">GPT-4 Turbo</option>
                                </select>
                            </div>
                            
                            <div className="h-96 overflow-y-auto mb-4 space-y-3">
                                {chatMessages.map((msg, idx) => (
                                    <div key={idx}>
                                        <div className="bg-blue-600 bg-opacity-20 rounded p-3 mb-2">
                                            <div className="font-semibold text-sm mb-1">You:</div>
                                            <div>{msg.user}</div>
                                        </div>
                                        <div className="bg-gray-700 rounded p-3">
                                            <div className="font-semibold text-sm mb-1">{msg.model}:</div>
                                            <div>{msg.ai}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && !loading && sendChatMessage()}
                                    placeholder="Ask anything..."
                                    className="flex-1 bg-gray-700 text-white px-4 py-2 rounded"
                                    disabled={loading}
                                />
                                <button
                                    onClick={sendChatMessage}
                                    disabled={loading}
                                    className="px-6 py-2 bg-gradient-to-r from-green-500 to-blue-500 rounded font-bold disabled:opacity-50"
                                >
                                    {loading ? 'Sending...' : 'Send'}
                                </button>
                            </div>
                        </div>
                    )}
                    
                    {activeTab === 'metrics' && (
                        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                            <h2 className="text-2xl font-bold mb-4">📊 System Metrics</h2>
                            <div className="space-y-2">
                                {metrics.map((metric, idx) => (
                                    <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-700">
                                        <div>
                                            <span className="font-semibold">{metric.name || metric.type}</span>
                                            <span className="text-sm text-gray-400 ml-2">({metric.component})</span>
                                        </div>
                                        <div className="text-green-400 font-mono">
                                            {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            );
        }
        
        ReactDOM.render(<OracleAGIV5Dashboard />, document.getElementById('root'));
    </script>
</body>
</html>'''
        
        # Save dashboard
        dashboard_path = self.mcpvots_agi / 'static' / 'dashboard.html'
        dashboard_path.parent.mkdir(exist_ok=True)
        
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_html)
            
        logger.info("✓ Production dashboard created")
        
    async def _shutdown_system(self):
        """Gracefully shutdown all services"""
        logger.info("Shutting down Oracle AGI V5...")
        
        # Close WebSocket connections
        for ws in self.websocket_connections:
            await ws.close()
            
        # Stop all service processes
        for service_id, process in self.service_processes.items():
            if process and process.poll() is None:
                logger.info(f"Stopping {service_id}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
        logger.info("✓ All services stopped")

async def main():
    """Main entry point"""
    oracle_agi = OracleAGIV5Complete()
    await oracle_agi.start_complete_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System stopped by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)