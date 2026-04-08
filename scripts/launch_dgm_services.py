#!/usr/bin/env python3
"""
DGM Services Launcher & Health Monitor
=====================================
Launches all DGM services and monitors their health status
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
import aiohttp
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DGMServiceLauncher")

class DGMServiceLauncher:
    def __init__(self, config_path: str = "dgm_config.json"):
        self.config_path = Path(config_path)
        self.project_root = Path.cwd()
        self.running_processes = {}
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load DGM configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Configuration loaded: {len(config.get('components', []))} components")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return {"components": []}

    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return False
        return True

    def kill_port_processes(self, port: int):
        """Kill processes using a specific port"""
        killed = False
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        proc = psutil.Process(conn.pid)
                        logger.warning(f"🔴 Killing process {conn.pid} ({proc.name()}) using port {port}")
                        proc.kill()
                        killed = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            logger.warning(f"⚠️ Error checking port {port}: {e}")

        if killed:
            time.sleep(2)  # Wait for cleanup

    def start_service(self, component: Dict) -> [subprocess.Popen]:
        """Start a DGM service component"""
        name = component['name']
        file_path = component.get('file_path', f"{name}.py")
        port = component['metadata']['port']

        # Check if file exists
        full_path = self.project_root / file_path
        if not full_path.exists():
            logger.error(f"❌ Service file not found: {full_path}")
            return None

        # Kill existing processes on the port
        if not self.check_port_available(port):
            logger.warning(f"⚠️ Port {port} is busy, cleaning up...")
            self.kill_port_processes(port)

        try:
            # Start the service
            cmd = [sys.executable, str(full_path)]
            logger.info(f"🚀 Starting {name} on port {port}: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_root,
                text=True
            )

            self.running_processes[name] = {
                'process': process,
                'port': port,
                'file_path': file_path,
                'start_time': time.time()
            }

            logger.info(f"✅ {name} started with PID {process.pid}")
            return process

        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return None

    async def check_service_health(self, component: Dict) -> bool:
        """Check if a service is healthy"""
        health_url = component.get('health_check_url')
        if not health_url:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception:
            return False

    async def wait_for_service_ready(self, component: Dict, timeout: int = 30) -> bool:
        """Wait for service to be ready"""
        name = component['name']
        start_time = time.time()

        while time.time() - start_time < timeout:
            if await self.check_service_health(component):
                logger.info(f"✅ {name} is ready and healthy")
                return True

            # Check if process is still running
            if name in self.running_processes:
                process = self.running_processes[name]['process']
                if process.poll() is not None:
                    logger.error(f"❌ {name} process died unexpectedly")
                    return False

            await asyncio.sleep(2)

        logger.warning(f"⚠️ {name} not ready after {timeout}s")
        return False

    async def start_all_services(self):
        """Start all DGM services"""
        components = self.config.get('components', [])
        logger.info(f"🎯 Starting {len(components)} DGM services...")

        # Start services in dependency order
        for component in components:
            name = component['name']
            logger.info(f"\n🔧 Processing {name}...")

            # Start the service
            process = self.start_service(component)
            if process:
                # Wait for it to be ready
                await self.wait_for_service_ready(component)
            else:
                logger.error(f"❌ Failed to start {name}")

    def get_service_status(self) -> dict:
        """Get status of all running services"""
        status = {}

        for name, info in self.running_processes.items():
            process = info['process']
            is_running = process.poll() is None

            status[name] = {
                'running': is_running,
                'pid': process.pid if is_running else None,
                'port': info['port'],
                'uptime': time.time() - info['start_time'] if is_running else 0,
                'file_path': info['file_path']
            }

        return status

    def stop_all_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping all DGM services...")

        for name, info in self.running_processes.items():
            try:
                process = info['process']
                if process.poll() is None:
                    logger.info(f"🔴 Stopping {name} (PID {process.pid})")
                    process.terminate()

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️ Force killing {name}")
                        process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")

        self.running_processes.clear()

    def print_status_report(self):
        """Print comprehensive status report"""
        status = self.get_service_status()

        print("\n" + "="*60)
        print("🎯 DGM SERVICES STATUS REPORT")
        print("="*60)

        total_services = len(status)
        running_services = sum(1 for s in status.values() if s['running'])

        print(f"\n📊 Summary: {running_services}/{total_services} services running")

        for name, info in status.items():
            status_icon = "✅" if info['running'] else "❌"
            uptime_str = f"{info['uptime']:.1f}s" if info['running'] else "stopped"

            print(f"\n{status_icon} {name}")
            print(f"   📁 File: {info['file_path']}")
            print(f"   🔌 Port: {info['port']}")
            print(f"   ⏱️ Status: {uptime_str}")
            if info['pid']:
                print(f"   🆔 PID: {info['pid']}")

async def main():
    """Main launcher function"""
    launcher = DGMServiceLauncher()

    try:
        print("🎯 DGM Services Launcher Starting...")
        print("="*50)

        # Start all services
        await launcher.start_all_services()

        # Print status report
        launcher.print_status_report()

        print(f"\n🎯 All services launched! Press Ctrl+C to stop all services.")

        # Keep running and monitor
        try:
            while True:
                await asyncio.sleep(30)

                # Quick health check
                status = launcher.get_service_status()
                running_count = sum(1 for s in status.values() if s['running'])
                total_count = len(status)

                if running_count < total_count:
                    logger.warning(f"⚠️ {total_count - running_count} services have stopped")

        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")

    except Exception as e:
        logger.error(f"❌ Launcher error: {e}")

    finally:
        launcher.stop_all_services()
        print("\n✅ All services stopped. Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
