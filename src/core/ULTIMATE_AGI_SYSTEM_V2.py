#!/usr/bin/env python3
"""
ULTIMATE AGI SYSTEM V2 - Enhanced with MCPVots Integration
==========================================================
🚀 Enhanced with MCPVots self-healing, browser automation, and desktop deployment
"""

import asyncio
import json
import os
import sys
import time
import subprocess
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque, defaultdict
from typing import Optional, Tuple
import random
import logging
import requests
import yaml
import tempfile
import shutil
import threading
import websockets
import socket
from urllib.parse import urlparse

# Core imports
try:
    from aiohttp import web
    import aiohttp
    import psutil
    import numpy as np
    import pandas as pd
    import ipfshttpclient
    HAS_DEPS = True
except ImportError:
    print("🔧 Installing core dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "aiohttp", "psutil", "numpy", "pandas", "pyyaml", "requests", "ipfshttpclient"])
    from aiohttp import web
    import aiohttp
    import psutil
    import numpy as np
    import pandas as pd
    import ipfshttpclient
    HAS_DEPS = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing integrations
try:
    from claudia_integration_bridge import ClaudiaIntegrationBridge
    HAS_CLAUDIA = True
except ImportError:
    ClaudiaIntegrationBridge = None
    HAS_CLAUDIA = False

# Import new integrations
try:
    from MCPVOTS_INTEGRATION import MCPVotsIntegration, create_mcpvots_integration
    HAS_MCPVOTS = True
except ImportError:
    MCPVotsIntegration = None
    HAS_MCPVOTS = False
    logger.warning("MCPVots integration not available")

try:
    from MCP_CHROME_INTEGRATION import MCPChromeIntegration, create_mcp_chrome_integration
    HAS_MCP_CHROME = True
except ImportError:
    MCPChromeIntegration = None
    HAS_MCP_CHROME = False
    logger.warning("MCP Chrome integration not available")

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "deployment"))
    from PAKE_DEPLOYMENT import PakeDeployment, create_pake_deployment
    HAS_PAKE = True
except ImportError:
    PakeDeployment = None
    HAS_PAKE = False
    logger.warning("Pake deployment not available")

# Import REAL implementations
try:
    from COMPLETE_MCP_IMPLEMENTATION import create_real_mcp_executor
    from trading.REAL_TRADING_ENGINE import create_real_trading_engine
    from memory.ultimate_memory_system import UltimateMemorySystem
    HAS_REAL_IMPL = True
except ImportError:
    HAS_REAL_IMPL = False
    logger.warning("Real implementations not available")


