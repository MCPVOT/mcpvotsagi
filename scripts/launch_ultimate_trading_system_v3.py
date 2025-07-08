#!/usr/bin/env python3
"""
Ultimate Trading System V3 Launcher
===================================
🚀 Launch the complete trading system with all components
🎯 Jupiter DEX integration with advanced RL strategies
📊 Real-time dashboard with professional UI
🧠 AI-powered trading with DeepSeek and Claudia integration
"""

import asyncio
import logging
import sys
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
import json
import traceback
from typing import Dict, List, Optional

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

class UltimateTradingSystemLauncher:
    """Complete system launcher with all components"""

    def __init__(self):
        self.f_drive_path = "F:/ULTIMATE_AGI_DATA/RL_TRADING/"
        self.workspace_path = Path(__file__).parent
        self.processes = {}
        self.status = {
            "system_started": False,
            "components_status": {},
            "start_time": None,
            "errors": []
        }

        # Ensure F: drive structure
        self._ensure_f_drive_structure()

        logger.info("🚀 Ultimate Trading System V3 Launcher initialized")

    def _ensure_f_drive_structure(self):
        """Ensure F: drive directory structure exists"""
        directories = [
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/models/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/data/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/logs/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/backups/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/dashboard_static/",
            "F:/ULTIMATE_AGI_DATA/RL_TRADING/templates/",
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

            # Check Python packages
            required_packages = [
                "aiohttp", "aiohttp_cors", "jinja2", "numpy", "pandas",
                "sqlite3", "requests", "asyncio", "websockets"
            ]

            optional_packages = [
                "torch", "sklearn", "psutil", "matplotlib", "plotly"
            ]

            missing_required = []
            missing_optional = []

            for package in required_packages:
                try:
                    __import__(package)
                    logger.info(f"✅ {package} - Available")
                except ImportError:
                    missing_required.append(package)
                    logger.error(f"❌ {package} - Missing (Required)")

            for package in optional_packages:
                try:
                    __import__(package)
                    logger.info(f"✅ {package} - Available")
                except ImportError:
                    missing_optional.append(package)
                    logger.warning(f"⚠️ {package} - Missing (Optional)")

            if missing_required:
                logger.error(f"❌ Missing required packages: {', '.join(missing_required)}")
                return False

            if missing_optional:
                logger.warning(f"⚠️ Missing optional packages: {', '.join(missing_optional)}")
                logger.info("📦 Optional packages provide enhanced functionality")

            # Check file system access
            if not os.path.exists("F:/"):
                logger.error("❌ F: drive not accessible")
                return False

            # Check component files
            component_files = [
                "ultimate_trading_system_v3.py",
                "jupiter_api_wrapper.py",
                "jupiter_rl_integration.py",
                "ultimate_trading_dashboard_v3.py",
                "deepseek_r1_trading_agent_enhanced.py"
            ]

            for file in component_files:
                if not os.path.exists(os.path.join(self.workspace_path, file)):
                    logger.error(f"❌ Component file missing: {file}")
                    return False
                logger.info(f"✅ {file} - Available")

            logger.info("✅ All dependencies checked successfully")
            return True

        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False

    async def launch_components(self):
        """Launch all system components"""
        try:
            logger.info("🚀 Launching system components...")

            # Start Ultimate AGI System V3 (if not already running)
            await self._launch_ultimate_agi_system()

            # Start Trading System V3
            await self._launch_trading_system()

            # Start Jupiter RL Integration
            await self._launch_jupiter_rl()

            # Start Trading Dashboard
            await self._launch_trading_dashboard()

            # Start monitoring and health checks
            await self._launch_system_monitor()

            logger.info("✅ All components launched successfully")

        except Exception as e:
            logger.error(f"Error launching components: {e}")
            logger.error(traceback.format_exc())
            raise

    async def _launch_ultimate_agi_system(self):
        """Launch Ultimate AGI System V3 if not already running"""
        try:
            logger.info("🧠 Checking Ultimate AGI System V3...")

            # Check if already running on port 8889
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8889))
            sock.close()

            if result == 0:
                logger.info("✅ Ultimate AGI System V3 already running on port 8889")
                self.status["components_status"]["ultimate_agi"] = "running"
                return

            # Launch Ultimate AGI System V3
            logger.info("🚀 Launching Ultimate AGI System V3...")

            # Try to import and run directly
            try:
                from src.core.ULTIMATE_AGI_SYSTEM_V3 import UltimateAGISystemV3
                agi_system = UltimateAGISystemV3()

                # Start in background
                async def run_agi():
                    await agi_system.start()

                asyncio.create_task(run_agi())

                # Wait a bit for startup
                await asyncio.sleep(5)

                # Check if it's running
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 8889))
                sock.close()

                if result == 0:
                    logger.info("✅ Ultimate AGI System V3 launched successfully")
                    self.status["components_status"]["ultimate_agi"] = "running"
                else:
                    logger.warning("⚠️ Ultimate AGI System V3 may not be fully started")
                    self.status["components_status"]["ultimate_agi"] = "starting"

            except Exception as e:
                logger.warning(f"Could not launch Ultimate AGI System V3 directly: {e}")
                self.status["components_status"]["ultimate_agi"] = "error"

        except Exception as e:
            logger.error(f"Error launching Ultimate AGI System: {e}")
            self.status["components_status"]["ultimate_agi"] = "error"

    async def _launch_trading_system(self):
        """Launch Ultimate Trading System V3"""
        try:
            logger.info("💰 Launching Ultimate Trading System V3...")

            from ultimate_trading_system_v3 import UltimateTradingSystemV3

            self.trading_system = UltimateTradingSystemV3()

            # Start in background
            async def run_trading():
                await self.trading_system.start()

            asyncio.create_task(run_trading())

            # Wait a bit for startup
            await asyncio.sleep(3)

            logger.info("✅ Ultimate Trading System V3 launched successfully")
            self.status["components_status"]["trading_system"] = "running"

        except Exception as e:
            logger.error(f"Error launching trading system: {e}")
            self.status["components_status"]["trading_system"] = "error"

    async def _launch_jupiter_rl(self):
        """Launch Jupiter RL Integration"""
        try:
            logger.info("🪐 Launching Jupiter RL Integration...")

            from jupiter_rl_integration import JupiterRLIntegration

            self.jupiter_rl = JupiterRLIntegration()

            # Test Jupiter RL with a sample analysis
            asyncio.create_task(self._test_jupiter_rl())

            logger.info("✅ Jupiter RL Integration launched successfully")
            self.status["components_status"]["jupiter_rl"] = "running"

        except Exception as e:
            logger.error(f"Error launching Jupiter RL: {e}")
            self.status["components_status"]["jupiter_rl"] = "error"

    async def _launch_trading_dashboard(self):
        """Launch Trading Dashboard"""
        try:
            logger.info("📊 Launching Ultimate Trading Dashboard V3...")

            from ultimate_trading_dashboard_v3 import UltimateTradingDashboard

            self.dashboard = UltimateTradingDashboard(port=8890)

            # Start in background
            async def run_dashboard():
                await self.dashboard.start()

            asyncio.create_task(run_dashboard())

            # Wait a bit for startup
            await asyncio.sleep(2)

            logger.info("✅ Ultimate Trading Dashboard V3 launched successfully")
            logger.info("🎯 Dashboard available at: http://localhost:8890")
            self.status["components_status"]["trading_dashboard"] = "running"

        except Exception as e:
            logger.error(f"Error launching trading dashboard: {e}")
            self.status["components_status"]["trading_dashboard"] = "error"

    async def _launch_system_monitor(self):
        """Launch system monitoring"""
        try:
            logger.info("📈 Launching system monitor...")

            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())

            logger.info("✅ System monitor launched successfully")
            self.status["components_status"]["system_monitor"] = "running"

        except Exception as e:
            logger.error(f"Error launching system monitor: {e}")
            self.status["components_status"]["system_monitor"] = "error"

    async def _test_jupiter_rl(self):
        """Test Jupiter RL integration"""
        try:
            await asyncio.sleep(5)  # Wait for system to stabilize

            logger.info("🧪 Testing Jupiter RL Integration...")

            # Test with SOL/USDC pair
            result = await self.jupiter_rl.analyze_trading_opportunity("SOL/USDC")

            if result and "error" not in result:
                logger.info("✅ Jupiter RL Integration test successful")
            else:
                logger.warning("⚠️ Jupiter RL Integration test returned errors")

        except Exception as e:
            logger.error(f"Error testing Jupiter RL: {e}")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds

                # Check system health
                await self._check_system_health()

                # Log system status
                await self._log_system_status()

                # Save status to file
                await self._save_status()

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _check_system_health(self):
        """Check health of all components"""
        try:
            # Check Ultimate AGI System
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 8889))
                sock.close()

                if result == 0:
                    self.status["components_status"]["ultimate_agi"] = "running"
                else:
                    self.status["components_status"]["ultimate_agi"] = "down"
            except:
                self.status["components_status"]["ultimate_agi"] = "error"

            # Check Trading Dashboard
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 8890))
                sock.close()

                if result == 0:
                    self.status["components_status"]["trading_dashboard"] = "running"
                else:
                    self.status["components_status"]["trading_dashboard"] = "down"
            except:
                self.status["components_status"]["trading_dashboard"] = "error"

            # Check other components
            for component in ["trading_system", "jupiter_rl", "system_monitor"]:
                if component not in self.status["components_status"]:
                    self.status["components_status"][component] = "unknown"

        except Exception as e:
            logger.error(f"Error checking system health: {e}")

    async def _log_system_status(self):
        """Log current system status"""
        try:
            running_components = sum(1 for status in self.status["components_status"].values()
                                   if status == "running")
            total_components = len(self.status["components_status"])

            logger.info(f"🔍 System Status: {running_components}/{total_components} components running")

            for component, status in self.status["components_status"].items():
                status_emoji = {
                    "running": "✅",
                    "starting": "🟡",
                    "down": "🔴",
                    "error": "❌",
                    "unknown": "⚪"
                }.get(status, "⚪")

                logger.info(f"   {status_emoji} {component}: {status}")

        except Exception as e:
            logger.error(f"Error logging system status: {e}")

    async def _save_status(self):
        """Save system status to file"""
        try:
            status_file = os.path.join(self.f_drive_path, "system_status.json")

            status_data = {
                **self.status,
                "last_update": datetime.now().isoformat(),
                "uptime": str(datetime.now() - self.status["start_time"]) if self.status["start_time"] else "0"
            }

            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving status: {e}")

    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            **self.status,
            "last_update": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.status["start_time"]) if self.status["start_time"] else "0"
        }

    async def start(self):
        """Start the complete system"""
        try:
            logger.info("🚀 Starting Ultimate Trading System V3...")
            logger.info("=" * 60)

            self.status["start_time"] = datetime.now()

            # Check dependencies
            if not await self.check_dependencies():
                logger.error("❌ Dependency check failed - cannot start system")
                return

            # Launch all components
            await self.launch_components()

            # Update status
            self.status["system_started"] = True

            # Display startup summary
            logger.info("=" * 60)
            logger.info("✅ Ultimate Trading System V3 Started Successfully!")
            logger.info("🎯 System Features:")
            logger.info("   • 🧠 Ultimate AGI System V3 (port 8889)")
            logger.info("   • 💰 Advanced Trading System with RL")
            logger.info("   • 🪐 Jupiter DEX Integration")
            logger.info("   • 📊 Real-time Trading Dashboard (port 8890)")
            logger.info("   • 🤖 DeepSeek R1 Trading Agent")
            logger.info("   • 📈 Performance Monitoring")
            logger.info("   • 🔄 WebSocket Live Updates")
            logger.info("=" * 60)
            logger.info("🌐 Access Points:")
            logger.info("   • Main AGI System: http://localhost:8889")
            logger.info("   • Trading Dashboard: http://localhost:8890")
            logger.info("   • System Logs: F:/ULTIMATE_AGI_DATA/RL_TRADING/")
            logger.info("=" * 60)

            # Keep the system running
            try:
                while True:
                    await asyncio.sleep(10)

                    # Check if we should continue running
                    if not self.status["system_started"]:
                        break

            except KeyboardInterrupt:
                logger.info("🛑 Received shutdown signal...")
                await self.shutdown()

        except Exception as e:
            logger.error(f"Error starting system: {e}")
            logger.error(traceback.format_exc())
            self.status["errors"].append(str(e))

    async def shutdown(self):
        """Shutdown the system gracefully"""
        try:
            logger.info("🛑 Shutting down Ultimate Trading System V3...")

            # Stop all components
            if hasattr(self, 'trading_system'):
                await self.trading_system.stop()

            # Update status
            self.status["system_started"] = False
            await self._save_status()

            logger.info("✅ System shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Main execution
async def main():
    """Main execution function"""
    launcher = UltimateTradingSystemLauncher()

    try:
        await launcher.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        await launcher.shutdown()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    print("🚀 Ultimate Trading System V3 Launcher")
    print("=" * 50)
    print("Starting all components...")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    asyncio.run(main())
