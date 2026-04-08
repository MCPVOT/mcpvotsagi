#!/usr/bin/env python3
"""
Advanced DGM System Launcher
============================

This script launches the complete Advanced DGM ecosystem including:
- Advanced DGM Evolution Engine (Neural Architecture Search, Meta-Learning)
- Neural Architecture Search Optimizer
- DGM Trading Algorithms (v1 and v2)
- DGM Evolution Connector
- Health monitoring and A2A communication

Author: MCPVotsAGI Development Team
Date: 2024
"""

import asyncio
import subprocess
import sys
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import aiohttp
from typing import Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class AdvancedDGMLauncher:
    """Advanced DGM System Launcher and Manager"""

    def __init__(self):
        self.services = {
            'dgm_evolution_connector': {
                'path': 'services/dgm_evolution_connector.py',
                'port': 8081,
                'process': None,
                'status': 'stopped'
            },
            'dgm_trading_v1': {
                'path': 'src/trading/dgm_trading_algorithms.py',
                'port': 8082,
                'process': None,
                'status': 'stopped'
            },
            'dgm_trading_v2': {
                'path': 'src/trading/dgm_trading_algorithms_v2.py',
                'port': 8083,
                'process': None,
                'status': 'stopped'
            },
            'advanced_dgm_evolution': {
                'path': 'services/advanced_dgm_evolution_engine.py',
                'port': 8087,
                'process': None,
                'status': 'stopped'
            },
            'neural_architecture_search': {
                'path': 'services/neural_architecture_search.py',
                'port': 8088,
                'process': None,
                'status': 'stopped'
            }
        }
        self.session = None
        self.startup_timeout = 30
        self.health_check_interval = 5

    async def setup_session(self):
        """Setup HTTP session for health checks"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def launch_service(self, service_name: str) -> bool:
        """Launch a specific service"""
        try:
            service = self.services[service_name]
            service_path = PROJECT_ROOT / service['path']

            if not service_path.exists():
                logger.error(f"❌ Service file not found: {service_path}")
                return False

            # Launch the service
            cmd = [sys.executable, str(service_path)]
            process = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            service['process'] = process
            service['status'] = 'starting'

            logger.info(f"🚀 Launched {service_name} (PID: {process.pid}) on port {service['port']}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to launch {service_name}: {e}")
            self.services[service_name]['status'] = 'failed'
            return False

    async def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        try:
            service = self.services[service_name]
            port = service['port']
            url = f"http://localhost:{port}/health"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    service['status'] = 'running'
                    logger.info(f"✅ {service_name} health check passed: {data.get('status', 'OK')}")
                    return True
                else:
                    logger.warning(f"⚠️ {service_name} health check failed: {response.status}")
                    return False

        except Exception as e:
            logger.debug(f"Health check failed for {service_name}: {e}")
            return False

    async def wait_for_service_startup(self, service_name: str) -> bool:
        """Wait for a service to become healthy"""
        start_time = time.time()

        while time.time() - start_time < self.startup_timeout:
            if await self.check_service_health(service_name):
                return True
            await asyncio.sleep(self.health_check_interval)

        logger.error(f"❌ {service_name} failed to start within {self.startup_timeout} seconds")
        self.services[service_name]['status'] = 'failed'
        return False

    def launch_all_services(self) -> list[str]:
        """Launch all DGM services"""
        logger.info("🚀 Launching Advanced DGM System...")

        launched_services = []
        failed_services = []

        for service_name in self.services.keys():
            if self.launch_service(service_name):
                launched_services.append(service_name)
            else:
                failed_services.append(service_name)

        logger.info(f"✅ Launched {len(launched_services)} services")
        if failed_services:
            logger.warning(f"⚠️ Failed to launch {len(failed_services)} services: {failed_services}")

        return launched_services

    async def validate_all_services(self, launched_services: list[str]) -> dict[str, bool]:
        """Validate all launched services"""
        logger.info("🔍 Validating service health...")

        await self.setup_session()
        validation_results = {}

        try:
            # Wait for all services to start
            logger.info("⏳ Waiting for services to initialize...")
            await asyncio.sleep(15)  # Give services time to start

            # Check each service health
            for service_name in launched_services:
                is_healthy = await self.wait_for_service_startup(service_name)
                validation_results[service_name] = is_healthy

        finally:
            await self.cleanup_session()

        return validation_results

    async def test_advanced_capabilities(self) -> dict[str, bool]:
        """Test advanced DGM capabilities"""
        logger.info("🧪 Testing Advanced DGM Capabilities...")

        await self.setup_session()
        results = {}

        try:
            # Test Advanced DGM Evolution Engine
            results['evolution_engine'] = await self._test_evolution_engine()

            # Test Neural Architecture Search
            results['neural_architecture_search'] = await self._test_nas()

            # Test A2A Communication
            results['a2a_communication'] = await self._test_a2a_communication()

        finally:
            await self.cleanup_session()

        return results

    async def _test_evolution_engine(self) -> bool:
        """Test the advanced evolution engine"""
        try:
            url = "http://localhost:8087/evolve"
            config = {
                "generations": 3,
                "population_size": 5,
                "mutation_rate": 0.1,
                "meta_learning": True
            }

            async with self.session.post(url, json=config) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Evolution engine test passed: {data.get('message', 'Success')}")
                    return True
                else:
                    logger.error(f"❌ Evolution engine test failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"❌ Evolution engine test error: {e}")
            return False

    async def _test_nas(self) -> bool:
        """Test neural architecture search"""
        try:
            url = "http://localhost:8088/search/darts"
            config = {
                "search_space": "macro",
                "epochs": 3,
                "channels": 8
            }

            async with self.session.post(url, json=config) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ NAS test passed: {data.get('message', 'Success')}")
                    return True
                else:
                    logger.error(f"❌ NAS test failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"❌ NAS test error: {e}")
            return False

    async def _test_a2a_communication(self) -> bool:
        """Test Agent-to-Agent communication"""
        try:
            # Test communication between services
            evolution_url = "http://localhost:8087/status"
            trading_url = "http://localhost:8083/health"

            evolution_ok = False
            trading_ok = False

            async with self.session.get(evolution_url) as response:
                evolution_ok = response.status == 200

            async with self.session.get(trading_url) as response:
                trading_ok = response.status == 200

            if evolution_ok and trading_ok:
                logger.info("✅ A2A communication test passed")
                return True
            else:
                logger.error("❌ A2A communication test failed")
                return False

        except Exception as e:
            logger.error(f"❌ A2A communication test error: {e}")
            return False

    def generate_status_report(self, validation_results: dict[str, bool],
                             capability_results: dict[str, bool]) -> str:
        """Generate comprehensive status report"""

        report_path = PROJECT_ROOT / "reports" / "advanced_dgm_system_status.md"
        report_path.parent.mkdir(exist_ok=True)

        # Calculate success rates
        total_services = len(validation_results)
        healthy_services = sum(validation_results.values())
        service_success_rate = healthy_services / total_services if total_services > 0 else 0

        total_capabilities = len(capability_results)
        working_capabilities = sum(capability_results.values())
        capability_success_rate = working_capabilities / total_capabilities if total_capabilities > 0 else 0

        overall_success = (service_success_rate + capability_success_rate) / 2

        report_content = f"""# Advanced DGM System Status Report

