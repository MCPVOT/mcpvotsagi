#!/usr/bin/env python3
"""
Quick verification of Context7 port resolution
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.CONTEXT7_INTEGRATION import Context7Integration

async def verify_port_resolution():
    """Quick verification that port resolution works"""
    print("🔍 Verifying Context7 Port Resolution...")

    # Create two instances
    ctx1 = Context7Integration()
    ctx2 = Context7Integration()

    print(f"Instance 1: Port {ctx1.port}")
    print(f"Instance 2: Port {ctx2.port}")
    print(f"Ports are different: {ctx1.port != ctx2.port}")

    # Clean up
    await ctx1.close_session()
    await ctx2.close_session()
    await ctx1.stop_server()
    await ctx2.stop_server()

    if ctx1.port != ctx2.port:
        print("✅ SUCCESS: Port conflict resolution working!")
        return True
    else:
        print("❌ FAILURE: Port conflict not resolved")
        return False

if __name__ == "__main__":
    result = asyncio.run(verify_port_resolution())
    sys.exit(0 if result else 1)
