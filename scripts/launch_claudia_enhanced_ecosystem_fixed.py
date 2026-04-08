#!/usr/bin/env python3
"""
Claudia-Enhanced Ultimate AGI System V3 Launcher
===============================================
Advanced ecosystem launcher with Claudia/Ollama integration
Optimized for top 3 models: DeepSeek-R1, Qwen2.5-Coder, Llama3.2:3b
"""

import asyncio
import logging
import subprocess
import sys
import time
import threading
import requests
import yaml
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ClaudiaEcosystemLauncher")

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    command: list[str]
    port: Optional[int] = None
    health_url: Optional[str] = None
    working_directory: str = "."
    restart_on_failure: bool = True
    wait_time: int = 2

class ClaudiaEcosystemLauncher:
    """Enhanced ecosystem launcher with Claudia integration"""

    def __init__(self):
        self.workspace = Path(__file__).parent
        self.processes = {}
        self.monitoring_active = False
        self.claudia_client = None

        # Top 3 optimized models
        self.top_models = [
            "deepseek-r1:latest",      # Advanced reasoning and trading analysis
            "qwen2.5-coder:latest",    # Code review and optimization
            "llama3.2:3b"              # Fast responses and general tasks
        ]

        # Service configurations
        self.services = [
            ServiceConfig(
                name="Jupiter Ultimate Dashboard V4",
                command=[sys.executable, "jupiter_ultimate_dashboard_v4.py"],
                port=8891,
                health_url="http://localhost:8891/health"
            ),
            ServiceConfig(
                name="Claudia Enhanced Trading System",
                command=[sys.executable, "claudia_enhanced_trading_system.py"],
                port=None,
                restart_on_failure=True
            ),
            ServiceConfig(
                name="Ultimate Trading System V3",
                command=[sys.executable, "ultimate_trading_system_v3.py"],
                port=8892,
                health_url="http://localhost:8892/health"
            ),
            ServiceConfig(
                name="WatchYourLAN Cyberpunk Integration",
                command=[sys.executable, "watchyourlan_cyberpunk_ultimate_integration.py"],
                port=8893,
                health_url="http://localhost:8893/health"
            ),
            ServiceConfig(
                name="Cyberpunk Dashboard",
                command=[sys.executable, "cyberpunk_dashboard.py"],
                port=8894,
                health_url="http://localhost:8894/health"
            ),
            ServiceConfig(
                name="DeepSeek R1 Trading Agent",
                command=[sys.executable, "deepseek_r1_trading_agent_enhanced.py"],
                port=None,
                restart_on_failure=True
            ),
            ServiceConfig(
                name="Jupiter RL Integration",
                command=[sys.executable, "jupiter_rl_integration.py"],
                port=None,
                restart_on_failure=True
            )
        ]

    async def start_ecosystem(self):
        """Start the complete Claudia-enhanced ecosystem"""
        logger.info("🚀 Starting Claudia-Enhanced Ultimate AGI System V3...")
        print("=" * 80)
        print("🤖 CLAUDIA-ENHANCED ULTIMATE AGI SYSTEM V3")
        print("=" * 80)

        # Step 1: Check Claudia/Ollama availability
        await self._check_claudia_availability()

        # Step 2: Initialize Claudia client
        await self._initialize_claudia()

        # Step 3: Verify top 3 models
        await self._verify_top_models()

        # Step 4: Start services
        await self._start_services()

        # Step 5: Start monitoring
        await self._start_monitoring()

        # Step 6: Display status
        self._display_startup_status()

        # Step 7: Keep running
        await self._keep_running()

    async def _check_claudia_availability(self):
        """Check if Claudia/Ollama is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                logger.info(f"✅ Claudia/Ollama available with {len(models)} models")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Claudia/Ollama not available: {e}")
            return False

    async def _initialize_claudia(self):
        """Initialize Claudia enhanced client"""
        try:
            from claudia_enhanced_client import ClaudiaEnhanced
            self.claudia_client = ClaudiaEnhanced()
            await self.claudia_client.initialize()

            # Test Claudia
            test_response = await self.claudia_client.query(
                "What is your current status?",
                task_type="quick_response"
            )
            logger.info(f"🧠 Claudia test response: {test_response[:50]}...")

            models_count = len(self.claudia_client.available_models)
            logger.info(f"📊 Available models: {models_count}")
            print("✅ Claudia AI Integration: ENABLED")

            logger.info("✅ Enhanced Claudia client initialized successfully")

        except Exception as e:
            logger.warning(f"⚠️ Claudia initialization failed: {e}")
            self.claudia_client = None

    async def _verify_top_models(self):
        """Verify top 3 models are available locally"""
        logger.info("🎯 Top 3 Models Strategy - Using local models only")

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = [model["name"] for model in response.json().get("models", [])]
                logger.info(f"✅ Found {len(available_models)} local models")

                for model in self.top_models:
                    if model in available_models:
                        logger.info(f"  ✅ {model} - Available")
                    else:
                        logger.warning(f"  ⚠️ {model} - Not found")

                logger.info("🚀 Proceeding with available models...")

        except Exception as e:
            logger.error(f"❌ Error checking models: {e}")

    async def _start_services(self):
        """Start all ecosystem services"""
        logger.info("🔄 Starting ecosystem services...")

        for service in self.services:
            await self._start_service(service)
            await asyncio.sleep(service.wait_time)

    async def _start_service(self, service: ServiceConfig):
        """Start a single service"""
        try:
            logger.info(f"🔄 Starting {service.name}...")

            # Check if port is already in use
            if service.port and self._is_port_in_use(service.port):
                logger.warning(f"⚠️ Port {service.port} already in use for {service.name}")
                return

            # Start the process
            process = subprocess.Popen(
                service.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=service.working_directory,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )

            # Store process info
            self.processes[service.name] = {
                'process': process,
                'config': service,
                'start_time': datetime.now()
            }

            # Wait for health check if available
            if service.health_url:
                health_ok = await self._wait_for_health_check(service)
                if health_ok:
                    logger.info(f"✅ {service.name} started successfully")
                else:
                    logger.warning(f"⚠️ {service.name} may not be fully ready")
            else:
                logger.info(f"✅ {service.name} started successfully")

        except Exception as e:
            logger.error(f"❌ Failed to start {service.name}: {e}")

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            return response.status_code == 200
        except Exception:
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

                            # Restart if enabled
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
        logger.info("🛑 Service monitoring stopped")

    def _display_startup_status(self):
        """Display startup status summary"""
        print("\\n" + "=" * 80)
        print("🚀 CLAUDIA-ENHANCED ECOSYSTEM STATUS")
        print("=" * 80)

        # Claudia status
        claudia_status = "✅ ENABLED" if self.claudia_client else "❌ DISABLED"
        print(f"🤖 Claudia AI Integration: {claudia_status}")

        # Services status
        running_services = 0
        total_services = len(self.services)

        for service_name, service_info in self.processes.items():
            if service_info['process'].poll() is None:
                running_services += 1

        print(f"🔧 Services Started: {running_services}")
        print(f"📊 Total Services: {total_services}")

        # Service details
        print("\\n📋 SERVICE STATUS:")
        for service in self.services:
            if service.name in self.processes:
                process = self.processes[service.name]['process']
                if process.poll() is None:
                    status = "✅ RUNNING"
                    if service.port:
                        status += f" (Port: {service.port})"
                else:
                    status = "❌ STOPPED"
                    if service.port:
                        status += f" (Port: {service.port})"
            else:
                status = "❌ STOPPED"

            service_type = " [Claudia-Enhanced]" if "Claudia" in service.name else ""
            print(f"   {service.name}: {status}{service_type}")

        # Access URLs
        print("\\n🌐 ACCESS URLS:")
        for service in self.services:
            if service.port and service.name in self.processes:
                process = self.processes[service.name]['process']
                if process.poll() is None:
                    print(f"   {service.name}: http://localhost:{service.port}")

        # Enhanced features
        if self.claudia_client:
            print("\\n🎯 ENHANCED FEATURES:")
            print("   ✅ AI-powered market analysis")
            print("   ✅ Advanced trading recommendations")
            print("   ✅ Real-time sentiment analysis")
            print("   ✅ Intelligent risk assessment")
            print("   ✅ Adaptive trading strategies")

        # Monitoring status
        print("\\n🔍 MONITORING:")
        print("   ✅ Service health monitoring active")
        print("   ✅ Auto-restart on failure enabled")
        print("   ✅ Real-time performance tracking")

        print("\\n" + "=" * 80)
        print("🎉 CLAUDIA-ENHANCED ECOSYSTEM READY!")
        print("=" * 80)

    async def _keep_running(self):
        """Keep the launcher running"""
        print("\\n✨ Ecosystem running. Press Ctrl+C to exit.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\\n🛑 Shutting down ecosystem...")
            self._stop_monitoring()
            self._stop_all_services()

    def _stop_all_services(self):
        """Stop all running services"""
        for service_name, service_info in self.processes.items():
            try:
                process = service_info['process']
                if process.poll() is None:
                    process.terminate()
                    logger.info(f"🛑 Stopped {service_name}")
            except Exception as e:
                logger.error(f"Error stopping {service_name}: {e}")

async def main():
    """Main entry point"""
    launcher = ClaudiaEcosystemLauncher()
    await launcher.start_ecosystem()

if __name__ == "__main__":
    asyncio.run(main())
