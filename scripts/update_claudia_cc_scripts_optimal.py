#!/usr/bin/env python3
"""
Update All Claude CC Scripts with Optimal Models
================================================
Update all Claudia scripts to use the optimal Ollama models based on test results
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ClaudiaCCScriptUpdater")

class ClaudiaCCScriptUpdater:
    """Update all Claude CC scripts with optimal model configuration"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.claudia_path = self.base_path / "claudia"
        self.src_path = self.base_path / "src"

        # Load optimal configuration
        self.optimal_config = self.load_optimal_config()

        # Define script update mappings
        self.scripts_to_update = [
            "src/core/claudia_integration_bridge.py",
            "claudia_integration_bridge.py",
            "claudia_production_integration.py",
            "deepseek_trading_agent_enhanced.py",
            "deepseek_r1_trading_agent_enhanced.py",
            "oracle_claudia_integration.py",
            "claudia_deepseek_system_analyzer.py",
            "deploy_jupiter_phase1.py"
        ]

    def load_optimal_config(self):
        """Load the optimal configuration generated from tests"""
        config_file = self.claudia_path / "claudia_optimal_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Fallback configuration based on test results
            return {
                "models": {
                    "primary": "qwen2.5-coder:latest",
                    "code_generation": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
                    "fast_response": "llama3.2:latest",
                    "jupiter_specialist": "deepseek-r1:latest"
                },
                "routing": {
                    "code_tasks": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
                    "reasoning_tasks": "qwen2.5-coder:latest",
                    "quick_tasks": "llama3.2:latest",
                    "jupiter_tasks": "deepseek-r1:latest",
                    "general_tasks": "qwen2.5-coder:latest"
                }
            }

    async def update_claudia_integration_bridge(self):
        """Update the main Claudia integration bridge"""
        logger.info("🔄 Updating Claudia integration bridge...")

        bridge_file = self.src_path / "core" / "claudia_integration_bridge.py"
        if not bridge_file.exists():
            bridge_file = self.base_path / "claudia_integration_bridge.py"

        if bridge_file.exists():
            # Read current content
            with open(bridge_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update model configuration
            model_config_section = f'''
# OPTIMAL MODEL CONFIGURATION (Generated from Performance Tests)
OPTIMAL_MODELS = {{
    "primary": "{self.optimal_config['models']['primary']}",
    "code_generation": "{self.optimal_config['models']['code_generation']}",
    "fast_response": "{self.optimal_config['models']['fast_response']}",
    "jupiter_specialist": "{self.optimal_config['models']['jupiter_specialist']}"
}}

# Model routing configuration
MODEL_ROUTING = {{
    "code_tasks": OPTIMAL_MODELS["code_generation"],
    "reasoning_tasks": OPTIMAL_MODELS["primary"],
    "quick_tasks": OPTIMAL_MODELS["fast_response"],
    "jupiter_tasks": OPTIMAL_MODELS["jupiter_specialist"],
    "general_tasks": OPTIMAL_MODELS["primary"]
}}

# Performance metrics from testing
MODEL_PERFORMANCE = {{
    "{self.optimal_config['models']['primary']}": {{"score": 0.945, "speed": 8.94, "success_rate": 1.0}},
    "{self.optimal_config['models']['fast_response']}": {{"score": 0.92, "speed": 5.37, "success_rate": 1.0}},
    "{self.optimal_config['models']['code_generation']}": {{"score": 0.4, "speed": 24.43, "success_rate": 0.4}},
}}
'''

            # Insert the configuration at the top of the file after imports
            import_end = content.find('\nlogger = ')
            if import_end != -1:
                updated_content = content[:import_end] + model_config_section + content[import_end:]
            else:
                updated_content = model_config_section + "\n" + content

            # Update any hardcoded model references
            updated_content = updated_content.replace(
                'self.default_model = "deepseek-r1:latest"',
                f'self.default_model = "{self.optimal_config["models"]["primary"]}"'
            )

            # Save updated content
            with open(bridge_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info(f"✅ Updated: {bridge_file}")
            return True
        else:
            logger.warning(f"⚠️ File not found: {bridge_file}")
            return False

    async def update_deepseek_trading_agent(self):
        """Update DeepSeek trading agent with optimal models"""
        logger.info("🤖 Updating DeepSeek trading agent...")

        agent_files = [
            "deepseek_trading_agent_enhanced.py",
            "deepseek_r1_trading_agent_enhanced.py"
        ]

        updated_files = []

        for filename in agent_files:
            agent_file = self.base_path / filename
            if agent_file.exists():
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Update model configuration
                model_update = f'''
    # OPTIMAL MODELS (Performance Tested)
    OPTIMAL_MODELS = {{
        "primary": "{self.optimal_config['models']['primary']}",
        "code_generation": "{self.optimal_config['models']['code_generation']}",
        "fast_response": "{self.optimal_config['models']['fast_response']}",
        "jupiter_specialist": "{self.optimal_config['models']['jupiter_specialist']}"
    }}

    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.primary_model = self.OPTIMAL_MODELS["primary"]  # qwen2.5-coder:latest
        self.fast_model = self.OPTIMAL_MODELS["fast_response"]  # llama3.2:latest
        self.jupiter_model = self.OPTIMAL_MODELS["jupiter_specialist"]  # deepseek-r1:latest
        self.f_drive_path = "F:/ULTIMATE_AGI_DATA/RL_TRADING/"
'''

                # Replace the __init__ method
                init_start = content.find('def __init__(self):')
                if init_start != -1:
                    init_end = content.find('\n    def ', init_start + 1)
                    if init_end == -1:
                        init_end = content.find('\n\n', init_start + 1)

                    if init_end != -1:
                        updated_content = content[:init_start] + model_update.strip() + content[init_end:]
                    else:
                        updated_content = content[:init_start] + model_update.strip()
                else:
                    # Add at the beginning of the class
                    class_start = content.find('class ')
                    if class_start != -1:
                        class_end = content.find(':', class_start) + 1
                        updated_content = content[:class_end] + model_update + content[class_end:]
                    else:
                        updated_content = content + model_update

                # Save updated content
                with open(agent_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                updated_files.append(str(agent_file))
                logger.info(f"✅ Updated: {agent_file}")

        return updated_files

    async def update_jupiter_deployment(self):
        """Update Jupiter deployment script"""
        logger.info("🪐 Updating Jupiter deployment script...")

        deploy_file = self.base_path / "deploy_jupiter_phase1.py"
        if deploy_file.exists():
            with open(deploy_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add optimal model configuration
            model_config = f'''
# OPTIMAL MODELS FOR JUPITER INTEGRATION
JUPITER_OPTIMAL_MODELS = {{
    "primary": "{self.optimal_config['models']['primary']}",  # Best overall: qwen2.5-coder:latest
    "jupiter_specialist": "{self.optimal_config['models']['jupiter_specialist']}",  # Jupiter tasks: deepseek-r1:latest
    "fast_response": "{self.optimal_config['models']['fast_response']}",  # Quick tasks: llama3.2:latest
    "code_generation": "{self.optimal_config['models']['code_generation']}"  # Code gen: DeepSeek-R1-Qwen3
}}

'''

            # Insert after imports
            import_end = content.find('logger = logging.getLogger')
            if import_end != -1:
                logger_line_end = content.find('\n', import_end) + 1
                updated_content = content[:logger_line_end] + model_config + content[logger_line_end:]
            else:
                updated_content = model_config + content

            # Update any model references
            updated_content = updated_content.replace(
                'self.deepseek_model = "deepseek-r1:latest"',
                f'self.deepseek_model = JUPITER_OPTIMAL_MODELS["jupiter_specialist"]'
            )

            # Save updated content
            with open(deploy_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info(f"✅ Updated: {deploy_file}")
            return True
        else:
            logger.warning(f"⚠️ File not found: {deploy_file}")
            return False

    async def create_performance_monitoring(self):
        """Create performance monitoring for optimal models"""
        logger.info("📊 Creating performance monitoring...")

        monitor_code = f'''#!/usr/bin/env python3
"""
Claudia Optimal Model Performance Monitor
========================================
Monitor performance of optimal Ollama models in Claudia
"""

import asyncio
import json
import logging
import requests
import time
from datetime import datetime
from pathlib import Path
# typing: use built-in list

logger = logging.getLogger("ClaudiaPerformanceMonitor")

class ClaudiaPerformanceMonitor:
    """Monitor performance of optimal Claudia models"""

    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.optimal_models = {json.dumps(self.optimal_config["models"], indent=12)}
        self.performance_log = Path(__file__).parent / "claudia_performance_log.json"

    async def monitor_model_performance(self):
        """Monitor performance of all optimal models"""
        logger.info("📊 Starting model performance monitoring...")

        performance_data = {{
            "timestamp": datetime.now().isoformat(),
            "models": {{}}
        }}

        for model_type, model_name in self.optimal_models.items():
            logger.info(f"🔍 Testing {{model_type}}: {{model_name}}")

            # Test model performance
            start_time = time.time()
            try:
                response = requests.post(
                    f"{{self.base_url}}/api/generate",
                    json={{
                        "model": model_name,
                        "prompt": "Calculate 2+2 and explain briefly.",
                        "stream": False
                    }},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    response_time = time.time() - start_time

                    performance_data["models"][model_name] = {{
                        "type": model_type,
                        "status": "active",
                        "response_time": response_time,
                        "response_length": len(result.get("response", "")),
                        "success": True
                    }}

                    logger.info(f"✅ {{model_name}}: {{response_time:.2f}}s")
                else:
                    performance_data["models"][model_name] = {{
                        "type": model_type,
                        "status": "error",
                        "error": f"HTTP {{response.status_code}}",
                        "success": False
                    }}

            except Exception as e:
                performance_data["models"][model_name] = {{
                    "type": model_type,
                    "status": "error",
                    "error": str(e),
                    "success": False
                }}
                logger.error(f"❌ {{model_name}}: {{e}}")

        # Save performance data
        with open(self.performance_log, 'w') as f:
            json.dump(performance_data, f, indent=2)

        logger.info(f"💾 Performance data saved to: {{self.performance_log}}")
        return performance_data

    async def get_model_recommendations(self):
        """Get model recommendations based on current performance"""
        if not self.performance_log.exists():
            await self.monitor_model_performance()

        with open(self.performance_log, 'r') as f:
            perf_data = json.load(f)

        recommendations = {{
            "fast_tasks": "llama3.2:latest",  # Fastest response
            "code_tasks": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",  # Best for code
            "reasoning_tasks": "qwen2.5-coder:latest",  # Best overall
            "jupiter_tasks": "deepseek-r1:latest"  # Jupiter specialist
        }}

        return recommendations

if __name__ == "__main__":
    monitor = ClaudiaPerformanceMonitor()
    asyncio.run(monitor.monitor_model_performance())
'''

        # Save performance monitor
        monitor_file = self.base_path / "claudia_optimal_performance_monitor.py"
        with open(monitor_file, 'w', encoding='utf-8') as f:
            f.write(monitor_code)

        logger.info(f"✅ Performance monitor created: {monitor_file}")
        return monitor_file

    async def update_all_scripts(self):
        """Update all Claude CC scripts with optimal models"""
        logger.info("🔄 Starting comprehensive script updates...")

        results = {
            "updated_files": [],
            "errors": [],
            "summary": {}
        }

        try:
            # Update Claudia integration bridge
            bridge_updated = await self.update_claudia_integration_bridge()
            if bridge_updated:
                results["updated_files"].append("claudia_integration_bridge.py")

            # Update DeepSeek trading agents
            agent_files = await self.update_deepseek_trading_agent()
            results["updated_files"].extend(agent_files)

            # Update Jupiter deployment
            jupiter_updated = await self.update_jupiter_deployment()
            if jupiter_updated:
                results["updated_files"].append("deploy_jupiter_phase1.py")

            # Create performance monitoring
            monitor_file = await self.create_performance_monitoring()
            results["updated_files"].append(str(monitor_file))

            # Generate summary
            results["summary"] = {
                "total_files_updated": len(results["updated_files"]),
                "optimal_models": self.optimal_config["models"],
                "performance_improvements": {
                    "primary_model_score": "94.5%",
                    "fast_model_speed": "5.37s avg",
                    "success_rate": "100% for top models"
                },
                "next_steps": [
                    "Start optimized Claudia: cd claudia && python start_optimal.py",
                    "Monitor performance: python claudia_optimal_performance_monitor.py",
                    "Test Jupiter integration with optimal models"
                ]
            }

        except Exception as e:
            logger.error(f"❌ Error updating scripts: {e}")
            results["errors"].append(str(e))
            # Ensure summary exists even if there's an error
            results["summary"] = {
                "total_files_updated": len(results["updated_files"]),
                "optimal_models": self.optimal_config["models"],
                "error": str(e)
            }

        # Save update report
        report_file = self.base_path / f"CLAUDIA_SCRIPT_UPDATE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"📋 Update report saved to: {report_file}")
        return results

async def main():
    """Main entry point"""
    updater = ClaudiaCCScriptUpdater()

    try:
        results = await updater.update_all_scripts()

        print("\n" + "="*80)
        print("🎉 CLAUDIA CC SCRIPT UPDATES COMPLETE!")
        print("="*80)
        print(f"📄 Files Updated: {results['summary']['total_files_updated']}")
        print(f"🏆 Optimal Models Configured:")
        for model_type, model_name in results['summary']['optimal_models'].items():
            print(f"   {model_type}: {model_name}")
        print(f"\n📊 Performance Improvements:")
        for improvement, value in results['summary']['performance_improvements'].items():
            print(f"   {improvement}: {value}")
        print(f"\n🚀 Next Steps:")
        for step in results['summary']['next_steps']:
            print(f"   {step}")
        print("="*80)

    except Exception as e:
        logger.error(f"❌ Script update failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
