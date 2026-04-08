#!/usr/bin/env python3
"""
Ollama Model Performance Tester for Claudia Integration
======================================================
Test multiple Ollama models to find optimal performance for different tasks
"""

import asyncio
import json
import logging
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OllamaModelTester")

class OllamaModelTester:
    """Test Ollama models for Claudia integration"""

    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.test_results = {}
        self.available_models = []

        # Test cases for different scenarios
        self.test_cases = {
            "code_generation": {
                "prompt": "Create a Python function that calculates fibonacci numbers optimally using dynamic programming. Include error handling and docstring.",
                "expected_keywords": ["def", "fibonacci", "dynamic", "memo", "return", "docstring"],
                "weight": 0.25
            },
            "mathematical_reasoning": {
                "prompt": "Explain the mathematical concept behind the Kelly Criterion for position sizing in trading. Provide the formula and explain each component.",
                "expected_keywords": ["kelly", "criterion", "formula", "probability", "odds", "bankroll"],
                "weight": 0.25
            },
            "system_design": {
                "prompt": "Design a microservices architecture for a real-time trading system. Include components for data ingestion, risk management, and order execution.",
                "expected_keywords": ["microservices", "trading", "data", "risk", "order", "architecture"],
                "weight": 0.20
            },
            "debugging_analysis": {
                "prompt": "Analyze this code and find potential issues: ```python\ndef process_trades(trades):\n    for trade in trades:\n        if trade['amount'] > 0:\n            profit = trade['price'] * trade['amount']\n            return profit\n```",
                "expected_keywords": ["loop", "return", "early", "issue", "problem", "fix"],
                "weight": 0.15
            },
            "jupiter_integration": {
                "prompt": "Explain how to integrate Jupiter DEX swap functionality with a React application. Include error handling and transaction monitoring.",
                "expected_keywords": ["jupiter", "dex", "swap", "react", "transaction", "solana"],
                "weight": 0.15
            }
        }

    async def get_available_models(self):
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['name'] for model in data['models']]
                logger.info(f"Found {len(self.available_models)} available models")
                return self.available_models
            else:
                logger.error(f"Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []

    async def test_model_response(self, model: str, prompt: str, timeout: int = 30):
        """Test a single model with a prompt"""
        try:
            start_time = time.time()

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_ctx": 4096
                }
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=timeout
            )

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data.get('response', ''),
                    "response_time": response_time,
                    "tokens": len(data.get('response', '').split()),
                    "tokens_per_second": len(data.get('response', '').split()) / response_time if response_time > 0 else 0
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": timeout
            }

    def score_response(self, response: str, expected_keywords: list[str]) -> float:
        """Score a response based on keyword presence and quality"""
        if not response:
            return 0.0

        response_lower = response.lower()
        keyword_score = sum(1 for keyword in expected_keywords if keyword.lower() in response_lower)
        keyword_percentage = keyword_score / len(expected_keywords)

        # Quality indicators
        length_score = min(len(response) / 500, 1.0)  # Prefer longer, detailed responses
        structure_score = 0.0

        # Check for code blocks, lists, explanations
        if "```" in response:
            structure_score += 0.3
        if any(char in response for char in ['1.', '2.', '-', '*']):
            structure_score += 0.2
        if len(response.split('\n')) > 3:
            structure_score += 0.2

        # Final score combining keyword match, length, and structure
        final_score = (keyword_percentage * 0.6) + (length_score * 0.2) + (min(structure_score, 0.3))
        return min(final_score, 1.0)

    async def test_all_models(self, models_to_test: list[str] = None):
        """Test all available models across all test cases"""
        if models_to_test is None:
            models_to_test = await self.get_available_models()

        if not models_to_test:
            logger.error("No models available for testing")
            return

        logger.info(f"Testing {len(models_to_test)} models with {len(self.test_cases)} test cases...")

        for model in models_to_test:
            logger.info(f"Testing model: {model}")
            model_results = {
                "model_name": model,
                "test_results": {},
                "overall_score": 0.0,
                "avg_response_time": 0.0,
                "avg_tokens_per_second": 0.0,
                "success_rate": 0.0
            }

            total_score = 0.0
            total_time = 0.0
            total_tps = 0.0
            successful_tests = 0

            for test_name, test_data in self.test_cases.items():
                logger.info(f"  Running test: {test_name}")

                result = await self.test_model_response(
                    model,
                    test_data["prompt"]
                )

                if result["success"]:
                    score = self.score_response(result["response"], test_data["expected_keywords"])
                    weighted_score = score * test_data["weight"]

                    model_results["test_results"][test_name] = {
                        "score": score,
                        "weighted_score": weighted_score,
                        "response_time": result["response_time"],
                        "tokens": result["tokens"],
                        "tokens_per_second": result["tokens_per_second"],
                        "response_preview": result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"]
                    }

                    total_score += weighted_score
                    total_time += result["response_time"]
                    total_tps += result["tokens_per_second"]
                    successful_tests += 1

                else:
                    model_results["test_results"][test_name] = {
                        "score": 0.0,
                        "weighted_score": 0.0,
                        "error": result["error"],
                        "response_time": result["response_time"]
                    }
                    total_time += result["response_time"]

            # Calculate overall metrics
            model_results["overall_score"] = total_score
            model_results["avg_response_time"] = total_time / len(self.test_cases)
            model_results["avg_tokens_per_second"] = total_tps / max(successful_tests, 1)
            model_results["success_rate"] = successful_tests / len(self.test_cases)

            self.test_results[model] = model_results

            logger.info(f"  Model {model} - Score: {total_score:.3f}, Avg Time: {model_results['avg_response_time']:.2f}s, Success: {model_results['success_rate']:.1%}")

    def generate_recommendations(self):
        """Generate model recommendations based on test results"""
        if not self.test_results:
            return {}

        # Sort models by different criteria
        by_overall_score = sorted(self.test_results.items(), key=lambda x: x[1]["overall_score"], reverse=True)
        by_speed = sorted(self.test_results.items(), key=lambda x: x[1]["avg_response_time"])
        by_tokens_per_second = sorted(self.test_results.items(), key=lambda x: x[1]["avg_tokens_per_second"], reverse=True)

        # Find best for specific tasks
        best_for_code = max(self.test_results.items(),
                           key=lambda x: x[1]["test_results"].get("code_generation", {}).get("score", 0))
        best_for_reasoning = max(self.test_results.items(),
                               key=lambda x: x[1]["test_results"].get("mathematical_reasoning", {}).get("score", 0))
        best_for_jupiter = max(self.test_results.items(),
                              key=lambda x: x[1]["test_results"].get("jupiter_integration", {}).get("score", 0))

        recommendations = {
            "top_3_overall": [model for model, _ in by_overall_score[:3]],
            "fastest_response": by_speed[0][0] if by_speed else None,
            "highest_throughput": by_tokens_per_second[0][0] if by_tokens_per_second else None,
            "best_for_code": best_for_code[0],
            "best_for_reasoning": best_for_reasoning[0],
            "best_for_jupiter": best_for_jupiter[0],
            "claudia_optimal_config": {
                "primary_model": by_overall_score[0][0] if by_overall_score else None,
                "code_model": best_for_code[0],
                "reasoning_model": best_for_reasoning[0],
                "fast_model": by_speed[0][0] if by_speed else None
            }
        }

        return recommendations

    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create comprehensive report
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_configuration": {
                "models_tested": len(self.test_results),
                "test_cases": list(self.test_cases.keys()),
                "ollama_url": self.ollama_url
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations(),
            "summary": {
                "best_overall": max(self.test_results.items(), key=lambda x: x[1]["overall_score"])[0] if self.test_results else None,
                "fastest": min(self.test_results.items(), key=lambda x: x[1]["avg_response_time"])[0] if self.test_results else None,
                "most_reliable": max(self.test_results.items(), key=lambda x: x[1]["success_rate"])[0] if self.test_results else None
            }
        }

        # Save detailed results
        results_file = Path(__file__).parent / f"ollama_model_test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Test results saved to: {results_file}")
        return results_file, report

