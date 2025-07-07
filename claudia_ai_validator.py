#!/usr/bin/env python3
"""
Claudia AI Integration Testing and Validation
============================================
Comprehensive testing suite for Claudia AI integration with trading systems
"""

import asyncio
import json
import logging
import time
import requests
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import aiohttp
from dataclasses import dataclass
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ClaudiaValidator")

@dataclass
class TestResult:
    """Test result structure"""
    test_name: str
    success: bool
    duration: float
    score: float
    details: Dict[str, Any]
    error: Optional[str] = None

class ClaudiaValidator:
    """Comprehensive Claudia AI integration validator"""

    def __init__(self, config_path: str = "claudia_ecosystem_config.yaml"):
        self.config = self._load_config(config_path)
        self.ollama_url = self.config.get("claudia", {}).get("ollama_url", "http://localhost:11435")
        self.test_results = []
        self.performance_metrics = {}

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config {config_path}: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "claudia": {
                "ollama_url": "http://localhost:11435",
                "models": {
                    "primary": "llama3.2:latest",
                    "fallback": "llama3.1:latest"
                },
                "parameters": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 1000
                }
            }
        }

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of Claudia integration"""
        logger.info("🧪 Starting comprehensive Claudia AI validation...")

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "pending",
            "test_results": [],
            "performance_metrics": {},
            "recommendations": []
        }

        # Test categories
        test_categories = [
            ("Connection Tests", self._test_connection_suite),
            ("Model Tests", self._test_model_suite),
            ("Performance Tests", self._test_performance_suite),
            ("Trading Integration Tests", self._test_trading_integration_suite),
            ("Advanced Features Tests", self._test_advanced_features_suite)
        ]

        total_tests = 0
        passed_tests = 0

        for category_name, test_suite in test_categories:
            logger.info(f"📋 Running {category_name}...")

            try:
                suite_results = await test_suite()
                validation_results["test_results"].extend(suite_results)

                # Count results
                for result in suite_results:
                    total_tests += 1
                    if result.success:
                        passed_tests += 1

            except Exception as e:
                logger.error(f"❌ {category_name} failed: {e}")
                validation_results["test_results"].append(TestResult(
                    test_name=f"{category_name} - Suite Error",
                    success=False,
                    duration=0,
                    score=0,
                    details={"error": str(e)},
                    error=str(e)
                ))
                total_tests += 1

        # Calculate overall metrics
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        validation_results["overall_status"] = "passed" if success_rate >= 0.8 else "failed"
        validation_results["performance_metrics"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "average_response_time": np.mean([r.duration for r in validation_results["test_results"]]),
            "average_score": np.mean([r.score for r in validation_results["test_results"]])
        }

        # Generate recommendations
        validation_results["recommendations"] = self._generate_recommendations(validation_results)

        logger.info(f"✅ Validation complete: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")
        return validation_results

    async def _test_connection_suite(self) -> List[TestResult]:
        """Test connection and basic functionality"""
        results = []

        # Test 1: Basic connection
        start_time = time.time()
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                models = response.json().get("models", [])
                results.append(TestResult(
                    test_name="Basic Connection",
                    success=True,
                    duration=duration,
                    score=1.0,
                    details={"available_models": len(models)}
                ))
            else:
                results.append(TestResult(
                    test_name="Basic Connection",
                    success=False,
                    duration=duration,
                    score=0.0,
                    details={"status_code": response.status_code},
                    error=f"HTTP {response.status_code}"
                ))
        except Exception as e:
            results.append(TestResult(
                test_name="Basic Connection",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        # Test 2: Model availability
        start_time = time.time()
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]

                required_models = self.config.get("claudia", {}).get("models", {})
                available_required = sum(1 for model in required_models.values() if model in model_names)

                score = available_required / len(required_models) if required_models else 0

                results.append(TestResult(
                    test_name="Model Availability",
                    success=score >= 0.5,
                    duration=duration,
                    score=score,
                    details={
                        "required_models": list(required_models.values()),
                        "available_models": model_names,
                        "availability_rate": score
                    }
                ))
            else:
                results.append(TestResult(
                    test_name="Model Availability",
                    success=False,
                    duration=duration,
                    score=0.0,
                    details={"status_code": response.status_code},
                    error=f"HTTP {response.status_code}"
                ))
        except Exception as e:
            results.append(TestResult(
                test_name="Model Availability",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        return results

    async def _test_model_suite(self) -> List[TestResult]:
        """Test model functionality"""
        results = []

        # Test 1: Basic generation
        start_time = time.time()
        try:
            model_name = self.config.get("claudia", {}).get("models", {}).get("primary", "llama3.2:latest")

            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model_name,
                    "prompt": "What is 2+2?",
                    "stream": False,
                    "options": {"num_predict": 50}
                }

                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    duration = time.time() - start_time

                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response", "")

                        # Check if response contains expected answer
                        success = "4" in response_text or "four" in response_text.lower()
                        score = 1.0 if success else 0.5

                        results.append(TestResult(
                            test_name="Basic Generation",
                            success=success,
                            duration=duration,
                            score=score,
                            details={
                                "model": model_name,
                                "response": response_text[:100],
                                "response_length": len(response_text)
                            }
                        ))
                    else:
                        results.append(TestResult(
                            test_name="Basic Generation",
                            success=False,
                            duration=duration,
                            score=0.0,
                            details={"status_code": response.status},
                            error=f"HTTP {response.status}"
                        ))
        except Exception as e:
            results.append(TestResult(
                test_name="Basic Generation",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        # Test 2: Trading-specific generation
        start_time = time.time()
        try:
            model_name = self.config.get("claudia", {}).get("models", {}).get("primary", "llama3.2:latest")

            trading_prompt = """Analyze this crypto market data and provide a trading recommendation:

            Token: SOL/USDC
            Price: $95.50
            24h Change: +3.2%
            Volume: $450M
            RSI: 65

            Respond with: BUY, SELL, or HOLD"""

            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model_name,
                    "prompt": trading_prompt,
                    "stream": False,
                    "options": self.config.get("claudia", {}).get("parameters", {})
                }

                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    duration = time.time() - start_time

                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response", "").upper()

                        # Check if response contains trading recommendation
                        has_recommendation = any(word in response_text for word in ["BUY", "SELL", "HOLD"])
                        has_analysis = any(word in response_text for word in ["RSI", "VOLUME", "PRICE"])

                        score = 0.5 if has_recommendation else 0
                        score += 0.5 if has_analysis else 0

                        results.append(TestResult(
                            test_name="Trading Generation",
                            success=has_recommendation,
                            duration=duration,
                            score=score,
                            details={
                                "model": model_name,
                                "response": response_text[:200],
                                "has_recommendation": has_recommendation,
                                "has_analysis": has_analysis
                            }
                        ))
                    else:
                        results.append(TestResult(
                            test_name="Trading Generation",
                            success=False,
                            duration=duration,
                            score=0.0,
                            details={"status_code": response.status},
                            error=f"HTTP {response.status}"
                        ))
        except Exception as e:
            results.append(TestResult(
                test_name="Trading Generation",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        return results

    async def _test_performance_suite(self) -> List[TestResult]:
        """Test performance characteristics"""
        results = []

        # Test 1: Response time
        start_time = time.time()
        try:
            model_name = self.config.get("claudia", {}).get("models", {}).get("primary", "llama3.2:latest")

            # Test multiple requests
            response_times = []
            for i in range(5):
                request_start = time.time()

                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_name,
                        "prompt": f"Analyze crypto market trend #{i+1}",
                        "stream": False,
                        "options": {"num_predict": 100}
                    }

                    async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                        if response.status == 200:
                            await response.json()
                            response_times.append(time.time() - request_start)
                        else:
                            response_times.append(float('inf'))

            duration = time.time() - start_time
            avg_response_time = np.mean(response_times) if response_times else float('inf')

            # Score based on response time (< 3s = 1.0, < 5s = 0.8, < 10s = 0.5, else 0.0)
            if avg_response_time < 3:
                score = 1.0
            elif avg_response_time < 5:
                score = 0.8
            elif avg_response_time < 10:
                score = 0.5
            else:
                score = 0.0

            results.append(TestResult(
                test_name="Response Time",
                success=avg_response_time < 10,
                duration=duration,
                score=score,
                details={
                    "average_response_time": avg_response_time,
                    "min_response_time": min(response_times) if response_times else 0,
                    "max_response_time": max(response_times) if response_times else 0,
                    "response_times": response_times
                }
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="Response Time",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        # Test 2: Concurrent requests
        start_time = time.time()
        try:
            model_name = self.config.get("claudia", {}).get("models", {}).get("primary", "llama3.2:latest")

            async def concurrent_request(session, prompt):
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 50}
                }

                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None

            async with aiohttp.ClientSession() as session:
                tasks = [
                    concurrent_request(session, f"Quick market analysis {i}")
                    for i in range(3)
                ]

                results_list = await asyncio.gather(*tasks, return_exceptions=True)

                duration = time.time() - start_time
                successful_requests = sum(1 for r in results_list if r is not None and not isinstance(r, Exception))

                score = successful_requests / len(tasks)

                results.append(TestResult(
                    test_name="Concurrent Requests",
                    success=successful_requests >= 2,
                    duration=duration,
                    score=score,
                    details={
                        "total_requests": len(tasks),
                        "successful_requests": successful_requests,
                        "success_rate": score
                    }
                ))
        except Exception as e:
            results.append(TestResult(
                test_name="Concurrent Requests",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        return results

    async def _test_trading_integration_suite(self) -> List[TestResult]:
        """Test trading-specific integrations"""
        results = []

        # Test 1: Market analysis integration
        start_time = time.time()
        try:
            # Simulate importing and using ClaudiaAIIntegration
            from claudia_enhanced_trading_system import ClaudiaAIIntegration, MarketContext

            claudia = ClaudiaAIIntegration()
            await claudia.initialize()

            # Test market analysis
            market_context = MarketContext(
                symbol="SOL/USDC",
                current_price=95.50,
                price_change_24h=3.2,
                volume_24h=450000000,
                market_cap=45000000000,
                rsi=65.0,
                macd=0.45,
                bollinger_position=0.7,
                volume_profile="High",
                social_sentiment="Positive",
                news_sentiment="Neutral"
            )

            analysis = await claudia.analyze_market_conditions(market_context)
            duration = time.time() - start_time

            # Check analysis quality
            has_sentiment = analysis.market_sentiment in ["BULLISH", "BEARISH", "NEUTRAL"]
            has_recommendation = analysis.trading_recommendation in ["BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"]
            has_confidence = 0 <= analysis.confidence_score <= 1
            has_risk = 0 <= analysis.risk_assessment <= 1

            score = sum([has_sentiment, has_recommendation, has_confidence, has_risk]) / 4

            results.append(TestResult(
                test_name="Market Analysis Integration",
                success=score >= 0.75,
                duration=duration,
                score=score,
                details={
                    "sentiment": analysis.market_sentiment,
                    "recommendation": analysis.trading_recommendation,
                    "confidence": analysis.confidence_score,
                    "risk": analysis.risk_assessment,
                    "has_sentiment": has_sentiment,
                    "has_recommendation": has_recommendation,
                    "has_confidence": has_confidence,
                    "has_risk": has_risk
                }
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="Market Analysis Integration",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        return results

    async def _test_advanced_features_suite(self) -> List[TestResult]:
        """Test advanced features"""
        results = []

        # Test 1: Caching functionality
        start_time = time.time()
        try:
            model_name = self.config.get("claudia", {}).get("models", {}).get("primary", "llama3.2:latest")

            # Make same request twice
            prompt = "What is the current crypto market sentiment?"

            # First request
            first_start = time.time()
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 100}
                }

                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        first_result = await response.json()
                        first_time = time.time() - first_start
                    else:
                        first_result = None
                        first_time = float('inf')

            # Second request (should be potentially cached)
            second_start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        second_result = await response.json()
                        second_time = time.time() - second_start
                    else:
                        second_result = None
                        second_time = float('inf')

            duration = time.time() - start_time

            # Check if second request was faster (potential caching)
            cache_improvement = (first_time - second_time) / first_time if first_time > 0 else 0
            success = first_result is not None and second_result is not None
            score = 1.0 if success else 0.0

            results.append(TestResult(
                test_name="Advanced Features",
                success=success,
                duration=duration,
                score=score,
                details={
                    "first_request_time": first_time,
                    "second_request_time": second_time,
                    "cache_improvement": cache_improvement,
                    "both_successful": success
                }
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="Advanced Features",
                success=False,
                duration=time.time() - start_time,
                score=0.0,
                details={},
                error=str(e)
            ))

        return results

    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Analyze test results
        test_results = validation_results.get("test_results", [])
        performance_metrics = validation_results.get("performance_metrics", {})

        # Response time recommendations
        avg_response_time = performance_metrics.get("average_response_time", 0)
        if avg_response_time > 5:
            recommendations.append("Consider optimizing model parameters or using a smaller model for better response times")

        # Success rate recommendations
        success_rate = performance_metrics.get("success_rate", 0)
        if success_rate < 0.8:
            recommendations.append("Review failed tests and consider system configuration adjustments")

        # Model-specific recommendations
        failed_tests = [r for r in test_results if not r.success]
        if any("Model Availability" in r.test_name for r in failed_tests):
            recommendations.append("Ensure required AI models are downloaded and available")

        if any("Connection" in r.test_name for r in failed_tests):
            recommendations.append("Check Ollama server status and network connectivity")

        # Performance recommendations
        if any("Concurrent" in r.test_name for r in failed_tests):
            recommendations.append("Consider increasing system resources or implementing request queuing")

        # General recommendations
        recommendations.extend([
            "Monitor Claudia performance in production environment",
            "Implement comprehensive logging for debugging",
            "Set up automated health checks",
            "Consider implementing fallback mechanisms for high availability"
        ])

        return recommendations

    async def create_validation_report(self) -> str:
        """Create comprehensive validation report"""
        logger.info("📊 Creating validation report...")

        validation_results = await self.run_comprehensive_validation()

        # Generate report
        report = f"""# Claudia AI Integration Validation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Status
