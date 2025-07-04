#!/usr/bin/env python3
"""
MCPVotsAGI Ecosystem Manager V4 - Clean Production Version
=========================================================
Comprehensive ecosystem management with F:\ drive integration, no mock data
"""

import asyncio
import json
import os
import sys
import psutil
import platform
import logging
import subprocess
import socket
import time
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import aiohttp
import websockets
import signal

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ecosystem_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EcosystemManagerV4")

# F:\ Drive Configuration
F_DRIVE_ROOT = Path("F:/MCPVotsAGI_Data") if platform.system() == "Windows" else Path("/mnt/f/MCPVotsAGI_Data")
F_DRIVE_ENABLED = F_DRIVE_ROOT.exists()

if F_DRIVE_ENABLED:
    DATA_ROOT = F_DRIVE_ROOT
    RL_DATA_PATH = DATA_ROOT / "rl_training"
    MARKET_DATA_PATH = DATA_ROOT / "market_data"
    MODEL_PATH = DATA_ROOT / "models"
    MEMORY_PATH = DATA_ROOT / "memory"
    BACKUP_PATH = DATA_ROOT / "backups"
    LOGS_PATH = DATA_ROOT / "logs"
    METRICS_PATH = DATA_ROOT / "metrics"
else:
    DATA_ROOT = Path(__file__).parent / "data"
    RL_DATA_PATH = DATA_ROOT / "rl_training"
    MARKET_DATA_PATH = DATA_ROOT / "market_data"
    MODEL_PATH = DATA_ROOT / "models"
    MEMORY_PATH = DATA_ROOT / "memory"
    BACKUP_PATH = DATA_ROOT / "backups"
    LOGS_PATH = DATA_ROOT / "logs"
    METRICS_PATH = DATA_ROOT / "metrics"

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    port: int
    command: List[str]
    priority: int = 3
    dependencies: List[str] = field(default_factory=list)
    health_check: Optional[str] = None
    critical: bool = False
    auto_restart: bool = True
    max_restarts: int = 5
    restart_delay: int = 5
    env: Dict[str, str] = field(default_factory=dict)
    startup_timeout: int = 60
    health_check_interval: int = 30

@dataclass
class ServiceHealth:
    """Service health status"""
    name: str
    port: int
    status: str  # 'healthy', 'unhealthy', 'recovering', 'stopped', 'starting'
    last_check: datetime
    response_time: float
    error_count: int
    restart_count: int
    memory_usage: float
    cpu_usage: float
    uptime: float
    health_score: float  # 0-100
    error_messages: List[str] = field(default_factory=list)

