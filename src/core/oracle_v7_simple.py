#!/usr/bin/env python3
"""
Oracle AGI V7 - Simple Working Version
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Try to import required modules
try:
    from aiohttp import web
    import psutil
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("Missing dependencies. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "psutil"])
    
    # Try again
    try:
        from aiohttp import web
        import psutil
        HAS_DEPS = True
    except:
        print("Failed to install dependencies. Running in basic mode.")

if HAS_DEPS:
    class OracleAGIV7Simple:
        def __init__(self):
            self.start_time = datetime.utcnow()
            
        async def handle_index(self, request):
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI V7</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            min-width: 600px;
        }
        h1 {
            font-size: 3.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 40px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 40px 0;
        }
        .metric {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #4CAF50;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.9em;
            text-transform: uppercase;
            opacity: 0.8;
        }
        .status {
            display: inline-block;
            padding: 8px 20px;
            background: #4CAF50;
            border-radius: 20px;
            margin: 20px 0;
            font-weight: bold;
        }
        .endpoints {
            margin-top: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            font-family: monospace;
            font-size: 0.9em;
        }
        .endpoint {
            margin: 5px 0;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Oracle AGI V7</h1>
        <p class="subtitle">Advanced Intelligent System</p>
        
        <div class="status">SYSTEM ONLINE</div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">CPU Usage</div>
                <div class="metric-value" id="cpu">--</div>
            </div>
            <div class="metric">
                <div class="metric-label">Memory</div>
                <div class="metric-value" id="memory">--</div>
            </div>
            <div class="metric">
                <div class="metric-label">Uptime</div>
                <div class="metric-value" id="uptime">--</div>
            </div>
        </div>
        
        <div class="endpoints">
            <div class="endpoint">Dashboard: http://localhost:8888</div>
            <div class="endpoint">API Status: http://localhost:8888/api/status</div>
            <div class="endpoint">WebSocket: ws://localhost:8888/ws</div>
        </div>
    </div>
    
    <script>
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else if (minutes > 0) {
                return `${minutes}m ${secs}s`;
            } else {
                return `${secs}s`;
            }
        }
        
        async function updateMetrics() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                document.getElementById('cpu').textContent = data.cpu.toFixed(1) + '%';
                document.getElementById('memory').textContent = data.memory.toFixed(1) + '%';
                document.getElementById('uptime').textContent = formatUptime(data.uptime_seconds);
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            }
        }
        
        // Update immediately and then every 2 seconds
        updateMetrics();
        setInterval(updateMetrics, 2000);
    </script>
</body>
</html>
            """
            return web.Response(text=html, content_type='text/html')
        
        async def handle_status(self, request):
            uptime_delta = datetime.utcnow() - self.start_time
            uptime_seconds = uptime_delta.total_seconds()
            
            return web.json_response({
                'status': 'running',
                'version': '7.0.0-simple',
                'cpu': psutil.cpu_percent(interval=0.1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
                'uptime_seconds': int(uptime_seconds),
                'start_time': self.start_time.isoformat(),
                'current_time': datetime.utcnow().isoformat(),
                'services': {
                    'oracle_core': 'running',
                    'web_interface': 'running',
                    'api': 'running'
                }
            })
        
        async def handle_ws(self, request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            
            try:
                # Send initial message
                await ws.send_json({
                    'type': 'connected',
                    'message': 'Connected to Oracle AGI V7',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Keep connection alive
                async for msg in ws:
                    if msg.type == web.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        # Echo back with response
                        await ws.send_json({
                            'type': 'response',
                            'original': data,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    elif msg.type == web.WSMsgType.ERROR:
                        print(f'WebSocket error: {ws.exception()}')
            finally:
                return ws
        
        async def start(self):
            app = web.Application()
            app.router.add_get('/', self.handle_index)
            app.router.add_get('/api/status', self.handle_status)
            app.router.add_get('/ws', self.handle_ws)
            
            # Add CORS headers
            async def cors_middleware(app, handler):
                async def middleware_handler(request):
                    response = await handler(request)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response
                return middleware_handler
            
            app.middlewares.append(cors_middleware)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8888)
            await site.start()
            
            print("\n" + "="*70)
            print("                    ORACLE AGI V7 - RUNNING")
            print("="*70)
            print(f"\nDashboard:  http://localhost:8888")
            print(f"API Status: http://localhost:8888/api/status")
            print(f"WebSocket:  ws://localhost:8888/ws")
            print(f"\nStarted at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("\nPress Ctrl+C to stop")
            print("="*70 + "\n")
            
            # Keep running
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                print("\nShutting down Oracle AGI V7...")
    
    # Run the server
    oracle = OracleAGIV7Simple()
    asyncio.run(oracle.start())

else:
    # Fallback without dependencies
    import http.server
    import socketserver
    
    class BasicHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = b"""
                <html>
                <head><title>Oracle AGI V7</title></head>
                <body style="font-family:Arial;text-align:center;padding:50px;">
                    <h1>Oracle AGI V7 - Basic Mode</h1>
                    <p>Running without dependencies</p>
                    <p>Install aiohttp and psutil for full functionality</p>
                </body>
                </html>
                """
                self.wfile.write(html)
            else:
                super().do_GET()
    
    print("\nOracle AGI V7 - Basic Mode (no dependencies)")
    print("Running on http://localhost:8888")
    with socketserver.TCPServer(("", 8888), BasicHandler) as httpd:
        httpd.serve_forever()