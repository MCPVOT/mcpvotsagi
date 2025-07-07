#!/usr/bin/env python3
"""
Unified AGI System Status Check
==============================
Comprehensive status check for the unified dashboard system
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemCheck")

class UnifiedSystemChecker:
    """Comprehensive system checker for unified dashboard"""

    def __init__(self):
        self.base_url = "http://localhost:8900"
        self.components = {
            "jupiter": "/api/jupiter",
            "network": "/api/network",
            "system": "/api/system",
            "ai_analysis": "/api/ai-analysis",
            "status": "/api/status"
        }
        self.results = {}

    async def check_component(self, name, endpoint):
        """Check individual component status"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.results[name] = {
                    "status": "✅ ONLINE",
                    "response_time": f"{response.elapsed.total_seconds():.3f}s",
                    "data_points": len(data) if isinstance(data, (dict, list)) else 1,
                    "details": data
                }
                logger.info(f"✅ {name.upper()}: Online ({response.elapsed.total_seconds():.3f}s)")
                return True
            else:
                self.results[name] = {
                    "status": "❌ ERROR",
                    "error": f"HTTP {response.status_code}",
                    "response_time": f"{response.elapsed.total_seconds():.3f}s"
                }
                logger.error(f"❌ {name.upper()}: HTTP {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            self.results[name] = {
                "status": "🔴 OFFLINE",
                "error": "Connection refused - Dashboard not running?"
            }
            logger.error(f"🔴 {name.upper()}: Connection refused")
            return False
        except Exception as e:
            self.results[name] = {
                "status": "⚠️ UNKNOWN",
                "error": str(e)
            }
            logger.error(f"⚠️ {name.upper()}: {e}")
            return False

    async def check_all_components(self):
        """Check all components"""
        logger.info("🚀 Starting Unified AGI System Check...")
        logger.info("="*60)

        # Check main dashboard
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ DASHBOARD: Main interface accessible")
                dashboard_online = True
            else:
                logger.error("❌ DASHBOARD: Main interface not accessible")
                dashboard_online = False
        except:
            logger.error("🔴 DASHBOARD: Not running or not accessible")
            dashboard_online = False

        # Check all API endpoints
        tasks = []
        for name, endpoint in self.components.items():
            task = self.check_component(name, endpoint)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        online_count = sum(1 for r in results if r is True)

        return dashboard_online, online_count, len(self.components)

    def print_detailed_report(self):
        """Print detailed system report"""
        logger.info("\n" + "="*60)
        logger.info("📊 DETAILED SYSTEM REPORT")
        logger.info("="*60)

        for component, result in self.results.items():
            logger.info(f"\n🔍 {component.upper()} COMPONENT:")
            logger.info(f"   Status: {result['status']}")

            if 'response_time' in result:
                logger.info(f"   Response Time: {result['response_time']}")

            if 'data_points' in result:
                logger.info(f"   Data Points: {result['data_points']}")

            if 'error' in result:
                logger.info(f"   Error: {result['error']}")

            # Show sample data for successful components
            if result['status'] == "✅ ONLINE" and 'details' in result:
                details = result['details']
                if isinstance(details, dict):
                    sample_keys = list(details.keys())[:3]
                    logger.info(f"   Sample Keys: {sample_keys}")

                    # Show specific info for each component
                    if component == 'jupiter' and details:
                        for token, info in list(details.items())[:2]:
                            price = info.get('price', 0)
                            logger.info(f"   • Token Price: ${price:.4f}")

                    elif component == 'network':
                        bytes_sent = details.get('bytes_sent', 0)
                        bytes_recv = details.get('bytes_recv', 0)
                        logger.info(f"   • Network: {bytes_sent:,} sent, {bytes_recv:,} recv")

                    elif component == 'system':
                        cpu = details.get('cpu_percent', 0)
                        memory = details.get('memory_percent', 0)
                        logger.info(f"   • System: {cpu:.1f}% CPU, {memory:.1f}% Memory")

                    elif component == 'ai_analysis':
                        analysis = details.get('analysis', 'N/A')
                        if len(analysis) > 100:
                            analysis = analysis[:100] + "..."
                        logger.info(f"   • AI Analysis: {analysis}")

    def generate_system_summary(self, dashboard_online, online_count, total_count):
        """Generate system summary"""
        logger.info("\n" + "="*60)
        logger.info("🎯 UNIFIED AGI SYSTEM SUMMARY")
        logger.info("="*60)

        # Overall status
        if dashboard_online and online_count == total_count:
            status = "🟢 FULLY OPERATIONAL"
            health = "100%"
        elif dashboard_online and online_count > total_count / 2:
            status = "🟡 PARTIALLY OPERATIONAL"
            health = f"{(online_count/total_count)*100:.0f}%"
        else:
            status = "🔴 SYSTEM ISSUES"
            health = f"{(online_count/total_count)*100:.0f}%" if total_count > 0 else "0%"

        logger.info(f"📊 System Status: {status}")
        logger.info(f"🏥 System Health: {health}")
        logger.info(f"✅ Online Components: {online_count}/{total_count}")
        logger.info(f"🌐 Dashboard: {'✅ Online' if dashboard_online else '❌ Offline'}")

        # Architecture benefits
        logger.info("\n🏗️ UNIFIED ARCHITECTURE BENEFITS:")
        logger.info("   • Single process - reduced memory footprint")
        logger.info("   • Shared data layer - no synchronization issues")
        logger.info("   • Real-time WebSocket updates across all components")
        logger.info("   • Unified cyberpunk theme and user experience")
        logger.info("   • Claudia AI integration for enhanced analysis")

        # Component details
        logger.info("\n🔧 COMPONENT OVERVIEW:")
        logger.info("   📊 Jupiter DEX: Real-time price feeds and trading data")
        logger.info("   🌐 Network Monitor: Bandwidth and device tracking")
        logger.info("   ⚡ System Metrics: CPU, memory, and disk monitoring")
        logger.info("   🧠 AI Analysis: DeepSeek-R1 powered market analysis")
        logger.info("   🔌 WebSocket: Real-time updates to all connected clients")

        # Usage info
        logger.info("\n🚀 USAGE INFORMATION:")
        logger.info(f"   Dashboard URL: {self.base_url}")
        logger.info("   Features: Jupiter Trading + Network Monitoring + AI Analysis")
        logger.info("   Theme: Cyberpunk-inspired unified interface")
        logger.info("   Updates: Real-time WebSocket broadcasting")

        return status, health

