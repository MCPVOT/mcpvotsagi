"""Enhanced MCP Memory Server with Redis Integration.

Unified memory service for MCPVotsAGI with Redis backend.
Provides persistent memory storage, retrieval, and search for MCP agents.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class MemoryNotConnectedError(Exception):
    """Raised when a memory operation is attempted before Redis is connected."""


class EnhancedMCPMemoryServer:
    """Enhanced MCP Memory server with Redis backend.

    Provides namespaced key-value memory with category indexing,
    access tracking, and full-text search over stored values.
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: str | None = None,
    ) -> None:
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password or os.environ.get("REDIS_PASSWORD")
        self.redis_client: redis.Redis | None = None
        self.memory_namespace = "mcp:memory"

    def _require_redis(self) -> redis.Redis:
        """Return the Redis client or raise if not connected."""
        if self.redis_client is None:
            raise MemoryNotConnectedError(
                "Redis client not connected. Call start() before using memory operations."
            )
        return self.redis_client

    async def start(self) -> bool:
        """Connect to Redis and verify connectivity."""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis at %s:%d", self.redis_host, self.redis_port)
            return True
        except Exception as e:
            logger.error("Failed to connect to Redis: %s", e)
            return False

    async def close(self) -> None:
        """Gracefully close the Redis connection."""
        if self.redis_client:
            await self.redis_client.aclose()
            self.redis_client = None

    async def store_memory(self, key: str, value: Any, category: str = "general") -> str:
        """Store memory with metadata. Returns the memory ID."""
        client = self._require_redis()

        memory_id = str(uuid.uuid4())
        memory_data: dict[str, str] = {
            "id": memory_id,
            "key": key,
            "value": json.dumps(value) if not isinstance(value, str) else value,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "access_count": "0",
        }

        redis_key = f"{self.memory_namespace}:{memory_id}"
        async with client.pipeline() as pipe:
            pipe.hset(redis_key, mapping=memory_data)
            pipe.sadd(f"{self.memory_namespace}:categories:{category}", memory_id)
            pipe.set(f"{self.memory_namespace}:keys:{key}", memory_id)
            await pipe.execute()

        logger.info("Stored memory: %s -> %s", key, memory_id)
        return memory_id

    async def retrieve_memory(self, key: str) -> dict[str, Any] | None:
        """Retrieve memory by key."""
        client = self._require_redis()

        memory_id = await client.get(f"{self.memory_namespace}:keys:{key}")
        if not memory_id:
            return None

        redis_key = f"{self.memory_namespace}:{memory_id}"
        memory_data = await client.hgetall(redis_key)
        if not memory_data:
            return None

        await client.hincrby(redis_key, "access_count", 1)

        try:
            memory_data["value"] = json.loads(memory_data["value"])
        except (json.JSONDecodeError, TypeError):
            pass

        logger.info("Retrieved memory: %s", key)
        return memory_data

    async def search_memories(self, category: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Search memories by category. Uses SCAN for production safety.

        When no category is provided, falls back to a full SCAN which can be
        slow on large datasets. Prefer querying with a category when possible.
        """
        client = self._require_redis()

        if category:
            memory_ids = await client.smembers(f"{self.memory_namespace}:categories:{category}")
        else:
            logger.warning("Searching all memories without category — this may be slow on large datasets")
            memory_ids: set[str] = set()
            async for key in client.scan_iter(match=f"{self.memory_namespace}:*"):
                parts = key.split(":")
                if len(parts) == 3:
                    memory_ids.add(parts[-1])

        memories: list[dict[str, Any]] = []
        for memory_id in list(memory_ids)[:limit]:
            redis_key = f"{self.memory_namespace}:{memory_id}"
            memory_data = await client.hgetall(redis_key)
            if memory_data:
                try:
                    memory_data["value"] = json.loads(memory_data["value"])
                except (json.JSONDecodeError, TypeError):
                    pass
                memories.append(memory_data)

        return memories

    async def delete_memory(self, key: str) -> bool:
        """Delete memory by key. Returns True if found and deleted."""
        client = self._require_redis()

        memory_id = await client.get(f"{self.memory_namespace}:keys:{key}")
        if not memory_id:
            return False

        redis_key = f"{self.memory_namespace}:{memory_id}"
        memory_data = await client.hgetall(redis_key)
        if not memory_data:
            return False

        category = memory_data.get("category", "general")
        async with client.pipeline() as pipe:
            pipe.srem(f"{self.memory_namespace}:categories:{category}", memory_id)
            pipe.delete(f"{self.memory_namespace}:keys:{key}")
            pipe.delete(redis_key)
            await pipe.execute()

        logger.info("Deleted memory: %s", key)
        return True

    async def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        client = self._require_redis()

        total = 0
        category_stats: dict[str, int] = {}
        async for key in client.scan_iter(match=f"{self.memory_namespace}:categories:*"):
            category = key.split(":")[-1]
            count = await client.scard(key)
            category_stats[category] = count
            total += count

        return {
            "total_memories": total,
            "categories": category_stats,
            "redis_info": {
                "host": self.redis_host,
                "port": self.redis_port,
                "connected": self.redis_client is not None,
            },
        }


async def main() -> None:
    """Run the MCP memory server."""
    memory_server = EnhancedMCPMemoryServer()

    if await memory_server.start():
        logger.info("Enhanced MCP Memory Server started")
        logger.info("  Redis: %s:%d", memory_server.redis_host, memory_server.redis_port)
        logger.info("  Namespace: %s", memory_server.memory_namespace)
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await memory_server.close()
            logger.info("MCP Memory Server shut down")
    else:
        logger.error("Failed to start MCP Memory Server")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
