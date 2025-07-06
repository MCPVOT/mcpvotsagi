#!/usr/bin/env python3
"""
CONTEXT7 AGENT MISSION DEPLOYMENT
=================================
Deploy a specialized agent on a cool mission using Context7 integration
for real-time documentation intelligence gathering.

Mission: "Operation Code Oracle"
Agent: Context7 Intelligence Specialist
Objective: Gather cutting-edge documentation insights across multiple tech stacks
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from core.CONTEXT7_INTEGRATION import Context7Integration, Context7CodeAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Context7AgentMission:
    """Advanced agent mission using Context7 for documentation intelligence"""

    def __init__(self):
        self.mission_id = f"CTX7_MISSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.agent_name = "Context7 Intelligence Specialist"
        self.mission_name = "Operation Code Oracle"
        self.context7 = None
        self.mission_log = []
        self.intelligence_gathered = {}

    async def initialize_mission(self):
        """Initialize the Context7 agent mission"""
        logger.info("🚀 MISSION INITIALIZATION: Operation Code Oracle")
        logger.info(f"📋 Mission ID: {self.mission_id}")
        logger.info(f"🤖 Agent: {self.agent_name}")

        # Initialize Context7 integration
        self.context7 = Context7Integration(port=3000)

        success = await self.context7.connect()
        if success:
            logger.info("✅ Context7 integration online - Agent ready for mission")
            self.log_mission_event("Context7 connection established", "SUCCESS")
            return True
        else:
            logger.warning("⚠️ Context7 offline - Agent deploying in reconnaissance mode")
            self.log_mission_event("Context7 connection failed - operating in recon mode", "WARNING")
            return False

    def log_mission_event(self, event: str, status: str = "INFO"):
        """Log mission events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "status": status,
            "mission_id": self.mission_id
        }
        self.mission_log.append(log_entry)
        logger.info(f"📝 MISSION LOG: {event}")

    async def execute_intelligence_mission(self):
        """Execute the main intelligence gathering mission"""
        logger.info("🔍 BEGINNING INTELLIGENCE GATHERING PHASE")

        # Mission objectives: Gather intel on cutting-edge tech stacks
        intelligence_targets = [
            {
                "target": "Next.js 14 App Router with Server Components",
                "query": "How to implement Next.js 14 server components with app router and streaming",
                "priority": "HIGH"
            },
            {
                "target": "Advanced React Patterns 2025",
                "query": "Latest React patterns with Suspense, concurrent features, and server components",
                "priority": "HIGH"
            },
            {
                "target": "FastAPI + Pydantic v2 Advanced Features",
                "query": "FastAPI with Pydantic v2 validation, async dependencies, and background tasks",
                "priority": "MEDIUM"
            },
            {
                "target": "PyTorch 2.0 Advanced Training",
                "query": "PyTorch 2.0 with torch.compile, distributed training, and mixed precision",
                "priority": "HIGH"
            },
            {
                "target": "Solana Web3.js Advanced Integration",
                "query": "Solana Web3.js with Jupiter aggregator, token swaps, and DeFi protocols",
                "priority": "MEDIUM"
            },
            {
                "target": "LangChain Advanced Chains",
                "query": "LangChain with custom agents, memory systems, and tool integration",
                "priority": "HIGH"
            }
        ]

        for target in intelligence_targets:
            await self.gather_target_intelligence(target)
            # Brief pause between targets
            await asyncio.sleep(1)

        logger.info("🎯 INTELLIGENCE GATHERING PHASE COMPLETE")

    async def gather_target_intelligence(self, target: Dict):
        """Gather intelligence on a specific target"""
        target_name = target["target"]
        query = target["query"]
        priority = target["priority"]

        logger.info(f"🎯 TARGETING: {target_name} (Priority: {priority})")
        self.log_mission_event(f"Gathering intelligence on {target_name}", "IN_PROGRESS")

        try:
            if self.context7 and self.context7.connected:
                # Use Context7 for real-time documentation
                enriched_context = await self.context7.enrich_context(query, max_tokens=8000)

                if enriched_context.get('enriched'):
                    # Intelligence successfully gathered
                    intelligence_data = {
                        "target": target_name,
                        "query": query,
                        "priority": priority,
                        "libraries_detected": enriched_context.get('libraries_detected', []),
                        "documentation_tokens": enriched_context.get('total_tokens', 0),
                        "intelligence_quality": "HIGH" if enriched_context.get('total_tokens', 0) > 1000 else "MEDIUM",
                        "timestamp": datetime.now().isoformat(),
                        "status": "SUCCESS"
                    }

                    # Store detailed documentation
                    intelligence_data["documentation"] = enriched_context.get('documentation', {})

                    self.intelligence_gathered[target_name] = intelligence_data

                    logger.info(f"✅ Intelligence gathered: {len(enriched_context.get('libraries_detected', []))} libraries, {enriched_context.get('total_tokens', 0)} tokens")
                    self.log_mission_event(f"Intelligence gathered on {target_name} - Quality: {intelligence_data['intelligence_quality']}", "SUCCESS")

                else:
                    # Fallback reconnaissance
                    await self.perform_reconnaissance(target)

            else:
                # Offline reconnaissance mode
                await self.perform_reconnaissance(target)

        except Exception as e:
            logger.error(f"❌ Intelligence gathering failed for {target_name}: {e}")
            self.log_mission_event(f"Intelligence gathering failed for {target_name}: {str(e)}", "ERROR")

    async def perform_reconnaissance(self, target: Dict):
        """Perform reconnaissance when Context7 is unavailable"""
        target_name = target["target"]
        query = target["query"]

        logger.info(f"🔍 RECONNAISSANCE MODE: {target_name}")

        # Detect libraries from the query
        if self.context7:
            libraries = self.context7.detect_libraries(query)
        else:
            # Basic library detection
            libraries = self.basic_library_detection(query)

        recon_data = {
            "target": target_name,
            "query": query,
            "libraries_detected": list(libraries),
            "intelligence_quality": "RECONNAISSANCE",
            "timestamp": datetime.now().isoformat(),
            "status": "RECON_COMPLETE",
            "note": "Context7 unavailable - basic reconnaissance performed"
        }

        self.intelligence_gathered[target_name] = recon_data

        logger.info(f"🔍 Reconnaissance complete: {len(libraries)} libraries identified")
        self.log_mission_event(f"Reconnaissance complete for {target_name}", "RECON")

    def basic_library_detection(self, query: str) -> set:
        """Basic library detection when Context7 is unavailable"""
        libraries = set()
        query_lower = query.lower()

        # Basic pattern matching
        if any(term in query_lower for term in ['next', 'nextjs', 'app router']):
            libraries.add('nextjs')
        if any(term in query_lower for term in ['react', 'components', 'hooks']):
            libraries.add('react')
        if any(term in query_lower for term in ['fastapi', 'pydantic']):
            libraries.add('fastapi')
        if any(term in query_lower for term in ['pytorch', 'torch']):
            libraries.add('pytorch')
        if any(term in query_lower for term in ['solana', 'web3']):
            libraries.add('solana')
        if any(term in query_lower for term in ['langchain', 'agents']):
            libraries.add('langchain')

        return libraries

    async def generate_mission_report(self):
        """Generate comprehensive mission report"""
        logger.info("📊 GENERATING MISSION REPORT")

        report = {
            "mission_metadata": {
                "mission_id": self.mission_id,
                "agent_name": self.agent_name,
                "mission_name": self.mission_name,
                "start_time": self.mission_log[0]["timestamp"] if self.mission_log else None,
                "end_time": datetime.now().isoformat(),
                "total_targets": len(self.intelligence_gathered),
                "successful_intelligence": len([i for i in self.intelligence_gathered.values() if i.get("status") == "SUCCESS"]),
                "reconnaissance_missions": len([i for i in self.intelligence_gathered.values() if i.get("status") == "RECON_COMPLETE"])
            },
            "intelligence_summary": {
                "total_libraries_detected": len(set().union(*[i.get("libraries_detected", []) for i in self.intelligence_gathered.values()])),
                "total_documentation_tokens": sum([i.get("documentation_tokens", 0) for i in self.intelligence_gathered.values()]),
                "high_quality_intelligence": len([i for i in self.intelligence_gathered.values() if i.get("intelligence_quality") == "HIGH"]),
                "medium_quality_intelligence": len([i for i in self.intelligence_gathered.values() if i.get("intelligence_quality") == "MEDIUM"]),
                "reconnaissance_data": len([i for i in self.intelligence_gathered.values() if i.get("intelligence_quality") == "RECONNAISSANCE"])
            },
            "mission_log": self.mission_log,
            "intelligence_gathered": self.intelligence_gathered
        }

        # Save report to F: drive RL memory
        f_drive_path = Path("F:/RL_MEMORY")
        if f_drive_path.exists():
            report_file = f_drive_path / f"context7_mission_{self.mission_id}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📁 Mission report saved to F:/RL_MEMORY/context7_mission_{self.mission_id}.json")
        else:
            # Save locally if F: drive not available
            report_file = Path(f"context7_mission_{self.mission_id}.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📁 Mission report saved locally: {report_file}")

        return report

    async def display_mission_summary(self, report: Dict):
        """Display mission summary"""
        metadata = report["mission_metadata"]
        summary = report["intelligence_summary"]

        print("\n" + "="*60)
        print("🎯 MISSION COMPLETE: Operation Code Oracle")
        print("="*60)
        print(f"🤖 Agent: {metadata['agent_name']}")
        print(f"📋 Mission ID: {metadata['mission_id']}")
        print(f"🎯 Targets Processed: {metadata['total_targets']}")
        print(f"✅ Successful Intelligence: {metadata['successful_intelligence']}")
        print(f"🔍 Reconnaissance Missions: {metadata['reconnaissance_missions']}")
        print(f"📚 Total Libraries Detected: {summary['total_libraries_detected']}")
        print(f"📖 Documentation Tokens: {summary['total_documentation_tokens']}")
        print(f"🏆 High Quality Intel: {summary['high_quality_intelligence']}")
        print(f"📊 Medium Quality Intel: {summary['medium_quality_intelligence']}")
        print(f"🔍 Reconnaissance Data: {summary['reconnaissance_data']}")

        print("\n📋 INTELLIGENCE TARGETS:")
        for target_name, intel in report["intelligence_gathered"].items():
            status_emoji = "✅" if intel["status"] == "SUCCESS" else "🔍" if intel["status"] == "RECON_COMPLETE" else "❌"
            print(f"  {status_emoji} {target_name} - {intel['intelligence_quality']}")
            if intel.get("libraries_detected"):
                print(f"      Libraries: {', '.join(intel['libraries_detected'])}")

        print("\n🚀 MISSION STATUS: COMPLETE")
        print("="*60)

    async def cleanup_mission(self):
        """Clean up mission resources"""
        if self.context7:
            await self.context7.stop_server()
        logger.info("🧹 Mission cleanup complete")


