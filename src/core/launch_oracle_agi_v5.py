#!/usr/bin/env python3
"""
Oracle AGI V5 Complete System Launcher
=====================================
Launches all components of the Oracle AGI ecosystem
"""

import asyncio
import subprocess
import sys
import os
import time
import logging
import json
from pathlib import Path
import psutil
import requests
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleAGILauncher")

class OracleAGIV5Launcher:
    """Complete Oracle AGI V5 System Launcher"""
    
    def __init__(self):
        self.workspace = Path("/mnt/c/Workspace")
        self.mcpvots_agi = self.workspace / "MCPVotsAGI"
        self.mcpvots = self.workspace / "MCPVots"
        
        # Process tracking
        self.processes = {}
        self.service_configs = self._load_service_configs()
        
    def _load_service_configs(self) -> Dict:
        """Load service configurations"""
        return {
            'oracle_core': {
                'name': 'Oracle AGI Core',
                'port': 8888,
                'script': 'oracle_agi_core.py',
                'path': self.workspace,
                'check_url': 'http://localhost:8888/health',
                'required': True
            },
            'trilogy_brain': {
                'name': 'Trilogy Oracle Brain',
                'port': 8887,
                'script': 'trilogy_oracle_brain.py',
                'path': self.workspace,
                'check_url': 'http://localhost:8887/health',
                'required': True
            },
            'dgm_voltagents': {
                'name': 'DGM Voltagents',
                'port': 8886,
                'script': 'dgm_voltagents.py',
                'path': self.workspace,
                'check_url': 'http://localhost:8886/health',
                'required': False
            },
            'trading_system': {
                'name': 'Trading System',
                'port': 8889,
                'script': 'oracle_trading_agi_enhanced_system.py',
                'path': self.workspace,
                'check_url': 'http://localhost:8889/health',
                'required': True
            },
            'deepseek': {
                'name': 'DeepSeek R1',
                'port': 11434,
                'command': ['ollama', 'serve'],
                'check_url': 'http://localhost:11434/api/tags',
                'required': False
            },
            'gemini_cli': {
                'name': 'Gemini CLI',
                'port': 8080,
                'script': 'gemini_cli_http_server.py',
                'path': self.mcpvots,
                'check_url': 'http://localhost:8080/health',
                'required': False
            },
            'unified_dashboard': {
                'name': 'Unified Dashboard',
                'port': 3002,
                'script': 'oracle_agi_v5_unified_dashboard.py',
                'path': self.mcpvots_agi,
                'check_url': 'http://localhost:3002/api/status',
                'required': True
            }
        }
        
    async def launch_complete_system(self):
        """Launch the complete Oracle AGI V5 system"""
        logger.info("=" * 80)
        logger.info("🚀 Oracle AGI V5 Complete System Launcher")
        logger.info("=" * 80)
        
        try:
            # Phase 1: System checks
            await self._system_checks()
            
            # Phase 2: Start Ollama/DeepSeek
            await self._start_ollama()
            
            # Phase 3: Start core services
            await self._start_core_services()
            
            # Phase 4: Start AI services
            await self._start_ai_services()
            
            # Phase 5: Start unified dashboard
            await self._start_unified_dashboard()
            
            # Phase 6: System verification
            await self._verify_system()
            
            logger.info("=" * 80)
            logger.info("✅ Oracle AGI V5 System Successfully Launched!")
            logger.info("=" * 80)
            logger.info("🌐 Main Dashboard: http://localhost:3002")
            logger.info("🔮 Oracle Core API: http://localhost:8888")
            logger.info("💹 Trading System: http://localhost:8889")
            logger.info("🤖 AI Chat: http://localhost:3002 (integrated)")
            logger.info("=" * 80)
            logger.info("Press Ctrl+C to stop all services")
            
            # Keep running
            await self._monitor_system()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown requested...")
            await self._shutdown_system()
        except Exception as e:
            logger.error(f"❌ System launch failed: {e}")
            await self._shutdown_system()
            raise
            
    async def _system_checks(self):
        """Perform system checks"""
        logger.info("🔍 Performing system checks...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8+ required")
            
        # Check required directories
        dirs_to_check = [self.workspace, self.mcpvots, self.mcpvots_agi]
        for dir_path in dirs_to_check:
            if not dir_path.exists():
                logger.warning(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
                
        # Check for required files
        dashboard_script = self.mcpvots_agi / "oracle_agi_v5_unified_dashboard.py"
        if not dashboard_script.exists():
            raise FileNotFoundError(f"Dashboard script not found: {dashboard_script}")
            
        logger.info("✓ System checks passed")
        
    async def _start_ollama(self):
        """Start Ollama for DeepSeek"""
        logger.info("🤖 Starting Ollama/DeepSeek...")
        
        # Check if Ollama is installed
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True)
            if result.returncode == 0:
                # Check if already running
                if not self._is_port_open(11434):
                    # Start Ollama serve
                    process = subprocess.Popen(
                        ['ollama', 'serve'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    self.processes['ollama'] = process
                    await asyncio.sleep(3)
                    
                # Pull DeepSeek model if not present
                logger.info("Checking DeepSeek model...")
                subprocess.run(['ollama', 'pull', 'deepseek:latest'], check=False)
                logger.info("✓ Ollama/DeepSeek ready")
            else:
                logger.warning("⚠ Ollama not installed, skipping DeepSeek")
        except FileNotFoundError:
            logger.warning("⚠ Ollama not found, skipping DeepSeek integration")
            
    async def _start_core_services(self):
        """Start core Oracle services"""
        logger.info("🔧 Starting core services...")
        
        core_services = ['oracle_core', 'trilogy_brain', 'trading_system']
        
        for service_id in core_services:
            config = self.service_configs.get(service_id)
            if not config:
                continue
                
            if self._is_service_running(config['port']):
                logger.info(f"✓ {config['name']} already running on port {config['port']}")
                continue
                
            await self._start_service(service_id, config)
            
    async def _start_ai_services(self):
        """Start AI services"""
        logger.info("🧠 Starting AI services...")
        
        ai_services = ['gemini_cli', 'dgm_voltagents']
        
        for service_id in ai_services:
            config = self.service_configs.get(service_id)
            if not config:
                continue
                
            if self._is_service_running(config['port']):
                logger.info(f"✓ {config['name']} already running on port {config['port']}")
                continue
                
            await self._start_service(service_id, config)
            
    async def _start_unified_dashboard(self):
        """Start the unified dashboard"""
        logger.info("🎯 Starting Unified Dashboard...")
        
        config = self.service_configs['unified_dashboard']
        
        if self._is_service_running(config['port']):
            logger.warning(f"⚠ Dashboard already running on port {config['port']}")
            # Try to stop it first
            self._stop_service_on_port(config['port'])
            await asyncio.sleep(2)
            
        await self._start_service('unified_dashboard', config)
        
    async def _start_service(self, service_id: str, config: Dict):
        """Start a specific service"""
        logger.info(f"Starting {config['name']}...")
        
        try:
            if 'script' in config:
                # Python script
                script_path = config['path'] / config['script']
                if not script_path.exists():
                    # Try to find alternative scripts
                    alternatives = self._find_alternative_scripts(config['name'])
                    if alternatives:
                        script_path = alternatives[0]
                        logger.info(f"Using alternative script: {script_path}")
                    else:
                        logger.warning(f"⚠ Script not found: {script_path}")
                        if config.get('required', False):
                            raise FileNotFoundError(f"Required script not found: {script_path}")
                        return
                        
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(config['path'])
                )
                self.processes[service_id] = process
                
            elif 'command' in config:
                # Direct command
                process = subprocess.Popen(
                    config['command'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes[service_id] = process
                
            # Wait for service to start
            await asyncio.sleep(3)
            
            # Verify service is running
            if config.get('check_url'):
                if await self._check_service_health(config['check_url']):
                    logger.info(f"✓ {config['name']} started successfully")
                else:
                    logger.warning(f"⚠ {config['name']} started but health check failed")
            else:
                logger.info(f"✓ {config['name']} started")
                
        except Exception as e:
            logger.error(f"❌ Failed to start {config['name']}: {e}")
            if config.get('required', False):
                raise
                
    def _find_alternative_scripts(self, service_name: str) -> List[Path]:
        """Find alternative scripts for a service"""
        alternatives = []
        
        # Map service names to possible script patterns
        patterns = {
            'Oracle AGI Core': ['oracle*.py', 'working_oracle*.py'],
            'Trilogy Oracle Brain': ['trilogy*.py', 'bee_ecosystem*.py'],
            'Trading System': ['*trading*.py', 'launch_oracle*.py'],
            'DGM Voltagents': ['*voltagent*.py', 'dgm*.py'],
            'Gemini CLI': ['gemini*.py', 'simple_gemini*.py']
        }
        
        search_patterns = patterns.get(service_name, [])
        search_dirs = [self.workspace, self.mcpvots]
        
        for directory in search_dirs:
            for pattern in search_patterns:
                matches = list(directory.glob(pattern))
                alternatives.extend(matches)
                
        return alternatives
        
    def _is_service_running(self, port: int) -> bool:
        """Check if a service is running on a port"""
        return self._is_port_open(port)
        
    def _is_port_open(self, port: int) -> bool:
        """Check if a port is open"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
        
    def _stop_service_on_port(self, port: int):
        """Stop service running on a specific port"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            logger.info(f"Stopping process {proc.info['name']} on port {port}")
                            proc.terminate()
                            return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"Error stopping service on port {port}: {e}")
            
    async def _check_service_health(self, url: str) -> bool:
        """Check if a service is healthy"""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
            
    async def _verify_system(self):
        """Verify all services are running"""
        logger.info("🔍 Verifying system status...")
        
        all_healthy = True
        for service_id, config in self.service_configs.items():
            if config.get('check_url'):
                health = await self._check_service_health(config['check_url'])
                status = "✓" if health else "✗"
                logger.info(f"{status} {config['name']} - Port {config['port']}")
                
                if not health and config.get('required', False):
                    all_healthy = False
                    
        if not all_healthy:
            logger.warning("⚠ Some required services are not healthy")
        else:
            logger.info("✅ All systems operational")
            
    async def _monitor_system(self):
        """Monitor system health"""
        while True:
            try:
                # Check process health
                for service_id, process in self.processes.items():
                    if process and process.poll() is not None:
                        logger.warning(f"⚠ {service_id} process died, restarting...")
                        config = self.service_configs.get(service_id)
                        if config:
                            await self._start_service(service_id, config)
                            
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
                
    async def _shutdown_system(self):
        """Shutdown all services"""
        logger.info("🛑 Shutting down Oracle AGI V5...")
        
        # Stop processes in reverse order
        for service_id in reversed(list(self.processes.keys())):
            process = self.processes.get(service_id)
            if process and process.poll() is None:
                logger.info(f"Stopping {service_id}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
        logger.info("✓ All services stopped")

async def main():
    """Main entry point"""
    launcher = OracleAGIV5Launcher()
    await launcher.launch_complete_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Launcher stopped by user")
    except Exception as e:
        logger.error(f"Launcher error: {e}")
        sys.exit(1)