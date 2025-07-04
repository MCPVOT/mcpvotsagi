#!/usr/bin/env python3
"""
Oracle AGI Ultimate Unified Dashboard V2
========================================
Production-ready dashboard with full ecosystem understanding,
self-healing, and hardware optimization
"""

import asyncio
import json
import os
import sys
import time
import psutil
import platform
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
from aiohttp import web
import aiohttp_cors
import websockets
import sqlite3
import hashlib
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleAGI")

# Import OpenCTI integration
try:
    from opencti_integration import OpenCTIDashboardIntegration
    OPENCTI_AVAILABLE = True
except ImportError:
    OPENCTI_AVAILABLE = False
    logger.warning("OpenCTI integration not available")

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: float
    network_recv: float
    active_connections: int
    response_time_ms: float
    error_rate: float
    
@dataclass
class ServiceStatus:
    """Individual service status"""
    name: str
    port: int
    status: str  # 'online', 'offline', 'degraded', 'starting'
    health_score: float  # 0-100
    uptime: timedelta
    last_error: Optional[str]
    metrics: Dict[str, Any]

class OracleAGIUnifiedDashboard:
    """Ultimate unified dashboard with full ecosystem integration"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_cors()
        
        # Paths
        self.workspace = Path("C:/Workspace") if platform.system() == "Windows" else Path("/mnt/c/Workspace")
        self.mcpvots_path = self.workspace / "MCPVots"
        self.mcpvotsagi_path = self.workspace / "MCPVotsAGI"
        
        # Ecosystem knowledge database
        self.knowledge_db = self.mcpvotsagi_path / "ecosystem_knowledge.db"
        self.metrics_db = self.mcpvotsagi_path / "dashboard_metrics.db"
        self.init_databases()
        
        # Service registry with full understanding
        self.service_registry = {
            # Core Services
            "oracle_core": {
                "name": "Oracle AGI Core",
                "port": 8888,
                "endpoint": "http://localhost:8888",
                "capabilities": ["orchestration", "reasoning", "planning"],
                "dependencies": ["memory_mcp", "trilogy_agi"],
                "health_endpoint": "/health"
            },
            "trilogy_brain": {
                "name": "Trilogy Brain",
                "port": 8887,
                "endpoint": "http://localhost:8887",
                "capabilities": ["deepseek", "gemini", "multi-model"],
                "dependencies": ["ollama"],
                "health_endpoint": "/api/health"
            },
            "dgm_voltagents": {
                "name": "DGM Voltagents",
                "port": 8886,
                "endpoint": "http://localhost:8886",
                "capabilities": ["self-improvement", "evolution", "optimization"],
                "dependencies": ["memory_mcp"],
                "health_endpoint": "/health"
            },
            
            # MCP Services
            "github_mcp": {
                "name": "GitHub MCP",
                "port": 3001,
                "endpoint": "ws://localhost:3001",
                "capabilities": ["repos", "issues", "prs", "actions"],
                "protocol": "websocket"
            },
            "memory_mcp": {
                "name": "Memory MCP",
                "port": 3002,
                "endpoint": "ws://localhost:3002",
                "capabilities": ["knowledge-graph", "embeddings", "storage"],
                "protocol": "websocket",
                "critical": True
            },
            "solana_mcp": {
                "name": "Solana MCP",
                "port": 3005,
                "endpoint": "ws://localhost:3005",
                "capabilities": ["blockchain", "defi", "smart-contracts"],
                "protocol": "websocket"
            },
            
            # AI Services
            "ollama": {
                "name": "Ollama",
                "port": 11434,
                "endpoint": "http://localhost:11434",
                "capabilities": ["deepseek", "codellama", "llama2"],
                "health_endpoint": "/api/tags"
            },
            "gemini_cli": {
                "name": "Gemini CLI",
                "port": 8015,
                "endpoint": "ws://localhost:8015",
                "capabilities": ["gemini-2.5", "multimodal", "reasoning"],
                "protocol": "websocket"
            },
            
            # Workflow Services
            "deerflow": {
                "name": "DeerFlow",
                "port": 8014,
                "endpoint": "ws://localhost:8014",
                "capabilities": ["workflow", "orchestration", "optimization"],
                "protocol": "websocket"
            },
            "n8n": {
                "name": "n8n Workflows",
                "port": 5678,
                "endpoint": "http://localhost:5678",
                "capabilities": ["automation", "integration", "visual-workflows"],
                "health_endpoint": "/healthz"
            },
            
            # Storage Services
            "ipfs": {
                "name": "IPFS",
                "port": 5001,
                "endpoint": "http://localhost:5001",
                "capabilities": ["distributed-storage", "content-addressing"],
                "health_endpoint": "/api/v0/id"
            }
        }
        
        # Real-time metrics
        self.system_metrics: List[SystemMetrics] = []
        self.service_status: Dict[str, ServiceStatus] = {}
        self.active_connections = set()
        
        # OpenCTI Security Integration
        self.opencti = None
        if OPENCTI_AVAILABLE:
            self.opencti = OpenCTIDashboardIntegration()
            asyncio.create_task(self._init_opencti())
        
        # Solana Trading Integration
        try:
            from solana_precious_metals_trading import SolanaTradingIntegration
            self.solana_trader = SolanaTradingIntegration()
            asyncio.create_task(self._init_solana_trading())
            logger.info("Solana precious metals trading integration loaded")
        except ImportError:
            self.solana_trader = None
            logger.warning("Solana trading integration not available")
        
        # Wallet Integration
        try:
            from wallet_integration import WalletIntegrationAPI, get_wallet_integration_html
            self.wallet_api = WalletIntegrationAPI()
            self.wallet_integration_html = get_wallet_integration_html()
            logger.info("Wallet integration loaded")
        except ImportError:
            self.wallet_api = None
            self.wallet_integration_html = ""
            logger.warning("Wallet integration not available")
        
        # LLM optimization configurations
        self.llm_assignments = {
            "code_analysis": {
                "primary": "deepseek-coder:latest",
                "fallback": "codellama:7b",
                "endpoint": "ollama"
            },
            "reasoning": {
                "primary": "gemini-2.5-pro",
                "fallback": "deepseek-r1:latest",
                "endpoint": "gemini_cli"
            },
            "memory_consolidation": {
                "primary": "llama2:7b",
                "fallback": "mistral:7b",
                "endpoint": "ollama"
            },
            "security_analysis": {
                "primary": "codellama:7b",
                "fallback": "deepseek-coder:latest",
                "endpoint": "ollama"
            }
        }
        
        # Hardware optimization settings
        self.hardware_optimization = {
            "cpu_threshold": 80,  # Start throttling at 80% CPU
            "memory_threshold": 85,  # Start optimizing at 85% memory
            "gpu_enabled": self.check_gpu_availability(),
            "optimal_workers": self.calculate_optimal_workers()
        }
        
        # Setup routes
        self.setup_routes()
        
    def setup_cors(self):
        """Setup CORS for the application"""
        self.cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
    def init_databases(self):
        """Initialize dashboard databases"""
        # Ensure directory exists
        self.mcpvotsagi_path.mkdir(exist_ok=True)
        
        # Initialize ecosystem knowledge database
        conn = sqlite3.connect(self.knowledge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_profiles (
                service_id TEXT PRIMARY KEY,
                profile_data TEXT,
                capabilities TEXT,
                dependencies TEXT,
                performance_baseline TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ecosystem_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                event_type TEXT,
                service_id TEXT,
                event_data TEXT,
                severity TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize metrics database
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_sent REAL,
                network_recv REAL,
                active_connections INTEGER,
                response_time_ms REAL,
                error_rate REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                service_id TEXT,
                status TEXT,
                health_score REAL,
                response_time REAL,
                error_count INTEGER,
                custom_metrics TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def check_gpu_availability(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
            
    def calculate_optimal_workers(self) -> int:
        """Calculate optimal number of workers based on hardware"""
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Base calculation on CPU cores and available memory
        optimal = min(
            cpu_count - 2,  # Leave 2 cores for system
            int(memory_gb / 2)  # 2GB per worker
        )
        
        return max(2, optimal)  # At least 2 workers
        
    def setup_routes(self):
        """Setup all API routes"""
        # API routes
        routes = [
            ('GET', '/api/status', self.get_system_status),
            ('GET', '/api/services', self.get_services_status),
            ('GET', '/api/metrics', self.get_system_metrics),
            ('GET', '/api/ecosystem/map', self.get_ecosystem_map),
            ('GET', '/api/ecosystem/health', self.get_ecosystem_health),
            ('POST', '/api/service/{service_id}/restart', self.restart_service),
            ('POST', '/api/service/{service_id}/optimize', self.optimize_service),
            ('GET', '/api/hardware', self.get_hardware_status),
            ('GET', '/api/llm/assignments', self.get_llm_assignments),
            ('POST', '/api/llm/optimize', self.optimize_llm_usage),
            ('GET', '/api/security/status', self.get_security_status),
            ('POST', '/api/security/check_ioc', self.check_ioc),
            ('GET', '/api/security/service/{service_id}', self.get_service_security),
            ('GET', '/api/trading/status', self.get_trading_status),
            ('POST', '/api/trading/start', self.start_trading),
            ('POST', '/api/trading/stop', self.stop_trading),
            ('POST', '/api/trading/manual', self.manual_trade),
            ('GET', '/api/trading/portfolio', self.get_portfolio),
            ('POST', '/api/wallet/connect', self.handle_wallet_connect),
            ('POST', '/api/wallet/disconnect', self.handle_wallet_disconnect),
            ('GET', '/ws', self.websocket_handler),
            ('GET', '/', self.serve_dashboard)
        ]
        
        # Add routes with CORS
        for method, path, handler in routes:
            resource = self.cors.add(self.app.router.add_resource(path))
            self.cors.add(resource.add_route(method, handler))
        
        # Static files (no CORS needed)
        self.app.router.add_static('/static', self.mcpvotsagi_path / 'static')
    
    async def collect_system_metrics(self):
        """Collect system-wide metrics"""
        # Get network stats
        net_io = psutil.net_io_counters()
        
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage('/').percent,
            network_sent=net_io.bytes_sent,
            network_recv=net_io.bytes_recv,
            active_connections=len(self.active_connections),
            response_time_ms=await self.measure_average_response_time(),
            error_rate=await self.calculate_error_rate()
        )
        
        # Store in memory (keep last hour)
        self.system_metrics.append(metrics)
        if len(self.system_metrics) > 3600:  # 1 hour at 1 sample/sec
            self.system_metrics.pop(0)
        
        # Store in database
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics 
            (timestamp, cpu_percent, memory_percent, disk_percent, 
             network_sent, network_recv, active_connections, 
             response_time_ms, error_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp,
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.disk_percent,
            metrics.network_sent,
            metrics.network_recv,
            metrics.active_connections,
            metrics.response_time_ms,
            metrics.error_rate
        ))
        
        conn.commit()
        conn.close()
        
        return metrics
    
    async def check_service_health(self, service_id: str, service_config: Dict[str, Any]) -> ServiceStatus:
        """Check health of a specific service"""
        start_time = time.time()
        status = "offline"
        health_score = 0.0
        last_error = None
        metrics = {}
        
        try:
            if service_config.get("protocol") == "websocket":
                # WebSocket health check
                try:
                    async with websockets.connect(service_config["endpoint"], timeout=5) as ws:
                        await ws.ping()
                        status = "online"
                        health_score = 100.0
                except:
                    status = "offline"
                    health_score = 0.0
            else:
                # HTTP health check
                health_endpoint = service_config.get("health_endpoint", "/health")
                url = f"{service_config['endpoint']}{health_endpoint}"
                
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                status = "online"
                                health_score = 100.0
                                
                                # Try to get additional metrics
                                try:
                                    data = await response.json()
                                    metrics = data.get("metrics", {})
                                except:
                                    pass
                            else:
                                status = "degraded"
                                health_score = 50.0
                    except aiohttp.ClientError as e:
                        status = "offline"
                        health_score = 0.0
                        last_error = str(e)
                        
        except Exception as e:
            status = "offline"
            health_score = 0.0
            last_error = str(e)
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Calculate uptime (simplified - in production would track actual uptime)
        uptime = timedelta(hours=1) if status == "online" else timedelta(0)
        
        service_status = ServiceStatus(
            name=service_config["name"],
            port=service_config["port"],
            status=status,
            health_score=health_score,
            uptime=uptime,
            last_error=last_error,
            metrics={
                "response_time_ms": response_time,
                **metrics
            }
        )
        
        # Store in database
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO service_metrics
            (timestamp, service_id, status, health_score, response_time, error_count, custom_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            service_id,
            status,
            health_score,
            response_time,
            1 if status == "offline" else 0,
            json.dumps(metrics)
        ))
        
        conn.commit()
        conn.close()
        
        return service_status
    
    async def measure_average_response_time(self) -> float:
        """Measure average response time across all services"""
        total_time = 0
        count = 0
        
        for service_id, status in self.service_status.items():
            if status.status == "online":
                total_time += status.metrics.get("response_time_ms", 0)
                count += 1
        
        return total_time / count if count > 0 else 0
    
    async def calculate_error_rate(self) -> float:
        """Calculate system-wide error rate"""
        total_services = len(self.service_registry)
        offline_services = sum(1 for s in self.service_status.values() if s.status == "offline")
        
        return (offline_services / total_services * 100) if total_services > 0 else 0
    
    async def get_system_status(self, request):
        """Get overall system status"""
        # Collect latest metrics
        metrics = await self.collect_system_metrics()
        
        # Check all services
        for service_id, service_config in self.service_registry.items():
            self.service_status[service_id] = await self.check_service_health(service_id, service_config)
        
        # Calculate overall health
        total_health = sum(s.health_score for s in self.service_status.values())
        avg_health = total_health / len(self.service_status) if self.service_status else 0
        
        status = {
            "status": "healthy" if avg_health > 80 else "degraded" if avg_health > 50 else "critical",
            "health_score": avg_health,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
                "active_connections": metrics.active_connections,
                "response_time_ms": metrics.response_time_ms,
                "error_rate": metrics.error_rate
            },
            "services": {
                "total": len(self.service_registry),
                "online": sum(1 for s in self.service_status.values() if s.status == "online"),
                "offline": sum(1 for s in self.service_status.values() if s.status == "offline"),
                "degraded": sum(1 for s in self.service_status.values() if s.status == "degraded")
            }
        }
        
        return web.json_response(status)
    
    async def get_services_status(self, request):
        """Get detailed status of all services"""
        services = {}
        
        for service_id, status in self.service_status.items():
            services[service_id] = {
                "name": status.name,
                "port": status.port,
                "status": status.status,
                "health_score": status.health_score,
                "uptime": str(status.uptime),
                "last_error": status.last_error,
                "metrics": status.metrics,
                "capabilities": self.service_registry[service_id].get("capabilities", []),
                "dependencies": self.service_registry[service_id].get("dependencies", [])
            }
        
        return web.json_response(services)
    
    async def get_system_metrics(self, request):
        """Get system metrics history"""
        # Get time range from query params
        hours = int(request.rel_url.query.get('hours', 1))
        
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM system_metrics 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC
        ''', (since,))
        
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            metrics.append({
                "timestamp": row[1],
                "cpu_percent": row[2],
                "memory_percent": row[3],
                "disk_percent": row[4],
                "network_sent": row[5],
                "network_recv": row[6],
                "active_connections": row[7],
                "response_time_ms": row[8],
                "error_rate": row[9]
            })
        
        return web.json_response(metrics)
    
    async def get_ecosystem_map(self, request):
        """Get complete ecosystem map with relationships"""
        ecosystem = {
            "nodes": [],
            "edges": [],
            "clusters": {}
        }
        
        # Define service clusters
        clusters = {
            "core": ["oracle_core", "trilogy_brain", "dgm_voltagents"],
            "mcp": ["github_mcp", "memory_mcp", "solana_mcp"],
            "ai": ["ollama", "gemini_cli"],
            "workflow": ["deerflow", "n8n"],
            "storage": ["ipfs"]
        }
        
        # Create nodes
        for service_id, service_config in self.service_registry.items():
            status = self.service_status.get(service_id)
            
            # Find cluster
            cluster = None
            for cluster_name, services in clusters.items():
                if service_id in services:
                    cluster = cluster_name
                    break
            
            node = {
                "id": service_id,
                "label": service_config["name"],
                "cluster": cluster,
                "status": status.status if status else "unknown",
                "health": status.health_score if status else 0,
                "port": service_config["port"],
                "capabilities": service_config.get("capabilities", [])
            }
            
            ecosystem["nodes"].append(node)
        
        # Create edges based on dependencies
        for service_id, service_config in self.service_registry.items():
            for dep in service_config.get("dependencies", []):
                if dep in self.service_registry:
                    edge = {
                        "source": service_id,
                        "target": dep,
                        "type": "depends_on"
                    }
                    ecosystem["edges"].append(edge)
        
        # Add capability-based relationships
        capability_map = {}
        for service_id, service_config in self.service_registry.items():
            for capability in service_config.get("capabilities", []):
                if capability not in capability_map:
                    capability_map[capability] = []
                capability_map[capability].append(service_id)
        
        # Create edges for services sharing capabilities
        for capability, services in capability_map.items():
            if len(services) > 1:
                for i in range(len(services)):
                    for j in range(i + 1, len(services)):
                        edge = {
                            "source": services[i],
                            "target": services[j],
                            "type": "shares_capability",
                            "capability": capability
                        }
                        ecosystem["edges"].append(edge)
        
        ecosystem["clusters"] = clusters
        
        return web.json_response(ecosystem)
    
    async def get_ecosystem_health(self, request):
        """Get detailed ecosystem health analysis"""
        health_analysis = {
            "overall_score": 0,
            "components": {},
            "issues": [],
            "recommendations": []
        }
        
        # Analyze each cluster
        clusters = {
            "core": ["oracle_core", "trilogy_brain", "dgm_voltagents"],
            "mcp": ["github_mcp", "memory_mcp", "solana_mcp"],
            "ai": ["ollama", "gemini_cli"],
            "workflow": ["deerflow", "n8n"],
            "storage": ["ipfs"]
        }
        
        total_score = 0
        
        for cluster_name, services in clusters.items():
            cluster_health = {
                "services": {},
                "score": 0,
                "status": "unknown"
            }
            
            cluster_score = 0
            service_count = 0
            
            for service_id in services:
                if service_id in self.service_status:
                    status = self.service_status[service_id]
                    cluster_health["services"][service_id] = {
                        "name": status.name,
                        "status": status.status,
                        "health": status.health_score
                    }
                    cluster_score += status.health_score
                    service_count += 1
                    
                    # Check for issues
                    if status.status == "offline":
                        health_analysis["issues"].append({
                            "severity": "high",
                            "service": status.name,
                            "issue": "Service is offline",
                            "cluster": cluster_name
                        })
                    elif status.status == "degraded":
                        health_analysis["issues"].append({
                            "severity": "medium",
                            "service": status.name,
                            "issue": "Service is degraded",
                            "cluster": cluster_name
                        })
            
            if service_count > 0:
                cluster_health["score"] = cluster_score / service_count
                cluster_health["status"] = (
                    "healthy" if cluster_health["score"] > 80 else
                    "degraded" if cluster_health["score"] > 50 else
                    "critical"
                )
            
            health_analysis["components"][cluster_name] = cluster_health
            total_score += cluster_health["score"]
        
        # Calculate overall score
        health_analysis["overall_score"] = total_score / len(clusters) if clusters else 0
        
        # Generate recommendations
        if health_analysis["overall_score"] < 80:
            health_analysis["recommendations"].append({
                "priority": "high",
                "action": "Investigate and restart offline services",
                "reason": "Multiple services are not functioning properly"
            })
        
        # Check hardware
        latest_metrics = self.system_metrics[-1] if self.system_metrics else None
        if latest_metrics:
            if latest_metrics.cpu_percent > self.hardware_optimization["cpu_threshold"]:
                health_analysis["recommendations"].append({
                    "priority": "high",
                    "action": "Optimize CPU usage",
                    "reason": f"CPU usage is {latest_metrics.cpu_percent}%"
                })
            
            if latest_metrics.memory_percent > self.hardware_optimization["memory_threshold"]:
                health_analysis["recommendations"].append({
                    "priority": "high",
                    "action": "Optimize memory usage",
                    "reason": f"Memory usage is {latest_metrics.memory_percent}%"
                })
        
        return web.json_response(health_analysis)
    
    async def restart_service(self, request):
        """Restart a specific service"""
        service_id = request.match_info['service_id']
        
        if service_id not in self.service_registry:
            return web.json_response({"error": "Service not found"}, status=404)
        
        # Import ecosystem manager
        from ecosystem_manager import EcosystemManager
        
        manager = EcosystemManager()
        success = await manager.restart_service(service_id)
        
        return web.json_response({
            "service": service_id,
            "action": "restart",
            "success": success
        })
    
    async def optimize_service(self, request):
        """Optimize a specific service using AI"""
        service_id = request.match_info['service_id']
        
        if service_id not in self.service_registry:
            return web.json_response({"error": "Service not found"}, status=404)
        
        # Get service status and metrics
        status = self.service_status.get(service_id)
        if not status:
            return web.json_response({"error": "Service status not available"}, status=400)
        
        # Use appropriate LLM for optimization
        llm_config = self.llm_assignments["code_analysis"]
        
        optimization_prompt = f"""
        Analyze and optimize the service: {status.name}
        
        Current Status:
        - Health Score: {status.health_score}
        - Response Time: {status.metrics.get('response_time_ms', 0)}ms
        - Status: {status.status}
        
        Service Capabilities: {self.service_registry[service_id].get('capabilities', [])}
        
        Provide specific optimization recommendations.
        """
        
        # Call LLM for optimization
        recommendations = await self.call_llm_for_optimization(
            llm_config["endpoint"],
            llm_config["primary"],
            optimization_prompt
        )
        
        return web.json_response({
            "service": service_id,
            "current_health": status.health_score,
            "recommendations": recommendations
        })
    
    async def call_llm_for_optimization(self, endpoint: str, model: str, prompt: str) -> List[str]:
        """Call LLM for optimization suggestions"""
        recommendations = []
        
        try:
            if endpoint == "ollama":
                url = f"http://localhost:11434/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "temperature": 0.7
                }
            elif endpoint == "gemini_cli":
                url = f"http://localhost:8015/api/chat"
                payload = {
                    "message": prompt,
                    "model": "gemini-2.5-pro"
                }
            else:
                return ["Unable to generate recommendations: Unknown endpoint"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse recommendations from response
                        text = data.get("response", "") or data.get("message", "")
                        # Simple parsing - in production would use more sophisticated parsing
                        lines = text.split('\n')
                        for line in lines:
                            if line.strip() and (line.startswith('-') or line.startswith('*')):
                                recommendations.append(line.strip().lstrip('-*').strip())
                        
        except Exception as e:
            logger.error(f"LLM optimization call failed: {e}")
            recommendations.append(f"Error getting recommendations: {str(e)}")
        
        return recommendations if recommendations else ["No specific recommendations generated"]
    
    async def get_hardware_status(self, request):
        """Get current hardware status"""
        cpu_info = {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "count_logical": psutil.cpu_count(logical=True),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        }
        
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
        
        # Network interfaces
        network_info = {}
        for interface, addrs in psutil.net_if_addrs().items():
            network_info[interface] = [
                {"family": addr.family.name, "address": addr.address}
                for addr in addrs
            ]
        
        # Temperature if available
        temps = {}
        try:
            for name, entries in psutil.sensors_temperatures().items():
                temps[name] = [
                    {"label": e.label, "current": e.current, "high": e.high, "critical": e.critical}
                    for e in entries
                ]
        except:
            pass
        
        hardware_status = {
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "network": network_info,
            "temperatures": temps,
            "gpu_available": self.hardware_optimization["gpu_enabled"],
            "optimal_workers": self.hardware_optimization["optimal_workers"]
        }
        
        return web.json_response(hardware_status)
    
    async def get_llm_assignments(self, request):
        """Get current LLM assignments for different tasks"""
        return web.json_response(self.llm_assignments)
    
    async def optimize_llm_usage(self, request):
        """Optimize LLM usage based on current hardware"""
        data = await request.json()
        task_type = data.get("task_type", "general")
        
        # Get current hardware status
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        recommendations = {
            "task_type": task_type,
            "current_assignment": self.llm_assignments.get(task_type, {}),
            "recommendations": []
        }
        
        # Optimize based on hardware
        if cpu_percent > 80 or memory_percent > 85:
            # High resource usage, recommend lighter models
            recommendations["recommendations"].append({
                "action": "switch_to_lighter_model",
                "reason": f"High resource usage (CPU: {cpu_percent}%, Memory: {memory_percent}%)",
                "suggested_model": "codellama:7b" if task_type == "code_analysis" else "mistral:7b"
            })
        else:
            # Resources available, can use more powerful models
            recommendations["recommendations"].append({
                "action": "use_optimal_model",
                "reason": "Sufficient resources available",
                "suggested_model": self.llm_assignments[task_type]["primary"]
            })
        
        # Check GPU availability for specific tasks
        if self.hardware_optimization["gpu_enabled"] and task_type in ["reasoning", "code_analysis"]:
            recommendations["recommendations"].append({
                "action": "enable_gpu_acceleration",
                "reason": "GPU available for acceleration"
            })
        
        return web.json_response(recommendations)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.active_connections.add(ws)
        
        try:
            # Send initial status
            status = await self.get_system_status(request)
            await ws.send_json({
                "type": "status",
                "data": json.loads(status.text)
            })
            
            # Keep connection alive and send updates
            while not ws.closed:
                # Send periodic updates
                await asyncio.sleep(5)
                
                # Update metrics
                metrics = await self.collect_system_metrics()
                
                # Update service status
                for service_id, service_config in self.service_registry.items():
                    self.service_status[service_id] = await self.check_service_health(
                        service_id, service_config
                    )
                
                # Send update
                update = {
                    "type": "update",
                    "timestamp": datetime.now().isoformat(),
                    "metrics": asdict(metrics),
                    "services": {
                        service_id: {
                            "status": status.status,
                            "health": status.health_score
                        }
                        for service_id, status in self.service_status.items()
                    }
                }
                
                await ws.send_json(update)
                
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.active_connections.discard(ws)
            
        return ws
    
    async def serve_dashboard(self, request):
        """Serve the main dashboard HTML"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle AGI Ultimate Dashboard V2</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: #1a1a2e;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #2a2a3e;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,150,255,0.2);
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #00ff88, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .services-container {
            background: #1a1a2e;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .service-card {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2a3f5f;
            transition: all 0.3s ease;
        }
        
        .service-card:hover {
            border-color: #0099ff;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .status-online { background: #00ff88; }
        .status-offline { background: #ff3838; }
        .status-degraded { background: #ffaa00; }
        
        .health-bar {
            width: 100%;
            height: 8px;
            background: #2a2a3e;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .health-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00d4ff);
            transition: width 0.5s ease;
        }
        
        .ecosystem-map {
            background: #1a1a2e;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            height: 500px;
            position: relative;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .btn {
            background: linear-gradient(135deg, #0099ff, #00d4ff);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,150,255,0.4);
        }
        
        .logs-container {
            background: #0f0f1f;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid #1a1a2e;
        }
        
        .log-info { color: #00d4ff; }
        .log-warning { color: #ffaa00; }
        .log-error { color: #ff3838; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Oracle AGI Ultimate Dashboard V2</h1>
            <p>Full Ecosystem Control & Monitoring <span class="live-indicator"></span></p>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshStatus()">Refresh Status</button>
            <button class="btn" onclick="showEcosystemMap()">Ecosystem Map</button>
            <button class="btn" onclick="optimizeSystem()">Optimize System</button>
            <button class="btn" onclick="viewLogs()">View Logs</button>
        </div>
        
        <div class="metrics-grid" id="metricsGrid">
            <div class="metric-card">
                <h3>CPU Usage</h3>
                <div class="metric-value" id="cpuUsage">--</div>
                <div class="health-bar">
                    <div class="health-fill" id="cpuBar" style="width: 0%"></div>
                </div>
            </div>
            <div class="metric-card">
                <h3>Memory Usage</h3>
                <div class="metric-value" id="memoryUsage">--</div>
                <div class="health-bar">
                    <div class="health-fill" id="memoryBar" style="width: 0%"></div>
                </div>
            </div>
            <div class="metric-card">
                <h3>Active Services</h3>
                <div class="metric-value" id="activeServices">--</div>
                <div class="health-bar">
                    <div class="health-fill" id="servicesBar" style="width: 0%"></div>
                </div>
            </div>
            <div class="metric-card">
                <h3>System Health</h3>
                <div class="metric-value" id="systemHealth">--</div>
                <div class="health-bar">
                    <div class="health-fill" id="healthBar" style="width: 0%"></div>
                </div>
            </div>
        </div>
        
        <div class="services-container">
            <h2>Service Status</h2>
            <div class="service-grid" id="serviceGrid">
                <!-- Services will be populated here -->
            </div>
        </div>
        
        <div class="ecosystem-map" id="ecosystemMap" style="display: none;">
            <h2>Ecosystem Map</h2>
            <canvas id="mapCanvas" width="1340" height="450"></canvas>
        </div>
        
        <div class="logs-container" id="logsContainer" style="display: none;">
            <h3>System Logs</h3>
            <div id="logEntries">
                <!-- Logs will be populated here -->
            </div>
        </div>
        
        <!-- OpenCTI Security Section -->
        <div class="security-container">
            <h2>🛡️ Security Status (OpenCTI)</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Security Score</h3>
                    <div class="metric-value" id="securityScore">--</div>
                    <div class="health-bar">
                        <div class="health-fill" id="securityBar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric-card">
                    <h3>Active Threats</h3>
                    <div class="metric-value" id="activeThreats">--</div>
                </div>
                <div class="metric-card">
                    <h3>Critical Alerts</h3>
                    <div class="metric-value" id="criticalAlerts" style="color: #ff3838;">--</div>
                </div>
                <div class="metric-card">
                    <h3>IOC Matches</h3>
                    <div class="metric-value" id="iocMatches">--</div>
                </div>
            </div>
            
            <div class="threat-summary" style="margin-top: 20px; background: #16213e; padding: 20px; border-radius: 10px;">
                <h3>Threat Intelligence Summary</h3>
                <div id="threatSummary">Loading...</div>
            </div>
            
            <div class="recent-threats" style="margin-top: 20px; background: #16213e; padding: 20px; border-radius: 10px;">
                <h3>Recent Threat Indicators</h3>
                <div id="recentThreats">Loading...</div>
            </div>
        </div>
        
        <!-- Solana Trading Section -->
        <div class="trading-container" style="margin-top: 30px;">
            <h2>💰 Solana Precious Metals Trading</h2>
            
            <div class="controls" style="margin-bottom: 20px;">
                <button class="btn" id="toggleTradingBtn" onclick="toggleTrading()">Start Trading</button>
                <button class="btn" onclick="refreshTradingStatus()">Refresh</button>
                <button class="btn" onclick="showTradingJournal()">Trading Journal</button>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Portfolio Value</h3>
                    <div class="metric-value" id="portfolioValue">$0.00</div>
                    <div class="health-bar">
                        <div class="health-fill" id="portfolioBar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric-card">
                    <h3>Daily P&L</h3>
                    <div class="metric-value" id="dailyPnl" style="color: #888;">$0.00</div>
                </div>
                <div class="metric-card">
                    <h3>Win Rate</h3>
                    <div class="metric-value" id="winRate">0%</div>
                    <div class="health-bar">
                        <div class="health-fill" id="winRateBar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric-card">
                    <h3>Sharpe Ratio</h3>
                    <div class="metric-value" id="sharpeRatio">0.00</div>
                </div>
            </div>
            
            <!-- Market Data -->
            <div class="market-data" style="margin-top: 20px; background: #16213e; padding: 20px; border-radius: 10px;">
                <h3>Precious Metals Market</h3>
                <div id="marketDataGrid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                    <!-- Market data will be populated here -->
                </div>
            </div>
            
            <!-- Portfolio Positions -->
            <div class="portfolio-positions" style="margin-top: 20px; background: #16213e; padding: 20px; border-radius: 10px;">
                <h3>Current Positions</h3>
                <div id="positionsTable" style="margin-top: 15px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 1px solid #2a3f5f;">
                                <th style="padding: 10px; text-align: left;">Asset</th>
                                <th style="padding: 10px; text-align: right;">Quantity</th>
                                <th style="padding: 10px; text-align: right;">Avg Price</th>
                                <th style="padding: 10px; text-align: right;">Current Price</th>
                                <th style="padding: 10px; text-align: right;">P&L</th>
                                <th style="padding: 10px; text-align: right;">Allocation</th>
                                <th style="padding: 10px; text-align: center;">Action</th>
                            </tr>
                        </thead>
                        <tbody id="positionsBody">
                            <!-- Positions will be populated here -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Manual Trading -->
            <div class="manual-trading" style="margin-top: 20px; background: #16213e; padding: 20px; border-radius: 10px;">
                <h3>Manual Trading</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div>
                        <label style="display: block; margin-bottom: 5px;">Asset</label>
                        <select id="tradeAsset" style="width: 100%; padding: 8px; background: #1a1a2e; color: #e0e0e0; border: 1px solid #2a3f5f; border-radius: 5px;">
                            <option value="GOLD">Gold Token</option>
                            <option value="PHYSICAL_GOLD">Physical Gold</option>
                            <option value="SILVER">Silver Token</option>
                            <option value="KNOX">Fort Knox (Yield)</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 5px;">Action</label>
                        <select id="tradeAction" style="width: 100%; padding: 8px; background: #1a1a2e; color: #e0e0e0; border: 1px solid #2a3f5f; border-radius: 5px;">
                            <option value="buy">Buy</option>
                            <option value="sell">Sell</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 5px;">Amount (USD)</label>
                        <input type="number" id="tradeAmount" min="0" step="0.01" placeholder="100.00" style="width: 100%; padding: 8px; background: #1a1a2e; color: #e0e0e0; border: 1px solid #2a3f5f; border-radius: 5px;">
                    </div>
                    <div style="display: flex; align-items: flex-end;">
                        <button class="btn" onclick="executeManualTrade()" style="width: 100%;">Execute Trade</button>
                    </div>
                </div>
            </div>
            
            <!-- Trading Journal -->
            <div class="trading-journal" id="tradingJournal" style="display: none; margin-top: 20px; background: #16213e; padding: 20px; border-radius: 10px;">
                <h3>Recent Trades</h3>
                <div id="journalEntries" style="max-height: 300px; overflow-y: auto; margin-top: 15px;">
                    <!-- Journal entries will be populated here -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let services = {};
        
        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                console.log('Connected to dashboard');
                addLog('Connected to Oracle AGI Dashboard', 'info');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            ws.onclose = () => {
                console.log('Disconnected from dashboard');
                addLog('Disconnected from dashboard', 'warning');
                // Reconnect after 5 seconds
                setTimeout(initWebSocket, 5000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                addLog('WebSocket error', 'error');
            };
        }
        
        // Handle WebSocket messages
        function handleWebSocketMessage(data) {
            if (data.type === 'status' || data.type === 'update') {
                updateMetrics(data.data || data);
                
                if (data.services) {
                    updateServices(data.services);
                }
            }
        }
        
        // Update metrics display
        function updateMetrics(data) {
            if (data.metrics) {
                document.getElementById('cpuUsage').textContent = `${data.metrics.cpu_percent.toFixed(1)}%`;
                document.getElementById('cpuBar').style.width = `${data.metrics.cpu_percent}%`;
                
                document.getElementById('memoryUsage').textContent = `${data.metrics.memory_percent.toFixed(1)}%`;
                document.getElementById('memoryBar').style.width = `${data.metrics.memory_percent}%`;
            }
            
            if (data.services) {
                const total = data.services.total || 0;
                const online = data.services.online || 0;
                
                document.getElementById('activeServices').textContent = `${online}/${total}`;
                document.getElementById('servicesBar').style.width = `${(online/total)*100}%`;
            }
            
            if (data.health_score !== undefined) {
                document.getElementById('systemHealth').textContent = `${data.health_score.toFixed(0)}%`;
                document.getElementById('healthBar').style.width = `${data.health_score}%`;
            }
        }
        
        // Update services display
        function updateServices(servicesData) {
            services = servicesData;
            const grid = document.getElementById('serviceGrid');
            grid.innerHTML = '';
            
            for (const [serviceId, service] of Object.entries(servicesData)) {
                const card = createServiceCard(serviceId, service);
                grid.appendChild(card);
            }
        }
        
        // Create service card element
        function createServiceCard(serviceId, service) {
            const card = document.createElement('div');
            card.className = 'service-card';
            
            const statusClass = `status-${service.status || 'offline'}`;
            
            card.innerHTML = `
                <div>
                    <span class="status-indicator ${statusClass}"></span>
                    <strong>${service.name || serviceId}</strong>
                </div>
                <div style="margin-top: 10px; color: #888;">
                    Port: ${service.port || 'N/A'}
                </div>
                <div style="margin-top: 5px; color: #888;">
                    Health: ${service.health_score ? service.health_score.toFixed(0) : 0}%
                </div>
                <div class="health-bar">
                    <div class="health-fill" style="width: ${service.health_score || 0}%"></div>
                </div>
                <div style="margin-top: 10px;">
                    <button class="btn" style="padding: 5px 10px; font-size: 0.9em;" 
                            onclick="restartService('${serviceId}')">
                        Restart
                    </button>
                    <button class="btn" style="padding: 5px 10px; font-size: 0.9em; margin-left: 5px;" 
                            onclick="optimizeService('${serviceId}')">
                        Optimize
                    </button>
                </div>
            `;
            
            return card;
        }
        
        // Refresh status
        async function refreshStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateMetrics(data);
                
                // Also get services
                const servicesResponse = await fetch('/api/services');
                const servicesData = await servicesResponse.json();
                updateServices(servicesData);
                
                addLog('Status refreshed', 'info');
            } catch (error) {
                console.error('Error refreshing status:', error);
                addLog('Failed to refresh status', 'error');
            }
        }
        
        // Show ecosystem map
        async function showEcosystemMap() {
            const mapDiv = document.getElementById('ecosystemMap');
            const logsDiv = document.getElementById('logsContainer');
            
            mapDiv.style.display = 'block';
            logsDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/ecosystem/map');
                const data = await response.json();
                drawEcosystemMap(data);
                addLog('Ecosystem map loaded', 'info');
            } catch (error) {
                console.error('Error loading ecosystem map:', error);
                addLog('Failed to load ecosystem map', 'error');
            }
        }
        
        // Draw ecosystem map on canvas
        function drawEcosystemMap(data) {
            const canvas = document.getElementById('mapCanvas');
            const ctx = canvas.getContext('2d');
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Position nodes
            const positions = {};
            const clusterPositions = {
                'core': { x: 200, y: 100 },
                'mcp': { x: 500, y: 100 },
                'ai': { x: 800, y: 100 },
                'workflow': { x: 350, y: 300 },
                'storage': { x: 650, y: 300 }
            };
            
            // Position nodes by cluster
            data.nodes.forEach((node, index) => {
                const cluster = node.cluster || 'core';
                const basePos = clusterPositions[cluster] || { x: 400, y: 200 };
                
                const angle = (index * Math.PI * 2) / data.nodes.filter(n => n.cluster === cluster).length;
                const radius = 80;
                
                positions[node.id] = {
                    x: basePos.x + Math.cos(angle) * radius,
                    y: basePos.y + Math.sin(angle) * radius
                };
            });
            
            // Draw edges
            ctx.strokeStyle = '#2a3f5f';
            ctx.lineWidth = 1;
            
            data.edges.forEach(edge => {
                const start = positions[edge.source];
                const end = positions[edge.target];
                
                if (start && end) {
                    ctx.beginPath();
                    ctx.moveTo(start.x, start.y);
                    ctx.lineTo(end.x, end.y);
                    ctx.stroke();
                }
            });
            
            // Draw nodes
            data.nodes.forEach(node => {
                const pos = positions[node.id];
                if (!pos) return;
                
                // Node circle
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 30, 0, Math.PI * 2);
                
                // Color based on status
                if (node.status === 'online') {
                    ctx.fillStyle = '#00ff88';
                } else if (node.status === 'degraded') {
                    ctx.fillStyle = '#ffaa00';
                } else {
                    ctx.fillStyle = '#ff3838';
                }
                
                ctx.fill();
                
                // Node label
                ctx.fillStyle = '#ffffff';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(node.label, pos.x, pos.y + 45);
            });
        }
        
        // Optimize system
        async function optimizeSystem() {
            try {
                const response = await fetch('/api/llm/optimize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_type: 'general' })
                });
                
                const data = await response.json();
                
                if (data.recommendations) {
                    data.recommendations.forEach(rec => {
                        addLog(`Optimization: ${rec.action} - ${rec.reason}`, 'info');
                    });
                }
            } catch (error) {
                console.error('Error optimizing system:', error);
                addLog('Failed to optimize system', 'error');
            }
        }
        
        // View logs
        function viewLogs() {
            const mapDiv = document.getElementById('ecosystemMap');
            const logsDiv = document.getElementById('logsContainer');
            
            mapDiv.style.display = 'none';
            logsDiv.style.display = 'block';
        }
        
        // Add log entry
        function addLog(message, level = 'info') {
            const logEntries = document.getElementById('logEntries');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${level}`;
            
            const timestamp = new Date().toLocaleTimeString();
            entry.textContent = `[${timestamp}] ${message}`;
            
            logEntries.insertBefore(entry, logEntries.firstChild);
            
            // Keep only last 100 entries
            while (logEntries.children.length > 100) {
                logEntries.removeChild(logEntries.lastChild);
            }
        }
        
        // Restart service
        async function restartService(serviceId) {
            try {
                const response = await fetch(`/api/service/${serviceId}/restart`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog(`Service ${serviceId} restarted successfully`, 'info');
                } else {
                    addLog(`Failed to restart ${serviceId}`, 'error');
                }
            } catch (error) {
                console.error('Error restarting service:', error);
                addLog(`Error restarting ${serviceId}`, 'error');
            }
        }
        
        // Optimize service
        async function optimizeService(serviceId) {
            try {
                const response = await fetch(`/api/service/${serviceId}/optimize`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.recommendations) {
                    data.recommendations.forEach(rec => {
                        addLog(`${serviceId}: ${rec}`, 'info');
                    });
                }
            } catch (error) {
                console.error('Error optimizing service:', error);
                addLog(`Error optimizing ${serviceId}`, 'error');
            }
        }
        
        // Security monitoring functions
        async function updateSecurityStatus() {
            try {
                const response = await fetch('/api/security/status');
                const data = await response.json();
                
                if (!data.error) {
                    // Update security score
                    document.getElementById('securityScore').textContent = data.security_score ? 
                        data.security_score.toFixed(0) + '%' : '100%';
                    document.getElementById('securityBar').style.width = (data.security_score || 100) + '%';
                    
                    // Update threat counts
                    document.getElementById('activeThreats').textContent = data.active_threats || '0';
                    document.getElementById('criticalAlerts').textContent = 
                        data.threat_summary ? data.threat_summary.critical || '0' : '0';
                    
                    // Update threat summary
                    if (data.threat_summary) {
                        const summaryHtml = Object.entries(data.threat_summary)
                            .map(([severity, count]) => `
                                <span style="margin-right: 15px; padding: 5px 10px; 
                                            background: #2a2a3e; border-radius: 5px;">
                                    <strong>${severity.toUpperCase()}</strong>: ${count}
                                </span>
                            `).join('');
                        document.getElementById('threatSummary').innerHTML = summaryHtml;
                    }
                    
                    // Update recent threats
                    if (data.recent_threats && data.recent_threats.length > 0) {
                        const threatsHtml = data.recent_threats.map(threat => `
                            <div style="padding: 10px; margin: 5px 0; background: #1a1a2e; 
                                        border-radius: 5px; border-left: 3px solid #ff3838;">
                                <strong>${threat.type ? threat.type.toUpperCase() : 'UNKNOWN'}</strong> - 
                                <span style="color: ${threat.severity === 'critical' ? '#ff3838' : 
                                                      threat.severity === 'high' ? '#ff6b6b' : 
                                                      '#ffaa00'};">
                                    ${threat.severity || 'unknown'}
                                </span>
                                <br>
                                <small>${threat.description || 'No description'}</small>
                            </div>
                        `).join('');
                        document.getElementById('recentThreats').innerHTML = threatsHtml;
                    } else {
                        document.getElementById('recentThreats').innerHTML = 
                            '<p style="color: #888;">No recent threats detected</p>';
                    }
                } else {
                    // OpenCTI not available
                    document.getElementById('securityScore').textContent = 'N/A';
                    document.getElementById('activeThreats').textContent = 'N/A';
                    document.getElementById('criticalAlerts').textContent = 'N/A';
                    document.getElementById('threatSummary').innerHTML = 
                        '<p style="color: #888;">OpenCTI integration not available</p>';
                    document.getElementById('recentThreats').innerHTML = 
                        '<p style="color: #888;">OpenCTI integration not available</p>';
                }
            } catch (error) {
                console.error('Failed to update security status:', error);
            }
        }
        
        // Check IOC function
        async function checkIOC(value) {
            try {
                const response = await fetch('/api/security/check_ioc', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ value: value })
                });
                
                const data = await response.json();
                
                if (data.is_threat) {
                    addLog(`THREAT DETECTED: ${value} - ${data.indicator.threat_type}`, 'error');
                } else {
                    addLog(`IOC Check: ${value} - CLEAR`, 'info');
                }
                
                return data;
            } catch (error) {
                console.error('IOC check failed:', error);
                return { is_threat: false, error: error.message };
            }
        }
        
        // Trading functions
        let tradingActive = false;
        
        async function updateTradingStatus() {
            try {
                const response = await fetch('/api/trading/status');
                const data = await response.json();
                
                if (!data.error) {
                    tradingActive = data.active;
                    document.getElementById('toggleTradingBtn').textContent = tradingActive ? 'Stop Trading' : 'Start Trading';
                    
                    if (data.data) {
                        // Update portfolio metrics
                        const portfolio = data.data.portfolio || {};
                        document.getElementById('portfolioValue').textContent = `$${(portfolio.total_value || 0).toFixed(2)}`;
                        document.getElementById('dailyPnl').textContent = `$${(portfolio.daily_pnl || 0).toFixed(2)}`;
                        document.getElementById('dailyPnl').style.color = portfolio.daily_pnl >= 0 ? '#00ff88' : '#ff3838';
                        
                        // Update performance metrics
                        const performance = data.data.performance || {};
                        document.getElementById('winRate').textContent = `${(performance.win_rate || 0).toFixed(1)}%`;
                        document.getElementById('winRateBar').style.width = `${performance.win_rate || 0}%`;
                        document.getElementById('sharpeRatio').textContent = (performance.sharpe_ratio || 0).toFixed(2);
                        
                        // Update market data
                        updateMarketData(data.data.market_data || {});
                        
                        // Update positions
                        updatePositions(portfolio.positions || []);
                    }
                }
            } catch (error) {
                console.error('Failed to update trading status:', error);
            }
        }
        
        function updateMarketData(marketData) {
            const grid = document.getElementById('marketDataGrid');
            grid.innerHTML = '';
            
            for (const [symbol, data] of Object.entries(marketData)) {
                const card = document.createElement('div');
                card.style.cssText = 'background: #1a1a2e; padding: 15px; border-radius: 8px; border: 1px solid #2a3f5f;';
                
                const changeColor = data.change_24h >= 0 ? '#00ff88' : '#ff3838';
                
                card.innerHTML = `
                    <div style="font-weight: bold; margin-bottom: 10px;">${symbol}</div>
                    <div style="font-size: 1.5em; color: #00d4ff;">$${(data.price || 0).toFixed(4)}</div>
                    <div style="color: ${changeColor}; margin-top: 5px;">
                        ${data.change_24h >= 0 ? '+' : ''}${(data.change_24h || 0).toFixed(2)}%
                    </div>
                    <div style="color: #888; font-size: 0.9em; margin-top: 5px;">
                        Vol: $${((data.volume_24h || 0) / 1000000).toFixed(2)}M
                    </div>
                `;
                
                grid.appendChild(card);
            }
        }
        
        function updatePositions(positions) {
            const tbody = document.getElementById('positionsBody');
            tbody.innerHTML = '';
            
            if (positions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px; color: #888;">No positions</td></tr>';
                return;
            }
            
            positions.forEach(pos => {
                const row = document.createElement('tr');
                row.style.borderBottom = '1px solid #1a1a2e';
                
                const pnlColor = pos.pnl >= 0 ? '#00ff88' : '#ff3838';
                
                row.innerHTML = `
                    <td style="padding: 10px;">${pos.symbol}</td>
                    <td style="padding: 10px; text-align: right;">${pos.quantity.toFixed(4)}</td>
                    <td style="padding: 10px; text-align: right;">$${pos.average_price.toFixed(4)}</td>
                    <td style="padding: 10px; text-align: right;">$${pos.current_price.toFixed(4)}</td>
                    <td style="padding: 10px; text-align: right; color: ${pnlColor};">
                        $${pos.pnl.toFixed(2)} (${pos.pnl_percent.toFixed(1)}%)
                    </td>
                    <td style="padding: 10px; text-align: right;">${pos.allocation_percent.toFixed(1)}%</td>
                    <td style="padding: 10px; text-align: center;">
                        <button class="btn" style="padding: 5px 10px; font-size: 0.9em;" 
                                onclick="quickSell('${pos.asset}', ${pos.quantity})">
                            Sell
                        </button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        }
        
        async function toggleTrading() {
            try {
                const endpoint = tradingActive ? '/api/trading/stop' : '/api/trading/start';
                const response = await fetch(endpoint, { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    addLog(`Trading ${tradingActive ? 'stopped' : 'started'}`, 'info');
                    await updateTradingStatus();
                } else {
                    addLog(`Failed to ${tradingActive ? 'stop' : 'start'} trading: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Toggle trading error:', error);
                addLog('Failed to toggle trading', 'error');
            }
        }
        
        async function refreshTradingStatus() {
            await updateTradingStatus();
            addLog('Trading status refreshed', 'info');
        }
        
        function showTradingJournal() {
            const journal = document.getElementById('tradingJournal');
            journal.style.display = journal.style.display === 'none' ? 'block' : 'none';
        }
        
        async function executeManualTrade() {
            const asset = document.getElementById('tradeAsset').value;
            const action = document.getElementById('tradeAction').value;
            const amount = parseFloat(document.getElementById('tradeAmount').value);
            
            if (!amount || amount <= 0) {
                addLog('Invalid trade amount', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/trading/manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ asset, action, amount })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog(`Manual trade executed: ${action} ${asset} for $${amount}`, 'info');
                    await updateTradingStatus();
                    
                    // Clear form
                    document.getElementById('tradeAmount').value = '';
                } else {
                    addLog(`Trade failed: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Manual trade error:', error);
                addLog('Failed to execute trade', 'error');
            }
        }
        
        async function quickSell(asset, quantity) {
            if (!confirm(`Sell ${quantity.toFixed(4)} ${asset}?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/trading/manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        asset, 
                        action: 'sell', 
                        amount: quantity * 1000 // Approximate USD value
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog(`Sold ${quantity.toFixed(4)} ${asset}`, 'info');
                    await updateTradingStatus();
                } else {
                    addLog(`Sell failed: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Quick sell error:', error);
                addLog('Failed to sell position', 'error');
            }
        }
        
        // Initialize on load
        window.onload = () => {
            initWebSocket();
            refreshStatus();
            updateSecurityStatus();
            updateTradingStatus();
            
            // Update security status every 30 seconds
            setInterval(updateSecurityStatus, 30000);
            
            // Update trading status every 10 seconds
            setInterval(updateTradingStatus, 10000);
        };
    </script>
    
    {self.wallet_integration_html}
</body>
</html>'''
        
        return web.Response(text=html_content, content_type='text/html')
    
    async def start_background_tasks(self, app):
        """Start background tasks"""
        app['metrics_collector'] = asyncio.create_task(self.continuous_metrics_collection())
        
    async def cleanup_background_tasks(self, app):
        """Cleanup background tasks"""
        app['metrics_collector'].cancel()
        await app['metrics_collector']
        
    async def continuous_metrics_collection(self):
        """Continuously collect metrics"""
        while True:
            try:
                await self.collect_system_metrics()
                
                # Check all services
                for service_id, service_config in self.service_registry.items():
                    self.service_status[service_id] = await self.check_service_health(
                        service_id, service_config
                    )
                
                # Self-healing checks
                await self.perform_self_healing_checks()
                
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(30)
    
    async def perform_self_healing_checks(self):
        """Perform self-healing checks and actions"""
        # Check critical services
        for service_id, service_config in self.service_registry.items():
            if service_config.get("critical") and service_id in self.service_status:
                status = self.service_status[service_id]
                
                if status.status == "offline":
                    logger.warning(f"Critical service {status.name} is offline, attempting restart...")
                    
                    # Import ecosystem manager for restart
                    from ecosystem_manager import EcosystemManager
                    manager = EcosystemManager()
                    
                    await manager.restart_service(service_id)
                    
        # Check system resources
        latest_metrics = self.system_metrics[-1] if self.system_metrics else None
        if latest_metrics:
            if latest_metrics.memory_percent > self.hardware_optimization["memory_threshold"]:
                logger.warning("Memory usage critical, initiating optimization...")
                await self.optimize_memory_usage()
    
    async def _init_opencti(self):
        """Initialize OpenCTI connection"""
        try:
            connected = await self.opencti.initialize()
            if connected:
                logger.info("OpenCTI security integration active")
            else:
                logger.warning("OpenCTI connection failed")
        except Exception as e:
            logger.error(f"OpenCTI initialization error: {e}")
    
    async def get_security_status(self, request):
        """Get security status from OpenCTI"""
        if not self.opencti:
            return web.json_response({
                "error": "OpenCTI not available",
                "security_score": 100,
                "active_threats": 0,
                "threat_summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}
            })
        
        try:
            security_data = await self.opencti.get_dashboard_data()
            return web.json_response(security_data)
        except Exception as e:
            logger.error(f"Security status error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def check_ioc(self, request):
        """Check if a value is an Indicator of Compromise"""
        if not self.opencti:
            return web.json_response({"error": "OpenCTI not available"}, status=503)
        
        data = await request.json()
        value = data.get("value")
        
        if not value:
            return web.json_response({"error": "Value required"}, status=400)
        
        try:
            indicator = await self.opencti.opencti.check_ioc(value)
            return web.json_response({
                "is_threat": indicator is not None,
                "indicator": asdict(indicator) if indicator else None
            })
        except Exception as e:
            logger.error(f"IOC check error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_service_security(self, request):
        """Get security analysis for a specific service"""
        if not self.opencti:
            return web.json_response({"error": "OpenCTI not available"}, status=503)
        
        service_id = request.match_info['service_id']
        
        if service_id not in self.service_registry:
            return web.json_response({"error": "Service not found"}, status=404)
        
        try:
            service_data = self.service_registry[service_id]
            security_analysis = await self.opencti.check_service_security(service_id, service_data)
            return web.json_response(security_analysis)
        except Exception as e:
            logger.error(f"Service security check error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def optimize_memory_usage(self):
        """Optimize memory usage across services"""
        # Get memory usage per service
        memory_usage = []
        
        for service_id, status in self.service_status.items():
            if status.status == "online" and "memory_usage" in status.metrics:
                memory_usage.append((service_id, status.metrics["memory_usage"]))
        
        # Sort by memory usage
        memory_usage.sort(key=lambda x: x[1], reverse=True)
        
        # Log top memory users
        for service_id, mem in memory_usage[:5]:
            logger.info(f"{service_id}: {mem}MB")
    
    async def _init_solana_trading(self):
        """Initialize Solana trading system"""
        try:
            # Start autonomous trading automatically
            await self.solana_trader.start_trading()
            logger.info("Solana precious metals autonomous trading started")
        except Exception as e:
            logger.error(f"Solana trading initialization error: {e}")
    
    async def get_trading_status(self, request):
        """Get current trading system status"""
        if not self.solana_trader:
            return web.json_response({"error": "Trading system not available"}, status=503)
        
        try:
            status = self.solana_trader.get_trading_status()
            return web.json_response(status)
        except Exception as e:
            logger.error(f"Trading status error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def start_trading(self, request):
        """Start autonomous trading"""
        if not self.solana_trader:
            return web.json_response({"error": "Trading system not available"}, status=503)
        
        try:
            await self.solana_trader.start_trading()
            return web.json_response({"success": True, "message": "Trading started"})
        except Exception as e:
            logger.error(f"Start trading error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def stop_trading(self, request):
        """Stop autonomous trading"""
        if not self.solana_trader:
            return web.json_response({"error": "Trading system not available"}, status=503)
        
        try:
            await self.solana_trader.stop_trading()
            return web.json_response({"success": True, "message": "Trading stopped"})
        except Exception as e:
            logger.error(f"Stop trading error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def manual_trade(self, request):
        """Execute manual trade"""
        if not self.solana_trader:
            return web.json_response({"error": "Trading system not available"}, status=503)
        
        try:
            data = await request.json()
            asset = data.get("asset")
            action = data.get("action")
            amount = float(data.get("amount", 0))
            
            if not all([asset, action, amount > 0]):
                return web.json_response({"error": "Invalid trade parameters"}, status=400)
            
            result = await self.solana_trader.manual_trade(asset, action, amount)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Manual trade error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_portfolio(self, request):
        """Get current portfolio details"""
        if not self.solana_trader:
            return web.json_response({"error": "Trading system not available"}, status=503)
        
        try:
            status = self.solana_trader.get_trading_status()
            return web.json_response(status.get("data", {}).get("portfolio", {}))
        except Exception as e:
            logger.error(f"Get portfolio error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_wallet_connect(self, request):
        """Handle wallet connection"""
        if not self.wallet_api:
            return web.json_response({"error": "Wallet integration not available"}, status=503)
        
        try:
            result = await self.wallet_api.handle_wallet_connect(request)
            
            # If we have a trading system and wallet, update it
            if self.solana_trader and result.get("success"):
                wallet_info = result.get("wallet", {})
                if wallet_info.get("address"):
                    self.solana_trader.trader.wallet_address = wallet_info["address"]
                    logger.info(f"Trading system updated with wallet: {wallet_info['address']}")
            
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Wallet connect error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_wallet_disconnect(self, request):
        """Handle wallet disconnection"""
        if not self.wallet_api:
            return web.json_response({"error": "Wallet integration not available"}, status=503)
        
        try:
            result = await self.wallet_api.handle_wallet_disconnect(request)
            
            # Clear wallet from trading system
            if self.solana_trader:
                self.solana_trader.trader.wallet_address = None
            
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Wallet disconnect error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    def run(self, host='0.0.0.0', port=3010):
        """Run the dashboard server"""
        self.app.on_startup.append(self.start_background_tasks)
        self.app.on_cleanup.append(self.cleanup_background_tasks)
        
        logger.info(f"Starting Oracle AGI Ultimate Dashboard V2 on http://{host}:{port}")
        web.run_app(self.app, host=host, port=port)

def main():
    dashboard = OracleAGIUnifiedDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()