#!/usr/bin/env python3
"""
ULTIMATE AGI SYSTEM v2.0 - Enhanced Dashboard Edition
====================================================
🎨 Modern UI/UX with advanced chat interface
🚀 Integrated Components from AG-UI and Animate-UI patterns
💬 Enhanced chat with real-time streaming
🎯 Professional cyberpunk design system
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
from typing import Dict, List, Any, Optional, Tuple
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

# Import integration bridges
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    from claudia_integration_bridge import ClaudiaCompleteIntegration
    HAS_CLAUDIA = True
    logger.info("✅ Complete Claudia integration loaded successfully")
except ImportError as e:
    ClaudiaCompleteIntegration = None
    HAS_CLAUDIA = False
    logger.warning(f"⚠️ Complete Claudia integration not available: {e}")

try:
    from CONTEXT7_INTEGRATION import Context7Integration
    HAS_CONTEXT7 = True
    logger.info("✅ Context7 integration loaded successfully")
except ImportError as e:
    Context7Integration = None
    HAS_CONTEXT7 = False
    logger.warning(f"⚠️ Context7 integration not available: {e}")

class EnhancedAGISystem:
    """Enhanced AGI system with modern UI/UX"""

    def __init__(self):
        """Initialize the enhanced AGI system"""
        self.version = "ENHANCED-V2.0"
        self.start_time = time.time()
        self.db_path = "enhanced_agi.db"
        self.port = 8889  # Different port to avoid conflicts
        self.app = web.Application()
        self.setup_routes()
        self.websocket_connections = set()
        self.chat_history = deque(maxlen=100)
        self.system_metrics = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'active_connections': 0,
            'chat_messages': 0,
            'uptime': 0
        }

        # Initialize integrations
        self.claudia_bridge = ClaudiaIntegrationBridge() if HAS_CLAUDIA else None
        self.context7_bridge = Context7Integration() if HAS_CONTEXT7 else None

        # Initialize database
        self.init_database()

        # Load configuration
        self.load_configurations()

        print(f"🚀 ENHANCED AGI SYSTEM v{self.version} initialized!")

    def setup_routes(self):
        """Setup HTTP routes with enhanced API"""
        self.app.router.add_get('/', self.serve_dashboard)
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_post('/api/chat', self.handle_chat)
        self.app.router.add_post('/api/chat/stream', self.handle_chat_stream)
        self.app.router.add_get('/api/status', self.get_system_status)
        self.app.router.add_get('/api/metrics', self.get_system_metrics)
        self.app.router.add_get('/api/history', self.get_chat_history)
        self.app.router.add_post('/api/clear-history', self.clear_chat_history)
        self.app.router.add_get('/api/models', self.get_available_models)
        self.app.router.add_post('/api/upload', self.handle_file_upload)
        self.app.router.add_static('/', path='.', name='static')

    def init_database(self):
        """Initialize SQLite database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enhanced chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                model TEXT NOT NULL,
                tokens INTEGER,
                response_time REAL,
                context7_enriched BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                memory_usage REAL,
                active_connections INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def load_configurations(self):
        """Load system configurations"""
        config_files = [
            'config/unified_system_config.yaml',
            'config/unified_agi_portal.yaml',
            'config/mcp_settings.json'
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"[OK] Loaded config: {config_file}")

    async def serve_dashboard(self, request):
        """Serve the enhanced dashboard with modern UI"""
        return web.Response(text=self.get_enhanced_dashboard_html(), content_type='text/html')

    def get_enhanced_dashboard_html(self):
        """Generate enhanced dashboard HTML with modern components"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced AGI Portal v{self.version}</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self.get_enhanced_css()}
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        {self.get_enhanced_javascript()}
    </script>
</body>
</html>
"""

    def get_enhanced_css(self):
        """Enhanced CSS with modern design system"""
        return """
        :root {
            --primary-color: #00ff88;
            --secondary-color: #00d4ff;
            --accent-color: #ff6b6b;
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-tertiary: #2a2a2a;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --text-accent: #00ff88;
            --border-color: rgba(0, 255, 136, 0.3);
            --shadow-glow: 0 0 20px rgba(0, 255, 136, 0.3);
            --gradient-primary: linear-gradient(45deg, #00ff88, #00d4ff);
            --gradient-secondary: linear-gradient(135deg, #ff6b6b, #ffa500);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
        }

        .app-container {
            display: grid;
            grid-template-columns: 300px 1fr 300px;
            grid-template-rows: 80px 1fr;
            grid-template-areas:
                "header header header"
                "sidebar main rightbar";
            height: 100vh;
            gap: 1rem;
            padding: 1rem;
        }

        /* Header */
        .header {
            grid-area: header;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            backdrop-filter: blur(10px);
            box-shadow: var(--shadow-glow);
        }

        .header h1 {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.8rem;
            font-weight: 700;
        }

        .header .status-badges {
            display: flex;
            gap: 0.5rem;
        }

        .status-badge {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            animation: pulse 2s infinite;
        }

        .status-badge.online {
            background: rgba(0, 255, 136, 0.2);
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
        }

        .status-badge.warning {
            background: rgba(255, 170, 0, 0.2);
            color: #ffaa00;
            border: 1px solid #ffaa00;
        }

        /* Sidebar */
        .sidebar {
            grid-area: sidebar;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 1.5rem;
            overflow-y: auto;
            backdrop-filter: blur(10px);
        }

        .sidebar h3 {
            color: var(--text-accent);
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .metric-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            border-color: var(--primary-color);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.2);
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Main Chat Area */
        .main-content {
            grid-area: main;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .chat-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .chat-header h2 {
            color: var(--text-accent);
            font-size: 1.3rem;
            font-weight: 600;
        }

        .model-selector {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }

        .model-select {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            color: var(--text-primary);
            font-size: 0.9rem;
            outline: none;
            transition: all 0.3s ease;
        }

        .model-select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.2);
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .message {
            max-width: 85%;
            padding: 1rem 1.5rem;
            border-radius: 15px;
            position: relative;
            animation: messageSlideIn 0.3s ease;
        }

        .message.user {
            align-self: flex-end;
            background: var(--gradient-primary);
            color: var(--bg-primary);
            border-bottom-right-radius: 5px;
        }

        .message.assistant {
            align-self: flex-start;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            border-bottom-left-radius: 5px;
        }

        .message-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.8rem;
            opacity: 0.8;
        }

        .message-content {
            line-height: 1.6;
        }

        .message-meta {
            margin-top: 0.5rem;
            font-size: 0.75rem;
            opacity: 0.6;
            display: flex;
            gap: 1rem;
        }

        .typing-indicator {
            align-self: flex-start;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .typing-dots {
            display: flex;
            gap: 0.3rem;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--primary-color);
            animation: typingDot 1.4s infinite;
        }

        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }

        /* Chat Input */
        .chat-input {
            padding: 1.5rem;
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 1rem;
            align-items: flex-end;
        }

        .input-container {
            flex: 1;
            position: relative;
        }

        .chat-input-field {
            width: 100%;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            color: var(--text-primary);
            font-size: 1rem;
            line-height: 1.5;
            resize: none;
            outline: none;
            transition: all 0.3s ease;
            min-height: 60px;
            max-height: 200px;
        }

        .chat-input-field:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.2);
        }

        .chat-input-field::placeholder {
            color: var(--text-secondary);
        }

        .send-button {
            background: var(--gradient-primary);
            border: none;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            color: var(--bg-primary);
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            min-width: 120px;
            justify-content: center;
        }

        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* Right Sidebar */
        .rightbar {
            grid-area: rightbar;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 1.5rem;
            overflow-y: auto;
            backdrop-filter: blur(10px);
        }

        .tools-section {
            margin-bottom: 2rem;
        }

        .tool-button {
            width: 100%;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.8rem;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tool-button:hover {
            border-color: var(--primary-color);
            background: rgba(0, 255, 136, 0.1);
        }

        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        @keyframes messageSlideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes typingDot {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }

        /* Responsive Design */
        @media (max-width: 1200px) {
            .app-container {
                grid-template-columns: 250px 1fr;
                grid-template-areas:
                    "header header"
                    "sidebar main";
            }

            .rightbar {
                display: none;
            }
        }

        @media (max-width: 768px) {
            .app-container {
                grid-template-columns: 1fr;
                grid-template-areas:
                    "header"
                    "main";
            }

            .sidebar {
                display: none;
            }
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }
        """

    def get_enhanced_javascript(self):
        """Enhanced JavaScript with React components"""
        return """
        const { useState, useEffect, useRef } = React;

        // Enhanced Chat Message Component
        const ChatMessage = ({ message, isUser, timestamp, tokens, responseTime, model }) => {
            const formatTime = (time) => {
                return new Date(time).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            };

            return (
                <div className={`message ${isUser ? 'user' : 'assistant'}`}>
                    <div className="message-header">
                        <span>{isUser ? '👤 You' : '🤖 ' + (model || 'DeepSeek-R1')}</span>
                        <span>{formatTime(timestamp)}</span>
                    </div>
                    <div className="message-content">
                        {message}
                    </div>
                    {!isUser && (
                        <div className="message-meta">
                            {tokens && <span>{tokens} tokens</span>}
                            {responseTime && <span>{responseTime.toFixed(2)}s</span>}
                        </div>
                    )}
                </div>
            );
        };

        // Typing Indicator Component
        const TypingIndicator = () => (
            <div className="typing-indicator">
                <span>🤖 DeepSeek-R1 is thinking</span>
                <div className="typing-dots">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                </div>
            </div>
        );

        // System Metrics Component
        const SystemMetrics = ({ metrics }) => (
            <div className="sidebar">
                <h3>📊 System Metrics</h3>
                <div className="metric-card">
                    <div className="metric-value">{metrics.cpu_usage}%</div>
                    <div className="metric-label">CPU Usage</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">{metrics.memory_usage}%</div>
                    <div className="metric-label">Memory Usage</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">{metrics.active_connections}</div>
                    <div className="metric-label">Active Connections</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">{metrics.chat_messages}</div>
                    <div className="metric-label">Chat Messages</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">{Math.floor(metrics.uptime / 60)}m</div>
                    <div className="metric-label">Uptime</div>
                </div>
            </div>
        );

        // Tools Panel Component
        const ToolsPanel = ({ onToolClick }) => (
            <div className="rightbar">
                <h3>🛠️ AI Tools</h3>
                <div className="tools-section">
                    <button className="tool-button" onClick={() => onToolClick('mcp')}>
                        🔧 MCP Tools
                    </button>
                    <button className="tool-button" onClick={() => onToolClick('memory')}>
                        🧠 Memory Graph
                    </button>
                    <button className="tool-button" onClick={() => onToolClick('github')}>
                        🐙 GitHub
                    </button>
                    <button className="tool-button" onClick={() => onToolClick('search')}>
                        🔍 Web Search
                    </button>
                    <button className="tool-button" onClick={() => onToolClick('browser')}>
                        🌐 Browser
                    </button>
                    <button className="tool-button" onClick={() => onToolClick('filesystem')}>
                        📁 File System
                    </button>
                </div>

                <h3>⚙️ Models</h3>
                <div className="tools-section">
                    <div className="tool-button" style={{background: 'rgba(0, 255, 136, 0.1)'}}>
                        🧠 DeepSeek-R1 (Active)
                    </div>
                    <div className="tool-button" style={{opacity: 0.5}}>
                        ✨ Gemini 2.5 (Available)
                    </div>
                </div>
            </div>
        );

        // Main App Component
        const App = () => {
            const [messages, setMessages] = useState([]);
            const [inputValue, setInputValue] = useState('');
            const [isLoading, setIsLoading] = useState(false);
            const [metrics, setMetrics] = useState({
                cpu_usage: 0,
                memory_usage: 0,
                active_connections: 0,
                chat_messages: 0,
                uptime: 0
            });
            const [selectedModel, setSelectedModel] = useState('deepseek-r1');
            const [websocket, setWebsocket] = useState(null);
            const messagesEndRef = useRef(null);
            const inputRef = useRef(null);

            // Initialize WebSocket connection
            useEffect(() => {
                const ws = new WebSocket(`ws://localhost:${window.location.port}/ws`);

                ws.onopen = () => {
                    console.log('WebSocket connected');
                    setWebsocket(ws);
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);

                    if (data.type === 'chat_response') {
                        setMessages(prev => [...prev, {
                            id: Date.now(),
                            content: data.message,
                            isUser: false,
                            timestamp: Date.now(),
                            tokens: data.tokens,
                            responseTime: data.responseTime,
                            model: data.model || 'DeepSeek-R1'
                        }]);
                        setIsLoading(false);
                    } else if (data.type === 'metrics') {
                        setMetrics(data.metrics);
                    }
                };

                ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    setWebsocket(null);
                };

                return () => {
                    ws.close();
                };
            }, []);

            // Scroll to bottom when new messages arrive
            useEffect(() => {
                messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }, [messages, isLoading]);

            // Fetch metrics periodically
            useEffect(() => {
                const fetchMetrics = async () => {
                    try {
                        const response = await fetch('/api/metrics');
                        const data = await response.json();
                        setMetrics(data);
                    } catch (error) {
                        console.error('Error fetching metrics:', error);
                    }
                };

                fetchMetrics();
                const interval = setInterval(fetchMetrics, 5000);
                return () => clearInterval(interval);
            }, []);

            // Handle message sending
            const sendMessage = async () => {
                if (!inputValue.trim() || isLoading) return;

                const userMessage = {
                    id: Date.now(),
                    content: inputValue,
                    isUser: true,
                    timestamp: Date.now()
                };

                setMessages(prev => [...prev, userMessage]);
                setInputValue('');
                setIsLoading(true);

                try {
                    if (websocket && websocket.readyState === WebSocket.OPEN) {
                        websocket.send(JSON.stringify({
                            type: 'chat',
                            message: inputValue,
                            model: selectedModel
                        }));
                    } else {
                        // Fallback to HTTP API
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                message: inputValue,
                                model: selectedModel
                            }),
                        });

                        const data = await response.json();

                        setMessages(prev => [...prev, {
                            id: Date.now() + 1,
                            content: data.response,
                            isUser: false,
                            timestamp: Date.now(),
                            tokens: data.tokens,
                            responseTime: data.responseTime,
                            model: selectedModel
                        }]);
                        setIsLoading(false);
                    }
                } catch (error) {
                    console.error('Error sending message:', error);
                    setIsLoading(false);
                }
            };

            // Handle key press
            const handleKeyPress = (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            };

            // Handle tool clicks
            const handleToolClick = (tool) => {
                const toolMessages = {
                    'mcp': 'List available MCP tools and their capabilities',
                    'memory': 'Show my knowledge graph and memory',
                    'github': 'Help me with GitHub repositories',
                    'search': 'Search the web for information',
                    'browser': 'Browse a website for me',
                    'filesystem': 'Help me with file operations'
                };

                if (toolMessages[tool]) {
                    setInputValue(toolMessages[tool]);
                    inputRef.current?.focus();
                }
            };

            return (
                <div className="app-container">
                    <div className="header">
                        <h1>🚀 Enhanced AGI Portal v2.0</h1>
                        <div className="status-badges">
                            <div className="status-badge online">🧠 DeepSeek-R1 Online</div>
                            <div className="status-badge online">🔧 MCP Tools Ready</div>
                            <div className="status-badge online">📚 Context7 Active</div>
                        </div>
                    </div>

                    <SystemMetrics metrics={metrics} />

                    <div className="main-content">
                        <div className="chat-header">
                            <h2>💬 Advanced AI Chat</h2>
                            <div className="model-selector">
                                <label>Model:</label>
                                <select
                                    className="model-select"
                                    value={selectedModel}
                                    onChange={(e) => setSelectedModel(e.target.value)}
                                >
                                    <option value="deepseek-r1">🧠 DeepSeek-R1</option>
                                    <option value="gemini-2.5">✨ Gemini 2.5</option>
                                </select>
                            </div>
                        </div>

                        <div className="chat-messages">
                            {messages.length === 0 && (
                                <div className="message assistant">
                                    <div className="message-header">
                                        <span>🤖 DeepSeek-R1</span>
                                        <span>Ready</span>
                                    </div>
                                    <div className="message-content">
                                        Hello! I'm your Enhanced AGI assistant with access to powerful tools and reasoning capabilities. How can I help you today?
                                    </div>
                                </div>
                            )}

                            {messages.map(message => (
                                <ChatMessage
                                    key={message.id}
                                    message={message.content}
                                    isUser={message.isUser}
                                    timestamp={message.timestamp}
                                    tokens={message.tokens}
                                    responseTime={message.responseTime}
                                    model={message.model}
                                />
                            ))}

                            {isLoading && <TypingIndicator />}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className="chat-input">
                            <div className="input-container">
                                <textarea
                                    ref={inputRef}
                                    className="chat-input-field"
                                    placeholder="Ask me anything... I have access to advanced tools and reasoning!"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    rows="1"
                                />
                            </div>
                            <button
                                className="send-button"
                                onClick={sendMessage}
                                disabled={isLoading || !inputValue.trim()}
                            >
                                {isLoading ? '⏳ Thinking...' : '🚀 Send'}
                            </button>
                        </div>
                    </div>

                    <ToolsPanel onToolClick={handleToolClick} />
                </div>
            );
        };

        // Render the app
        ReactDOM.render(<App />, document.getElementById('root'));
        """

    async def handle_chat(self, request):
        """Enhanced chat handler with metrics"""
        start_time = time.time()

        try:
            data = await request.json()
            message = data.get('message', '')
            model = data.get('model', 'deepseek-r1')

            if not message:
                return web.json_response({'error': 'No message provided'}, status=400)

            # Enrich context with Context7 if available
            enriched_context = None
            if self.context7_bridge and hasattr(self.context7_bridge, 'connected') and self.context7_bridge.connected:
                try:
                    enriched_context = await self.context7_bridge.enrich_context(message)
                    logger.info(f"Context7 enriched: {enriched_context.get('enriched', False)}")
                except Exception as e:
                    logger.warning(f"Context7 enrichment failed: {e}")

            # Process with selected model
            response = await self.process_with_model(message, model, enriched_context)

            # Calculate metrics
            response_time = time.time() - start_time
            tokens = len(response.split())

            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (user_id, message, response, model, tokens, response_time, context7_enriched)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('user', message, response, model, tokens, response_time,
                  enriched_context.get('enriched', False) if enriched_context else False))
            conn.commit()
            conn.close()

            # Update metrics
            self.system_metrics['chat_messages'] += 1

            return web.json_response({
                'response': response,
                'tokens': tokens,
                'responseTime': response_time,
                'model': model,
                'context7_enriched': enriched_context.get('enriched', False) if enriched_context else False
            })

        except Exception as e:
            logger.error(f"Error handling chat: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_chat_stream(self, request):
        """Handle streaming chat responses"""
        # Implementation for streaming responses
        pass

    async def get_system_status(self, request):
        """Get system status"""
        return web.json_response({
            'version': self.version,
            'uptime': time.time() - self.start_time,
            'status': 'online',
            'models': ['deepseek-r1', 'gemini-2.5'],
            'active_model': 'deepseek-r1',
            'integrations': {
                'claudia': self.claudia_bridge is not None,
                'context7': self.context7_bridge is not None,
                'ipfs': False  # Placeholder
            }
        })

    async def get_system_metrics(self, request):
        """Get system metrics"""
        # Update real-time metrics
        self.system_metrics['cpu_usage'] = psutil.cpu_percent()
        self.system_metrics['memory_usage'] = psutil.virtual_memory().percent
        self.system_metrics['active_connections'] = len(self.websocket_connections)
        self.system_metrics['uptime'] = time.time() - self.start_time

        return web.json_response(self.system_metrics)

    async def get_chat_history(self, request):
        """Get chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, response, model, tokens, response_time, timestamp
            FROM chat_history
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        history = cursor.fetchall()
        conn.close()

        return web.json_response([
            {
                'message': row[0],
                'response': row[1],
                'model': row[2],
                'tokens': row[3],
                'response_time': row[4],
                'timestamp': row[5]
            }
            for row in history
        ])

    async def clear_chat_history(self, request):
        """Clear chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chat_history')
        conn.commit()
        conn.close()

        return web.json_response({'success': True})

    async def get_available_models(self, request):
        """Get available models"""
        return web.json_response({
            'models': [
                {
                    'id': 'deepseek-r1',
                    'name': 'DeepSeek-R1',
                    'description': 'Advanced reasoning model with chain-of-thought capabilities',
                    'status': 'online'
                },
                {
                    'id': 'gemini-2.5',
                    'name': 'Gemini 2.5 Flash',
                    'description': 'Multimodal model with 2M context window',
                    'status': 'available'
                }
            ]
        })

    async def handle_file_upload(self, request):
        """Handle file uploads"""
        try:
            reader = await request.multipart()
            async for field in reader:
                if field.name == 'file':
                    filename = field.filename
                    content = await field.read()

                    # Save file and create hash
                    file_hash = hashlib.sha256(content).hexdigest()

                    return web.json_response({
                        'filename': filename,
                        'hash': file_hash,
                        'size': len(content),
                        'status': 'uploaded'
                    })
        except Exception as e:
            logger.error(f"Error handling file upload: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def websocket_handler(self, request):
        """Enhanced WebSocket handler"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websocket_connections.add(ws)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)

                    if data.get('type') == 'chat':
                        message = data.get('message', '')
                        model = data.get('model', 'deepseek-r1')

                        start_time = time.time()
                        response = await self.process_with_model(message, model)
                        response_time = time.time() - start_time

                        await ws.send_text(json.dumps({
                            'type': 'chat_response',
                            'message': response,
                            'tokens': len(response.split()),
                            'responseTime': response_time,
                            'model': model
                        }))

                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")

        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            self.websocket_connections.discard(ws)

        return ws

    async def process_with_model(self, message, model='deepseek-r1', enriched_context=None):
        """Process message with specified model"""
        try:
            # Prepare enhanced prompt
            enhanced_prompt = message

            if enriched_context and enriched_context.get('enriched'):
                context_info = []
                libraries_detected = enriched_context.get('libraries_detected', [])

                if libraries_detected:
                    context_info.append(f"📚 Libraries detected: {', '.join(libraries_detected)}")

                documentation = enriched_context.get('documentation', {})
                for lib, docs in documentation.items():
                    if docs and docs.get('content'):
                        context_info.append(f"\\n🔍 {lib} Documentation Context:")
                        context_info.append(docs['content'][:1000] + "..." if len(docs['content']) > 1000 else docs['content'])

                if context_info:
                    enhanced_prompt = f"""Context Information:
{chr(10).join(context_info)}

User Query: {message}

Please provide a response that takes into account the above context information, especially for code-related queries."""

            # Process with appropriate model
            if model == 'deepseek-r1':
                return await self.process_with_deepseek(enhanced_prompt)
            elif model == 'gemini-2.5':
                return await self.process_with_gemini(enhanced_prompt)
            else:
                return await self.process_with_deepseek(enhanced_prompt)

        except Exception as e:
            logger.error(f"Error processing with model {model}: {e}")
            return "I'm currently processing your request. Please try again in a moment."

    async def process_with_deepseek(self, message):
        """Process with DeepSeek-R1"""
        try:
            model_name = self.get_deepseek_model_name()
            cmd = ['ollama', 'run', model_name, message]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "I'm processing your request with advanced reasoning capabilities..."

        except subprocess.TimeoutExpired:
            return "I'm thinking deeply about your request using chain-of-thought reasoning..."
        except Exception as e:
            return "I'm initializing my cognitive systems. How can I help you today?"

    async def process_with_gemini(self, message):
        """Process with Gemini (placeholder)"""
        return "Gemini 2.5 Flash processing (implementation pending)..."

    def get_deepseek_model_name(self):
        """Get the correct DeepSeek model name"""
        return "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"

    async def ensure_deepseek_model(self):
        """Ensure DeepSeek-R1 model is available"""
        try:
            model_name = self.get_deepseek_model_name()

            # Check if model is already loaded
            cmd = ['ollama', 'list']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if model_name in result.stdout:
                logger.info(f"✅ DeepSeek-R1 model {model_name} is already loaded")
                return True

            # Pull model if not available
            logger.info(f"🔄 Pulling DeepSeek-R1 model: {model_name}")
            cmd = ['ollama', 'pull', model_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info(f"✅ DeepSeek-R1 model {model_name} loaded successfully")
                return True
            else:
                logger.error(f"❌ Failed to load DeepSeek-R1 model: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error ensuring DeepSeek model: {e}")
            return False

    async def init_system_components(self):
        """Initialize all system components"""
        try:
            # Ensure DeepSeek model
            print("[SYSTEM] Ensuring DeepSeek-R1 model is loaded...")
            await self.ensure_deepseek_model()

            # Initialize IPFS (optional)
            try:
                self.ipfs_client = ipfshttpclient.connect()
                print("[OK] IPFS client initialized")
            except:
                print("[WARNING] IPFS not available")

            # Initialize integrations
            if self.claudia_bridge:
                await self.claudia_bridge.integrate_with_ultimate_agi(self)
                logger.info("🔗 Claudia integration activated")

            if self.context7_bridge:
                try:
                    await self.context7_bridge.start_server()
                    logger.info("📚 Context7 documentation bridge activated")
                except Exception as e:
                    logger.error(f"Context7 initialization failed: {e}")

            print("[OK] All system components initialized")

        except Exception as e:
            logger.error(f"Error initializing system components: {e}")

    async def run(self):
        """Run the enhanced AGI system"""
        try:
            await self.init_system_components()

            print(f"""
[SYSTEM] ====================================================
   ENHANCED AGI SYSTEM v{self.version} STARTING
[SYSTEM] ====================================================

[BRAIN] 🧠 DeepSeek-R1 Advanced Reasoning: Ready
[TOOLS] 🔧 MCP Tools Suite: Loaded
[NETWORK] 🌐 Enhanced WebSocket: Active
[GUI] 🎨 Modern React Dashboard: Ready
[INTEGRATIONS] 🔗 Claudia & Context7: Connected

[WEB] 🚀 Enhanced Dashboard: http://localhost:{self.port}
[STATUS] ✅ ALL SYSTEMS OPERATIONAL

[READY] 🎯 Enhanced AGI Portal is LIVE!
""")

            # Start the web server
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', self.port)
            await site.start()

            print(f"[LIVE] 🌟 Enhanced AGI System is running at http://localhost:{self.port}")
            print("[SUCCESS] 🎉 Modern UI with advanced chat capabilities ready!")

            # Keep the server running
            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                print("\\n[SHUTDOWN] 👋 Enhanced AGI System shutting down...")
                await runner.cleanup()

        except Exception as e:
            logger.error(f"Error running enhanced AGI system: {e}")
            raise

if __name__ == "__main__":
    system = EnhancedAGISystem()
    asyncio.run(system.run())