**Status**: {validation_results['overall_status'].upper()}
**Success Rate**: {validation_results['performance_metrics']['success_rate']:.1%}
**Total Tests**: {validation_results['performance_metrics']['total_tests']}
**Passed Tests**: {validation_results['performance_metrics']['passed_tests']}

## Performance Metrics
- **Average Response Time**: {validation_results['performance_metrics']['average_response_time']:.2f}s
- **Average Score**: {validation_results['performance_metrics']['average_score']:.2f}

## Test Results
"""

        for result in validation_results['test_results']:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report += f"### {result.test_name}\n"
            report += f"- **Status**: {status}\n"
            report += f"- **Duration**: {result.duration:.2f}s\n"
            report += f"- **Score**: {result.score:.2f}\n"
            if result.error:
                report += f"- **Error**: {result.error}\n"
            report += f"- **Details**: {json.dumps(result.details, indent=2)}\n\n"

        report += f"""## Recommendations
{chr(10).join(f"💡 {rec}" for rec in validation_results['recommendations'])}

## Configuration Used
{yaml.dump(self.config, default_flow_style=False)}

## Next Steps
1. Address any failed tests
2. Implement recommended optimizations
3. Set up continuous monitoring
4. Plan for production deployment
"""

        # Save report
        report_path = Path("claudia_validation_report.md")
        with open(report_path, 'w') as f:
            f.write(report)

        logger.info(f"✅ Validation report saved to {report_path}")
        return report

async def main():
    """Main validation function"""
    validator = ClaudiaValidator()

    print("🧪 Claudia AI Integration Validator")
    print("=" * 50)

    try:
        # Run comprehensive validation
        await validator.create_validation_report()

        print("\n✅ Validation Complete!")
        print("Check 'claudia_validation_report.md' for detailed results")

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
