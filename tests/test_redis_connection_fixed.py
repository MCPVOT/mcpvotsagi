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

def test_redis_host(host, password=None):
    """Test Redis connection to specific host"""
    try:
        print(f"🔍 Testing Redis connection to {host}:{REDIS_PORT}")

        # Create Redis client
        r = redis.Redis(
            host=host,
            port=REDIS_PORT,
            password=password,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test basic operations
        r.ping()
        print(f"✅ Redis PING successful on {host}")

        # Test set/get
        test_key = "test:connection"
        test_value = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "source": "MCPVotsAGI Windows Client",
            "host": host,
            "test": "Redis connectivity from Windows to WSL2"
        })

        r.set(test_key, test_value, ex=60)  # Expires in 60 seconds
        retrieved = r.get(test_key)
        print(f"✅ Redis SET/GET successful on {host}")
        print(f"   Data: {retrieved}")

        # Test pub/sub capability
        pubsub = r.pubsub()
        pubsub.subscribe("test:channel")
        r.publish("test:channel", f"Hello from Windows via {host}!")

        message = pubsub.get_message(timeout=1)
        if message and message['type'] == 'subscribe':
            message = pubsub.get_message(timeout=1)

        if message:
            print(f"✅ Redis PUB/SUB successful on {host}")

        pubsub.close()
        r.close()

        return True

    except Exception as e:
        print(f"❌ Redis connection failed to {host}:{REDIS_PORT} - {e}")
        return False

async def test_async_redis_host(host, password=None):
    """Test asynchronous Redis connection to specific host"""
    try:
        print(f"🔍 Testing async Redis connection to {host}:{REDIS_PORT}")

        # Create async Redis client using redis-py async
        redis_client = redis.asyncio.Redis(
            host=host,
            port=REDIS_PORT,
            password=password,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test basic operations
        await redis_client.ping()
        print(f"✅ Async Redis PING successful on {host}")

        # Test async set/get
        test_key = "test:async_connection"
        test_value = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "source": "MCPVotsAGI Async Windows Client",
            "host": host,
            "test": "Async Redis connectivity"
        })

        await redis_client.set(test_key, test_value, ex=60)
        retrieved = await redis_client.get(test_key)
        print(f"✅ Async Redis SET/GET successful on {host}")
        print(f"   Data: {retrieved}")

        # Test async pub/sub
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("test:async_channel")
        await redis_client.publish("test:async_channel", f"Hello from async Windows via {host}!")

        message = await pubsub.get_message(timeout=1)
        if message and message['type'] == 'subscribe':
            message = await pubsub.get_message(timeout=1)

        if message:
            print(f"✅ Async Redis PUB/SUB successful on {host}")

        await pubsub.unsubscribe("test:async_channel")
        await pubsub.close()
        await redis_client.close()

        return True

    except Exception as e:
        print(f"❌ Async Redis connection failed to {host}:{REDIS_PORT} - {e}")
        return False

def find_working_redis_host():
    """Find a working Redis host from the list"""
    print("🔍 Searching for working Redis host...")

    for host in REDIS_HOSTS:
        if test_redis_host(host, REDIS_PASSWORD):
            print(f"✅ Found working Redis host: {host}")
            return host

    print("❌ No working Redis host found")
    return None

async def find_working_async_redis_host():
    """Find a working async Redis host from the list"""
    print("🔍 Searching for working async Redis host...")

    for host in REDIS_HOSTS:
        if await test_async_redis_host(host, REDIS_PASSWORD):
            print(f"✅ Found working async Redis host: {host}")
            return host

    print("❌ No working async Redis host found")
    return None

def main():
    """Main test function"""
    print("🚀 Starting Redis Connection Tests for MCPVotsAGI A2A System")
    print("=" * 70)

    # Test synchronous Redis
    print("\n📡 TESTING SYNCHRONOUS REDIS CONNECTIONS")
    print("-" * 50)
    sync_host = find_working_redis_host()

    print("\n📡 TESTING ASYNCHRONOUS REDIS CONNECTIONS")
    print("-" * 50)
    async_host = asyncio.run(find_working_async_redis_host())

    # Summary
    print("\n" + "=" * 70)
    print("📊 REDIS CONNECTION TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Synchronous Redis: {'PASS' if sync_host else 'FAIL'}")
    if sync_host:
        print(f"   Working Host: {sync_host}")

    print(f"✅ Asynchronous Redis: {'PASS' if async_host else 'FAIL'}")
    if async_host:
        print(f"   Working Host: {async_host}")

    if sync_host or async_host:
        print("🎉 SUCCESS! Redis is ready for A2A integration.")
        working_host = sync_host or async_host
        print(f"🔗 Redis Connection String: redis://:{REDIS_PASSWORD}@{working_host}:{REDIS_PORT}/{REDIS_DB}")

        # Save configuration
        config = {
            "redis_host": working_host,
            "redis_port": REDIS_PORT,
            "redis_password": REDIS_PASSWORD,
            "redis_db": REDIS_DB,
            "sync_working": bool(sync_host),
            "async_working": bool(async_host),
            "tested_hosts": REDIS_HOSTS,
            "timestamp": datetime.now().isoformat()
        }

        with open("redis_working_config.json", "w") as f:
            json.dump(config, f, indent=2)

        print(f"📄 Working configuration saved to: redis_working_config.json")
        return True
    else:
        print("❌ FAILED! Redis is not accessible. Check Redis configuration.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
