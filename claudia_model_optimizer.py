#!/usr/bin/env python3
"""
Claudia Model Optimizer
======================
Automatically selects and configures the best Ollama models for trading analysis
"""

import requests
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("ClaudiaOptimizer")

class ClaudiaModelOptimizer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_performance = {}
        self.optimal_config = {}

        # Model categories and their use cases
        self.model_categories = {
            "analysis": {
                "models": ["llama3.2:3b", "qwen2.5:3b", "deepseek-r1:1.5b"],
                "test_prompt": "Analyze this trading scenario: SOL price increased 5% with high volume. Provide brief analysis.",
                "weight": 0.4
            },
            "reasoning": {
                "models": ["deepseek-r1:1.5b", "llama3.2:3b", "qwen2.5:3b"],
                "test_prompt": "Given market conditions: volatility 15%, liquidity good, trend bullish. Should we increase position size? Yes/No and why.",
                "weight": 0.3
            },
            "speed": {
                "models": ["llama3.2:1b", "qwen2.5:3b", "deepseek-r1:1.5b"],
                "test_prompt": "Quick: Is 2+2=4?",
                "weight": 0.3
            }
        }

    def get_available_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error getting models: {e}")
        return []

    def test_model_performance(self, model: str, prompt: str) -> Dict:
        """Test model performance"""
        try:
            start_time = time.time()

            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100,
                    "top_k": 40,
                    "top_p": 0.9
                }
            }

            response = requests.post(f"{self.ollama_url}/api/generate", json=data, timeout=60)

            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time
                response_text = result.get("response", "")

                # Calculate performance metrics
                performance = {
                    "response_time": response_time,
                    "response_length": len(response_text),
                    "words_per_second": len(response_text.split()) / response_time,
                    "success": True,
                    "response": response_text[:200]  # First 200 chars
                }

                logger.info(f"✅ {model}: {response_time:.2f}s, {performance['words_per_second']:.1f} words/s")
                return performance
            else:
                logger.error(f"❌ {model} failed: {response.status_code}")
                return {"success": False, "error": response.status_code}

        except Exception as e:
            logger.error(f"❌ {model} error: {e}")
            return {"success": False, "error": str(e)}

    def benchmark_models(self) -> Dict:
        """Benchmark all available models"""
        available_models = self.get_available_models()
        logger.info(f"📋 Testing {len(available_models)} available models...")

        results = {}

        for category, config in self.model_categories.items():
            logger.info(f"\n🧪 Testing {category} category...")
            category_results = {}

            for model in config["models"]:
                if model in available_models:
                    performance = self.test_model_performance(model, config["test_prompt"])
                    if performance.get("success"):
                        # Calculate score based on speed and category weight
                        score = (performance["words_per_second"] * 10) + (100 / max(performance["response_time"], 0.1))
                        performance["score"] = score * config["weight"]
                        category_results[model] = performance
                else:
                    logger.warning(f"⚠️ Model {model} not available")

            results[category] = category_results

        return results

    def select_optimal_models(self, benchmark_results: Dict) -> Dict:
        """Select optimal models for each use case"""
        optimal_models = {}

        for category, results in benchmark_results.items():
            if results:
                # Sort by score
                sorted_models = sorted(results.items(), key=lambda x: x[1].get("score", 0), reverse=True)
                best_model = sorted_models[0][0]
                optimal_models[category] = {
                    "model": best_model,
                    "performance": sorted_models[0][1]
                }
                logger.info(f"🏆 Best {category} model: {best_model} (score: {sorted_models[0][1].get('score', 0):.1f})")
            else:
                logger.warning(f"⚠️ No models available for {category}")

        return optimal_models

    def generate_claudia_config(self, optimal_models: Dict) -> Dict:
        """Generate optimized Claudia configuration"""
        config = {
            "claudia_config": {
                "ollama_url": self.ollama_url,
                "models": {},
                "default_options": {
                    "temperature": 0.1,
                    "top_k": 40,
                    "top_p": 0.9,
                    "num_predict": 150
                },
                "trading_config": {
                    "analysis_model": optimal_models.get("analysis", {}).get("model", "llama3.2:3b"),
                    "reasoning_model": optimal_models.get("reasoning", {}).get("model", "deepseek-r1:1.5b"),
                    "quick_model": optimal_models.get("speed", {}).get("model", "llama3.2:1b"),
                    "confidence_threshold": 0.7,
                    "max_response_time": 10.0
                },
                "performance_data": optimal_models
            }
        }

        # Add model-specific configurations
        for category, model_info in optimal_models.items():
            model_name = model_info.get("model")
            if model_name:
                config["claudia_config"]["models"][model_name] = {
                    "use_case": category,
                    "performance": model_info.get("performance", {}),
                    "options": self._get_model_specific_options(model_name)
                }

        return config

    def _get_model_specific_options(self, model_name: str) -> Dict:
        """Get model-specific optimization options"""
        base_options = {
            "temperature": 0.1,
            "top_k": 40,
            "top_p": 0.9
        }

        # Model-specific optimizations
        if "deepseek" in model_name.lower():
            base_options.update({
                "temperature": 0.05,  # Lower for more deterministic reasoning
                "num_predict": 200
            })
        elif "llama" in model_name.lower():
            base_options.update({
                "temperature": 0.15,
                "num_predict": 150
            })
        elif "qwen" in model_name.lower():
            base_options.update({
                "temperature": 0.1,
                "num_predict": 180
            })

        return base_options

    def save_config(self, config: Dict, filepath: str = "claudia_optimal_config.json"):
        """Save optimal configuration to file"""
        config_path = Path(filepath)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"💾 Saved optimal config to {config_path}")

    async def optimize_claudia_setup(self):
        """Complete Claudia optimization process"""
        logger.info("🚀 Starting Claudia model optimization...")

        # Benchmark all models
        benchmark_results = self.benchmark_models()

        # Select optimal models
        optimal_models = self.select_optimal_models(benchmark_results)

        # Generate configuration
        config = self.generate_claudia_config(optimal_models)

        # Save configuration
        self.save_config(config)

        # Also save as YAML for ecosystem
        yaml_config = {
            "trading_ai": {
                "analysis_model": config["claudia_config"]["trading_config"]["analysis_model"],
                "reasoning_model": config["claudia_config"]["trading_config"]["reasoning_model"],
                "quick_model": config["claudia_config"]["trading_config"]["quick_model"]
            },
            "performance": {
                category: {
                    "model": info.get("model", ""),
                    "score": info.get("performance", {}).get("score", 0),
                    "response_time": info.get("performance", {}).get("response_time", 0)
                }
                for category, info in optimal_models.items()
            }
        }

        # Update the ecosystem config
        config_path = Path("claudia_ecosystem_config.yaml")
        if config_path.exists():
            import yaml
            with open(config_path, 'r') as f:
                existing_config = yaml.safe_load(f)

            existing_config.update(yaml_config)

            with open(config_path, 'w') as f:
                yaml.dump(existing_config, f, default_flow_style=False)

        logger.info("🎉 Claudia optimization complete!")
        return config

if __name__ == "__main__":
    import asyncio

    optimizer = ClaudiaModelOptimizer()
    asyncio.run(optimizer.optimize_claudia_setup())
