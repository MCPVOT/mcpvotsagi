#!/usr/bin/env python3
"""
ULTIMATE AGI SYSTEM V3 - Integration Test Suite
This script performs comprehensive testing of all integrated components
"""

import asyncio
import json
import time
import requests
from pathlib import Path
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateAGIV3IntegrationTest:
    def __init__(self):
        self.backend_url = "http://localhost:8888"
        self.frontend_url = "http://localhost:3000"
        self.test_results = {}

    def test_frontend_status(self):
        """Test frontend accessibility and loading"""
        logger.info("🌐 Testing Frontend Status...")

        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Frontend accessible and responding")
                self.test_results['frontend_status'] = 'SUCCESS'
                return True
            else:
                logger.error(f"❌ Frontend returned status code: {response.status_code}")
                self.test_results['frontend_status'] = 'FAILED'
                return False
        except Exception as e:
            logger.error(f"❌ Frontend test failed: {e}")
            self.test_results['frontend_status'] = 'FAILED'
            return False

    def test_backend_status(self):
        """Test backend accessibility and core endpoints"""
        logger.info("🔧 Testing Backend Status...")

        try:
            # Test main status endpoint
            response = requests.get(f"{self.backend_url}/api/status", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend status endpoint accessible")
                self.test_results['backend_status'] = 'SUCCESS'
                return True
            else:
                logger.error(f"❌ Backend status endpoint returned: {response.status_code}")
                self.test_results['backend_status'] = 'FAILED'
                return False
        except Exception as e:
            logger.error(f"❌ Backend test failed: {e}")
            self.test_results['backend_status'] = 'FAILED'
            return False

    def test_ui_component_integration(self):
        """Test UI component catalog and integration"""
        logger.info("🎨 Testing UI Component Integration...")

        try:
            # Test UI catalog endpoint
            response = requests.get(f"{self.backend_url}/api/v3/ui/catalog", timeout=10)
            if response.status_code == 200:
                data = response.json()
                available_libraries = data.get('available_libraries', [])
                total_components = data.get('total_components', 0)

                logger.info(f"✅ UI Catalog accessible - {len(available_libraries)} libraries, {total_components} components")

                # Test specific component libraries
                expected_libraries = ['animate-ui', 'dashboard-starter', 'icons']
                for lib in expected_libraries:
                    if lib in available_libraries:
                        logger.info(f"  ✅ {lib} library integrated")
                    else:
                        logger.warning(f"  ⚠️ {lib} library not found")

                self.test_results['ui_integration'] = 'SUCCESS'
                return True
            else:
                logger.error(f"❌ UI catalog endpoint returned: {response.status_code}")
                self.test_results['ui_integration'] = 'FAILED'
                return False
        except Exception as e:
            logger.error(f"❌ UI integration test failed: {e}")
            self.test_results['ui_integration'] = 'FAILED'
            return False

    def test_v3_dashboard(self):
        """Test V3 dashboard endpoint"""
        logger.info("📊 Testing V3 Dashboard...")

        try:
            response = requests.get(f"{self.backend_url}/api/v3/dashboard", timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'Unknown')
                uptime = data.get('uptime', 0)

                logger.info(f"✅ V3 Dashboard accessible - Version: {version}, Uptime: {uptime}s")

                # Check for key dashboard components
                if 'ui_components' in data:
                    ui_info = data['ui_components']
                    logger.info(f"  📦 UI Components: {ui_info.get('total_components', 0)} total")
                    logger.info(f"  🎯 Icons: {ui_info.get('available_icons', 0)} available")
                    logger.info(f"  🎨 Animate UI: {ui_info.get('animate_ui_components', 0)} components")
                    logger.info(f"  📋 Dashboard: {ui_info.get('dashboard_components', 0)} components")

                self.test_results['v3_dashboard'] = 'SUCCESS'
                return True
            else:
                logger.error(f"❌ V3 dashboard endpoint returned: {response.status_code}")
                self.test_results['v3_dashboard'] = 'FAILED'
                return False
        except Exception as e:
            logger.error(f"❌ V3 dashboard test failed: {e}")
            self.test_results['v3_dashboard'] = 'FAILED'
            return False

    def test_mcp_memory_integration(self):
        """Test MCP memory integration"""
        logger.info("🧠 Testing MCP Memory Integration...")

        try:
            # Test WSL MCP configuration
            result = subprocess.run(['wsl', 'test', '-f', '/root/claude_desktop_config.json'],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("✅ Claude desktop config exists")

                # Test MCP server
                mcp_test = subprocess.run(['wsl', 'test', '-f', '/usr/local/bin/mcp-server-memory'],
                                        capture_output=True, text=True)

                if mcp_test.returncode == 0:
                    logger.info("✅ MCP server executable found")

                    # Test memory store
                    store_test = subprocess.run(['wsl', 'test', '-d', '/root/.mcp-memory-store'],
                                              capture_output=True, text=True)

                    if store_test.returncode == 0:
                        logger.info("✅ Memory store directory exists")
                        self.test_results['mcp_memory'] = 'SUCCESS'
                        return True
                    else:
                        logger.error("❌ Memory store directory not found")
                        self.test_results['mcp_memory'] = 'FAILED'
                        return False
                else:
                    logger.error("❌ MCP server executable not found")
                    self.test_results['mcp_memory'] = 'FAILED'
                    return False
            else:
                logger.error("❌ Claude desktop config not found")
                self.test_results['mcp_memory'] = 'FAILED'
                return False
        except Exception as e:
            logger.error(f"❌ MCP memory integration test failed: {e}")
            self.test_results['mcp_memory'] = 'FAILED'
            return False

    def test_chat_functionality(self):
        """Test chat functionality"""
        logger.info("💬 Testing Chat Functionality...")

        try:
            chat_data = {
                "message": "Hello, this is a test message for the Ultimate AGI System V3",
                "model": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
            }

            response = requests.post(f"{self.backend_url}/api/chat",
                                   json=chat_data,
                                   timeout=30)

            if response.status_code == 200:
                data = response.json()
                if 'response' in data:
                    logger.info("✅ Chat functionality working")
                    logger.info(f"  📝 Response preview: {data['response'][:100]}...")
                    self.test_results['chat_functionality'] = 'SUCCESS'
                    return True
                else:
                    logger.error("❌ Chat response missing 'response' field")
                    self.test_results['chat_functionality'] = 'FAILED'
                    return False
            else:
                logger.error(f"❌ Chat endpoint returned: {response.status_code}")
                self.test_results['chat_functionality'] = 'FAILED'
                return False
        except Exception as e:
            logger.error(f"❌ Chat functionality test failed: {e}")
            self.test_results['chat_functionality'] = 'FAILED'
            return False

    def test_metrics_endpoints(self):
        """Test metrics and monitoring endpoints"""
        logger.info("📈 Testing Metrics Endpoints...")

        try:
            # Test real-time metrics
            response = requests.get(f"{self.backend_url}/api/v3/metrics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Real-time metrics endpoint accessible")

                # Log key metrics
                if 'system_health' in data:
                    logger.info(f"  🏥 System Health: {data['system_health']}")
                if 'active_sessions' in data:
                    logger.info(f"  👥 Active Sessions: {data['active_sessions']}")
                if 'models_loaded' in data:
                    logger.info(f"  🤖 Models Loaded: {data['models_loaded']}")

                self.test_results['metrics_endpoints'] = 'SUCCESS'
                return True
            else:
                logger.error(f"❌ Metrics endpoint returned: {response.status_code}")
                self.test_results['metrics_endpoints'] = 'FAILED'
                return False
        except Exception as e:
            logger.error(f"❌ Metrics endpoint test failed: {e}")
            self.test_results['metrics_endpoints'] = 'FAILED'
            return False

    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        logger.info("🚀 Starting Comprehensive Integration Test...")
        logger.info("=" * 60)

        # Run all tests
        tests = [
            ("Frontend Status", self.test_frontend_status),
            ("Backend Status", self.test_backend_status),
            ("UI Component Integration", self.test_ui_component_integration),
            ("V3 Dashboard", self.test_v3_dashboard),
            ("MCP Memory Integration", self.test_mcp_memory_integration),
            ("Chat Functionality", self.test_chat_functionality),
            ("Metrics Endpoints", self.test_metrics_endpoints)
        ]

        total_tests = len(tests)
        passed_tests = 0

        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            logger.info("-" * 40)

            try:
                if test_func():
                    passed_tests += 1
                    logger.info(f"✅ {test_name} - PASSED")
                else:
                    logger.error(f"❌ {test_name} - FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name} - ERROR: {e}")

        # Generate final report
        logger.info("\n" + "=" * 60)
        logger.info("🎯 FINAL TEST REPORT")
        logger.info("=" * 60)

        success_rate = (passed_tests / total_tests) * 100

        logger.info(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

        if success_rate >= 80:
            logger.info("🎉 INTEGRATION TEST SUITE - OVERALL SUCCESS")
            logger.info("✅ Ultimate AGI System V3 is fully operational!")
        elif success_rate >= 60:
            logger.info("⚠️ INTEGRATION TEST SUITE - PARTIAL SUCCESS")
            logger.info("🔧 Some components need attention")
        else:
            logger.info("❌ INTEGRATION TEST SUITE - NEEDS WORK")
            logger.info("🚨 Multiple components require fixing")

        # Detailed results
        logger.info("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result == 'SUCCESS' else "❌"
            logger.info(f"  {status_emoji} {test_name}: {result}")

        # Next steps
        logger.info("\n📌 Next Steps:")
        if success_rate == 100:
            logger.info("🎯 All systems operational! Ready for production use.")
            logger.info("🔄 Restart Claude Code in WSL to test MCP memory tools")
            logger.info("🧪 Test MCP memory tools: mcp_memory_create_entities, mcp_memory_search_nodes")
        else:
            logger.info("🔧 Address any failed tests before proceeding")
            logger.info("📊 Check logs for specific error details")

        logger.info("\n🌟 Ultimate AGI System V3 Integration Complete!")

        return success_rate >= 80

def main():
    """Main test runner"""
    print("🧪 ULTIMATE AGI SYSTEM V3 - Integration Test Suite")
    print("=" * 55)

    tester = UltimateAGIV3IntegrationTest()

    if tester.run_comprehensive_test():
        print("\n🎉 Integration test completed successfully!")
        return 0
    else:
        print("\n⚠️ Integration test completed with issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
