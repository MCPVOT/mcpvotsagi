#!/usr/bin/env python3
"""
Claudia Model Selection Demo
===========================
Demonstrate how Claudia selects Claude models based on task type
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ClaudiaModelDemo")

class ClaudiaModelSelector:
    """Demonstrate Claudia's model selection logic"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_file = self.base_path / "claudia_config.json"
        self.load_config()

    def load_config(self):
        """Load Claudia configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info("✅ Claudia configuration loaded")
        except Exception as e:
            logger.error(f"❌ Error loading config: {e}")
            self.config = {}

    def select_model_for_task(self, task_type: str, task_description: str) -> Dict[str, Any]:
        """Select appropriate Claude model based on task type"""

        # Get model configuration
        claudia_cc = self.config.get("claudia_cc_upgrade", {})
        model_routing = self.config.get("model_routing", {})

        # Model selection logic based on task type
        if task_type in ["complex_reasoning", "strategic_planning", "multi_repository_analysis"]:
            model = claudia_cc.get("primary_model", "claude-3-opus-4")
            priority = "HIGH"
            reason = "Complex reasoning requires Claude Opus 4's advanced capabilities"

        elif task_type in ["code_generation", "api_integration", "documentation", "debugging"]:
            model = claudia_cc.get("secondary_model", "claude-3-sonnet-4")
            priority = "MEDIUM"
            reason = "Code tasks are handled efficiently by Claude Sonnet 4"

        elif task_type in ["quick_response", "status_check", "simple_query"]:
            model = claudia_cc.get("fallback_model", "claude-3-haiku-20240307")
            priority = "LOW"
            reason = "Simple tasks use Claude Haiku for speed and efficiency"

        else:
            # Default to adaptive selection
            model = claudia_cc.get("primary_model", "claude-3-opus-4")
            priority = "MEDIUM"
            reason = "Unknown task type defaults to primary model"

        # Get model settings
        model_settings = model_routing.get(model, {})

        return {
            "selected_model": model,
            "priority": priority,
            "reason": reason,
            "task_type": task_type,
            "task_description": task_description,
            "model_settings": {
                "max_tokens": model_settings.get("max_tokens", 4096),
                "temperature": model_settings.get("temperature", 0.1),
                "top_p": model_settings.get("top_p", 0.9),
                "use_cases": model_settings.get("use_cases", [])
            },
            "timestamp": datetime.now().isoformat()
        }

    def demonstrate_model_selection(self):
        """Demonstrate model selection for various task types"""
        logger.info("🎯 Demonstrating Claudia Model Selection...")
        logger.info("="*70)

        # Define test tasks
        test_tasks = [
            {
                "type": "complex_reasoning",
                "description": "Analyze Jupiter DEX integration strategy and recommend optimal approach"
            },
            {
                "type": "code_generation",
                "description": "Generate Python code for RL trading algorithm integration"
            },
            {
                "type": "api_integration",
                "description": "Create API wrapper for Solana blockchain interactions"
            },
            {
                "type": "documentation",
                "description": "Write comprehensive documentation for trading system"
            },
            {
                "type": "debugging",
                "description": "Debug Unicode encoding issues in trading dashboard"
            },
            {
                "type": "strategic_planning",
                "description": "Develop multi-DEX arbitrage strategy for production deployment"
            },
            {
                "type": "quick_response",
                "description": "Check system health status"
            },
            {
                "type": "status_check",
                "description": "Verify all components are running correctly"
            },
            {
                "type": "performance_optimization",
                "description": "Optimize RL model training performance"
            }
        ]

        results = []

        for task in test_tasks:
            result = self.select_model_for_task(task["type"], task["description"])
            results.append(result)

            logger.info(f"📋 Task: {task['type']}")
            logger.info(f"   Description: {task['description']}")
            logger.info(f"   Selected Model: {result['selected_model']}")
            logger.info(f"   Priority: {result['priority']}")
            logger.info(f"   Reason: {result['reason']}")
            logger.info(f"   Max Tokens: {result['model_settings']['max_tokens']}")
            logger.info(f"   Temperature: {result['model_settings']['temperature']}")
            logger.info("")

        # Summary
        logger.info("="*70)
        logger.info("📊 MODEL SELECTION SUMMARY")
        logger.info("="*70)

        model_usage = {}
        for result in results:
            model = result["selected_model"]
            if model not in model_usage:
                model_usage[model] = []
            model_usage[model].append(result["task_type"])

        for model, tasks in model_usage.items():
            logger.info(f"🤖 {model}: {len(tasks)} tasks")
            for task in tasks:
                logger.info(f"   - {task}")
            logger.info("")

        # Show that Claude 4 models are being used
        logger.info("🎉 CLAUDE 4 MODEL USAGE:")
        opus_4_tasks = model_usage.get("claude-3-opus-4", [])
        sonnet_4_tasks = model_usage.get("claude-3-sonnet-4", [])

        logger.info(f"   Claude Opus 4: {len(opus_4_tasks)} tasks (HIGH priority)")
        logger.info(f"   Claude Sonnet 4: {len(sonnet_4_tasks)} tasks (MEDIUM priority)")

        if opus_4_tasks or sonnet_4_tasks:
            logger.info("✅ Claudia is configured to use Claude Opus 4 and Sonnet 4 when required!")
        else:
            logger.info("⚠️ Claude 4 models are not being selected for these tasks")

        return results

    def show_adaptive_selection_logic(self):
        """Show how Claudia's adaptive selection works"""
        logger.info("\n🧠 ADAPTIVE MODEL SELECTION LOGIC:")
        logger.info("="*50)

        claudia_cc = self.config.get("claudia_cc_upgrade", {})
        strategy = claudia_cc.get("model_selection_strategy", "adaptive")

        logger.info(f"Strategy: {strategy}")
        logger.info(f"Usage Monitoring: {claudia_cc.get('usage_monitoring', False)}")
        logger.info(f"Cost Optimization: {claudia_cc.get('cost_optimization', False)}")

        logger.info("\n🎯 When Claude Opus 4 is selected:")
        logger.info("   - Complex reasoning tasks")
        logger.info("   - Advanced code analysis")
        logger.info("   - Strategic planning")
        logger.info("   - Jupiter DEX integration analysis")
        logger.info("   - RL strategy development")
        logger.info("   - Multi-repository analysis")

        logger.info("\n🎯 When Claude Sonnet 4 is selected:")
        logger.info("   - Code generation")
        logger.info("   - API integration")
        logger.info("   - Documentation writing")
        logger.info("   - Error debugging")
        logger.info("   - Performance optimization")
        logger.info("   - UI/UX improvements")

if __name__ == "__main__":
    selector = ClaudiaModelSelector()

    # Demonstrate model selection
    results = selector.demonstrate_model_selection()

    # Show adaptive logic
    selector.show_adaptive_selection_logic()

    # Save results
    results_file = Path(__file__).parent / f"claudia_model_selection_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n💾 Results saved to: {results_file}")
    logger.info("✅ Demonstration complete!")
