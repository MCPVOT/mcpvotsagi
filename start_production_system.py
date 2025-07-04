#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCPVotsAGI Production System Startup
====================================
Real services only - no demos, no mocks, no fake data
"""

import asyncio
import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import psutil
import time

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ProductionSystem")

class MCPVotsAGIProduction:
    """Production system startup - real services only"""
    
    def __init__(self):
        # Set paths
        if sys.platform == "win32":
            self.workspace = Path("C:/Workspace")
        else:
            self.workspace = Path("/mnt/c/Workspace")
            
        self.mcpvots = self.workspace / "MCPVots"
        self.mcpvots_agi = self.workspace / "MCPVotsAGI"
        
        # Real service configurations based on analysis
        self.real_services = {
            # Core Oracle AGI Services
            'oracle_agi_core': {
                'script': 'working_oracle.py',
                'port': 8888,
                'path': self.workspace,
                'critical': True,
                'health_check': 'http://localhost:8888/oracle/status'
            },
            'trilogy_oracle_brain': {
                'script': 'trilogy_oracle_brain.py',
                'port': 8887,
                'path': self.workspace,
                'critical': True,
                'health_check': 'http://localhost:8887/health'
            },
            'dgm_voltagents_trading': {
                'script': 'servers/dgm_voltagents_trading_server.py',
                'port': 8886,
                'path': self.mcpvots,
                'critical': True,
                'health_check': 'http://localhost:8886/dgm/status'
            },
            
            # MCP Servers
            'gemini_cli_service': {
                'script': 'gemini_cli_http_server.py',
                'port': 8080,
                'path': self.mcpvots,
                'critical': True,
                'env': {'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY', '')}
            },
            'memory_service': {
                'script': 'memory_service.py',
                'port': 8894,
                'path': self.mcpvots,
                'critical': True
            },
            'chat_api': {
                'script': 'chat_api.py',
                'port': 8890,
                'path': self.mcpvots,
                'critical': True
            },
            
            # Trading Services
            'oracle_solana_trading': {
                'script': 'oracle_solana_trading_system.py',
                'port': None,  # Runs as background service
                'path': self.workspace,
                'critical': False
            },
            'advanced_arbitrage_engine': {
                'script': 'advanced_arbitrage_engine.py',
                'port': None,
                'path': self.workspace,
                'critical': False
            },
            
            # Dashboard Services
            'enhanced_oracle_dashboard': {
                'script': 'enhanced_oracle_dashboard.py',
                'port': 3001,
                'path': self.mcpvots,
                'critical': False
            },
            'oracle_agi_unified_final': {
                'script': 'oracle_agi_v5_unified_final.py',
                'port': 3002,
                'path': self.mcpvots_agi,
                'critical': True
            },
            
            # Integration Services
            'oracle_claudia_integration': {
                'script': 'oracle_claudia_integration.py',
                'port': 3003,
                'path': self.mcpvots_agi,
                'critical': False
            }
        }
        
        # Real MCP servers from mcp-config.json
        self.mcp_servers = [
            {'name': 'GitHub MCP', 'port': 3001},
            {'name': 'Memory MCP', 'port': 3002},
            {'name': 'HuggingFace MCP', 'port': 3003},
            {'name': 'Solana MCP', 'port': 3005},
            {'name': 'Browser Tools MCP', 'port': 3006},
            {'name': 'Trilogy AGI Gateway', 'port': 8000}
        ]
        
        self.processes = {}
        self.failed_services = []
        
    async def start_production(self):
        """Start the production system"""
        logger.info("="*80)
        logger.info(" MCPVOTSAGI PRODUCTION SYSTEM STARTUP")
        logger.info(" Real Services Only - No Demos")
        logger.info("="*80)
        
        # Pre-flight checks
        if not await self._preflight_checks():
            logger.error("Pre-flight checks failed. Aborting startup.")
            return False
            
        # Start services in order
        logger.info("\nPhase 1: Starting Core Services...")
        core_started = await self._start_core_services()
        
        logger.info("\nPhase 2: Starting Trading Services...")
        trading_started = await self._start_trading_services()
        
        logger.info("\nPhase 3: Starting Dashboard Services...")
        dashboard_started = await self._start_dashboard_services()
        
        logger.info("\nPhase 4: Verifying System Health...")
        health_status = await self._verify_system_health()
        
        # Report status
        self._report_startup_status(core_started, trading_started, dashboard_started, health_status)
        
        return len(self.failed_services) == 0
        
    async def _preflight_checks(self):
        """Pre-flight system checks"""
        logger.info("Running pre-flight checks...")
        
        checks_passed = True
        
        # Check Python environment
        logger.info(f"Python: {sys.version}")
        
        # Check virtual environment
        venv_path = self.workspace / ".venv"
        if venv_path.exists():
            logger.info(f"✓ Virtual environment found: {venv_path}")
        else:
            logger.warning("✗ No virtual environment found - using system Python")
            
        # Check for required directories
        required_dirs = [self.workspace, self.mcpvots, self.mcpvots_agi]
        for dir_path in required_dirs:
            if dir_path.exists():
                logger.info(f"✓ Directory exists: {dir_path}")
            else:
                logger.error(f"✗ Directory missing: {dir_path}")
                checks_passed = False
                
        # Check for critical environment variables
        critical_env_vars = ['GEMINI_API_KEY']
        for var in critical_env_vars:
            if os.environ.get(var):
                logger.info(f"✓ Environment variable set: {var}")
            else:
                logger.warning(f"✗ Environment variable missing: {var}")
                # Not failing for now, but warning
                
        # Check for port conflicts
        critical_ports = [8888, 8887, 8886, 3002]
        for port in critical_ports:
            if self._is_port_in_use(port):
                logger.warning(f"⚠ Port {port} already in use")
                
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        logger.info(f"System resources - CPU: {cpu_percent}%, Memory: {memory.percent}%")
        
        if memory.percent > 90:
            logger.warning("⚠ High memory usage detected")
            
        return checks_passed
        
    async def _start_core_services(self):
        """Start core Oracle AGI services"""
        core_services = ['oracle_agi_core', 'trilogy_oracle_brain', 'dgm_voltagents_trading', 
                        'gemini_cli_service', 'memory_service', 'chat_api']
        
        started = 0
        for service_name in core_services:
            if service_name in self.real_services:
                success = await self._start_service(service_name, self.real_services[service_name])
                if success:
                    started += 1
                elif self.real_services[service_name].get('critical', False):
                    logger.error(f"Critical service {service_name} failed to start")
                    self.failed_services.append(service_name)
                    
        return started
        
    async def _start_trading_services(self):
        """Start trading services"""
        trading_services = ['oracle_solana_trading', 'advanced_arbitrage_engine']
        
        started = 0
        for service_name in trading_services:
            if service_name in self.real_services:
                success = await self._start_service(service_name, self.real_services[service_name])
                if success:
                    started += 1
                    
        return started
        
    async def _start_dashboard_services(self):
        """Start dashboard services"""
        dashboard_services = ['oracle_agi_unified_final', 'enhanced_oracle_dashboard', 
                            'oracle_claudia_integration']
        
        started = 0
        for service_name in dashboard_services:
            if service_name in self.real_services:
                success = await self._start_service(service_name, self.real_services[service_name])
                if success:
                    started += 1
                elif self.real_services[service_name].get('critical', False):
                    self.failed_services.append(service_name)
                    
        return started
        
    async def _start_service(self, name, config):
        """Start a single service"""
        script = config['script']
        port = config.get('port')
        path = config.get('path', self.workspace)
        env = config.get('env', {})
        
        # Check if already running
        if port and self._is_port_in_use(port):
            logger.info(f"✓ {name} already running on port {port}")
            return True
            
        # Find script
        script_path = path / script
        if not script_path.exists():
            # Try alternative paths
            alt_paths = [self.workspace, self.mcpvots, self.mcpvots_agi]
            for alt_path in alt_paths:
                alt_script = alt_path / script
                if alt_script.exists():
                    script_path = alt_script
                    break
                    
        if not script_path.exists():
            logger.error(f"✗ Script not found for {name}: {script}")
            return False
            
        # Prepare Python executable
        if sys.platform == "win32":
            venv_python = self.workspace / ".venv" / "Scripts" / "python.exe"
            python_exe = str(venv_python) if venv_python.exists() else sys.executable
        else:
            python_exe = sys.executable
            
        # Prepare environment
        process_env = os.environ.copy()
        process_env.update(env)
        
        try:
            logger.info(f"Starting {name}...")
            
            # Start the process
            process = subprocess.Popen(
                [python_exe, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(script_path.parent),
                env=process_env
            )
            
            self.processes[name] = process
            
            # Wait for startup
            await asyncio.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                # Additional port check if applicable
                if port and self._is_port_in_use(port):
                    logger.info(f"✓ {name} started successfully on port {port}")
                    return True
                elif not port:
                    logger.info(f"✓ {name} started successfully (no port)")
                    return True
                else:
                    logger.error(f"✗ {name} process running but port {port} not listening")
                    return False
            else:
                # Process died
                stderr = process.stderr.read().decode('utf-8', errors='ignore')
                logger.error(f"✗ {name} failed to start: {stderr[:200]}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Failed to start {name}: {e}")
            return False
            
    def _is_port_in_use(self, port):
        """Check if a port is in use"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
            
    async def _verify_system_health(self):
        """Verify system health after startup"""
        health_checks = {
            'oracle_agi': 'http://localhost:8888/oracle/status',
            'trilogy_brain': 'http://localhost:8887/health',
            'dgm_voltagents': 'http://localhost:8886/dgm/status',
            'unified_dashboard': 'http://localhost:3002/api/status'
        }
        
        healthy = 0
        total = len(health_checks)
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for service, url in health_checks.items():
                    try:
                        async with session.get(url, timeout=5) as resp:
                            if resp.status == 200:
                                logger.info(f"✓ {service} health check passed")
                                healthy += 1
                            else:
                                logger.warning(f"✗ {service} health check failed: status {resp.status}")
                    except Exception as e:
                        logger.warning(f"✗ {service} health check failed: {e}")
                        
        except ImportError:
            logger.warning("aiohttp not available for health checks")
            
        return healthy, total
        
    def _report_startup_status(self, core, trading, dashboard, health):
        """Report final startup status"""
        logger.info("\n" + "="*80)
        logger.info(" STARTUP SUMMARY")
        logger.info("="*80)
        
        logger.info(f"Core Services Started: {core}")
        logger.info(f"Trading Services Started: {trading}")
        logger.info(f"Dashboard Services Started: {dashboard}")
        
        if health:
            healthy, total = health
            logger.info(f"Health Checks Passed: {healthy}/{total}")
            
        if self.failed_services:
            logger.error(f"\nFailed Services: {', '.join(self.failed_services)}")
        else:
            logger.info("\n✓ All critical services started successfully!")
            
        logger.info("\n" + "="*80)
        logger.info(" PRODUCTION SYSTEM ONLINE")
        logger.info("="*80)
        logger.info("\nAccess Points:")
        logger.info("  🔮 Oracle AGI Dashboard: http://localhost:3002")
        logger.info("  📊 Enhanced Dashboard: http://localhost:3001")
        logger.info("  🌟 Claudia Integration: http://localhost:3003")
        logger.info("\nAPI Endpoints:")
        logger.info("  Oracle Core: http://localhost:8888")
        logger.info("  Trilogy Brain: http://localhost:8887")
        logger.info("  DGM Trading: http://localhost:8886")
        logger.info("="*80)
        
    async def monitor_system(self):
        """Monitor running services"""
        logger.info("\nStarting system monitor...")
        
        while True:
            try:
                # Check process health
                dead_processes = []
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        dead_processes.append(name)
                        
                if dead_processes:
                    logger.warning(f"Dead processes detected: {dead_processes}")
                    for name in dead_processes:
                        logger.info(f"Attempting to restart {name}...")
                        if name in self.real_services:
                            await self._start_service(name, self.real_services[name])
                            
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
                
    async def shutdown(self):
        """Shutdown all services"""
        logger.info("\nShutting down production system...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {name}")
                    process.kill()
                    
        logger.info("All services stopped")

async def main():
    """Main entry point"""
    system = MCPVotsAGIProduction()
    
    try:
        # Start production system
        success = await system.start_production()
        
        if success:
            # Monitor system
            await system.monitor_system()
        else:
            logger.error("System startup failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\nShutdown requested...")
    except Exception as e:
        logger.error(f"System error: {e}")
        return 1
    finally:
        await system.shutdown()
        
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)