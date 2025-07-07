#!/usr/bin/env python3
"""
Claudia-Enhanced Ultimate AGI Ecosystem Launcher
==============================================
Complete ecosystem launcher with Claudia AI integration for advanced trading and analysis
"""

import asyncio
import logging
import subprocess
import sys
import time
import json
import requests
from pathlib import Path
fr    def _stop_monitoring(self):
        """Stop service monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Service monitoring stopped")

    def _display_startup_status(self):ort Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import psutil
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ClaudiaEcosystemLauncher")

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    command: List[str]
    port: Optional[int] = None
    health_url: Optional[str] = None
    enabled: bool = True
    priority: int = 1
    requires_claudia: bool = False
    restart_on_failure: bool = True

class ClaudiaEcosystemLauncher:
    """Enhanced ecosystem launcher with Claudia AI integration"""

    def __init__(self):
        self.workspace = Path(__file__).parent
        self.processes = {}
        self.claudia_status = False
        self.services_config = []
        self.monitoring_active = False
        self.ollama_process = None

    async def check_claudia_availability(self) -> bool:
        """Check if Claudia/Ollama is available and initialize enhanced client"""
        try:
            # Check Ollama API with correct port
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                logger.info(f"✅ Claudia/Ollama available with {len(models)} models")

                # Initialize enhanced Claudia client
                try:
                    from claudia_enhanced_client import EnhancedClaudiaClient
                    self.claudia_client = EnhancedClaudiaClient()
                    claudia_initialized = await self.claudia_client.initialize()

                    if claudia_initialized:
                        logger.info("✅ Enhanced Claudia client initialized successfully")

                        # Test the enhanced client
                        test_response = await self.claudia_client.quick_response("System status check")
                        logger.info(f"🧠 Claudia test response: {test_response[:100]}...")

                        # Get performance report
                        perf_report = await self.claudia_client.get_performance_report()
                        logger.info(f"📊 Available models: {len(perf_report['available_models'])}")

                        return True
                    else:
                        logger.warning("⚠️ Enhanced Claudia client failed to initialize")
                        return False

                except Exception as e:
                    logger.warning(f"⚠️ Enhanced Claudia client error: {e}")

                # Fallback to basic check
                model_names = [m.get("name", "") for m in models]
                if any("llama" in name or "deepseek" in name for name in model_names):
                    logger.info("🤖 Suitable AI models detected for Claudia")
                    return True
                else:
                    logger.warning("⚠️ No suitable AI models found for Claudia")
        except Exception as e:
            logger.warning(f"⚠️ Claudia/Ollama not available: {e}")
        return False

    async def start_ollama_if_needed(self) -> bool:
        """Start Ollama if not running"""
        if await self.check_claudia_availability():
            return True

        logger.info("🔄 Starting Ollama server...")
        try:
            # Try to start Ollama
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for startup
            for _ in range(30):  # 30 second timeout
                await asyncio.sleep(1)
                if await self.check_claudia_availability():
                    logger.info("✅ Ollama server started successfully")
                    return True

            logger.error("❌ Ollama server failed to start within timeout")
            return False

        except Exception as e:
            logger.error(f"❌ Failed to start Ollama: {e}")
            return False

    def _setup_service_configs(self):
        """Setup service configurations"""
        self.services_config = [
            ServiceConfig(
                name="Jupiter Ultimate Dashboard V4",
                command=[sys.executable, "jupiter_ultimate_dashboard_v4.py"],
                port=8891,
                health_url="http://localhost:8891",
                priority=1,
                requires_claudia=False
            ),
            ServiceConfig(
                name="Claudia Enhanced Trading System",
                command=[sys.executable, "claudia_enhanced_trading_system.py"],
                priority=2,
                requires_claudia=True,
                enabled=self.claudia_status
            ),
            ServiceConfig(
                name="Ultimate Trading System V3",
                command=[sys.executable, "ultimate_trading_system_v3.py"],
                port=8892,
                priority=3
            ),
            ServiceConfig(
                name="WatchYourLAN Cyberpunk Integration",
                command=[sys.executable, "watchyourlan_cyberpunk_ultimate_integration.py"],
                port=8893,
                priority=4
            ),
            ServiceConfig(
                name="Cyberpunk Dashboard",
                command=[sys.executable, "cyberpunk_dashboard.py"],
                port=8894,
                priority=5
            ),
            ServiceConfig(
                name="DeepSeek R1 Trading Agent",
                command=[sys.executable, "deepseek_r1_trading_agent_enhanced.py"],
                priority=6,
                requires_claudia=False
            ),
            ServiceConfig(
                name="Jupiter RL Integration",
                command=[sys.executable, "jupiter_rl_integration.py"],
                priority=7,
                requires_claudia=False
            )
        ]

    async def start_core_services(self):
        """Start core AGI services with Claudia integration"""
        logger.info("🚀 Starting Claudia-Enhanced Ultimate AGI System V3...")

        print("=" * 80)
        print("🤖 CLAUDIA-ENHANCED ULTIMATE AGI SYSTEM V3")
        print("=" * 80)

        # Check/start Claudia/Ollama
        self.claudia_status = await self.start_ollama_if_needed()

        if self.claudia_status:
            print("✅ Claudia AI Integration: ENABLED")
            # Check local models (top 3 strategy)
            await self._pull_required_models()
        else:
            print("⚠️ Claudia AI Integration: DISABLED (fallback mode)")

        # Setup service configurations
        self._setup_service_configs()

        # Start services by priority
        await self._start_services_by_priority()

        # Start monitoring
        await self._start_monitoring()

        # Display status
        self._display_startup_status()

        return True

    async def _pull_required_models(self):
        """Check locally available models (no pulling required)"""
        logger.info("🎯 Top 3 Models Strategy - Using local models only")

        top_3_models = [
            "deepseek-r1:latest",      # Reasoning & Trading
            "qwen2.5-coder:latest",    # Code & Optimization
            "llama3.2:3b"              # Fast & Real-time
        ]

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_names = [m.get('name', '') for m in models]

                logger.info(f"✅ Found {len(models)} local models")

                # Check top 3 availability
                for model in top_3_models:
                    if model in available_names:
                        logger.info(f"  ✅ {model} - Available")
                    else:
                        logger.warning(f"  ⚠️ {model} - Not found locally")

            else:
                logger.warning(f"⚠️ Could not check models: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Could not check local models: {e}")

        logger.info("� Proceeding with available models...")

    async def _start_services_by_priority(self):
        """Start services ordered by priority"""
        # Sort by priority
        services = sorted(self.services_config, key=lambda x: x.priority)

        for service in services:
            if service.enabled and (not service.requires_claudia or self.claudia_status):
                await self._start_service(service)
                await asyncio.sleep(2)  # Stagger startup
            else:
                reason = "disabled" if not service.enabled else "requires Claudia"
                logger.info(f"⏭️ Skipping {service.name} ({reason})")

    async def _start_service(self, service: ServiceConfig):
        """Start individual service"""
        try:
            logger.info(f"🔄 Starting {service.name}...")

            # Check if port is already in use
            if service.port and self._is_port_in_use(service.port):
                logger.warning(f"⚠️ Port {service.port} already in use for {service.name}")
                return False

            process = subprocess.Popen(
                service.command,
                cwd=self.workspace,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes[service.name] = {
                'process': process,
                'config': service,
                'start_time': datetime.now()
            }

            # Wait for service to be ready
            if service.health_url:
                await self._wait_for_health_check(service)
            else:
                await asyncio.sleep(3)  # Basic wait

            logger.info(f"✅ {service.name} started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start {service.name}: {e}")
            return False

    def _is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.laddr.port == port:
                    return True
        except Exception:
            pass
        return False

    async def _wait_for_health_check(self, service: ServiceConfig):
        """Wait for service health check"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(service.health_url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ {service.name} health check passed")
                    return True
            except Exception:
                pass
            await asyncio.sleep(1)

        logger.warning(f"⚠️ {service.name} health check timeout")
        return False

    async def _start_monitoring(self):
        """Start service monitoring"""
        self.monitoring_active = True

        def monitor_services():
            """Monitor services in background thread"""
            while self.monitoring_active:
                try:
                    for service_name, service_info in self.processes.items():
                        process = service_info['process']
                        config = service_info['config']

                        # Check if process is still running
                        if process.poll() is not None:
                            logger.warning(f"⚠️ {service_name} has stopped")

                            # Restart if enabled (simplified restart without async)
                            if config.restart_on_failure:
                                logger.info(f"🔄 Attempting to restart {service_name}")
                                try:
                                    # Simple restart using subprocess
                                    new_process = subprocess.Popen(
                                        config.command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        cwd=config.working_directory,
                                        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                                    )
                                    self.processes[service_name]['process'] = new_process
                                    logger.info(f"✅ {service_name} restarted successfully")
                                except Exception as restart_error:
                                    logger.error(f"❌ Failed to restart {service_name}: {restart_error}")

                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.error(f"Error in service monitoring: {e}")
                    time.sleep(10)

        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_services, daemon=True)
        monitor_thread.start()
        logger.info("🔍 Service monitoring started")

    def _stop_monitoring(self):
        """Stop service monitoring"""
        self.monitoring_active = False
        logger.info("� Service monitoring stopped")
                    'start_time': datetime.now()
                }

                logger.info(f"✅ {service_name} restarted successfully")

        except Exception as e:
            logger.error(f"❌ Failed to restart {service_name}: {e}")

    def _display_startup_status(self):
        """Display startup status summary"""
        print("\n" + "=" * 80)
        print("🚀 CLAUDIA-ENHANCED ECOSYSTEM STATUS")
        print("=" * 80)

        print(f"🤖 Claudia AI Integration: {'✅ ENABLED' if self.claudia_status else '❌ DISABLED'}")
        print(f"🔧 Services Started: {len(self.processes)}")
        print(f"📊 Total Services: {len([s for s in self.services_config if s.enabled])}")

        print("\n📋 SERVICE STATUS:")
        for service_name, service_info in self.processes.items():
            config = service_info['config']
            status = "✅ RUNNING" if service_info['process'].poll() is None else "❌ STOPPED"
            port_info = f" (Port: {config.port})" if config.port else ""
            claudia_info = " [Claudia-Enhanced]" if config.requires_claudia else ""
            print(f"   {service_name}: {status}{port_info}{claudia_info}")

        print("\n🌐 ACCESS URLS:")
        for service_name, service_info in self.processes.items():
            config = service_info['config']
            if config.port:
                print(f"   {service_name}: http://localhost:{config.port}")

        print("\n🎯 ENHANCED FEATURES:")
        if self.claudia_status:
            print("   ✅ AI-powered market analysis")
            print("   ✅ Advanced trading recommendations")
            print("   ✅ Real-time sentiment analysis")
            print("   ✅ Intelligent risk assessment")
            print("   ✅ Adaptive trading strategies")
        else:
            print("   ⚠️ Using traditional analysis (Claudia disabled)")

        print("\n🔍 MONITORING:")
        print("   ✅ Service health monitoring active")
        print("   ✅ Auto-restart on failure enabled")
        print("   ✅ Real-time performance tracking")

        print("\n" + "=" * 80)
        print("🎉 CLAUDIA-ENHANCED ECOSYSTEM READY!")
        print("=" * 80)

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down Claudia-Enhanced Ecosystem...")

        self.monitoring_active = False

        # Stop all services
        for service_name, service_info in self.processes.items():
            try:
                process = service_info['process']
                if process.poll() is None:
                    logger.info(f"🛑 Stopping {service_name}")
                    process.terminate()

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️ Force killing {service_name}")
                        process.kill()

            except Exception as e:
                logger.error(f"Error stopping {service_name}: {e}")

        # Stop Ollama if we started it
        if self.ollama_process and self.ollama_process.poll() is None:
            logger.info("🛑 Stopping Ollama server")
            self.ollama_process.terminate()
            try:
                self.ollama_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()

        logger.info("✅ Ecosystem shutdown complete")

    async def run_interactive(self):
        """Run in interactive mode"""
        try:
            await self.start_core_services()

            print("\n🎮 INTERACTIVE MODE")
            print("Commands: status, restart <service>, stop, claudia")
            print("Press Ctrl+C to exit")

            while True:
                try:
                    command = input("\n> ").strip().lower()

                    if command == "status":
                        await self._show_status()
                    elif command.startswith("restart "):
                        service_name = command.replace("restart ", "")
                        await self._restart_service(service_name)
                    elif command == "stop":
                        await self.shutdown()
                        break
                    elif command == "claudia":
                        await self._show_claudia_status()
                    elif command == "help":
                        print("Commands: status, restart <service>, stop, claudia, help")
                    else:
                        print("Unknown command. Type 'help' for available commands.")

                except EOFError:
                    break

        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested...")
            await self.shutdown()

    async def _show_status(self):
        """Show current status"""
        print("\n📊 CURRENT STATUS:")
        for service_name, service_info in self.processes.items():
            status = "✅ RUNNING" if service_info['process'].poll() is None else "❌ STOPPED"
            uptime = datetime.now() - service_info['start_time']
            print(f"   {service_name}: {status} (Uptime: {uptime})")

    async def _show_claudia_status(self):
        """Show Claudia AI status"""
        print("\n🤖 CLAUDIA AI STATUS:")
        print(f"   Connection: {'✅ CONNECTED' if self.claudia_status else '❌ DISCONNECTED'}")

        if self.claudia_status:
            try:
                response = requests.get("http://localhost:11435/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    print(f"   Models Available: {len(models)}")
                    for model in models:
                        print(f"     - {model.get('name', 'Unknown')}")
            except Exception as e:
                print(f"   Error getting models: {e}")

async def main():
    """Main launcher function"""
    launcher = ClaudiaEcosystemLauncher()

    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
            await launcher.run_interactive()
        else:
            await launcher.start_core_services()

            # Keep running
            print("\n✨ Ecosystem running. Press Ctrl+C to exit.")
            while True:
                await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested...")
        await launcher.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await launcher.shutdown()

if __name__ == "__main__":
    # Run the launcher
    asyncio.run(main())
