"""Custom exceptions for the MCPVotsAGI SDK."""

from __future__ import annotations


class MCPVotsAGIError(Exception):
    """Base exception for all MCPVotsAGI errors."""


class ServiceConnectionError(MCPVotsAGIError):
    """Failed to connect to a service (Redis, WebSocket, etc.)."""


class MemoryOperationError(MCPVotsAGIError):
    """Error in memory operations (store, retrieve, search)."""


class AgentError(MCPVotsAGIError):
    """Error in agent operations (registration, discovery, messaging)."""


class ReasoningError(MCPVotsAGIError):
    """Error in AI reasoning operations."""


class ConfigError(MCPVotsAGIError):
    """Invalid or missing configuration."""


class ServerError(MCPVotsAGIError):
    """Error in MCP server operations."""