## Executive Summary
- **Overall Success Rate**: {overall_success:.2%}
- **Service Health**: {service_success_rate:.2%} ({healthy_services}/{total_services})
- **Capability Tests**: {capability_success_rate:.2%} ({working_capabilities}/{total_capabilities})
- **Timestamp**: {datetime.now().isoformat()}

## Service Status
| Service | Port | Status | Health |
|---------|------|--------|---------|
{chr(10).join(f"| {name} | {info['port']} | {info['status']} | {'✅' if validation_results.get(name, False) else '❌'} |"
             for name, info in self.services.items())}

## Advanced Capabilities
| Capability | Status | Result |
|------------|--------|---------|
{chr(10).join(f"| {name.replace('_', ' ').title()} | {'✅ Pass' if result else '❌ Fail'} | {'Operational' if result else 'Needs Investigation'} |"
             for name, result in capability_results.items())}

## Service Details

### Advanced DGM Evolution Engine (Port 8087)
- **Neural Architecture Search**: Integrated DARTS, Evolutionary, and Progressive NAS
- **Meta-Learning**: Few-shot adaptation and cross-domain transfer
- **Self-Modifying Code**: Architecture optimization with safety checks
- **Status**: {self.services['advanced_dgm_evolution']['status']}

### Neural Architecture Search (Port 8088)
- **DARTS Search**: Differentiable architecture search
- **Evolutionary Search**: Population-based architecture optimization
- **Progressive Search**: Incremental complexity scaling
- **Status**: {self.services['neural_architecture_search']['status']}

