#!/usr/bin/env python3
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
from typing import Dict, List

logger = logging.getLogger("ClaudiaPerformanceMonitor")

class ClaudiaPerformanceMonitor:
    """Monitor performance of optimal Claudia models"""

    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.optimal_models = {
            "primary": {
                        "name": "qwen2.5-coder:latest",
                        "description": "Primary model for complex tasks",
                        "use_cases": [
                                    "Complex reasoning",
                                    "Mathematical analysis",
                                    "System design",
                                    "General problem solving"
                        ],
                        "performance": {
                                    "score": 0.945,
                                    "avg_time": 8.94,
                                    "success_rate": 1.0
                        },
                        "ollama_config": {
                                    "temperature": 0.1,
                                    "top_p": 0.9,
                                    "num_ctx": 4096,
                                    "repeat_penalty": 1.1
                        }
            },
            "code_generation": {
                        "name": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
                        "description": "Specialized for code generation",
                        "use_cases": [
                                    "Python/JavaScript/TypeScript code generation",
                                    "Code debugging and analysis",
                                    "API wrapper creation",
                                    "Documentation generation"
                        ],
                        "performance": {
                                    "score": 0.4,
                                    "avg_time": 24.43,
                                    "success_rate": 0.4
                        },
                        "ollama_config": {
                                    "temperature": 0.05,
                                    "top_p": 0.8,
                                    "num_ctx": 8192,
                                    "repeat_penalty": 1.05
                        }
            },
            "fast_response": {
                        "name": "llama3.2:latest",
                        "description": "Fastest model for quick responses",
                        "use_cases": [
                                    "Quick queries",
                                    "Status checks",
                                    "Simple questions",
                                    "Real-time responses"
                        ],
                        "performance": {
                                    "score": 0.92,
                                    "avg_time": 5.37,
                                    "success_rate": 1.0
                        },
                        "ollama_config": {
                                    "temperature": 0.3,
                                    "top_p": 0.7,
                                    "num_ctx": 2048,
                                    "repeat_penalty": 1.0
                        }
            },
            "jupiter_specialist": {
                        "name": "deepseek-r1:latest",
                        "description": "Specialized for Jupiter DEX integration",
                        "use_cases": [
                                    "Jupiter DEX analysis",
                                    "Solana blockchain queries",
                                    "Trading strategy development",
                                    "DeFi protocol analysis"
                        ],
                        "performance": {
                                    "score": 0.4,
                                    "avg_time": 28.23,
                                    "success_rate": 0.4
                        },
                        "ollama_config": {
                                    "temperature": 0.2,
                                    "top_p": 0.85,
                                    "num_ctx": 4096,
                                    "repeat_penalty": 1.1
                        }
            }
}
        self.performance_log = Path(__file__).parent / "claudia_performance_log.json"

    async def monitor_model_performance(self):
        """Monitor performance of all optimal models"""
        logger.info("📊 Starting model performance monitoring...")

        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "models": {}
        }

        for model_type, model_name in self.optimal_models.items():
            logger.info(f"🔍 Testing {model_type}: {model_name}")

            # Test model performance
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "Calculate 2+2 and explain briefly.",
                        "stream": False
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    response_time = time.time() - start_time

                    performance_data["models"][model_name] = {
                        "type": model_type,
                        "status": "active",
                        "response_time": response_time,
                        "response_length": len(result.get("response", "")),
                        "success": True
                    }

                    logger.info(f"✅ {model_name}: {response_time:.2f}s")
                else:
                    performance_data["models"][model_name] = {
                        "type": model_type,
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    }

            except Exception as e:
                performance_data["models"][model_name] = {
                    "type": model_type,
                    "status": "error",
                    "error": str(e),
                    "success": False
                }
                logger.error(f"❌ {model_name}: {e}")

        # Save performance data
        with open(self.performance_log, 'w') as f:
            json.dump(performance_data, f, indent=2)

        logger.info(f"💾 Performance data saved to: {self.performance_log}")
        return performance_data

    async def get_model_recommendations(self):
        """Get model recommendations based on current performance"""
        if not self.performance_log.exists():
            await self.monitor_model_performance()

        with open(self.performance_log, 'r') as f:
            perf_data = json.load(f)

        recommendations = {
            "fast_tasks": "llama3.2:latest",  # Fastest response
            "code_tasks": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",  # Best for code
            "reasoning_tasks": "qwen2.5-coder:latest",  # Best overall
            "jupiter_tasks": "deepseek-r1:latest"  # Jupiter specialist
        }

        return recommendations

if __name__ == "__main__":
    monitor = ClaudiaPerformanceMonitor()
    asyncio.run(monitor.monitor_model_performance())
