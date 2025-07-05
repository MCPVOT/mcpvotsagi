#!/usr/bin/env python3
"""
Test core systems without full startup
"""

import os
import sys
import asyncio

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

async def test_systems():
    print("Testing Core Systems")
    print("=" * 60)
    
    # Test 1: Ollama connection
    print("\n1. Testing Ollama/DeepSeek-R1...")
    try:
        import ollama
        response = ollama.list()
        models = [m['name'] for m in response['models']]
        deepseek_model = next((m for m in models if 'DeepSeek-R1' in m), None)
        if deepseek_model:
            print(f"   OK: Found {deepseek_model}")
            # Test generation
            result = ollama.generate(model=deepseek_model, prompt="Say 'System operational' in 3 words")
            print(f"   Response: {result['response'].strip()}")
        else:
            print("   WARNING: DeepSeek-R1 model not found")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: MCP Implementation
    print("\n2. Testing MCP Implementation...")
    try:
        from core.COMPLETE_MCP_IMPLEMENTATION import RealMCPClient
        print("   OK: MCP client imported")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Trading Engine
    print("\n3. Testing Trading Engine...")
    try:
        from trading.REAL_TRADING_ENGINE import RealTradingEngine
        engine = RealTradingEngine({})
        print("   OK: Trading engine created")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 4: Memory System
    print("\n4. Testing Memory System...")
    try:
        from memory.ultimate_memory_system import UltimateMemorySystem
        from pathlib import Path
        memory = UltimateMemorySystem(Path.cwd())
        print("   OK: Memory system initialized")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 5: Dashboard
    print("\n5. Testing Dashboard...")
    try:
        from core.ULTIMATE_DASHBOARD_V2 import generate_ultimate_dashboard_v2
        html = generate_ultimate_dashboard_v2()
        print(f"   OK: Dashboard generated ({len(html)} bytes)")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 6: Port availability
    print("\n6. Testing Port 8888...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8888))
    sock.close()
    if result == 0:
        print("   WARNING: Port 8888 is in use")
    else:
        print("   OK: Port 8888 is available")
    
    print("\n" + "=" * 60)
    print("Core Systems Test Complete")

if __name__ == "__main__":
    asyncio.run(test_systems())
    input("\nPress Enter to exit...")