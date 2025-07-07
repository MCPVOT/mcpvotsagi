#!/usr/bin/env python3
"""
Working Services Launcher
=========================
Launch only the services that actually work with proper error handling
"""

import asyncio
import subprocess
import time
import logging
import requests
import socket
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkingServicesLauncher")

class WorkingServicesLauncher:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.services = {}

    def check_port(self, port):
        """Check if a port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def check_service_health(self, url, timeout=5):
        """Check if a service is responding"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code < 500
        except Exception:
            return False

    def start_service(self, name, script_name, port):
        """Start a service and verify it's running"""
        logger.info(f"🔄 Starting {name}...")

        # Check if port is already in use
        if self.check_port(port):
            logger.warning(f"⚠️ Port {port} already in use for {name}")
            return None

        try:
            # Start the service
            process = subprocess.Popen([
                'python', script_name
            ], cwd=self.base_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait a moment for startup
            time.sleep(3)

            # Check if service is responding
            if self.check_port(port):
                logger.info(f"✅ {name} started successfully on port {port}")
                return process
            else:
                logger.error(f"❌ {name} failed to start on port {port}")
                process.terminate()
                return None

        except Exception as e:
            logger.error(f"❌ Error starting {name}: {e}")
            return None

    def start_web_service(self, name, script_name, port, health_url):
        """Start a web service with health check"""
        process = self.start_service(name, script_name, port)
        if process:
            # Additional health check for web services
            time.sleep(2)
            if self.check_service_health(health_url):
                logger.info(f"✅ {name} health check passed")
                return process
            else:
                logger.warning(f"⚠️ {name} started but health check failed")
                return process
        return None

    async def launch_ecosystem(self):
        """Launch the working ecosystem services"""
        logger.info("🚀 Starting Working Claudia-Enhanced Ecosystem...")

        print("=" * 80)
        print("🤖 WORKING CLAUDIA-ENHANCED ULTIMATE AGI SYSTEM V3")
        print("=" * 80)

        # Check Ollama availability
        if self.check_service_health("http://localhost:11434/api/tags"):
            logger.info("✅ Ollama API available")
            try:
                response = requests.get("http://localhost:11434/api/tags")
                models = response.json().get("models", [])
                logger.info(f"🧠 {len(models)} models available")
            except Exception as e:
                logger.warning(f"⚠️ Could not get model count: {e}")
        else:
            logger.warning("⚠️ Ollama API not available")

        # Service definitions
        services_to_start = [
            {
                "name": "Ultimate Trading System V3",
                "script": "ultimate_trading_system_v3.py",
                "port": 8892,
                "type": "service"
            },
            {
                "name": "Jupiter RL Integration",
                "script": "jupiter_rl_integration.py",
                "port": 8895,
                "type": "service"
            },
            {
                "name": "DeepSeek R1 Trading Agent",
                "script": "deepseek_r1_trading_agent_enhanced.py",
                "port": 8896,
                "type": "service"
            }
        ]

        started_services = 0

        for service_config in services_to_start:
            name = service_config["name"]
            script = service_config["script"]
            port = service_config["port"]

            # Check if script exists
            script_path = self.base_path / script
            if not script_path.exists():
                logger.warning(f"⚠️ Script not found: {script}")
                continue

            # Start the service
            process = self.start_service(name, script, port)
            if process:
                self.services[name] = {
                    "process": process,
                    "port": port,
                    "script": script
                }
                started_services += 1

            # Small delay between services
            time.sleep(1)

        # Display status
        self.display_status(started_services)

        # Keep running and monitor
        try:
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                self.monitor_services()
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down services...")
            self.shutdown_services()

    def monitor_services(self):
        """Monitor running services"""
        for name, service_info in self.services.items():
            process = service_info["process"]
            port = service_info["port"]

            # Check if process is still running
            if process.poll() is not None:
                logger.warning(f"⚠️ {name} has stopped")
                # Could implement restart logic here
            elif not self.check_port(port):
                logger.warning(f"⚠️ {name} port {port} not responding")

    def display_status(self, started_services):
        """Display ecosystem status"""
        print(f"\n✅ Started {started_services}/{len(self.services)} services")

        print("\n" + "=" * 80)
        print("🚀 WORKING ECOSYSTEM STATUS")
        print("=" * 80)
        print(f"🤖 Claudia AI Integration: ✅ ENABLED")
        print(f"🔧 Services Running: {len(self.services)}")

        print(f"\n📋 SERVICE STATUS:")

        # Check Jupiter Dashboard (external)
        if self.check_port(8891):
            print(f"   Jupiter Ultimate Dashboard V4: ✅ RUNNING (Port: 8891)")
            print(f"   🌐 Access: http://localhost:8891")

        # Check our services
        for name, service_info in self.services.items():
            port = service_info["port"]
            status = "✅ RUNNING" if self.check_port(port) else "❌ STOPPED"
            print(f"   {name}: {status} (Port: {port})")
            if status == "✅ RUNNING":
                print(f"   🌐 Access: http://localhost:{port}")

        # Check Ollama
        if self.check_port(11434):
            print(f"   Ollama API: ✅ RUNNING (Port: 11434)")

        print(f"\n✨ Working ecosystem running. Press Ctrl+C to exit.")
        print("=" * 80)

    def shutdown_services(self):
        """Shutdown all services"""
        for name, service_info in self.services.items():
            process = service_info["process"]
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} shutdown successfully")
            except Exception as e:
                logger.error(f"❌ Error shutting down {name}: {e}")
                process.kill()

async def main():
    launcher = WorkingServicesLauncher()
    await launcher.launch_ecosystem()

if __name__ == "__main__":
    asyncio.run(main())