async def main():
    """Main testing function"""
    tester = OllamaModelTester()

    # Priority models for testing (based on your available models)
    priority_models = [
        "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
        "deepseek-r1:latest",
        "qwen2.5-coder:latest",
        "llama3.1:8b",
        "llama3.2:latest"
    ]

    try:
        print("\n" + "="*80)
        print("🧪 OLLAMA MODEL PERFORMANCE TESTING FOR CLAUDIA")
        print("="*80)

        # Test models
        await tester.test_all_models(priority_models)

        # Save results and get recommendations
        results_file, report = tester.save_results()
        recommendations = report["recommendations"]

        print(f"\n🏆 TEST RESULTS SUMMARY:")
        print(f"Models Tested: {len(tester.test_results)}")
        print(f"Test Cases: {len(tester.test_cases)}")

        print(f"\n🥇 TOP 3 OVERALL PERFORMERS:")
        for i, model in enumerate(recommendations["top_3_overall"], 1):
            score = tester.test_results[model]["overall_score"]
            time_avg = tester.test_results[model]["avg_response_time"]
            print(f"   {i}. {model}")
            print(f"      Score: {score:.3f} | Avg Time: {time_avg:.2f}s")

        print(f"\n🎯 SPECIALIZED RECOMMENDATIONS:")
        print(f"   Best for Code Generation: {recommendations['best_for_code']}")
        print(f"   Best for Mathematical Reasoning: {recommendations['best_for_reasoning']}")
        print(f"   Best for Jupiter Integration: {recommendations['best_for_jupiter']}")
        print(f"   Fastest Response: {recommendations['fastest_response']}")

        print(f"\n⚙️ CLAUDIA OPTIMAL CONFIGURATION:")
        config = recommendations["claudia_optimal_config"]
        print(f"   Primary Model (Complex Tasks): {config['primary_model']}")
        print(f"   Code Generation Model: {config['code_model']}")
        print(f"   Reasoning Model: {config['reasoning_model']}")
        print(f"   Fast Response Model: {config['fast_model']}")

        print(f"\n📊 Detailed results saved to: {results_file}")
        print("="*80)

        return recommendations

    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        raise

if __name__ == "__main__":
    recommendations = asyncio.run(main())
