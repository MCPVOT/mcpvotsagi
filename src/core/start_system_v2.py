#!/usr/bin/env python3
"""
System Startup Script V2
========================
Complete system initialization with health checks and monitoring
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
import psutil
import aiohttp
from aiohttp import web
import json
import subprocess
from dataclasses import dataclass
from enum import Enum
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows
colorama.init()

# Configure logging with colors
class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Apply colored formatter
for handler in logging.root.handlers:
    handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger("SystemStartup")


class ServiceStatus(Enum):
    """Service status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class Service:
    """Service definition"""
    name: str
    command: List[str]
    port: Optional[int] = None
    health_endpoint: Optional[str] = None
    required: bool = True
    depends_on: List[str] = None
    env: Dict[str, str] = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.env is None:
            self.env = {}


class SystemManager:
    """Main system manager"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.status: Dict[str, ServiceStatus] = {}
        self.config = self._load_config()
        self._setup_services()
        self._shutdown_requested = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Load system configuration"""
        config_path = Path("system_config.yaml")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
                
        # Default configuration
        return {
            "python_path": sys.executable,
            "workspace": str(Path.cwd()),
            "startup_timeout": 300,
            "health_check_interval": 30,
            "auto_restart": True,
            "log_level": "INFO"
        }
        
    def _setup_services(self):
        """Define all services"""
        python = self.config["python_path"]
        
        # Core MCP services
        self.add_service(Service(
            name="Memory MCP",
            command=[python, "servers/enhanced_memory_mcp_server.py"],
            port=3002,
            health_endpoint="http://localhost:3002/health",
            required=True
        ))
        
        self.add_service(Service(
            name="GitHub MCP",
            command=[python, "servers/mcp_github_server.py"],
            port=3001,
            health_endpoint="http://localhost:3001/health",
            required=False,
            env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")}
        ))
        
        self.add_service(Service(
            name="Solana MCP",
            command=[python, "solana_mcp_deepseek_integration.py"],
            port=3005,
            health_endpoint="http://localhost:3005/solana/status",
            required=True
        ))
        
        # Trading services
        self.add_service(Service(
            name="Trading Backend",
            command=[python, "unified_trading_backend_v2.py"],
            port=8080,
            health_endpoint="http://localhost:8080/api/status",
            required=True,
            depends_on=["Memory MCP", "Solana MCP"]
        ))
        
        # AI services
        self.add_service(Service(
            name="Ollama",
            command=["ollama", "serve"],
            port=11434,
            health_endpoint="http://localhost:11434/api/tags",
            required=False
        ))
        
        # Integration services
        self.add_service(Service(
            name="n8n Workflows",
            command=["n8n", "start"],
            port=5678,
            health_endpoint="http://localhost:5678/healthz",
            required=False
        ))
        
        # Dashboard
        self.add_service(Service(
            name="Oracle Dashboard",
            command=[python, "oracle_v7_simple.py"],
            port=3011,
            health_endpoint="http://localhost:3011/api/status",
            required=True,
            depends_on=["Trading Backend"]
        ))
        
    def add_service(self, service: Service):
        """Add service to manager"""
        self.services[service.name] = service
        self.status[service.name] = ServiceStatus.STOPPED
        
    async def start_all(self):
        """Start all services in dependency order"""
        logger.info(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}MCPVotsAGI SYSTEM STARTUP{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Check prerequisites
        if not await self._check_prerequisites():
            logger.error("Prerequisites check failed")
            return False
            
        # Start services in dependency order
        started = set()
        
        while len(started) < len(self.services):
            made_progress = False
            
            for name, service in self.services.items():
                if name in started:
                    continue
                    
                # Check dependencies
                deps_satisfied = all(dep in started for dep in service.depends_on)
                
                if deps_satisfied:
                    success = await self._start_service(service)
                    
                    if success:
                        started.add(name)
                        made_progress = True
                    elif service.required:
                        logger.error(f"Required service {name} failed to start")
                        return False
                        
            if not made_progress:
                logger.error("Circular dependency or unresolvable services")
                return False
                
        # Show summary
        self._show_status_summary()
        
        # Start monitoring
        asyncio.create_task(self._monitor_services())
        
        return True
        
    async def _check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        logger.info("Checking prerequisites...")
        
        checks = {
            "Python version": sys.version_info >= (3, 9),
            "Available memory": psutil.virtual_memory().available > 2 * 1024**3,  # 2GB
            "Required directories": all(
                Path(d).exists() for d in ["TradingAgents", "servers", "scripts"]
            ),
            "Environment variables": all(
                os.getenv(var) for var in ["OPENAI_API_KEY", "FINNHUB_API_KEY"]
                if self.config.get("require_all_keys", False)
            )
        }
        
        all_passed = True
        for check, passed in checks.items():
            if passed:
                logger.info(f"  ✓ {check}")
            else:
                logger.error(f"  ✗ {check}")
                all_passed = False
                
        return all_passed
        
    async def _start_service(self, service: Service) -> bool:
        """Start individual service"""
        logger.info(f"Starting {service.name}...")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(service.env)
            
            # Start process
            process = subprocess.Popen(
                service.command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service.name] = process
            self.status[service.name] = ServiceStatus.STARTING
            
            # Wait for service to be ready
            if service.health_endpoint:
                ready = await self._wait_for_service(service)
                
                if ready:
                    self.status[service.name] = ServiceStatus.RUNNING
                    logger.info(f"{Fore.GREEN}  ✓ {service.name} started on port {service.port}{Style.RESET_ALL}")
                    return True
                else:
                    self.status[service.name] = ServiceStatus.FAILED
                    logger.error(f"{Fore.RED}  ✗ {service.name} health check failed{Style.RESET_ALL}")
                    process.terminate()
                    return False
            else:
                # No health check, assume started
                await asyncio.sleep(2)
                
                if process.poll() is None:
                    self.status[service.name] = ServiceStatus.RUNNING
                    logger.info(f"{Fore.GREEN}  ✓ {service.name} started{Style.RESET_ALL}")
                    return True
                else:
                    self.status[service.name] = ServiceStatus.FAILED
                    logger.error(f"{Fore.RED}  ✗ {service.name} failed to start{Style.RESET_ALL}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to start {service.name}: {e}")
            self.status[service.name] = ServiceStatus.FAILED
            return False
            
    async def _wait_for_service(self, service: Service, timeout: int = 60) -> bool:
        """Wait for service to be ready"""
        start_time = datetime.now()
        
        async with aiohttp.ClientSession() as session:
            while (datetime.now() - start_time).seconds < timeout:
                try:
                    async with session.get(service.health_endpoint, timeout=5) as resp:
                        if resp.status == 200:
                            return True
                except:
                    pass
                    
                # Check if process died
                process = self.processes.get(service.name)
                if process and process.poll() is not None:
                    # Process exited
                    stdout, stderr = process.communicate()
                    logger.error(f"{service.name} process exited")
                    if stderr:
                        logger.error(f"Error output: {stderr[:200]}")
                    return False
                    
                await asyncio.sleep(1)
                
        return False
        
    async def _monitor_services(self):
        """Monitor service health"""
        while not self._shutdown_requested:
            try:
                await asyncio.sleep(self.config.get("health_check_interval", 30))
                
                for name, service in self.services.items():
                    if self.status[name] != ServiceStatus.RUNNING:
                        continue
                        
                    # Check process
                    process = self.processes.get(name)
                    if process and process.poll() is not None:
                        logger.warning(f"{name} process died")
                        self.status[name] = ServiceStatus.FAILED
                        
                        if self.config.get("auto_restart") and service.required:
                            logger.info(f"Attempting to restart {name}")
                            await self._start_service(service)
                            
                    # Check health endpoint
                    elif service.health_endpoint:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(service.health_endpoint, timeout=5) as resp:
                                    if resp.status != 200:
                                        logger.warning(f"{name} health check failed")
                        except:
                            logger.warning(f"{name} health check error")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                
    def _show_status_summary(self):
        """Show status summary"""
        logger.info(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}SYSTEM STATUS{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        running = sum(1 for s in self.status.values() if s == ServiceStatus.RUNNING)
        total = len(self.status)
        
        for name, status in self.status.items():
            service = self.services[name]
            
            if status == ServiceStatus.RUNNING:
                color = Fore.GREEN
                symbol = "✓"
            elif status == ServiceStatus.FAILED:
                color = Fore.RED
                symbol = "✗"
            else:
                color = Fore.YELLOW
                symbol = "○"
                
            port_info = f" (port {service.port})" if service.port else ""
            logger.info(f"{color}  {symbol} {name}{port_info} - {status.value}{Style.RESET_ALL}")
            
        logger.info(f"\n{Fore.CYAN}Summary: {running}/{total} services running{Style.RESET_ALL}")
        
        # Show access URLs
        if running > 0:
            logger.info(f"\n{Fore.CYAN}Access URLs:{Style.RESET_ALL}")
            
            urls = {
                "Oracle Dashboard": "http://localhost:3011",
                "n8n Workflows": "http://localhost:5678",
                "Metrics": "http://localhost:8000",
                "Trading API": "http://localhost:8080/api/status"
            }
            
            for name, url in urls.items():
                service = self.services.get(name)
                if service and self.status.get(name) == ServiceStatus.RUNNING:
                    logger.info(f"  • {name}: {Fore.BLUE}{url}{Style.RESET_ALL}")
                    
        logger.info(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info(f"\n{Fore.YELLOW}Shutting down services...{Style.RESET_ALL}")
        self._shutdown_requested = True
        
        # Stop services in reverse order
        for name in reversed(list(self.services.keys())):
            process = self.processes.get(name)
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                process.terminate()
                
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
                self.status[name] = ServiceStatus.STOPPED
                
        logger.info(f"{Fore.GREEN}All services stopped{Style.RESET_ALL}")


class HealthCheckServer:
    """System health check server"""
    
    def __init__(self, manager: SystemManager):
        self.manager = manager
        self.app = web.Application()
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup web routes"""
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/services', self.handle_services)
        self.app.router.add_post('/restart/{service}', self.handle_restart)
        
    async def handle_health(self, request):
        """Overall system health"""
        running = sum(1 for s in self.manager.status.values() 
                     if s == ServiceStatus.RUNNING)
        total = len(self.manager.status)
        
        healthy = running == total or (
            running >= len([s for s in self.manager.services.values() if s.required])
        )
        
        return web.json_response({
            "healthy": healthy,
            "services_running": running,
            "services_total": total,
            "timestamp": datetime.now().isoformat()
        }, status=200 if healthy else 503)
        
    async def handle_services(self, request):
        """Service status details"""
        services = {}
        
        for name, service in self.manager.services.items():
            services[name] = {
                "status": self.manager.status[name].value,
                "port": service.port,
                "required": service.required,
                "health_endpoint": service.health_endpoint
            }
            
        return web.json_response(services)
        
    async def handle_restart(self, request):
        """Restart a service"""
        service_name = request.match_info['service']
        
        if service_name not in self.manager.services:
            return web.json_response({"error": "Service not found"}, status=404)
            
        # Stop service
        process = self.manager.processes.get(service_name)
        if process and process.poll() is None:
            process.terminate()
            
        # Start service
        service = self.manager.services[service_name]
        success = await self.manager._start_service(service)
        
        return web.json_response({
            "service": service_name,
            "restarted": success
        })
        
    async def start(self, port: int = 8090):
        """Start health check server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        
        logger.info(f"Health check server running on http://localhost:{port}")


async def main():
    """Main entry point"""
    manager = SystemManager()
    health_server = HealthCheckServer(manager)
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("\nReceived interrupt signal")
        asyncio.create_task(manager.shutdown())
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start health check server
        await health_server.start()
        
        # Start all services
        success = await manager.start_all()
        
        if success:
            logger.info(f"\n{Fore.GREEN}System startup complete!{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}Press Ctrl+C to shutdown{Style.RESET_ALL}\n")
            
            # Keep running
            while True:
                await asyncio.sleep(60)
        else:
            logger.error(f"\n{Fore.RED}System startup failed{Style.RESET_ALL}")
            await manager.shutdown()
            sys.exit(1)
            
    except KeyboardInterrupt:
        await manager.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await manager.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    # Check if running on Windows and need to use ProactorEventLoop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(main())