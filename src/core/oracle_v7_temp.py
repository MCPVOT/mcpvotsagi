
import asyncio
from aiohttp import web
import json
import psutil
import time
from datetime import datetime

class MinimalOracleAGI:
    def __init__(self):
        self.start_time = time.time()
        self.services = {
            "oracle_core": "running",
            "web_interface": "running"
        }
        
    async def handle_index(self, request):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI V7</title>
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff; 
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 40px 0;
        }
        h1 { 
            font-size: 3em; 
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .status-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        .metric {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        .label {
            font-size: 0.9em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .services {
            margin-top: 20px;
        }
        .service {
            display: inline-block;
            padding: 5px 15px;
            margin: 5px;
            background: #4CAF50;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .message {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Oracle AGI V7</h1>
            <p>Intelligent System Interface</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <div class="label">CPU Usage</div>
                <div class="metric" id="cpu">--</div>
            </div>
            <div class="status-card">
                <div class="label">Memory Usage</div>
                <div class="metric" id="memory">--</div>
            </div>
            <div class="status-card">
                <div class="label">Uptime</div>
                <div class="metric" id="uptime">--</div>
            </div>
            <div class="status-card">
                <div class="label">Active Services</div>
                <div class="services" id="services">
                    <span class="service">Oracle Core</span>
                    <span class="service">Web Interface</span>
                </div>
            </div>
        </div>
        
        <div class="message">
            <h2>System Ready</h2>
            <p>Oracle AGI V7 is running in minimal mode. For full functionality, ensure all MCP servers are started.</p>
            <p>API Endpoint: <code>http://localhost:8888/api/status</code></p>
        </div>
    </div>
    
    <script>
        async function updateStatus() {
            try {
                const resp = await fetch('/api/status');
                const data = await resp.json();
                
                document.getElementById('cpu').textContent = data.metrics.cpu.toFixed(1) + '%';
                document.getElementById('memory').textContent = data.metrics.memory.toFixed(1) + '%';
                document.getElementById('uptime').textContent = data.uptime;
                
                // Update services
                const servicesHtml = Object.entries(data.services)
                    .map(([name, status]) => 
                        `<span class="service">${name.replace('_', ' ').toUpperCase()}</span>`
                    ).join('');
                document.getElementById('services').innerHTML = servicesHtml;
                
            } catch(e) {
                console.error('Update failed:', e);
            }
        }
        
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_status(self, request):
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        return web.json_response({
            'status': 'running',
            'version': '7.0.0-minimal',
            'uptime': f'{hours}h {minutes}m {seconds}s',
            'metrics': {
                'cpu': psutil.cpu_percent(interval=1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent
            },
            'services': self.services,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_query(self, request):
        data = await request.json()
        query = data.get('query', '')
        
        # Simple response for now
        response = f"Oracle AGI V7 received query: '{query}'. Full AI processing requires MCP servers to be running."
        
        return web.json_response({
            'response': response,
            'status': 'minimal_mode',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def start(self):
        app = web.Application()
        app.router.add_get('/', self.handle_index)
        app.router.add_get('/api/status', self.handle_status)
        app.router.add_post('/api/query', self.handle_query)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8888)
        await site.start()
        
        print("\n" + "="*60)
        print("Oracle AGI V7 Started Successfully!")
        print("="*60)
        print(f"Web Interface: http://localhost:8888")
        print(f"API Status: http://localhost:8888/api/status")
        print("\nPress Ctrl+C to stop")
        print("="*60)
        
        # Keep running
        await asyncio.Event().wait()

# Run the server
oracle = MinimalOracleAGI()
asyncio.run(oracle.start())
    