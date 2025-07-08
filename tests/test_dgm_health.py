#!/usr/bin/env python3
"""
Quick DGM Services Health Test
=============================
Test all DGM services and report their status
"""

import asyncio
import aiohttp
import json
from pathlib import Path

async def test_dgm_health():
    """Test health of all DGM services"""
    services = [
        {"name": "dgm_evolution_connector", "url": "http://localhost:8002/health"},
        {"name": "dgm_trading_algorithms_v2", "url": "http://localhost:8004/health"},
        {"name": "dgm_trading_algorithms", "url": "http://localhost:8005/health"}
    ]

    print("🔍 Testing DGM Services Health...")
    print("=" * 50)

    healthy_count = 0

    async with aiohttp.ClientSession() as session:
        for service in services:
            try:
                async with session.get(service["url"], timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {service['name']}: {data.get('status', 'unknown')}")
                        healthy_count += 1
                    else:
                        print(f"❌ {service['name']}: HTTP {response.status}")
            except Exception as e:
                print(f"❌ {service['name']}: {str(e)}")

    print(f"\n📊 Health Summary: {healthy_count}/{len(services)} services healthy")

    if healthy_count == len(services):
        print("🎯 All DGM services are operational!")

        # Save success status
        status_file = Path("dgm_services_status.json")
        with open(status_file, 'w') as f:
            json.dump({
                "all_healthy": True,
                "healthy_count": healthy_count,
                "total_services": len(services),
                "timestamp": "2025-07-07T20:53:00"
            }, f, indent=2)

        print(f"💾 Status saved to {status_file}")

    return healthy_count == len(services)

if __name__ == "__main__":
    asyncio.run(test_dgm_health())