async def main():
    """Main system check function"""
    checker = UnifiedSystemChecker()

    print("\n" + "="*80)
    print("🔍 UNIFIED AGI SYSTEM COMPREHENSIVE CHECK")
    print("="*80)
    print("🎯 Checking unified dashboard combining:")
    print("   • Jupiter DEX Trading")
    print("   • Network Monitoring")
    print("   • System Performance")
    print("   • Claudia AI Analysis")
    print("="*80)

    start_time = time.time()

    # Run comprehensive check
    dashboard_online, online_count, total_count = await checker.check_all_components()

    # Print detailed report
    checker.print_detailed_report()

    # Generate summary
    status, health = checker.generate_system_summary(dashboard_online, online_count, total_count)

    # Final summary
    elapsed_time = time.time() - start_time
    print("\n" + "="*80)
    print("🏁 SYSTEM CHECK COMPLETE")
    print("="*80)
    print(f"⏱️ Check Duration: {elapsed_time:.2f} seconds")
    print(f"📊 Final Status: {status}")
    print(f"🏥 System Health: {health}")

    if dashboard_online and online_count == total_count:
        print("\n✨ SYSTEM IS FULLY OPERATIONAL!")
        print("🌟 All components are working perfectly in unified architecture")
        print("🚀 Ready for production use!")
    elif dashboard_online:
        print("\n⚠️ SYSTEM HAS MINOR ISSUES")
        print("🔧 Some components may need attention")
        print("💡 Core functionality should still be available")
    else:
        print("\n🚨 SYSTEM REQUIRES ATTENTION")
        print("🔧 Dashboard is not running or accessible")
        print("💡 Start with: python unified_agi_dashboard.py")

    print("="*80)

    # Save results
    results_file = Path("system_check_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "dashboard_online": dashboard_online,
            "components_online": online_count,
            "total_components": total_count,
            "health_percentage": (online_count/total_count)*100 if total_count > 0 else 0,
            "status": status,
            "elapsed_time": elapsed_time,
            "component_details": checker.results
        }, f, indent=2)

    print(f"📄 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(main())
