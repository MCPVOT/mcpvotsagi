#!/usr/bin/env python3
"""
Oracle AGI Minimal Dashboard
===========================
A minimal dashboard that works without external dependencies
"""

import http.server
import socketserver
import json
import socket
import threading
import time
from datetime import datetime

PORT = 3010

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handle dashboard requests"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_dashboard()
        elif self.path == '/api/status':
            self.send_status()
        else:
            super().do_GET()
    
    def send_dashboard(self):
        """Send the main dashboard HTML"""
        html = '''<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI Dashboard - Minimal</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #00d4ff;
            text-align: center;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .service-card {
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 20px;
        }
        .service-name {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .status-online {
            color: #00ff88;
        }
        .status-offline {
            color: #ff3838;
        }
        .info {
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }
        button {
            background: #00d4ff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
        }
        button:hover {
            background: #0099ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 Oracle AGI Dashboard</h1>
        <p style="text-align: center;">Minimal Version - Running on Port 3010</p>
        
        <div class="info">
            <h2>System Status</h2>
            <p>Dashboard Time: <span id="time"></span></p>
            <p>Services Status: <span id="services-status">Checking...</span></p>
            <button onclick="checkStatus()">Refresh Status</button>
        </div>
        
        <div class="status-grid" id="status-grid">
            <!-- Services will be populated here -->
        </div>
        
        <div class="info">
            <h2>Quick Actions</h2>
            <p>To start the full ecosystem, run:</p>
            <pre style="background: #333; padding: 10px; border-radius: 5px;">
# From Windows Command Prompt:
cd C:\\Workspace\\MCPVotsAGI
START_ECOSYSTEM.bat

# Or manually start services:
python ecosystem_manager.py start</pre>
            
            <h3>Available Services</h3>
            <ul>
                <li>Oracle AGI Core - Port 8888</li>
                <li>Memory MCP - Port 3002</li>
                <li>GitHub MCP - Port 3001</li>
                <li>Trilogy AGI - Port 8000</li>
                <li>Ollama - Port 11434</li>
                <li>n8n Workflows - Port 5678</li>
            </ul>
        </div>
    </div>
    
    <script>
        function updateTime() {
            document.getElementById('time').textContent = new Date().toLocaleString();
        }
        
        function checkStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('services-status').textContent = 
                        data.online_count + '/' + data.total_services + ' services online';
                    
                    // Update service grid
                    const grid = document.getElementById('status-grid');
                    grid.innerHTML = '';
                    
                    for (const [name, info] of Object.entries(data.services)) {
                        const card = document.createElement('div');
                        card.className = 'service-card';
                        card.innerHTML = `
                            <div class="service-name">${name}</div>
                            <div>Port: ${info.port}</div>
                            <div class="${info.status === 'online' ? 'status-online' : 'status-offline'}">
                                Status: ${info.status.toUpperCase()}
                            </div>
                        `;
                        grid.appendChild(card);
                    }
                })
                .catch(error => {
                    document.getElementById('services-status').textContent = 'Error checking status';
                });
        }
        
        // Update time every second
        setInterval(updateTime, 1000);
        updateTime();
        
        // Check status on load
        checkStatus();
        
        // Auto-refresh every 10 seconds
        setInterval(checkStatus, 10000);
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_status(self):
        """Send service status"""
        services = {
            "Oracle AGI Core": {"port": 8888, "status": "offline"},
            "Memory MCP": {"port": 3002, "status": "offline"},
            "GitHub MCP": {"port": 3001, "status": "offline"},
            "Trilogy AGI": {"port": 8000, "status": "offline"},
            "Ollama": {"port": 11434, "status": "offline"},
            "n8n": {"port": 5678, "status": "offline"}
        }
        
        # Check which services are actually running
        online_count = 0
        for name, info in services.items():
            if self.is_port_open(info["port"]):
                info["status"] = "online"
                online_count += 1
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": services,
            "online_count": online_count,
            "total_services": len(services)
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def is_port_open(self, port):
        """Check if a port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0

def main():
    print("="*60)
    print("Oracle AGI Minimal Dashboard")
    print("="*60)
    print(f"\nStarting dashboard on port {PORT}...")
    
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            print(f"[OK] Dashboard running at http://localhost:{PORT}")
            print("\nPress Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
    except Exception as e:
        print(f"[ERROR] Error starting dashboard: {e}")

if __name__ == "__main__":
    main()