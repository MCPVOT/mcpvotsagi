#!/usr/bin/env python3
"""
Run ULTIMATE AGI SYSTEM - Windows compatible
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
        print("[OK] Ollama connected")
        deepseek = any('DeepSeek-R1' in m.get('name', '') for m in models.get('models', []))
        if deepseek:
            print("[OK] DeepSeek-R1 model available")
    except:
        print("[WARN] Ollama not available")
    
    # Check port
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8888))
    sock.close()
    if result == 0:
        print("[WARN] Port 8888 in use - will find alternative")
        # Find available port
        for port in range(8889, 9000):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:
                print(f"[OK] Using port {port}")
                os.environ['AGI_PORT'] = str(port)
                break
    else:
        print("[OK] Port 8888 available")
        os.environ['AGI_PORT'] = '8888'
    
    print("\nStarting ULTIMATE AGI SYSTEM...")
    print("=" * 60)
    
    try:
        # Import core system
        from core.ULTIMATE_AGI_SYSTEM import UltimateAGISystem
        
        # Override port if needed
        port = int(os.environ.get('AGI_PORT', 8888))
        
        # Create system
        system = UltimateAGISystem()
        system.port = port
        
        # Import REAL implementations to replace dummies
        try:
            from core.COMPLETE_MCP_IMPLEMENTATION import create_real_mcp_executor
            from trading.REAL_TRADING_ENGINE import create_real_trading_engine
            
            # Initialize real components
            print("\nInitializing REAL components...")
            
            # Real MCP
            system.mcp_executor = await create_real_mcp_executor()
            print("[OK] REAL MCP executor initialized")
            
            # Real Trading
            trading_config = {
                'finnhub_api_key': os.getenv('FINNHUB_API_KEY'),
                'solana_rpc': 'https://api.mainnet-beta.solana.com'
            }
            system.trading_engine = await create_real_trading_engine(trading_config)
            print("[OK] REAL trading engine initialized")
            
        except Exception as e:
            print(f"[WARN] Could not initialize all REAL components: {e}")
        
        # Start web server
        from aiohttp import web
        app = system.app
        
        print(f"\n[OK] System initialized")
        print(f"[OK] Dashboard: http://localhost:{port}")
        print(f"[OK] API: http://localhost:{port}/api")
        print(f"[OK] WebSocket: ws://localhost:{port}/ws")
        print("\nPress Ctrl+C to stop\n")
        
        # Open browser
        try:
            import webbrowser
            webbrowser.open(f'http://localhost:{port}')
        except:
            pass
        
        # Run server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        
        print("System is running...")
        
        # Keep running
        while True:
            await asyncio.sleep(60)
            # Could add periodic status updates here
            
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
    except Exception as e:
        print(f"Fatal error: {e}")
    
    input("\nPress Enter to exit...")