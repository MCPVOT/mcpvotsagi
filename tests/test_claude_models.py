#!/usr/bin/env python3
"""
Test Claude Model Availability
==============================
Test if Claude Opus 4 and Sonnet 4 are available through Anthropic API
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
logger = logging.getLogger("ClaudeModelTest")

class ClaudeModelTester:
    """Test Claude model availability and capabilities"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.test_results = {}

    async def test_model_availability(self):
        """Test if Claude models are available"""
        logger.info("🧪 Testing Claude Model Availability...")

        # Models to test
        models_to_test = [
            "claude-3-opus-4",
            "claude-3-sonnet-4",
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022"
        ]

        # Test each model
        for model in models_to_test:
            try:
                result = await self.test_single_model(model)
                self.test_results[model] = result
                logger.info(f"✅ {model}: {result['status']}")
            except Exception as e:
                self.test_results[model] = {
                    "status": "ERROR",
                    "error": str(e),
                    "available": False
                }
                logger.error(f"❌ {model}: {e}")

        return self.test_results

    async def test_single_model(self, model_name: str) -> dict:
        """Test a single Claude model"""
        try:
            # Import anthropic here to avoid issues if not installed
            import anthropic

            if not self.api_key:
                return {
                    "status": "NO_API_KEY",
                    "error": "ANTHROPIC_API_KEY not set",
                    "available": False,
                    "model": model_name
                }

            # Create client
            client = anthropic.Anthropic(api_key=self.api_key)

            # Test simple completion
            test_prompt = "Hello! Please respond with just 'Model test successful' if you can understand this."

            message = client.messages.create(
                model=model_name,
                max_tokens=20,
                messages=[
                    {"role": "user", "content": test_prompt}
                ]
            )

            response_text = message.content[0].text if message.content else ""

            return {
                "status": "SUCCESS",
                "available": True,
                "model": model_name,
                "response": response_text,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                },
                "test_time": datetime.now().isoformat()
            }

        except anthropic.NotFoundError:
            return {
                "status": "NOT_FOUND",
                "error": f"Model {model_name} not found",
                "available": False,
                "model": model_name
            }
        except anthropic.AuthenticationError:
            return {
                "status": "AUTH_ERROR",
                "error": "Authentication failed - check API key",
                "available": False,
                "model": model_name
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "available": False,
                "model": model_name
            }

    async def generate_claudia_config(self):
        """Generate Claudia configuration based on available models"""
        logger.info("📋 Generating Claudia configuration...")

        available_models = [
            model for model, result in self.test_results.items()
            if result.get('available', False)
        ]

        if not available_models:
            logger.warning("⚠️  No Claude models available!")
            return None

        # Determine best models for different tasks
        config = {
            "claude_model_availability": {
                "test_date": datetime.now().isoformat(),
                "available_models": available_models,
                "test_results": self.test_results
            },
            "claudia_cc_upgrade": {
                "primary_model": None,
                "secondary_model": None,
                "fallback_model": None,
                "model_selection_strategy": "adaptive",
                "usage_monitoring": True,
                "cost_optimization": True
            },
            "model_routing": {},
            "usage_monitoring": {
                "enabled": True,
                "update_interval": 3,
                "cost_tracking": True,
                "token_limits": {},
                "auto_fallback": True,
                "cost_alerts": {
                    "daily_limit": 100.0,
                    "hourly_limit": 10.0,
                    "alert_thresholds": [0.5, 0.75, 0.9, 0.95]
                }
            }
        }

        # Set primary model (prefer Opus 4, then Sonnet 4, then others)
        if "claude-3-opus-4" in available_models:
            config["claudia_cc_upgrade"]["primary_model"] = "claude-3-opus-4"
            config["model_routing"]["claude-3-opus-4"] = {
                "use_cases": [
                    "Complex reasoning tasks",
                    "Advanced code analysis",
                    "Strategic planning",
                    "Jupiter DEX integration analysis",
                    "RL strategy development",
                    "Multi-repository analysis"
                ],
                "max_tokens": 4096,
                "temperature": 0.1,
                "top_p": 0.9,
                "priority": "HIGH"
            }
        elif "claude-3-5-sonnet-20241022" in available_models:
            config["claudia_cc_upgrade"]["primary_model"] = "claude-3-5-sonnet-20241022"
        elif "claude-3-opus-20240229" in available_models:
            config["claudia_cc_upgrade"]["primary_model"] = "claude-3-opus-20240229"

        # Set secondary model (prefer Sonnet 4, then others)
        if "claude-3-sonnet-4" in available_models:
            config["claudia_cc_upgrade"]["secondary_model"] = "claude-3-sonnet-4"
            config["model_routing"]["claude-3-sonnet-4"] = {
                "use_cases": [
                    "Code generation",
                    "API integration",
                    "Documentation writing",
                    "Error debugging",
                    "Performance optimization",
                    "UI/UX improvements"
                ],
                "max_tokens": 4096,
                "temperature": 0.2,
                "top_p": 0.8,
                "priority": "MEDIUM"
            }
        elif "claude-3-5-sonnet-20241022" in available_models:
            config["claudia_cc_upgrade"]["secondary_model"] = "claude-3-5-sonnet-20241022"
        elif "claude-3-sonnet-20240229" in available_models:
            config["claudia_cc_upgrade"]["secondary_model"] = "claude-3-sonnet-20240229"

        # Set fallback model
        if "claude-3-haiku-20240307" in available_models:
            config["claudia_cc_upgrade"]["fallback_model"] = "claude-3-haiku-20240307"
        elif "claude-3-5-haiku-20241022" in available_models:
            config["claudia_cc_upgrade"]["fallback_model"] = "claude-3-5-haiku-20241022"

        # Save configuration
        config_file = self.base_path / "claudia_model_test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"✅ Configuration saved to {config_file}")
        return config

    async def update_claudia_integration(self):
        """Update Claudia integration with verified models"""
        logger.info("🔄 Updating Claudia integration...")

        # Read current claudia_config.json
        config_file = self.base_path / "claudia_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                current_config = json.load(f)
        else:
            current_config = {}

        # Update with tested models
        available_models = [
            model for model, result in self.test_results.items()
            if result.get('available', False)
        ]

        if available_models:
            # Update model configuration
            if "claude-3-opus-4" in available_models:
                current_config["claudia_cc_upgrade"]["primary_model"] = "claude-3-opus-4"
                logger.info("✅ Claude Opus 4 available and set as primary")
            elif "claude-3-5-sonnet-20241022" in available_models:
                current_config["claudia_cc_upgrade"]["primary_model"] = "claude-3-5-sonnet-20241022"
                logger.info("✅ Claude 3.5 Sonnet available and set as primary")

            if "claude-3-sonnet-4" in available_models:
                current_config["claudia_cc_upgrade"]["secondary_model"] = "claude-3-sonnet-4"
                logger.info("✅ Claude Sonnet 4 available and set as secondary")
            elif "claude-3-5-sonnet-20241022" in available_models:
                current_config["claudia_cc_upgrade"]["secondary_model"] = "claude-3-5-sonnet-20241022"
                logger.info("✅ Claude 3.5 Sonnet available and set as secondary")

            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(current_config, f, indent=2)

            logger.info(f"✅ Updated {config_file} with verified models")
        else:
            logger.warning("⚠️  No Claude models available - configuration not updated")

    async def run_full_test(self):
        """Run complete Claude model test"""
        logger.info("🚀 Starting Claude Model Availability Test...")

        # Test models
        results = await self.test_model_availability()

        # Generate configuration
        config = await self.generate_claudia_config()

        # Update integration
        await self.update_claudia_integration()

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("CLAUDE MODEL TEST SUMMARY")
        logger.info("="*60)

        for model, result in results.items():
            status = "✅ AVAILABLE" if result.get('available') else "❌ NOT AVAILABLE"
            logger.info(f"{model}: {status}")
            if result.get('error'):
                logger.info(f"  Error: {result['error']}")

        # Check for Opus 4 and Sonnet 4 specifically
        opus4_available = results.get("claude-3-opus-4", {}).get('available', False)
        sonnet4_available = results.get("claude-3-sonnet-4", {}).get('available', False)

        logger.info("\n" + "="*60)
        logger.info("CLAUDE 4 MODEL STATUS")
        logger.info("="*60)
        logger.info(f"Claude Opus 4: {'✅ AVAILABLE' if opus4_available else '❌ NOT AVAILABLE'}")
        logger.info(f"Claude Sonnet 4: {'✅ AVAILABLE' if sonnet4_available else '❌ NOT AVAILABLE'}")

        if opus4_available and sonnet4_available:
            logger.info("🎉 Both Claude 4 models are available!")
        elif opus4_available or sonnet4_available:
            logger.info("⚠️  Some Claude 4 models are available")
        else:
            logger.info("⚠️  Claude 4 models are not available - using fallback models")

        return results

if __name__ == "__main__":
    tester = ClaudeModelTester()
    asyncio.run(tester.run_full_test())
