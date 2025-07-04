#!/usr/bin/env python3
"""
Fix common issues and run Oracle AGI
"""

import os
import sys
import subprocess
import socket
import time
import signal
from pathlib import Path

def kill_process_on_port(port):
    """Kill process using a specific port"""
    if sys.platform == "win32":
        # Windows
        cmd = f"netstat -ano | findstr :{port}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    try:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                        print(f"✓ Killed process {pid} on port {port}")
                    except:
                        pass
    else:
        # Linux/Mac
        try:
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
            if result.stdout:
                pid = result.stdout.strip()
                os.kill(int(pid), signal.SIGTERM)
                print(f"✓ Killed process {pid} on port {port}")
        except:
            pass

def check_and_create_dirs():
    """Create necessary directories"""
    dirs = [
        "servers",
        "logs",
        "backups",
        "static"
    ]
    
    for dir_name in dirs:
        dir_path = Path(__file__).parent / dir_name
        dir_path.mkdir(exist_ok=True)
    
    print("✓ Directories created")

def create_minimal_mcp_server():
    """Create a minimal memory MCP server if missing"""
    server_path = Path(__file__).parent / "servers" / "enhanced_memory_mcp_server.py"
    
    if not server_path.exists():
        server_path.parent.mkdir(exist_ok=True)
        
        content = '''#!/usr/bin/env python3
"""Minimal Memory MCP Server"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

memory_store = {}

async def handle_client(websocket, path):
    """Handle WebSocket connections"""
    logger.info(f"Client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data.get("method") == "memory/store":
                key = data.get("params", {}).get("key", "default")
                value = data.get("params", {}).get("value", "")
                memory_store[key] = value
                
                response = {
                    "jsonrpc": "2.0",
                    "result": {"status": "stored", "key": key},
                    "id": data.get("id")
                }
                await websocket.send(json.dumps(response))
                
            elif data.get("method") == "memory/retrieve":
                key = data.get("params", {}).get("key", "default")
                value = memory_store.get(key, None)
                
                response = {
                    "jsonrpc": "2.0",
                    "result": {"key": key, "value": value},
                    "id": data.get("id")
                }
                await websocket.send(json.dumps(response))
                
            elif data.get("method") == "ping":
                await websocket.pong()
                
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info(f"Client disconnected: {websocket.remote_address}")

async def main():
    """Start the MCP server"""
    server = await websockets.serve(handle_client, "localhost", 3002)
    logger.info("Memory MCP Server started on ws://localhost:3002")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        server_path.write_text(content)
        print("✓ Created minimal Memory MCP server")

def main():
    print("=" * 60)
    print("  Oracle AGI Fix & Run Script")
    print("=" * 60)
    
    # Kill processes on common ports
    print("\n1. Checking ports...")
    ports_to_check = [3011, 3010, 3012, 8080, 8081, 3002]
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:  # Port in use
            print(f"⚠️  Port {port} is in use, attempting to free it...")
            kill_process_on_port(port)
            time.sleep(1)
    
    # Create directories
    print("\n2. Setting up directories...")
    check_and_create_dirs()
    
    # Create minimal servers if needed
    print("\n3. Checking MCP servers...")
    create_minimal_mcp_server()
    
    # Install minimal dependencies
    print("\n4. Installing dependencies...")
    try:
        import aiohttp
        import websockets
        print("✓ Core dependencies already installed")
    except ImportError:
        print("Installing core dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp", "websockets", "aiohttp-cors", "psutil"], 
                      capture_output=True)
        print("✓ Dependencies installed")
    
    # Run the dashboard
    print("\n5. Starting Oracle AGI Dashboard...")
    
    run_script = Path(__file__).parent / "run_oracle_agi.py"
    if run_script.exists():
        subprocess.run([sys.executable, str(run_script)])
    else:
        # Direct run
        oracle_script = Path(__file__).parent / "oracle_agi_unified_final.py"
        if oracle_script.exists():
            print("\n🚀 Starting Oracle AGI Dashboard...")
            subprocess.run([sys.executable, str(oracle_script)])
        else:
            print("❌ Oracle AGI scripts not found!")
            print("Please ensure oracle_agi_unified_final.py exists")

if __name__ == "__main__":
    main()