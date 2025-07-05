#!/usr/bin/env python3
"""
ULTIMATE DASHBOARD V2 - FULLY FUNCTIONAL UPGRADE
================================================
Real-time updates, working integrations, beautiful UI
"""

def generate_ultimate_dashboard_v2() -> str:
    """Generate the upgraded, fully functional dashboard"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 MCPVotsAGI Ultimate Dashboard V2</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #00ff41;
            --secondary: #0099ff;
            --danger: #ff4444;
            --warning: #ffaa00;
            --bg-dark: #0a0a0a;
            --bg-panel: rgba(26, 26, 26, 0.95);
            --text: #ffffff;
            --text-dim: #cccccc;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            overflow: hidden;
            height: 100vh;
        }

        /* Animated background */
        .matrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.1;
        }

        .matrix-bg canvas {
            width: 100%;
            height: 100%;
        }

        /* Header */
        .header {
            background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 100%);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid var(--primary);
            backdrop-filter: blur(10px);
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo h1 {
            font-size: 1.8rem;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        .status-bar {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--primary);
            box-shadow: 0 0 10px currentColor;
        }

        .status-indicator.warning {
            background: var(--warning);
        }

        .status-indicator.error {
            background: var(--danger);
        }

        /* Main Layout */
        .main-container {
            display: grid;
            grid-template-columns: 250px 1fr 350px;
            height: calc(100vh - 70px);
            gap: 1rem;
            padding: 1rem;
        }

        /* Sidebar */
        .sidebar {
            background: var(--bg-panel);
            border-radius: 12px;
            padding: 1.5rem;
            overflow-y: auto;
            border: 1px solid rgba(0, 255, 65, 0.2);
        }

        .sidebar h2 {
            font-size: 1.2rem;
            margin-bottom: 1.5rem;
            color: var(--primary);
        }

        .menu-item {
            padding: 0.8rem 1rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .menu-item:hover {
            background: rgba(0, 255, 65, 0.1);
            transform: translateX(5px);
        }

        .menu-item.active {
            background: rgba(0, 255, 65, 0.2);
            border-left: 3px solid var(--primary);
        }

        /* Central Panel */
        .central-panel {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .chat-container {
            flex: 1;
            background: var(--bg-panel);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            border: 1px solid rgba(0, 255, 65, 0.2);
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 12px;
            max-width: 80%;
            animation: messageSlide 0.3s ease-out;
        }

        @keyframes messageSlide {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            background: linear-gradient(135deg, rgba(0, 153, 255, 0.2), rgba(0, 153, 255, 0.1));
            margin-left: auto;
            border: 1px solid rgba(0, 153, 255, 0.3);
        }

        .message.assistant {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.2), rgba(0, 255, 65, 0.1));
            border: 1px solid rgba(0, 255, 65, 0.3);
        }

        .message-header {
            font-size: 0.8rem;
            color: var(--text-dim);
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
        }

        .chat-input-container {
            display: flex;
            gap: 1rem;
        }

        .chat-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border: 2px solid rgba(0, 255, 65, 0.3);
            border-radius: 12px;
            padding: 1rem;
            color: var(--text);
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
        }

        .send-button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border: none;
            border-radius: 12px;
            padding: 0 2rem;
            color: #000;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 255, 65, 0.4);
        }

        /* Metrics Panel */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }

        .metric-card {
            background: var(--bg-panel);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(0, 255, 65, 0.2);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 255, 65, 0.2);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            margin: 0.5rem 0;
        }

        .metric-label {
            font-size: 0.9rem;
            color: var(--text-dim);
        }

        .metric-change {
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }

        .metric-change.positive {
            color: var(--primary);
        }

        .metric-change.negative {
            color: var(--danger);
        }

        /* Right Panel */
        .right-panel {
            background: var(--bg-panel);
            border-radius: 12px;
            padding: 1.5rem;
            overflow-y: auto;
            border: 1px solid rgba(0, 255, 65, 0.2);
        }

        .agent-list {
            margin-top: 1rem;
        }

        .agent-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 3px solid var(--primary);
            transition: all 0.3s ease;
        }

        .agent-card:hover {
            transform: translateX(5px);
            box-shadow: 0 3px 15px rgba(0, 255, 65, 0.2);
        }

        .agent-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.5rem;
        }

        .progress-bar {
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            margin-top: 0.5rem;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 2px;
            transition: width 0.3s ease;
        }

        /* Trading Panel */
        .trading-panel {
            background: var(--bg-panel);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(0, 255, 65, 0.2);
        }

        .position-list {
            margin-top: 1rem;
        }

        .position-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .position-info {
            flex: 1;
        }

        .position-symbol {
            font-weight: 600;
            margin-bottom: 0.3rem;
        }

        .position-details {
            font-size: 0.8rem;
            color: var(--text-dim);
        }

        .position-pnl {
            text-align: right;
        }

        .pnl-value {
            font-size: 1.2rem;
            font-weight: 600;
        }

        .pnl-value.positive {
            color: var(--primary);
        }

        .pnl-value.negative {
            color: var(--danger);
        }

        /* Notifications */
        .notification {
            position: fixed;
            top: 90px;
            right: 20px;
            background: var(--bg-panel);
            border: 1px solid var(--primary);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.5);
            animation: slideIn 0.3s ease-out;
            z-index: 1000;
        }

        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        /* Loading animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(0, 255, 65, 0.3);
            border-radius: 50%;
            border-top-color: var(--primary);
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Responsive */
        @media (max-width: 1200px) {
            .main-container {
                grid-template-columns: 200px 1fr 300px;
            }
        }

        @media (max-width: 900px) {
            .main-container {
                grid-template-columns: 1fr;
            }
            .sidebar, .right-panel {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="matrix-bg">
        <canvas id="matrix-canvas"></canvas>
    </div>

    <header class="header">
        <div class="logo">
            <h1>MCPVotsAGI</h1>
            <span style="color: var(--text-dim)">Ultimate Dashboard V2</span>
        </div>
        <div class="status-bar">
            <div class="status-item">
                <span class="status-indicator" id="ollama-status"></span>
                <span>DeepSeek-R1</span>
            </div>
            <div class="status-item">
                <span class="status-indicator" id="mcp-status"></span>
                <span>MCP Tools</span>
            </div>
            <div class="status-item">
                <span class="status-indicator" id="trading-status"></span>
                <span>Trading</span>
            </div>
            <div class="status-item">
                <span class="status-indicator" id="memory-status"></span>
                <span>Memory</span>
            </div>
        </div>
    </header>

    <div class="main-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <h2>Navigation</h2>
            <div class="menu-item active" onclick="switchView('chat')">
                <span>💬</span> AGI Chat
            </div>
            <div class="menu-item" onclick="switchView('trading')">
                <span>💹</span> Trading
            </div>
            <div class="menu-item" onclick="switchView('agents')">
                <span>🤖</span> Agents
            </div>
            <div class="menu-item" onclick="switchView('memory')">
                <span>🧠</span> Memory
            </div>
            <div class="menu-item" onclick="switchView('mcp')">
                <span>🔧</span> MCP Tools
            </div>
            <div class="menu-item" onclick="switchView('metrics')">
                <span>📊</span> Metrics
            </div>
            <div class="menu-item" onclick="switchView('settings')">
                <span>⚙️</span> Settings
            </div>
        </aside>

        <!-- Central Panel -->
        <main class="central-panel">
            <!-- Chat View -->
            <div id="chat-view" class="chat-container">
                <div class="chat-messages" id="chat-messages">
                    <div class="message assistant">
                        <div class="message-header">
                            <span>🚀 Ultimate AGI</span>
                            <span>DeepSeek-R1</span>
                        </div>
                        <div>Welcome to MCPVotsAGI Ultimate Dashboard V2! I have access to all MCP tools, trading capabilities, memory systems, and agent coordination. How can I assist you today?</div>
                    </div>
                </div>
                <div class="chat-input-container">
                    <input type="text" class="chat-input" id="chat-input" 
                           placeholder="Ask anything... (Use Ctrl+Enter for multiline)" 
                           onkeypress="handleChatInput(event)">
                    <button class="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>

            <!-- Trading View (hidden by default) -->
            <div id="trading-view" class="trading-panel" style="display: none;">
                <h2>Trading Dashboard</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Portfolio Value</div>
                        <div class="metric-value" id="portfolio-value">$0.00</div>
                        <div class="metric-change positive" id="portfolio-change">+0.00%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Today's P&L</div>
                        <div class="metric-value" id="daily-pnl">$0.00</div>
                        <div class="metric-change" id="daily-pnl-change">0.00%</div>
                    </div>
                </div>
                <h3 style="margin-top: 2rem;">Active Positions</h3>
                <div class="position-list" id="position-list">
                    <!-- Positions will be populated here -->
                </div>
            </div>

            <!-- Metrics Overview -->
            <div class="metrics-grid" style="margin-top: 1rem;">
                <div class="metric-card">
                    <div class="metric-label">System Uptime</div>
                    <div class="metric-value" id="uptime">0s</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Active Agents</div>
                    <div class="metric-value" id="active-agents">0</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Memory Usage</div>
                    <div class="metric-value" id="memory-usage">0%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">MCP Calls</div>
                    <div class="metric-value" id="mcp-calls">0</div>
                </div>
            </div>
        </main>

        <!-- Right Panel -->
        <aside class="right-panel">
            <h2>Active Agents</h2>
            <div class="agent-list" id="agent-list">
                <div class="agent-card">
                    <h3>🧠 DeepSeek-R1</h3>
                    <p style="font-size: 0.8rem; color: var(--text-dim);">Primary reasoning engine</p>
                    <div class="agent-status">
                        <span style="color: var(--primary);">Active</span>
                        <span>CPU: 12%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 12%;"></div>
                    </div>
                </div>
                <div class="agent-card">
                    <h3>💹 Trading Agent</h3>
                    <p style="font-size: 0.8rem; color: var(--text-dim);">Market analysis & execution</p>
                    <div class="agent-status">
                        <span style="color: var(--primary);">Active</span>
                        <span>Tasks: 3</span>
                    </div>
                </div>
                <div class="agent-card">
                    <h3>🔗 MCP Coordinator</h3>
                    <p style="font-size: 0.8rem; color: var(--text-dim);">Tool orchestration</p>
                    <div class="agent-status">
                        <span style="color: var(--primary);">Active</span>
                        <span>Tools: 5</span>
                    </div>
                </div>
            </div>

            <h2 style="margin-top: 2rem;">Recent Activity</h2>
            <div id="activity-feed" style="margin-top: 1rem;">
                <!-- Activity items will be populated here -->
            </div>
        </aside>
    </div>

    <script>
        // WebSocket connection
        let ws = null;
        let reconnectAttempts = 0;

        // Initialize WebSocket
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onopen = () => {
                console.log('WebSocket connected');
                reconnectAttempts = 0;
                updateConnectionStatus(true);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                updateConnectionStatus(false);
                setTimeout(reconnectWebSocket, Math.min(1000 * Math.pow(2, reconnectAttempts), 30000));
                reconnectAttempts++;
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }

        function reconnectWebSocket() {
            if (ws.readyState === WebSocket.CLOSED) {
                initWebSocket();
            }
        }

        function handleWebSocketMessage(data) {
            switch(data.type) {
                case 'chat_response':
                    addMessage(data.message, 'assistant', data.model);
                    break;
                case 'status_update':
                    updateSystemStatus(data);
                    break;
                case 'trading_update':
                    updateTradingData(data);
                    break;
                case 'agent_update':
                    updateAgentStatus(data);
                    break;
                case 'notification':
                    showNotification(data.message, data.level);
                    break;
            }
        }

        // Chat functionality
        function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage(message, 'user');
            
            // Send via WebSocket
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'chat',
                    message: message
                }));
            } else {
                // Fallback to HTTP
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.response, 'assistant');
                })
                .catch(error => {
                    addMessage('Error: ' + error.message, 'assistant');
                });
            }
            
            input.value = '';
        }

        function handleChatInput(event) {
            if (event.key === 'Enter' && !event.ctrlKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        function addMessage(message, sender, model = 'DeepSeek-R1') {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const header = document.createElement('div');
            header.className = 'message-header';
            header.innerHTML = `
                <span>${sender === 'user' ? '👤 You' : '🚀 Ultimate AGI'}</span>
                <span>${sender === 'assistant' ? model : new Date().toLocaleTimeString()}</span>
            `;
            
            const content = document.createElement('div');
            content.textContent = message;
            
            messageDiv.appendChild(header);
            messageDiv.appendChild(content);
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // System status updates
        function updateSystemStatus(status) {
            // Update status indicators
            updateIndicator('ollama-status', status.deepseek_status);
            updateIndicator('mcp-status', status.mcp_status);
            updateIndicator('trading-status', status.trading_status);
            updateIndicator('memory-status', status.memory_status);
            
            // Update metrics
            document.getElementById('uptime').textContent = status.uptime || '0s';
            document.getElementById('memory-usage').textContent = status.memory || '0%';
            document.getElementById('active-agents').textContent = status.active_agents || '0';
            document.getElementById('mcp-calls').textContent = status.mcp_calls || '0';
        }

        function updateIndicator(id, status) {
            const indicator = document.getElementById(id);
            if (indicator) {
                indicator.className = 'status-indicator';
                if (status === 'active' || status === 'online') {
                    // Keep default (green)
                } else if (status === 'warning') {
                    indicator.classList.add('warning');
                } else {
                    indicator.classList.add('error');
                }
            }
        }

        // Trading updates
        function updateTradingData(data) {
            if (data.portfolio_value) {
                document.getElementById('portfolio-value').textContent = `$${data.portfolio_value.toLocaleString()}`;
            }
            if (data.daily_pnl !== undefined) {
                const pnlElement = document.getElementById('daily-pnl');
                const changeElement = document.getElementById('daily-pnl-change');
                pnlElement.textContent = `$${data.daily_pnl.toLocaleString()}`;
                changeElement.textContent = `${data.daily_pnl_percent}%`;
                changeElement.className = `metric-change ${data.daily_pnl >= 0 ? 'positive' : 'negative'}`;
            }
            
            // Update positions
            if (data.positions) {
                updatePositions(data.positions);
            }
        }

        function updatePositions(positions) {
            const container = document.getElementById('position-list');
            container.innerHTML = '';
            
            Object.entries(positions).forEach(([symbol, position]) => {
                const card = document.createElement('div');
                card.className = 'position-card';
                card.innerHTML = `
                    <div class="position-info">
                        <div class="position-symbol">${symbol}</div>
                        <div class="position-details">
                            ${position.amount} @ $${position.average_price.toFixed(2)}
                        </div>
                    </div>
                    <div class="position-pnl">
                        <div class="pnl-value ${position.pnl_percentage >= 0 ? 'positive' : 'negative'}">
                            $${position.total_pnl.toFixed(2)}
                        </div>
                        <div class="position-details">
                            ${position.pnl_percentage >= 0 ? '+' : ''}${position.pnl_percentage.toFixed(2)}%
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        // View switching
        function switchView(view) {
            // Update menu
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.closest('.menu-item').classList.add('active');
            
            // Hide all views
            document.getElementById('chat-view').style.display = 'none';
            document.getElementById('trading-view').style.display = 'none';
            
            // Show selected view
            switch(view) {
                case 'chat':
                    document.getElementById('chat-view').style.display = 'flex';
                    break;
                case 'trading':
                    document.getElementById('trading-view').style.display = 'block';
                    loadTradingData();
                    break;
                // Add more views as needed
            }
        }

        // Load trading data
        function loadTradingData() {
            fetch('/api/trading')
                .then(response => response.json())
                .then(data => updateTradingData(data))
                .catch(error => console.error('Error loading trading data:', error));
        }

        // Notifications
        function showNotification(message, level = 'info') {
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }

        // Matrix background effect
        function initMatrixEffect() {
            const canvas = document.getElementById('matrix-canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            const matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}";
            const matrixArray = matrix.split("");
            
            const fontSize = 10;
            const columns = canvas.width / fontSize;
            
            const drops = [];
            for(let x = 0; x < columns; x++) {
                drops[x] = 1;
            }
            
            function draw() {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = '#00ff41';
                ctx.font = fontSize + 'px monospace';
                
                for(let i = 0; i < drops.length; i++) {
                    const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    
                    if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }
            
            setInterval(draw, 35);
        }

        // Auto-refresh system status
        function startAutoRefresh() {
            setInterval(() => {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => updateSystemStatus(data))
                    .catch(error => console.error('Status update error:', error));
            }, 5000);
        }

        // Initialize on load
        window.onload = () => {
            initWebSocket();
            initMatrixEffect();
            startAutoRefresh();
            
            // Load initial data
            updateSystemStatus({});
            
            // Focus chat input
            document.getElementById('chat-input').focus();
        };

        // Handle window resize
        window.addEventListener('resize', () => {
            const canvas = document.getElementById('matrix-canvas');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    </script>
</body>
</html>
"""