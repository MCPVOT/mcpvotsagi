#!/usr/bin/env python3
"""
Start ULTIMATE AGI SYSTEM V2 with MCPVots Integration
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    subprocess.run('chcp 65001', shell=True, capture_output=True)
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set environment
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'core'))

print("""
================================================================================
                    ULTIMATE AGI SYSTEM V2 - MCPVots Enhanced
================================================================================
Features:
- Self-healing architecture (94%+ success rate)
- Browser automation with MCP Chrome
- Desktop app deployment with Pake
- Advanced ML/DL workflows from MCPVots
- Knowledge graph and semantic reasoning
- Evolutionary algorithm optimization
================================================================================
""")

async def main():
    # Check dependencies
    print("Checking system dependencies...")
    
    # Check Ollama
    try:
        import ollama
        models = ollama.list()
        print("[OK] Ollama connected")
        if any('DeepSeek-R1' in m.get('name', '') for m in models.get('models', [])):
            print("[OK] DeepSeek-R1 model available")
    except:
        print("[WARN] Ollama not available - some features disabled")
    
    # Check MCP Chrome
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3000/health') as resp:
                if resp.status == 200:
                    print("[OK] MCP Chrome server running")
    except:
        print("[INFO] MCP Chrome not running - browser automation disabled")
        print("      To enable: cd tools/mcp-chrome && npm install && npm start")
    
    # Check IPFS
    try:
        import ipfshttpclient
        client = ipfshttpclient.connect()
        print("[OK] IPFS daemon connected")
    except:
        print("[INFO] IPFS not running - distributed storage disabled")
        print("      To enable: ipfs daemon")
    
    print("\nStarting ULTIMATE AGI SYSTEM V2...")
    
    # Import and run V2
    from core.ULTIMATE_AGI_SYSTEM_V2 import UltimateAGISystemV2
    
    system = UltimateAGISystemV2()
    
    # Check port availability
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', system.port))
    sock.close()
    
    if result == 0:
        print(f"\n[WARN] Port {system.port} is already in use!")
        print("Options:")
        print("1. Stop the existing process")
        print("2. Use a different port (set AGI_PORT environment variable)")
        print("3. Continue anyway (may fail)")
        
        choice = input("\nYour choice (1/2/3): ")
        
        if choice == '1':
            if sys.platform == 'win32':
                os.system(f'netstat -ano | findstr :{system.port}')
                pid = input("Enter PID to kill: ")
                os.system(f'taskkill /F /PID {pid}')
            else:
                os.system(f'lsof -ti:{system.port} | xargs kill -9')
            print("Process killed. Restarting...")
        elif choice == '2':
            new_port = input("Enter new port: ")
            os.environ['AGI_PORT'] = new_port
            system.port = int(new_port)
    
    print(f"\nSystem will start on: http://localhost:{system.port}")
    print("Press Ctrl+C to stop\n")
    
    # Open browser
    try:
        import webbrowser
        webbrowser.open(f'http://localhost:{system.port}')
    except:
        pass
    
    # Run system
    await system.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown complete. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")