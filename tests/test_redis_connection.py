#!/usr/bin/env python3
"""
Redis Connection Test for MCPVotsAGI A2A System
Tests Redis connectivity from Windows to WSL2
"""

import redis
import asyncio
import json
from datetime import datetime

# WSL2 Redis configuration - try multiple connection options
REDIS_HOSTS = [
    "localhost",  # If Redis is forwarded to localhost
    "127.0.0.1",  # Local loopback
    "172.27.187.70"  # WSL2 IP address
]
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = "os.environ.get('REDIS_PASSWORD', '')"  # Password set by configuration script

def test_sync_redis():
    """Test synchronous Redis connection"""
    try:
        print(f"🔍 Testing synchronous Redis connection to {REDIS_HOST}:{REDIS_PORT}")

        # Create Redis client
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test basic operations
        r.ping()
        print("✅ Redis PING successful")

        # Test set/get
        test_key = "test:connection"
        test_value = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "source": "MCPVotsAGI Windows Client",
            "test": "Redis connectivity from Windows to WSL2"
        })

        r.set(test_key, test_value, ex=60)  # Expires in 60 seconds
        retrieved = r.get(test_key)
        print(f"✅ Redis SET/GET successful: {retrieved}")

        # Test pub/sub capability
        pubsub = r.pubsub()
        pubsub.subscribe("test:channel")
        r.publish("test:channel", "Hello from Windows!")

        message = pubsub.get_message(timeout=1)
        if message and message['type'] == 'subscribe':
            message = pubsub.get_message(timeout=1)

        if message:
            print(f"✅ Redis PUB/SUB successful: {message}")

        pubsub.close()
        r.close()

        return True

    except Exception as e:
        print(f"❌ Synchronous Redis test failed: {e}")
        return False

async def test_async_redis():
    """Test asynchronous Redis connection"""
    try:
        print(f"🔍 Testing asynchronous Redis connection to {REDIS_HOST}:{REDIS_PORT}")

        # Create async Redis client using redis-py async
        redis_client = redis.asyncio.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test basic operations
        await redis_client.ping()
        print("✅ Async Redis PING successful")

        # Test async set/get
        test_key = "test:async_connection"
        test_value = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "source": "MCPVotsAGI Async Windows Client",
            "test": "Async Redis connectivity"
        })

        await redis_client.set(test_key, test_value, ex=60)
        retrieved = await redis_client.get(test_key)
        print(f"✅ Async Redis SET/GET successful: {retrieved}")

        # Test async pub/sub
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("test:async_channel")
        await redis_client.publish("test:async_channel", "Hello from async Windows!")

        message = await pubsub.get_message(timeout=1)
        if message and message['type'] == 'subscribe':
            message = await pubsub.get_message(timeout=1)

        if message:
            print(f"✅ Async Redis PUB/SUB successful: {message}")

        await pubsub.unsubscribe("test:async_channel")
        await pubsub.close()
        await redis_client.close()

        return True

    except Exception as e:
        print(f"❌ Async Redis test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Redis Connection Tests for MCPVotsAGI A2A System")
    print("=" * 70)

    # Test synchronous Redis
    sync_success = test_sync_redis()
    print()

    # Test asynchronous Redis
    async_success = asyncio.run(test_async_redis())
    print()

    # Summary
    print("=" * 70)
    print("📊 REDIS CONNECTION TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Synchronous Redis: {'PASS' if sync_success else 'FAIL'}")
    print(f"✅ Asynchronous Redis: {'PASS' if async_success else 'FAIL'}")

    if sync_success and async_success:
        print("🎉 ALL TESTS PASSED! Redis is ready for A2A integration.")
        print(f"🔗 Redis Connection String: redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        return True
    else:
        print("❌ Some tests failed. Check Redis configuration and connectivity.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
