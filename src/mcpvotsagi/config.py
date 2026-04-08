"""Configuration management for MCPVotsAGI SDK.

Loads settings from environment variables with sensible defaults.
All settings can be overridden via the MCPVotsAGIConfig constructor.

Environment variables::

    REDIS_HOST          Default: localhost
    REDIS_PORT          Default: 6379
    REDIS_PASSWORD      Default: (empty)
    A2A_PORT            Default: 8001
    MCP_MEMORY_PORT     Default: 3002
    DEEPSEEK_PORT       Default: 3003
    OPENCTI_PORT        Default: 3007
    OLLAMA_HOST         Default: http://localhost:11434
    LOG_LEVEL           Default: INFO
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MCPVotsAGIConfig:
    """SDK configuration. Immutable — create a new instance to change settings."""

    redis_host: str = field(default_factory=lambda: os.environ.get("REDIS_HOST", "localhost"))
    redis_port: int = field(default_factory=lambda: int(os.environ.get("REDIS_PORT", "6379")))
    redis_password: str | None = field(default_factory=lambda: os.environ.get("REDIS_PASSWORD") or None)

    a2a_port: int = field(default_factory=lambda: int(os.environ.get("A2A_PORT", "8001")))
    mcp_memory_port: int = field(default_factory=lambda: int(os.environ.get("MCP_MEMORY_PORT", "3002")))
    deepseek_port: int = field(default_factory=lambda: int(os.environ.get("DEEPSEEK_PORT", "3003")))
    opencti_port: int = field(default_factory=lambda: int(os.environ.get("OPENCTI_PORT", "3007")))

    ollama_host: str = field(default_factory=lambda: os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
    deepseek_model: str = "deepseek-r1"

    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))

    @property
    def redis_url(self) -> str:
        """Build Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"
