#!/usr/bin/env python3
"""
CLAUDIA AGI SYSTEM INTEGRATION BRIDGE
====================================
Integration bridge between Claudia AGI system and ULTIMATE AGI SYSTEM V3
Handles system communication, task routing, and orchestration coordination
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiohttp
import time
import psutil
import subprocess
import signal
import os
from dataclasses import dataclass, asdict

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from core.CONTEXT7_INTEGRATION import Context7Integration
    from core.ecosystem_core import EcosystemCore
except ImportError as e:
    print(f"⚠️ Warning: Could not import ecosystem modules: {e}")
    print("🔄 Running in standalone mode...")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claudia_integration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ClaudiaIntegration')

@dataclass
class ClaudiaSystemStatus:
    """Status information for Claudia system components"""
    orchestrator_running: bool = False
    deepseek_agent_running: bool = False
    mcp_specialist_running: bool = False
    database_connected: bool = False
    ollama_available: bool = False

    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return all([
            self.orchestrator_running,
            self.deepseek_agent_running,
            self.mcp_specialist_running,
            self.database_connected
        ])

@dataclass
class TaskRequest:
    """Task request structure for Claudia system"""
    task_id: str
    task_type: str
    priority: int
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['created_at'] = self.created_at.isoformat()
        return result

class ClaudiaIntegrationBridge:
    """
    Integration bridge between Claudia AGI system and ULTIMATE AGI SYSTEM V3
    """

    def __init__(self):
        self.logger = logging.getLogger('ClaudiaIntegration')
        self.status = ClaudiaSystemStatus()
        self.claudia_processes = {}
        self.api_endpoints = {
            'orchestrator': 'http://localhost:8888',
            'deepseek_agent': 'http://localhost:8893',
            'mcp_specialist': 'http://localhost:8894'
        }
        self.running = False
        self.context7_integration = None
        self.ecosystem_core = None

        # Initialize ecosystem connections if available
        try:
            self.context7_integration = Context7Integration()
            self.ecosystem_core = EcosystemCore()
            self.logger.info("✅ Ecosystem integrations initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ Ecosystem integrations not available: {e}")

    async def initialize_system(self) -> bool:
        """Initialize the Claudia AGI system"""
        try:
            self.logger.info("🚀 INITIALIZING CLAUDIA AGI SYSTEM INTEGRATION")

            # Check prerequisites
            if not await self.check_prerequisites():
                self.logger.error("❌ Prerequisites not met")
                return False

            # Start Claudia system components
            if not await self.start_claudia_system():
                self.logger.error("❌ Failed to start Claudia system")
                return False

            # Verify system health
            if not await self.verify_system_health():
                self.logger.error("❌ System health check failed")
                return False

            # Set up integration bridges
            await self.setup_integration_bridges()

            self.running = True
            self.logger.info("✅ CLAUDIA AGI SYSTEM INTEGRATION COMPLETE")
            return True

        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            return False

    async def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.logger.info("🔍 Checking prerequisites...")

        prerequisites = {
            'python_version': sys.version_info >= (3, 8),
            'claudia_scripts': (Path(__file__).parent / "claudia" / "scripts").exists(),
            'postgres_available': await self.check_postgres(),
            'ollama_available': await self.check_ollama(),
            'disk_space': psutil.disk_usage('/').free > 1024**3  # 1GB free space
        }

        all_met = True
        for prereq, status in prerequisites.items():
            if status:
                self.logger.info(f"✅ {prereq}: OK")
            else:
                self.logger.error(f"❌ {prereq}: FAILED")
                all_met = False

        return all_met

    async def check_postgres(self) -> bool:
        """Check if PostgreSQL is available"""
        try:
            # Try to connect to PostgreSQL
            proc = subprocess.run(
                ['pg_isready', '-h', 'localhost', '-p', '5432'],
                capture_output=True,
                timeout=5
            )
            return proc.returncode == 0
        except Exception:
            # If pg_isready not available, try basic connection
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host='localhost',
                    port=5432,
                    database='postgres',
                    user='postgres',
                    password=os.environ.get('REDIS_PASSWORD', ''),
                    connect_timeout=5
                )
                conn.close()
                return True
            except Exception:
                return False

    async def check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            proc = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                timeout=5
            )
            return proc.returncode == 0
        except Exception:
            return False

    async def start_claudia_system(self) -> bool:
        """Start the Claudia AGI system components"""
        self.logger.info("🚀 Starting Claudia AGI system components...")

        try:
            # Start the launcher script
            claudia_launcher = Path(__file__).parent / "claudia" / "scripts" / "launch_claudia_system.py"

            if not claudia_launcher.exists():
                self.logger.error(f"❌ Claudia launcher not found: {claudia_launcher}")
                return False

            # Start Claudia system in background
            proc = subprocess.Popen([
                sys.executable, str(claudia_launcher)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.claudia_processes['launcher'] = proc

            # Give system time to start
            await asyncio.sleep(10)

            # Check if processes are running
            return await self.verify_claudia_processes()

        except Exception as e:
            self.logger.error(f"❌ Failed to start Claudia system: {e}")
            return False

    async def verify_claudia_processes(self) -> bool:
        """Verify that Claudia processes are running"""
        self.logger.info("🔍 Verifying Claudia system processes...")

        try:
            # Check if ports are in use (indicating services are running)
            for service, endpoint in self.api_endpoints.items():
                port = int(endpoint.split(':')[2])
                if self.is_port_in_use(port):
                    self.logger.info(f"✅ {service} is running on port {port}")
                else:
                    self.logger.warning(f"⚠️ {service} not detected on port {port}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Process verification failed: {e}")
            return False

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.laddr.port == port:
                    return True
            return False
        except Exception:
            return False

    async def verify_system_health(self) -> bool:
        """Verify system health through API calls"""
        self.logger.info("🏥 Performing system health check...")

        try:
            async with aiohttp.ClientSession() as session:
                for service, endpoint in self.api_endpoints.items():
                    try:
                        async with session.get(f"{endpoint}/health", timeout=5) as response:
                            if response.status == 200:
                                self.logger.info(f"✅ {service} health check passed")
                                if service == 'orchestrator':
                                    self.status.orchestrator_running = True
                                elif service == 'deepseek_agent':
                                    self.status.deepseek_agent_running = True
                                elif service == 'mcp_specialist':
                                    self.status.mcp_specialist_running = True
                            else:
                                self.logger.warning(f"⚠️ {service} health check failed: {response.status}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ {service} not responding: {e}")

            return self.status.is_healthy()

        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return False

    async def setup_integration_bridges(self):
        """Set up integration bridges with existing ecosystem"""
        self.logger.info("🌉 Setting up integration bridges...")

        try:
            # Register Claudia as an available service in ecosystem
            if self.ecosystem_core:
                await self.ecosystem_core.register_service(
                    'claudia_orchestrator',
                    self.api_endpoints['orchestrator'],
                    'Claudia AGI System Orchestrator'
                )

            # Set up task routing
            await self.setup_task_routing()

            # Set up monitoring
            await self.setup_monitoring()

            self.logger.info("✅ Integration bridges established")

        except Exception as e:
            self.logger.error(f"❌ Integration bridge setup failed: {e}")

    async def setup_task_routing(self):
        """Set up intelligent task routing"""
        self.logger.info("🔄 Setting up task routing...")

        # Define task routing rules
        self.task_routing_rules = {
            'code_analysis': 'deepseek_agent',
            'reasoning': 'deepseek_agent',
            'mcp_operations': 'mcp_specialist',
            'system_orchestration': 'orchestrator',
            'agent_missions': 'orchestrator'
        }

        self.logger.info("✅ Task routing configured")

    async def setup_monitoring(self):
        """Set up system monitoring"""
        self.logger.info("📊 Setting up monitoring...")

        # Start monitoring task
        asyncio.create_task(self.monitor_system_health())

        self.logger.info("✅ Monitoring configured")

    async def monitor_system_health(self):
        """Monitor system health continuously"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self.verify_system_health()

                # Log status
                if self.status.is_healthy():
                    self.logger.debug("💚 System health: GOOD")
                else:
                    self.logger.warning("💛 System health: DEGRADED")

            except Exception as e:
                self.logger.error(f"❌ Health monitoring error: {e}")

    async def submit_task(self, task_request: TaskRequest) -> str:
        """Submit a task to the Claudia system"""
        try:
            # Determine target service based on task type
            target_service = self.task_routing_rules.get(task_request.task_type, 'orchestrator')
            endpoint = self.api_endpoints[target_service]

            # Submit task
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/submit_task",
                    json=task_request.to_dict(),
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"✅ Task submitted successfully: {task_request.task_id}")
                        return result.get('task_id', task_request.task_id)
                    else:
                        self.logger.error(f"❌ Task submission failed: {response.status}")
                        return None

        except Exception as e:
            self.logger.error(f"❌ Task submission error: {e}")
            return None

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a submitted task"""
        try:
            # Check orchestrator for task status
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_endpoints['orchestrator']}/task_status/{task_id}",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {'status': 'unknown', 'error': f'HTTP {response.status}'}

        except Exception as e:
            self.logger.error(f"❌ Task status check error: {e}")
            return {'status': 'error', 'error': str(e)}

    async def shutdown_system(self):
        """Shutdown the Claudia system gracefully"""
        self.logger.info("🛑 Shutting down Claudia AGI system...")

        self.running = False

        # Terminate processes
        for proc_name, proc in self.claudia_processes.items():
            try:
                proc.terminate()
                await asyncio.sleep(2)
                if proc.poll() is None:
                    proc.kill()
                self.logger.info(f"✅ {proc_name} process terminated")
            except Exception as e:
                self.logger.error(f"❌ Error terminating {proc_name}: {e}")

        self.logger.info("✅ Claudia AGI system shutdown complete")

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            metrics = {
                'status': asdict(self.status),
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0,
                'processes': len(self.claudia_processes),
                'memory_usage': psutil.virtual_memory()._asdict(),
                'cpu_usage': psutil.cpu_percent(interval=1)
            }

            # Get metrics from orchestrator if available
            if self.status.orchestrator_running:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{self.api_endpoints['orchestrator']}/system_metrics",
                            timeout=5
                        ) as response:
                            if response.status == 200:
                                claudia_metrics = await response.json()
                                metrics['claudia_metrics'] = claudia_metrics
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not fetch Claudia metrics: {e}")

            return metrics

        except Exception as e:
            self.logger.error(f"❌ Error getting system metrics: {e}")
            return {'error': str(e)}

async def main():
    """Main function for testing the integration bridge"""
    bridge = ClaudiaIntegrationBridge()

    try:
        # Initialize system
        if await bridge.initialize_system():
            print("✅ Claudia AGI system initialized successfully!")

            # Test task submission
            test_task = TaskRequest(
                task_id="test_001",
                task_type="code_analysis",
                priority=1,
                payload={"code": "print('Hello, Claudia AGI!')"},
                metadata={"source": "integration_test"},
                created_at=datetime.now()
            )

            task_id = await bridge.submit_task(test_task)
            if task_id:
                print(f"✅ Test task submitted: {task_id}")

                # Check task status
                await asyncio.sleep(2)
                status = await bridge.get_task_status(task_id)
                print(f"📊 Task status: {status}")

            # Get system metrics
            metrics = await bridge.get_system_metrics()
            print(f"📈 System metrics: {json.dumps(metrics, indent=2)}")

            # Keep running for demonstration
            print("🔄 System running... Press Ctrl+C to stop")
            await asyncio.sleep(10)

        else:
            print("❌ Failed to initialize Claudia AGI system")

    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await bridge.shutdown_system()

if __name__ == "__main__":
    print("🧠 CLAUDIA AGI SYSTEM INTEGRATION BRIDGE")
    print("=" * 50)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
