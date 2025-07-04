import subprocess
import sys
import os

# Change to the correct directory
os.chdir(r"C:\Workspace\MCPVotsAGI")

# Use venv Python
venv_python = r"C:\Workspace\.venv\Scripts\python.exe"

# Run Oracle AGI V7
if os.path.exists("oracle_agi_v7_ultimate.py"):
    print("Starting Oracle AGI V7 Ultimate...")
    subprocess.run([venv_python, "oracle_agi_v7_ultimate.py"])
else:
    print("Starting minimal version...")
    
    # Create minimal server
    code = '''
import asyncio
from aiohttp import web
import json
import psutil
from datetime import datetime

async def handle_index(request):
    return web.Response(text="""
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI V7</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; padding: 40px; text-align: center; }
        h1 { color: #4CAF50; font-size: 3em; }
        .status { background: #2a2a2a; padding: 30px; border-radius: 10px; display: inline-block; margin: 20px; }
        .metric { font-size: 2em; margin: 10px; }
    </style>
</head>
<body>
    <h1>Oracle AGI V7</h1>
    <div class="status">
        <div class="metric">CPU: <span id="cpu">--</span>%</div>
        <div class="metric">Memory: <span id="memory">--</span>%</div>
    </div>
    <p>Dashboard: http://localhost:8888</p>
    <script>
        setInterval(async () => {
            const r = await fetch('/api/status');
            const d = await r.json();
            document.getElementById('cpu').textContent = d.cpu.toFixed(1);
            document.getElementById('memory').textContent = d.memory.toFixed(1);
        }, 2000);
    </script>
</body>
</html>""", content_type='text/html')

async def handle_status(request):
    return web.json_response({
        'status': 'running',
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent
    })

app = web.Application()
app.router.add_get('/', handle_index)
app.router.add_get('/api/status', handle_status)

print("\\nOracle AGI V7 running at http://localhost:8888")
web.run_app(app, port=8888)
    '''
    
    with open("oracle_minimal.py", "w") as f:
        f.write(code)
    
    subprocess.run([venv_python, "oracle_minimal.py"])