class UltimateAGISystemV2:
    """Enhanced ULTIMATE AGI system with MCPVots features"""

    def __init__(self):
        """Initialize the enhanced AGI system"""
        self.version = "ULTIMATE-V2.0"
        self.start_time = time.time()
        self.db_path = "ultimate_agi_v2.db"
        self.port = int(os.environ.get('AGI_PORT', 8888))
        self.app = web.Application()
        self.setup_routes()

        # Core components
        self.agents = {}
        self.mcp_tools = {}
        self.ipfs_client = None
        self.deepseek_model = None
        self.trading_engine = None
        self.memory_system = None

        # New integrations
        self.mcpvots = None
        self.mcp_chrome = None
        self.pake_deployment = None
        self.claudia_bridge = None

        # Self-healing metrics
        self.health_status = {
            'errors_detected': 0,
            'errors_healed': 0,
            'uptime': 0,
            'healing_rate': 0.0
        }

        # Initialize database
        self.init_database()

        # Load configurations
        self.load_configs()

        # Start background tasks
        self.background_tasks = []

        logger.info(f"🚀 ULTIMATE AGI SYSTEM V2 initialized on port {self.port}")

    async def initialize_all_systems(self):
        """Initialize all system components asynchronously"""
        logger.info("Initializing all systems...")
        
        # Initialize in parallel for faster startup
        init_tasks = []
        
        # Core systems
        init_tasks.append(self._init_memory_system())
        init_tasks.append(self._init_ipfs())
        init_tasks.append(self._init_ollama())
        
        # New integrations
        if HAS_MCPVOTS:
            init_tasks.append(self._init_mcpvots())
        
        if HAS_MCP_CHROME:
            init_tasks.append(self._init_mcp_chrome())
        
        if HAS_REAL_IMPL:
            init_tasks.append(self._init_real_implementations())
        
        if HAS_CLAUDIA:
            init_tasks.append(self._init_claudia())
        
        # Execute all initializations
        results = await asyncio.gather(*init_tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Initialization error: {result}")
        
        # Initialize Pake deployment (not async)
        if HAS_PAKE:
            self.pake_deployment = create_pake_deployment()
        
        # Start background monitoring
        self.background_tasks.append(
            asyncio.create_task(self._monitor_health())
        )
        
        logger.info("✅ All systems initialized")

    async def _init_mcpvots(self):
        """Initialize MCPVots integration"""
        logger.info("Initializing MCPVots integration...")
        self.mcpvots = await create_mcpvots_integration()
        
        # Get integration status
        status = self.mcpvots.get_status()
        logger.info(f"MCPVots status: {status}")

    async def _init_mcp_chrome(self):
        """Initialize MCP Chrome browser automation"""
        logger.info("Initializing MCP Chrome...")
        self.mcp_chrome = await create_mcp_chrome_integration()
        
        if self.mcp_chrome:
            logger.info("✅ MCP Chrome connected")

    async def _init_memory_system(self):
        """Initialize memory system"""
        if HAS_REAL_IMPL:
            from memory.ultimate_memory_system import UltimateMemorySystem
            self.memory_system = UltimateMemorySystem(Path.cwd())
            logger.info("✅ Memory system initialized")

    async def _init_ipfs(self):
        """Initialize IPFS client"""
        try:
            self.ipfs_client = ipfshttpclient.connect()
            logger.info("✅ IPFS connected")
        except Exception:
            logger.warning("⚠️ IPFS not available")

    async def _init_ollama(self):
        """Initialize Ollama/DeepSeek connection"""
        try:
            import ollama
            models = ollama.list()
            self.deepseek_model = next(
                (m['name'] for m in models.get('models', []) if 'DeepSeek-R1' in m.get('name', '')),
                None
            )
            if self.deepseek_model:
                logger.info(f"✅ DeepSeek-R1 model available: {self.deepseek_model}")
        except Exception:
            logger.warning("⚠️ Ollama/DeepSeek not available")

    async def _init_real_implementations(self):
        """Initialize REAL implementations"""
        # Real MCP
        self.mcp_executor = await create_real_mcp_executor()
        
        # Real Trading
        trading_config = {
            'finnhub_api_key': os.getenv('FINNHUB_API_KEY'),
            'solana_rpc': 'https://api.mainnet-beta.solana.com'
        }
        self.trading_engine = await create_real_trading_engine(trading_config)

    async def _init_claudia(self):
        """Initialize Claudia integration"""
        self.claudia_bridge = ClaudiaIntegrationBridge()
        logger.info("✅ Claudia integration initialized")

    async def _monitor_health(self):
        """Background health monitoring with self-healing"""
        while True:
            try:
                # Update uptime
                self.health_status['uptime'] = time.time() - self.start_time
                
                # Check component health
                components = {
                    'memory': self.memory_system is not None,
                    'ipfs': self.ipfs_client is not None,
                    'deepseek': self.deepseek_model is not None,
                    'mcp_chrome': self.mcp_chrome and self.mcp_chrome.connected,
                    'mcpvots': self.mcpvots is not None
                }
                
                # Detect issues
                for component, healthy in components.items():
                    if not healthy:
                        self.health_status['errors_detected'] += 1
                        
                        # Attempt self-healing
                        if self.mcpvots:
                            error = {
                                'message': f'{component} service not available',
                                'service': component
                            }
                            healing_result = await self.mcpvots.heal_error(error)
                            
                            if healing_result.get('status') == 'healed':
                                self.health_status['errors_healed'] += 1
                
                # Calculate healing rate
                if self.health_status['errors_detected'] > 0:
                    self.health_status['healing_rate'] = (
                        self.health_status['errors_healed'] / 
                        self.health_status['errors_detected']
                    )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)

    def init_database(self):
        """Initialize enhanced database with MCPVots tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Original tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                component TEXT,
                status TEXT,
                data TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                message TEXT,
                response TEXT,
                model TEXT
            )
        ''')

        # New MCPVots tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_healing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_type TEXT,
                error_message TEXT,
                healing_action TEXT,
                success BOOLEAN,
                duration_ms INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browser_automation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                task_type TEXT,
                url TEXT,
                action TEXT,
                result TEXT,
                screenshot_path TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                algorithm TEXT,
                generation INTEGER,
                fitness REAL,
                improvement_rate REAL
            )
        ''')

        conn.commit()
        conn.close()

    def load_configs(self):
        """Load all configuration files"""
        config_files = [
            "config/unified_system_config.yaml",
            "config/unified_agi_portal.yaml",
            "config/mcp_settings.json",
            "config/mcpvots_config.yaml"  # New config
        ]

        self.config = {}
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    if config_file.endswith('.yaml'):
                        with open(config_file, 'r') as f:
                            self.config.update(yaml.safe_load(f))
                    elif config_file.endswith('.json'):
                        with open(config_file, 'r') as f:
                            self.config.update(json.load(f))
                except Exception as e:
                    logger.warning(f"Could not load {config_file}: {e}")

    def setup_routes(self):
        """Setup all web routes including new endpoints"""
        # Original routes
        self.app.router.add_get('/', self.serve_dashboard_v2)
        self.app.router.add_get('/api/status', self.get_system_status)
        self.app.router.add_post('/api/chat', self.handle_chat)
        self.app.router.add_post('/api/agent', self.handle_agent_request)
        self.app.router.add_get('/api/trading', self.get_trading_status)
        self.app.router.add_post('/api/mcp', self.handle_mcp_request)
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # New MCPVots routes
        self.app.router.add_post('/api/browser', self.handle_browser_automation)
        self.app.router.add_post('/api/research', self.handle_web_research)
        self.app.router.add_get('/api/health', self.get_health_status)
        self.app.router.add_post('/api/evolve', self.handle_evolution_request)
        self.app.router.add_post('/api/knowledge', self.handle_knowledge_query)
        
        # Desktop deployment route
        self.app.router.add_post('/api/deploy', self.handle_desktop_deployment)

    async def serve_dashboard_v2(self, request):
        """Serve the enhanced dashboard"""
        # Import and use the V2 dashboard
        try:
            from ULTIMATE_DASHBOARD_V2 import generate_ultimate_dashboard_v2
            html = generate_ultimate_dashboard_v2()
        except Exception:
            html = self.generate_fallback_dashboard()
        
        return web.Response(text=html, content_type='text/html')

    async def handle_browser_automation(self, request):
        """Handle browser automation requests"""
        if not self.mcp_chrome:
            return web.json_response({'error': 'MCP Chrome not available'})
        
        data = await request.json()
        tool = data.get('tool')
        params = data.get('params', {})
        
        result = await self.mcp_chrome.execute_tool(tool, params)
        
        # Log to database
        self._log_browser_action(tool, params, result)
        
        return web.json_response(result)

    async def handle_web_research(self, request):
        """Handle web research requests"""
        if not self.mcp_chrome:
            return web.json_response({'error': 'MCP Chrome not available'})
        
        data = await request.json()
        topic = data.get('topic')
        depth = data.get('depth', 3)
        
        result = await self.mcp_chrome.research_topic(topic, depth)
        
        # Store in knowledge graph if available
        if self.mcpvots and self.mcpvots.knowledge_graph:
            await self.mcpvots.knowledge_graph.add_knowledge(
                subject=topic,
                predicate='research_results',
                object=result
            )
        
        return web.json_response(result)

    async def handle_evolution_request(self, request):
        """Handle algorithm evolution requests"""
        if not self.mcpvots:
            return web.json_response({'error': 'MCPVots not available'})
        
        data = await request.json()
        result = await self.mcpvots.evolve_algorithm(data)
        
        # Log evolution
        self._log_evolution(data, result)
        
        return web.json_response(result)

    async def handle_knowledge_query(self, request):
        """Handle knowledge graph queries"""
        if not self.mcpvots:
            return web.json_response({'error': 'MCPVots not available'})
        
        data = await request.json()
        result = await self.mcpvots.query_knowledge(data)
        
        return web.json_response(result)

    async def handle_desktop_deployment(self, request):
        """Handle desktop app deployment requests"""
        if not self.pake_deployment:
            return web.json_response({'error': 'Pake deployment not available'})
        
        data = await request.json()
        app_name = data.get('app_name')
        config = data.get('config', {})
        
        result = self.pake_deployment.build_desktop_app(app_name, config)
        
        return web.json_response(result)

    async def get_health_status(self, request):
        """Get system health status with self-healing metrics"""
        status = {
            'version': self.version,
            'uptime': self.health_status['uptime'],
            'healing_rate': f"{self.health_status['healing_rate'] * 100:.1f}%",
            'errors_detected': self.health_status['errors_detected'],
            'errors_healed': self.health_status['errors_healed'],
            'components': {
                'memory': self.memory_system is not None,
                'ipfs': self.ipfs_client is not None,
                'deepseek': self.deepseek_model is not None,
                'mcp_chrome': self.mcp_chrome and self.mcp_chrome.connected,
                'mcpvots': self.mcpvots is not None,
                'claudia': self.claudia_bridge is not None,
                'pake': self.pake_deployment is not None
            },
            'mcpvots_status': self.mcpvots.get_status() if self.mcpvots else None
        }
        
        return web.json_response(status)

    async def get_system_status(self, request):
        """Enhanced system status endpoint"""
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)
        
        status = {
            'status': 'online',
            'version': self.version,
            'uptime': int(time.time() - self.start_time),
            'memory_usage': f"{memory_usage:.1f}%",
            'cpu_usage': f"{cpu_usage:.1f}%",
            'active_agents': len(self.agents),
            'mcp_tools': len(self.mcp_tools),
            'deepseek_status': 'online' if self.deepseek_model else 'offline',
            'mcp_status': 'online' if self.mcp_tools else 'offline',
            'trading_status': 'online' if self.trading_engine else 'offline',
            'memory_status': 'online' if self.memory_system else 'offline',
            'browser_status': 'online' if self.mcp_chrome and self.mcp_chrome.connected else 'offline',
            'healing_rate': f"{self.health_status['healing_rate'] * 100:.1f}%"
        }
        
        return web.json_response(status)

    async def handle_chat(self, request):
        """Enhanced chat handler with browser capabilities"""
        data = await request.json()
        message = data.get('message', '')
        
        # Check if message requires browser action
        if any(keyword in message.lower() for keyword in ['browse', 'search web', 'website', 'research']):
            if self.mcp_chrome:
                # Extract search query
                query = message.replace('search web for', '').replace('browse', '').strip()
                research_result = await self.mcp_chrome.research_topic(query, depth=2)
                
                response = f"I've researched '{query}' for you. Found {len(research_result['sources'])} sources. "
                response += research_result['summary']
            else:
                response = "Browser automation is not available at the moment."
        else:
            # Regular chat handling
            response = await self._process_chat_message(message)
        
        # Store in database
        self._store_chat_history(message, response)
        
        return web.json_response({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    async def _process_chat_message(self, message: str) -> str:
        """Process chat message with available models"""
        if self.deepseek_model:
            try:
                import ollama
                result = ollama.generate(
                    model=self.deepseek_model,
                    prompt=message
                )
                return result['response']
            except Exception:
                pass
        
        # Fallback response
        return f"Processing: {message}"

    async def handle_mcp_request(self, request):
        """Enhanced MCP request handler"""
        data = await request.json()
        tool = data.get('tool')
        method = data.get('method')
        params = data.get('params', {})
        
        # Use REAL MCP implementation if available
        if hasattr(self, 'mcp_executor') and self.mcp_executor:
            try:
                result = await self.mcp_executor.execute_tool(tool, method, params)
                return web.json_response(result)
            except Exception as e:
                # Self-heal if MCPVots available
                if self.mcpvots:
                    healing_result = await self.mcpvots.heal_error({
                        'message': str(e),
                        'service': 'mcp_executor'
                    })
                    if healing_result.get('status') == 'healed':
                        # Retry
                        result = await self.mcp_executor.execute_tool(tool, method, params)
                        return web.json_response(result)
        
        return web.json_response({'error': 'MCP not available'})

    async def websocket_handler(self, request):
        """Enhanced WebSocket handler"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    # Process WebSocket message
                    response = await self._process_ws_message(data)
                    
                    await ws.send_json(response)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            logger.error(f'WebSocket handler error: {e}')
        finally:
            return ws

    async def _process_ws_message(self, data: Dict) -> dict:
        """Process WebSocket messages"""
        msg_type = data.get('type')
        
        if msg_type == 'chat':
            response = await self._process_chat_message(data.get('message', ''))
            return {
                'type': 'chat_response',
                'message': response,
                'timestamp': datetime.now().isoformat()
            }
        elif msg_type == 'status':
            status = await self.get_system_status(None)
            return {
                'type': 'status_update',
                **json.loads(status.text)
            }
        else:
            return {'type': 'error', 'message': 'Unknown message type'}

    def _store_chat_history(self, message: str, response: str):
        """Store chat history in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_id, message, response, model)
            VALUES (?, ?, ?, ?)
        ''', ('user', message, response, self.deepseek_model or 'fallback'))
        conn.commit()
        conn.close()

    def _log_browser_action(self, action: str, params: Dict, result: Dict):
        """Log browser automation actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO browser_automation_log (task_type, url, action, result)
            VALUES (?, ?, ?, ?)
        ''', (action, params.get('url', ''), json.dumps(params), json.dumps(result)))
        conn.commit()
        conn.close()

    def _log_evolution(self, task: Dict, result: Dict):
        """Log evolution results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO evolution_log (algorithm, generation, fitness, improvement_rate)
            VALUES (?, ?, ?, ?)
        ''', (
            task.get('algorithm', ''),
            result.get('generation', 0),
            result.get('fitness', 0.0),
            result.get('improvement_rate', 0.0)
        ))
        conn.commit()
        conn.close()

    def generate_fallback_dashboard(self) -> str:
        """Generate fallback dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ULTIMATE AGI SYSTEM V2</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #00ff41; }
                .status { padding: 10px; background: #f0f0f0; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>ULTIMATE AGI SYSTEM V2</h1>
            <div class="status">
                <h2>System Status</h2>
                <p>Loading...</p>
            </div>
            <script>
                fetch('/api/health')
                    .then(r => r.json())
                    .then(data => {
                        document.querySelector('.status p').innerHTML = JSON.stringify(data, null, 2);
                    });
            </script>
        </body>
        </html>
        """

    async def run(self):
        """Run the enhanced AGI system"""
        # Initialize all systems
        await self.initialize_all_systems()
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"✅ ULTIMATE AGI SYSTEM V2 running on http://localhost:{self.port}")
        logger.info(f"✅ Self-healing enabled with {self.health_status['healing_rate']*100:.1f}% success rate")
        logger.info(f"✅ Browser automation: {'enabled' if self.mcp_chrome else 'disabled'}")
        logger.info(f"✅ Desktop deployment: {'enabled' if self.pake_deployment else 'disabled'}")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(3600)  # Sleep for an hour
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            # Cleanup
            for task in self.background_tasks:
                task.cancel()
            
            if self.mcp_chrome:
                await self.mcp_chrome.disconnect()


async def main():
    """Main entry point"""
    system = UltimateAGISystemV2()
    await system.run()


if __name__ == "__main__":
    # Set up better error handling for Windows
    if sys.platform == 'win32':
        # Set console to UTF-8
        subprocess.run('chcp 65001', shell=True, capture_output=True)
        
        # Fix stdout encoding
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()