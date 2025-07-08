#!/usr/bin/env python3
"""
Simple Ecosystem Launcher
========================

A simple script to launch the core MCPVotsAGI ecosystem services.

Author: MCPVotsAGI Team
Date: January 2025
Version: 1.0.0
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleEcosystemLauncher:
    """Simple launcher for core ecosystem services"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.services = [
            {
                "name": "DGM Evolution Connector",
                "script": "services/dgm_evolution_connector.py",
                "port": 8003,
                "required": True
            },
            {
                "name": "DGM Trading V2",
                "script": "src/trading/dgm_trading_algorithms_v2.py",
                "port": 8004,
                "required": True
            },
            {
                "name": "Ecosystem Manager",
                "script": "services/ecosystem_manager.py",
                "port": 8001,
                "required": False
            }
        ]
        self.processes = []

    def check_service_file(self, script_path: str) -> bool:
        """Check if service file exists"""
        full_path = self.project_root / script_path
        exists = full_path.exists()

        if exists:
            logger.info(f"✅ Found service file: {script_path}")
        else:
            logger.error(f"❌ Missing service file: {script_path}")

        return exists

    def start_service(self, service: dict) -> bool:
        """Start a single service"""
        script_path = self.project_root / service["script"]

        if not script_path.exists():
            logger.error(f"❌ Cannot start {service['name']}: File not found")
            return False

        try:
            logger.info(f"🚀 Starting {service['name']} on port {service['port']}...")

            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.processes.append({
                "name": service["name"],
                "process": process,
                "port": service["port"]
            })

            logger.info(f"✅ Started {service['name']} (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start {service['name']}: {e}")
            return False

    def check_service_health(self, port: int, service_name: str) -> bool:
        """Check if service is responding on its port"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result == 0:
                logger.info(f"✅ {service_name} is responding on port {port}")
                return True
            else:
                logger.warning(f"⚠️  {service_name} not responding on port {port}")
                return False

        except Exception as e:
            logger.error(f"❌ Health check failed for {service_name}: {e}")
            return False

    def launch_ecosystem(self):
        """Launch the ecosystem services"""
        logger.info("🚀 Starting MCPVotsAGI Simple Ecosystem Launcher")
        logger.info("=" * 60)

        # Check all service files first
        logger.info("🔍 Checking service files...")
        missing_files = []
        for service in self.services:
            if not self.check_service_file(service["script"]):
                missing_files.append(service["script"])

        if missing_files:
            logger.error(f"❌ Missing {len(missing_files)} service files. Cannot continue.")
            return False

        # Start services
        logger.info("🚀 Starting services...")
        started_services = 0

        for service in self.services:
            if self.start_service(service):
                started_services += 1
                # Wait between service starts
                time.sleep(2)
            elif service["required"]:
                logger.error(f"❌ Required service {service['name']} failed to start")
                return False

        if started_services == 0:
            logger.error("❌ No services started successfully")
            return False

        # Wait for services to initialize
        logger.info("⏳ Waiting for services to initialize...")
        time.sleep(10)

        # Check service health
        logger.info("🏥 Checking service health...")
        healthy_services = 0

        for service in self.services:
            if self.check_service_health(service["port"], service["name"]):
                healthy_services += 1

        # Print summary
        logger.info("=" * 60)
        logger.info("📊 ECOSYSTEM LAUNCH SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Services Started: {started_services}/{len(self.services)}")
        logger.info(f"Services Healthy: {healthy_services}/{len(self.services)}")

        if healthy_services >= len([s for s in self.services if s["required"]]):
            logger.info("🎉 ECOSYSTEM LAUNCH: SUCCESS!")
            logger.info("💡 Ecosystem is running. Press Ctrl+C to stop all services.")
            return True
        else:
            logger.error("❌ ECOSYSTEM LAUNCH: FAILED!")
            return False

    def stop_all_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping all services...")

        for service_info in self.processes:
            try:
                service_info["process"].terminate()
                service_info["process"].wait(timeout=5)
                logger.info(f"✅ Stopped {service_info['name']}")
            except Exception as e:
                logger.error(f"❌ Error stopping {service_info['name']}: {e}")
                try:
                    service_info["process"].kill()
                except:
                    pass

    def run(self):
        """Run the launcher with proper cleanup"""
        try:
            success = self.launch_ecosystem()

            if success:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            else:
                logger.error("❌ Ecosystem launch failed")
                return False

        except KeyboardInterrupt:
            logger.info("👋 Received interrupt signal. Shutting down...")
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
        finally:
            self.stop_all_services()

        return True

def main():
    """Main entry point"""
    launcher = SimpleEcosystemLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
