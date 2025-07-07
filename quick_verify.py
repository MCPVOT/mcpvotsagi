#!/usr/bin/env python3
"""Quick verification of Context7 integration"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.CONTEXT7_INTEGRATION import Context7Integration

async def main():
    print("🔍 Quick Context7 Integration Verification")

    # Create two instances
    ctx1 = Context7Integration()
    ctx2 = Context7Integration()

    print(f"Instance 1: Port {ctx1.port}")
    print(f"Instance 2: Port {ctx2.port}")
    print(f"Ports are different: {ctx1.port != ctx2.port}")

    # Test DeepSeek agent
    print(f"DeepSeek Agent 1: {ctx1.deepseek_agent.agent_id}")
    print(f"DeepSeek Agent 2: {ctx2.deepseek_agent.agent_id}")

    # Cleanup
    await ctx1.close_session()
    await ctx2.close_session()
    await ctx1.stop_server()
    await ctx2.stop_server()

    print("✅ Verification complete!")

if __name__ == "__main__":
    asyncio.run(main())
