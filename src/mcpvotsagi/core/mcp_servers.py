"""
Consolidated MCP Servers Manager
==============================
Single process to manage all MCP tool servers and avoid duplicates
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConsolidatedMCPServers:
    """Manages all MCP servers in a single process."""

    def __init__(self) -> None:
        self.servers: dict[str, dict[str, Any]] = {}
        self.running = False

        # Default data directory — override via MCP_DATA_DIR env var
        data_dir = os.environ.get("MCP_DATA_DIR", str(Path.home() / ".mcpvotsagi" / "data"))
        Path(data_dir).mkdir(parents=True, exist_ok=True)

        # Define MCP servers configuration
        self.mcp_config: dict[str, dict[str, Any]] = {
            "filesystem": {
                "port": 3000,
                "command": ["npx", "@modelcontextprotocol/server-filesystem", data_dir],
                "description": "File system operations",
            },
            "github": {
                "port": 3001,
                "command": ["npx", "@modelcontextprotocol/server-github"],
                "description": "GitHub integration",
            },
            "memory": {
                "port": 3002,
                "command": [sys.executable, "-m", "mcpvotsagi.core.memory"],
                "description": "Enhanced memory with Redis",
            },
            "browser": {
                "port": 3003,
                "command": ["npx", "@modelcontextprotocol/server-puppeteer"],
                "description": "Browser automation",
            },
            "search": {
                "port": 3004,
                "command": ["npx", "@modelcontextprotocol/server-brave-search"],
                "description": "Web search via Brave",
            },
            "solana": {
                "port": 3005,
                "command": ["npx", "@modelcontextprotocol/server-solana"],
                "description": "Solana blockchain",
            },
            "huggingface": {
                "port": 3006,
                "command": ["npx", "@modelcontextprotocol/server-huggingface"],
                "description": "HuggingFace models",
            },
        }

    async def _drain_output(self, name: str, stream: asyncio.StreamReader) -> None:
        """Drain subprocess stdout/stderr to prevent pipe deadlock."""
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                logger.debug("[%s] %s", name, line.decode(errors="replace").rstrip())
        except Exception:
            pass

    async def start_server(self, name: str, config: dict[str, Any]) -> bool:
        """Start individual MCP server."""
        try:
            logger.info("Starting %s MCP server on port %d...", name, config["port"])

            process = await asyncio.create_subprocess_exec(
                *config["command"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.servers[name] = {
                "process": process,
                "config": config,
                "started_at": datetime.now(),
            }

            # Drain stdout/stderr to prevent pipe buffer deadlock
            asyncio.create_task(self._drain_output(name, process.stdout))
            asyncio.create_task(self._drain_output(name, process.stderr))

            logger.info("%s MCP server started (PID: %s)", name, process.pid)
            return True

        except Exception as e:
            logger.error("Failed to start %s MCP server: %s", name, e)
            return False

    async def start_all_servers(self) -> bool:
        """Start all MCP servers."""
        logger.info("Starting Consolidated MCP Servers...")
        logger.info("=" * 50)

        success_count = 0
        for name, config in self.mcp_config.items():
            if await self.start_server(name, config):
                success_count += 1
            await asyncio.sleep(1)  # Stagger starts

        logger.info("MCP Servers Status: %d/%d started", success_count, len(self.mcp_config))
        self.running = True

        return success_count > 0

    async def stop_all_servers(self) -> None:
        """Stop all MCP servers."""
        logger.info("Stopping all MCP servers...")

        for name, server_info in self.servers.items():
            try:
                process = server_info["process"]
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5)
                logger.info("Stopped %s MCP server", name)
            except asyncio.TimeoutError:
                process.kill()
                logger.warning("Force killed %s MCP server", name)
            except Exception as e:
                logger.error("Error stopping %s: %s", name, e)

        self.running = False

    async def monitor_servers(self) -> None:
        """Monitor server health and restart if needed."""
        while self.running:
            for name, server_info in list(self.servers.items()):
                process = server_info["process"]
                if process.returncode is not None:
                    logger.warning("%s MCP server died (exit code %d), restarting...", name, process.returncode)
                    await self.start_server(name, server_info["config"])

            await asyncio.sleep(30)

    async def run(self) -> None:
        """Main run loop with graceful shutdown via asyncio.Event."""
        if not await self.start_all_servers():
            logger.error("Failed to start MCP servers")
            return

        logger.info("All MCP servers are running!")
        logger.info("Press Ctrl+C to stop all servers")

        shutdown_event = asyncio.Event()

        # Use asyncio signal handlers instead of signal.signal()
        loop = asyncio.get_event_loop()
        try:
            loop.add_signal_handler(asyncio.Signal.SIGINT, shutdown_event.set)
            loop.add_signal_handler(asyncio.Signal.SIGTERM, shutdown_event.set)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler — fall back gracefully
            pass

        monitor_task = asyncio.create_task(self.monitor_servers())

        try:
            await shutdown_event.wait()
        except asyncio.CancelledError:
            pass
        finally:
            monitor_task.cancel()
            await self.stop_all_servers()


async def main() -> None:
    """Main entry point."""
    servers_manager = ConsolidatedMCPServers()
    await servers_manager.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
