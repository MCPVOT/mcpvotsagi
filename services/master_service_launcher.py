#!/usr/bin/env python3
"""
MCPVotsAGI Master Service Launcher
=================================
Single-source-of-truth launcher that starts all services in correct order.
Prevents duplicates and ensures proper A2A + MCP integration.
"""

import asyncio
import subprocess
import sys
import time
import json
import socket
import psutil
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterServiceLauncher:
    """Master launcher for all MCPVotsAGI services"""

    def __init__(self):
        self.workspace = Path("c:/Workspace/MCPVotsAGI")
        self.processes = {}
        self.running = False
        self.config = {}

        # Load consolidated configuration
        self.load_config()

        # Define service startup order (critical for dependencies)
        self.startup_order = [
            {
                'name': 'redis',
                'description': 'Redis Message Queue & Memory Backend',
                'command': ['wsl', '-d', 'Ubuntu', 'sudo', 'systemctl', 'start', 'redis-server'],
                'port': 6379,
                'wait': 3,
                'health_check': self.check_redis_health
            },
            {
                'name': 'enhanced_mcp_memory',
                'description': 'Enhanced MCP Memory with Redis',
                'command': [sys.executable, 'core/enhanced_mcp_memory_server.py'],
                'port': 3002,
                'wait': 2,
                'health_check': self.check_port_health
            },
            {
                'name': 'consolidated_mcp_servers',
                'description': 'Consolidated MCP Tool Servers',
                'command': [sys.executable, 'core/consolidated_mcp_servers.py'],
                'ports': [3000, 3001, 3003, 3004, 3005, 3006, 3007],
                'wait': 5,
                'health_check': self.check_mcp_servers_health
            },
            {
                'name': 'a2a_enhanced_protocol',
                'description': 'A2A Enhanced Communication Protocol',
                'command': [sys.executable, 'core/a2a_enhanced_protocol.py'],
                'port': 8001,
                'wait': 2,
                'health_check': self.check_port_health
            },
            {
                'name': 'deepseek_trading_enhanced',
                'description': 'Enhanced Trading System',
                'command': [sys.executable, 'deepseek_trading_agent_enhanced.py'],
                'port': 8004,
                'wait': 2,
                'health_check': self.check_port_health
            },
            {
                'name': 'ecosystem_manager',
                'description': 'System Orchestration Manager',
                'command': [sys.executable, 'ecosystem_manager_v4_clean.py'],
                'port': 8002,
                'wait': 2,
                'health_check': self.check_port_health
            },
            {
                'name': 'unified_agi_portal',
                'description': 'Unified AGI Portal Dashboard',
                'command': [sys.executable, 'src/core/unified_agi_portal.py'],
                'port': 8000,
                'wait': 3,
                'health_check': self.check_port_health
            }
        ]

    def load_config(self):
        """Load consolidated services configuration"""
        config_path = self.workspace / "consolidated_services_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def check_port_health(self, port: int) -> bool:
        """Check if a port is being used (indicates service is running)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0  # Port is in use (service running)
        except Exception:
            return False

    async def check_redis_health(self) -> bool:
        """Check Redis health"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, password='MCPVotsAGI2025!')
            r.ping()
            return True
        except Exception:
            return False

    def check_mcp_servers_health(self) -> bool:
        """Check if MCP servers are healthy"""
        mcp_ports = [3000, 3001, 3003, 3004, 3005, 3006, 3007]
        healthy_count = sum(1 for port in mcp_ports if self.check_port_health(port))
        return healthy_count >= len(mcp_ports) // 2  # At least half should be running

    def kill_duplicate_processes(self):
        """Kill any existing duplicate processes"""
        print("🔍 Scanning for existing processes...")

        duplicate_scripts = [
            'oracle_agi_v5_simple.py',
            'oracle_agi_v5_complete.py',
            'oracle_agi_v6_realtime_dashboard.py',
            'oracle_agi_v7_full_dashboard.py',
            'oracle_agi_v7_ultimate.py',
            'oracle_agi_v8_ultimate_brain.py',
            'oracle_agi_ultimate_unified.py',
            'oracle_agi_ultimate_unified_v2.py',
            'knowledge_base_system.py',
            'basic_a2a_protocol.py',
            'dgm_trading_algorithms.py'
        ]

        killed_count = 0
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and len(cmdline) > 1:
                    script_name = Path(cmdline[1]).name
                    if script_name in duplicate_scripts:
                        print(f"🔥 Terminating duplicate: {script_name} (PID: {proc.pid})")
                        proc.terminate()
                        killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue

        if killed_count > 0:
            print(f"✅ Terminated {killed_count} duplicate processes")
            time.sleep(2)  # Wait for cleanup
        else:
            print("✅ No duplicate processes found")

    async def start_service(self, service_config: Dict) -> bool:
        """Start an individual service"""
        name = service_config['name']
        command = service_config['command']
        description = service_config['description']

        print(f"\n🚀 Starting {name}: {description}")

        # Special handling for Redis (system service)
        if name == 'redis':
            try:
                # Start Redis in WSL2
                result = subprocess.run(command,
                                      capture_output=True,
                                      text=True,
                                      timeout=10)

                # Wait for Redis to start
                await asyncio.sleep(service_config['wait'])

                # Check health
                if await service_config['health_check']():
                    print(f"✅ {name} is healthy")
                    return True
                else:
                    print(f"❌ {name} health check failed")
                    return False

            except Exception as e:
                print(f"❌ Failed to start {name}: {e}")
                return False

        # Start Python processes
        try:
            # Change to workspace directory
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(self.workspace),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            self.processes[name] = {
                'process': process,
                'config': service_config,
                'started_at': datetime.now()
            }

            # Wait for service to initialize
            await asyncio.sleep(service_config['wait'])

            # Check health
            health_ok = False
            if 'port' in service_config:
                health_ok = self.check_port_health(service_config['port'])
            elif 'ports' in service_config:
                health_ok = service_config['health_check']()
            elif 'health_check' in service_config:
                if asyncio.iscoroutinefunction(service_config['health_check']):
                    health_ok = await service_config['health_check']()
                else:
                    health_ok = service_config['health_check']()

            if health_ok:
                print(f"✅ {name} started successfully (PID: {process.pid})")
                return True
            else:
                print(f"⚠️ {name} started but health check failed")
                return True  # Still consider it started

        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False

    async def start_all_services(self):
        """Start all services in the correct order"""
        print("🎯 STARTING MCPVOTSAGI UNIFIED SYSTEM")
        print("=" * 80)
        print(f"Workspace: {self.workspace}")
        print(f"Time: {datetime.now().isoformat()}")

        # Kill any duplicate processes first
        self.kill_duplicate_processes()

        print(f"\n📋 Starting {len(self.startup_order)} services in dependency order...")

        success_count = 0
        for i, service_config in enumerate(self.startup_order, 1):
            print(f"\n[{i}/{len(self.startup_order)}] {service_config['name']}")

            if await self.start_service(service_config):
                success_count += 1
            else:
                print(f"⚠️ Service {service_config['name']} failed to start properly")

        print(f"\n📊 STARTUP SUMMARY")
        print("=" * 50)
        print(f"✅ Services started: {success_count}/{len(self.startup_order)}")

        if success_count >= len(self.startup_order) * 0.8:  # 80% success rate
            print("🎉 SYSTEM STARTUP SUCCESSFUL!")
            self.running = True

            print(f"\n🌐 ACCESS POINTS:")
            print(f"   Main Dashboard: http://localhost:8000")
            print(f"   A2A Protocol: ws://localhost:8001")
            print(f"   MCP Memory: http://localhost:3002")
            print(f"   Trading System: http://localhost:8004")
            print(f"   System Manager: http://localhost:8002")

            print(f"\n🔧 REDIS ACCESS:")
            print(f"   Host: localhost:6379")
            print(f"   Password: MCPVotsAGI2025!")
            print(f"   Databases: 0=A2A, 1=MCP Memory, 2=Cache")

            return True
        else:
            print("❌ SYSTEM STARTUP FAILED!")
            return False

    async def monitor_services(self):
        """Monitor service health and restart if needed"""
        while self.running:
            print(f"\n🔍 Health check at {datetime.now().strftime('%H:%M:%S')}")

            for name, process_info in list(self.processes.items()):
                process = process_info['process']
                config = process_info['config']

                # Check if process is still running
                if process.returncode is not None:
                    print(f"💀 {name} process died (exit code: {process.returncode})")
                    print(f"🔄 Restarting {name}...")

                    if await self.start_service(config):
                        print(f"✅ {name} restarted successfully")
                    else:
                        print(f"❌ Failed to restart {name}")

                # Check health
                elif 'health_check' in config:
                    try:
                        if asyncio.iscoroutinefunction(config['health_check']):
                            healthy = await config['health_check']()
                        else:
                            healthy = config['health_check']()

                        if healthy:
                            print(f"✅ {name} healthy")
                        else:
                            print(f"⚠️ {name} unhealthy")
                    except Exception as e:
                        print(f"❌ Health check failed for {name}: {e}")

            await asyncio.sleep(30)  # Check every 30 seconds

    async def shutdown_all_services(self):
        """Gracefully shutdown all services"""
        print("\n🛑 SHUTTING DOWN ALL SERVICES")
        print("=" * 50)

        for name, process_info in self.processes.items():
            try:
                process = process_info['process']
                print(f"🔄 Stopping {name}...")

                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                    print(f"✅ {name} stopped gracefully")
                except asyncio.TimeoutError:
                    process.kill()
                    print(f"🔥 {name} force killed")

            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")

        self.running = False
        print("✅ All services stopped")

    async def run(self):
        """Main run loop"""
        try:
            if await self.start_all_services():
                print("\n🎮 MCPVotsAGI is running! Press Ctrl+C to stop.")

                # Set up signal handlers for graceful shutdown
                def signal_handler(signum, frame):
                    print(f"\n🛑 Received signal {signum}, shutting down...")
                    self.running = False

                signal.signal(signal.SIGINT, signal_handler)
                signal.signal(signal.SIGTERM, signal_handler)

                # Start monitoring
                monitor_task = asyncio.create_task(self.monitor_services())

                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass

            else:
                print("❌ Failed to start system")

        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        finally:
            await self.shutdown_all_services()

async def main():
    """Main entry point"""
    launcher = MasterServiceLauncher()
    await launcher.run()

if __name__ == "__main__":
    asyncio.run(main())
