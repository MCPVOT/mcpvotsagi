#!/usr/bin/env python3
"""
Fixed Claudia Optimal Model Performance Monitor
==============================================
Monitor performance of optimal Ollama models in Claudia
"""

import asyncio
import json
import logging
import requests
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClaudiaPerformanceMonitor")

class ClaudiaPerformanceMonitor:
    """Monitor performance of optimal Claudia models"""

    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.optimal_models = {
            "primary": "qwen2.5-coder:latest",
            "code_generation": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
            "fast_response": "llama3.2:latest",
            "jupiter_specialist": "deepseek-r1:latest"
        }
        self.performance_log = Path(__file__).parent / "claudia_performance_log.json"

    async def test_model(self, model_name: str, test_prompt: str = "Calculate 2+2 and explain briefly."):
        """Test a single model's performance"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": test_prompt,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time
                return {
                    "status": "active",
                    "response_time": response_time,
                    "response_length": len(result.get("response", "")),
                    "success": True,
                    "response_preview": result.get("response", "")[:100]
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "success": False
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }

    async def monitor_model_performance(self):
        """Monitor performance of all optimal models"""
        logger.info("📊 Starting model performance monitoring...")

        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "models": {}
        }

        for model_type, model_name in self.optimal_models.items():
            logger.info(f"🔍 Testing {model_type}: {model_name}")

            result = await self.test_model(model_name)
            result["type"] = model_type
            performance_data["models"][model_name] = result

            if result["success"]:
                logger.info(f"✅ {model_name}: {result['response_time']:.2f}s")
            else:
                logger.error(f"❌ {model_name}: {result.get('error', 'Unknown error')}")

        # Save performance data
        with open(self.performance_log, 'w') as f:
            json.dump(performance_data, f, indent=2)

        logger.info(f"💾 Performance data saved to: {self.performance_log}")

        # Print summary
        print("\n" + "="*60)
        print("📊 CLAUDIA OPTIMAL MODELS PERFORMANCE TEST")
        print("="*60)

        for model_name, data in performance_data["models"].items():
            status_icon = "✅" if data["success"] else "❌"
            if data["success"]:
                print(f"{status_icon} {data['type']}: {model_name}")
                print(f"   Response Time: {data['response_time']:.2f}s")
                print(f"   Response Length: {data['response_length']} chars")
            else:
                print(f"{status_icon} {data['type']}: {model_name}")
                print(f"   Error: {data['error']}")
            print()

        print("="*60)
        return performance_data

if __name__ == "__main__":
    monitor = ClaudiaPerformanceMonitor()
    asyncio.run(monitor.monitor_model_performance())
