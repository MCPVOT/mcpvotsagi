#!/usr/bin/env python3
"""
Oracle AGI ULTIMATE Portal - Unified AGI Dashboard with IPFS Integration
========================================================================
The ULTIMATE AGI portal for humans and agents with DeepSeek-R1 + IPFS
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
import ipfshttpclient
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
    HAS_DEPS = True
except ImportError:
    print("Installing core dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "aiohttp", "psutil", "numpy", "pandas", "pyyaml", "requests", "ipfshttpclient"])
    from aiohttp import web
    import aiohttp
    import psutil
    import numpy as np
    import pandas as pd
    HAS_DEPS = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekR1Integration:
    """DeepSeek-R1 Ollama Integration"""

    def __init__(self):
        self.model_name = "DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
        self.ollama_url = "http://localhost:11434"
        self.available = False
        self.check_availability()

    def check_availability(self):
        """Check if DeepSeek-R1 model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if "deepseek" in model.get("name", "").lower():
                        self.model_name = model["name"]
                        self.available = True
                        logger.info(f"DeepSeek-R1 model available: {self.model_name}")
                        return
                logger.warning("DeepSeek-R1 model not found in Ollama")
            else:
                logger.warning("Ollama not accessible")
        except Exception as e:
            logger.error(f"Error checking DeepSeek-R1 availability: {e}")

    async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using DeepSeek-R1"""
        if not self.available:
            return "DeepSeek-R1 model not available. Please ensure Ollama is running with the DeepSeek-R1 model."

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "top_p": 0.9
                }
            }

            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "No response generated")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error generating response: {e}"

class IPFSIntegration:
    """IPFS Integration for decentralized storage"""

    def __init__(self):
        self.client = None
        self.available = False
        self.init_ipfs()

    def init_ipfs(self):
        """Initialize IPFS client"""
        try:
            # Try to connect to IPFS
            self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
            self.available = True
            logger.info("IPFS client connected successfully")
        except Exception as e:
            logger.warning(f"IPFS not available: {e}")
            # Try to start IPFS daemon
            self.start_ipfs_daemon()

    def start_ipfs_daemon(self):
        """Start IPFS daemon"""
        try:
            subprocess.Popen(['ipfs', 'daemon'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(5)  # Wait for daemon to start
            self.init_ipfs()
        except Exception as e:
            logger.error(f"Failed to start IPFS daemon: {e}")

    def add_to_ipfs(self, data: str, name: str = "data.json") -> [str]:
        """Add data to IPFS"""
        if not self.available:
            return None

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(data)
                temp_path = f.name

            # Add to IPFS
            result = self.client.add(temp_path)
            os.unlink(temp_path)  # Clean up

            hash_value = result['Hash']
            logger.info(f"Added to IPFS: {hash_value}")
            return hash_value
        except Exception as e:
            logger.error(f"Error adding to IPFS: {e}")
            return None

    def get_from_ipfs(self, hash_value: str) -> [str]:
        """Get data from IPFS"""
        if not self.available:
            return None

        try:
            data = self.client.cat(hash_value)
            return data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting from IPFS: {e}")
            return None

class MCPAgent:
    """Unified MCP Agent with all capabilities"""

    def __init__(self, name: str, description: str, endpoint: str, port: int = None):
        self.name = name
        self.description = description
        self.endpoint = endpoint
        self.port = port
        self.status = 'checking'
        self.last_used = None
        self.usage_count = 0
        self.capabilities = []

    def check_status(self):
        """Check if MCP agent is running"""
        try:
            if self.port:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', self.port))
                sock.close()
                self.status = 'online' if result == 0 else 'offline'
            else:
                self.status = 'configured'
        except Exception as e:
            self.status = 'error'
            logger.error(f"Error checking {self.name}: {e}")

class UnifiedAGIPortal:
    """Unified AGI Portal - The ultimate AGI dashboard"""

    def __init__(self):
        self.start_time = datetime.now().replace(microsecond=0)
        self.workspace = Path("C:/Workspace/MCPVotsAGI")

        # Initialize core components
        self.deepseek = DeepSeekR1Integration()
        self.ipfs = IPFSIntegration()
        self.websockets = set()
        self.chat_sessions = {}
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.events = deque(maxlen=200)

        # Initialize MCP Agents
        self.mcp_agents = {
            'filesystem': MCPAgent(
                'FileSystem',
                'File operations, reading, writing, manipulation',
                'npx @modelcontextprotocol/server-filesystem',
                port=3000
            ),
            'github': MCPAgent(
                'GitHub',
                'GitHub integration, repos, issues, PRs',
                'npx @modelcontextprotocol/server-github',
                port=3001
            ),
            'memory': MCPAgent(
                'Memory',
                'Persistent memory across sessions',
                'npx @modelcontextprotocol/server-memory',
                port=3002
            ),
            'browser': MCPAgent(
                'Browser',
                'Web automation, scraping, interaction',
                'npx @agentdeskai/browser-tools-mcp',
                port=3006
            ),
            'search': MCPAgent(
                'Search',
                'Web search via Brave API',
                'npx @modelcontextprotocol/server-brave-search',
                port=3003
            ),
            'solana': MCPAgent(
                'Solana',
                'Solana blockchain integration',
                'npx @modelcontextprotocol/server-solana',
                port=3004
            ),
            'huggingface': MCPAgent(
                'HuggingFace',
                'AI model integration via HuggingFace',
                'npx @modelcontextprotocol/server-huggingface',
                port=3005
            )
        }

        # Initialize database
        self.init_database()

        # Log initialization
        self.log_event("System", "Unified AGI Portal initialized")

    def init_database(self):
        """Initialize SQLite database"""
        db_path = self.workspace / "data" / "agi_portal.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                messages TEXT,
                ipfs_hash TEXT,
                metadata TEXT
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_name TEXT,
                action TEXT,
                parameters TEXT,
                response TEXT,
                ipfs_hash TEXT
            )
        ''')

        self.conn.commit()

    def log_event(self, source: str, message: str, level: str = "INFO"):
        """Log an event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'message': message,
            'level': level
        }
        self.events.append(event)
        logger.info(f"[{source}] {message}")

    async def process_chat_message(self, message: str, session_id: str = None) -> dict:
        """Process chat message with AGI intelligence"""
        if not session_id:
            session_id = f"session_{int(time.time())}"

        # Get or create chat session
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = {
                'messages': [],
                'created_at': datetime.now().isoformat(),
                'metadata': {}
            }

        session = self.chat_sessions[session_id]

        # Add user message
        user_msg = {
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        session['messages'].append(user_msg)

        # Analyze message for MCP agent requirements
        required_agents = self.analyze_message_for_agents(message)

        # Generate system prompt
        system_prompt = self.generate_system_prompt(required_agents)

        # Generate response using DeepSeek-R1
        response = await self.deepseek.generate_response(message, system_prompt)

        # Add assistant response
        assistant_msg = {
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'agents_used': required_agents
        }
        session['messages'].append(assistant_msg)

        # Store in IPFS
        ipfs_hash = self.ipfs.add_to_ipfs(json.dumps(session, indent=2))
        if ipfs_hash:
            session['ipfs_hash'] = ipfs_hash

        # Save to database
        self.save_chat_session(session_id, session)

        self.log_event("Chat", f"Processed message in session {session_id}")

        return {
            'response': response,
            'session_id': session_id,
            'ipfs_hash': ipfs_hash,
            'agents_used': required_agents
        }

    def analyze_message_for_agents(self, message: str) -> list:
        """Analyze message to determine required MCP agents"""
        required_agents = []
        message_lower = message.lower()

        # File operations
        if any(word in message_lower for word in ['file', 'read', 'write', 'save', 'load', 'directory']):
            required_agents.append('filesystem')

        # GitHub operations
        if any(word in message_lower for word in ['github', 'repo', 'pull request', 'issue', 'commit']):
            required_agents.append('github')

        # Web operations
        if any(word in message_lower for word in ['search', 'web', 'browse', 'scrape', 'website']):
            required_agents.append('browser')
            required_agents.append('search')

        # Blockchain operations
        if any(word in message_lower for word in ['solana', 'blockchain', 'crypto', 'token', 'wallet']):
            required_agents.append('solana')

        # AI/ML operations
        if any(word in message_lower for word in ['model', 'ai', 'machine learning', 'huggingface']):
            required_agents.append('huggingface')

        # Memory operations
        if any(word in message_lower for word in ['remember', 'recall', 'store', 'memory']):
            required_agents.append('memory')

        return required_agents

    def generate_system_prompt(self, required_agents: list) -> str:
        """Generate system prompt based on required agents"""
        base_prompt = """You are the Oracle AGI, a unified artificial general intelligence portal. You have access to multiple MCP agents and can perform complex tasks across domains.

Your capabilities include:
- Advanced reasoning and planning
- File system operations
- GitHub integration
- Web browsing and search
- Blockchain operations (Solana)
- AI model integration
- Persistent memory
- IPFS decentralized storage

When answering:
1. Provide clear, actionable responses
2. Use available agents when needed
3. Explain complex concepts simply
4. Offer multiple approaches when possible
5. Store important information in IPFS for permanence

"""

        if required_agents:
            agent_descriptions = []
            for agent_name in required_agents:
                if agent_name in self.mcp_agents:
                    agent = self.mcp_agents[agent_name]
                    agent_descriptions.append(f"- {agent.name}: {agent.description}")

            if agent_descriptions:
                base_prompt += f"\nAvailable agents for this task:\n" + "\n".join(agent_descriptions)

        return base_prompt

    def save_chat_session(self, session_id: str, session: dict):
        """Save chat session to database"""
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO chat_sessions (id, updated_at, messages, ipfs_hash, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                datetime.now().isoformat(),
                json.dumps(session['messages']),
                session.get('ipfs_hash'),
                json.dumps(session.get('metadata', {}))
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving chat session: {e}")

    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        # Check MCP agents
        for agent in self.mcp_agents.values():
            agent.check_status()

        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': str(datetime.now() - self.start_time),
            'deepseek_r1': {
                'available': self.deepseek.available,
                'model': self.deepseek.model_name,
                'endpoint': self.deepseek.ollama_url
            },
            'ipfs': {
                'available': self.ipfs.available,
                'endpoint': 'http://localhost:5001' if self.ipfs.available else 'Not available'
            },
            'mcp_agents': {
                name: {
                    'status': agent.status,
                    'description': agent.description,
                    'usage_count': agent.usage_count,
                    'last_used': agent.last_used
                } for name, agent in self.mcp_agents.items()
            },
            'chat_sessions': len(self.chat_sessions),
            'total_events': len(self.events),
            'workspace': str(self.workspace)
        }

    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        self.websockets.add(websocket)
        self.log_event("WebSocket", f"Client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')

                    if message_type == 'chat':
                        response = await self.process_chat_message(
                            data.get('message', ''),
                            data.get('session_id')
                        )
                        await websocket.send(json.dumps({
                            'type': 'chat_response',
                            'data': response
                        }))

                    elif message_type == 'status':
                        status = self.get_system_status()
                        await websocket.send(json.dumps({
                            'type': 'status_response',
                            'data': status
                        }))

                    elif message_type == 'ping':
                        await websocket.send(json.dumps({
                            'type': 'pong',
                            'timestamp': datetime.now().isoformat()
                        }))

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.websockets.discard(websocket)
            self.log_event("WebSocket", f"Client disconnected: {websocket.remote_address}")

    async def create_web_app(self):
        """Create the web application"""
        app = web.Application()

        # API routes
        app.router.add_get('/', self.handle_root)
        app.router.add_get('/api/status', self.handle_status)
        app.router.add_post('/api/chat', self.handle_chat)
        app.router.add_get('/api/sessions', self.handle_sessions)
        app.router.add_get('/api/events', self.handle_events)
        app.router.add_get('/api/ipfs/{hash}', self.handle_ipfs_get)

        # Static files
        app.router.add_static('/', path=str(self.workspace / 'static'), name='static')

        return app

    async def handle_root(self, request):
        """Handle root request"""
        html = self.generate_dashboard_html()
        return web.Response(text=html, content_type='text/html')

    async def handle_status(self, request):
        """Handle status request"""
        status = self.get_system_status()
        return web.json_response(status)

    async def handle_chat(self, request):
        """Handle chat request"""
        try:
            data = await request.json()
            response = await self.process_chat_message(
                data.get('message', ''),
                data.get('session_id')
            )
            return web.json_response(response)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_sessions(self, request):
        """Handle sessions request"""
        try:
            cursor = self.conn.execute('''
                SELECT id, created_at, updated_at, ipfs_hash
                FROM chat_sessions
                ORDER BY updated_at DESC
                LIMIT 50
            ''')
            sessions = [dict(row) for row in cursor.fetchall()]
            return web.json_response(sessions)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_events(self, request):
        """Handle events request"""
        return web.json_response(list(self.events))

    async def handle_ipfs_get(self, request):
        """Handle IPFS get request"""
        hash_value = request.match_info['hash']
        data = self.ipfs.get_from_ipfs(hash_value)
        if data:
            return web.Response(text=data, content_type='application/json')
        else:
            return web.json_response({'error': 'Not found'}, status=404)

    def generate_dashboard_html(self) -> str:
        """Generate the main dashboard HTML"""
        status = self.get_system_status()

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle AGI Portal - Ultimate AGI Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
        }}

        .header {{
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }}

        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .panel {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .panel h2 {{
            margin-bottom: 15px;
            font-size: 1.5em;
            color: #fff;
        }}

        .chat-panel {{
            grid-column: 1 / -1;
            min-height: 400px;
        }}

        .chat-container {{
            display: flex;
            flex-direction: column;
            height: 400px;
        }}

        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            margin-bottom: 10px;
        }}

        .message {{
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }}

        .message.user {{
            background: rgba(103, 126, 234, 0.3);
            margin-left: auto;
        }}

        .message.assistant {{
            background: rgba(118, 75, 162, 0.3);
        }}

        .chat-input {{
            display: flex;
            gap: 10px;
        }}

        .chat-input input {{
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            font-size: 16px;
        }}

        .chat-input input::placeholder {{
            color: rgba(255, 255, 255, 0.7);
        }}

        .chat-input button {{
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }}

        .chat-input button:hover {{
            transform: scale(1.05);
        }}

        .status-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}

        .status-item {{
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            text-align: center;
        }}

        .status-item.online {{
            background: rgba(76, 175, 80, 0.3);
        }}

        .status-item.offline {{
            background: rgba(244, 67, 54, 0.3);
        }}

        .agents-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}

        .agent-card {{
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .agent-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .agent-status {{
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .agent-status.online {{
            background: #4caf50;
        }}

        .agent-status.offline {{
            background: #f44336;
        }}

        .agent-status.checking {{
            background: #ff9800;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }}

        .metric {{
            text-align: center;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4caf50;
        }}

        .metric-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            opacity: 0.7;
        }}

        @media (max-width: 768px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌟 Oracle AGI Portal</h1>
        <p class="subtitle">Ultimate AGI Dashboard with DeepSeek-R1 + IPFS Integration</p>
    </div>

    <div class="dashboard">
        <div class="panel chat-panel">
            <h2>💬 AGI Chat Interface</h2>
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message assistant">
                        <strong>Oracle AGI:</strong> Hello! I'm the Oracle AGI, your unified artificial general intelligence portal. I have access to multiple MCP agents and can help with complex tasks across domains. What would you like to accomplish today?
                    </div>
                </div>
                <div class="chat-input">
                    <input type="text" id="chatInput" placeholder="Ask me anything... I have access to files, GitHub, web, blockchain, AI models, and more!">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>

        <div class="panel">
            <h2>🤖 DeepSeek-R1 Status</h2>
            <div class="status-grid">
                <div class="status-item {'online' if status['deepseek_r1']['available'] else 'offline'}">
                    <div>Model Status</div>
                    <div>{'🟢 Online' if status['deepseek_r1']['available'] else '🔴 Offline'}</div>
                </div>
                <div class="status-item">
                    <div>Model Name</div>
                    <div>{status['deepseek_r1']['model']}</div>
                </div>
            </div>
        </div>

        <div class="panel">
            <h2>🌐 IPFS Integration</h2>
            <div class="status-grid">
                <div class="status-item {'online' if status['ipfs']['available'] else 'offline'}">
                    <div>IPFS Status</div>
                    <div>{'🟢 Online' if status['ipfs']['available'] else '🔴 Offline'}</div>
                </div>
                <div class="status-item">
                    <div>Endpoint</div>
                    <div>{status['ipfs']['endpoint']}</div>
                </div>
            </div>
        </div>

        <div class="panel">
            <h2>⚡ MCP Agents</h2>
            <div class="agents-grid">
                {self.generate_agents_html(status['mcp_agents'])}
            </div>
        </div>

        <div class="panel">
            <h2>📊 System Metrics</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{status['chat_sessions']}</div>
                    <div class="metric-label">Chat Sessions</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{status['total_events']}</div>
                    <div class="metric-label">Events</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{status['uptime']}</div>
                    <div class="metric-label">Uptime</div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Oracle AGI Portal - Powered by DeepSeek-R1, MCP Agents, and IPFS</p>
        <p>Built for humans and agents alike 🤖🤝👥</p>
    </div>

    <script>
        let ws = null;
        let currentSessionId = null;

        function connectWebSocket() {{
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');

            ws.onopen = function() {{
                console.log('WebSocket connected');
                // Send ping to keep connection alive
                setInterval(() => {{
                    if (ws.readyState === WebSocket.OPEN) {{
                        ws.send(JSON.stringify({{type: 'ping'}}));
                    }}
                }}, 30000);
            }};

            ws.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                if (data.type === 'chat_response') {{
                    displayMessage('assistant', data.data.response);
                    currentSessionId = data.data.session_id;
                }}
            }};

            ws.onclose = function() {{
                console.log('WebSocket disconnected');
                setTimeout(connectWebSocket, 3000);
            }};
        }}

        function sendMessage() {{
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;

            displayMessage('user', message);
            input.value = '';

            if (ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{
                    type: 'chat',
                    message: message,
                    session_id: currentSessionId
                }}));
            }} else {{
                // Fallback to HTTP
                fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        message: message,
                        session_id: currentSessionId
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    displayMessage('assistant', data.response);
                    currentSessionId = data.session_id;
                }})
                .catch(error => {{
                    displayMessage('assistant', 'Error: ' + error.message);
                }});
            }}
        }}

        function displayMessage(role, content) {{
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + role;
            messageDiv.innerHTML = '<strong>' + (role === 'user' ? 'You' : 'Oracle AGI') + ':</strong> ' + content;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}

        document.getElementById('chatInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                sendMessage();
            }}
        }});

        // Connect WebSocket on page load
        connectWebSocket();

        // Auto-refresh status every 30 seconds
        setInterval(() => {{
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {{
                    // Update status indicators
                    console.log('Status updated:', data);
                }})
                .catch(error => console.error('Status update error:', error));
        }}, 30000);
    </script>
