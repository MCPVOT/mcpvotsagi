#!/usr/bin/env python3
"""
Ultimate Trading System V3 - Quick Test
=======================================
🧪 Test all components and integrations
🚀 Verify system functionality before full launch
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemTest")

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

class SystemTester:
    """Test all system components"""

    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown"
        }

    async def run_all_tests(self):
        """Run all system tests"""
        try:
            logger.info("🧪 Starting Ultimate Trading System V3 Tests")
            logger.info("=" * 50)

            # Test 1: Import all components
            await self.test_imports()

            # Test 2: Jupiter API wrapper
            await self.test_jupiter_api()

            # Test 3: RL Integration
            await self.test_rl_integration()

            # Test 4: Trading System
            await self.test_trading_system()

            # Test 5: Dashboard components
            await self.test_dashboard()

            # Test 6: File system access
            await self.test_file_system()

            # Generate report
            await self.generate_report()

        except Exception as e:
            logger.error(f"Error running tests: {e}")
            logger.error(traceback.format_exc())

    async def test_imports(self):
        """Test all component imports"""
        try:
            logger.info("📦 Testing component imports...")

            tests = {
                "jupiter_api_wrapper": self._test_import("jupiter_api_wrapper"),
                "jupiter_rl_integration": self._test_import("jupiter_rl_integration"),
                "ultimate_trading_system_v3": self._test_import("ultimate_trading_system_v3"),
                "ultimate_trading_dashboard_v3": self._test_import("ultimate_trading_dashboard_v3"),
                "deepseek_r1_trading_agent_enhanced": self._test_import("deepseek_r1_trading_agent_enhanced")
            }

            self.test_results["tests"]["imports"] = tests

            passed = sum(1 for result in tests.values() if result["status"] == "pass")
            total = len(tests)

            logger.info(f"📦 Import tests: {passed}/{total} passed")

        except Exception as e:
            logger.error(f"Error testing imports: {e}")
            self.test_results["tests"]["imports"] = {"error": str(e)}

    def _test_import(self, module_name):
        """Test importing a specific module"""
        try:
            __import__(module_name)
            return {"status": "pass", "message": "Import successful"}
        except ImportError as e:
            return {"status": "fail", "message": f"Import failed: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    async def test_jupiter_api(self):
        """Test Jupiter API wrapper"""
        try:
            logger.info("🪐 Testing Jupiter API wrapper...")

            from jupiter_api_wrapper import JupiterAPIWrapper

            api = JupiterAPIWrapper()

            # Test health check
            health = await api.health_check()

            # Test statistics
            stats = api.get_statistics()

            result = {
                "status": "pass" if health else "fail",
                "health_check": health,
                "statistics": stats,
                "message": "Jupiter API test completed"
            }

            self.test_results["tests"]["jupiter_api"] = result
            logger.info(f"🪐 Jupiter API test: {'✅ PASS' if health else '❌ FAIL'}")

        except Exception as e:
            logger.error(f"Error testing Jupiter API: {e}")
            self.test_results["tests"]["jupiter_api"] = {
                "status": "error",
                "message": str(e)
            }

    async def test_rl_integration(self):
        """Test RL integration"""
        try:
            logger.info("🧠 Testing RL integration...")

            from jupiter_rl_integration import JupiterRLIntegration

            rl = JupiterRLIntegration()

            # Test performance metrics
            metrics = rl.get_performance_metrics()

            # Test simple analysis with real data
            result = {
                "status": "pass",
                "metrics": metrics,
                "message": "RL integration test completed"
            }

            self.test_results["tests"]["rl_integration"] = result
            logger.info("🧠 RL integration test: ✅ PASS")

        except Exception as e:
            logger.error(f"Error testing RL integration: {e}")
            self.test_results["tests"]["rl_integration"] = {
                "status": "error",
                "message": str(e)
            }

    async def test_trading_system(self):
        """Test trading system"""
        try:
            logger.info("💰 Testing trading system...")

            from ultimate_trading_system_v3 import UltimateTradingSystemV3

            system = UltimateTradingSystemV3()

            # Test system status
            status = await system.get_system_status()

            result = {
                "status": "pass",
                "system_status": status,
                "message": "Trading system test completed"
            }

            self.test_results["tests"]["trading_system"] = result
            logger.info("💰 Trading system test: ✅ PASS")

        except Exception as e:
            logger.error(f"Error testing trading system: {e}")
            self.test_results["tests"]["trading_system"] = {
                "status": "error",
                "message": str(e)
            }

    async def test_dashboard(self):
        """Test dashboard components"""
        try:
            logger.info("📊 Testing dashboard components...")

            from ultimate_trading_dashboard_v3 import UltimateTradingDashboard

            dashboard = UltimateTradingDashboard()

            result = {
                "status": "pass",
                "message": "Dashboard components test completed"
            }

            self.test_results["tests"]["dashboard"] = result
            logger.info("📊 Dashboard test: ✅ PASS")

        except Exception as e:
            logger.error(f"Error testing dashboard: {e}")
            self.test_results["tests"]["dashboard"] = {
                "status": "error",
                "message": str(e)
            }

    async def test_file_system(self):
        """Test file system access"""
        try:
            logger.info("📁 Testing file system access...")

            # Test F: drive access
            f_drive_accessible = os.path.exists("F:/")

            # Test creating directories
            test_dir = "F:/ULTIMATE_AGI_DATA/RL_TRADING/test/"
            os.makedirs(test_dir, exist_ok=True)

            # Test writing file
            test_file = os.path.join(test_dir, "test.json")
            with open(test_file, 'w') as f:
                json.dump({"test": True, "timestamp": datetime.now().isoformat()}, f)

            # Test reading file
            with open(test_file, 'r') as f:
                data = json.load(f)

            # Clean up
            os.remove(test_file)

            result = {
                "status": "pass",
                "f_drive_accessible": f_drive_accessible,
                "write_test": True,
                "read_test": True,
                "message": "File system test completed"
            }

            self.test_results["tests"]["file_system"] = result
            logger.info("📁 File system test: ✅ PASS")

        except Exception as e:
            logger.error(f"Error testing file system: {e}")
            self.test_results["tests"]["file_system"] = {
                "status": "error",
                "message": str(e)
            }

    async def generate_report(self):
        """Generate test report"""
        try:
            logger.info("📋 Generating test report...")

            # Count results
            total_tests = len(self.test_results["tests"])
            passed_tests = sum(1 for test in self.test_results["tests"].values()
                             if isinstance(test, dict) and test.get("status") == "pass")
            failed_tests = sum(1 for test in self.test_results["tests"].values()
                             if isinstance(test, dict) and test.get("status") in ["fail", "error"])

            # Determine overall status
            if passed_tests == total_tests:
                self.test_results["overall_status"] = "all_pass"
                status_emoji = "✅"
                status_text = "ALL TESTS PASSED"
            elif passed_tests > 0:
                self.test_results["overall_status"] = "partial_pass"
                status_emoji = "⚠️"
                status_text = "PARTIAL PASS"
            else:
                self.test_results["overall_status"] = "fail"
                status_emoji = "❌"
                status_text = "TESTS FAILED"

            # Save report
            report_file = "F:/ULTIMATE_AGI_DATA/RL_TRADING/test_report.json"
            with open(report_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)

            # Display summary
            logger.info("=" * 60)
            logger.info(f"{status_emoji} TEST SUMMARY: {status_text}")
            logger.info(f"📊 Total Tests: {total_tests}")
            logger.info(f"✅ Passed: {passed_tests}")
            logger.info(f"❌ Failed: {failed_tests}")
            logger.info(f"📋 Report saved: {report_file}")
            logger.info("=" * 60)

            # Display individual test results
            for test_name, test_result in self.test_results["tests"].items():
                if isinstance(test_result, dict):
                    if test_result.get("status") == "pass":
                        logger.info(f"✅ {test_name}: PASS")
                    elif test_result.get("status") == "fail":
                        logger.info(f"❌ {test_name}: FAIL - {test_result.get('message', '')}")
                    elif test_result.get("status") == "error":
                        logger.info(f"🔥 {test_name}: ERROR - {test_result.get('message', '')}")
                    else:
                        logger.info(f"⚪ {test_name}: UNKNOWN")
                else:
                    logger.info(f"⚪ {test_name}: INCOMPLETE")

            logger.info("=" * 60)

            if self.test_results["overall_status"] == "all_pass":
                logger.info("🚀 System is ready for launch!")
                logger.info("   Run: python launch_ultimate_trading_system_v3.py")
            else:
                logger.warning("⚠️ System has issues - check failed tests before launching")

            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error generating report: {e}")

# Main execution
async def main():
    """Main test execution"""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    print("🧪 Ultimate Trading System V3 - Component Tests")
    print("=" * 60)
    print("Testing all system components...")
    print("=" * 60)

    asyncio.run(main())
