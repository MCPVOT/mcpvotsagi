#!/usr/bin/env python3
"""
MCPVotsAGI Streamlined Production Launcher V2
============================================
Production-ready launcher with enhanced reliability, monitoring, and recovery
"""

import asyncio
import subprocess
import psutil
import time
import json
import sys
import os
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service status enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"

@dataclass
class ServiceConfig:
    """Service configuration dataclass"""
    name: str
    command: List[str]
    port: Optional[int] = None
    required: bool = True
    startup_timeout: int = 10
    health_check_retries: int = 3
    health_check_delay: float = 2.0
    restart_on_failure: bool = True
    max_restarts: int = 3
    environment: Dict[str, str] = field(default_factory=dict)

@dataclass
class ServiceState:
    """Track service state"""
    status: ServiceStatus = ServiceStatus.STOPPED
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    restart_count: int = 0
    last_health_check: Optional[datetime] = None
    health_check_failures: int = 0

class ProductionLauncherV2:
    """Enhanced production launcher for MCPVotsAGI"""

    def __init__(self):
        self.workspace = Path.cwd()
        self.service_states: Dict[str, ServiceState] = {}
        self.running = False
        self.health_check_interval = 30  # seconds
        
        # Core service definitions with enhanced configuration
        self.service_configs = {
            "redis": ServiceConfig(
                name="Redis Message Queue",
                command=["wsl", "-d", "Ubuntu", "sudo", "systemctl", "start", "redis-server"],
                port=6379,
                required=True,
                startup_timeout=15,
                restart_on_failure=False  # System service, let systemd handle
            ),
            "unified_dgm": ServiceConfig(
                name="Unified DGM Server V2",
                command=[sys.executable, "core/unified_dgm_server_v2.py"],
                port=8013,  # Fixed port number
                required=True,
                health_check_retries=5,
                environment={"PYTHONUNBUFFERED": "1"}
            ),
            "a2a_protocol": ServiceConfig(
                name="A2A Enhanced Protocol",
                command=[sys.executable, "core/a2a_enhanced_protocol.py"],
                port=8001,
                required=True,
                environment={"PYTHONUNBUFFERED": "1"}
            ),
            "mcp_memory": ServiceConfig(
                name="Enhanced MCP Memory Server",
                command=[sys.executable, "core/enhanced_mcp_memory_server.py"],
                port=3002,
                required=False,
                restart_on_failure=True
            ),
            "deepseek_mcp": ServiceConfig(
                name="DeepSeek MCP Server",
                command=[sys.executable, "deepseek_mcp_server.py"],
                port=8003,
                required=False,
                health_check_retries=2
            ),
            "dgm_dashboard": ServiceConfig(
                name="DGM Dashboard",
                command=[sys.executable, "-m", "streamlit", "run", "dgm_dashboard.py", "--server.port", "8501"],
                port=8501,
                required=False,
                startup_timeout=20,
                health_check_delay=5.0
            )
        }
        
        # Initialize service states
        for service_id in self.service_configs:
            self.service_states[service_id] = ServiceState()

    async def check_redis_health(self) -> bool:
        """Enhanced Redis health check with connection pooling"""
        try:
            import redis
            # Use connection pool for efficiency
            pool = redis.ConnectionPool(
                host="localhost",
                port=6379,
                password="mcpvotsagi2025",
                socket_connect_timeout=2,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            r = redis.Redis(connection_pool=pool)
            
            # Perform multiple checks
            r.ping()
            # Check if we can write/read
            test_key = f"health_check_{int(time.time())}"
            r.setex(test_key, 10, "ok")
            result = r.get(test_key)
            r.delete(test_key)
            
            pool.disconnect()
            return result == b"ok"
        except Exception as e:
            logger.debug(f"Redis health check failed: {e}")
            return False

    async def check_http_health(self, port: int, path: str = "/health") -> bool:
        """Enhanced HTTP health check with retries"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:{port}{path}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    return 200 <= response.status < 300
        except Exception as e:
            logger.debug(f"HTTP health check failed for port {port}: {e}")
            return False

    async def check_websocket_health(self, port: int) -> bool:
        """Enhanced WebSocket health check"""
        try:
            import websockets
            uri = f"ws://localhost:{port}"
            async with websockets.connect(uri, timeout=3, close_timeout=1) as ws:
                # Send ping and wait for response
                await ws.send(json.dumps({"type": "ping", "timestamp": time.time()}))
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                
                # Verify response is valid
                try:
                    data = json.loads(response)
                    return data.get("type") in ["pong", "ping_response"]
                except json.JSONDecodeError:
                    # Some services might not return JSON
                    return len(response) > 0
        except Exception as e:
            logger.debug(f"WebSocket health check failed for port {port}: {e}")
            return False

    async def check_service_health(self, service_id: str, config: ServiceConfig) -> bool:
        """Unified health check for a service"""
        if config.port is None:
            # No port means we just check if process is running
            state = self.service_states[service_id]
            return state.process is not None and state.process.poll() is None
        
        # Determine health check method based on service
        if service_id == "redis":
            return await self.check_redis_health()
        elif service_id in ["unified_dgm", "mcp_memory", "dgm_dashboard"]:
            return await self.check_http_health(config.port)
        elif service_id in ["a2a_protocol", "deepseek_mcp"]:
            return await self.check_websocket_health(config.port)
        else:
            # Default to HTTP health check
            return await self.check_http_health(config.port)

    def kill_duplicate_processes(self) -> int:
        """Enhanced duplicate process killer with better pattern matching"""
        logger.info("Scanning for duplicate processes...")
        
        # Enhanced patterns with regex support
        patterns = {
            "unified_dgm_server": ["unified_dgm_server", "dgm_server_v2"],
            "a2a_enhanced_protocol": ["a2a_enhanced", "a2a_protocol"],
            "enhanced_mcp_memory": ["mcp_memory", "memory_server"],
            "deepseek_mcp_server": ["deepseek_mcp", "deepseek_server"],
            "master_service_launcher": ["service_launcher", "master_launcher"],
            "dgm_integration_manager": ["dgm_integration", "dgm_manager"],
            "streamlit": ["streamlit.*dgm_dashboard"]  # Kill old dashboard instances
        }
        
        killed_count = 0
        current_pids = {state.pid for state in self.service_states.values() if state.pid}
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['pid'] in current_pids:
                    continue
                    
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                for pattern_name, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        if pattern in cmdline.lower():
                            # Don't kill very recent processes (might be starting up)
                            create_time = datetime.fromtimestamp(proc.info['create_time'])
                            if datetime.now() - create_time > timedelta(seconds=5):
                                logger.info(f"Killing duplicate {pattern_name} process: PID {proc.info['pid']}")
                                proc.terminate()
                                try:
                                    proc.wait(timeout=3)
                                except psutil.TimeoutExpired:
                                    proc.kill()
                                killed_count += 1
                                break
                                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if killed_count > 0:
            logger.info(f"Killed {killed_count} duplicate processes")
            time.sleep(2)  # Wait for cleanup
        else:
            logger.info("No duplicate processes found")
            
        return killed_count

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            return sock.connect_ex(('localhost', port)) == 0

    async def start_service(self, service_id: str, config: ServiceConfig) -> bool:
        """Enhanced service starter with better error handling"""
        state = self.service_states[service_id]
        
        logger.info(f"Starting {service_id}: {config.name}")
        
        try:
            # Check if already running
            if config.port and self.is_port_in_use(config.port):
                logger.info(f"{service_id} already running on port {config.port}")
                state.status = ServiceStatus.RUNNING
                # Try to find the PID
                for proc in psutil.process_iter(['pid', 'cmdline']):
                    try:
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if str(config.port) in cmdline and service_id in cmdline.lower():
                            state.pid = proc.info['pid']
                            break
                    except:
                        continue
                return True
            
            # Special handling for Redis
            if service_id == "redis":
                state.status = ServiceStatus.STARTING
                process = subprocess.run(
                    config.command,
                    capture_output=True,
                    text=True,
                    timeout=config.startup_timeout
                )
                
                if process.returncode == 0:
                    state.status = ServiceStatus.RUNNING
                    logger.info(f"{service_id} started successfully")
                    return True
                else:
                    state.status = ServiceStatus.FAILED
                    logger.error(f"{service_id} failed: {process.stderr}")
                    return False
            
            # Start other services
            state.status = ServiceStatus.STARTING
            
            # Prepare environment
            env = os.environ.copy()
            env.update(config.environment)
            
            # Start process
            process = subprocess.Popen(
                config.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.workspace,
                env=env,
                preexec_fn=os.setsid if sys.platform != "win32" else None
            )
            
            state.process = process
            state.pid = process.pid
            state.start_time = datetime.now()
            
            # Wait for startup
            await asyncio.sleep(config.health_check_delay)
            
            # Check if process is still running
            if process.poll() is None:
                # Perform health check with retries
                healthy = False
                for attempt in range(config.health_check_retries):
                    if await self.check_service_health(service_id, config):
                        healthy = True
                        break
                    await asyncio.sleep(1)
                
                if healthy:
                    state.status = ServiceStatus.HEALTHY
                    logger.info(f"{service_id} started successfully (PID: {process.pid})")
                    return True
                else:
                    state.status = ServiceStatus.UNHEALTHY
                    logger.warning(f"{service_id} started but health check failed")
                    return config.required is False  # Non-required services can be unhealthy
            else:
                # Process died during startup
                stdout, stderr = process.communicate()
                state.status = ServiceStatus.FAILED
                logger.error(f"{service_id} failed to start")
                if stderr:
                    logger.error(f"Error output: {stderr.decode()[:500]}")  # Limit error output
                return False
                
        except subprocess.TimeoutExpired:
            state.status = ServiceStatus.FAILED
            logger.error(f"{service_id} startup timed out")
            return False
        except Exception as e:
            state.status = ServiceStatus.FAILED
            logger.error(f"{service_id} startup failed: {e}")
            return False

    async def restart_service(self, service_id: str) -> bool:
        """Restart a failed service"""
        state = self.service_states[service_id]
        config = self.service_configs[service_id]
        
        if state.restart_count >= config.max_restarts:
            logger.error(f"{service_id} exceeded max restarts ({config.max_restarts})")
            return False
        
        logger.info(f"Restarting {service_id} (attempt {state.restart_count + 1}/{config.max_restarts})")
        
        # Stop the service first
        if state.process:
            try:
                if sys.platform == "win32":
                    state.process.terminate()
                else:
                    os.killpg(os.getpgid(state.process.pid), signal.SIGTERM)
                state.process.wait(timeout=5)
            except:
                if state.process:
                    state.process.kill()
        
        state.restart_count += 1
        await asyncio.sleep(2)  # Wait before restart
        
        return await self.start_service(service_id, config)

    async def monitor_services(self):
        """Background task to monitor service health"""
        logger.info("Starting health monitor...")
        
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for service_id, config in self.service_configs.items():
                    state = self.service_states[service_id]
                    
                    if state.status in [ServiceStatus.RUNNING, ServiceStatus.HEALTHY, ServiceStatus.UNHEALTHY]:
                        # Perform health check
                        healthy = await self.check_service_health(service_id, config)
                        
                        if healthy:
                            if state.status != ServiceStatus.HEALTHY:
                                logger.info(f"{service_id} is now healthy")
                            state.status = ServiceStatus.HEALTHY
                            state.health_check_failures = 0
                        else:
                            state.health_check_failures += 1
                            
                            if state.health_check_failures >= 3:
                                state.status = ServiceStatus.UNHEALTHY
                                logger.warning(f"{service_id} is unhealthy")
                                
                                # Restart if configured
                                if config.restart_on_failure and config.required:
                                    await self.restart_service(service_id)
                        
                        state.last_health_check = datetime.now()
                        
            except Exception as e:
                logger.error(f"Health monitor error: {e}")

    async def verify_system_health(self) -> Tuple[bool, Dict[str, bool]]:
        """Enhanced system health verification"""
        logger.info("Verifying System Health...")
        print("=" * 60)
        
        health_results = {}
        
        for service_id, config in self.service_configs.items():
            state = self.service_states[service_id]
            
            if state.status == ServiceStatus.HEALTHY:
                health_results[service_id] = True
                logger.info(f"   ✅ HEALTHY  {config.name:<30} (PID: {state.pid})")
            elif state.status == ServiceStatus.RUNNING:
                # Double-check health
                healthy = await self.check_service_health(service_id, config)
                health_results[service_id] = healthy
                status = "HEALTHY" if healthy else "RUNNING"
                logger.info(f"   {'✅' if healthy else '⚠️'} {status:<8} {config.name:<30} (PID: {state.pid})")
            else:
                health_results[service_id] = False
                logger.info(f"   ❌ {state.status.value.upper():<8} {config.name}")
        
        # Calculate overall health
        required_services = [sid for sid, cfg in self.service_configs.items() if cfg.required]
        required_healthy = sum(1 for sid in required_services if health_results.get(sid, False))
        total_healthy = sum(1 for healthy in health_results.values() if healthy)
        
        overall_healthy = required_healthy == len(required_services)
        
        print("=" * 60)
        logger.info(f"System Health Summary:")
        logger.info(f"  Required Services: {required_healthy}/{len(required_services)}")
        logger.info(f"  Total Services: {total_healthy}/{len(self.service_configs)}")
        
        return overall_healthy, health_results

    async def launch_production_system(self):
        """Launch the complete production system with monitoring"""
        print("\n🚀 MCPVotsAGI PRODUCTION LAUNCHER V2")
        print("=" * 60)
        logger.info(f"Workspace: {self.workspace}")
        logger.info(f"Python: {sys.executable}")
        logger.info(f"Platform: {sys.platform}")
        
        self.running = True
        
        # Step 1: Clean up duplicates
        self.kill_duplicate_processes()
        
        # Step 2: Start services in dependency order
        service_order = ["redis", "unified_dgm", "a2a_protocol", "mcp_memory", "deepseek_mcp", "dgm_dashboard"]
        
        startup_results = {}
        for service_id in service_order:
            if service_id in self.service_configs:
                config = self.service_configs[service_id]
                result = await self.start_service(service_id, config)
                startup_results[service_id] = result
                
                if config.required and not result:
                    logger.error(f"Critical service {service_id} failed - aborting startup")
                    self.running = False
                    return False
                
                # Small delay between services
                await asyncio.sleep(1)
        
        # Step 3: Verify system health
        system_healthy, health_results = await self.verify_system_health()
        
        # Step 4: Start monitoring
        monitor_task = asyncio.create_task(self.monitor_services())
        
        # Step 5: Display final status
        print("\n" + "=" * 60)
        print("📊 STARTUP SUMMARY")
        print("=" * 60)
        
        if system_healthy:
            print("\n✅ SYSTEM STARTUP SUCCESSFUL!\n")
            print("🌐 ACCESS POINTS:")
            print(f"   📡 Redis:          localhost:6379 (password: mcpvotsagi2025)")
            print(f"   🤖 A2A Protocol:   ws://localhost:8001")
            print(f"   🧬 DGM Server:     ws://localhost:8013")
            print(f"   💾 MCP Memory:     http://localhost:3002")
            print(f"   🔍 DeepSeek MCP:   ws://localhost:8003")
            print(f"   📊 DGM Dashboard:  http://localhost:8501")
            
            print(f"\n📋 MONITORING:")
            print(f"   • Health checks every {self.health_check_interval}s")
            print(f"   • Auto-restart enabled for critical services")
            print(f"   • Logs available in console")
            
            print(f"\n🎮 System is RUNNING! Press Ctrl+C to shutdown...")
            
            # Keep running with periodic status updates
            try:
                last_status_time = datetime.now()
                while self.running:
                    await asyncio.sleep(5)
                    
                    # Print status update every 5 minutes
                    if datetime.now() - last_status_time > timedelta(minutes=5):
                        healthy_count = sum(1 for s in self.service_states.values() 
                                          if s.status == ServiceStatus.HEALTHY)
                        logger.info(f"Status Update: {healthy_count}/{len(self.service_configs)} services healthy")
                        last_status_time = datetime.now()
                        
            except KeyboardInterrupt:
                logger.info("Shutdown requested...")
                
        else:
            print("\n❌ SYSTEM STARTUP FAILED!")
            print("\nFailed services:")
            for service_id, healthy in health_results.items():
                if not healthy:
                    config = self.service_configs[service_id]
                    print(f"   • {config.name}")
        
        # Cleanup
        self.running = False
        monitor_task.cancel()
        await self.shutdown_services()
        
        return system_healthy

    async def shutdown_services(self):
        """Enhanced graceful shutdown with timeout handling"""
        logger.info("Shutting down services...")
        
        shutdown_order = ["dgm_dashboard", "deepseek_mcp", "mcp_memory", "a2a_protocol", "unified_dgm"]
        
        for service_id in shutdown_order:
            if service_id not in self.service_states:
                continue
                
            state = self.service_states[service_id]
            if state.process and state.process.poll() is None:
                try:
                    logger.info(f"Stopping {service_id}...")
                    
                    # Send SIGTERM (or terminate on Windows)
                    if sys.platform == "win32":
                        state.process.terminate()
                    else:
                        os.killpg(os.getpgid(state.process.pid), signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    state.process.wait(timeout=5)
                    logger.info(f"{service_id} stopped gracefully")
                    
                except subprocess.TimeoutExpired:
                    # Force kill if not responding
                    logger.warning(f"{service_id} not responding, forcing shutdown")
                    state.process.kill()
                    state.process.wait()
                    
                except Exception as e:
                    logger.error(f"Error stopping {service_id}: {e}")
                
                state.status = ServiceStatus.STOPPED
                state.process = None
        
        logger.info("All services stopped")

async def main():
    """Main launcher function with signal handling"""
    launcher = ProductionLauncherV2()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        launcher.running = False
    
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        success = await launcher.launch_production_system()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Launch failed: {e}")
        return 1

if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)