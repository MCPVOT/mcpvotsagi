"""Test fixtures for MCPVotsAGI SDK."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.aclose = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.hset = AsyncMock(return_value=1)
    client.hgetall = AsyncMock(return_value={})
    client.hincrby = AsyncMock(return_value=1)
    client.delete = AsyncMock(return_value=1)
    client.sadd = AsyncMock(return_value=1)
    client.srem = AsyncMock(return_value=1)
    client.scard = AsyncMock(return_value=0)
    client.smembers = AsyncMock(return_value=set())

    # Mock pipeline
    pipeline = AsyncMock()
    pipeline.hset = MagicMock(return_value=pipeline)
    pipeline.sadd = MagicMock(return_value=pipeline)
    pipeline.set = MagicMock(return_value=pipeline)
    pipeline.delete = MagicMock(return_value=pipeline)
    pipeline.srem = MagicMock(return_value=pipeline)
    pipeline.execute = AsyncMock(return_value=[True])
    pipeline.__aenter__ = AsyncMock(return_value=pipeline)
    pipeline.__aexit__ = AsyncMock(return_value=None)
    client.pipeline = MagicMock(return_value=pipeline)

    # Mock scan_iter
    async def mock_scan_iter(match=None):
        return iter([])
    client.scan_iter = mock_scan_iter

    return client


@pytest.fixture
def config():
    """Create a test config."""
    from mcpvotsagi.config import MCPVotsAGIConfig
    return MCPVotsAGIConfig(
        redis_host="localhost",
        redis_port=6379,
        redis_password=None,
    )
