#!/usr/bin/env python3
"""
MCPVotsAGI Master Orchestrator
=============================
Master orchestrator for coordinating all system components
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MasterOrchestrator")

class MCPVotsAGIMasterOrchestrator:
    """Master orchestrator for all system components"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.running_processes = {}
        self.system_status = {}

        # Define system components
        self.components = {
            "rl_trading": {
                "path": "core/rl_trading/enhanced_24x7_rl_system.py",
                "description": "24/7 RL Trading System",
                "critical": True,
                "restart_on_failure": True
            },
            "claudia_ai": {
                "path": "core/agents/claudia_advanced_system.py",
                "description": "Claudia AI Self-Improvement",
                "critical": True,
                "restart_on_failure": True
            },
            "network_monitoring": {
                "path": "integrations/watchyourlan/watchyourlan_dashboard_integration.py",
                "description": "Network Monitoring Dashboard",
                "critical": False,
                "restart_on_failure": True
            },
            "trading_dashboard": {
                "path": "dashboards/trading/ultimate_trading_dashboard_v3_fixed.py",
                "description": "Trading Dashboard",
                "critical": False,
                "restart_on_failure": True
            }
        }

    async def start_all_systems(self):
        """Start all system components"""
        logger.info("🚀 Starting MCPVotsAGI Master Orchestrator...")

        # Start all components
        for component_name, config in self.components.items():
            await self.start_component(component_name, config)

        # Start monitoring loop
        await self.monitoring_loop()

    async def start_component(self, name: str, config: Dict[str, Any]):
        """Start a system component"""
        component_path = self.base_path / config["path"]

        if not component_path.exists():
            logger.warning(f"⚠️  Component file not found: {component_path}")
            return

        try:
            logger.info(f"🔄 Starting {config['description']}...")

            process = await asyncio.create_subprocess_exec(
                sys.executable, str(component_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            self.running_processes[name] = {
                "process": process,
                "config": config,
                "start_time": datetime.now(),
                "restart_count": 0
            }

            logger.info(f"✅ {config['description']} started (PID: {process.pid})")

        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")

    async def monitoring_loop(self):
        """Monitor all components and restart if needed"""
        logger.info("👁️  Starting system monitoring...")

        while True:
            try:
                for name, process_info in list(self.running_processes.items()):
                    await self.check_component_health(name, process_info)

                # Update system status
                await self.update_system_status()

                await asyncio.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                logger.info("🛑 Shutting down master orchestrator...")
                await self.shutdown_all_systems()
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)

    async def check_component_health(self, name: str, process_info: Dict[str, Any]):
        """Check health of a component"""
        process = process_info["process"]
        config = process_info["config"]

        # Check if process is still running
        if process.returncode is not None:
            logger.warning(f"⚠️  {config['description']} has stopped")

            if config.get("restart_on_failure", False):
                if process_info["restart_count"] < 5:  # Max 5 restarts
                    logger.info(f"🔄 Restarting {config['description']}...")

                    # Remove old process
                    del self.running_processes[name]

                    # Start new process
                    await self.start_component(name, config)

                    if name in self.running_processes:
                        self.running_processes[name]["restart_count"] = process_info["restart_count"] + 1
                else:
                    logger.error(f"❌ {config['description']} failed too many times, not restarting")

    async def update_system_status(self):
        """Update overall system status"""
        running_components = len([p for p in self.running_processes.values()
                                 if p["process"].returncode is None])
        total_components = len(self.components)

        self.system_status = {
            "timestamp": datetime.now().isoformat(),
            "running_components": running_components,
            "total_components": total_components,
            "system_health": "healthy" if running_components == total_components else "degraded",
            "components": {}
        }

        for name, process_info in self.running_processes.items():
            self.system_status["components"][name] = {
                "status": "running" if process_info["process"].returncode is None else "stopped",
                "uptime": str(datetime.now() - process_info["start_time"]),
                "restart_count": process_info["restart_count"]
            }

        # Log status every 10 minutes
        if datetime.now().minute % 10 == 0:
            logger.info(f"📊 System Status: {running_components}/{total_components} components running")

    async def shutdown_all_systems(self):
        """Gracefully shutdown all systems"""
        logger.info("🛑 Shutting down all systems...")

        for name, process_info in self.running_processes.items():
            process = process_info["process"]
            config = process_info["config"]

            if process.returncode is None:
                logger.info(f"🔄 Stopping {config['description']}...")
                process.terminate()

                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)
                    logger.info(f"✅ {config['description']} stopped gracefully")
                except asyncio.TimeoutError:
                    logger.warning(f"⚠️  Force killing {config['description']}...")
                    process.kill()
                    await process.wait()

        logger.info("✅ All systems stopped")

async def main():
    """Main function"""
    orchestrator = MCPVotsAGIMasterOrchestrator()
    await orchestrator.start_all_systems()

if __name__ == "__main__":
    asyncio.run(main())