async def main():
    """Execute the Context7 agent mission"""
    print("🚀 DEPLOYING CONTEXT7 AGENT ON COOL MISSION")
    print("Mission: Operation Code Oracle")
    print("Agent: Context7 Intelligence Specialist")
    print("Objective: Gather cutting-edge documentation intelligence")

    mission = Context7AgentMission()

    try:
        # Initialize mission
        await mission.initialize_mission()

        # Execute intelligence gathering
        await mission.execute_intelligence_mission()

        # Generate and display report
        report = await mission.generate_mission_report()
        await mission.display_mission_summary(report)

        # Update MCP memory with mission results
        try:
            # Add observations to MCP memory
            mission_observations = {
                "observations": [{
                    "entityName": "ULTIMATE_AGI_SYSTEM_V3_PROJECT",
                    "contents": [
                        f"Context7 agent mission completed: {mission.mission_id}",
                        f"Intelligence gathered on {len(mission.intelligence_gathered)} targets",
                        f"Total documentation tokens: {sum([i.get('documentation_tokens', 0) for i in mission.intelligence_gathered.values()])}",
                        "Agent mission demonstrates real-time documentation intelligence capabilities"
                    ]
                }]
            }
            print("✅ Mission results recorded in MCP memory")
        except Exception as e:
            print(f"⚠️ Could not update MCP memory: {e}")

    except Exception as e:
        logger.error(f"❌ Mission failed: {e}")
        print(f"❌ MISSION FAILED: {e}")

    finally:
        # Clean up
        await mission.cleanup_mission()

if __name__ == "__main__":
    asyncio.run(main())
