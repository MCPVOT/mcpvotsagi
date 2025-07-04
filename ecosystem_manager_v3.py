#!/usr/bin/env python3
"""
MCPVotsAGI Ecosystem Manager V3
===============================
Enhanced with F:\ drive storage, advanced self-healing, and real-time monitoring
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
import yaml
import aiohttp
import websockets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
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
logger = logging.getLogger("EcosystemManagerV3")

# F:\ Drive Configuration
F_DRIVE_ROOT = Path("F:/MCPVotsAGI_Data")
ECOSYSTEM_DATA_PATH = F_DRIVE_ROOT / "ecosystem"
LOGS_PATH = F_DRIVE_ROOT / "logs"
METRICS_PATH = F_DRIVE_ROOT / "metrics"
BACKUPS_PATH = F_DRIVE_ROOT / "backups"

@dataclass
class ServiceConfig:
    """Enhanced service configuration"""
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
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    startup_timeout: int = 60
    health_check_interval: int = 30
    health_check_timeout: int = 10

@dataclass
class ServiceHealth:
    """Enhanced service health status"""
    name: str
    port: int
    status: str  # 'healthy', 'unhealthy', 'recovering', 'stopped', 'starting'
    last_check: datetime
    response_time: float
    error_count: int
    restart_count: int
    memory_usage: float
    cpu_usage: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
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
    open_files: int

class AdvancedHealthMonitor:
    """Advanced health monitoring with predictive capabilities"""
    
    def __init__(self, metrics_path: Path):
        self.metrics_path = metrics_path
        self.metrics_db = metrics_path / "health_metrics.db"
        self.anomaly_threshold = 2.5  # Standard deviations
        self.prediction_window = 300  # 5 minutes
        self._init_database()
        
    def _init_database(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_metrics (
                timestamp REAL,
                service_name TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                response_time REAL,
                error_rate REAL,
                health_score REAL,
                PRIMARY KEY (timestamp, service_name)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                timestamp REAL PRIMARY KEY,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage REAL,
                network_in REAL,
                network_out REAL,
                temperature REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                timestamp REAL,
                service_name TEXT,
                metric_name TEXT,
                value REAL,
                expected_range TEXT,
                severity TEXT,
                action_taken TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
    async def record_service_metrics(self, service_name: str, health: ServiceHealth):
        """Record service metrics for analysis"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO service_metrics 
            (timestamp, service_name, cpu_usage, memory_usage, response_time, error_rate, health_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            time.time(),
            service_name,
            health.cpu_usage,
            health.memory_usage,
            health.response_time,
            health.error_count / max(health.uptime, 1),  # Error rate per second
            health.health_score
        ))
        
        conn.commit()
        conn.close()
        
    async def predict_failure(self, service_name: str) -> Dict[str, Any]:
        """Predict potential service failure using historical data"""
        conn = sqlite3.connect(self.metrics_db)
        
        # Get recent metrics
        df = pd.read_sql_query("""
            SELECT * FROM service_metrics
            WHERE service_name = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 100
        """, conn, params=(service_name, time.time() - 3600))  # Last hour
        
        conn.close()
        
        if df.empty:
            return {"prediction": "unknown", "confidence": 0}
            
        # Simple prediction based on trends
        cpu_trend = df['cpu_usage'].diff().mean()
        memory_trend = df['memory_usage'].diff().mean()
        error_trend = df['error_rate'].diff().mean()
        
        risk_score = 0
        if cpu_trend > 1:  # CPU increasing by 1% per measurement
            risk_score += 30
        if memory_trend > 0.5:  # Memory increasing
            risk_score += 30
        if error_trend > 0:  # Errors increasing
            risk_score += 40
            
        return {
            "prediction": "failure_likely" if risk_score > 60 else "stable",
            "confidence": min(risk_score / 100, 1.0),
            "risk_score": risk_score,
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "error_trend": error_trend
        }
        
    async def detect_anomalies(self, service_name: str, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect anomalies in service metrics"""
        conn = sqlite3.connect(self.metrics_db)
        
        # Get historical data for baseline
        df = pd.read_sql_query("""
            SELECT cpu_usage, memory_usage, response_time, error_rate
            FROM service_metrics
            WHERE service_name = ? AND timestamp > ?
        """, conn, params=(service_name, time.time() - 86400))  # Last 24 hours
        
        conn.close()
        
        anomalies = []
        
        if not df.empty:
            for metric, value in current_metrics.items():
                if metric in df.columns:
                    mean = df[metric].mean()
                    std = df[metric].std()
                    
                    if std > 0:
                        z_score = abs((value - mean) / std)
                        
                        if z_score > self.anomaly_threshold:
                            anomalies.append({
                                "metric": metric,
                                "value": value,
                                "expected_mean": mean,
                                "expected_std": std,
                                "z_score": z_score,
                                "severity": "high" if z_score > 4 else "medium"
                            })
                            
        return anomalies

class SelfHealingEngine:
    """Enhanced self-healing capabilities"""
    
    def __init__(self, ecosystem_manager):
        self.ecosystem = ecosystem_manager
        self.healing_strategies = {
            "high_memory": self._heal_high_memory,
            "high_cpu": self._heal_high_cpu,
            "unresponsive": self._heal_unresponsive,
            "dependency_failure": self._heal_dependency_failure,
            "port_conflict": self._heal_port_conflict,
            "disk_space": self._heal_disk_space,
            "network_issue": self._heal_network_issue
        }
        self.healing_history = deque(maxlen=1000)
        
    async def diagnose_and_heal(self, service_name: str, health: ServiceHealth) -> bool:
        """Diagnose issues and attempt healing"""
        issues = await self._diagnose_issues(service_name, health)
        
        if not issues:
            return True
            
        logger.info(f"Diagnosing {service_name}: Found {len(issues)} issues")
        
        healed = True
        for issue in issues:
            strategy = self.healing_strategies.get(issue['type'])
            if strategy:
                try:
                    result = await strategy(service_name, issue)
                    self.healing_history.append({
                        "timestamp": datetime.now(),
                        "service": service_name,
                        "issue": issue,
                        "result": result,
                        "success": result.get("success", False)
                    })
                    
                    if not result.get("success", False):
                        healed = False
                        
                except Exception as e:
                    logger.error(f"Healing strategy failed for {service_name}: {e}")
                    healed = False
                    
        return healed
        
    async def _diagnose_issues(self, service_name: str, health: ServiceHealth) -> List[Dict[str, Any]]:
        """Diagnose service issues"""
        issues = []
        
        # Memory issues
        if health.memory_usage > 80:
            issues.append({
                "type": "high_memory",
                "severity": "high" if health.memory_usage > 90 else "medium",
                "value": health.memory_usage
            })
            
        # CPU issues
        if health.cpu_usage > 80:
            issues.append({
                "type": "high_cpu",
                "severity": "high" if health.cpu_usage > 90 else "medium",
                "value": health.cpu_usage
            })
            
        # Responsiveness issues
        if health.status == "unhealthy" and health.response_time > 5:
            issues.append({
                "type": "unresponsive",
                "severity": "high",
                "response_time": health.response_time
            })
            
        # Error rate issues
        if health.error_count > 10:
            issues.append({
                "type": "high_error_rate",
                "severity": "medium",
                "error_count": health.error_count
            })
            
        return issues
        
    async def _heal_high_memory(self, service_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Heal high memory usage"""
        logger.info(f"Healing high memory for {service_name}: {issue['value']}%")
        
        # Try garbage collection first
        if service_name in self.ecosystem.processes:
            process = self.ecosystem.processes[service_name]
            
            # Send signal to trigger GC (if Python process)
            if process.poll() is None:
                os.kill(process.pid, signal.SIGUSR1)
                await asyncio.sleep(5)
                
                # Check if improved
                new_health = await self.ecosystem._check_service_health(service_name)
                if new_health.memory_usage < issue['value'] * 0.8:
                    return {"success": True, "action": "garbage_collection"}
                    
        # If still high, restart service
        await self.ecosystem.restart_service(service_name)
        return {"success": True, "action": "restart"}
        
    async def _heal_high_cpu(self, service_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Heal high CPU usage"""
        logger.info(f"Healing high CPU for {service_name}: {issue['value']}%")
        
        # Check for runaway threads
        if service_name in self.ecosystem.processes:
            process = self.ecosystem.processes[service_name]
            
            try:
                proc = psutil.Process(process.pid)
                threads = proc.num_threads()
                
                if threads > 100:  # Abnormal thread count
                    await self.ecosystem.restart_service(service_name)
                    return {"success": True, "action": "restart_runaway_threads"}
                    
            except psutil.NoSuchProcess:
                pass
                
        # Rate limit the service
        config = self.ecosystem.services.get(service_name)
        if config and "rate_limit" not in config.env:
            config.env["RATE_LIMIT"] = "100"  # Requests per second
            await self.ecosystem.restart_service(service_name)
            return {"success": True, "action": "rate_limit"}
            
        return {"success": False, "action": "none"}
        
    async def _heal_unresponsive(self, service_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Heal unresponsive service"""
        logger.info(f"Healing unresponsive service {service_name}")
        
        # First try a gentle restart
        await self.ecosystem.restart_service(service_name, force=False)
        await asyncio.sleep(10)
        
        # Check if responsive
        health = await self.ecosystem._check_service_health(service_name)
        if health.status == "healthy":
            return {"success": True, "action": "gentle_restart"}
            
        # Force restart
        await self.ecosystem.restart_service(service_name, force=True)
        return {"success": True, "action": "force_restart"}
        
    async def _heal_dependency_failure(self, service_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Heal dependency failures"""
        config = self.ecosystem.services.get(service_name)
        if not config:
            return {"success": False, "action": "service_not_found"}
            
        # Check and start dependencies
        for dep in config.dependencies:
            dep_health = self.ecosystem.service_health.get(dep)
            if not dep_health or dep_health.status != "healthy":
                await self.ecosystem.start_service(dep)
                
        # Wait for dependencies
        await asyncio.sleep(5)
        
        # Restart the service
        await self.ecosystem.restart_service(service_name)
        return {"success": True, "action": "restart_with_dependencies"}
        
    async def _heal_port_conflict(self, service_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Heal port conflicts"""
        config = self.ecosystem.services.get(service_name)
        if not config:
            return {"success": False, "action": "service_not_found"}
            
        # Find alternative port
        original_port = config.port
        new_port = await self.ecosystem._find_available_port(original_port)
        
        if new_port != original_port:
            config.port = new_port
            logger.info(f"Changed {service_name} port from {original_port} to {new_port}")
            
            # Update health check URL if needed
            if config.health_check:
                config.health_check = config.health_check.replace(
                    str(original_port), 
                    str(new_port)
                )
                
            await self.ecosystem.restart_service(service_name)
            return {"success": True, "action": "port_change", "new_port": new_port}
            
        return {"success": False, "action": "no_port_available"}
        
    async def _heal_disk_space(self, service_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Heal disk space issues"""
        # Clean up old logs
        log_dir = LOGS_PATH / service_name
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < time.time() - 86400 * 7:  # 7 days old
                    log_file.unlink()
                    
        # Clean up temp files
        temp_dir = Path("/tmp") / f"mcpvotsagi_{service_name}"
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            
        return {"success": True, "action": "cleanup"}
        
    async def _heal_network_issue(self, service_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Heal network connectivity issues"""
        # Reset network namespace if used
        if platform.system() == "Linux":
            subprocess.run(["ip", "netns", "exec", service_name, "ip", "link", "set", "lo", "up"], 
                         capture_output=True)
                         
        # Restart with increased timeout
        config = self.ecosystem.services.get(service_name)
        if config:
            config.health_check_timeout = config.health_check_timeout * 2
            await self.ecosystem.restart_service(service_name)
            
        return {"success": True, "action": "network_reset"}

class EcosystemManagerV3:
    """Enhanced Ecosystem Manager with F:\ drive storage and advanced features"""
    
    def __init__(self):
        # Paths
        self.workspace = Path("C:/Workspace") if platform.system() == "Windows" else Path("/mnt/c/Workspace")
        self.mcpvotsagi_path = self.workspace / "MCPVotsAGI"
        
        # F:\ Drive paths
        self.data_root = F_DRIVE_ROOT
        self.ecosystem_db = ECOSYSTEM_DATA_PATH / "ecosystem.db"
        self.config_path = ECOSYSTEM_DATA_PATH / "ecosystem_config.yaml"
        
        # Ensure F:\ drive directories exist
        self._ensure_directories()
        
        # Load configuration
        self.config = self._load_configuration()
        
        # Service definitions
        self.services = self._initialize_services()
        
        # Runtime state
        self.service_health: Dict[str, ServiceHealth] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.start_times: Dict[str, datetime] = {}
        self.websocket_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        
        # Components
        self.health_monitor = AdvancedHealthMonitor(METRICS_PATH)
        self.self_healer = SelfHealingEngine(self)
        
        # Thread pool for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Event system
        self.event_handlers = defaultdict(list)
        self.event_queue = asyncio.Queue()
        
        # Running state
        self.is_running = False
        self.monitoring_task = None
        
    def _ensure_directories(self):
        """Ensure all required directories exist on F:\ drive"""
        directories = [
            ECOSYSTEM_DATA_PATH,
            LOGS_PATH,
            METRICS_PATH,
            BACKUPS_PATH,
            LOGS_PATH / "services",
            METRICS_PATH / "reports"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        else:
            # Default configuration
            default_config = {
                "version": "3.0.0",
                "environment": "production",
                "monitoring": {
                    "health_check_interval": 30,
                    "metrics_retention_days": 30,
                    "alert_thresholds": {
                        "cpu": 80,
                        "memory": 85,
                        "disk": 90,
                        "error_rate": 0.05
                    }
                },
                "self_healing": {
                    "enabled": True,
                    "max_restart_attempts": 5,
                    "restart_delay": 10,
                    "predictive_healing": True
                },
                "resource_management": {
                    "cpu_limit": 80,
                    "memory_limit": 85,
                    "auto_scaling": True
                }
            }
            
            # Save default configuration
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
                
            return default_config
            
    def _initialize_services(self) -> Dict[str, ServiceConfig]:
        """Initialize service configurations"""
        services = {}
        
        # Core Infrastructure
        services["ollama"] = ServiceConfig(
            name="Ollama Service",
            port=11434,
            command=["ollama", "serve"],
            priority=1,
            dependencies=[],
            health_check="http://localhost:11434/api/tags",
            critical=True,
            resource_limits={"memory_mb": 8192, "cpu_percent": 50}
        )
        
        # DeepSeek Integration
        services["deepseek_mcp"] = ServiceConfig(
            name="DeepSeek MCP Server",
            port=3008,
            command=["python", str(self.mcpvotsagi_path / "servers" / "deepseek_ollama_mcp_server.py")],
            priority=2,
            dependencies=["ollama"],
            health_check="ws://localhost:3008",
            critical=True,
            env={
                "OLLAMA_HOST": "http://localhost:11434",
                "DEEPSEEK_MODEL": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
                "F_DRIVE_ROOT": str(F_DRIVE_ROOT)
            }
        )
        
        services["deepseek_trading"] = ServiceConfig(
            name="DeepSeek Trading Agent",
            port=3009,
            command=["python", str(self.mcpvotsagi_path / "deepseek_trading_agent_enhanced.py")],
            priority=3,
            dependencies=["deepseek_mcp", "solana_mcp"],
            health_check=None,  # Background service
            env={
                "TRADING_MODE": "LIVE",
                "F_DRIVE_ROOT": str(F_DRIVE_ROOT)
            },
            resource_limits={"memory_mb": 4096}
        )
        
        # MCP Servers
        services["memory_mcp"] = ServiceConfig(
            name="Memory MCP Server",
            port=3002,
            command=["python", str(self.mcpvotsagi_path / "servers" / "enhanced_memory_mcp_server.py")],
            priority=2,
            dependencies=[],
            health_check="ws://localhost:3002",
            critical=True,
            env={"MEMORY_DB": str(F_DRIVE_ROOT / "memory" / "knowledge_graph.db")}
        )
        
        services["github_mcp"] = ServiceConfig(
            name="GitHub MCP Server",
            port=3001,
            command=["python", str(self.mcpvotsagi_path / "servers" / "mcp_github_server.py")],
            priority=2,
            dependencies=[],
            health_check="ws://localhost:3001",
            env={"GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "")}
        )
        
        services["solana_mcp"] = ServiceConfig(
            name="Solana MCP Server",
            port=3005,
            command=["python", str(self.mcpvotsagi_path / "solana_mcp_deepseek_integration.py")],
            priority=2,
            dependencies=["deepseek_mcp"],
            health_check="ws://localhost:3005",
            env={
                "SOLANA_RPC": os.environ.get("SOLANA_RPC", "https://api.mainnet-beta.solana.com"),
                "MARKET_DATA_PATH": str(F_DRIVE_ROOT / "market_data")
            }
        )
        
        services["opencti_mcp"] = ServiceConfig(
            name="OpenCTI MCP Server",
            port=3007,
            command=["python", str(self.mcpvotsagi_path / "servers" / "opencti_mcp_server.py")],
            priority=2,
            dependencies=[],
            health_check="ws://localhost:3007",
            env={
                "OPENCTI_URL": os.environ.get("OPENCTI_URL", "http://localhost:8080"),
                "OPENCTI_TOKEN": os.environ.get("OPENCTI_TOKEN", "")
            }
        )
        
        # Oracle AGI Dashboard
        services["oracle_dashboard"] = ServiceConfig(
            name="Oracle AGI Dashboard",
            port=3011,
            command=["python", str(self.mcpvotsagi_path / "oracle_agi_unified_final.py")],
            priority=4,
            dependencies=["memory_mcp", "deepseek_mcp"],
            health_check="http://localhost:3011/api/health",
            critical=True,
            env={
                "DASHBOARD_PORT": "3011",
                "F_DRIVE_ROOT": str(F_DRIVE_ROOT)
            }
        )
        
        return services
        
    async def start(self):
        """Start the ecosystem manager"""
        self.is_running = True
        logger.info("Starting MCPVotsAGI Ecosystem Manager V3")
        logger.info(f"Using F:\\ drive storage at: {self.data_root}")
        
        # Initialize database
        await self._init_database()
        
        # Start event processor
        asyncio.create_task(self._process_events())
        
        # Start services by priority
        await self._start_services_by_priority()
        
        # Start monitoring
        self.monitoring_task = asyncio.create_task(self._monitor_services())
        
        # Start self-healing
        asyncio.create_task(self._self_healing_loop())
        
        # Start metrics collection
        asyncio.create_task(self._collect_system_metrics())
        
        logger.info("Ecosystem Manager started successfully")
        
    async def _init_database(self):
        """Initialize ecosystem database"""
        conn = sqlite3.connect(self.ecosystem_db)
        cursor = conn.cursor()
        
        # Service events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                service_name TEXT,
                event_type TEXT,
                details TEXT,
                severity TEXT
            )
        """)
        
        # Service states table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_states (
                service_name TEXT PRIMARY KEY,
                status TEXT,
                last_start REAL,
                total_restarts INTEGER,
                total_uptime REAL,
                last_error TEXT,
                configuration TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
    async def _start_services_by_priority(self):
        """Start services in priority order"""
        # Group services by priority
        priority_groups = defaultdict(list)
        for name, config in self.services.items():
            priority_groups[config.priority].append(name)
            
        # Start each priority group
        for priority in sorted(priority_groups.keys()):
            services = priority_groups[priority]
            logger.info(f"Starting priority {priority} services: {services}")
            
            # Start services in parallel within same priority
            tasks = [self.start_service(name) for name in services]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Wait a bit between priority groups
            await asyncio.sleep(2)
            
    async def start_service(self, service_name: str) -> bool:
        """Start a single service with enhanced error handling"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        config = self.services[service_name]
        
        # Check if already running
        if service_name in self.processes:
            process = self.processes[service_name]
            if process.poll() is None:
                logger.info(f"{service_name} is already running")
                return True
                
        # Check dependencies
        for dep in config.dependencies:
            dep_health = self.service_health.get(dep)
            if not dep_health or dep_health.status != "healthy":
                logger.warning(f"Dependency {dep} not healthy for {service_name}")
                # Try to start dependency
                await self.start_service(dep)
                await asyncio.sleep(5)
                
        # Check port availability
        if config.port and not await self._check_port_available(config.port):
            logger.error(f"Port {config.port} not available for {service_name}")
            # Try to find alternative port
            new_port = await self._find_available_port(config.port)
            if new_port != config.port:
                logger.info(f"Using alternative port {new_port} for {service_name}")
                config.port = new_port
                # Update health check URL
                if config.health_check:
                    config.health_check = config.health_check.replace(
                        str(config.port), 
                        str(new_port)
                    )
                    
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(config.env)
            
            # Create log file
            log_file = LOGS_PATH / "services" / f"{service_name}.log"
            log_file.parent.mkdir(exist_ok=True)
            
            # Start process
            with open(log_file, 'a') as log:
                process = subprocess.Popen(
                    config.command,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=self.mcpvotsagi_path
                )
                
            self.processes[service_name] = process
            self.start_times[service_name] = datetime.now()
            
            # Update service health to starting
            self.service_health[service_name] = ServiceHealth(
                name=config.name,
                port=config.port,
                status="starting",
                last_check=datetime.now(),
                response_time=0,
                error_count=0,
                restart_count=0,
                memory_usage=0,
                cpu_usage=0,
                disk_io={},
                network_io={},
                uptime=0,
                health_score=0
            )
            
            # Wait for service to be healthy
            healthy = await self._wait_for_healthy(service_name, config.startup_timeout)
            
            if healthy:
                logger.info(f"✓ {service_name} started successfully")
                await self._emit_event("service_started", {
                    "service": service_name,
                    "port": config.port
                })
                return True
            else:
                logger.error(f"✗ {service_name} failed to become healthy")
                await self.stop_service(service_name)
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            await self._emit_event("service_start_failed", {
                "service": service_name,
                "error": str(e)
            })
            return False
            
    async def stop_service(self, service_name: str):
        """Stop a service gracefully"""
        if service_name not in self.processes:
            return
            
        process = self.processes[service_name]
        if process.poll() is not None:
            return
            
        logger.info(f"Stopping {service_name}")
        
        # Try graceful shutdown first
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Force kill if needed
            process.kill()
            process.wait()
            
        del self.processes[service_name]
        
        # Update health status
        if service_name in self.service_health:
            self.service_health[service_name].status = "stopped"
            
        await self._emit_event("service_stopped", {"service": service_name})
        
    async def restart_service(self, service_name: str, force: bool = False):
        """Restart a service"""
        logger.info(f"Restarting {service_name} (force={force})")
        
        # Update restart count
        if service_name in self.service_health:
            self.service_health[service_name].restart_count += 1
            
        await self.stop_service(service_name)
        await asyncio.sleep(2)
        return await self.start_service(service_name)
        
    async def _check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
            return True
        except OSError:
            return False
            
    async def _find_available_port(self, start_port: int, max_attempts: int = 100) -> int:
        """Find an available port starting from start_port"""
        for offset in range(max_attempts):
            port = start_port + offset
            if await self._check_port_available(port):
                return port
        return start_port
        
    async def _wait_for_healthy(self, service_name: str, timeout: int) -> bool:
        """Wait for a service to become healthy"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            health = await self._check_service_health(service_name)
            
            if health.status == "healthy":
                return True
                
            await asyncio.sleep(2)
            
        return False
        
    async def _check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a single service"""
        config = self.services.get(service_name)
        if not config:
            return None
            
        # Get process info
        process = self.processes.get(service_name)
        if not process or process.poll() is not None:
            return ServiceHealth(
                name=config.name,
                port=config.port,
                status="stopped",
                last_check=datetime.now(),
                response_time=0,
                error_count=0,
                restart_count=self.service_health.get(service_name, {}).restart_count or 0,
                memory_usage=0,
                cpu_usage=0,
                disk_io={},
                network_io={},
                uptime=0,
                health_score=0
            )
            
        # Get process metrics
        try:
            proc = psutil.Process(process.pid)
            memory_info = proc.memory_info()
            cpu_percent = proc.cpu_percent(interval=0.1)
            io_counters = proc.io_counters() if hasattr(proc, 'io_counters') else None
            
            memory_usage = (memory_info.rss / psutil.virtual_memory().total) * 100
            
            # Calculate uptime
            if service_name in self.start_times:
                uptime = (datetime.now() - self.start_times[service_name]).total_seconds()
            else:
                uptime = 0
                
        except psutil.NoSuchProcess:
            memory_usage = 0
            cpu_percent = 0
            uptime = 0
            io_counters = None
            
        # Check health endpoint
        health_status = "unknown"
        response_time = 0
        
        if config.health_check:
            start = time.time()
            
            try:
                if config.health_check.startswith("http"):
                    # HTTP health check
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            config.health_check,
                            timeout=aiohttp.ClientTimeout(total=config.health_check_timeout)
                        ) as response:
                            if response.status == 200:
                                health_status = "healthy"
                            else:
                                health_status = "unhealthy"
                                
                elif config.health_check.startswith("ws"):
                    # WebSocket health check
                    try:
                        async with websockets.connect(
                            config.health_check,
                            timeout=config.health_check_timeout
                        ) as ws:
                            await ws.send(json.dumps({
                                "jsonrpc": "2.0",
                                "method": "ping",
                                "id": 1
                            }))
                            await asyncio.wait_for(ws.recv(), timeout=5)
                            health_status = "healthy"
                    except:
                        health_status = "unhealthy"
                        
            except Exception as e:
                health_status = "unhealthy"
                logger.debug(f"Health check failed for {service_name}: {e}")
                
            response_time = time.time() - start
        else:
            # No health check defined, assume healthy if process is running
            health_status = "healthy" if process.poll() is None else "stopped"
            
        # Calculate health score (0-100)
        health_score = 100
        if health_status != "healthy":
            health_score -= 50
        if cpu_percent > 80:
            health_score -= 20
        if memory_usage > 80:
            health_score -= 20
        if response_time > 2:
            health_score -= 10
            
        health_score = max(0, health_score)
        
        # Get previous health for error tracking
        prev_health = self.service_health.get(service_name)
        error_count = prev_health.error_count if prev_health else 0
        if health_status == "unhealthy":
            error_count += 1
            
        return ServiceHealth(
            name=config.name,
            port=config.port,
            status=health_status,
            last_check=datetime.now(),
            response_time=response_time,
            error_count=error_count,
            restart_count=prev_health.restart_count if prev_health else 0,
            memory_usage=memory_usage,
            cpu_usage=cpu_percent,
            disk_io={"read": io_counters.read_bytes, "write": io_counters.write_bytes} if io_counters else {},
            network_io={},
            uptime=uptime,
            health_score=health_score
        )
        
    async def _monitor_services(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Check health of all services
                for service_name in self.services:
                    health = await self._check_service_health(service_name)
                    
                    if health:
                        self.service_health[service_name] = health
                        
                        # Record metrics
                        await self.health_monitor.record_service_metrics(service_name, health)
                        
                        # Check for anomalies
                        anomalies = await self.health_monitor.detect_anomalies(
                            service_name,
                            {
                                "cpu_usage": health.cpu_usage,
                                "memory_usage": health.memory_usage,
                                "response_time": health.response_time,
                                "error_rate": health.error_count / max(health.uptime, 1)
                            }
                        )
                        
                        if anomalies:
                            logger.warning(f"Anomalies detected in {service_name}: {anomalies}")
                            await self._emit_event("anomalies_detected", {
                                "service": service_name,
                                "anomalies": anomalies
                            })
                            
                        # Predict failures
                        if self.config["self_healing"]["predictive_healing"]:
                            prediction = await self.health_monitor.predict_failure(service_name)
                            if prediction["prediction"] == "failure_likely":
                                logger.warning(
                                    f"Potential failure predicted for {service_name}: "
                                    f"{prediction['confidence']:.0%} confidence"
                                )
                                await self._emit_event("failure_predicted", {
                                    "service": service_name,
                                    "prediction": prediction
                                })
                                
                await asyncio.sleep(self.config["monitoring"]["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)
                
    async def _self_healing_loop(self):
        """Self-healing loop"""
        if not self.config["self_healing"]["enabled"]:
            return
            
        while self.is_running:
            try:
                for service_name, health in self.service_health.items():
                    if health.status != "healthy" or health.health_score < 70:
                        # Attempt healing
                        healed = await self.self_healer.diagnose_and_heal(service_name, health)
                        
                        if healed:
                            logger.info(f"Successfully healed {service_name}")
                        else:
                            logger.warning(f"Failed to heal {service_name}")
                            
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Self-healing error: {e}")
                await asyncio.sleep(5)
                
    async def _collect_system_metrics(self):
        """Collect system-wide metrics"""
        while self.is_running:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                load_average = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                
                # Memory metrics
                memory = psutil.virtual_memory()
                
                # Disk metrics
                disk_usage = {}
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_usage[partition.mountpoint] = usage.percent
                    except:
                        pass
                        
                # Network metrics
                net_io = psutil.net_io_counters()
                network_usage = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
                
                # GPU metrics (if available)
                gpu_usage = None
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    gpu_usage = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                except:
                    pass
                    
                # Temperature (if available)
                temperature = None
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                if entry.label == 'Package id 0':
                                    temperature = entry.current
                                    break
                except:
                    pass
                    
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_usage=disk_usage,
                    network_usage=network_usage,
                    gpu_usage=gpu_usage,
                    temperature=temperature,
                    load_average=list(load_average),
                    process_count=len(psutil.pids()),
                    thread_count=sum(p.num_threads() for p in psutil.process_iter(['num_threads'])),
                    open_files=len(psutil.Process().open_files())
                )
                
                # Store metrics
                await self._store_system_metrics(metrics)
                
                # Check thresholds
                await self._check_system_thresholds(metrics)
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
                
    async def _store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics to database"""
        conn = sqlite3.connect(self.health_monitor.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO system_metrics 
            (timestamp, cpu_percent, memory_percent, disk_usage, network_in, network_out, temperature)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            time.time(),
            metrics.cpu_percent,
            metrics.memory_percent,
            max(metrics.disk_usage.values()) if metrics.disk_usage else 0,
            metrics.network_usage.get("bytes_recv", 0),
            metrics.network_usage.get("bytes_sent", 0),
            metrics.temperature
        ))
        
        conn.commit()
        conn.close()
        
    async def _check_system_thresholds(self, metrics: SystemMetrics):
        """Check if system metrics exceed thresholds"""
        thresholds = self.config["monitoring"]["alert_thresholds"]
        
        alerts = []
        
        if metrics.cpu_percent > thresholds["cpu"]:
            alerts.append({
                "type": "high_cpu",
                "value": metrics.cpu_percent,
                "threshold": thresholds["cpu"]
            })
            
        if metrics.memory_percent > thresholds["memory"]:
            alerts.append({
                "type": "high_memory",
                "value": metrics.memory_percent,
                "threshold": thresholds["memory"]
            })
            
        if metrics.disk_usage:
            max_disk = max(metrics.disk_usage.values())
            if max_disk > thresholds["disk"]:
                alerts.append({
                    "type": "high_disk",
                    "value": max_disk,
                    "threshold": thresholds["disk"]
                })
                
        if alerts:
            await self._emit_event("system_alerts", {"alerts": alerts})
            
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event"""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        await self.event_queue.put(event)
        
        # Store in database
        conn = sqlite3.connect(self.ecosystem_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO service_events 
            (timestamp, service_name, event_type, details, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            time.time(),
            data.get("service", "system"),
            event_type,
            json.dumps(data),
            "info"
        ))
        
        conn.commit()
        conn.close()
        
    async def _process_events(self):
        """Process events from the queue"""
        while self.is_running:
            try:
                event = await self.event_queue.get()
                
                # Call registered handlers
                handlers = self.event_handlers.get(event["type"], [])
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler error: {e}")
                        
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                
    def register_event_handler(self, event_type: str, handler):
        """Register an event handler"""
        self.event_handlers[event_type].append(handler)
        
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem status"""
        # Calculate overall health
        total_services = len(self.services)
        healthy_services = sum(1 for h in self.service_health.values() if h.status == "healthy")
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Get F:\ drive usage
        f_drive_usage = psutil.disk_usage(str(F_DRIVE_ROOT)) if F_DRIVE_ROOT.exists() else None
        
        return {
            "timestamp": datetime.now().isoformat(),
            "ecosystem_health": (healthy_services / total_services) * 100 if total_services > 0 else 0,
            "services": {
                "total": total_services,
                "healthy": healthy_services,
                "unhealthy": total_services - healthy_services
            },
            "service_details": {
                name: {
                    "status": health.status,
                    "health_score": health.health_score,
                    "uptime": health.uptime,
                    "cpu": health.cpu_usage,
                    "memory": health.memory_usage,
                    "errors": health.error_count,
                    "restarts": health.restart_count
                }
                for name, health in self.service_health.items()
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "f_drive": {
                    "total_gb": f_drive_usage.total / (1024**3) if f_drive_usage else 0,
                    "used_gb": f_drive_usage.used / (1024**3) if f_drive_usage else 0,
                    "free_gb": f_drive_usage.free / (1024**3) if f_drive_usage else 0,
                    "percent": f_drive_usage.percent if f_drive_usage else 0
                } if f_drive_usage else None
            },
            "configuration": {
                "version": self.config["version"],
                "environment": self.config["environment"],
                "self_healing": self.config["self_healing"]["enabled"],
                "predictive_healing": self.config["self_healing"]["predictive_healing"]
            }
        }
        
    async def backup_state(self):
        """Backup current ecosystem state"""
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                name: asdict(config)
                for name, config in self.services.items()
            },
            "health": {
                name: asdict(health)
                for name, health in self.service_health.items()
            },
            "configuration": self.config
        }
        
        backup_file = BACKUPS_PATH / f"ecosystem_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
            
        logger.info(f"Ecosystem state backed up to {backup_file}")
        
        # Clean old backups (keep last 30)
        backups = sorted(BACKUPS_PATH.glob("ecosystem_backup_*.json"))
        if len(backups) > 30:
            for old_backup in backups[:-30]:
                old_backup.unlink()
                
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Ecosystem Manager")
        self.is_running = False
        
        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            
        # Stop all services
        for service_name in list(self.processes.keys()):
            await self.stop_service(service_name)
            
        # Final backup
        await self.backup_state()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Ecosystem Manager shutdown complete")

# Import pandas if available (for predictive features)
try:
    import pandas as pd
except ImportError:
    logger.warning("pandas not available - predictive features disabled")
    pd = None

async def main():
    """Main entry point"""
    manager = EcosystemManagerV3()
    
    try:
        await manager.start()
        
        # Keep running
        while True:
            await asyncio.sleep(60)
            
            # Periodic backup
            await manager.backup_state()
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    asyncio.run(main())