</body>
</html>
        """

    def generate_agents_html(self, agents: dict) -> str:
        """Generate HTML for agents display"""
        html = ""
        for name, agent in agents.items():
            status_class = agent['status']
            html += f"""
                <div class="agent-card">
                    <div class="agent-name">{name.title()}</div>
                    <div class="agent-status {status_class}">{agent['status'].upper()}</div>
                    <div style="font-size: 0.8em; margin-top: 5px;">{agent['description']}</div>
                </div>
            """
        return html

    async def run_server(self, host='localhost', port=8000):
        """Run the AGI portal server"""
        # Create web app
        app = await self.create_web_app()

        # Create and configure WebSocket server
        async def websocket_server():
            await websockets.serve(
                self.websocket_handler,
                host,
                port + 1
            )

        # Start WebSocket server in background
        websocket_task = asyncio.create_task(websocket_server())

        # Start web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        self.log_event("Server", f"Oracle AGI Portal running on http://{host}:{port}")
        self.log_event("WebSocket", f"WebSocket server running on ws://{host}:{port + 1}")

        print(f"""
🌟 Oracle AGI Portal Started Successfully! 🌟

Web Interface: http://{host}:{port}
WebSocket: ws://{host}:{port + 1}

DeepSeek-R1: {'✅ Available' if self.deepseek.available else '❌ Not Available'}
IPFS: {'✅ Available' if self.ipfs.available else '❌ Not Available'}

MCP Agents Status:
{self.format_agents_status()}

The portal is ready for humans and agents!
Use the web interface or connect via WebSocket for real-time interaction.
        """)

        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            self.log_event("Server", "Shutting down...")
            await runner.cleanup()

    def format_agents_status(self) -> str:
        """Format agents status for console output"""
        status_lines = []
        for name, agent in self.mcp_agents.items():
            agent.check_status()
            status = "✅" if agent.status == "online" else "❌"
            status_lines.append(f"  {status} {name.title()}: {agent.status}")
        return "\n".join(status_lines)

async def main():
    """Main entry point"""
    portal = UnifiedAGIPortal()
    await portal.run_server()

if __name__ == "__main__":
    asyncio.run(main())
