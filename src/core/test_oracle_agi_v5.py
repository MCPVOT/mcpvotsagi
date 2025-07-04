#!/usr/bin/env python3
"""
Oracle AGI V5 System Test
========================
Quick test to verify all components are working
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

async def test_service(name: str, url: str) -> bool:
    """Test if a service is responsive"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                status = response.status == 200
                print(f"{'✓' if status else '✗'} {name}: {url} - {'OK' if status else 'FAILED'}")
                return status
    except Exception as e:
        print(f"✗ {name}: {url} - ERROR: {str(e)}")
        return False

async def test_api_endpoint(name: str, url: str, method: str = 'GET', data: dict = None) -> bool:
    """Test API endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, timeout=5) as response:
                    status = response.status == 200
                    if status:
                        result = await response.json()
                        print(f"✓ {name}: {len(result)} items" if isinstance(result, list) else f"✓ {name}: Response received")
                    return status
            else:
                async with session.post(url, json=data, timeout=5) as response:
                    status = response.status == 200
                    print(f"{'✓' if status else '✗'} {name}: {'OK' if status else 'FAILED'}")
                    return status
    except Exception as e:
        print(f"✗ {name}: {url} - ERROR: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🔮 Oracle AGI V5 System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test core services
    print("\n📡 Testing Core Services:")
    services = {
        "Oracle AGI Core": "http://localhost:8888/health",
        "Trilogy Brain": "http://localhost:8887/health",
        "Trading System": "http://localhost:8889/health",
        "Dashboard": "http://localhost:3002/api/status",
        "DeepSeek/Ollama": "http://localhost:11434/api/tags",
        "Gemini CLI": "http://localhost:8080/health"
    }
    
    service_results = []
    for name, url in services.items():
        result = await test_service(name, url)
        service_results.append(result)
    
    # Test API endpoints
    print("\n🔌 Testing API Endpoints:")
    api_tests = [
        ("System Status", "http://localhost:3002/api/status", "GET", None),
        ("Trading Signals", "http://localhost:3002/api/trading/signals", "GET", None),
        ("Performance Metrics", "http://localhost:3002/api/metrics", "GET", None),
    ]
    
    api_results = []
    for name, url, method, data in api_tests:
        result = await test_api_endpoint(name, url, method, data)
        api_results.append(result)
    
    # Test WebSocket
    print("\n🔗 Testing WebSocket:")
    try:
        import websockets
        async with websockets.connect("ws://localhost:3002/ws", timeout=5) as ws:
            await ws.send(json.dumps({"type": "ping"}))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"✓ WebSocket: Connected and responsive")
            ws_result = True
    except Exception as e:
        print(f"✗ WebSocket: Connection failed - {str(e)}")
        ws_result = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    total_services = len(service_results)
    passed_services = sum(service_results)
    total_apis = len(api_results)
    passed_apis = sum(api_results)
    
    print(f"Services: {passed_services}/{total_services} passed")
    print(f"APIs: {passed_apis}/{total_apis} passed")
    print(f"WebSocket: {'Passed' if ws_result else 'Failed'}")
    
    overall_health = (passed_services + passed_apis + (1 if ws_result else 0)) / (total_services + total_apis + 1) * 100
    
    print(f"\n🎯 Overall System Health: {overall_health:.1f}%")
    
    if overall_health >= 80:
        print("✅ System is healthy and ready to use!")
    elif overall_health >= 50:
        print("⚠️  System is partially operational. Some services may be unavailable.")
    else:
        print("❌ System health is critical. Please check the services.")
    
    print("=" * 60)
    
    # Provide helpful next steps
    if overall_health < 100:
        print("\n💡 Troubleshooting Tips:")
        if not service_results[0]:  # Oracle Core
            print("- Start Oracle AGI Core: python oracle_agi_core.py")
        if not service_results[3]:  # Dashboard
            print("- Start Dashboard: python oracle_agi_v5_unified_dashboard.py")
        if not service_results[4]:  # DeepSeek
            print("- Start Ollama: ollama serve")
        print("\nOr run the complete launcher: python launch_oracle_agi_v5.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest error: {e}")
        sys.exit(1)