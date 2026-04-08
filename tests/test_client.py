"""Tests for MCPVotsAGI client."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcpvotsagi.client import MCPVotsAGI
from mcpvotsagi.config import MCPVotsAGIConfig
from mcpvotsagi.exceptions import ConnectionError as AGIConnectionError


class TestMCPVotsAGIConfig:
    def test_default_config(self):
        config = MCPVotsAGIConfig()
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.a2a_port == 8001
        assert config.log_level == "INFO"

    def test_custom_config(self):
        config = MCPVotsAGIConfig(redis_host="redis.example.com", redis_port=6380)
        assert config.redis_host == "redis.example.com"
        assert config.redis_port == 6380

    def test_redis_url_with_password(self):
        config = MCPVotsAGIConfig(redis_password="secret")
        assert "secret" in config.redis_url
        assert config.redis_url.startswith("redis://:secret@")

    def test_redis_url_without_password(self):
        config = MCPVotsAGIConfig()
        assert config.redis_url == "redis://localhost:6379/0"


class TestMCPVotsAGIClient:
    async def test_context_manager(self):
        with patch("mcpvotsagi.client.EnhancedMCPMemoryServer") as MockMemory:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock(return_value=True)
            mock_instance.close = AsyncMock()
            MockMemory.return_value = mock_instance

            async with MCPVotsAGI() as agi:
                assert agi._started is True

    async def test_start_raises_on_redis_failure(self):
        with patch("mcpvotsagi.client.EnhancedMCPMemoryServer") as MockMemory:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock(return_value=False)
            MockMemory.return_value = mock_instance

            agi = MCPVotsAGI()
            with pytest.raises(AGIConnectionError, match="Failed to connect to Redis"):
                await agi.start()

    async def test_memory_property_raises_before_start(self):
        agi = MCPVotsAGI()
        with pytest.raises(RuntimeError, match="SDK not started"):
            _ = agi.memory

    async def test_status(self):
        with patch("mcpvotsagi.client.EnhancedMCPMemoryServer") as MockMemory:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock(return_value=True)
            mock_instance.close = AsyncMock()
            mock_instance.redis_client = AsyncMock()
            mock_instance.redis_client.ping = AsyncMock(return_value=True)
            MockMemory.return_value = mock_instance

            async with MCPVotsAGI() as agi:
                status = await agi.status()
                assert status["started"] is True
                assert status["version"] == "2.0.0"
                assert status["services"]["redis"] == "connected"

    async def test_import_package(self):
        import mcpvotsagi
        assert mcpvotsagi.__version__ == "2.0.0"
        assert hasattr(mcpvotsagi, "MCPVotsAGI")
        assert hasattr(mcpvotsagi, "MCPVotsAGIConfig")
        assert hasattr(mcpvotsagi, "EnhancedMCPMemoryServer")