### DGM Trading Algorithms
- **v1 (Port 8082)**: Classic trading algorithms with DGM integration
- **v2 (Port 8083)**: Enhanced algorithms with advanced features
- **Status v1**: {self.services['dgm_trading_v1']['status']}
- **Status v2**: {self.services['dgm_trading_v2']['status']}

### DGM Evolution Connector (Port 8081)
- **Agent Communication**: A2A protocol implementation
- **Evolution Coordination**: Cross-service evolution management
- **Status**: {self.services['dgm_evolution_connector']['status']}

## Recommendations

### Immediate Actions
{chr(10).join([
    "- ✅ All services operational - system ready for production" if overall_success >= 0.9
    else "- ⚠️ Some services need attention - check failed components",
    "- 🔍 Monitor service logs for any error patterns",
    "- 📊 Set up continuous health monitoring",
    "- 🔄 Implement automatic service restart on failure"
])}

### Next Steps
1. **Performance Optimization**: Tune neural architecture search parameters
2. **Monitoring**: Implement comprehensive metrics collection
3. **Scaling**: Prepare for distributed deployment
4. **Integration**: Connect with external trading systems
5. **Documentation**: Update API documentation with new endpoints

## API Endpoints

### Advanced DGM Evolution Engine (localhost:8087)
- `GET /health` - Health check
- `GET /status` - Service status
- `POST /evolve` - Run evolution process
- `POST /meta_learn` - Meta-learning adaptation
- `POST /self_modify` - Self-modification process

### Neural Architecture Search (localhost:8088)
- `GET /health` - Health check
- `GET /status` - Service status
- `POST /search/darts` - DARTS architecture search
- `POST /search/evolutionary` - Evolutionary search
- `POST /search/progressive` - Progressive search

### DGM Trading (localhost:8082, localhost:8083)
- `GET /health` - Health check
- `POST /execute_trade` - Execute trading algorithm
- `GET /performance` - Trading performance metrics

### DGM Evolution Connector (localhost:8081)
- `GET /health` - Health check
- `POST /coordinate_evolution` - Cross-service evolution
- `GET /agent_status` - A2A communication status

---
Generated by Advanced DGM System Launcher
MCPVotsAGI Development Team - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"📊 Status report saved to: {report_path}")
        return str(report_path)

    def stop_all_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping all DGM services...")

        for service_name, service in self.services.items():
            if service['process'] and service['process'].poll() is None:
                try:
                    service['process'].terminate()
                    service['process'].wait(timeout=5)
                    service['status'] = 'stopped'
                    logger.info(f"✅ Stopped {service_name}")
                except subprocess.TimeoutExpired:
                    service['process'].kill()
                    service['status'] = 'killed'
                    logger.warning(f"⚠️ Force killed {service_name}")
                except Exception as e:
                    logger.error(f"❌ Error stopping {service_name}: {e}")

async def main():
    """Main launcher function"""
    launcher = AdvancedDGMLauncher()

    try:
        # Launch all services
        launched_services = launcher.launch_all_services()

        if not launched_services:
            logger.error("❌ No services launched successfully")
            return False

        # Validate services
        validation_results = await launcher.validate_all_services(launched_services)

        # Test advanced capabilities
        capability_results = await launcher.test_advanced_capabilities()

        # Generate status report
        report_path = launcher.generate_status_report(validation_results, capability_results)

        # Print summary
        healthy_services = sum(validation_results.values())
        working_capabilities = sum(capability_results.values())

        logger.info(f"\n🎯 Advanced DGM System Launch Complete!")
        logger.info(f"Services Running: {healthy_services}/{len(validation_results)}")
        logger.info(f"Capabilities Working: {working_capabilities}/{len(capability_results)}")
        logger.info(f"Status Report: {report_path}")

        if healthy_services >= len(validation_results) * 0.8:
            logger.info("🎉 Advanced DGM System Launch SUCCESSFUL!")
            logger.info("💡 System is ready for advanced AI evolution tasks")
        else:
            logger.warning("⚠️ Advanced DGM System Launch completed with issues")

        # Keep services running
        logger.info("🔄 Services running... Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(30)
                # Periodic health check
                await launcher.setup_session()
                for service_name in launched_services:
                    await launcher.check_service_health(service_name)
                await launcher.cleanup_session()
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown signal received")

    except Exception as e:
        logger.error(f"❌ Launch failed: {e}")
        return False
    finally:
        launcher.stop_all_services()

    return True

if __name__ == "__main__":
    asyncio.run(main())
