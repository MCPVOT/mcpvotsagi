#!/usr/bin/env python3
"""
Production Hierarchical Agent System
===================================
DeepSeek streams and analyzes data → Claude Opus 4 makes executive decisions
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
# typing: use built-in list

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from hierarchical_agent_system import HierarchicalAgentSystem
from src.core.CONTEXT7_INTEGRATION import Context7Integration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProductionHierarchicalSystem")

class ProductionAgentOrchestrator:
    """Production orchestrator for hierarchical agent system"""

    def __init__(self):
        self.hierarchical_system = HierarchicalAgentSystem()
        self.running = False
        self.mission_counter = 0

    async def start_production_system(self):
        """Start the production hierarchical agent system"""
        logger.info("🚀 Starting Production Hierarchical Agent System...")

        # Initialize all components
        await self.hierarchical_system.start_system()
        self.running = True

        # Start continuous operations
        asyncio.create_task(self.continuous_data_analysis())
        asyncio.create_task(self.periodic_executive_decisions())
        asyncio.create_task(self.system_health_monitor())

        logger.info("✅ Production system operational")

    async def continuous_data_analysis(self):
        """Continuous data analysis with DeepSeek"""
        logger.info("📊 Starting continuous data analysis (DeepSeek)")

        while self.running:
            try:
                # Process multiple data streams
                await self.hierarchical_system.process_data_streams()

                # Log analysis progress
                status = await self.hierarchical_system.get_system_status()
                logger.info(f"📈 Analyses: {status['analysis_results']}, Decisions: {status['executive_decisions']}")

                await asyncio.sleep(10)  # Analyze every 10 seconds

            except Exception as e:
                logger.error(f"Error in continuous analysis: {e}")
                await asyncio.sleep(30)

    async def periodic_executive_decisions(self):
        """Periodic executive decision making with Claude Opus 4"""
        logger.info("🎯 Starting executive decision cycles (Claude Opus 4)")

        while self.running:
            try:
                # Deploy strategic missions every 60 seconds
                await asyncio.sleep(60)

                self.mission_counter += 1
                mission_name = f"Strategic_Mission_{self.mission_counter:03d}"

                logger.info(f"🚀 Deploying {mission_name}")

                # Deploy multi-target mission
                mission_result = await self.hierarchical_system.deploy_coordinated_mission(
                    mission_name,
                    [
                        "market_trends",
                        "system_performance",
                        "user_engagement",
                        "resource_utilization",
                        "competitive_analysis"
                    ]
                )

                logger.info(f"✅ {mission_name} completed with {mission_result['success_rate']}% success")

            except Exception as e:
                logger.error(f"Error in executive decisions: {e}")
                await asyncio.sleep(60)

    async def system_health_monitor(self):
        """Monitor system health and performance"""
        logger.info("🏥 Starting system health monitoring")

        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                status = await self.hierarchical_system.get_system_status()

                # Log comprehensive status
                logger.info("🔍 System Health Check:")
                logger.info(f"   DeepSeek Agent: {status['deepseek_agent_status']}")
                logger.info(f"   Claude Opus 4: {status['claude_opus_4_status']}")
                logger.info(f"   Context7: {'✅ Connected' if status['context7_connected'] else '❌ Disconnected'}")
                logger.info(f"   Analyses: {status['analysis_results']}")
                logger.info(f"   Decisions: {status['executive_decisions']}")

                # Health warnings
                if not status['context7_connected']:
                    logger.warning("⚠️ Context7 disconnected - documentation enrichment unavailable")

                if status['deepseek_agent_status'] != 'ACTIVE':
                    logger.warning("⚠️ DeepSeek agent not active - using fallback analysis")

            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)

    async def execute_emergency_protocol(self, emergency_type: str, severity: int):
        """Execute emergency decision protocol"""
        logger.warning(f"🚨 EMERGENCY PROTOCOL: {emergency_type} (Severity: {severity})")

        emergency_mission = await self.hierarchical_system.deploy_coordinated_mission(
            f"EMERGENCY_{emergency_type}_{datetime.now().strftime('%H%M%S')}",
            ["emergency_assessment", "risk_analysis", "mitigation_strategy"]
        )

        logger.info(f"🚑 Emergency mission completed: {emergency_mission['mission_id']}")
        return emergency_mission

    async def demonstrate_hierarchical_flow(self):
        """Demonstrate the complete hierarchical decision flow"""
        logger.info("🎬 DEMONSTRATING HIERARCHICAL DECISION FLOW")
        logger.info("=" * 60)

        # Step 1: Data Stream Analysis (DeepSeek)
        logger.info("📊 STEP 1: DeepSeek Data Stream Analysis")
        logger.info("   → Processing financial, performance, and user data")
        await self.hierarchical_system.process_data_streams()

        await asyncio.sleep(2)

        # Step 2: Executive Decision Making (Claude Opus 4)
        logger.info("🎯 STEP 2: Claude Opus 4 Executive Decision Making")
        logger.info("   → Analyzing DeepSeek insights for strategic decisions")

        mission = await self.hierarchical_system.deploy_coordinated_mission(
            "DEMO_Strategic_Analysis",
            ["market_analysis", "performance_optimization", "user_experience"]
        )

        await asyncio.sleep(2)

        # Step 3: Results Summary
        logger.info("📋 STEP 3: Decision Flow Results")
        status = await self.hierarchical_system.get_system_status()

        logger.info(f"   ✅ DeepSeek Analyses: {status['analysis_results']}")
        logger.info(f"   ✅ Claude Decisions: {status['executive_decisions']}")
        logger.info(f"   ✅ Mission Success Rate: {mission['success_rate']}%")
        logger.info(f"   ✅ Total Insights: {mission['total_insights']}")

        logger.info("🎉 HIERARCHICAL DECISION FLOW COMPLETE")
        logger.info("=" * 60)

        return mission

    async def stop_system(self):
        """Gracefully stop the production system"""
        logger.info("🛑 Stopping production system...")
        self.running = False

        # Close Context7 connections
        await self.hierarchical_system.context7.close_session()
        await self.hierarchical_system.context7.stop_server()

        logger.info("✅ Production system stopped")

async def main():
    """Run the production hierarchical agent system"""
    print("🧠 PRODUCTION HIERARCHICAL AGENT SYSTEM")
    print("=" * 60)
    print("🔄 Data Flow: DeepSeek Analysis → Claude Opus 4 Decisions → Execution")
    print("=" * 60)

    orchestrator = ProductionAgentOrchestrator()

    try:
        # Start the production system
        await orchestrator.start_production_system()

        # Demonstrate the hierarchical flow
        demo_result = await orchestrator.demonstrate_hierarchical_flow()

        print("\n🎯 PRODUCTION DEMONSTRATION COMPLETE")
        print(f"✅ Mission ID: {demo_result['mission_id']}")
        print(f"📊 DeepSeek Analyses: {demo_result['deepseek_analyses']}")
        print(f"🎯 Claude Decisions: {demo_result['claude_decisions']}")
        print(f"⚡ Executions: {demo_result['executions']}")
        print(f"🎉 Success Rate: {demo_result['success_rate']}%")

        # Show system status
        status = await orchestrator.hierarchical_system.get_system_status()
        print(f"\n📋 SYSTEM STATUS:")
        print(f"   🧠 DeepSeek Agent: {status['deepseek_agent_status']}")
        print(f"   💼 Claude Opus 4: {status['claude_opus_4_status']}")
        print(f"   📚 Context7: {'✅ Connected' if status['context7_connected'] else '❌ Disconnected'}")
        print(f"   📈 Total Analyses: {status['analysis_results']}")
        print(f"   🎯 Total Decisions: {status['executive_decisions']}")

        # Optional: Run for extended period
        print("\n🔄 System ready for extended operation...")
        print("   (Press Ctrl+C to stop)")

        # Keep running until interrupted
        while True:
            await asyncio.sleep(60)
            status = await orchestrator.hierarchical_system.get_system_status()
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Analyses: {status['analysis_results']}, Decisions: {status['executive_decisions']}")

    except KeyboardInterrupt:
        print("\n⏹️ Stopping system...")
        await orchestrator.stop_system()
        print("✅ System stopped gracefully")

    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        await orchestrator.stop_system()

if __name__ == "__main__":
    asyncio.run(main())