@dataclass
class SystemMetrics:
    """System-wide metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    network_usage: Dict[str, float]
    gpu_usage: Optional[float]
    temperature: Optional[float]
    load_average: List[float]
    process_count: int
    thread_count: int

class EcosystemManagerV4:
    """Production-ready ecosystem manager with F:\ drive integration"""
    
    def __init__(self):
        self.workspace = Path("C:/Workspace") if platform.system() == "Windows" else Path("/mnt/c/Workspace")
        self.mcpvots_path = self.workspace / "MCPVots"
        self.mcpvotsagi_path = self.workspace / "MCPVotsAGI"
        
        # Ensure directories exist
        for path in [DATA_ROOT, LOGS_PATH, METRICS_PATH, MEMORY_PATH]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Active processes
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.stop_event = asyncio.Event()
        
        # Initialize services
        self._init_services()
        
        # Initialize database
        self._init_database()
        
        # Performance tracking
        self.start_time = datetime.now()
        self.health_check_tasks = {}
        
    def _init_services(self):
        """Initialize service configurations"""
        self.services: Dict[str, ServiceConfig] = {}
        
        # Core Infrastructure (Priority 1)
        if self._check_command_exists("ipfs"):
            self.services["ipfs_daemon"] = ServiceConfig(
                name="IPFS Daemon",
                port=5001,
                command=["ipfs", "daemon"],
                priority=1,
                health_check="http://localhost:5001/api/v0/id",
                critical=False
            )
        
        # Ollama Service (Priority 1)
        if self._check_command_exists("ollama"):
            self.services["ollama"] = ServiceConfig(
                name="Ollama Service",
                port=11434,
                command=["ollama", "serve"],
                priority=1,
                health_check="http://localhost:11434/api/tags",
                critical=True
            )
        
        # MCP Servers (Priority 2)
        self._add_mcp_servers()
        
        # AGI Services (Priority 3)
        self._add_agi_services()
        
        # Trading & Analytics (Priority 4)
        self._add_trading_services()
        
    def _add_mcp_servers(self):
        """Add MCP server configurations"""
        mcp_servers = [
            {
                "id": "memory_mcp",
                "name": "Memory MCP",
                "port": 3002,
                "script": "servers/enhanced_memory_mcp_server.py",
                "critical": True,
                "workspace": "MCPVots"
            },
            {
                "id": "github_mcp",
                "name": "GitHub MCP",
                "port": 3001,
                "script": "servers/mcp_github_server.py",
                "env": {"GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "")},
                "workspace": "MCPVots"
            },
            {
                "id": "solana_mcp",
                "name": "Solana MCP",
                "port": 3005,
                "script": "solana_mcp_deepseek_integration.py",
                "workspace": "MCPVotsAGI"
            },
            {
                "id": "deepseek_mcp",
                "name": "DeepSeek MCP",
                "port": 3008,
                "script": "servers/deepseek_ollama_mcp_server.py",
                "dependencies": ["ollama"],
                "critical": True,
                "env": {
                    "OLLAMA_HOST": "http://localhost:11434",
                    "DEEPSEEK_MODEL": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
                },
                "workspace": "MCPVotsAGI"
            },
            {
                "id": "opencti_mcp",
                "name": "OpenCTI MCP",
                "port": 3007,
                "script": "servers/opencti_mcp_server.py",
                "env": {"OPENCTI_URL": os.environ.get("OPENCTI_URL", "http://localhost:8080")},
                "workspace": "MCPVotsAGI"
            }
        ]
        
        for mcp in mcp_servers:
            workspace = self.mcpvots_path if mcp.get("workspace") == "MCPVots" else self.mcpvotsagi_path
            script_path = workspace / mcp["script"]
            
            if script_path.exists():
                self.services[mcp["id"]] = ServiceConfig(
                    name=mcp["name"],
                    port=mcp["port"],
                    command=[sys.executable, str(script_path)],
                    priority=2,
                    dependencies=mcp.get("dependencies", []),
                    health_check=f"ws://localhost:{mcp['port']}",
                    critical=mcp.get("critical", False),
                    env=mcp.get("env", {})
                )
            else:
                logger.warning(f"Script not found: {script_path}")
    
    def _add_agi_services(self):
        """Add AGI service configurations"""
        agi_services = [
            {
                "id": "oracle_agi_dashboard",
                "name": "Oracle AGI Dashboard",
                "port": 3011,
                "script": "oracle_agi_v6_realtime_dashboard.py",
                "dependencies": ["deepseek_mcp", "memory_mcp"],
                "critical": True
            },
            {
                "id": "deepseek_trading",
                "name": "DeepSeek Trading Agent",
                "port": 3009,
                "script": "deepseek_trading_agent_enhanced.py",
                "dependencies": ["deepseek_mcp", "solana_mcp"]
            }
        ]
        
        for agi in agi_services:
            script_path = self.mcpvotsagi_path / agi["script"]
            
            if script_path.exists():
                self.services[agi["id"]] = ServiceConfig(
                    name=agi["name"],
                    port=agi["port"],
                    command=[sys.executable, str(script_path)],
                    priority=3,
                    dependencies=agi.get("dependencies", []),
                    health_check=f"http://localhost:{agi['port']}/health",
                    critical=agi.get("critical", False)
                )
    
    def _add_trading_services(self):
        """Add trading and analytics services"""
        if F_DRIVE_ENABLED:
            # Add data pipeline service
            pipeline_script = self.mcpvotsagi_path / "market_data_pipeline.py"
            if pipeline_script.exists():
                self.services["data_pipeline"] = ServiceConfig(
                    name="Market Data Pipeline",
                    port=0,  # No web port
                    command=[sys.executable, str(pipeline_script)],
                    priority=4,
                    auto_restart=True
                )
            
            # Add performance monitor
            monitor_script = self.mcpvotsagi_path / "performance_monitor.py"
            if monitor_script.exists():
                self.services["performance_monitor"] = ServiceConfig(
                    name="Performance Monitor",
                    port=0,  # No web port
                    command=[sys.executable, str(monitor_script)],
                    priority=4,
                    auto_restart=True
                )
    
    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system"""
        try:
            subprocess.run([command, "--version"], capture_output=True)
            return True
        except:
            return False
    
    def _init_database(self):
        """Initialize ecosystem database"""
        db_path = METRICS_PATH / "ecosystem.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Service health history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                status TEXT NOT NULL,
                response_time REAL,
                cpu_usage REAL,
                memory_usage REAL,
                error_message TEXT,
                INDEX idx_service_time (service_id, timestamp)
            )
        ''')
        
        # System metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_mbps REAL,
                process_count INTEGER,
                thread_count INTEGER,
                INDEX idx_timestamp (timestamp)
            )
        ''')
        
        # Service events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                details TEXT,
                INDEX idx_service_event (service_id, timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start_ecosystem(self):
        """Start the complete ecosystem"""
        logger.info("🚀 Starting MCPVotsAGI Ecosystem V4...")
        
        # Check F:\ drive
        if F_DRIVE_ENABLED:
            disk = psutil.disk_usage(str(F_DRIVE_ROOT))
            logger.info(f"💾 F:\\ Drive: {disk.free / (1024**3):.2f} GB free of {disk.total / (1024**3):.2f} GB")
        else:
            logger.warning("⚠️ F:\\ Drive not available - using local storage")
        
        # Start services by priority
        for priority in range(1, 5):
            services_to_start = [
                (sid, svc) for sid, svc in self.services.items()
                if svc.priority == priority
            ]
            
            if services_to_start:
                logger.info(f"Starting priority {priority} services...")
                await self._start_services_batch(services_to_start)
                await asyncio.sleep(2)  # Allow services to stabilize
        
        # Start monitoring
        asyncio.create_task(self._monitor_system())
        asyncio.create_task(self._health_check_loop())
        
        logger.info("✅ Ecosystem started successfully!")
        logger.info("🌐 Dashboard: http://localhost:3011")
    
    async def _start_services_batch(self, services: List[Tuple[str, ServiceConfig]]):
        """Start a batch of services"""
        tasks = []
        for service_id, config in services:
            # Check dependencies
            deps_ready = all(
                dep in self.processes and self._is_service_healthy(dep)
                for dep in config.dependencies
            )
            
            if deps_ready:
                tasks.append(self._start_service(service_id, config))
            else:
                logger.warning(f"Dependencies not ready for {config.name}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _start_service(self, service_id: str, config: ServiceConfig):
        """Start a single service"""
        if service_id in self.processes:
            logger.info(f"{config.name} already running")
            return
        
        try:
            logger.info(f"Starting {config.name}...")
            
            # Set up environment
            env = os.environ.copy()
            env.update(config.env)
            
            # Add Python path
            env["PYTHONPATH"] = f"{self.mcpvots_path};{self.mcpvotsagi_path}"
            
            # Start process
            process = subprocess.Popen(
                config.command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.workspace)
            )
            
            self.processes[service_id] = process
            
            # Initialize health status
            self.service_health[service_id] = ServiceHealth(
                name=config.name,
                port=config.port,
                status="starting",
                last_check=datetime.now(),
                response_time=0,
                error_count=0,
                restart_count=0,
                memory_usage=0,
                cpu_usage=0,
                uptime=0,
                health_score=0
            )
            
            # Log event
            await self._log_service_event(service_id, "started", f"PID: {process.pid}")
            
            # Wait for service to be ready
            await self._wait_for_service(service_id, config)
            
        except Exception as e:
            logger.error(f"Failed to start {config.name}: {e}")
            await self._log_service_event(service_id, "start_failed", str(e))
    
    async def _wait_for_service(self, service_id: str, config: ServiceConfig):
        """Wait for service to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < config.startup_timeout:
            if await self._check_service_health_once(service_id, config):
                logger.info(f"✓ {config.name} is ready")
                self.service_health[service_id].status = "healthy"
                return
            
            await asyncio.sleep(1)
        
        logger.warning(f"⚠️ {config.name} failed to start within timeout")
        self.service_health[service_id].status = "unhealthy"
    
    async def _check_service_health_once(self, service_id: str, config: ServiceConfig) -> bool:
        """Check service health once"""
        if not config.health_check:
            # No health check defined, assume healthy if process is running
            process = self.processes.get(service_id)
            return process and process.poll() is None
        
        start_time = time.time()
        
        try:
            if config.health_check.startswith("http"):
                # HTTP health check
                async with aiohttp.ClientSession() as session:
                    async with session.get(config.health_check, timeout=5) as response:
                        healthy = response.status == 200
                        
            elif config.health_check.startswith("ws"):
                # WebSocket health check
                async with websockets.connect(config.health_check, timeout=5) as ws:
                    await ws.ping()
                    healthy = True
            else:
                healthy = False
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if service_id in self.service_health:
                self.service_health[service_id].response_time = response_time
                self.service_health[service_id].last_check = datetime.now()
                if healthy:
                    self.service_health[service_id].error_count = 0
            
            return healthy
            
        except Exception as e:
            if service_id in self.service_health:
                self.service_health[service_id].error_count += 1
                self.service_health[service_id].error_messages.append(str(e))
            return False
    
    def _is_service_healthy(self, service_id: str) -> bool:
        """Check if service is considered healthy"""
        health = self.service_health.get(service_id)
        return health and health.status == "healthy"
    
    async def _health_check_loop(self):
        """Continuous health checking"""
        while not self.stop_event.is_set():
            try:
                for service_id, config in self.services.items():
                    if service_id in self.processes:
                        healthy = await self._check_service_health_once(service_id, config)
                        
                        if service_id in self.service_health:
                            old_status = self.service_health[service_id].status
                            new_status = "healthy" if healthy else "unhealthy"
                            
                            if old_status != new_status:
                                self.service_health[service_id].status = new_status
                                await self._log_service_event(
                                    service_id, 
                                    f"status_changed_{new_status}",
                                    f"Health check {'passed' if healthy else 'failed'}"
                                )
                                
                                # Handle unhealthy critical services
                                if not healthy and config.critical:
                                    logger.error(f"❌ Critical service {config.name} is unhealthy!")
                                    if config.auto_restart:
                                        await self._restart_service(service_id, config)
                
                # Store health metrics
                await self._store_health_metrics()
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def _restart_service(self, service_id: str, config: ServiceConfig):
        """Restart a service"""
        health = self.service_health.get(service_id)
        if health and health.restart_count >= config.max_restarts:
            logger.error(f"Service {config.name} exceeded max restarts")
            return
        
        logger.info(f"Restarting {config.name}...")
        
        # Stop the service
        await self._stop_service(service_id)
        
        # Wait before restart
        await asyncio.sleep(config.restart_delay)
        
        # Start the service
        await self._start_service(service_id, config)
        
        if health:
            health.restart_count += 1
    
    async def _stop_service(self, service_id: str):
        """Stop a service gracefully"""
        process = self.processes.get(service_id)
        if not process:
            return
        
        config = self.services.get(service_id)
        if config:
            logger.info(f"Stopping {config.name}...")
        
        # Try graceful shutdown
        process.terminate()
        
        try:
            await asyncio.wait_for(
                asyncio.create_subprocess_exec(*["taskkill", "/PID", str(process.pid), "/F"]),
                timeout=10
            )
        except asyncio.TimeoutError:
            # Force kill if needed
            process.kill()
        
        del self.processes[service_id]
        
        if service_id in self.service_health:
            self.service_health[service_id].status = "stopped"
        
        await self._log_service_event(service_id, "stopped", "Service stopped")
    
    async def _monitor_system(self):
        """Monitor system resources"""
        while not self.stop_event.is_set():
            try:
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_usage={
                        "system": psutil.disk_usage("/").percent,
                        "f_drive": psutil.disk_usage(str(F_DRIVE_ROOT)).percent if F_DRIVE_ENABLED else 0
                    },
                    network_usage=self._get_network_usage(),
                    gpu_usage=self._get_gpu_usage(),
                    temperature=self._get_temperature(),
                    load_average=psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                    process_count=len(psutil.pids()),
                    thread_count=sum(p.num_threads() for p in psutil.process_iter(['num_threads']))
                )
                
                # Store metrics
                await self._store_system_metrics(metrics)
                
                # Check for resource issues
                if metrics.cpu_percent > 90:
                    logger.warning(f"⚠️ High CPU usage: {metrics.cpu_percent}%")
                
                if metrics.memory_percent > 90:
                    logger.warning(f"⚠️ High memory usage: {metrics.memory_percent}%")
                
                if F_DRIVE_ENABLED and metrics.disk_usage["f_drive"] > 90:
                    logger.warning(f"⚠️ F:\\ drive usage above 90%")
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
            
            await asyncio.sleep(60)  # Check every minute
    
    def _get_network_usage(self) -> Dict[str, float]:
        """Get network usage statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            return {}
    
    def _get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage if available"""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return util.gpu
        except:
            return None
    
    def _get_temperature(self) -> Optional[float]:
        """Get system temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.label == "Package id 0" or entry.label == "CPU":
                            return entry.current
        except:
            return None
    
    async def _store_health_metrics(self):
        """Store service health metrics to database"""
        db_path = METRICS_PATH / "ecosystem.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for service_id, health in self.service_health.items():
            cursor.execute('''
                INSERT INTO service_health 
                (service_id, timestamp, status, response_time, cpu_usage, memory_usage, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                service_id,
                time.time(),
                health.status,
                health.response_time,
                health.cpu_usage,
                health.memory_usage,
                health.error_messages[-1] if health.error_messages else None
            ))
        
        conn.commit()
        conn.close()
    
    async def _store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics to database"""
        db_path = METRICS_PATH / "ecosystem.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics 
            (timestamp, cpu_percent, memory_percent, disk_percent, network_mbps, process_count, thread_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            time.time(),
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.disk_usage.get("f_drive", metrics.disk_usage.get("system", 0)),
            0,  # Calculate from network usage if needed
            metrics.process_count,
            metrics.thread_count
        ))
        
        conn.commit()
        conn.close()
    
    async def _log_service_event(self, service_id: str, event_type: str, details: str = ""):
        """Log service event to database"""
        db_path = METRICS_PATH / "ecosystem.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO service_events (service_id, event_type, timestamp, details)
            VALUES (?, ?, ?, ?)
        ''', (service_id, event_type, time.time(), details))
        
        conn.commit()
        conn.close()
    
    async def stop_ecosystem(self):
        """Stop all services gracefully"""
        logger.info("Stopping ecosystem...")
        
        self.stop_event.set()
        
        # Stop services in reverse priority order
        for priority in range(4, 0, -1):
            services_to_stop = [
                sid for sid, svc in self.services.items()
                if svc.priority == priority and sid in self.processes
            ]
            
            if services_to_stop:
                logger.info(f"Stopping priority {priority} services...")
                for service_id in services_to_stop:
                    await self._stop_service(service_id)
        
        logger.info("✅ Ecosystem stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current ecosystem status"""
        return {
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "f_drive_enabled": F_DRIVE_ENABLED,
            "services": {
                sid: {
                    "name": self.services[sid].name,
                    "status": self.service_health.get(sid, {}).status if sid in self.service_health else "stopped",
                    "port": self.services[sid].port,
                    "health_score": self.service_health.get(sid, {}).health_score if sid in self.service_health else 0
                }
                for sid in self.services
            },
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_free_gb": psutil.disk_usage(str(F_DRIVE_ROOT)).free / (1024**3) if F_DRIVE_ENABLED else 0
            }
        }

async def main():
    """Main entry point"""
    manager = EcosystemManagerV4()
    
    # Handle shutdown signals
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(manager.stop_ecosystem())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await manager.start_ecosystem()
        
        # Keep running
        await manager.stop_event.wait()
        
    except Exception as e:
        logger.error(f"Ecosystem error: {e}")
        await manager.stop_ecosystem()

if __name__ == "__main__":
    asyncio.run(main())