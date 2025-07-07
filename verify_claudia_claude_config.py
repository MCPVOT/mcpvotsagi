#!/usr/bin/env python3
"""
Claudia Model Configuration Verification
=======================================
Verify that Claudia is properly configured to use Claude Opus 4 and Sonnet 4
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ClaudiaVerification")

class ClaudiaModelVerification:
    """Verify Claudia model configuration"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_file = self.base_path / "claudia_config.json"
        self.usage_monitor_file = self.base_path / "claudia_usage_monitor.py"

    def verify_config_file(self) -> Dict[str, Any]:
        """Verify the main configuration file"""
        logger.info("🔍 Verifying Claudia configuration...")

        if not self.config_file.exists():
            logger.error(f"❌ Configuration file not found: {self.config_file}")
            return {"status": "error", "message": "Config file not found"}

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Check primary model
            primary_model = config.get("claudia_cc_upgrade", {}).get("primary_model")
            secondary_model = config.get("claudia_cc_upgrade", {}).get("secondary_model")
            fallback_model = config.get("claudia_cc_upgrade", {}).get("fallback_model")

            result = {
                "status": "success",
                "primary_model": primary_model,
                "secondary_model": secondary_model,
                "fallback_model": fallback_model,
                "model_routing": config.get("model_routing", {}),
                "usage_monitoring": config.get("usage_monitoring", {})
            }

            # Verify Claude 4 models
            if primary_model == "claude-3-opus-4":
                logger.info("✅ Claude Opus 4 set as primary model")
            else:
                logger.warning(f"⚠️ Primary model is {primary_model}, not Claude Opus 4")

            if secondary_model == "claude-3-sonnet-4":
                logger.info("✅ Claude Sonnet 4 set as secondary model")
            else:
                logger.warning(f"⚠️ Secondary model is {secondary_model}, not Claude Sonnet 4")

            return result

        except Exception as e:
            logger.error(f"❌ Error reading configuration: {e}")
            return {"status": "error", "message": str(e)}

    def verify_usage_monitor(self) -> Dict[str, Any]:
        """Verify the usage monitor configuration"""
        logger.info("🔍 Verifying usage monitor...")

        if not self.usage_monitor_file.exists():
            logger.error(f"❌ Usage monitor file not found: {self.usage_monitor_file}")
            return {"status": "error", "message": "Usage monitor file not found"}

        try:
            with open(self.usage_monitor_file, 'r') as f:
                content = f.read()

            # Check for model selection logic
            has_opus_4 = "claude-3-opus-4" in content
            has_sonnet_4 = "claude-3-sonnet-4" in content
            has_model_selection = "optimize_model_selection" in content

            result = {
                "status": "success",
                "has_opus_4_reference": has_opus_4,
                "has_sonnet_4_reference": has_sonnet_4,
                "has_model_selection_logic": has_model_selection
            }

            if has_opus_4:
                logger.info("✅ Usage monitor references Claude Opus 4")
            if has_sonnet_4:
                logger.info("✅ Usage monitor references Claude Sonnet 4")
            if has_model_selection:
                logger.info("✅ Usage monitor has model selection logic")

            return result

        except Exception as e:
            logger.error(f"❌ Error reading usage monitor: {e}")
            return {"status": "error", "message": str(e)}

    def verify_model_routing(self) -> Dict[str, Any]:
        """Verify model routing configuration"""
        logger.info("🔍 Verifying model routing...")

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            model_routing = config.get("model_routing", {})

            # Check if Claude 4 models have proper routing
            opus_4_routing = model_routing.get("claude-3-opus-4", {})
            sonnet_4_routing = model_routing.get("claude-3-sonnet-4", {})

            result = {
                "status": "success",
                "opus_4_configured": bool(opus_4_routing),
                "sonnet_4_configured": bool(sonnet_4_routing),
                "opus_4_use_cases": opus_4_routing.get("use_cases", []),
                "sonnet_4_use_cases": sonnet_4_routing.get("use_cases", []),
                "opus_4_priority": opus_4_routing.get("priority", "NONE"),
                "sonnet_4_priority": sonnet_4_routing.get("priority", "NONE")
            }

            if opus_4_routing:
                logger.info("✅ Claude Opus 4 routing configured")
                logger.info(f"   Priority: {opus_4_routing.get('priority', 'NONE')}")
                logger.info(f"   Use cases: {len(opus_4_routing.get('use_cases', []))}")

            if sonnet_4_routing:
                logger.info("✅ Claude Sonnet 4 routing configured")
                logger.info(f"   Priority: {sonnet_4_routing.get('priority', 'NONE')}")
                logger.info(f"   Use cases: {len(sonnet_4_routing.get('use_cases', []))}")

            return result

        except Exception as e:
            logger.error(f"❌ Error verifying model routing: {e}")
            return {"status": "error", "message": str(e)}

    def show_current_configuration(self):
        """Show the current Claudia configuration"""
        logger.info("📋 Current Claudia Configuration:")
        logger.info("="*60)

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            claudia_cc = config.get("claudia_cc_upgrade", {})

            logger.info(f"Primary Model: {claudia_cc.get('primary_model', 'Not set')}")
            logger.info(f"Secondary Model: {claudia_cc.get('secondary_model', 'Not set')}")
            logger.info(f"Fallback Model: {claudia_cc.get('fallback_model', 'Not set')}")
            logger.info(f"Model Selection Strategy: {claudia_cc.get('model_selection_strategy', 'Not set')}")
            logger.info(f"Usage Monitoring: {claudia_cc.get('usage_monitoring', False)}")
            logger.info(f"Cost Optimization: {claudia_cc.get('cost_optimization', False)}")

            logger.info("\n🎯 Model Routing Configuration:")
            model_routing = config.get("model_routing", {})
            for model, settings in model_routing.items():
                logger.info(f"  {model}:")
                logger.info(f"    Priority: {settings.get('priority', 'Not set')}")
                logger.info(f"    Use Cases: {len(settings.get('use_cases', []))}")
                logger.info(f"    Max Tokens: {settings.get('max_tokens', 'Not set')}")

        except Exception as e:
            logger.error(f"❌ Error showing configuration: {e}")

    def run_verification(self):
        """Run complete verification"""
        logger.info("🚀 Starting Claudia Model Configuration Verification...")
        logger.info("="*60)

        # Show current configuration
        self.show_current_configuration()

        # Verify configuration file
        config_result = self.verify_config_file()

        # Verify usage monitor
        monitor_result = self.verify_usage_monitor()

        # Verify model routing
        routing_result = self.verify_model_routing()

        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("="*60)

        all_good = True

        # Check if Claude 4 models are configured
        if config_result.get("primary_model") == "claude-3-opus-4":
            logger.info("✅ Claude Opus 4 is configured as primary model")
        else:
            logger.warning("⚠️ Claude Opus 4 is NOT configured as primary model")
            all_good = False

        if config_result.get("secondary_model") == "claude-3-sonnet-4":
            logger.info("✅ Claude Sonnet 4 is configured as secondary model")
        else:
            logger.warning("⚠️ Claude Sonnet 4 is NOT configured as secondary model")
            all_good = False

        if routing_result.get("opus_4_configured") and routing_result.get("sonnet_4_configured"):
            logger.info("✅ Both Claude 4 models have proper routing configuration")
        else:
            logger.warning("⚠️ Claude 4 models routing may be incomplete")
            all_good = False

        if monitor_result.get("has_model_selection_logic"):
            logger.info("✅ Usage monitor has model selection logic")
        else:
            logger.warning("⚠️ Usage monitor may not have proper model selection")
            all_good = False

        if all_good:
            logger.info("\n🎉 VERIFICATION COMPLETE: Claudia is properly configured to use Claude Opus 4 and Sonnet 4!")
        else:
            logger.info("\n⚠️ VERIFICATION COMPLETE: Some issues found with Claude 4 configuration")

        return {
            "config_verification": config_result,
            "monitor_verification": monitor_result,
            "routing_verification": routing_result,
            "all_configured": all_good
        }

if __name__ == "__main__":
    verifier = ClaudiaModelVerification()
    verifier.run_verification()
