#!/usr/bin/env python3
"""
Test A2A Enhanced Protocol with Redis Integration
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the core directory to the path
sys.path.append(str(Path(__file__).parent / "core"))

from a2a_enhanced_protocol import A2AMessageQueue, A2AMessage, MessageType, AgentInfo, AgentStatus
from datetime import datetime

async def test_redis_message_queue():
    """Test Redis message queue functionality"""
    print("🚀 Testing A2A Enhanced Protocol with Redis")
    print("=" * 60)

    # Initialize message queue
    queue = A2AMessageQueue()

    try:
        # Connect to Redis
        print("🔌 Connecting to Redis...")
        await queue.connect()

        # Create test message
        test_message = A2AMessage(
            message_id="test-001",
            source_agent="test-agent-1",
            target_agent="test-agent-2",
            message_type=MessageType.REQUEST,
            payload={
                "action": "test_action",
                "data": {"message": "Hello from A2A Enhanced Protocol!"},
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now()
        )

        # Test publish
        print("📤 Publishing test message...")
        await queue.publish("test-channel", test_message)
        print(f"✅ Message {test_message.message_id} published successfully")

        # Test message serialization
        print("🔄 Testing message serialization...")
        message_dict = test_message.to_dict()
        print(f"✅ Serialized: {json.dumps(message_dict, indent=2)}")

        # Test message deserialization
        restored_message = A2AMessage.from_dict(message_dict)
        print(f"✅ Deserialized: {restored_message.message_id}")

        print("\n🎉 A2A Enhanced Protocol Redis test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ A2A test failed: {e}")
        return False

    finally:
        # Disconnect
        print("🔌 Disconnecting from Redis...")
        await queue.disconnect()

async def test_agent_registry():
    """Test agent registry functionality"""
    print("\n📋 Testing Agent Registry")
    print("-" * 40)

    try:
        # Create test agent
        agent = AgentInfo(
            agent_id="test-agent-001",
            name="Test Agent",
            capabilities=["chat", "file_operations", "web_search"],
            endpoint="ws://localhost:8001",
            status=AgentStatus.ONLINE,
            metadata={"version": "1.0.0", "type": "test"},
            last_seen=datetime.now()
        )

        # Test agent serialization
        agent_dict = agent.to_dict()
        print(f"✅ Agent serialized: {json.dumps(agent_dict, indent=2)}")

        return True

    except Exception as e:
        print(f"❌ Agent registry test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 MCPVotsAGI A2A Enhanced Protocol Test Suite")
    print("=" * 70)

    # Test Redis message queue
    redis_success = await test_redis_message_queue()

    # Test agent registry
    agent_success = await test_agent_registry()

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Redis Message Queue: {'PASS' if redis_success else 'FAIL'}")
    print(f"✅ Agent Registry: {'PASS' if agent_success else 'FAIL'}")

    if redis_success and agent_success:
        print("🎉 ALL TESTS PASSED! A2A Enhanced Protocol is ready.")
        return True
    else:
        print("❌ Some tests failed. Check the A2A protocol configuration.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
