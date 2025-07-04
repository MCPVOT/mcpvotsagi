#!/usr/bin/env python3
"""
Perfect Oracle AGI V7 Launcher with venv
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("="*80)
    print(" ORACLE AGI V7 ULTIMATE - PERFECT LAUNCH SYSTEM")
    print("="*80)
    
    # Set paths
    workspace = Path("C:/Workspace")
    mcpvots_agi = workspace / "MCPVotsAGI"
    venv_python = workspace / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print("ERROR: Virtual environment not found!")
        print(f"Expected at: {venv_python}")
        return
    
    print(f"✓ Using venv Python: {venv_python}")
    
    # Change to MCPVotsAGI directory
    os.chdir(mcpvots_agi)
    print(f"✓ Working directory: {os.getcwd()}")
    
    # Kill any existing processes
    print("\nCleaning up existing processes...")
    subprocess.run("taskkill /F /IM python.exe 2>nul", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM node.exe 2>nul", shell=True, capture_output=True)
    time.sleep(2)
    
    # Check and install requirements
    print("\nChecking requirements...")
    requirements_file = mcpvots_agi / "requirements.txt"
    
    if not requirements_file.exists():
        print("Creating requirements.txt...")
        requirements = """aiohttp>=3.9.0
psutil>=5.9.0
redis>=5.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
torch>=2.0.0
transformers>=4.30.0
faiss-cpu>=1.7.4
networkx>=3.0
pyyaml>=6.0
websockets>=11.0
aiofiles>=23.0
python-dotenv>=1.0.0
"""
        with open(requirements_file, 'w') as f:
            f.write(requirements)
    
    # Install/upgrade requirements
    print("Installing/upgrading requirements...")
    result = subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Warning: Some packages failed to install")
        print("Installing core requirements only...")
        core_reqs = ["aiohttp", "psutil", "pyyaml", "websockets", "numpy", "pandas"]
        for req in core_reqs:
            subprocess.run(
                [str(venv_python), "-m", "pip", "install", req],
                capture_output=True
            )
    
    # Start infrastructure services
    print("\n" + "="*60)
    print("Starting infrastructure services...")
    print("="*60)
    
    # Start Redis if available
    redis_path = Path("C:/ProgramData/chocolatey/bin/redis-server.exe")
    if redis_path.exists():
        print("Starting Redis...")
        subprocess.Popen([str(redis_path)], shell=True)
        time.sleep(2)
    else:
        print("! Redis not found (optional)")
    
    # Start IPFS if available
    ipfs_path = Path("C:/ProgramData/chocolatey/bin/ipfs.exe")
    if ipfs_path.exists():
        print("Starting IPFS...")
        subprocess.Popen([str(ipfs_path), "daemon"], shell=True)
        time.sleep(3)
    else:
        print("! IPFS not found (optional)")
    
    # Start Ollama if available
    ollama_path = Path("C:/Users/Aldo7/AppData/Local/Programs/Ollama/ollama.exe")
    if ollama_path.exists():
        print("Starting Ollama...")
        subprocess.Popen([str(ollama_path), "serve"], shell=True)
        time.sleep(3)
    else:
        print("! Ollama not found (optional)")
    
    # Start n8n if available
    try:
        print("Checking n8n...")
        subprocess.run("npx --version", shell=True, capture_output=True, check=True)
        print("Starting n8n...")
        subprocess.Popen("npx n8n", shell=True)
        time.sleep(5)
    except:
        print("! n8n not available (optional)")
    
    # Launch Oracle AGI V7
    print("\n" + "="*60)
    print("Launching Oracle AGI V7 Ultimate...")
    print("="*60)
    
    oracle_v7 = mcpvots_agi / "oracle_agi_v7_ultimate.py"
    
    if oracle_v7.exists():
        print(f"✓ Found: {oracle_v7}")
        print("\nStarting Oracle AGI V7 Ultimate...")
        
        # Run in a new window
        subprocess.Popen([
            "cmd", "/c", "start", "Oracle AGI V7", 
            str(venv_python), str(oracle_v7)
        ])
        
        # Wait and check if it started
        time.sleep(5)
        
        # Check if port 8888 is open
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8888))
        sock.close()
        
        if result == 0:
            print("\n" + "="*60)
            print("✅ SUCCESS! Oracle AGI V7 is running!")
            print("="*60)
            print("\n📊 Dashboard: http://localhost:8888")
            print("🔌 API: http://localhost:8888/api/status")
            print("🌐 WebSocket: ws://localhost:8888/ws")
            print("\n💡 Additional Services:")
            print("  - n8n Workflows: http://localhost:5678")
            print("  - Ollama Models: http://localhost:11434")
            print("  - IPFS Gateway: http://localhost:8080")
            print("\nPress Ctrl+C to stop all services")
        else:
            print("\n⚠️  Oracle AGI may still be starting...")
            print("Check http://localhost:8888 in a few seconds")
    else:
        # Fallback to simple version
        print("! oracle_agi_v7_ultimate.py not found")
        print("Creating minimal version...")
        
        minimal_code = '''
import asyncio
from aiohttp import web
import json
import psutil
from datetime import datetime

async def handle_index(request):
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Oracle AGI V7</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            margin: 0; 
            padding: 40px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        h1 { font-size: 3em; margin-bottom: 20px; }
        .status {
            background: rgba(255,255,255,0.2);
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }
        .metric {
            display: inline-block;
            margin: 20px;
            font-size: 1.5em;
        }
        .value { 
            font-size: 2em; 
            font-weight: bold; 
            color: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Oracle AGI V7</h1>
        <div class="status">
            <h2>System Status</h2>
            <div class="metric">
                CPU: <span class="value" id="cpu">--</span>%
            </div>
            <div class="metric">
                Memory: <span class="value" id="memory">--</span>%
            </div>
            <div class="metric">
                Uptime: <span class="value" id="uptime">--</span>
            </div>
        </div>
        <p>API Endpoint: <code>http://localhost:8888/api/status</code></p>
    </div>
    <script>
        setInterval(async () => {
            const resp = await fetch('/api/status');
            const data = await resp.json();
            document.getElementById('cpu').textContent = data.cpu.toFixed(1);
            document.getElementById('memory').textContent = data.memory.toFixed(1);
            document.getElementById('uptime').textContent = data.uptime;
        }, 2000);
    </script>
</body>
</html>
    """
    return web.Response(text=html, content_type='text/html')

async def handle_status(request):
    return web.json_response({
        'status': 'running',
        'version': '7.0.0-minimal',
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'uptime': 'Just started',
        'timestamp': datetime.utcnow().isoformat()
    })

app = web.Application()
app.router.add_get('/', handle_index)
app.router.add_get('/api/status', handle_status)

print("Starting Oracle AGI V7 Minimal on http://localhost:8888")
web.run_app(app, host='0.0.0.0', port=8888)
        '''
        
        oracle_minimal = mcpvots_agi / "oracle_v7_minimal.py"
        with open(oracle_minimal, 'w') as f:
            f.write(minimal_code)
        
        subprocess.Popen([
            "cmd", "/c", "start", "Oracle AGI V7 Minimal", 
            str(venv_python), str(oracle_minimal)
        ])
    
    # Keep this launcher running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down...")
        subprocess.run("taskkill /F /IM python.exe", shell=True)
        subprocess.run("taskkill /F /IM ollama.exe", shell=True)
        subprocess.run("taskkill /F /IM redis-server.exe", shell=True)
        subprocess.run("taskkill /F /IM ipfs.exe", shell=True)

if __name__ == "__main__":
    main()