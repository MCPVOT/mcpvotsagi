#!/usr/bin/env python3
"""
DGM Services Runtime Test
========================

Tests that DGM services can be imported and initialized in the new repository structure.

Author: MCPVotsAGI Team
Date: January 2025
Version: 1.0.0
"""

import sys
import subprocess
import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DGMServicesRuntimeTest:
    """Test DGM services runtime functionality"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}

    def test_dgm_service_imports(self) -> Dict[str, bool]:
        """Test that DGM services can be imported correctly"""
        logger.info("🔍 Testing DGM service imports...")

        import_results = {}

        # Test DGM Evolution Connector
        try:
            sys.path.insert(0, str(self.project_root / "services"))
            exec("import dgm_evolution_connector")
            import_results["dgm_evolution_connector"] = True
            logger.info("✅ DGM Evolution Connector import successful")
        except Exception as e:
            import_results["dgm_evolution_connector"] = False
            logger.error(f"❌ DGM Evolution Connector import failed: {e}")

        # Test DGM Trading V2
        try:
            sys.path.insert(0, str(self.project_root / "src" / "trading"))
            exec("import dgm_trading_algorithms_v2")
            import_results["dgm_trading_algorithms_v2"] = True
            logger.info("✅ DGM Trading V2 import successful")
        except Exception as e:
            import_results["dgm_trading_algorithms_v2"] = False
            logger.error(f"❌ DGM Trading V2 import failed: {e}")

        # Test DGM Trading Legacy
        try:
            exec("import dgm_trading_algorithms")
            import_results["dgm_trading_algorithms"] = True
            logger.info("✅ DGM Trading Legacy import successful")
        except Exception as e:
            import_results["dgm_trading_algorithms"] = False
            logger.error(f"❌ DGM Trading Legacy import failed: {e}")

        # Test Ecosystem Manager
        try:
            exec("import ecosystem_manager")
            import_results["ecosystem_manager"] = True
            logger.info("✅ Ecosystem Manager import successful")
        except Exception as e:
            import_results["ecosystem_manager"] = False
            logger.error(f"❌ Ecosystem Manager import failed: {e}")

        return import_results

    def test_service_syntax(self) -> Dict[str, bool]:
        """Test that service files have valid Python syntax"""
        logger.info("🔍 Testing service file syntax...")

        syntax_results = {}
        service_files = [
            "services/dgm_evolution_connector.py",
            "src/trading/dgm_trading_algorithms_v2.py",
            "src/trading/dgm_trading_algorithms.py",
            "services/ecosystem_manager.py"
        ]

        for service_file in service_files:
            file_path = self.project_root / service_file

            if not file_path.exists():
                syntax_results[service_file] = False
                logger.error(f"❌ File not found: {service_file}")
                continue

            try:
                # Use python -m py_compile to check syntax
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(file_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root)
                )

                if result.returncode == 0:
                    syntax_results[service_file] = True
                    logger.info(f"✅ Syntax valid: {service_file}")
                else:
                    syntax_results[service_file] = False
                    logger.error(f"❌ Syntax error in {service_file}: {result.stderr}")

            except Exception as e:
                syntax_results[service_file] = False
                logger.error(f"❌ Error checking {service_file}: {e}")

        return syntax_results

    def test_service_startup(self) -> Dict[str, bool]:
        """Test that services can start without immediate errors"""
        logger.info("🔍 Testing service startup...")

        startup_results = {}
        service_configs = [
            {
                "name": "dgm_evolution_connector",
                "script": "services/dgm_evolution_connector.py",
                "timeout": 5
            },
            {
                "name": "dgm_trading_algorithms_v2",
                "script": "src/trading/dgm_trading_algorithms_v2.py",
                "timeout": 5
            }
        ]

        for config in service_configs:
            script_path = self.project_root / config["script"]

            if not script_path.exists():
                startup_results[config["name"]] = False
                logger.error(f"❌ Script not found: {config['script']}")
                continue

            try:
                logger.info(f"🚀 Testing startup for {config['name']}...")

                # Start process and let it run briefly
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # Wait for brief startup period
                time.sleep(config["timeout"])

                # Check if process is still running (good sign)
                if process.poll() is None:
                    startup_results[config["name"]] = True
                    logger.info(f"✅ {config['name']} started successfully")

                    # Terminate the test process
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()

                else:
                    startup_results[config["name"]] = False
                    stdout, stderr = process.communicate()
                    logger.error(f"❌ {config['name']} exited early: {stderr.decode()[:200]}")

            except Exception as e:
                startup_results[config["name"]] = False
                logger.error(f"❌ Error testing {config['name']}: {e}")

        return startup_results

    def test_configuration_files(self) -> Dict[str, bool]:
        """Test that configuration files are valid"""
        logger.info("🔍 Testing configuration files...")

        config_results = {}

        # Test YAML config
        config_file = self.project_root / "config" / "ecosystem_config.yaml"
        try:
            import yaml
            with open(config_file, 'r') as f:
                yaml.safe_load(f)
            config_results["ecosystem_config.yaml"] = True
            logger.info("✅ ecosystem_config.yaml is valid")
        except Exception as e:
            config_results["ecosystem_config.yaml"] = False
            logger.error(f"❌ ecosystem_config.yaml error: {e}")

        # Test package.json
        package_file = self.project_root / "package.json"
        try:
            with open(package_file, 'r') as f:
                json.load(f)
            config_results["package.json"] = True
            logger.info("✅ package.json is valid")
        except Exception as e:
            config_results["package.json"] = False
            logger.error(f"❌ package.json error: {e}")

        return config_results

    def test_utility_imports(self) -> Dict[str, bool]:
        """Test that utility imports work"""
        logger.info("🔍 Testing utility imports...")

        utility_results = {}

        # Test import helper
        try:
            sys.path.insert(0, str(self.project_root))
            from utils.import_helper import dgm_trading_v2, dgm_evolution, ecosystem_manager
            utility_results["import_helper"] = True
            logger.info("✅ Import helper works")
        except Exception as e:
            utility_results["import_helper"] = False
            logger.error(f"❌ Import helper failed: {e}")

        return utility_results

    def run_comprehensive_test(self) -> Dict:
        """Run all DGM runtime tests"""
        logger.info("🚀 Starting DGM Services Runtime Test")
        logger.info("=" * 60)

        # Run all test categories
        self.test_results["imports"] = self.test_dgm_service_imports()
        self.test_results["syntax"] = self.test_service_syntax()
        self.test_results["startup"] = self.test_service_startup()
        self.test_results["configuration"] = self.test_configuration_files()
        self.test_results["utilities"] = self.test_utility_imports()

        # Calculate summary
        total_tests = 0
        passed_tests = 0

        for category, results in self.test_results.items():
            for test, result in results.items():
                total_tests += 1
                if result:
                    passed_tests += 1

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }

        self.test_results["summary"] = summary

        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 DGM SERVICES RUNTIME TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed_tests']}")
        logger.info(f"Failed: {summary['failed_tests']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")

        if summary['success_rate'] >= 80:
            logger.info("🎉 DGM SERVICES RUNTIME TEST: SUCCESS!")
        elif summary['success_rate'] >= 60:
            logger.info("⚠️  DGM SERVICES RUNTIME TEST: PARTIAL SUCCESS")
        else:
            logger.error("❌ DGM SERVICES RUNTIME TEST: FAILURE")

        # Save detailed results
        report_path = self.project_root / "reports" / "DGM_RUNTIME_TEST_RESULTS.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)

        logger.info(f"📊 Detailed results saved to: {report_path}")
        logger.info("=" * 60)

        return self.test_results

def main():
    """Main test entry point"""
    tester = DGMServicesRuntimeTest()
    results = tester.run_comprehensive_test()

    # Exit with appropriate code
    success_rate = results["summary"]["success_rate"]
    sys.exit(0 if success_rate >= 80 else 1)

if __name__ == "__main__":
    main()
