"""MCPVotsAGI — MCP integration SDK with agent orchestration, memory, and AI reasoning.

Quick start::

    from mcpvotsagi import MCPVotsAGI

    async with MCPVotsAGI() as agi:
        await agi.memory.store("key", {"data": "value"})
        agents = await agi.a2a.discover(capability="trading")
        result = await agi.reason("Analyze this market data...")
"""

from __future__ import annotations

__version__ = "2.0.0"
__all__ = [
    "__version__",
    "MCPVotsAGI",
    "MCPVotsAGIConfig",
    "EnhancedMCPMemoryServer",
    "A2AProtocolGateway",
    "AgentRegistry",
    "UnifiedDGMServer",
    "ConsolidatedMCPServers",
    "DeepSeekMCPServer",
    "DeepSeekReasoningEngine",
]

from mcpvotsagi.client import MCPVotsAGI
from mcpvotsagi.config import MCPVotsAGIConfig
from mcpvotsagi.core.memory import EnhancedMCPMemoryServer
from mcpvotsagi.core.a2a import A2AProtocolGateway, AgentRegistry
from mcpvotsagi.core.dgm import UnifiedDGMServer
from mcpvotsagi.core.mcp_servers import ConsolidatedMCPServers
from mcpvotsagi.servers.deepseek import DeepSeekMCPServer, DeepSeekReasoningEngine
