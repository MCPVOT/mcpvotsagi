#!/usr/bin/env python3
"""
Ultimate Trading System V3 - Fixed Launch Script
===============================================
🚀 Fixed launcher with proper token mint addresses and error handling
"""

import asyncio
import logging
import sys
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('F:/ULTIMATE_AGI_DATA/RL_TRADING/system_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SystemLauncher")

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import fixed components
try:
    from jupiter_api_wrapper_fixed import JupiterAPIWrapper
    from jupiter_rl_integration import JupiterRLIntegration
    from ultimate_trading_system_v3 import UltimateTradingSystemV3
    from ultimate_trading_dashboard_v3 import UltimateTradingDashboard
    HAS_COMPONENTS = True
except ImportError as e:
    logger.error(f"Failed to import components: {e}")
    HAS_COMPONENTS = False

class FixedTradingSystemLauncher:
    """Fixed trading system launcher with proper error handling"""

    def __init__(self):
        self.f_drive_path = "F:/ULTIMATE_AGI_DATA/RL_TRADING/"
        self.workspace_path = Path(__file__).parent
        self.components = {}
        self.status = {
            "system_started": False,
            "components_status": {},
            "start_time": None,
            "errors": []
        }

        # Ensure F: drive structure
        self._ensure_f_drive_structure()

        logger.info("🚀 Fixed Ultimate Trading System V3 Launcher initialized")

    def _ensure_f_drive_structure(self):
        """Ensure F: drive directory structure exists"""
        directories = [
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/models/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/data/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/logs/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/backups/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/dashboard_static/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/dashboard_templates/",
            "F:/ULTIMATE_AGI_DATA/CHAT_MEMORY/",
            "F:/ULTIMATE_AGI_DATA/KNOWLEDGE_GRAPH/",
            "F:/ULTIMATE_AGI_DATA/SYSTEM_LOGS/",
            "F:/ULTIMATE_AGI_DATA/CONFIG/",
            "F:/ULTIMATE_AGI_DATA/BACKUPS/"
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        logger.info("📁 F: drive structure ensured")

    async def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        try:
            logger.info("🔍 Checking system dependencies...")

            # Check if Jupiter API is accessible
            if HAS_COMPONENTS:
                async with JupiterAPIWrapper() as jupiter:
                    health = await jupiter.health_check()
                    logger.info(f"🪐 Jupiter API: {'✅ HEALTHY' if health else '❌ UNHEALTHY'}")
                    return health
            else:
                logger.error("❌ Components not available")
                return False

        except Exception as e:
            logger.error(f"❌ Dependency check failed: {e}")
            return False

    async def initialize_components(self) -> bool:
        """Initialize all system components"""
        try:
            logger.info("🔧 Initializing system components...")

            if not HAS_COMPONENTS:
                logger.error("❌ Components not available")
                return False

            # Initialize Jupiter API
            self.components["jupiter_api"] = JupiterAPIWrapper()
            logger.info("✅ Jupiter API initialized")

            # Initialize RL Integration
            self.components["jupiter_rl"] = JupiterRLIntegration()
            logger.info("✅ Jupiter RL initialized")

            # Initialize Trading System
            self.components["trading_system"] = UltimateTradingSystemV3()
            logger.info("✅ Trading System initialized")

            # Initialize Dashboard
            self.components["dashboard"] = UltimateTradingDashboard()
            logger.info("✅ Dashboard initialized")

            return True

        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            return False

    async def start_system(self) -> bool:
        """Start the complete trading system"""
        try:
            logger.info("🚀 Starting Ultimate Trading System V3...")

            # Check dependencies
            if not await self.check_dependencies():
                logger.error("❌ Dependency check failed")
                return False

            # Initialize components
            if not await self.initialize_components():
                logger.error("❌ Component initialization failed")
                return False

            # Start dashboard
            await self.start_dashboard()

            # Start trading system
            await self.start_trading()

            self.status["system_started"] = True
            self.status["start_time"] = datetime.now()

            logger.info("🎉 Ultimate Trading System V3 started successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ System start failed: {e}")
            self.status["errors"].append(str(e))
            return False

    async def start_dashboard(self):
        """Start the trading dashboard"""
        try:
            logger.info("📊 Starting trading dashboard...")

            if "dashboard" in self.components:
                dashboard = self.components["dashboard"]

                # Start dashboard server
                dashboard_task = asyncio.create_task(dashboard.start_server())

                # Wait a bit to ensure it starts
                await asyncio.sleep(2)

                logger.info("✅ Dashboard started on http://localhost:8890")
                self.status["components_status"]["dashboard"] = "running"

                return dashboard_task
            else:
                logger.error("❌ Dashboard component not initialized")
                return None

        except Exception as e:
            logger.error(f"❌ Dashboard start failed: {e}")
            self.status["components_status"]["dashboard"] = "failed"
            return None

    async def start_trading(self):
        """Start the trading system"""
        try:
            logger.info("💰 Starting trading system...")

            if "trading_system" in self.components:
                trading_system = self.components["trading_system"]

                # Start trading system (non-blocking)
                trading_task = asyncio.create_task(trading_system.start())

                # Wait a bit to ensure it starts
                await asyncio.sleep(2)

                logger.info("✅ Trading system started")
                self.status["components_status"]["trading_system"] = "running"

                return trading_task
            else:
                logger.error("❌ Trading system component not initialized")
                return None

        except Exception as e:
            logger.error(f"❌ Trading system start failed: {e}")
            self.status["components_status"]["trading_system"] = "failed"
            return None

    async def monitor_system(self):
        """Monitor system health and performance"""
        try:
            logger.info("👁️ Starting system monitoring...")

            while self.status["system_started"]:
                # Check component health
                for component_name, component in self.components.items():
                    if hasattr(component, 'health_check'):
                        health = await component.health_check()
                        status = "healthy" if health else "unhealthy"
                        self.status["components_status"][component_name] = status
                        logger.debug(f"📊 {component_name}: {status}")

                # Log system statistics
                if "trading_system" in self.components:
                    stats = self.components["trading_system"].performance_metrics
                    logger.info(f"📈 Trading Stats: {stats}")

                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"❌ System monitoring failed: {e}")

    async def run(self):
        """Run the complete system"""
        try:
            logger.info("="*60)
            logger.info("🚀 ULTIMATE TRADING SYSTEM V3 - FIXED LAUNCHER")
            logger.info("="*60)

            # Start the system
            if await self.start_system():
                logger.info("✅ System started successfully")

                # Print access points
                logger.info("🌐 Access Points:")
                logger.info("   • Trading Dashboard: http://localhost:8890")
                logger.info("   • System Logs: F:/ULTIMATE_AGI_DATA/RL_TRADING/")
                logger.info("   • Configuration: F:/ULTIMATE_AGI_DATA/CONFIG/")
                logger.info("="*60)

                # Start monitoring
                await self.monitor_system()

            else:
                logger.error("❌ System failed to start")
                logger.error("📋 Check logs for details")

        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
            await self.shutdown()
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            await self.shutdown()

    async def shutdown(self):
        """Shutdown the system gracefully"""
        try:
            logger.info("🛑 Shutting down system...")

            # Stop components
            for component_name, component in self.components.items():
                if hasattr(component, 'stop'):
                    await component.stop()
                    logger.info(f"✅ {component_name} stopped")

            # Close sessions
            for component_name, component in self.components.items():
                if hasattr(component, 'close'):
                    await component.close()
                    logger.info(f"✅ {component_name} closed")

            self.status["system_started"] = False
            logger.info("✅ System shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

async def main():
    """Main entry point"""
    launcher = FixedTradingSystemLauncher()
    await launcher.run()

if __name__ == "__main__":
    asyncio.run(main())
