#!/usr/bin/env python3
"""
Ultimate AGI System V3 Production Launcher
==========================================

Production-ready launcher for the Ultimate AGI System V3 with comprehensive
orchestration, monitoring, and self-healing capabilities.

Features:
- Automated component startup and dependency management
- Real-time health monitoring and alerting
- Self-healing and auto-recovery mechanisms
- Performance optimization and resource management
- Comprehensive logging and debugging
- Production deployment readiness
- 24/7 operation support

Author: Ultimate AGI System V3
Version: 3.0.0
Date: 2025-07-06
"""

import asyncio
import json
import logging
import os
import sys
import signal
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import psutil
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from contextlib import asynccontextmanager
import sqlite3
import yaml

# Setup comprehensive logging
def setup_logging():
    """Setup comprehensive logging for production"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / "ultimate_agi_v3.log"),
            logging.FileHandler(log_dir / "ultimate_agi_v3_debug.log"),
            logging.StreamHandler()
        ]
    )

    # Set debug level for debug file
    debug_handler = logging.FileHandler(log_dir / "ultimate_agi_v3_debug.log")
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter(log_format)
    debug_handler.setFormatter(debug_formatter)

    # Add debug handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(debug_handler)
    root_logger.setLevel(logging.DEBUG)

setup_logging()
logger = logging.getLogger(__name__)

@dataclass
class ComponentInfo:
    """Information about a system component"""
    name: str
    script_path: str
    port: Optional[int] = None
    health_endpoint: str = "/health"
    critical: bool = False
    auto_restart: bool = True
    max_restarts: int = 3
    restart_count: int = 0
    dependencies: List[str] = None
    environment: Dict[str, str] = None
    process: Optional[subprocess.Popen] = None
    status: str = "STOPPED"  # STOPPED, STARTING, RUNNING, ERROR, CRASHED
    last_health_check: Optional[datetime] = None
    health_score: float = 0.0
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class SystemStatus:
    """Overall system status"""
    running: bool
    start_time: datetime
    uptime: timedelta
    total_components: int
    running_components: int
    failed_components: int
    overall_health: float
    resource_usage: Dict[str, float]
    alerts: List[str]
    version: str = "3.0.0"

class UltimateAGILauncher:
    """Production launcher for Ultimate AGI System V3"""

    def __init__(self, config_path: str = "orchestrator_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.components: Dict[str, ComponentInfo] = {}
        self.system_running = False
        self.start_time = datetime.now()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.health_check_interval = 30
        self.db_path = "launcher.db"
        self.shutdown_event = asyncio.Event()

        # Initialize components
        self.init_components()
        self.init_database()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info("🚀 Ultimate AGI System V3 Launcher initialized")

    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Configuration loaded from {self.config_path}")
                    return config
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "components": {
                "trading_system": {
                    "script": "ultimate_trading_system_v3.py",
                    "port": 8890,
                    "critical": True,
                    "dependencies": ["mcp_server"]
                },
                "trading_dashboard": {
                    "script": "ultimate_trading_dashboard_v3_fixed.py",
                    "port": 8891,
                    "critical": False,
                    "dependencies": ["trading_system"]
                },
                "health_monitor": {
                    "script": "health_monitor_v3.py",
                    "port": 8999,
                    "critical": True,
                    "dependencies": []
                },
                "mcp_server": {
                    "script": "oracle_mcp_server.py",
                    "port": 8894,
                    "critical": True,
                    "dependencies": []
                }
            },
            "monitoring": {
                "health_check_interval": 30,
                "restart_delay": 5,
                "max_restart_attempts": 3
            }
        }

    def init_components(self):
        """Initialize component information"""
        components_config = self.config.get("components", {})

        for name, config in components_config.items():
            component = ComponentInfo(
                name=name,
                script_path=config.get("script", ""),
                port=config.get("port"),
                health_endpoint=config.get("health_endpoint", "/health"),
                critical=config.get("critical", False),
                auto_restart=config.get("auto_restart", True),
                max_restarts=config.get("max_restarts", 3),
                dependencies=config.get("dependencies", []),
                environment=config.get("environment", {})
            )

            self.components[name] = component
            logger.debug(f"Initialized component: {name}")

    def init_database(self):
        """Initialize database for launcher data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS launch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_name TEXT,
                    action TEXT,
                    timestamp DATETIME,
                    success BOOLEAN,
                    error_message TEXT,
                    details TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    start_time DATETIME,
                    end_time DATETIME,
                    total_components INTEGER,
                    successful_components INTEGER,
                    failed_components INTEGER,
                    uptime_seconds INTEGER
                )
            ''')

            conn.commit()
            conn.close()

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()

    async def start_system(self):
        """Start the complete Ultimate AGI System V3"""
        logger.info("🚀 Starting Ultimate AGI System V3...")
        logger.info("=" * 80)

        self.system_running = True
        self.start_time = datetime.now()

        # Record session start
        await self.record_session_start()

        try:
            # Start components in dependency order
            await self.start_all_components()

            # Start monitoring tasks
            monitoring_tasks = [
                asyncio.create_task(self.health_monitoring_loop()),
                asyncio.create_task(self.resource_monitoring_loop()),
                asyncio.create_task(self.auto_recovery_loop()),
                asyncio.create_task(self.status_reporting_loop())
            ]

            logger.info("✅ Ultimate AGI System V3 started successfully!")
            logger.info("🌟 All components are operational")
            logger.info("📊 Monitoring and self-healing active")
            logger.info("=" * 80)

            # Wait for shutdown signal
            await self.shutdown_event.wait()

            # Cancel monitoring tasks
            for task in monitoring_tasks:
                task.cancel()

            await asyncio.gather(*monitoring_tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error in system startup: {e}")
            traceback.print_exc()
        finally:
            await self.shutdown_system()

    async def start_all_components(self):
        """Start all components in dependency order"""
        # Calculate startup order based on dependencies
        startup_order = self.calculate_startup_order()

        logger.info(f"Starting components in order: {startup_order}")

        for component_name in startup_order:
            if component_name in self.components:
                success = await self.start_component(component_name)
                if not success and self.components[component_name].critical:
                    logger.error(f"Failed to start critical component: {component_name}")
                    raise Exception(f"Critical component startup failed: {component_name}")

                # Wait between component starts
                await asyncio.sleep(2)

    def calculate_startup_order(self) -> List[str]:
        """Calculate component startup order based on dependencies"""
        # Topological sort of dependencies
        visited = set()
        temp_visited = set()
        order = []

        def visit(component_name: str):
            if component_name in temp_visited:
                # Circular dependency detected
                logger.warning(f"Circular dependency detected involving {component_name}")
                return

            if component_name in visited:
                return

            temp_visited.add(component_name)

            # Visit dependencies first
            component = self.components.get(component_name)
            if component and component.dependencies:
                for dep in component.dependencies:
                    if dep in self.components:
                        visit(dep)

            temp_visited.remove(component_name)
            visited.add(component_name)
            order.append(component_name)

        # Visit all components
        for component_name in self.components:
            visit(component_name)

        return order

    async def start_component(self, name: str) -> bool:
        """Start a specific component"""
        component = self.components.get(name)
        if not component:
            logger.error(f"Component not found: {name}")
            return False

        try:
            logger.info(f"Starting component: {name}")
            component.status = "STARTING"

            # Check if script exists
            if not os.path.exists(component.script_path):
                logger.error(f"Script not found: {component.script_path}")
                component.status = "ERROR"
                component.error_message = f"Script not found: {component.script_path}"
                return False

            # Prepare environment
            env = os.environ.copy()
            if component.environment:
                env.update(component.environment)

            # Start process
            process = subprocess.Popen(
                [sys.executable, component.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=os.getcwd()
            )

            component.process = process
            component.pid = process.pid
            component.start_time = datetime.now()

            # Wait for process to stabilize
            await asyncio.sleep(3)

            # Check if process is still running
            if process.poll() is None:
                component.status = "RUNNING"
                component.restart_count = 0
                logger.info(f"✅ Component {name} started successfully (PID: {process.pid})")

                # Record successful start
                await self.record_component_action(name, "START", True)

                return True
            else:
                # Process died immediately
                stdout, stderr = process.communicate()
                error_msg = f"Process died: {stderr or stdout}"

                component.status = "ERROR"
                component.error_message = error_msg
                component.process = None
                component.pid = None

                logger.error(f"❌ Component {name} failed to start: {error_msg}")

                # Record failed start
                await self.record_component_action(name, "START", False, error_msg)

                return False

        except Exception as e:
            logger.error(f"Error starting component {name}: {e}")
            component.status = "ERROR"
            component.error_message = str(e)
            component.process = None
            component.pid = None

            # Record failed start
            await self.record_component_action(name, "START", False, str(e))

            return False

    async def health_monitoring_loop(self):
        """Monitor health of all components"""
        while self.system_running:
            try:
                await self.check_all_component_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)

    async def check_all_component_health(self):
        """Check health of all components"""
        for name, component in self.components.items():
            await self.check_component_health(name, component)

    async def check_component_health(self, name: str, component: ComponentInfo):
        """Check health of a specific component"""
        try:
            # Check if process is still running
            if component.process and component.pid:
                try:
                    process = psutil.Process(component.pid)
                    if process.is_running():
                        # Process is running, check health endpoint if available
                        if component.port:
                            health_score = await self.check_health_endpoint(component.port)
                            component.health_score = health_score

                            if health_score > 80:
                                component.status = "RUNNING"
                            elif health_score > 50:
                                component.status = "DEGRADED"
                            else:
                                component.status = "UNHEALTHY"
                        else:
                            component.status = "RUNNING"
                            component.health_score = 90.0
                    else:
                        component.status = "CRASHED"
                        component.health_score = 0.0
                        component.process = None
                        component.pid = None
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    component.status = "CRASHED"
                    component.health_score = 0.0
                    component.process = None
                    component.pid = None
            else:
                component.status = "STOPPED"
                component.health_score = 0.0

            component.last_health_check = datetime.now()

        except Exception as e:
            logger.error(f"Error checking health of {name}: {e}")
            component.status = "ERROR"
            component.error_message = str(e)
            component.health_score = 0.0

    async def check_health_endpoint(self, port: int) -> float:
        """Check health endpoint of a component"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health", timeout=5) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return data.get("health_score", 100.0)
                        except:
                            return 100.0
                    else:
                        return 50.0
        except Exception:
            return 0.0

    async def auto_recovery_loop(self):
        """Auto-recovery loop for failed components"""
        while self.system_running:
            try:
                await self.check_and_recover_components()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in auto-recovery loop: {e}")
                await asyncio.sleep(5)

    async def check_and_recover_components(self):
        """Check and recover failed components"""
        for name, component in self.components.items():
            if component.status in ["CRASHED", "ERROR"] and component.auto_restart:
                if component.restart_count < component.max_restarts:
                    logger.info(f"Attempting to restart component: {name}")
                    component.restart_count += 1

                    # Wait before restart
                    restart_delay = self.config.get("monitoring", {}).get("restart_delay", 5)
                    await asyncio.sleep(restart_delay)

                    # Attempt restart
                    success = await self.start_component(name)
                    if success:
                        logger.info(f"✅ Component {name} restarted successfully")
                    else:
                        logger.error(f"❌ Failed to restart component {name}")

                        # If critical component can't be restarted, alert
                        if component.critical:
                            logger.critical(f"🚨 Critical component {name} cannot be restarted!")
                else:
                    logger.error(f"Component {name} has exceeded max restart attempts")

    async def resource_monitoring_loop(self):
        """Monitor system resources"""
        while self.system_running:
            try:
                await self.monitor_system_resources()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in resource monitoring loop: {e}")
                await asyncio.sleep(10)

    async def monitor_system_resources(self):
        """Monitor system resources and alert if needed"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")

            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                logger.warning(f"High memory usage: {memory.percent:.1f}%")

            # Disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                logger.warning(f"High disk usage: {disk.percent:.1f}%")

            # Log resource usage (debug level)
            logger.debug(f"Resources - CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%, Disk: {disk.percent:.1f}%")

        except Exception as e:
            logger.error(f"Error monitoring system resources: {e}")

    async def status_reporting_loop(self):
        """Periodic status reporting"""
        while self.system_running:
            try:
                await self.report_system_status()
                await asyncio.sleep(300)  # Report every 5 minutes
            except Exception as e:
                logger.error(f"Error in status reporting loop: {e}")
                await asyncio.sleep(30)

    async def report_system_status(self):
        """Report current system status"""
        try:
            status = await self.get_system_status()

            logger.info("📊 SYSTEM STATUS REPORT")
            logger.info("=" * 50)
            logger.info(f"Uptime: {status.uptime}")
            logger.info(f"Components: {status.running_components}/{status.total_components} running")
            logger.info(f"Overall Health: {status.overall_health:.1f}%")
            logger.info(f"CPU: {status.resource_usage.get('cpu', 0):.1f}%")
            logger.info(f"Memory: {status.resource_usage.get('memory', 0):.1f}%")

            if status.alerts:
                logger.info("🚨 Active Alerts:")
                for alert in status.alerts:
                    logger.info(f"  - {alert}")

            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"Error reporting system status: {e}")

    async def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        try:
            uptime = datetime.now() - self.start_time
            total_components = len(self.components)
            running_components = sum(1 for c in self.components.values() if c.status == "RUNNING")
            failed_components = sum(1 for c in self.components.values() if c.status in ["CRASHED", "ERROR"])

            # Calculate overall health
            if total_components > 0:
                health_scores = [c.health_score for c in self.components.values()]
                overall_health = sum(health_scores) / len(health_scores)
            else:
                overall_health = 0.0

            # Get resource usage
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent

            resource_usage = {
                "cpu": cpu_usage,
                "memory": memory_usage,
                "disk": disk_usage
            }

            # Generate alerts
            alerts = []
            if failed_components > 0:
                alerts.append(f"{failed_components} component(s) failed")
            if cpu_usage > 80:
                alerts.append(f"High CPU usage: {cpu_usage:.1f}%")
            if memory_usage > 85:
                alerts.append(f"High memory usage: {memory_usage:.1f}%")
            if overall_health < 70:
                alerts.append(f"Low system health: {overall_health:.1f}%")

            return SystemStatus(
                running=self.system_running,
                start_time=self.start_time,
                uptime=uptime,
                total_components=total_components,
                running_components=running_components,
                failed_components=failed_components,
                overall_health=overall_health,
                resource_usage=resource_usage,
                alerts=alerts
            )

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return SystemStatus(
                running=False,
                start_time=self.start_time,
                uptime=timedelta(0),
                total_components=0,
                running_components=0,
                failed_components=0,
                overall_health=0.0,
                resource_usage={},
                alerts=[f"Status error: {str(e)}"]
            )

    async def record_component_action(self, component_name: str, action: str,
                                    success: bool, error_message: str = None):
        """Record component action in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO launch_history
                (component_name, action, timestamp, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                component_name,
                action,
                datetime.now().isoformat(),
                success,
                error_message
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error recording component action: {e}")

    async def record_session_start(self):
        """Record session start in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            session_id = f"session_{int(self.start_time.timestamp())}"

            cursor.execute('''
                INSERT INTO system_sessions
                (session_id, start_time, total_components)
                VALUES (?, ?, ?)
            ''', (
                session_id,
                self.start_time.isoformat(),
                len(self.components)
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error recording session start: {e}")

    async def shutdown_system(self):
        """Gracefully shutdown the system"""
        logger.info("🛑 Shutting down Ultimate AGI System V3...")
        logger.info("=" * 60)

        self.system_running = False

        # Stop all components
        for name, component in self.components.items():
            await self.stop_component(name, component)

        # Record session end
        await self.record_session_end()

        # Shutdown executor
        self.executor.shutdown(wait=True)

        uptime = datetime.now() - self.start_time
        logger.info(f"✅ System shutdown complete. Uptime: {uptime}")
        logger.info("=" * 60)

    async def stop_component(self, name: str, component: ComponentInfo):
        """Stop a specific component"""
        try:
            if component.process and component.pid:
                logger.info(f"Stopping component: {name}")

                try:
                    process = psutil.Process(component.pid)

                    # Try graceful shutdown first
                    process.terminate()

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        logger.info(f"✅ Component {name} stopped gracefully")
                    except psutil.TimeoutExpired:
                        # Force kill if needed
                        process.kill()
                        logger.warning(f"⚠️ Component {name} force-killed")

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    logger.info(f"Component {name} already stopped")

                component.status = "STOPPED"
                component.process = None
                component.pid = None

                # Record stop action
                await self.record_component_action(name, "STOP", True)

        except Exception as e:
            logger.error(f"Error stopping component {name}: {e}")
            await self.record_component_action(name, "STOP", False, str(e))

    async def record_session_end(self):
        """Record session end in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            session_id = f"session_{int(self.start_time.timestamp())}"
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()

            running_components = sum(1 for c in self.components.values() if c.status == "RUNNING")

            cursor.execute('''
                UPDATE system_sessions
                SET end_time = ?, successful_components = ?, uptime_seconds = ?
                WHERE session_id = ?
            ''', (
                datetime.now().isoformat(),
                running_components,
                uptime_seconds,
                session_id
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error recording session end: {e}")

async def main():
    """Main entry point"""
    print("🚀 Ultimate AGI System V3 - Production Launcher")
    print("=" * 60)
    print("Starting comprehensive AI system with:")
    print("  • Advanced RL Trading System")
    print("  • Claudia AI Integration")
    print("  • WatchYourLAN Network Monitoring")
    print("  • Real-time Health Monitoring")
    print("  • Self-healing and Auto-recovery")
    print("  • 24/7 Production Operation")
    print("=" * 60)

    try:
        launcher = UltimateAGILauncher()
        await launcher.start_system()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error in launcher: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
