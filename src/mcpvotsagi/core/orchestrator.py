"""MCPVotsAGI Master Orchestrator — coordinates all system components.

Manages lifecycle of child processes (MCP servers, agents, dashboards).
Components are configured at construction time, not hardcoded.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class MCPVotsAGIMasterOrchestrator:
    """Master orchestrator for all system components.

    Example::

        orchestrator = MCPVotsAGIMasterOrchestrator(components={
            "memory": {
                "module": "mcpvotsagi.core.memory",
                "description": "MCP Memory Server",
                "critical": True,
            },
        })
        await orchestrator.start_all_systems()
    """

    def __init__(self, components: dict[str, dict[str, Any]] | None = None) -> None:
        self.running_processes: dict[str, dict[str, Any]] = {}
        self.system_status: dict[str, Any] = {}
        self.components = components or {}

    async def start_all_systems(self) -> None:
        """Start all registered components."""
        logger.info("Starting MCPVotsAGI Master Orchestrator")

        for name, config in self.components.items():
            await self.start_component(name, config)

        await self.monitoring_loop()

    async def start_component(self, name: str, config: dict[str, Any]) -> None:
        """Start a system component as a subprocess."""
        module = config.get("module")
        if not module:
            logger.warning("Component %s has no 'module' configured, skipping", name)
            return

        logger.info("Starting %s...", config.get("description", name))

        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", module,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.running_processes[name] = {
                "process": process,
                "config": config,
                "start_time": datetime.now(),
                "restart_count": 0,
            }

            logger.info("%s started (PID: %d)", config.get("description", name), process.pid)

        except Exception as e:
            logger.error("Failed to start %s: %s", name, e)

    async def monitoring_loop(self) -> None:
        """Monitor all components and restart if needed."""
        logger.info("Starting system monitoring")

        while True:
            try:
                for name, process_info in list(self.running_processes.items()):
                    await self.check_component_health(name, process_info)

                await self.update_system_status()
                await asyncio.sleep(30)

            except asyncio.CancelledError:
                logger.info("Shutting down master orchestrator")
                await self.shutdown_all_systems()
                break
            except Exception as e:
                logger.error("Monitoring error: %s", e)
                await asyncio.sleep(60)

    async def check_component_health(self, name: str, process_info: dict[str, Any]) -> None:
        """Check health of a component and restart if needed."""
        process = process_info["process"]
        config = process_info["config"]

        if process.returncode is not None:
            logger.warning("%s has stopped", config.get("description", name))

            if config.get("restart_on_failure", True):
                max_restarts = config.get("max_restarts", 5)
                if process_info["restart_count"] < max_restarts:
                    logger.info("Restarting %s...", config.get("description", name))
                    del self.running_processes[name]
                    await self.start_component(name, config)
                    if name in self.running_processes:
                        self.running_processes[name]["restart_count"] = process_info["restart_count"] + 1
                else:
                    logger.error("%s failed too many times", config.get("description", name))

    async def update_system_status(self) -> None:
        """Update overall system status."""
        running = sum(1 for p in self.running_processes.values() if p["process"].returncode is None)
        total = len(self.components)

        self.system_status = {
            "timestamp": datetime.now().isoformat(),
            "running_components": running,
            "total_components": total,
            "system_health": "healthy" if running == total else "degraded",
            "components": {},
        }

        for name, process_info in self.running_processes.items():
            self.system_status["components"][name] = {
                "status": "running" if process_info["process"].returncode is None else "stopped",
                "uptime": str(datetime.now() - process_info["start_time"]),
                "restart_count": process_info["restart_count"],
            }

    async def shutdown_all_systems(self) -> None:
        """Gracefully shutdown all systems."""
        logger.info("Shutting down all systems")

        for name, process_info in self.running_processes.items():
            process = process_info["process"]
            desc = process_info["config"].get("description", name)

            if process.returncode is None:
                logger.info("Stopping %s...", desc)
                process.terminate()

                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)
                    logger.info("%s stopped gracefully", desc)
                except asyncio.TimeoutError:
                    logger.warning("Force killing %s", desc)
                    process.kill()
                    await process.wait()

        logger.info("All systems stopped")


async def main() -> None:
    """Run the orchestrator with default components."""
    orchestrator = MCPVotsAGIMasterOrchestrator()
    await orchestrator.start_all_systems()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
