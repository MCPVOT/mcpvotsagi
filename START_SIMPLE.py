#!/usr/bin/env python3
"""
Simple startup for ULTIMATE AGI SYSTEM
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Set UTF-8
if sys.platform == 'win32':
    subprocess.run('chcp 65001', shell=True, capture_output=True)
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

async def main():
    print("MCPVotsAGI ULTIMATE SYSTEM")
    print("=" * 60)
    
    # Quick system check
    print("\nSystem Check:")
    
    # Check Ollama
    try:
        import ollama
        models = ollama.list()
        print("✓ Ollama connected")
        deepseek = any('DeepSeek-R1' in m.get('name', '') for m in models.get('models', []))
        if deepseek:
            print("✓ DeepSeek-R1 model available")
    except:
        print("✗ Ollama not available")
    
    # Check port
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8888))
    sock.close()
    if result == 0:
        print("! Port 8888 in use")
    else:
        print("✓ Port 8888 available")
    
    print("\nStarting ULTIMATE AGI SYSTEM...")
    print("=" * 60)
    
    try:
        from core.ULTIMATE_AGI_SYSTEM import UltimateAGISystem
        
        # Create and run system
        system = UltimateAGISystem()
        
        # Start web server
        from aiohttp import web
        app = system.app
        
        print(f"\n✓ System initialized")
        print(f"✓ Dashboard: http://localhost:{system.port}")
        print(f"✓ API: http://localhost:{system.port}/api")
        print("\nPress Ctrl+C to stop\n")
        
        # Run server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', system.port)
        await site.start()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")