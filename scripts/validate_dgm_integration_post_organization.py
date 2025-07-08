#!/usr/bin/env python3
"""
DGM Integration Validation Script - Post Repository Organization
================================================================

This script validates that all DGM services are functioning correctly
after the repository reorganization. It tests:
1. DGM service imports and initialization
2. Health check endpoints
3. A2A communication
4. File path consistency
5. Service dependencies

Author: MCPVotsAGI Team
Date: January 2025
Version: 1.0.0
"""

import asyncio
import sys
import subprocess
import time
import json
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dgm_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DGMValidationSuite:
    """Comprehensive DGM validation after repository organization"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.services = {
            "dgm_evolution": {
                "path": "services/dgm_evolution_connector.py",
                "port": 8003,
                "health_endpoint": "/health"
            },
            "dgm_trading_v2": {
                "path": "src/trading/dgm_trading_algorithms_v2.py",
                "port": 8004,
                "health_endpoint": "/health"
            },
            "dgm_trading_legacy": {
                "path": "src/trading/dgm_trading_algorithms.py",
                "port": 8005,
                "health_endpoint": "/health"
            }
        }
        self.validation_results = {}

    async def validate_file_paths(self) -> Dict[str, bool]:
        """Validate that all DGM service files exist in correct locations"""
        logger.info("🔍 Validating DGM service file paths...")

        path_results = {}
        for service_name, config in self.services.items():
            file_path = self.project_root / config["path"]
            exists = file_path.exists()
            path_results[service_name] = exists

            if exists:
                logger.info(f"✅ {service_name}: {file_path}")
            else:
                logger.error(f"❌ {service_name}: {file_path} NOT FOUND")

        return path_results

    async def validate_imports(self) -> Dict[str, bool]:
        """Test that DGM services can be imported correctly"""
        logger.info("🔍 Validating DGM service imports...")

        import_results = {}

        # Test DGM Evolution Connector
        try:
            sys.path.insert(0, str(self.project_root / "services"))
            import dgm_evolution_connector
            import_results["dgm_evolution"] = True
            logger.info("✅ DGM Evolution Connector import successful")
        except Exception as e:
            import_results["dgm_evolution"] = False
            logger.error(f"❌ DGM Evolution Connector import failed: {e}")

        # Test DGM Trading V2
        try:
            sys.path.insert(0, str(self.project_root / "src" / "trading"))
            # Use exec to avoid import issues during static analysis
            exec("import dgm_trading_algorithms_v2")
            import_results["dgm_trading_v2"] = True
            logger.info("✅ DGM Trading V2 import successful")
        except Exception as e:
            import_results["dgm_trading_v2"] = False
            logger.error(f"❌ DGM Trading V2 import failed: {e}")

        # Test DGM Trading Legacy
        try:
            # Use exec to avoid import issues during static analysis
            exec("import dgm_trading_algorithms")
            import_results["dgm_trading_legacy"] = True
            logger.info("✅ DGM Trading Legacy import successful")
        except Exception as e:
            import_results["dgm_trading_legacy"] = False
            logger.error(f"❌ DGM Trading Legacy import failed: {e}")

        return import_results

    async def start_dgm_services(self) -> Dict[str, bool]:
        """Start DGM services and validate they're running"""
        logger.info("🚀 Starting DGM services...")

        startup_results = {}
        processes = {}

        for service_name, config in self.services.items():
            try:
                file_path = self.project_root / config["path"]

                if not file_path.exists():
                    startup_results[service_name] = False
                    continue

                # Start service process
                process = subprocess.Popen(
                    [sys.executable, str(file_path)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                processes[service_name] = process
                startup_results[service_name] = True
                logger.info(f"✅ Started {service_name} (PID: {process.pid})")

                # Give service time to start
                await asyncio.sleep(2)

            except Exception as e:
                startup_results[service_name] = False
                logger.error(f"❌ Failed to start {service_name}: {e}")

        # Wait for services to fully initialize
        await asyncio.sleep(5)

        # Store processes for cleanup
        self.processes = processes
        return startup_results

    async def validate_health_endpoints(self) -> Dict[str, bool]:
        """Test health check endpoints for all DGM services"""
        logger.info("🏥 Validating DGM service health endpoints...")

        health_results = {}
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for service_name, config in self.services.items():
                try:
                    url = f"http://localhost:{config['port']}{config['health_endpoint']}"

                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            health_results[service_name] = True
                            logger.info(f"✅ {service_name} health check passed: {data.get('status', 'healthy')}")
                        else:
                            health_results[service_name] = False
                            logger.error(f"❌ {service_name} health check failed: HTTP {response.status}")

                except Exception as e:
                    health_results[service_name] = False
                    logger.error(f"❌ {service_name} health check error: {e}")

        return health_results

    async def validate_a2a_communication(self) -> Dict[str, bool]:
        """Test A2A communication between DGM services"""
        logger.info("🔗 Validating A2A communication...")

        a2a_results = {}

        try:
            # Import A2A tools
            sys.path.insert(0, str(self.project_root / "core"))
            from a2a_protocol import A2AProtocol

            # Initialize A2A protocol
            a2a = A2AProtocol()
            await a2a.initialize()

            # Test message sending between DGM services
            test_message = {
                "type": "health_check",
                "from": "validation_suite",
                "timestamp": time.time(),
                "data": {"test": True}
            }

            for service_name in self.services.keys():
                try:
                    await a2a.send_message(f"dgm_{service_name}", test_message)
                    a2a_results[service_name] = True
                    logger.info(f"✅ A2A message sent to {service_name}")
                except Exception as e:
                    a2a_results[service_name] = False
                    logger.error(f"❌ A2A communication failed for {service_name}: {e}")

            await a2a.close()

        except Exception as e:
            logger.error(f"❌ A2A validation failed: {e}")
            for service_name in self.services.keys():
                a2a_results[service_name] = False

        return a2a_results

    async def validate_dependencies(self) -> Dict[str, bool]:
        """Check that all required dependencies are available"""
        logger.info("📦 Validating DGM service dependencies...")

        dependency_results = {}
        required_packages = [
            "numpy", "pandas", "scipy", "scikit-learn",
            "aiohttp", "redis", "websockets", "asyncio",
            "torch", "transformers", "fastapi", "uvicorn"
        ]

        for package in required_packages:
            try:
                __import__(package)
                dependency_results[package] = True
                logger.info(f"✅ {package} available")
            except ImportError:
                dependency_results[package] = False
                logger.error(f"❌ {package} missing")

        return dependency_results

    async def cleanup_services(self):
        """Stop all started services"""
        logger.info("🧹 Cleaning up services...")

        if hasattr(self, 'processes'):
            for service_name, process in self.processes.items():
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info(f"✅ Stopped {service_name}")
                except Exception as e:
                    logger.error(f"❌ Error stopping {service_name}: {e}")
                    try:
                        process.kill()
                    except:
                        pass

    async def generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("📊 Generating DGM validation report...")

        report = {
            "validation_timestamp": time.time(),
            "validation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": str(self.project_root),
            "services_tested": list(self.services.keys()),
            "results": self.validation_results,
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }

        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0

        for category, results in self.validation_results.items():
            for test, result in results.items():
                total_tests += 1
                if result:
                    passed_tests += 1

        report["summary"]["total_tests"] = total_tests
        report["summary"]["passed_tests"] = passed_tests
        report["summary"]["failed_tests"] = total_tests - passed_tests
        report["summary"]["success_rate"] = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Save report
        report_path = self.project_root / "reports" / "DGM_POST_ORGANIZATION_VALIDATION_REPORT.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Validation report saved to: {report_path}")
        return report

    async def run_full_validation(self):
        """Run complete DGM validation suite"""
        logger.info("🚀 Starting DGM Integration Validation Suite")
        logger.info("=" * 60)

        try:
            # Run all validation tests
            self.validation_results["file_paths"] = await self.validate_file_paths()
            self.validation_results["imports"] = await self.validate_imports()
            self.validation_results["dependencies"] = await self.validate_dependencies()
            self.validation_results["service_startup"] = await self.start_dgm_services()
            self.validation_results["health_endpoints"] = await self.validate_health_endpoints()
            self.validation_results["a2a_communication"] = await self.validate_a2a_communication()

            # Generate report
            report = await self.generate_validation_report()

            # Print summary
            logger.info("=" * 60)
            logger.info("🎯 DGM VALIDATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total Tests: {report['summary']['total_tests']}")
            logger.info(f"Passed: {report['summary']['passed_tests']}")
            logger.info(f"Failed: {report['summary']['failed_tests']}")
            logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")

            if report['summary']['success_rate'] >= 90:
                logger.info("🎉 DGM INTEGRATION VALIDATION: SUCCESS!")
            elif report['summary']['success_rate'] >= 70:
                logger.info("⚠️  DGM INTEGRATION VALIDATION: PARTIAL SUCCESS")
            else:
                logger.error("❌ DGM INTEGRATION VALIDATION: FAILURE")

        except Exception as e:
            logger.error(f"💥 Validation suite error: {e}")

        finally:
            await self.cleanup_services()

        return self.validation_results

async def main():
    """Main validation entry point"""
    # Ensure logs directory exists
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Run validation suite
    validator = DGMValidationSuite()
    results = await validator.run_full_validation()

    # Exit with appropriate code
    total_tests = sum(len(category_results) for category_results in results.values())
    passed_tests = sum(sum(category_results.values()) for category_results in results.values())
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    sys.exit(0 if success_rate >= 90 else 1)

if __name__ == "__main__":
    asyncio.run(main())
