#!/usr/bin/env python3
"""
MCPVotsAGI Ecosystem Core
========================
Unified, optimized ecosystem management system with proper error handling,
service discovery, and resource management.
"""

import asyncio
import json
import yaml
import os
import sys
import psutil
import platform
import logging
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import aiohttp
import structlog
from contextlib import asynccontextmanager
import sqlite3
import aiosqlite

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class ServiceState(Enum):
    """Service states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"

class ServicePriority(Enum):
    """Service priority levels"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    command: List[str]
    port: int
    priority: ServicePriority = ServicePriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    health_check: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    restart_policy: str = "on-failure"
    max_restarts: int = 3
    startup_timeout: int = 30
    shutdown_timeout: int = 10
    resource_limits: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceHealth:
    """Service health information"""
    state: ServiceState
    uptime: timedelta
    restart_count: int
    last_health_check: datetime
    health_score: float
    metrics: Dict[str, Any]
    errors: List[str]

class CircuitBreaker:
    """Circuit breaker for service failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_time: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure = None
        self.state = "closed"  # closed, open, half-open
        
    def record_failure(self):
        """Record a failure"""
        self.failures += 1
        self.last_failure = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning("circuit_breaker_opened", failures=self.failures)
            
    def record_success(self):
        """Record a success"""
        self.failures = 0
        self.state = "closed"
        
    def can_attempt(self) -> bool:
        """Check if we can attempt operation"""
        if self.state == "closed":
            return True
            
        if self.state == "open":
            if (datetime.now() - self.last_failure).seconds > self.recovery_time:
                self.state = "half-open"
                return True
            return False
            
        return True  # half-open state

class ResourceManager:
    """Manage system resources"""
    
    def __init__(self):
        self.cpu_threshold = 80
        self.memory_threshold = 85
        self.disk_threshold = 90
        
    async def check_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "threshold_exceeded": psutil.cpu_percent() > self.cpu_threshold
            },
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available_gb": psutil.virtual_memory().available / (1024**3),
                "threshold_exceeded": psutil.virtual_memory().percent > self.memory_threshold
            },
            "disk": {
                "percent": psutil.disk_usage('/').percent,
                "free_gb": psutil.disk_usage('/').free / (1024**3),
                "threshold_exceeded": psutil.disk_usage('/').percent > self.disk_threshold
            }
        }
    
    async def can_start_service(self, service_config: ServiceConfig) -> Tuple[bool, str]:
        """Check if we have resources to start service"""
        resources = await self.check_resources()
        
        # Check resource limits
        limits = service_config.resource_limits
        
        if limits.get("min_memory_gb"):
            if resources["memory"]["available_gb"] < limits["min_memory_gb"]:
                return False, f"Insufficient memory: {resources['memory']['available_gb']:.1f}GB available"
                
        if resources["cpu"]["threshold_exceeded"]:
            return False, f"CPU usage too high: {resources['cpu']['percent']}%"
            
        if resources["memory"]["threshold_exceeded"]:
            return False, f"Memory usage too high: {resources['memory']['percent']}%"
            
        return True, "OK"

class ServiceRegistry:
    """Service discovery and registry"""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.health: Dict[str, ServiceHealth] = {}
        self.processes: Dict[str, Any] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
    def register(self, service_id: str, config: ServiceConfig):
        """Register a service"""
        self.services[service_id] = config
        self.circuit_breakers[service_id] = CircuitBreaker()
        logger.info("service_registered", service=service_id, port=config.port)
        
    def get_service(self, service_id: str) -> Optional[ServiceConfig]:
        """Get service configuration"""
        return self.services.get(service_id)
        
    def get_dependencies(self, service_id: str) -> List[str]:
        """Get service dependencies"""
        service = self.services.get(service_id)
        return service.dependencies if service else []
        
    def get_dependents(self, service_id: str) -> List[str]:
        """Get services that depend on this service"""
        dependents = []
        for sid, config in self.services.items():
            if service_id in config.dependencies:
                dependents.append(sid)
        return dependents

class ConnectionPool:
    """HTTP connection pool for health checks"""
    
    def __init__(self, size: int = 10):
        self.size = size
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=self.size),
            timeout=aiohttp.ClientTimeout(total=5)
        )
        return self._session
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

class EcosystemCore:
    """Core ecosystem management system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
        self.config_path = config_path or self.workspace / "ecosystem_config.yaml"
        
        # Core components
        self.registry = ServiceRegistry()
        self.resource_manager = ResourceManager()
        self.connection_pool = ConnectionPool()
        
        # Runtime state
        self.running = False
        self.shutdown_event = asyncio.Event()
        self.health_check_task = None
        self.resource_monitor_task = None
        
        # Configuration
        self.config = self._load_configuration()
        self._register_services()
        
        # Database
        self.db_path = self.workspace / "ecosystem_core.db"
        self._init_database()
        
    def _load_configuration(self) -> Dict[str, Any]:
        """Load ecosystem configuration"""
        default_config = {
            "mode": "development",
            "health_check_interval": 30,
            "resource_check_interval": 60,
            "max_startup_time": 300,
            "enable_auto_recovery": True,
            "enable_metrics": True
        }
        
        if self.config_path.exists():
            with open(self.config_path) as f:
                loaded_config = yaml.safe_load(f)
                default_config.update(loaded_config)
                
        return default_config
        
    def _register_services(self):
        """Register all services"""
        # Core services
        self.registry.register("memory_mcp", ServiceConfig(
            name="Memory MCP Server",
            command=["python", str(self.workspace / "servers" / "enhanced_memory_mcp_server.py")],
            port=3002,
            priority=ServicePriority.CRITICAL,
            health_check="ws://localhost:3002/health",
            restart_policy="always",
            resource_limits={"min_memory_gb": 0.5}
        ))
        
        self.registry.register("github_mcp", ServiceConfig(
            name="GitHub MCP Server",
            command=["python", str(self.workspace / "servers" / "mcp_github_server.py")],
            port=3001,
            priority=ServicePriority.HIGH,
            health_check="ws://localhost:3001/health",
            env={"GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "")}
        ))
        
        self.registry.register("solana_mcp", ServiceConfig(
            name="Solana MCP Server",
            command=["python", str(self.workspace / "solana_mcp_deepseek_integration.py")],
            port=3005,
            priority=ServicePriority.MEDIUM,
            health_check="ws://localhost:3005/health",
            dependencies=["memory_mcp"]
        ))
        
        self.registry.register("oracle_agi", ServiceConfig(
            name="Oracle AGI Dashboard",
            command=["python", str(self.workspace / "oracle_agi_ultimate_unified_v2.py")],
            port=3011,
            priority=ServicePriority.LOW,
            health_check="http://localhost:3011/api/status",
            dependencies=["memory_mcp", "github_mcp"],
            startup_timeout=60
        ))
        
        # Add more services as needed...
        
    def _init_database(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                service_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                severity TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                service_id TEXT NOT NULL,
                state TEXT NOT NULL,
                health_score REAL,
                metrics TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def start(self):
        """Start the ecosystem"""
        logger.info("ecosystem_starting", mode=self.config["mode"])
        
        self.running = True
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start resource monitoring
        self.resource_monitor_task = asyncio.create_task(self._monitor_resources())
        
        # Start services by priority
        await self._start_services_by_priority()
        
        # Start health monitoring
        self.health_check_task = asyncio.create_task(self._monitor_health())
        
        logger.info("ecosystem_started")
        
        # Wait for shutdown
        await self.shutdown_event.wait()
        
    async def _start_services_by_priority(self):
        """Start services in priority order"""
        # Group by priority
        priority_groups: Dict[ServicePriority, List[str]] = {}
        
        for service_id, config in self.registry.services.items():
            if config.priority not in priority_groups:
                priority_groups[config.priority] = []
            priority_groups[config.priority].append(service_id)
            
        # Start in priority order
        for priority in sorted(priority_groups.keys(), key=lambda x: x.value):
            services = priority_groups[priority]
            logger.info("starting_priority_group", priority=priority.name, services=services)
            
            # Start services in parallel within priority group
            tasks = [self._start_service(sid) for sid in services]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for service_id, result in zip(services, results):
                if isinstance(result, Exception):
                    logger.error("service_start_failed", 
                        service=service_id, 
                        error=str(result),
                        exc_info=result
                    )
                    
            # Brief delay between priority groups
            await asyncio.sleep(2)
            
    async def _start_service(self, service_id: str) -> bool:
        """Start a single service with retry logic"""
        config = self.registry.get_service(service_id)
        if not config:
            return False
            
        circuit_breaker = self.registry.circuit_breakers[service_id]
        
        for attempt in range(config.max_restarts):
            if not circuit_breaker.can_attempt():
                logger.warning("circuit_breaker_open", service=service_id)
                return False
                
            try:
                # Check dependencies
                for dep in config.dependencies:
                    dep_health = self.registry.health.get(dep)
                    if not dep_health or dep_health.state != ServiceState.RUNNING:
                        logger.warning("dependency_not_ready", 
                            service=service_id, 
                            dependency=dep
                        )
                        await asyncio.sleep(5)
                        continue
                        
                # Check resources
                can_start, reason = await self.resource_manager.can_start_service(config)
                if not can_start:
                    logger.warning("insufficient_resources", 
                        service=service_id, 
                        reason=reason
                    )
                    await asyncio.sleep(10)
                    continue
                    
                # Start the service
                logger.info("starting_service", service=service_id, attempt=attempt+1)
                
                process = await asyncio.create_subprocess_exec(
                    *config.command,
                    env={**os.environ, **config.env},
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                self.registry.processes[service_id] = process
                
                # Wait for service to be healthy
                healthy = await self._wait_for_health(service_id, config.startup_timeout)
                
                if healthy:
                    circuit_breaker.record_success()
                    logger.info("service_started", service=service_id)
                    await self._record_event(service_id, "started", "Service started successfully")
                    return True
                else:
                    raise Exception("Service failed health check")
                    
            except Exception as e:
                circuit_breaker.record_failure()
                logger.error("service_start_error", 
                    service=service_id, 
                    attempt=attempt+1,
                    error=str(e)
                )
                await self._record_event(service_id, "start_failed", str(e), "error")
                
                if attempt < config.max_restarts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        return False
        
    async def _wait_for_health(self, service_id: str, timeout: int) -> bool:
        """Wait for service to become healthy"""
        config = self.registry.get_service(service_id)
        if not config or not config.health_check:
            return True  # No health check defined
            
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                async with self.connection_pool as session:
                    if config.health_check.startswith("http"):
                        async with session.get(config.health_check) as response:
                            if response.status == 200:
                                return True
                    elif config.health_check.startswith("ws"):
                        # WebSocket health check
                        import websockets
                        async with websockets.connect(config.health_check) as ws:
                            await ws.ping()
                            return True
            except:
                pass
                
            await asyncio.sleep(1)
            
        return False
        
    async def _monitor_health(self):
        """Monitor service health"""
        while self.running:
            try:
                async with self.connection_pool as session:
                    for service_id, config in self.registry.services.items():
                        if service_id in self.registry.processes:
                            health = await self._check_service_health(service_id, config, session)
                            self.registry.health[service_id] = health
                            
                            # Record metrics
                            await self._record_health_metrics(service_id, health)
                            
                            # Auto-recovery if enabled
                            if self.config["enable_auto_recovery"]:
                                if health.state == ServiceState.FAILED:
                                    logger.warning("auto_recovery_triggered", service=service_id)
                                    asyncio.create_task(self._start_service(service_id))
                                    
            except Exception as e:
                logger.error("health_monitor_error", error=str(e))
                
            await asyncio.sleep(self.config["health_check_interval"])
            
    async def _check_service_health(self, service_id: str, config: ServiceConfig, session: aiohttp.ClientSession) -> ServiceHealth:
        """Check health of a single service"""
        process = self.registry.processes.get(service_id)
        
        # Default health
        health = ServiceHealth(
            state=ServiceState.STOPPED,
            uptime=timedelta(0),
            restart_count=0,
            last_health_check=datetime.now(),
            health_score=0.0,
            metrics={},
            errors=[]
        )
        
        if not process:
            return health
            
        # Check if process is running
        if process.returncode is not None:
            health.state = ServiceState.FAILED
            health.errors.append(f"Process exited with code {process.returncode}")
            return health
            
        # Perform health check
        if config.health_check:
            try:
                if config.health_check.startswith("http"):
                    async with session.get(config.health_check) as response:
                        if response.status == 200:
                            health.state = ServiceState.RUNNING
                            health.health_score = 100.0
                            data = await response.json()
                            health.metrics = data.get("metrics", {})
                        else:
                            health.state = ServiceState.DEGRADED
                            health.health_score = 50.0
                elif config.health_check.startswith("ws"):
                    # WebSocket health check
                    import websockets
                    async with websockets.connect(config.health_check, timeout=5) as ws:
                        await ws.ping()
                        health.state = ServiceState.RUNNING
                        health.health_score = 100.0
            except Exception as e:
                health.state = ServiceState.DEGRADED
                health.errors.append(str(e))
                health.health_score = 25.0
        else:
            # No health check, assume running if process is alive
            health.state = ServiceState.RUNNING
            health.health_score = 75.0
            
        return health
        
    async def _monitor_resources(self):
        """Monitor system resources"""
        while self.running:
            try:
                resources = await self.resource_manager.check_resources()
                
                # Log resource status
                logger.info("resource_status",
                    cpu_percent=resources["cpu"]["percent"],
                    memory_percent=resources["memory"]["percent"],
                    disk_percent=resources["disk"]["percent"]
                )
                
                # Alert on threshold exceeded
                for resource_type, data in resources.items():
                    if data.get("threshold_exceeded"):
                        logger.warning("resource_threshold_exceeded",
                            resource=resource_type,
                            percent=data["percent"]
                        )
                        
            except Exception as e:
                logger.error("resource_monitor_error", error=str(e))
                
            await asyncio.sleep(self.config["resource_check_interval"])
            
    async def _record_event(self, service_id: str, event_type: str, details: str, severity: str = "info"):
        """Record service event to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO service_events (service_id, event_type, details, severity)
                VALUES (?, ?, ?, ?)
            ''', (service_id, event_type, details, severity))
            await db.commit()
            
    async def _record_health_metrics(self, service_id: str, health: ServiceHealth):
        """Record health metrics to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO health_metrics (service_id, state, health_score, metrics)
                VALUES (?, ?, ?, ?)
            ''', (service_id, health.state.value, health.health_score, json.dumps(health.metrics)))
            await db.commit()
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("shutdown_signal_received", signal=signum)
        asyncio.create_task(self.shutdown())
        
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("ecosystem_shutdown_starting")
        self.running = False
        
        # Stop health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
            
        if self.resource_monitor_task:
            self.resource_monitor_task.cancel()
            
        # Stop services in reverse priority order
        priority_groups: Dict[ServicePriority, List[str]] = {}
        
        for service_id, config in self.registry.services.items():
            if config.priority not in priority_groups:
                priority_groups[config.priority] = []
            priority_groups[config.priority].append(service_id)
            
        # Stop in reverse priority order
        for priority in sorted(priority_groups.keys(), key=lambda x: x.value, reverse=True):
            services = priority_groups[priority]
            logger.info("stopping_priority_group", priority=priority.name, services=services)
            
            tasks = [self._stop_service(sid) for sid in services]
            await asyncio.gather(*tasks, return_exceptions=True)
            
        logger.info("ecosystem_shutdown_complete")
        self.shutdown_event.set()
        
    async def _stop_service(self, service_id: str):
        """Stop a service gracefully"""
        config = self.registry.get_service(service_id)
        process = self.registry.processes.get(service_id)
        
        if not process or process.returncode is not None:
            return
            
        logger.info("stopping_service", service=service_id)
        
        try:
            # Send terminate signal
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(
                    process.wait(),
                    timeout=config.shutdown_timeout if config else 10
                )
            except asyncio.TimeoutError:
                # Force kill if needed
                logger.warning("force_killing_service", service=service_id)
                process.kill()
                await process.wait()
                
            await self._record_event(service_id, "stopped", "Service stopped")
            
        except Exception as e:
            logger.error("service_stop_error", service=service_id, error=str(e))
            
    async def get_status(self) -> Dict[str, Any]:
        """Get ecosystem status"""
        status = {
            "running": self.running,
            "mode": self.config["mode"],
            "services": {},
            "resources": await self.resource_manager.check_resources()
        }
        
        for service_id, config in self.registry.services.items():
            health = self.registry.health.get(service_id)
            status["services"][service_id] = {
                "name": config.name,
                "port": config.port,
                "state": health.state.value if health else "unknown",
                "health_score": health.health_score if health else 0,
                "uptime": str(health.uptime) if health else "0:00:00",
                "errors": health.errors if health else []
            }
            
        return status


async def main():
    """Main entry point"""
    ecosystem = EcosystemCore()
    
    try:
        await ecosystem.start()
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt")
    except Exception as e:
        logger.error("ecosystem_error", error=str(e), exc_info=e)
    finally:
        await ecosystem.shutdown()


if __name__ == "__main__":
    asyncio.run(main())