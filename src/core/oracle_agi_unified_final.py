#!/usr/bin/env python3
"""
Oracle AGI Unified Final Dashboard
==================================
Complete integration of all MCP tools with automatic service discovery
and management. This is the FINAL unified version.
"""

import asyncio
import json
import os
import sys
import time
import psutil
import platform
import logging
import subprocess
import socket
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
from aiohttp import web
import aiohttp_cors
import websockets
import sqlite3
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleAGI")

@dataclass
class MCPToolStatus:
    """MCP tool status information"""
    name: str
    port: int
    status: str  # 'online', 'offline', 'starting'
    endpoint: str
    capabilities: List[str]
    last_check: datetime
    response_time: float
    error: Optional[str] = None

class MCPToolsManager:
    """Manage all MCP tools and their connections"""
    
    def __init__(self):
        self.mcp_tools = {
            # Core MCP Servers
            "memory_mcp": {
                "name": "Memory MCP",
                "port": 3002,
                "endpoint": "ws://localhost:3002",
                "start_cmd": ["python", "servers/enhanced_memory_mcp_server.py"],
                "capabilities": ["knowledge-graph", "storage", "retrieval"],
                "required": True
            },
            "github_mcp": {
                "name": "GitHub MCP",
                "port": 3001,
                "endpoint": "ws://localhost:3001",
                "start_cmd": ["python", "servers/mcp_github_server.py"],
                "capabilities": ["repositories", "issues", "pull-requests"],
                "required": False
            },
            "solana_mcp": {
                "name": "Solana MCP",
                "port": 3005,
                "endpoint": "ws://localhost:3005",
                "start_cmd": ["python", "solana_mcp_deepseek_integration.py"],
                "capabilities": ["blockchain", "trading", "defi"],
                "required": False
            },
            "browser_mcp": {
                "name": "Browser Tools",
                "port": 3006,
                "endpoint": "ws://localhost:3006",
                "start_cmd": ["python", "servers/browser_tools_mcp.py"],
                "capabilities": ["automation", "scraping", "testing"],
                "required": False
            },
            "opencti_mcp": {
                "name": "OpenCTI Security",
                "port": 3007,
                "endpoint": "ws://localhost:3007",
                "start_cmd": ["python", "servers/opencti_mcp_server.py"],
                "capabilities": ["threat-intelligence", "ioc-checking", "security"],
                "required": False
            }
        }
        
        self.tool_status: Dict[str, MCPToolStatus] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        
    async def check_port_available(self, port: int) -> bool:
        """Check if port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0
    
    async def find_available_port(self, start_port: int) -> int:
        """Find next available port"""
        port = start_port
        while port < start_port + 100:
            if await self.check_port_available(port):
                return port
            port += 1
        raise Exception(f"No available ports found starting from {start_port}")
    
    async def start_mcp_tool(self, tool_id: str) -> bool:
        """Start an MCP tool"""
        config = self.mcp_tools.get(tool_id)
        if not config:
            return False
            
        try:
            # Check if already running
            if not await self.check_port_available(config["port"]):
                logger.info(f"{config['name']} already running on port {config['port']}")
                return True
                
            logger.info(f"Starting {config['name']}...")
            
            # Start the process
            env = os.environ.copy()
            if tool_id == "github_mcp":
                env["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "")
            elif tool_id == "opencti_mcp":
                env["OPENCTI_URL"] = os.environ.get("OPENCTI_URL", "http://localhost:8080")
                env["OPENCTI_TOKEN"] = os.environ.get("OPENCTI_TOKEN", "")
                
            process = subprocess.Popen(
                config["start_cmd"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            
            self.processes[tool_id] = process
            
            # Wait for startup
            await asyncio.sleep(3)
            
            # Verify it started
            if not await self.check_port_available(config["port"]):
                logger.info(f"✓ {config['name']} started successfully")
                return True
            else:
                logger.error(f"✗ {config['name']} failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {config['name']}: {e}")
            return False
    
    async def connect_to_mcp_tool(self, tool_id: str) -> Optional[websockets.WebSocketClientProtocol]:
        """Connect to an MCP tool"""
        config = self.mcp_tools.get(tool_id)
        if not config:
            return None
            
        try:
            ws = await websockets.connect(config["endpoint"])
            self.connections[tool_id] = ws
            logger.info(f"Connected to {config['name']}")
            return ws
        except Exception as e:
            logger.error(f"Failed to connect to {config['name']}: {e}")
            return None
    
    async def check_all_tools(self):
        """Check status of all MCP tools"""
        for tool_id, config in self.mcp_tools.items():
            start_time = time.time()
            
            try:
                # Check if port is in use
                port_available = await self.check_port_available(config["port"])
                
                if port_available:
                    status = "offline"
                    error = "Port not in use"
                else:
                    # Try to connect
                    try:
                        async with websockets.connect(config["endpoint"], timeout=2) as ws:
                            await ws.ping()
                            status = "online"
                            error = None
                    except:
                        status = "offline"
                        error = "Connection failed"
                        
            except Exception as e:
                status = "offline"
                error = str(e)
                
            response_time = (time.time() - start_time) * 1000
            
            self.tool_status[tool_id] = MCPToolStatus(
                name=config["name"],
                port=config["port"],
                status=status,
                endpoint=config["endpoint"],
                capabilities=config["capabilities"],
                last_check=datetime.now(),
                response_time=response_time,
                error=error
            )
    
    async def start_required_tools(self):
        """Start all required MCP tools"""
        for tool_id, config in self.mcp_tools.items():
            if config.get("required", False):
                if self.tool_status.get(tool_id, MCPToolStatus("", 0, "offline", "", [], datetime.now(), 0)).status == "offline":
                    await self.start_mcp_tool(tool_id)
    
    async def execute_mcp_command(self, tool_id: str, method: str, params: Any = None) -> Any:
        """Execute command on MCP tool"""
        ws = self.connections.get(tool_id)
        
        if not ws or ws.closed:
            ws = await self.connect_to_mcp_tool(tool_id)
            if not ws:
                return {"error": f"Cannot connect to {tool_id}"}
        
        try:
            # Send JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {},
                "id": str(time.time())
            }
            
            await ws.send(json.dumps(request))
            response = await ws.recv()
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"MCP command error: {e}")
            return {"error": str(e)}


class OracleAGIUnifiedFinal:
    """The final unified Oracle AGI dashboard with all integrations"""
    
    def __init__(self, port: int = None):
        self.app = web.Application()
        self.setup_cors()
        
        # Find available port if not specified
        self.port = port
        if not self.port:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            for p in [3011, 3010, 3012, 8080, 8081]:
                if sock.connect_ex(('localhost', p)) != 0:
                    self.port = p
                    break
            sock.close()
        
        if not self.port:
            self.port = 8080  # Fallback
            
        # Paths
        self.workspace = Path(__file__).parent
        
        # MCP Tools Manager
        self.mcp_manager = MCPToolsManager()
        
        # Initialize components
        self.init_database()
        
        # WebSocket clients
        self.ws_clients = set()
        
        # Trading system
        self.trading_active = False
        self.trading_data = {
            "portfolio": {"total_value": 0, "positions": []},
            "market_data": {},
            "performance": {"sharpe_ratio": 0, "win_rate": 0}
        }
        
        # Setup routes
        self.setup_routes()
        
        # Import integrations
        self._load_integrations()
        
    def setup_cors(self):
        """Setup CORS"""
        self.cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
    
    def init_database(self):
        """Initialize database"""
        self.db_path = self.workspace / "oracle_agi_unified.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type TEXT,
                source TEXT,
                data TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mcp_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tool TEXT,
                method TEXT,
                params TEXT,
                result TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_integrations(self):
        """Load optional integrations"""
        # Solana Trading
        try:
            from solana_precious_metals_trading import SolanaTradingIntegration
            self.solana_trader = SolanaTradingIntegration()
            logger.info("Solana trading integration loaded")
        except:
            self.solana_trader = None
            
        # OpenCTI
        try:
            from opencti_integration import OpenCTIDashboardIntegration
            self.opencti = OpenCTIDashboardIntegration()
            logger.info("OpenCTI security integration loaded")
        except:
            self.opencti = None
            
        # Wallet Integration
        try:
            from wallet_integration import WalletIntegrationAPI, get_wallet_integration_html
            self.wallet_api = WalletIntegrationAPI()
            self.wallet_html = get_wallet_integration_html()
            logger.info("Wallet integration loaded")
        except:
            self.wallet_api = None
            self.wallet_html = ""
    
    def setup_routes(self):
        """Setup all routes"""
        routes = [
            # Core API
            ('GET', '/api/status', self.get_status),
            ('GET', '/api/mcp/tools', self.get_mcp_tools),
            ('POST', '/api/mcp/start/{tool_id}', self.start_mcp_tool),
            ('POST', '/api/mcp/execute', self.execute_mcp_command),
            
            # Memory operations
            ('POST', '/api/memory/store', self.store_memory),
            ('GET', '/api/memory/retrieve', self.retrieve_memory),
            ('GET', '/api/memory/graph', self.get_knowledge_graph),
            
            # GitHub operations
            ('GET', '/api/github/repos', self.get_github_repos),
            ('POST', '/api/github/sync', self.sync_github_repo),
            
            # Trading
            ('GET', '/api/trading/status', self.get_trading_status),
            ('POST', '/api/trading/start', self.start_trading),
            ('POST', '/api/trading/manual', self.manual_trade),
            
            # Security
            ('GET', '/api/security/status', self.get_security_status),
            ('POST', '/api/security/check', self.check_security),
            
            # WebSocket
            ('GET', '/ws', self.websocket_handler),
            
            # Dashboard
            ('GET', '/', self.serve_dashboard),
        ]
        
        for method, path, handler in routes:
            resource = self.cors.add(self.app.router.add_resource(path))
            self.cors.add(resource.add_route(method, handler))
    
    async def get_status(self, request):
        """Get system status"""
        # Check all MCP tools
        await self.mcp_manager.check_all_tools()
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        status = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "port": self.port,
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3)
            },
            "mcp_tools": {
                tool_id: asdict(status) 
                for tool_id, status in self.mcp_manager.tool_status.items()
            },
            "integrations": {
                "trading": self.solana_trader is not None,
                "security": self.opencti is not None,
                "wallet": self.wallet_api is not None
            }
        }
        
        return web.json_response(status)
    
    async def get_mcp_tools(self, request):
        """Get MCP tools status"""
        await self.mcp_manager.check_all_tools()
        return web.json_response({
            tool_id: asdict(status)
            for tool_id, status in self.mcp_manager.tool_status.items()
        })
    
    async def start_mcp_tool(self, request):
        """Start an MCP tool"""
        tool_id = request.match_info['tool_id']
        success = await self.mcp_manager.start_mcp_tool(tool_id)
        return web.json_response({"success": success})
    
    async def execute_mcp_command(self, request):
        """Execute MCP command"""
        data = await request.json()
        tool_id = data.get("tool")
        method = data.get("method")
        params = data.get("params", {})
        
        result = await self.mcp_manager.execute_mcp_command(tool_id, method, params)
        
        # Log command
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mcp_commands (tool, method, params, result)
            VALUES (?, ?, ?, ?)
        ''', (tool_id, method, json.dumps(params), json.dumps(result)))
        conn.commit()
        conn.close()
        
        return web.json_response(result)
    
    # Memory MCP operations
    async def store_memory(self, request):
        """Store data in memory MCP"""
        data = await request.json()
        result = await self.mcp_manager.execute_mcp_command(
            "memory_mcp",
            "memory/store",
            data
        )
        return web.json_response(result)
    
    async def retrieve_memory(self, request):
        """Retrieve data from memory MCP"""
        query = request.rel_url.query.get('query', '')
        result = await self.mcp_manager.execute_mcp_command(
            "memory_mcp",
            "memory/retrieve",
            {"query": query}
        )
        return web.json_response(result)
    
    async def get_knowledge_graph(self, request):
        """Get knowledge graph visualization"""
        result = await self.mcp_manager.execute_mcp_command(
            "memory_mcp",
            "memory/get_graph",
            {}
        )
        return web.json_response(result)
    
    # GitHub MCP operations
    async def get_github_repos(self, request):
        """Get GitHub repositories"""
        result = await self.mcp_manager.execute_mcp_command(
            "github_mcp",
            "github/list_repos",
            {"user": "kabrony"}
        )
        return web.json_response(result)
    
    async def sync_github_repo(self, request):
        """Sync GitHub repository"""
        data = await request.json()
        result = await self.mcp_manager.execute_mcp_command(
            "github_mcp",
            "github/sync_repo",
            data
        )
        return web.json_response(result)
    
    # Trading operations
    async def get_trading_status(self, request):
        """Get trading status"""
        if self.solana_trader:
            return web.json_response(self.solana_trader.get_trading_status())
        return web.json_response({"active": False, "data": self.trading_data})
    
    async def start_trading(self, request):
        """Start trading"""
        if self.solana_trader:
            await self.solana_trader.start_trading()
            return web.json_response({"success": True})
        return web.json_response({"error": "Trading not available"}, status=503)
    
    async def manual_trade(self, request):
        """Execute manual trade"""
        if self.solana_trader:
            data = await request.json()
            result = await self.solana_trader.manual_trade(
                data.get("asset"),
                data.get("action"),
                data.get("amount")
            )
            return web.json_response(result)
        return web.json_response({"error": "Trading not available"}, status=503)
    
    # Security operations
    async def get_security_status(self, request):
        """Get security status"""
        if self.opencti:
            data = await self.opencti.get_dashboard_data()
            return web.json_response(data)
        
        # Use OpenCTI MCP if available
        result = await self.mcp_manager.execute_mcp_command(
            "opencti_mcp",
            "security/status",
            {}
        )
        return web.json_response(result)
    
    async def check_security(self, request):
        """Check security threat"""
        data = await request.json()
        result = await self.mcp_manager.execute_mcp_command(
            "opencti_mcp",
            "security/check_ioc",
            data
        )
        return web.json_response(result)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.ws_clients.add(ws)
        
        try:
            # Send initial status
            await self.send_status_update(ws)
            
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    if data.get("type") == "ping":
                        await ws.send_json({"type": "pong"})
                    elif data.get("type") == "execute_mcp":
                        result = await self.mcp_manager.execute_mcp_command(
                            data.get("tool"),
                            data.get("method"),
                            data.get("params")
                        )
                        await ws.send_json({"type": "mcp_result", "data": result})
                        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.ws_clients.discard(ws)
            
        return ws
    
    async def send_status_update(self, ws=None):
        """Send status update to WebSocket clients"""
        status = await self.get_status(None)
        status_data = json.loads(status.text)
        
        message = {
            "type": "status_update",
            "data": status_data
        }
        
        if ws:
            await ws.send_json(message)
        else:
            # Broadcast to all clients
            for client in self.ws_clients:
                try:
                    await client.send_json(message)
                except:
                    pass
    
    async def serve_dashboard(self, request):
        """Serve the unified dashboard"""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle AGI Unified Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .status-bar {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .status-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
        }}
        
        .status-indicator {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff88;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #2a2a3e;
        }}
        
        .tab {{
            padding: 12px 24px;
            background: none;
            border: none;
            color: #888;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            border-bottom: 2px solid transparent;
        }}
        
        .tab.active {{
            color: #00d4ff;
            border-bottom-color: #00d4ff;
        }}
        
        .tab-content {{
            display: none;
            animation: fadeIn 0.3s ease;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .mcp-tools-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .mcp-tool-card {{
            background: #1a1a2e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2a3f5f;
            transition: all 0.3s ease;
        }}
        
        .mcp-tool-card:hover {{
            transform: translateY(-2px);
            border-color: #0099ff;
        }}
        
        .tool-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .tool-status {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .capabilities {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }}
        
        .capability {{
            padding: 4px 8px;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 4px;
            font-size: 0.85em;
        }}
        
        .btn {{
            background: linear-gradient(135deg, #0099ff, #00d4ff);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,150,255,0.4);
        }}
        
        .btn-small {{
            padding: 6px 12px;
            font-size: 0.9em;
        }}
        
        .terminal {{
            background: #0f0f1f;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
            margin-top: 20px;
        }}
        
        .terminal-line {{
            padding: 2px 0;
            white-space: pre-wrap;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: #1a1a2e;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #00d4ff;
            margin: 10px 0;
        }}
        
        .command-input {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .command-input input {{
            flex: 1;
            padding: 10px;
            background: #1a1a2e;
            border: 1px solid #2a3f5f;
            color: #e0e0e0;
            border-radius: 8px;
        }}
        
        .status-online {{ background: #00ff88; }}
        .status-offline {{ background: #ff3838; }}
        .status-starting {{ background: #ffaa00; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Oracle AGI Unified Dashboard</h1>
            <p>Complete MCP Tools Integration & Control Center</p>
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-indicator" id="mainStatus"></div>
                    <span>System Online</span>
                </div>
                <div class="status-item">
                    <span id="cpuUsage">CPU: --</span>
                </div>
                <div class="status-item">
                    <span id="memoryUsage">Memory: --</span>
                </div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('mcp-tools')">MCP Tools</button>
            <button class="tab" onclick="switchTab('memory')">Memory & Knowledge</button>
            <button class="tab" onclick="switchTab('github')">GitHub</button>
            <button class="tab" onclick="switchTab('trading')">Trading</button>
            <button class="tab" onclick="switchTab('security')">Security</button>
            <button class="tab" onclick="switchTab('terminal')">Terminal</button>
        </div>
        
        <!-- MCP Tools Tab -->
        <div id="mcp-tools" class="tab-content active">
            <h2>MCP Tools Status</h2>
            <div class="mcp-tools-grid" id="mcpToolsGrid">
                <!-- MCP tools will be populated here -->
            </div>
        </div>
        
        <!-- Memory Tab -->
        <div id="memory" class="tab-content">
            <h2>Memory & Knowledge Graph</h2>
            <div class="command-input">
                <input type="text" id="memoryInput" placeholder="Enter data to store or query to retrieve">
                <button class="btn" onclick="storeMemory()">Store</button>
                <button class="btn" onclick="retrieveMemory()">Retrieve</button>
            </div>
            <div class="terminal" id="memoryTerminal"></div>
        </div>
        
        <!-- GitHub Tab -->
        <div id="github" class="tab-content">
            <h2>GitHub Integration</h2>
            <button class="btn" onclick="loadGitHubRepos()">Load Repositories</button>
            <div id="githubContent" style="margin-top: 20px;"></div>
        </div>
        
        <!-- Trading Tab -->
        <div id="trading" class="tab-content">
            <h2>Solana Trading</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Portfolio Value</h3>
                    <div class="metric-value" id="portfolioValue">$0.00</div>
                </div>
                <div class="metric-card">
                    <h3>Daily P&L</h3>
                    <div class="metric-value" id="dailyPnl">$0.00</div>
                </div>
                <div class="metric-card">
                    <h3>Win Rate</h3>
                    <div class="metric-value" id="winRate">0%</div>
                </div>
            </div>
            <button class="btn" onclick="toggleTrading()">Start Trading</button>
        </div>
        
        <!-- Security Tab -->
        <div id="security" class="tab-content">
            <h2>Security Monitoring</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Security Score</h3>
                    <div class="metric-value" id="securityScore">100%</div>
                </div>
                <div class="metric-card">
                    <h3>Active Threats</h3>
                    <div class="metric-value" id="activeThreats">0</div>
                </div>
            </div>
            <div class="command-input">
                <input type="text" id="iocInput" placeholder="Enter IOC to check">
                <button class="btn" onclick="checkIOC()">Check IOC</button>
            </div>
        </div>
        
        <!-- Terminal Tab -->
        <div id="terminal" class="tab-content">
            <h2>MCP Command Terminal</h2>
            <div class="command-input">
                <select id="mcpToolSelect" style="padding: 10px; background: #1a1a2e; border: 1px solid #2a3f5f; color: #e0e0e0; border-radius: 8px;">
                    <option value="memory_mcp">Memory MCP</option>
                    <option value="github_mcp">GitHub MCP</option>
                    <option value="solana_mcp">Solana MCP</option>
                    <option value="browser_mcp">Browser MCP</option>
                    <option value="opencti_mcp">OpenCTI MCP</option>
                </select>
                <input type="text" id="commandInput" placeholder="Enter MCP command (e.g., memory/store)">
                <button class="btn" onclick="executeMCPCommand()">Execute</button>
            </div>
            <div class="terminal" id="commandTerminal"></div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let currentTab = 'mcp-tools';
        
        // Initialize WebSocket
        function initWebSocket() {{
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${{protocol}}//${{window.location.host}}/ws`);
            
            ws.onopen = () => {{
                console.log('Connected to Oracle AGI');
                addTerminalLine('Connected to Oracle AGI WebSocket');
            }};
            
            ws.onmessage = (event) => {{
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            }};
            
            ws.onclose = () => {{
                console.log('Disconnected from Oracle AGI');
                addTerminalLine('Disconnected - Reconnecting...');
                setTimeout(initWebSocket, 5000);
            }};
            
            ws.onerror = (error) => {{
                console.error('WebSocket error:', error);
            }};
        }}
        
        function handleWebSocketMessage(data) {{
            if (data.type === 'status_update') {{
                updateStatus(data.data);
            }} else if (data.type === 'mcp_result') {{
                displayMCPResult(data.data);
            }}
        }}
        
        function updateStatus(status) {{
            // Update system metrics
            document.getElementById('cpuUsage').textContent = `CPU: ${{status.metrics.cpu_percent.toFixed(1)}}%`;
            document.getElementById('memoryUsage').textContent = `Memory: ${{status.metrics.memory_percent.toFixed(1)}}%`;
            
            // Update MCP tools
            updateMCPTools(status.mcp_tools);
        }}
        
        function updateMCPTools(tools) {{
            const grid = document.getElementById('mcpToolsGrid');
            grid.innerHTML = '';
            
            for (const [toolId, tool] of Object.entries(tools)) {{
                const card = document.createElement('div');
                card.className = 'mcp-tool-card';
                
                const statusClass = `status-${{tool.status}}`;
                
                card.innerHTML = `
                    <div class="tool-header">
                        <h3>${{tool.name}}</h3>
                        <div class="tool-status">
                            <div class="status-indicator ${{statusClass}}"></div>
                            <span>${{tool.status}}</span>
                        </div>
                    </div>
                    <p>Port: ${{tool.port}}</p>
                    <p>Response: ${{tool.response_time.toFixed(0)}}ms</p>
                    <div class="capabilities">
                        ${{tool.capabilities.map(cap => `<span class="capability">${{cap}}</span>`).join('')}}
                    </div>
                    ${{tool.status === 'offline' ? `<button class="btn btn-small" onclick="startMCPTool('${{toolId}}')">Start</button>` : ''}}
                `;
                
                grid.appendChild(card);
            }}
        }}
        
        function switchTab(tabName) {{
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.getElementById(tabName).classList.add('active');
            
            currentTab = tabName;
        }}
        
        async function startMCPTool(toolId) {{
            const response = await fetch(`/api/mcp/start/${{toolId}}`, {{ method: 'POST' }});
            const result = await response.json();
            
            if (result.success) {{
                addTerminalLine(`Started ${{toolId}}`);
                refreshStatus();
            }} else {{
                addTerminalLine(`Failed to start ${{toolId}}`, 'error');
            }}
        }}
        
        async function executeMCPCommand() {{
            const tool = document.getElementById('mcpToolSelect').value;
            const command = document.getElementById('commandInput').value;
            
            if (!command) return;
            
            const [method, ...paramsParts] = command.split(' ');
            let params = {{}};
            
            // Simple param parsing
            if (paramsParts.length > 0) {{
                try {{
                    params = JSON.parse(paramsParts.join(' '));
                }} catch {{
                    params = {{ value: paramsParts.join(' ') }};
                }}
            }}
            
            addTerminalLine(`> ${{tool}}: ${{command}}`);
            
            const response = await fetch('/api/mcp/execute', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ tool, method, params }})
            }});
            
            const result = await response.json();
            displayMCPResult(result);
            
            document.getElementById('commandInput').value = '';
        }}
        
        function displayMCPResult(result) {{
            if (result.error) {{
                addTerminalLine(`Error: ${{result.error}}`, 'error');
            }} else {{
                addTerminalLine(JSON.stringify(result, null, 2), 'success');
            }}
        }}
        
        async function storeMemory() {{
            const input = document.getElementById('memoryInput').value;
            if (!input) return;
            
            const response = await fetch('/api/memory/store', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ content: input }})
            }});
            
            const result = await response.json();
            addMemoryLine(`Stored: ${{input}}`);
            document.getElementById('memoryInput').value = '';
        }}
        
        async function retrieveMemory() {{
            const query = document.getElementById('memoryInput').value;
            if (!query) return;
            
            const response = await fetch(`/api/memory/retrieve?query=${{encodeURIComponent(query)}}`);
            const result = await response.json();
            
            addMemoryLine(`Query: ${{query}}`);
            addMemoryLine(`Results: ${{JSON.stringify(result, null, 2)}}`);
        }}
        
        async function loadGitHubRepos() {{
            const response = await fetch('/api/github/repos');
            const result = await response.json();
            
            const content = document.getElementById('githubContent');
            if (result.result && Array.isArray(result.result)) {{
                content.innerHTML = `
                    <h3>Repositories</h3>
                    <ul>
                        ${{result.result.map(repo => `<li>${{repo.name}} - ${{repo.description || 'No description'}}</li>`).join('')}}
                    </ul>
                `;
            }} else {{
                content.innerHTML = '<p>No repositories found or error loading</p>';
            }}
        }}
        
        async function toggleTrading() {{
            const response = await fetch('/api/trading/start', {{ method: 'POST' }});
            const result = await response.json();
            
            if (result.success) {{
                addTerminalLine('Trading started');
            }} else {{
                addTerminalLine('Trading failed to start', 'error');
            }}
        }}
        
        async function checkIOC() {{
            const ioc = document.getElementById('iocInput').value;
            if (!ioc) return;
            
            const response = await fetch('/api/security/check', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ value: ioc }})
            }});
            
            const result = await response.json();
            addTerminalLine(`IOC Check: ${{ioc}} - ${{JSON.stringify(result)}}`);
        }}
        
        function addTerminalLine(text, type = 'info') {{
            const terminal = document.getElementById('commandTerminal');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.style.color = type === 'error' ? '#ff3838' : type === 'success' ? '#00ff88' : '#e0e0e0';
            line.textContent = `[${{new Date().toLocaleTimeString()}}] ${{text}}`;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }}
        
        function addMemoryLine(text) {{
            const terminal = document.getElementById('memoryTerminal');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.textContent = `[${{new Date().toLocaleTimeString()}}] ${{text}}`;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }}
        
        async function refreshStatus() {{
            const response = await fetch('/api/status');
            const status = await response.json();
            updateStatus(status);
        }}
        
        // Initialize on load
        window.onload = () => {{
            initWebSocket();
            refreshStatus();
            
            // Refresh status every 10 seconds
            setInterval(refreshStatus, 10000);
        }};
    </script>
    
    {self.wallet_html}
</body>
</html>'''
        
        return web.Response(text=html, content_type='text/html')
    
    async def background_tasks(self, app):
        """Start background tasks"""
        # Start required MCP tools
        await self.mcp_manager.start_required_tools()
        
        # Start periodic status updates
        async def status_updater():
            while True:
                await asyncio.sleep(5)
                await self.send_status_update()
                
        asyncio.create_task(status_updater())
    
    async def cleanup_tasks(self, app):
        """Cleanup on shutdown"""
        # Close all WebSocket connections
        for ws in list(self.ws_clients):
            await ws.close()
            
        # Close MCP connections
        for ws in self.mcp_manager.connections.values():
            await ws.close()
    
    def run(self):
        """Run the dashboard"""
        self.app.on_startup.append(self.background_tasks)
        self.app.on_cleanup.append(self.cleanup_tasks)
        
        logger.info(f"Starting Oracle AGI Unified Dashboard on http://localhost:{self.port}")
        logger.info(f"Dashboard will auto-start required MCP tools and manage connections")
        
        web.run_app(self.app, host='0.0.0.0', port=self.port)


def main():
    """Main entry point"""
    dashboard = OracleAGIUnifiedFinal()
    dashboard.run()


if __name__ == "__main__":
    main()