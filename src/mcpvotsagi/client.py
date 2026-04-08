"""MCPVotsAGI main client — unified entry point for the SDK.

Usage::

    from mcpvotsagi import MCPVotsAGI, MCPVotsAGIConfig

    config = MCPVotsAGIConfig(redis_password="secret")
    async with MCPVotsAGI(config) as agi:
        # Memory operations
        await agi.memory.store("trade_1", {"action": "buy", "asset": "SOL"})

        # Agent discovery
        agents = await agi.a2a.discover(capability="trading")

        # AI reasoning
        result = await agi.reason("Should I buy SOL at current price?")

        # System status
        status = await agi.status()
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from mcpvotsagi.config import MCPVotsAGIConfig
from mcpvotsagi.core.memory import EnhancedMCPMemoryServer
from mcpvotsagi.exceptions import ConnectionError as AGIConnectionError

if TYPE_CHECKING:
    from mcpvotsagi.core.a2a import A2AProtocolGateway, AgentRegistry
    from mcpvotsagi.core.dgm import UnifiedDGMServer

logger = logging.getLogger(__name__)


class MCPVotsAGI:
    """Main SDK client for the MCPVotsAGI ecosystem.

    Provides unified access to:
    - **memory**: Persistent key-value store with Redis backend
    - **a2a**: Agent-to-agent communication protocol
    - **dgm**: Darwin Gödel Machine evolution engine
    - **reason()**: AI reasoning via DeepSeek/Ollama

    Can be used as an async context manager or managed manually.
    """

    def __init__(self, config: MCPVotsAGIConfig | None = None) -> None:
        self.config = config or MCPVotsAGIConfig()
        self._memory: EnhancedMCPMemoryServer | None = None
        self._a2a: A2AProtocolGateway | None = None
        self._dgm: UnifiedDGMServer | None = None
        self._started = False

    async def __aenter__(self) -> MCPVotsAGI:
        await self.start()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.stop()

    async def start(self) -> None:
        """Initialize all services."""
        if self._started:
            return

        logging.basicConfig(level=getattr(logging, self.config.log_level.upper(), logging.INFO))

        # Start memory server
        self._memory = EnhancedMCPMemoryServer(
            redis_host=self.config.redis_host,
            redis_port=self.config.redis_port,
            redis_password=self.config.redis_password,
        )
        if not await self._memory.start():
            raise AGIConnectionError("Failed to connect to Redis")

        logger.info("MCPVotsAGI SDK started")
        self._started = True

    async def stop(self) -> None:
        """Shut down all services."""
        if self._memory:
            await self._memory.close()
        if self._a2a:
            # A2A gateway cleanup if started
            pass
        self._started = False
        logger.info("MCPVotsAGI SDK stopped")

    @property
    def memory(self) -> EnhancedMCPMemoryServer:
        """Access the memory server. Must call start() first."""
        if not self._memory:
            raise RuntimeError("SDK not started. Use 'async with MCPVotsAGI() as agi:' or call await agi.start()")
        return self._memory

    @property
    def a2a(self) -> A2AProtocolGateway:
        """Access the A2A gateway. Must call start() first."""
        if not self._a2a:
            from mcpvotsagi.core.a2a import A2AProtocolGateway

            self._a2a = A2AProtocolGateway(port=self.config.a2a_port)
        return self._a2a

    @property
    def dgm(self) -> UnifiedDGMServer:
        """Access the DGM engine. Must call start() first."""
        if not self._dgm:
            from mcpvotsagi.core.dgm import UnifiedDGMServer

            self._dgm = UnifiedDGMServer()
        return self._dgm

    async def reason(self, prompt: str, *, task_type: str = "general", context: dict[str, Any] | None = None) -> str:
        """Send a reasoning request to the DeepSeek AI engine.

        Args:
            prompt: The question or task to reason about.
            task_type: One of 'trading', 'security', 'ecosystem', 'general'.
            context: Optional context data.

        Returns:
            The AI's response text.
        """
        from mcpvotsagi.servers.deepseek import DeepSeekReasoningEngine

        engine = DeepSeekReasoningEngine()
        response = await engine.reason(task_type=task_type, prompt=prompt, context=context or {})
        return response.result

    async def status(self) -> dict[str, Any]:
        """Get system status overview."""
        result: dict[str, Any] = {
            "version": "2.0.0",
            "started": self._started,
            "services": {},
        }
        if self._memory and self._memory.redis_client:
            try:
                await self._memory.redis_client.ping()
                result["services"]["redis"] = "connected"
            except Exception:
                result["services"]["redis"] = "disconnected"
        return result
