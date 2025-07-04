#!/usr/bin/env python3
"""
Simple Oracle AGI V7 Launcher
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def check_port(port):
    """Check if a port is in use"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def main():
    print("="*60)
    print("Starting Oracle AGI V7 - Simple Mode")
    print("="*60)
    
    workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
    os.chdir(workspace)
    
    # Check if the full V7 exists, otherwise use minimal
    if (workspace / "oracle_agi_v7_ultimate.py").exists():
        print("\nStarting Oracle AGI V7 Ultimate...")
        try:
            # Try to start with minimal dependencies
            subprocess.run([sys.executable, "oracle_agi_v7_ultimate.py"])
        except Exception as e:
            print(f"\nV7 Ultimate failed: {e}")
            print("Falling back to minimal version...")
    
    # Fallback to minimal
    if (workspace / "oracle_agi_minimal.py").exists():
        print("\nStarting Oracle AGI Minimal...")
        subprocess.run([sys.executable, "oracle_agi_minimal.py"])
    else:
        print("\nCreating and starting a simple web server...")
        
        # Create a minimal server
        minimal_code = '''
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
        body { font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px; }
        .status { background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0; }
        h1 { color: #4CAF50; }
    </style>
</head>
<body>
    <h1>Oracle AGI V7 - Running</h1>
    <div class="status">
        <h2>System Status</h2>
        <p>CPU: <span id="cpu">--</span>%</p>
        <p>Memory: <span id="memory">--</span>%</p>
        <p>Time: <span id="time">--</span></p>
    </div>
    <script>
        async function updateStatus() {
            try {
                const resp = await fetch('/api/status');
                const data = await resp.json();
                document.getElementById('cpu').textContent = data.cpu.toFixed(1);
                document.getElementById('memory').textContent = data.memory.toFixed(1);
                document.getElementById('time').textContent = new Date(data.time).toLocaleString();
            } catch(e) {
                console.error(e);
            }
        }
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
    """, content_type='text/html')

async def handle_status(request):
    return web.json_response({
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'time': datetime.utcnow().isoformat(),
        'version': 'Oracle AGI V7 Minimal'
    })

app = web.Application()
app.router.add_get('/', handle_index)
app.router.add_get('/api/status', handle_status)

print("Starting Oracle AGI V7 on http://localhost:8888")
web.run_app(app, host='0.0.0.0', port=8888)
        '''
        
        with open("oracle_agi_v7_minimal_temp.py", "w") as f:
            f.write(minimal_code)
        
        subprocess.run([sys.executable, "oracle_agi_v7_minimal_temp.py"])

if __name__ == "__main__":
    main()