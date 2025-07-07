#!/usr/bin/env python3
"""
En        # Top 3 Optimized Models - Load only when required
        self.model_routes = {
            "trading_analysis": "deepseek-r1:latest",    # Best for complex trading decisions
            "code_optimization": "qwen2.5-coder:latest", # Best for code analysis & system optimization
            "quick_response": "llama3.2:3b",             # Best for fast responses & real-time data
            "reasoning": "deepseek-r1:latest",           # Complex reasoning tasks
            "risk_assessment": "deepseek-r1:latest",     # Risk analysis
            "system_monitoring": "llama3.2:3b"          # Real-time monitoring
        }udia Client with Optimal Model Selection
==================================================
Intelligent AI client that uses the best available Ollama models
for different tasks in the Ultimate AGI System V3
"""

import asyncio
import aiohttp
import json
import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClaudiaEnhanced")

class EnhancedClaudiaClient:
    """Enhanced Claudia client with intelligent model selection"""

    def __init__(self, config_path: str = "claudia_optimal_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.session = None
        self.available_models = []
        self.model_performance = {}

        # Model routing based on your available models
        self.model_routes = {
            "trading_analysis": "deepseek-r1:latest",
            "code_review": "qwen2.5-coder:latest",
            "mathematical": "gemma3n:latest",
            "quick_response": "llama3.2:3b",
            "general": "llama3.1:8b",
            "reasoning": "deepseek-r1:latest",
            "instruction": "llama3.1:8b-instruct-q4_K_M"
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Config file {self.config_path} not found, using defaults")
                return self._default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "api": {"host": "localhost", "port": 11434, "timeout": 30},
            "performance": {"temperature": 0.7, "max_tokens": 2048}
        }

    async def initialize(self):
        """Initialize the client and check available models"""
        try:
            api_config = self.config.get("api", {})
            base_url = f"http://{api_config.get('host', 'localhost')}:{api_config.get('port', 11434)}"

            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=api_config.get('timeout', 30))
            )

            # Check available models
            async with self.session.get(f"{base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    self.available_models = [model['name'] for model in data.get('models', [])]
                    logger.info(f"🤖 Available models: {len(self.available_models)}")

                    # Log best models for each task
                    for task, model in self.model_routes.items():
                        if model in self.available_models:
                            logger.info(f"✅ {task}: {model}")
                        else:
                            logger.warning(f"⚠️ {task}: {model} not available")

                    return True
                else:
                    logger.error(f"Failed to connect to Ollama API: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error initializing Claudia client: {e}")
            return False

    async def analyze_trading_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trading data using DeepSeek-R1 for advanced reasoning"""
        model = "deepseek-r1:latest"

        prompt = f"""
        🔍 ADVANCED TRADING ANALYSIS - DeepSeek-R1

        Market Data:
        - Symbol: {market_data.get('symbol', 'Unknown')}
        - Price: ${market_data.get('price', 0):.4f}
        - 24h Change: {market_data.get('change_24h', 0):.2f}%
        - Volume: ${market_data.get('volume_24h', 0):,.0f}
        - Market Cap: ${market_data.get('market_cap', 0):,.0f}

        Please provide:
        1. Technical Analysis (Support/Resistance, Trends)
        2. Risk Assessment (High/Medium/Low with reasoning)
        3. Trading Recommendation (Buy/Hold/Sell with rationale)
        4. Price Targets (Short-term and long-term)
        5. Risk Management Strategy

        Format as JSON with confidence scores.
        """

        return await self._query_model(model, prompt, task_type="trading_analysis")

    async def analyze_code_quality(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code quality using Qwen2.5-Coder"""
        model = "qwen2.5-coder:latest"

        prompt = f"""
        🔍 CODE QUALITY ANALYSIS - Qwen2.5-Coder

        Language: {language}
        Code:
        ```{language}
        {code}
        ```

        Please analyze:
        1. Code Quality (Structure, Readability, Best Practices)
        2. Performance Optimizations
        3. Security Considerations
        4. Bug Detection
        5. Improvement Suggestions

        Provide detailed feedback with specific recommendations.
        """

        return await self._query_model(model, prompt, task_type="code_review")

    async def perform_mathematical_analysis(self, problem: str) -> Dict[str, Any]:
        """Perform mathematical analysis using Gemma3n"""
        model = "gemma3n:latest"

        prompt = f"""
        🧮 MATHEMATICAL ANALYSIS - Gemma3n

        Problem: {problem}

        Please provide:
        1. Step-by-step solution
        2. Mathematical reasoning
        3. Alternative approaches
        4. Verification of results
        5. Real-world applications

        Show all work clearly and explain each step.
        """

        return await self._query_model(model, prompt, task_type="mathematical")

    async def quick_response(self, question: str) -> str:
        """Get quick response using Llama3.2:3b for speed"""
        model = "llama3.2:3b"

        prompt = f"""
        Quick response needed: {question}

        Provide a concise, accurate answer.
        """

        result = await self._query_model(model, prompt, task_type="quick_response")
        return result.get("response", "No response available")

    async def general_reasoning(self, query: str) -> Dict[str, Any]:
        """General reasoning using Llama3.1:8b"""
        model = "llama3.1:8b"

        prompt = f"""
        🧠 GENERAL REASONING - Llama3.1:8b

        Query: {query}

        Please provide:
        1. Analysis of the situation
        2. Key considerations
        3. Recommended approach
        4. Potential outcomes
        5. Next steps

        Be thorough but concise.
        """

        return await self._query_model(model, prompt, task_type="general")

    async def _query_model(self, model: str, prompt: str, task_type: str = "general") -> Dict[str, Any]:
        """Query a specific model with performance tracking"""
        if not self.session:
            await self.initialize()

        if model not in self.available_models:
            logger.warning(f"Model {model} not available, using fallback")
            model = self._get_fallback_model(task_type)

        try:
            api_config = self.config.get("api", {})
            perf_config = self.config.get("performance", {})
            base_url = f"http://{api_config.get('host', 'localhost')}:{api_config.get('port', 11434)}"

            start_time = datetime.now()

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": perf_config.get("temperature", 0.7),
                    "top_p": perf_config.get("top_p", 0.9),
                    "num_predict": perf_config.get("max_tokens", 2048)
                }
            }

            async with self.session.post(f"{base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()

                    # Track performance
                    self._update_performance_metrics(model, task_type, response_time, True)

                    logger.info(f"✅ {task_type} completed with {model} in {response_time:.2f}s")

                    return {
                        "response": data.get("response", ""),
                        "model": model,
                        "task_type": task_type,
                        "response_time": response_time,
                        "success": True
                    }
                else:
                    logger.error(f"Model query failed: {response.status}")
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error querying model {model}: {e}")
            self._update_performance_metrics(model, task_type, 0, False)
            return {"success": False, "error": str(e)}

    def _get_fallback_model(self, task_type: str) -> str:
        """Get fallback model for task type"""
        fallbacks = {
            "trading_analysis": ["deepseek-r1:8b", "llama3.1:8b", "llama3.2:3b"],
            "code_review": ["llama3.1:8b", "llama3.2:3b"],
            "mathematical": ["llama3.1:8b", "llama3.2:3b"],
            "quick_response": ["llama3.2:3b", "llama3.1:8b"],
            "general": ["llama3.1:8b", "llama3.2:3b"]
        }

        for fallback in fallbacks.get(task_type, ["llama3.2:3b"]):
            if fallback in self.available_models:
                return fallback

        # Ultimate fallback
        return self.available_models[0] if self.available_models else "llama3.2:3b"

    def _update_performance_metrics(self, model: str, task_type: str, response_time: float, success: bool):
        """Update performance metrics for model selection optimization"""
        if model not in self.model_performance:
            self.model_performance[model] = {"total_queries": 0, "successful_queries": 0, "avg_response_time": 0}

        metrics = self.model_performance[model]
        metrics["total_queries"] += 1
        if success:
            metrics["successful_queries"] += 1
            # Update rolling average response time
            metrics["avg_response_time"] = (metrics["avg_response_time"] + response_time) / 2

    async def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all models"""
        return {
            "available_models": self.available_models,
            "model_routes": self.model_routes,
            "performance_metrics": self.model_performance,
            "timestamp": datetime.now().isoformat()
        }

    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()


# Example usage and testing
async def test_enhanced_claudia():
    """Test the enhanced Claudia client"""
    client = EnhancedClaudiaClient()

    if await client.initialize():
        logger.info("🚀 Testing Enhanced Claudia Client...")

        # Test quick response
        quick_result = await client.quick_response("What is the current status of the crypto market?")
        print(f"Quick Response: {quick_result}")

        # Test trading analysis
        sample_market_data = {
            "symbol": "SOL/USDC",
            "price": 145.67,
            "change_24h": 5.23,
            "volume_24h": 2500000,
            "market_cap": 65000000000
        }

        trading_analysis = await client.analyze_trading_data(sample_market_data)
        print(f"Trading Analysis: {trading_analysis.get('response', 'No response')[:200]}...")

        # Get performance report
        perf_report = await client.get_performance_report()
        print(f"Performance Report: {json.dumps(perf_report, indent=2)}")

        await client.close()
    else:
        logger.error("Failed to initialize Claudia client")


if __name__ == "__main__":
    asyncio.run(test_enhanced_claudia())
