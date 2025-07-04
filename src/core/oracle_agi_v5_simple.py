#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle AGI V5 - Simplified Production System
"""

import asyncio
import json
import logging
import sqlite3
import sys
import os
from pathlib import Path
from aiohttp import web
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleAGIV5")

class OracleAGIV5Simple:
    """Simplified Oracle AGI V5 System"""
    
    def __init__(self):
        # Use Windows paths when on Windows
        if sys.platform == "win32":
            self.workspace = Path("C:/Workspace")
        else:
            self.workspace = Path("/mnt/c/Workspace")
            
        self.mcpvots_agi = self.workspace / "MCPVotsAGI"
        self.mcpvots_agi.mkdir(exist_ok=True)
        
        # Initialize database
        self.db_path = self.mcpvots_agi / "oracle_agi_v5.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                action TEXT,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                response TEXT,
                model TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
        
    async def start_system(self):
        """Start the system"""
        logger.info("Starting Oracle AGI V5...")
        
        # Create web app
        app = web.Application()
        
        # Routes
        app.router.add_get('/', self.handle_index)
        app.router.add_get('/api/status', self.handle_status)
        app.router.add_get('/api/trading/signals', self.handle_trading_signals)
        app.router.add_post('/api/chat', self.handle_chat)
        
        # Create dashboard HTML
        await self._create_dashboard()
        
        # Serve static files
        static_path = self.mcpvots_agi / 'static'
        static_path.mkdir(exist_ok=True)
        app.router.add_static('/static', static_path)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 3002)
        await site.start()
        
        logger.info("=" * 60)
        logger.info("Oracle AGI V5 Started Successfully!")
        logger.info("Dashboard: http://localhost:3002")
        logger.info("API Status: http://localhost:3002/api/status")
        logger.info("=" * 60)
        
        # Keep running
        await asyncio.Event().wait()
        
    async def handle_index(self, request):
        """Serve dashboard"""
        html_path = self.mcpvots_agi / 'static' / 'index.html'
        return web.FileResponse(html_path)
        
    async def handle_status(self, request):
        """Get system status"""
        return web.json_response({
            'status': 'online',
            'timestamp': str(Path.ctime(self.db_path)),
            'services': {
                'dashboard': {'status': 'online', 'port': 3002},
                'oracle_core': {'status': 'checking', 'port': 8888},
                'trading': {'status': 'checking', 'port': 8889}
            }
        })
        
    async def handle_trading_signals(self, request):
        """Get trading signals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, action, confidence, timestamp
            FROM trading_signals
            ORDER BY timestamp DESC
            LIMIT 20
        ''')
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'symbol': row[0],
                'action': row[1],
                'confidence': row[2],
                'timestamp': row[3]
            })
            
        # Add some demo signals if empty
        if not signals:
            signals = [
                {'symbol': 'BTC/USDT', 'action': 'BUY', 'confidence': 0.85, 'timestamp': 'now'},
                {'symbol': 'SOL/USDT', 'action': 'HOLD', 'confidence': 0.72, 'timestamp': 'now'},
                {'symbol': 'ETH/USDT', 'action': 'BUY', 'confidence': 0.91, 'timestamp': 'now'}
            ]
            
        conn.close()
        return web.json_response({'signals': signals})
        
    async def handle_chat(self, request):
        """Handle chat requests"""
        data = await request.json()
        message = data.get('message', '')
        model = data.get('model', 'gemini')
        
        # Simple response for now
        response = f"[{model}] Received: {message}"
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (message, response, model)
            VALUES (?, ?, ?)
        ''', (message, response, model))
        conn.commit()
        conn.close()
        
        return web.json_response({
            'response': response,
            'model': model
        })
        
    async def _create_dashboard(self):
        """Create simple dashboard"""
        html = '''<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI V5 Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: #fff;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            color: #00ff88;
            font-size: 3em;
            margin: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: #2a2a2a;
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .status-item {
            background: #333;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .online { color: #00ff88; }
        .offline { color: #ff4444; }
        button {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #00cc77;
        }
        input, select {
            background: #333;
            color: #fff;
            border: 1px solid #555;
            padding: 10px;
            border-radius: 5px;
            width: 100%;
            margin-bottom: 10px;
        }
        .signals {
            max-height: 400px;
            overflow-y: auto;
        }
        .signal {
            background: #333;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .buy { border-left: 4px solid #00ff88; }
        .sell { border-left: 4px solid #ff4444; }
        .hold { border-left: 4px solid #ffaa00; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Oracle AGI V5</h1>
        <p>Production Dashboard</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>System Status</h2>
            <div class="status" id="status">
                <div class="status-item">
                    <h3>Dashboard</h3>
                    <p class="online">ONLINE</p>
                    <p>Port: 3002</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Trading Signals</h2>
            <div class="signals" id="signals">
                <!-- Signals will be loaded here -->
            </div>
            <button onclick="loadSignals()">Refresh Signals</button>
        </div>
        
        <div class="card">
            <h2>AI Chat</h2>
            <select id="model">
                <option value="gemini">Gemini</option>
                <option value="deepseek">DeepSeek</option>
                <option value="claude">Claude</option>
                <option value="gpt4">GPT-4</option>
            </select>
            <input type="text" id="message" placeholder="Enter your message..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()">Send</button>
            <div id="chat-response" style="margin-top: 20px;"></div>
        </div>
    </div>
    
    <script>
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '';
                
                for (const [key, service] of Object.entries(data.services)) {
                    statusDiv.innerHTML += `
                        <div class="status-item">
                            <h3>${key}</h3>
                            <p class="${service.status === 'online' ? 'online' : 'offline'}">${service.status.toUpperCase()}</p>
                            <p>Port: ${service.port}</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading status:', error);
            }
        }
        
        async function loadSignals() {
            try {
                const response = await fetch('/api/trading/signals');
                const data = await response.json();
                
                const signalsDiv = document.getElementById('signals');
                signalsDiv.innerHTML = '';
                
                for (const signal of data.signals) {
                    signalsDiv.innerHTML += `
                        <div class="signal ${signal.action.toLowerCase()}">
                            <div>
                                <strong>${signal.symbol}</strong>
                                <br>Confidence: ${(signal.confidence * 100).toFixed(1)}%
                            </div>
                            <div>
                                <strong>${signal.action}</strong>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading signals:', error);
            }
        }
        
        async function sendMessage() {
            const message = document.getElementById('message').value;
            const model = document.getElementById('model').value;
            
            if (!message) return;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, model })
                });
                const data = await response.json();
                
                document.getElementById('chat-response').innerHTML = `
                    <div style="background: #333; padding: 10px; border-radius: 5px;">
                        <strong>Response:</strong><br>
                        ${data.response}
                    </div>
                `;
                
                document.getElementById('message').value = '';
            } catch (error) {
                console.error('Error sending message:', error);
            }
        }
        
        // Load initial data
        loadStatus();
        loadSignals();
        
        // Auto-refresh
        setInterval(loadStatus, 5000);
        setInterval(loadSignals, 10000);
    </script>
</body>
</html>'''
        
        # Save dashboard
        html_path = self.mcpvots_agi / 'static' / 'index.html'
        html_path.parent.mkdir(exist_ok=True)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        logger.info("Dashboard created")

async def main():
    """Main entry point"""
    oracle = OracleAGIV5Simple()
    await oracle.start_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System stopped by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)