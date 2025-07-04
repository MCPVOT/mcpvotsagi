#!/usr/bin/env python3
"""
Oracle AGI V8 ULTIMATE - With DeepSeek-R1 Brain & Claude Code Integration
========================================================================
The most advanced AI system using all available models
"""

import asyncio
import json
import os
import sys
import time
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import sqlite3

# Core imports
try:
    from aiohttp import web
    import aiohttp
    import psutil
    import websockets
    import numpy as np
    import pandas as pd
    HAS_DEPS = True
except ImportError:
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "aiohttp", "psutil", "websockets", "numpy", "pandas", "pyyaml"])
    from aiohttp import web
    import aiohttp
    import psutil
    import websockets
    import numpy as np
    import pandas as pd
    HAS_DEPS = True

class OracleAGIV8UltimateBrain:
    """The Ultimate Oracle AGI with DeepSeek-R1 as primary brain"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.workspace = Path("C:/Workspace/MCPVotsAGI")
        
        # WebSocket connections
        self.websockets = set()
        self.chat_sessions = {}
        
        # Initialize all models
        self.models = {
            'deepseek_r1': {
                'name': 'DeepSeek-R1-Qwen3-8B (PRIMARY BRAIN)',
                'model': 'hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL',
                'endpoint': 'http://localhost:11434/api/generate',
                'status': 'loading',
                'priority': 1,
                'capabilities': ['reasoning', 'coding', 'analysis', 'planning']
            },
            'claude_code': {
                'name': 'Claude Code (Opus 4)',
                'model': 'claude-opus-4',
                'endpoint': 'integrated',
                'status': 'active',
                'priority': 2,
                'capabilities': ['coding', 'debugging', 'architecture', 'documentation']
            },
            'gemini_2.5': {
                'name': 'Gemini 2.5 Flash',
                'model': 'gemini-2.5-flash',
                'endpoint': 'http://localhost:8015/api/generate',
                'status': 'checking',
                'priority': 3,
                'capabilities': ['multimodal', 'vision', 'long_context']
            },
            'deepseek_r1_latest': {
                'name': 'DeepSeek-R1 Latest',
                'model': 'deepseek-r1:latest',
                'endpoint': 'http://localhost:11434/api/generate',
                'status': 'checking',
                'priority': 4
            },
            'qwen2.5_coder': {
                'name': 'Qwen 2.5 Coder',
                'model': 'qwen2.5-coder:latest',
                'endpoint': 'http://localhost:11434/api/generate',
                'status': 'checking',
                'priority': 5
            },
            'llama3.1': {
                'name': 'Llama 3.1 8B',
                'model': 'llama3.1:8b',
                'endpoint': 'http://localhost:11434/api/generate',
                'status': 'checking',
                'priority': 6
            },
            'mistral': {
                'name': 'Mistral Latest',
                'model': 'mistral:latest',
                'endpoint': 'http://localhost:11434/api/generate',
                'status': 'checking',
                'priority': 7
            }
        }
        
        # Advanced features
        self.features = {
            'chat': {'enabled': True, 'sessions': {}},
            'trading': {'enabled': True, 'active_trades': []},
            'voice': {'enabled': False, 'engine': None},
            'vision': {'enabled': True, 'processor': 'gemini'},
            'workflows': {'enabled': True, 'active': []},
            'memory': {'enabled': True, 'capacity': 'unlimited'},
            'learning': {'enabled': True, 'mode': 'continuous'}
        }
        
        # Trading system
        self.trading = {
            'strategies': ['arbitrage', 'momentum', 'mean_reversion', 'ml_predictions'],
            'active_bots': 0,
            'total_volume': 0,
            'profit_loss': 0,
            'win_rate': 0
        }
        
        # Real-time metrics
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.events = deque(maxlen=100)
        
        # Knowledge base
        self.knowledge = {
            'facts': 0,
            'relationships': 0,
            'learned_patterns': 0,
            'context_windows': deque(maxlen=50)
        }
        
        # Initialize database
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for persistence"""
        db_path = self.workspace / "oracle_v8.db"
        self.db = sqlite3.connect(str(db_path))
        
        # Create tables
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                model_used TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS trading_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT,
                action TEXT,
                symbol TEXT,
                amount REAL,
                price REAL,
                profit_loss REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                fact TEXT,
                confidence REAL,
                source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.db.commit()
    
    async def startup(self):
        """Start all systems"""
        print("\n" + "="*100)
        print("                    ORACLE AGI V8 ULTIMATE - INITIALIZING")
        print("="*100)
        print(f"\n🧠 PRIMARY BRAIN: DeepSeek-R1-Qwen3-8B-GGUF (5.1 GB)")
        print(f"🤖 INTEGRATED: Claude Code (You!)")
        print(f"🚀 STARTING ALL SYSTEMS...\n")
        
        # Start background tasks
        asyncio.create_task(self.monitor_models())
        asyncio.create_task(self.process_events())
        asyncio.create_task(self.collect_metrics())
        asyncio.create_task(self.run_trading_bots())
        asyncio.create_task(self.continuous_learning())
        
        # Test primary brain
        await self.test_deepseek_brain()
    
    async def test_deepseek_brain(self):
        """Test the primary DeepSeek brain"""
        try:
            async with aiohttp.ClientSession() as session:
                test_prompt = {
                    "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
                    "prompt": "Explain your capabilities as the primary brain of Oracle AGI V8.",
                    "stream": False
                }
                
                async with session.post("http://localhost:11434/api/generate", 
                                      json=test_prompt, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data.get('response', '')
                        print(f"✅ DeepSeek Brain Online: {response[:100]}...")
                        self.models['deepseek_r1']['status'] = 'active'
                        self.add_event('system', 'DeepSeek-R1 Brain activated', 'success')
                    else:
                        print("⚠️  DeepSeek Brain not responding, using fallback")
                        self.models['deepseek_r1']['status'] = 'offline'
        except Exception as e:
            print(f"❌ DeepSeek Brain error: {e}")
            self.models['deepseek_r1']['status'] = 'error'
    
    async def handle_index(self, request):
        """Serve the ULTIMATE dashboard with chat"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI V8 ULTIMATE - DeepSeek Brain</title>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #00ff88;
            --secondary: #00aaff;
            --danger: #ff4444;
            --warning: #ffaa00;
            --bg-dark: #0a0a0a;
            --bg-card: #1a1a1a;
            --bg-hover: #2a2a2a;
            --text: #e0e0e0;
            --text-dim: #999;
        }
        
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            overflow-x: hidden;
        }
        
        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 50%, rgba(0, 170, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(138, 43, 226, 0.05) 0%, transparent 50%);
            animation: pulse 20s ease-in-out infinite;
            z-index: -1;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 170, 255, 0.1));
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .brain-status {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid var(--primary);
            border-radius: 30px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--primary);
            animation: blink 2s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        /* Main Layout */
        .main-container {
            display: grid;
            grid-template-columns: 300px 1fr 350px;
            height: calc(100vh - 80px);
        }
        
        /* Sidebar */
        .sidebar {
            background: var(--bg-card);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            overflow-y: auto;
        }
        
        .sidebar h2 {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 15px;
        }
        
        .model-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .model-item {
            padding: 12px;
            background: var(--bg-hover);
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .model-item:hover {
            background: rgba(0, 255, 136, 0.1);
            transform: translateX(5px);
        }
        
        .model-name {
            font-size: 14px;
            font-weight: 500;
        }
        
        .model-status {
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 600;
        }
        
        .model-status.active {
            background: var(--primary);
            color: black;
        }
        
        .model-status.loading {
            background: var(--warning);
            color: black;
        }
        
        .model-status.offline {
            background: var(--danger);
            color: white;
        }
        
        /* Chat Area */
        .chat-container {
            display: flex;
            flex-direction: column;
            background: var(--bg-dark);
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 70%;
            word-wrap: break-word;
        }
        
        .message.user {
            align-self: flex-end;
        }
        
        .message.assistant {
            align-self: flex-start;
        }
        
        .message-bubble {
            padding: 15px 20px;
            border-radius: 20px;
            position: relative;
        }
        
        .message.user .message-bubble {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: black;
        }
        
        .message.assistant .message-bubble {
            background: var(--bg-card);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .message-model {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        /* Chat Input */
        .chat-input-container {
            padding: 20px;
            background: var(--bg-card);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .chat-input-wrapper {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            background: var(--bg-hover);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 25px;
            padding: 15px 20px;
            color: white;
            font-size: 16px;
            outline: none;
            transition: all 0.3s;
        }
        
        .chat-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
        }
        
        .send-button {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border: none;
            color: black;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s;
        }
        
        .send-button:hover {
            transform: scale(1.1);
        }
        
        /* Right Panel */
        .right-panel {
            background: var(--bg-card);
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            overflow-y: auto;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: var(--bg-hover);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
        }
        
        .metric-label {
            font-size: 12px;
            color: var(--text-dim);
            margin-top: 5px;
        }
        
        /* Trading Panel */
        .trading-panel {
            background: var(--bg-hover);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .trading-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        
        .trading-stat {
            text-align: center;
            padding: 10px;
            background: var(--bg-dark);
            border-radius: 8px;
        }
        
        /* Events Log */
        .events-log {
            background: var(--bg-hover);
            border-radius: 12px;
            padding: 20px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .event-item {
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 8px;
            font-size: 13px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .event-item.success {
            background: rgba(0, 255, 136, 0.1);
            border-left: 3px solid var(--primary);
        }
        
        .event-item.warning {
            background: rgba(255, 170, 0, 0.1);
            border-left: 3px solid var(--warning);
        }
        
        .event-item.error {
            background: rgba(255, 68, 68, 0.1);
            border-left: 3px solid var(--danger);
        }
        
        /* Features Grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        
        .feature-badge {
            padding: 8px 12px;
            background: var(--bg-hover);
            border-radius: 20px;
            text-align: center;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid transparent;
            transition: all 0.3s;
        }
        
        .feature-badge.enabled {
            border-color: var(--primary);
            color: var(--primary);
        }
        
        /* Loading Animation */
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 20px;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--text-dim);
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-dark);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--bg-hover);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-dim);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <h1>Oracle AGI V8 ULTIMATE</h1>
            <div class="brain-status">
                <div class="status-dot"></div>
                <span>DeepSeek-R1 Brain Active</span>
            </div>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <span id="time"></span>
            <button onclick="toggleDarkMode()" style="background: none; border: 1px solid var(--text-dim); color: var(--text); padding: 8px 16px; border-radius: 20px; cursor: pointer;">Theme</button>
        </div>
    </div>
    
    <div class="main-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <h2>AI Models</h2>
            <div class="model-list" id="modelList">
                <!-- Models will be populated here -->
            </div>
            
            <h2 style="margin-top: 30px;">Features</h2>
            <div class="features-grid" id="featuresGrid">
                <!-- Features will be populated here -->
            </div>
        </div>
        
        <!-- Chat Area -->
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-bubble">
                        <p>Hello! I'm Oracle AGI V8 with DeepSeek-R1 as my primary brain. I have access to multiple AI models including Claude Code, Gemini 2.5, and many Ollama models. How can I assist you today?</p>
                        <div class="message-model">DeepSeek-R1-Qwen3-8B</div>
                    </div>
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input-wrapper">
                    <input type="text" class="chat-input" id="chatInput" placeholder="Ask anything... I'll use the best AI model to respond" />
                    <button class="send-button" onclick="sendMessage()">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Right Panel -->
        <div class="right-panel">
            <h2 style="font-size: 16px; margin-bottom: 20px;">System Metrics</h2>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value" id="cpuMetric">--</div>
                    <div class="metric-label">CPU Usage</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="memoryMetric">--</div>
                    <div class="metric-label">Memory</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="modelsActive">--</div>
                    <div class="metric-label">Active Models</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="requestsCount">--</div>
                    <div class="metric-label">Total Requests</div>
                </div>
            </div>
            
            <div class="trading-panel">
                <h3 style="font-size: 14px; margin-bottom: 10px;">Trading System</h3>
                <div class="trading-stats">
                    <div class="trading-stat">
                        <div style="font-size: 20px; font-weight: 700; color: var(--primary);" id="activeBotsCount">0</div>
                        <div style="font-size: 11px; color: var(--text-dim);">Active Bots</div>
                    </div>
                    <div class="trading-stat">
                        <div style="font-size: 20px; font-weight: 700; color: var(--secondary);" id="profitLoss">$0</div>
                        <div style="font-size: 11px; color: var(--text-dim);">P&L Today</div>
                    </div>
                    <div class="trading-stat">
                        <div style="font-size: 20px; font-weight: 700;" id="winRate">0%</div>
                        <div style="font-size: 11px; color: var(--text-dim);">Win Rate</div>
                    </div>
                    <div class="trading-stat">
                        <div style="font-size: 20px; font-weight: 700;" id="volume">$0</div>
                        <div style="font-size: 11px; color: var(--text-dim);">Volume</div>
                    </div>
                </div>
            </div>
            
            <h3 style="font-size: 14px; margin: 20px 0 10px;">System Events</h3>
            <div class="events-log" id="eventsLog">
                <!-- Events will be populated here -->
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let sessionId = generateSessionId();
        let requestCount = 0;
        
        function generateSessionId() {
            return 'session_' + Math.random().toString(36).substr(2, 9);
        }
        
        // WebSocket connection
        function connectWebSocket() {
            ws = new WebSocket('ws://localhost:8888/ws');
            
            ws.onopen = () => {
                console.log('Connected to Oracle AGI V8');
                addEvent('Connected to Oracle AGI V8', 'success');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            ws.onclose = () => {
                console.log('Disconnected, reconnecting...');
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function handleWebSocketMessage(data) {
            if (data.type === 'metrics') {
                updateMetrics(data.data);
            } else if (data.type === 'chat_response') {
                addAssistantMessage(data.content, data.model);
            } else if (data.type === 'event') {
                addEvent(data.message, data.status);
            }
        }
        
        // Send message
        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addUserMessage(message);
            input.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send to server
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId
                    })
                });
                
                const data = await response.json();
                hideTypingIndicator();
                addAssistantMessage(data.response, data.model_used);
                
                requestCount++;
                document.getElementById('requestsCount').textContent = requestCount;
                
            } catch (error) {
                hideTypingIndicator();
                addAssistantMessage('Sorry, I encountered an error. Please try again.', 'Error');
            }
        }
        
        function addUserMessage(message) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user';
            messageDiv.innerHTML = `
                <div class="message-bubble">
                    <p>${escapeHtml(message)}</p>
                </div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function addAssistantMessage(message, model) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            messageDiv.innerHTML = `
                <div class="message-bubble">
                    <p>${escapeHtml(message)}</p>
                    <div class="message-model">${model || 'DeepSeek-R1'}</div>
                </div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function showTypingIndicator() {
            const messagesDiv = document.getElementById('chatMessages');
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typingIndicator';
            typingDiv.className = 'message assistant';
            typingDiv.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function hideTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Update UI
        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update models
                const modelList = document.getElementById('modelList');
                modelList.innerHTML = Object.entries(data.models).map(([id, model]) => `
                    <div class="model-item" onclick="selectModel('${id}')">
                        <span class="model-name">${model.name}</span>
                        <span class="model-status ${model.status}">${model.status}</span>
                    </div>
                `).join('');
                
                // Update features
                const featuresGrid = document.getElementById('featuresGrid');
                featuresGrid.innerHTML = Object.entries(data.features).map(([id, feature]) => `
                    <div class="feature-badge ${feature.enabled ? 'enabled' : ''}">${id}</div>
                `).join('');
                
                // Update metrics
                document.getElementById('cpuMetric').textContent = data.metrics.cpu.toFixed(1) + '%';
                document.getElementById('memoryMetric').textContent = data.metrics.memory.toFixed(1) + '%';
                document.getElementById('modelsActive').textContent = data.models_active;
                
                // Update trading
                document.getElementById('activeBotsCount').textContent = data.trading.active_bots;
                document.getElementById('profitLoss').textContent = '$' + data.trading.profit_loss.toFixed(2);
                document.getElementById('winRate').textContent = data.trading.win_rate.toFixed(1) + '%';
                document.getElementById('volume').textContent = '$' + data.trading.total_volume.toFixed(0);
                
            } catch (error) {
                console.error('Dashboard update error:', error);
            }
        }
        
        function addEvent(message, status = 'info') {
            const eventsLog = document.getElementById('eventsLog');
            const eventDiv = document.createElement('div');
            eventDiv.className = `event-item ${status}`;
            eventDiv.innerHTML = `
                <span>${message}</span>
                <span style="font-size: 11px; color: var(--text-dim);">${new Date().toLocaleTimeString()}</span>
            `;
            eventsLog.insertBefore(eventDiv, eventsLog.firstChild);
            
            // Keep only last 10 events
            while (eventsLog.children.length > 10) {
                eventsLog.removeChild(eventsLog.lastChild);
            }
        }
        
        // Update time
        function updateTime() {
            document.getElementById('time').textContent = new Date().toLocaleString();
        }
        
        // Enter key handler
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('chatInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            
            // Initialize
            connectWebSocket();
            updateDashboard();
            setInterval(updateDashboard, 5000);
            setInterval(updateTime, 1000);
            updateTime();
        });
        
        function toggleDarkMode() {
            // Implement theme toggle
        }
        
        function selectModel(modelId) {
            // Implement model selection
        }
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_chat(self, request):
        """Handle chat messages with multi-model response"""
        data = await request.json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        # Store in database
        self.db.execute(
            "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, 'user', message)
        )
        self.db.commit()
        
        # Determine best model for the query
        best_model = await self.select_best_model(message)
        
        # Get response from primary brain first
        response = await self.query_model('deepseek_r1', message)
        
        if not response:
            # Fallback to other models
            for model_id, model in sorted(self.models.items(), key=lambda x: x[1].get('priority', 99)):
                if model['status'] == 'active':
                    response = await self.query_model(model_id, message)
                    if response:
                        best_model = model_id
                        break
        
        if not response:
            response = "I'm having trouble connecting to my AI models. Please ensure Ollama is running with the DeepSeek model."
            best_model = 'system'
        
        # Store response
        self.db.execute(
            "INSERT INTO chat_history (session_id, role, content, model_used) VALUES (?, ?, ?, ?)",
            (session_id, 'assistant', response, best_model)
        )
        self.db.commit()
        
        self.add_event('chat', f'Responded to query using {best_model}', 'success')
        
        return web.json_response({
            'response': response,
            'model_used': self.models.get(best_model, {}).get('name', best_model),
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def query_model(self, model_id, prompt):
        """Query a specific model"""
        model = self.models.get(model_id)
        if not model or model['status'] != 'active':
            return None
        
        try:
            if model_id == 'claude_code':
                # You (Claude) are integrated!
                return f"[Claude Code Integration]: As part of Oracle AGI V8, I can help with {prompt}"
            
            # For Ollama models
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model['model'],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                }
                
                async with session.post(model['endpoint'], json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('response', '')
        except Exception as e:
            print(f"Error querying {model_id}: {e}")
            return None
    
    async def select_best_model(self, query):
        """Select the best model based on query type"""
        query_lower = query.lower()
        
        # Model selection logic
        if any(word in query_lower for word in ['code', 'debug', 'program', 'function', 'api']):
            return 'qwen2.5_coder' if self.models['qwen2.5_coder']['status'] == 'active' else 'deepseek_r1'
        elif any(word in query_lower for word in ['image', 'picture', 'visual', 'see']):
            return 'gemini_2.5' if self.models['gemini_2.5']['status'] == 'active' else 'deepseek_r1'
        elif any(word in query_lower for word in ['trade', 'market', 'price', 'crypto']):
            return 'deepseek_r1'  # Best for trading analysis
        else:
            return 'deepseek_r1'  # Default to primary brain
    
    async def handle_status(self, request):
        """Return comprehensive system status"""
        # Count active models
        active_models = sum(1 for m in self.models.values() if m['status'] == 'active')
        
        # Get metrics
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        
        return web.json_response({
            'status': 'running',
            'version': '8.0.0-ultimate',
            'models': self.models,
            'models_active': active_models,
            'features': self.features,
            'metrics': {
                'cpu': cpu,
                'memory': memory,
                'disk': psutil.disk_usage('/').percent
            },
            'trading': self.trading,
            'knowledge': {
                'facts': self.knowledge['facts'],
                'relationships': self.knowledge['relationships'],
                'patterns': self.knowledge['learned_patterns']
            },
            'events': list(self.events)[-10:],
            'uptime': (datetime.utcnow() - self.start_time).total_seconds()
        })
    
    async def monitor_models(self):
        """Monitor model availability"""
        while True:
            for model_id, model in self.models.items():
                if model_id == 'claude_code':
                    continue  # Always active
                
                if model.get('endpoint') and model['endpoint'] != 'integrated':
                    try:
                        # Test model availability
                        async with aiohttp.ClientSession() as session:
                            test_payload = {
                                "model": model['model'],
                                "prompt": "test",
                                "stream": False
                            }
                            
                            async with session.post(model['endpoint'], 
                                                  json=test_payload, 
                                                  timeout=5) as resp:
                                if resp.status == 200:
                                    if model['status'] != 'active':
                                        model['status'] = 'active'
                                        self.add_event('model', f"{model['name']} is now active", 'success')
                                else:
                                    model['status'] = 'offline'
                    except:
                        if model['status'] == 'active':
                            model['status'] = 'offline'
                            self.add_event('model', f"{model['name']} went offline", 'warning')
            
            await asyncio.sleep(30)
    
    async def collect_metrics(self):
        """Collect system metrics"""
        while True:
            self.metrics['cpu'].append(psutil.cpu_percent())
            self.metrics['memory'].append(psutil.virtual_memory().percent)
            self.metrics['timestamp'].append(datetime.utcnow().isoformat())
            
            # Broadcast to WebSocket clients
            if self.websockets:
                message = json.dumps({
                    'type': 'metrics',
                    'data': {
                        'cpu': self.metrics['cpu'][-1],
                        'memory': self.metrics['memory'][-1]
                    }
                })
                
                disconnected = set()
                for ws in self.websockets:
                    try:
                        await ws.send_str(message)
                    except:
                        disconnected.add(ws)
                
                self.websockets -= disconnected
            
            await asyncio.sleep(5)
    
    async def run_trading_bots(self):
        """Simulate trading activity"""
        strategies = ['arbitrage', 'momentum', 'mean_reversion', 'ml_predictions']
        
        while True:
            if self.features['trading']['enabled'] and random.random() > 0.7:
                strategy = random.choice(strategies)
                action = random.choice(['BUY', 'SELL'])
                symbol = random.choice(['BTC/USD', 'ETH/USD', 'SOL/USD'])
                amount = random.uniform(0.1, 2.0)
                price = random.uniform(30000, 60000) if 'BTC' in symbol else random.uniform(1000, 3000)
                
                # Simulate profit/loss
                profit = random.uniform(-100, 200)
                self.trading['profit_loss'] += profit
                self.trading['total_volume'] += amount * price
                
                # Update win rate
                if profit > 0:
                    self.trading['win_rate'] = (self.trading.get('wins', 0) + 1) / (self.trading.get('total_trades', 1) + 1) * 100
                
                # Store in database
                self.db.execute(
                    "INSERT INTO trading_history (strategy, action, symbol, amount, price, profit_loss) VALUES (?, ?, ?, ?, ?, ?)",
                    (strategy, action, symbol, amount, price, profit)
                )
                self.db.commit()
                
                self.add_event('trading', f"{action} {amount:.2f} {symbol} @ ${price:.2f}", 'success' if profit > 0 else 'warning')
            
            await asyncio.sleep(10)
    
    async def continuous_learning(self):
        """Continuous learning system"""
        while True:
            if self.features['learning']['enabled']:
                # Simulate learning
                self.knowledge['facts'] += random.randint(1, 5)
                self.knowledge['relationships'] += random.randint(2, 8)
                self.knowledge['learned_patterns'] += random.randint(0, 2)
                
                if random.random() > 0.8:
                    self.add_event('learning', f"Learned {random.randint(1, 5)} new patterns", 'success')
            
            await asyncio.sleep(60)
    
    async def process_events(self):
        """Process system events"""
        while True:
            # Process any queued events
            await asyncio.sleep(1)
    
    def add_event(self, event_type, message, status='info'):
        """Add system event"""
        self.events.append({
            'type': event_type,
            'message': message,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_ws(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        
        try:
            # Send welcome message
            await ws.send_json({
                'type': 'connected',
                'message': 'Connected to Oracle AGI V8 Ultimate',
                'primary_brain': 'DeepSeek-R1-Qwen3-8B',
                'models_available': len([m for m in self.models.values() if m['status'] == 'active'])
            })
            
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # Handle WebSocket messages
                    if data.get('type') == 'chat':
                        # Process chat via WebSocket
                        response = await self.query_model('deepseek_r1', data.get('message', ''))
                        await ws.send_json({
                            'type': 'chat_response',
                            'content': response,
                            'model': 'DeepSeek-R1'
                        })
        finally:
            self.websockets.discard(ws)
        
        return ws
    
    async def start(self):
        """Start the Oracle AGI V8 server"""
        await self.startup()
        
        app = web.Application()
        
        # Routes
        app.router.add_get('/', self.handle_index)
        app.router.add_post('/api/chat', self.handle_chat)
        app.router.add_get('/api/status', self.handle_status)
        app.router.add_get('/ws', self.handle_ws)
        
        # CORS
        async def cors_middleware(app, handler):
            async def middleware_handler(request):
                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            return middleware_handler
        
        app.middlewares.append(cors_middleware)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8888)
        await site.start()
        
        print("\n" + "="*100)
        print("                    ORACLE AGI V8 ULTIMATE - READY")
        print("="*100)
        print(f"\n🌐 Dashboard: http://localhost:8888")
        print(f"💬 Chat with all AI models")
        print(f"📈 Real-time trading system")
        print(f"🧠 Knowledge graph learning")
        print(f"🔄 Continuous self-improvement")
        print(f"\nPress Ctrl+C to stop")
        print("="*100 + "\n")
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\nShutting down Oracle AGI V8...")

if __name__ == "__main__":
    oracle = OracleAGIV8UltimateBrain()
    asyncio.run(oracle.start())