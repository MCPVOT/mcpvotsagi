#!/usr/bin/env python3
"""
Enhanced Ecosystem Launcher with Claudia AI Integration
======================================================
Launch the complete Ultimate AGI System V3 with Claudia AI assistance
"""

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EcosystemLauncher")

class EnhancedEcosystemLauncher:
    """Enhanced launcher with Claudia AI integration"""

    def __init__(self):
        self.workspace = Path(__file__).parent
        self.processes = {}
        self.claudia_status = False

    async def check_claudia_availability(self) -> bool:
        """Check if Claudia/Ollama is available"""
        try:
            import requests
            response = requests.get("http://localhost:11435/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                logger.info(f"✅ Claudia/Ollama available with {len(models)} models")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Claudia/Ollama not available: {e}")
        return False

    async def start_core_services(self):
        """Start core AGI services"""
        logger.info("🚀 Starting Enhanced Ultimate AGI System V3...")

        # Check Claudia availability
        self.claudia_status = await self.check_claudia_availability()

        services = [
            {
                "name": "Jupiter Ultimate Dashboard V4",
                "command": [sys.executable, "jupiter_ultimate_dashboard_v4.py"],
                "port": 8891,
                "health_url": "http://localhost:8891",
                "enhanced": True
            },
            {
                "name": "Claudia Enhanced Trading System",
                "command": [sys.executable, "claudia_enhanced_trading_system.py"],
                "enabled": self.claudia_status
            },
            {
                "name": "Ultimate Trading System V3",
                "command": [sys.executable, "ultimate_trading_system_v3.py"],
                "port": 8892
            },
            {
                "name": "WatchYourLAN Cyberpunk Integration",
                "command": [sys.executable, "watchyourlan_cyberpunk_ultimate_integration.py"],
                "port": 8893
            },
            {
                "name": "Cyberpunk Dashboard",
                "command": [sys.executable, "cyberpunk_dashboard.py"],
                "port": 8894
            }
        ]

        for service in services:
            if service.get("enabled", True):
                await self._start_service(service)
            else:
                logger.info(f"⏭️ Skipping {service['name']} (requirements not met)")

    async def _start_service(self, service: Dict):
        """Start individual service"""
        try:
            logger.info(f"🔄 Starting {service['name']}...")

            process = subprocess.Popen(
                service["command"],
                cwd=self.workspace,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes[service["name"]] = process

            # Give service time to start
            await asyncio.sleep(2)

            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✅ {service['name']} started successfully")
                if service.get("port"):
                    logger.info(f"   🌐 Available at: http://localhost:{service['port']}")
                if service.get("enhanced"):
                    logger.info(f"   🤖 Claudia AI: {'Enabled' if self.claudia_status else 'Disabled'}")
            else:
                logger.error(f"❌ {service['name']} failed to start")

        except Exception as e:
            logger.error(f"Error starting {service['name']}: {e}")

    async def monitor_ecosystem(self):
        """Monitor ecosystem health"""
        logger.info("📊 Monitoring ecosystem health...")

        while True:
            try:
                running_services = []
                failed_services = []

                for name, process in self.processes.items():
                    if process.poll() is None:
                        running_services.append(name)
                    else:
                        failed_services.append(name)

                logger.info(f"🔄 Status: {len(running_services)} running, {len(failed_services)} failed")

                if failed_services:
                    logger.warning(f"⚠️ Failed services: {', '.join(failed_services)}")

                # Check Claudia status periodically
                if len(running_services) > 0:
                    current_claudia_status = await self.check_claudia_availability()
                    if current_claudia_status != self.claudia_status:
                        self.claudia_status = current_claudia_status
                        logger.info(f"🤖 Claudia status changed: {'Available' if current_claudia_status else 'Unavailable'}")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in ecosystem monitoring: {e}")
                await asyncio.sleep(10)

    async def display_status(self):
        """Display enhanced status information"""
        logger.info("\n" + "="*60)
        logger.info("🌟 ULTIMATE AGI SYSTEM V3 - ENHANCED ECOSYSTEM STATUS")
        logger.info("="*60)

        if self.claudia_status:
            logger.info("🤖 CLAUDIA AI: ACTIVE")
            logger.info("   ✅ Advanced market analysis enabled")
            logger.info("   ✅ Intelligent trading signals active")
            logger.info("   ✅ AI-powered risk assessment online")
        else:
            logger.info("🤖 CLAUDIA AI: INACTIVE")
            logger.info("   ⚠️ Using fallback technical analysis")

        logger.info("\n📊 ACTIVE SERVICES:")
        for name, process in self.processes.items():
            status = "🟢 RUNNING" if process.poll() is None else "🔴 STOPPED"
            logger.info(f"   {name}: {status}")

        logger.info("\n🌐 ACCESS POINTS:")
        access_points = [
            ("Jupiter Ultimate Dashboard V4", "http://localhost:8891", "Enhanced with Claudia AI"),
            ("Ultimate Trading System V3", "http://localhost:8892", "Real trading engine"),
            ("WatchYourLAN Integration", "http://localhost:8893", "Network monitoring"),
            ("Cyberpunk Dashboard", "http://localhost:8894", "System overview")
        ]

        for name, url, description in access_points:
            logger.info(f"   {name}: {url}")
            logger.info(f"     → {description}")

        logger.info("\n🚀 ENHANCED FEATURES:")
        features = [
            "✅ Real Jupiter DEX data streaming",
            "✅ Advanced RL trading algorithms",
            "✅ Real-time system monitoring",
            "✅ Resource-optimized MCP integration",
            "✅ Dark cyberpunk UI theme",
            "✅ WebSocket live updates"
        ]

        if self.claudia_status:
            features.extend([
                "🤖 Claudia AI market analysis",
                "🧠 Intelligent signal combination",
                "📈 AI-powered risk assessment"
            ])

        for feature in features:
            logger.info(f"   {feature}")

        logger.info("="*60)

    async def shutdown(self):
        """Gracefully shutdown all services"""
        logger.info("🔄 Shutting down Enhanced Ultimate AGI System V3...")

        for name, process in self.processes.items():
            try:
                logger.info(f"⏹️ Stopping {name}...")
                process.terminate()

                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ {name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Force killing {name}...")
                    process.kill()

            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")

        logger.info("✅ Enhanced ecosystem shutdown complete")

    async def run(self):
        """Run the enhanced ecosystem"""
        try:
            # Start all services
            await self.start_core_services()

            # Wait a bit for services to fully initialize
            await asyncio.sleep(5)

            # Display status
            await self.display_status()

            # Start monitoring
            await self.monitor_ecosystem()

        except KeyboardInterrupt:
            logger.info("\n🛑 Received shutdown signal...")
        except Exception as e:
            logger.error(f"Ecosystem error: {e}")
        finally:
            await self.shutdown()

async def main():
    """Main launcher function"""
    logger.info("🌟 Enhanced Ultimate AGI System V3 Launcher")
    logger.info("🤖 With Claudia AI Integration")
    logger.info("=" * 50)

    launcher = EnhancedEcosystemLauncher()
    await launcher.run()

if __name__ == "__main__":
    asyncio.run(main())
