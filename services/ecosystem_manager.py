#!/usr/bin/env python3
"""
MCPVotsAGI Ecosystem Manager
===========================
Comprehensive ecosystem management with auto-start, self-healing, and hardware optimization
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
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
import threading
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EcosystemManager")

@dataclass
class ServiceHealth:
    """Service health status"""
    name: str
    port: int
    status: str  # 'healthy', 'unhealthy', 'recovering', 'stopped'
    last_check: datetime
    response_time: float
    error_count: int
    restart_count: int
    memory_usage: float
    cpu_usage: float

@dataclass
class HardwareStatus:
    """Hardware resource status"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    gpu_available: bool
    gpu_memory: Optional[float]
    temperature: Optional[float]
    optimal_threads: int
    available_ram_gb: float

class EcosystemManager:
    """Comprehensive ecosystem management system"""
    
    def __init__(self):
        self.workspace = Path("C:/Workspace") if platform.system() == "Windows" else Path("/mnt/c/Workspace")
        self.mcpvots_path = self.workspace / "MCPVots"
        self.mcpvotsagi_path = self.workspace / "MCPVotsAGI"
        
        # Service definitions with priority and dependencies
        self.services = {
            # Core Infrastructure
            "ipfs_daemon": {
                "name": "IPFS Daemon",
                "port": 5001,
                "command": ["ipfs", "daemon"],
                "priority": 1,
                "dependencies": [],
                "health_check": "http://localhost:5001/api/v0/id",
                "critical": True
            },
            
            # MCP Servers (Priority 2)
            "github_mcp": {
                "name": "GitHub MCP",
                "port": 3001,
                "command": ["python", str(self.mcpvots_path / "servers" / "mcp_github_server.py")],
                "priority": 2,
                "dependencies": [],
                "health_check": "ws://localhost:3001",
                "env": {"GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "")}
            },
            "memory_mcp": {
                "name": "Memory MCP",
                "port": 3002,
                "command": ["python", str(self.mcpvots_path / "servers" / "enhanced_memory_mcp_server.py")],
                "priority": 2,
                "dependencies": [],
                "health_check": "ws://localhost:3002",
                "critical": True
            },
            "solana_mcp": {
                "name": "Solana MCP",
                "port": 3005,
                "command": ["python", str(self.mcpvotsagi_path / "solana_mcp_deepseek_integration.py")],
                "priority": 2,
                "dependencies": [],
                "health_check": "ws://localhost:3005"
            },
            
            # AGI Core Services (Priority 3)
            "trilogy_agi": {
                "name": "Trilogy AGI Gateway",
                "port": 8000,
                "command": ["python", str(self.mcpvots_path / "servers" / "trilogy_agi_gateway.py")],
                "priority": 3,
                "dependencies": ["memory_mcp"],
                "health_check": "ws://localhost:8000",
                "critical": True
            },
            "dgm_evolution": {
                "name": "DGM Evolution Engine",
                "port": 8013,
                "command": ["python", str(self.mcpvots_path / "servers" / "dgm_evolution_server.py")],
                "priority": 3,
                "dependencies": ["memory_mcp"],
                "health_check": "ws://localhost:8013"
            },
            "deerflow": {
                "name": "DeerFlow Orchestrator",
                "port": 8014,
                "command": ["python", str(self.mcpvots_path / "servers" / "deerflow_server.py")],
                "priority": 3,
                "dependencies": [],
                "health_check": "ws://localhost:8014"
            },
            "gemini_cli": {
                "name": "Gemini CLI Service",
                "port": 8015,
                "command": ["python", str(self.mcpvots_path / "gemini_cli_http_server.py")],
                "priority": 3,
                "dependencies": [],
                "health_check": "ws://localhost:8015",
                "env": {"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")}
            },
            
            # Ollama Service
            "ollama": {
                "name": "Ollama Service",
                "port": 11434,
                "command": ["ollama", "serve"],
                "priority": 2,
                "dependencies": [],
                "health_check": "http://localhost:11434/api/tags",
                "critical": True
            },
            
            # Oracle AGI Services (Priority 4)
            "oracle_agi": {
                "name": "Oracle AGI Core",
                "port": 8888,
                "command": ["python", str(self.mcpvotsagi_path / "oracle_agi_ultimate_unified.py")],
                "priority": 4,
                "dependencies": ["memory_mcp", "trilogy_agi"],
                "health_check": "http://localhost:3010/api/status",
                "critical": True
            },
            
            # n8n Workflow Engine
            "n8n": {
                "name": "n8n Workflow Engine",
                "port": 5678,
                "command": ["n8n", "start"],
                "priority": 3,
                "dependencies": [],
                "health_check": "http://localhost:5678",
                "env": {"N8N_PORT": "5678"}
            },
            
            # DeepSeek Reasoning Engine
            "deepseek_mcp": {
                "name": "DeepSeek Ollama MCP",
                "port": 3008,
                "command": ["python", str(self.mcpvotsagi_path / "servers" / "deepseek_ollama_mcp_server.py")],
                "priority": 2,
                "dependencies": ["ollama"],
                "health_check": "ws://localhost:3008",
                "critical": True,
                "env": {
                    "OLLAMA_HOST": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
                    "DEEPSEEK_MODEL": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
                }
            },
            
            # OpenCTI Security
            "opencti_mcp": {
                "name": "OpenCTI MCP",
                "port": 3007,
                "command": ["python", str(self.mcpvotsagi_path / "servers" / "opencti_mcp_server.py")],
                "priority": 2,
                "dependencies": [],
                "health_check": "ws://localhost:3007",
                "env": {
                    "OPENCTI_URL": os.environ.get("OPENCTI_URL", "http://localhost:8080"),
                    "OPENCTI_TOKEN": os.environ.get("OPENCTI_TOKEN", "")
                }
            },
            
            # DeepSeek Trading Agent
            "deepseek_trading": {
                "name": "DeepSeek Trading Agent",
                "port": 3009,
                "command": ["python", str(self.mcpvotsagi_path / "deepseek_trading_agent.py")],
                "priority": 3,
                "dependencies": ["deepseek_mcp", "solana_mcp"],
                "health_check": None,  # Runs as background service
                "env": {
                    "TRADING_MODE": "LIVE",
                    "MAX_POSITION_SIZE": "0.1",
                    "RISK_LEVEL": "MODERATE"
                }
            }
        }
        
        # Service health tracking
        self.service_health: Dict[str, ServiceHealth] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.hardware_status: Optional[HardwareStatus] = None
        
        # Self-healing configuration
        self.healing_config = {
            "max_restart_attempts": 3,
            "restart_delay": 5,  # seconds
            "health_check_interval": 30,  # seconds
            "memory_threshold": 85,  # percent
            "cpu_threshold": 90,  # percent
            "recovery_timeout": 300  # seconds
        }
        
        # Knowledge index database
        self.knowledge_db = self.mcpvotsagi_path / "ecosystem_knowledge.db"
        self.init_knowledge_db()
        
        # LLM configurations for specific tasks
        self.llm_configs = {
            "code_analysis": {
                "model": "deepseek-coder:latest",
                "endpoint": "http://localhost:11434/api/generate",
                "purpose": "Code analysis and optimization"
            },
            "reasoning": {
                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
                "endpoint": "ws://localhost:3008",
                "purpose": "Advanced reasoning and trading decisions"
            },
            "reasoning_fallback": {
                "model": "gemini-2.5-pro",
                "endpoint": "http://localhost:8015/api/chat",
                "purpose": "Complex reasoning and planning"
            },
            "memory": {
                "model": "llama2:7b",
                "endpoint": "http://localhost:11434/api/generate",
                "purpose": "Memory consolidation and retrieval"
            },
            "security": {
                "model": "codellama:7b",
                "endpoint": "http://localhost:11434/api/generate",
                "purpose": "Security analysis and vulnerability detection"
            }
        }
        
    def init_knowledge_db(self):
        """Initialize knowledge database for ecosystem understanding"""
        conn = sqlite3.connect(self.knowledge_db)
        cursor = conn.cursor()
        
        # Create tables for ecosystem knowledge
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_knowledge (
                service_id TEXT PRIMARY KEY,
                service_name TEXT,
                description TEXT,
                capabilities TEXT,
                dependencies TEXT,
                performance_profile TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                service_id TEXT,
                optimization_type TEXT,
                before_metrics TEXT,
                after_metrics TEXT,
                llm_used TEXT,
                success BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                service_id TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                response_time REAL,
                error_count INTEGER,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def check_hardware_status(self) -> HardwareStatus:
        """Check current hardware status and capabilities"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check GPU availability
        gpu_available = False
        gpu_memory = None
        try:
            import torch
            if torch.cuda.is_available():
                gpu_available = True
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        except:
            pass
        
        # Get CPU temperature if available
        temperature = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.label == 'Package id 0' or 'cpu' in entry.label.lower():
                            temperature = entry.current
                            break
        except:
            pass
        
        # Calculate optimal thread count based on CPU
        cpu_count = psutil.cpu_count()
        optimal_threads = max(1, cpu_count - 2)  # Leave 2 cores for system
        
        self.hardware_status = HardwareStatus(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            gpu_available=gpu_available,
            gpu_memory=gpu_memory,
            temperature=temperature,
            optimal_threads=optimal_threads,
            available_ram_gb=memory.available / 1024**3
        )
        
        return self.hardware_status
    
    def is_port_open(self, port: int) -> bool:
        """Check if a port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    async def health_check_service(self, service_id: str, service_config: Dict[str, Any]) -> ServiceHealth:
        """Perform health check on a service"""
        start_time = time.time()
        port = service_config["port"]
        
        # Get current health or create new
        current_health = self.service_health.get(service_id, ServiceHealth(
            name=service_config["name"],
            port=port,
            status="stopped",
            last_check=datetime.now(),
            response_time=0,
            error_count=0,
            restart_count=0,
            memory_usage=0,
            cpu_usage=0
        ))
        
        try:
            # Check if port is open
            if not self.is_port_open(port):
                current_health.status = "stopped"
                current_health.error_count += 1
            else:
                # Perform specific health check
                health_url = service_config.get("health_check")
                if health_url:
                    if health_url.startswith("http"):
                        async with aiohttp.ClientSession() as session:
                            async with session.get(health_url, timeout=5) as response:
                                if response.status == 200:
                                    current_health.status = "healthy"
                                    current_health.error_count = 0
                                else:
                                    current_health.status = "unhealthy"
                                    current_health.error_count += 1
                    elif health_url.startswith("ws"):
                        # WebSocket health check
                        import websockets
                        try:
                            async with websockets.connect(health_url, timeout=5) as ws:
                                await ws.ping()
                                current_health.status = "healthy"
                                current_health.error_count = 0
                        except:
                            current_health.status = "unhealthy"
                            current_health.error_count += 1
                else:
                    # Port is open, assume healthy
                    current_health.status = "healthy"
                    
                # Get process metrics if running
                if service_id in self.processes:
                    process = self.processes[service_id]
                    if process.poll() is None:
                        try:
                            p = psutil.Process(process.pid)
                            current_health.cpu_usage = p.cpu_percent()
                            current_health.memory_usage = p.memory_info().rss / 1024**2  # MB
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"Health check failed for {service_config['name']}: {e}")
            current_health.status = "unhealthy"
            current_health.error_count += 1
        
        current_health.response_time = time.time() - start_time
        current_health.last_check = datetime.now()
        
        # Store in database
        self.store_health_metrics(service_id, current_health)
        
        return current_health
    
    def store_health_metrics(self, service_id: str, health: ServiceHealth):
        """Store health metrics in database"""
        conn = sqlite3.connect(self.knowledge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO health_metrics 
            (timestamp, service_id, cpu_usage, memory_usage, response_time, error_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            service_id,
            health.cpu_usage,
            health.memory_usage,
            health.response_time,
            health.error_count,
            health.status
        ))
        
        conn.commit()
        conn.close()
    
    async def start_service(self, service_id: str, service_config: Dict[str, Any]) -> bool:
        """Start a single service"""
        try:
            # Check dependencies first
            for dep in service_config.get("dependencies", []):
                if dep not in self.service_health or self.service_health[dep].status != "healthy":
                    logger.warning(f"Cannot start {service_config['name']}: dependency {dep} not healthy")
                    return False
            
            # Check if already running
            if self.is_port_open(service_config["port"]):
                logger.info(f"{service_config['name']} already running on port {service_config['port']}")
                return True
            
            # Prepare environment
            env = os.environ.copy()
            if "env" in service_config:
                env.update(service_config["env"])
            
            # Start process
            logger.info(f"Starting {service_config['name']}...")
            
            process = subprocess.Popen(
                service_config["command"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
            )
            
            self.processes[service_id] = process
            
            # Wait for startup
            await asyncio.sleep(3)
            
            # Verify started
            health = await self.health_check_service(service_id, service_config)
            if health.status == "healthy":
                logger.info(f"✓ {service_config['name']} started successfully")
                return True
            else:
                logger.error(f"✗ {service_config['name']} failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {service_config['name']}: {e}")
            return False
    
    async def stop_service(self, service_id: str):
        """Stop a service gracefully"""
        if service_id in self.processes:
            process = self.processes[service_id]
            if process.poll() is None:
                logger.info(f"Stopping {self.services[service_id]['name']}...")
                
                if platform.system() == "Windows":
                    process.terminate()
                else:
                    process.terminate()
                    
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
                del self.processes[service_id]
    
    async def restart_service(self, service_id: str) -> bool:
        """Restart a service"""
        service_config = self.services[service_id]
        health = self.service_health.get(service_id)
        
        if health and health.restart_count >= self.healing_config["max_restart_attempts"]:
            logger.error(f"{service_config['name']} exceeded max restart attempts")
            return False
        
        logger.info(f"Restarting {service_config['name']}...")
        
        # Stop the service
        await self.stop_service(service_id)
        await asyncio.sleep(self.healing_config["restart_delay"])
        
        # Start the service
        success = await self.start_service(service_id, service_config)
        
        if success and service_id in self.service_health:
            self.service_health[service_id].restart_count += 1
            
        return success
    
    async def self_heal_service(self, service_id: str):
        """Attempt to heal an unhealthy service"""
        service_config = self.services[service_id]
        health = self.service_health[service_id]
        
        logger.info(f"Attempting to heal {service_config['name']}...")
        
        # Different healing strategies based on issue
        if health.status == "stopped":
            # Service is not running, start it
            await self.start_service(service_id, service_config)
            
        elif health.status == "unhealthy":
            # Service is running but unhealthy
            if health.memory_usage > self.healing_config["memory_threshold"]:
                # High memory usage, restart
                logger.warning(f"{service_config['name']} using too much memory ({health.memory_usage}MB)")
                await self.restart_service(service_id)
                
            elif health.cpu_usage > self.healing_config["cpu_threshold"]:
                # High CPU usage, might need optimization
                logger.warning(f"{service_config['name']} using too much CPU ({health.cpu_usage}%)")
                await self.optimize_service(service_id)
                
            elif health.error_count > 5:
                # Too many errors, restart
                logger.warning(f"{service_config['name']} has too many errors ({health.error_count})")
                await self.restart_service(service_id)
                
        elif health.status == "recovering":
            # Wait for recovery timeout
            recovery_time = (datetime.now() - health.last_check).total_seconds()
            if recovery_time > self.healing_config["recovery_timeout"]:
                # Recovery taking too long, force restart
                await self.restart_service(service_id)
    
    async def optimize_service(self, service_id: str):
        """Optimize a service using LLM analysis"""
        service_config = self.services[service_id]
        health = self.service_health[service_id]
        
        logger.info(f"Optimizing {service_config['name']} with AI analysis...")
        
        # Get service metrics history
        conn = sqlite3.connect(self.knowledge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM health_metrics 
            WHERE service_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''', (service_id,))
        
        metrics_history = cursor.fetchall()
        conn.close()
        
        # Prepare optimization prompt
        optimization_prompt = f"""
        Analyze the performance metrics for {service_config['name']} and suggest optimizations:
        
        Current Status:
        - CPU Usage: {health.cpu_usage}%
        - Memory Usage: {health.memory_usage}MB
        - Response Time: {health.response_time}s
        - Error Count: {health.error_count}
        
        Recent metrics history shows patterns of high resource usage.
        
        Suggest specific optimizations for this service.
        """
        
        # Use appropriate LLM for optimization
        llm_config = self.llm_configs["code_analysis"]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    llm_config["endpoint"],
                    json={
                        "model": llm_config["model"],
                        "prompt": optimization_prompt,
                        "temperature": 0.7
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        optimization_suggestion = result.get("response", "")
                        
                        # Store optimization in database
                        conn = sqlite3.connect(self.knowledge_db)
                        cursor = conn.cursor()
                        
                        cursor.execute('''
                            INSERT INTO optimization_history
                            (timestamp, service_id, optimization_type, before_metrics, after_metrics, llm_used, success)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            datetime.now(),
                            service_id,
                            "performance",
                            json.dumps(asdict(health)),
                            "",  # Will be updated after optimization
                            llm_config["model"],
                            False  # Will be updated if successful
                        ))
                        
                        conn.commit()
                        conn.close()
                        
                        logger.info(f"Optimization suggestion for {service_config['name']}: {optimization_suggestion[:200]}...")
                        
        except Exception as e:
            logger.error(f"Failed to optimize {service_config['name']}: {e}")
    
    async def continuous_health_monitor(self):
        """Continuously monitor service health"""
        while True:
            try:
                # Check hardware status
                hardware = await self.check_hardware_status()
                
                # Check each service
                for service_id, service_config in self.services.items():
                    health = await self.health_check_service(service_id, service_config)
                    self.service_health[service_id] = health
                    
                    # Apply self-healing if needed
                    if health.status != "healthy":
                        if service_config.get("critical", False):
                            # Critical service needs immediate attention
                            await self.self_heal_service(service_id)
                        else:
                            # Non-critical service, log and continue
                            logger.warning(f"{service_config['name']} is {health.status}")
                
                # Check overall system health
                if hardware.memory_percent > 90:
                    logger.warning(f"System memory usage critical: {hardware.memory_percent}%")
                    await self.optimize_memory_usage()
                    
                if hardware.cpu_percent > 95:
                    logger.warning(f"System CPU usage critical: {hardware.cpu_percent}%")
                    await self.optimize_cpu_usage()
                
                # Sleep before next check
                await asyncio.sleep(self.healing_config["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)
    
    async def optimize_memory_usage(self):
        """Optimize system memory usage"""
        logger.info("Optimizing memory usage...")
        
        # Find services using most memory
        memory_usage = []
        for service_id, health in self.service_health.items():
            if health.status == "healthy":
                memory_usage.append((service_id, health.memory_usage))
        
        memory_usage.sort(key=lambda x: x[1], reverse=True)
        
        # Restart top memory consumers if they're not critical
        for service_id, mem_usage in memory_usage[:3]:
            if not self.services[service_id].get("critical", False):
                logger.info(f"Restarting {self.services[service_id]['name']} to free memory")
                await self.restart_service(service_id)
                await asyncio.sleep(5)
    
    async def optimize_cpu_usage(self):
        """Optimize system CPU usage"""
        logger.info("Optimizing CPU usage...")
        
        # Reduce thread counts for non-critical services
        for service_id, health in self.service_health.items():
            if health.cpu_usage > 50 and not self.services[service_id].get("critical", False):
                logger.info(f"Throttling {self.services[service_id]['name']} CPU usage")
                # In real implementation, would adjust service configuration
    
    async def start_ecosystem(self):
        """Start the entire ecosystem in priority order"""
        logger.info("="*60)
        logger.info("Starting MCPVotsAGI Ecosystem")
        logger.info("="*60)
        
        # Check hardware
        hardware = await self.check_hardware_status()
        logger.info(f"Hardware Status:")
        logger.info(f"  CPU: {hardware.cpu_percent}% | RAM: {hardware.memory_percent}% | Disk: {hardware.disk_percent}%")
        logger.info(f"  GPU: {'Available' if hardware.gpu_available else 'Not Available'}")
        logger.info(f"  Optimal Threads: {hardware.optimal_threads}")
        logger.info(f"  Available RAM: {hardware.available_ram_gb:.2f} GB")
        
        # Group services by priority
        priority_groups = {}
        for service_id, config in self.services.items():
            priority = config.get("priority", 99)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(service_id)
        
        # Start services in priority order
        for priority in sorted(priority_groups.keys()):
            logger.info(f"\nStarting Priority {priority} services...")
            
            tasks = []
            for service_id in priority_groups[priority]:
                task = self.start_service(service_id, self.services[service_id])
                tasks.append(task)
            
            # Start all services in this priority group concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Wait a bit before next priority group
            await asyncio.sleep(2)
        
        logger.info("\n" + "="*60)
        logger.info("Ecosystem Startup Complete")
        logger.info("="*60)
        
        # Print status summary
        await self.print_status_summary()
    
    async def stop_ecosystem(self):
        """Stop all services gracefully"""
        logger.info("Stopping MCPVotsAGI Ecosystem...")
        
        # Stop in reverse priority order
        priority_groups = {}
        for service_id, config in self.services.items():
            priority = config.get("priority", 99)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(service_id)
        
        for priority in sorted(priority_groups.keys(), reverse=True):
            for service_id in priority_groups[priority]:
                await self.stop_service(service_id)
        
        logger.info("Ecosystem stopped")
    
    async def print_status_summary(self):
        """Print ecosystem status summary"""
        healthy = sum(1 for h in self.service_health.values() if h.status == "healthy")
        total = len(self.service_health)
        
        print("\nService Status Summary:")
        print("-" * 60)
        
        for service_id, health in self.service_health.items():
            status_icon = "🟢" if health.status == "healthy" else "🔴"
            print(f"{status_icon} {health.name:<30} Port {health.port:<6} {health.status:<10} "
                  f"CPU: {health.cpu_usage:>5.1f}% MEM: {health.memory_usage:>6.1f}MB")
        
        print("-" * 60)
        print(f"Total: {healthy}/{total} services healthy")
    
    def create_windows_service(self):
        """Create Windows service for auto-start"""
        if platform.system() != "Windows":
            logger.warning("Windows service creation only available on Windows")
            return
        
        service_script = r'''
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import asyncio

sys.path.append(r"C:\Workspace\MCPVotsAGI")
# Import path adjusted - see services/dgm_integration_manager.py for proper imports
# from ecosystem_manager import EcosystemManager

class MCPVotsAGIService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MCPVotsAGI"
    _svc_display_name_ = "MCPVotsAGI Ecosystem Service"
    _svc_description_ = "Manages the MCPVotsAGI AI ecosystem with auto-start and self-healing"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.manager = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.manager:
            asyncio.run(self.manager.stop_ecosystem())
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        self.manager = EcosystemManager()
        
        # Start ecosystem
        asyncio.run(self.manager.start_ecosystem())
        
        # Start health monitor in background
        monitor_task = asyncio.create_task(self.manager.continuous_health_monitor())
        
        # Wait for stop signal
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        
        # Cancel monitor task
        monitor_task.cancel()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MCPVotsAGIService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MCPVotsAGIService)
'''
        
        # Save service script
        service_path = self.mcpvotsagi_path / "mcpvotsagi_service.py"
        service_path.write_text(service_script)
        
        # Create batch file to install service
        install_script = f'''@echo off
echo Installing MCPVotsAGI Service...
python "{service_path}" install
echo Starting MCPVotsAGI Service...
python "{service_path}" start
echo.
echo Service installed and started!
echo.
echo To manage the service:
echo   - Stop:    python "{service_path}" stop
echo   - Remove:  python "{service_path}" remove
echo   - Status:  sc query MCPVotsAGI
pause
'''
        
        install_path = self.mcpvotsagi_path / "install_service.bat"
        install_path.write_text(install_script)
        
        logger.info(f"Windows service installer created at: {install_path}")
    
    def create_systemd_service(self):
        """Create systemd service for Linux auto-start"""
        if platform.system() != "Linux":
            logger.warning("Systemd service creation only available on Linux")
            return
        
        service_content = f'''[Unit]
Description=MCPVotsAGI Ecosystem Service
After=network.target

[Service]
Type=simple
User={os.getenv("USER")}
WorkingDirectory={self.mcpvotsagi_path}
Environment="PATH=/usr/local/bin:/usr/bin:/bin:{os.getenv("PATH")}"
ExecStart=/usr/bin/python3 {self.mcpvotsagi_path}/ecosystem_manager.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
        
        service_path = Path("/etc/systemd/system/mcpvotsagi.service")
        
        # Create install script
        install_script = f'''#!/bin/bash
echo "Installing MCPVotsAGI systemd service..."

# Create service file
sudo tee {service_path} > /dev/null << EOF
{service_content}
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable mcpvotsagi.service
sudo systemctl start mcpvotsagi.service

echo "Service installed and started!"
echo ""
echo "To manage the service:"
echo "  - Status: sudo systemctl status mcpvotsagi"
echo "  - Stop:   sudo systemctl stop mcpvotsagi"
echo "  - Start:  sudo systemctl start mcpvotsagi"
echo "  - Logs:   sudo journalctl -u mcpvotsagi -f"
'''
        
        install_path = self.mcpvotsagi_path / "install_service.sh"
        install_path.write_text(install_script)
        install_path.chmod(0o755)
        
        logger.info(f"Systemd service installer created at: {install_path}")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCPVotsAGI Ecosystem Manager")
    parser.add_argument("command", 
                       choices=["start", "stop", "status", "monitor", "install-service", "daemon"],
                       help="Command to execute")
    parser.add_argument("--force", action="store_true", help="Force operation")
    
    args = parser.parse_args()
    
    manager = EcosystemManager()
    
    if args.command == "start":
        await manager.start_ecosystem()
        # Keep running with health monitor
        await manager.continuous_health_monitor()
        
    elif args.command == "stop":
        await manager.stop_ecosystem()
        
    elif args.command == "status":
        # Quick status check
        for service_id, config in manager.services.items():
            health = await manager.health_check_service(service_id, config)
            manager.service_health[service_id] = health
        await manager.print_status_summary()
        
    elif args.command == "monitor":
        # Start continuous monitoring
        await manager.continuous_health_monitor()
        
    elif args.command == "install-service":
        # Install auto-start service
        if platform.system() == "Windows":
            manager.create_windows_service()
        elif platform.system() == "Linux":
            manager.create_systemd_service()
        else:
            logger.error("Service installation not supported on this platform")
            
    elif args.command == "daemon":
        # Run as daemon (for systemd)
        await manager.start_ecosystem()
        await manager.continuous_health_monitor()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("MCPVotsAGI Ecosystem Manager")
        print("="*40)
        print("\nUsage: python ecosystem_manager.py [command]")
        print("\nCommands:")
        print("  start           - Start all services")
        print("  stop            - Stop all services")
        print("  status          - Check service status")
        print("  monitor         - Start health monitoring")
        print("  install-service - Install auto-start service")
        print("\nExample: python ecosystem_manager.py start")
        sys.exit(1)
    
    asyncio.run(main())