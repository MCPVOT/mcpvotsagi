#!/usr/bin/env python3
"""
Enhanced MCP Memory Server with Redis Integration
===============================================
Unified memory service for MCPVotsAGI with Redis backend
"""

import asyncio
import json
import logging
import redis.asyncio as redis
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class EnhancedMCPMemoryServer:
    """Enhanced MCP Memory server with Redis backend"""

    def __init__(self, redis_host='localhost', redis_port=6379, redis_password='MCPVotsAGI2025!'):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_client = None
        self.memory_namespace = "mcp:memory"

    async def start(self):
        """Start the memory server"""
        try:
            # Connect to Redis
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            logging.info(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")

            return True

        except Exception as e:
            logging.error(f"❌ Failed to connect to Redis: {e}")
            return False

    async def store_memory(self, key: str, value: Any, category: str = "general") -> str:
        """Store memory with metadata"""
        memory_id = str(uuid.uuid4())
        memory_data = {
            "id": memory_id,
            "key": key,
            "value": json.dumps(value) if not isinstance(value, str) else value,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }

        # Store in Redis
        redis_key = f"{self.memory_namespace}:{memory_id}"
        await self.redis_client.hset(redis_key, mapping=memory_data)

        # Add to category index
        await self.redis_client.sadd(f"{self.memory_namespace}:categories:{category}", memory_id)

        # Add to key index
        await self.redis_client.set(f"{self.memory_namespace}:keys:{key}", memory_id)

        logging.info(f"📝 Stored memory: {key} -> {memory_id}")
        return memory_id

    async def retrieve_memory(self, key: str) -> Optional[Dict]:
        """Retrieve memory by key"""
        # Get memory ID from key index
        memory_id = await self.redis_client.get(f"{self.memory_namespace}:keys:{key}")
        if not memory_id:
            return None

        # Get memory data
        redis_key = f"{self.memory_namespace}:{memory_id}"
        memory_data = await self.redis_client.hgetall(redis_key)

        if memory_data:
            # Increment access count
            await self.redis_client.hincrby(redis_key, "access_count", 1)

            # Try to parse JSON value
            try:
                memory_data["value"] = json.loads(memory_data["value"])
            except (json.JSONDecodeError, TypeError):
                pass  # Keep as string

            logging.info(f"📖 Retrieved memory: {key}")
            return memory_data

        return None

    async def search_memories(self, category: str = None, limit: int = 100) -> List[Dict]:
        """Search memories by category"""
        if category:
            memory_ids = await self.redis_client.smembers(f"{self.memory_namespace}:categories:{category}")
        else:
            # Get all memory keys
            keys = await self.redis_client.keys(f"{self.memory_namespace}:*")
            memory_ids = [key.split(":")[-1] for key in keys if len(key.split(":")) == 3]

        memories = []
        for memory_id in list(memory_ids)[:limit]:
            redis_key = f"{self.memory_namespace}:{memory_id}"
            memory_data = await self.redis_client.hgetall(redis_key)
            if memory_data:
                try:
                    memory_data["value"] = json.loads(memory_data["value"])
                except (json.JSONDecodeError, TypeError):
                    pass
                memories.append(memory_data)

        return memories

    async def delete_memory(self, key: str) -> bool:
        """Delete memory by key"""
        memory_id = await self.redis_client.get(f"{self.memory_namespace}:keys:{key}")
        if not memory_id:
            return False

        # Get memory data to find category
        redis_key = f"{self.memory_namespace}:{memory_id}"
        memory_data = await self.redis_client.hgetall(redis_key)

        if memory_data:
            category = memory_data.get("category", "general")

            # Remove from category index
            await self.redis_client.srem(f"{self.memory_namespace}:categories:{category}", memory_id)

            # Remove key index
            await self.redis_client.delete(f"{self.memory_namespace}:keys:{key}")

            # Remove memory data
            await self.redis_client.delete(redis_key)

            logging.info(f"🗑️ Deleted memory: {key}")
            return True

        return False

    async def get_stats(self) -> Dict:
        """Get memory statistics"""
        total_memories = len(await self.redis_client.keys(f"{self.memory_namespace}:*"))
        categories = await self.redis_client.keys(f"{self.memory_namespace}:categories:*")
        category_stats = {}

        for cat_key in categories:
            category = cat_key.split(":")[-1]
            count = await self.redis_client.scard(cat_key)
            category_stats[category] = count

        return {
            "total_memories": total_memories,
            "categories": category_stats,
            "redis_info": {
                "host": self.redis_host,
                "port": self.redis_port,
                "connected": self.redis_client is not None
            }
        }

async def main():
    """Main MCP memory server"""
    memory_server = EnhancedMCPMemoryServer()

    if await memory_server.start():
        print("🧠 Enhanced MCP Memory Server started successfully!")
        print(f"   Redis: {memory_server.redis_host}:{memory_server.redis_port}")
        print(f"   Namespace: {memory_server.memory_namespace}")

        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down MCP Memory Server...")
    else:
        print("❌ Failed to start MCP Memory Server")

if __name__ == "__main__":
    asyncio.run(main())
