"""Tests for EnhancedMCPMemoryServer."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcpvotsagi.core.memory import EnhancedMCPMemoryServer


@pytest.fixture
def memory_server(mock_redis):
    """Create a memory server with mocked Redis."""
    server = EnhancedMCPMemoryServer(redis_host="localhost", redis_port=6379)
    server.redis_client = mock_redis
    return server


class TestMemoryServer:
    async def test_start_connects_to_redis(self):
        server = EnhancedMCPMemoryServer()
        with patch("mcpvotsagi.core.memory.redis") as mock_redis_mod:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(return_value=True)
            mock_redis_mod.Redis = MagicMock(return_value=mock_client)

            result = await server.start()
            assert result is True
            assert server.redis_client is not None

    async def test_start_fails_gracefully(self):
        server = EnhancedMCPMemoryServer()
        with patch("mcpvotsagi.core.memory.redis") as mock_redis_mod:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(side_effect=Exception("Connection refused"))
            mock_redis_mod.Redis = MagicMock(return_value=mock_client)

            result = await server.start()
            assert result is False

    async def test_store_memory(self, memory_server, mock_redis):
        memory_id = await memory_server.store_memory("test_key", {"action": "buy"}, category="trading")
        assert memory_id is not None
        assert len(memory_id) == 36  # UUID format
        mock_redis.hset.assert_called_once()

    async def test_retrieve_memory_found(self, memory_server, mock_redis):
        mock_redis.get = AsyncMock(return_value="test-uuid")
        mock_redis.hgetall = AsyncMock(return_value={
            "id": "test-uuid",
            "key": "test_key",
            "value": json.dumps({"action": "buy"}),
            "category": "trading",
        })

        result = await memory_server.retrieve_memory("test_key")
        assert result is not None
        assert result["key"] == "test_key"
        assert result["value"]["action"] == "buy"

    async def test_retrieve_memory_not_found(self, memory_server, mock_redis):
        mock_redis.get = AsyncMock(return_value=None)
        result = await memory_server.retrieve_memory("nonexistent")
        assert result is None

    async def test_delete_memory(self, memory_server, mock_redis):
        mock_redis.get = AsyncMock(return_value="test-uuid")
        mock_redis.hgetall = AsyncMock(return_value={"category": "trading"})

        result = await memory_server.delete_memory("test_key")
        assert result is True

    async def test_delete_memory_not_found(self, memory_server, mock_redis):
        mock_redis.get = AsyncMock(return_value=None)
        result = await memory_server.delete_memory("nonexistent")
        assert result is False

    async def test_close(self, memory_server, mock_redis):
        await memory_server.close()
        mock_redis.aclose.assert_called_once()
        assert memory_server.redis_client is None
