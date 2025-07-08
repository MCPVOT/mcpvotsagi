#!/usr/bin/env python3
"""
MCPVotsAGI Streamlined Production Launcher
=========================================
Production-ready launcher that eliminates duplicates and ensures clean system startup
"""

import asyncio
import subprocess
import psutil
import time
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

class ProductionLauncher:
    """Streamlined production launcher for MCPVotsAGI"""

    def __init__(self):
        self.workspace = Path.cwd()
        self.services = {}
        self.running_processes: Set[int] = set()

        # Core service definitions - no duplicates
        self.service_config = {
            "redis": {
                "name": "Redis Message Queue",
                "command": ["wsl", "-d", "Ubuntu", "sudo", "systemctl", "start", "redis-server"],
                "health_check": self.check_redis_health,
                "port": 6379,
                "required": True
            },
            "unified_dgm": {
                "name": "Unified DGM Server V2",
                "command": [sys.executable, "core/unified_dgm_server_v2.py"],
                "health_check": self.check_http_health,
                "port": 8002,
                "required": True
            },
            "a2a_protocol": {
                "name": "A2A Enhanced Protocol",
                "command": [sys.executable, "core/a2a_enhanced_protocol.py"],
                "health_check": self.check_websocket_health,
                "port": 8001,
                "required": True
            },
            "mcp_memory": {
                "name": "Enhanced MCP Memory Server",
                "command": [sys.executable, "core/enhanced_mcp_memory_server.py"],
                "health_check": self.check_http_health,
                "port": 3002,
                "required": False
            },
            "deepseek_mcp": {
                "name": "DeepSeek MCP Server",
                "command": [sys.executable, "deepseek_mcp_server.py"],
                "health_check": self.check_websocket_health,
                "port": 8003,
                "required": False
            }
        }

    async def check_redis_health(self) -> bool:
        """Check Redis health"""
        try:
            import redis
            r = redis.Redis(
                host="localhost",
                port=6379,
                password="mcpvotsagi2025",
                socket_connect_timeout=2
            )
            r.ping()
            r.close()
            return True
        except:
            return False

    async def check_http_health(self, port: int) -> bool:
        """Check HTTP service health"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health", timeout=3) as response:
                    return response.status == 200
        except:
            return False

    async def check_websocket_health(self, port: int) -> bool:
        """Check WebSocket service health"""
        try:
            import websockets
            async with websockets.connect(f"ws://localhost:{port}", timeout=3) as ws:
                await ws.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                return True
        except:
            return False

    def kill_duplicate_processes(self):
        """Kill any duplicate or conflicting processes"""
        print("🔍 Scanning for duplicate processes...")

        # Process patterns to check
        patterns = [
            "unified_dgm_server",
            "a2a_enhanced_protocol",
            "enhanced_mcp_memory",
            "deepseek_mcp_server",
            "master_service_launcher",
            "dgm_integration_manager"
        ]

        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                for pattern in patterns:
                    if pattern in cmdline and proc.info['pid'] not in self.running_processes:
                        print(f"🔪 Killing duplicate process: {proc.info['pid']} - {pattern}")
                        proc.kill()
                        killed_count += 1
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed_count > 0:
            print(f"✅ Killed {killed_count} duplicate processes")
            time.sleep(2)  # Wait for cleanup
        else:
            print("✅ No duplicate processes found")

    async def start_service(self, service_id: str, config: Dict) -> bool:
        """Start a single service"""
        print(f"\n🚀 Starting {service_id}: {config['name']}")

        try:
            # Check if service is already running
            if hasattr(config, 'port'):
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', config['port']))
                sock.close()

                if result == 0:
                    print(f"✅ {service_id} already running on port {config['port']}")
                    return True

            # Start the service
            if service_id == "redis":
                # Special handling for Redis
                process = subprocess.run(config['command'], capture_output=True, text=True, timeout=10)
                success = process.returncode == 0
                if success:
                    print(f"✅ {service_id} started successfully")
                else:
                    print(f"❌ {service_id} failed: {process.stderr}")
                return success
            else:
                # Start other services
                process = subprocess.Popen(
                    config['command'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.workspace
                )

                self.services[service_id] = process
                self.running_processes.add(process.pid)

                # Wait a moment for startup
                await asyncio.sleep(2)

                # Check if process is still running
                if process.poll() is None:
                    print(f"✅ {service_id} started successfully (PID: {process.pid})")
                    return True
                else:
                    stdout, stderr = process.communicate()
                    print(f"❌ {service_id} failed to start")
                    if stderr:
                        print(f"   Error: {stderr.decode()}")
                    return False

        except subprocess.TimeoutExpired:
            print(f"⏱️ {service_id} startup timed out")
            return False
        except Exception as e:
            print(f"❌ {service_id} startup failed: {e}")
            return False

    async def verify_system_health(self) -> bool:
        """Verify overall system health"""
        print("\n🔍 Verifying System Health...")
        print("=" * 50)

        health_results = {}

        for service_id, config in self.service_config.items():
            if config.get('required', False):
                try:
                    if service_id == "redis":
                        healthy = await config['health_check']()
                    else:
                        healthy = await config['health_check'](config['port'])

                    health_results[service_id] = healthy
                    status = "✅ HEALTHY" if healthy else "❌ UNHEALTHY"
                    print(f"   {status} {config['name']}")

                except Exception as e:
                    health_results[service_id] = False
                    print(f"   ❌ ERROR {config['name']}: {e}")

        required_services = [s for s, cfg in self.service_config.items() if cfg.get('required', False)]
        healthy_required = sum(1 for s in required_services if health_results.get(s, False))

        overall_healthy = healthy_required == len(required_services)

        print(f"\n📊 System Health: {healthy_required}/{len(required_services)} required services healthy")

        if overall_healthy:
            print("🎉 SYSTEM IS HEALTHY AND READY!")
        else:
            print("⚠️ SYSTEM NEEDS ATTENTION")

        return overall_healthy

    async def launch_production_system(self):
        """Launch the complete production system"""
        print("🎯 MCPVotsAGI PRODUCTION LAUNCHER")
        print("=" * 60)
        print(f"Workspace: {self.workspace}")
        print(f"Time: {datetime.now().isoformat()}")

        # Step 1: Clean up duplicates
        self.kill_duplicate_processes()

        # Step 2: Start core services in order
        print(f"\n📋 Starting {len(self.service_config)} services...")

        startup_results = {}
        for service_id, config in self.service_config.items():
            result = await self.start_service(service_id, config)
            startup_results[service_id] = result

            if config.get('required', False) and not result:
                print(f"❌ Critical service {service_id} failed - aborting startup")
                return False

        # Step 3: Verify system health
        system_healthy = await self.verify_system_health()

        # Step 4: Display results
        print(f"\n" + "=" * 60)
        print("📊 STARTUP SUMMARY")
        print("=" * 60)

        successful_services = sum(1 for success in startup_results.values() if success)
        total_services = len(startup_results)

        print(f"✅ Services Started: {successful_services}/{total_services}")
        print(f"🎯 System Health: {'HEALTHY' if system_healthy else 'NEEDS ATTENTION'}")

        if system_healthy:
            print(f"\n🌐 ACCESS POINTS:")
            print(f"   🔗 Redis: localhost:6379 (password: mcpvotsagi2025)")
            print(f"   🤖 A2A Protocol: ws://localhost:8001")
            print(f"   🧠 DGM Server: http://localhost:8002")
            print(f"   💾 MCP Memory: http://localhost:3002")
            print(f"   🔍 DeepSeek MCP: ws://localhost:8003")

            print(f"\n🎮 MCPVotsAGI Production System is RUNNING!")
            print(f"Press Ctrl+C to stop all services...")

            # Keep running
            try:
                while True:
                    await asyncio.sleep(30)
                    # Could add periodic health checks here
            except KeyboardInterrupt:
                print(f"\n🛑 Shutdown requested...")
                await self.shutdown_services()

        return system_healthy

    async def shutdown_services(self):
        """Gracefully shutdown all services"""
        print("🔄 Shutting down services...")

        for service_id, process in self.services.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {service_id} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 {service_id} forcefully killed")
            except Exception as e:
                print(f"❌ Error stopping {service_id}: {e}")

        print("🎯 All services stopped")

async def main():
    """Main launcher function"""
    launcher = ProductionLauncher()

    try:
        success = await launcher.launch_production_system()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Launch cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Launch failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
