#!/usr/bin/env python3
"""
Test DeepSeek Integration
========================
Quick test to verify DeepSeek model is working with MCPVotsAGI
"""

import asyncio
import json
import subprocess
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepSeekTest")

async def test_ollama():
    """Test if Ollama is running and has DeepSeek model"""
    logger.info("Testing Ollama connection...")
    
    try:
        # Check Ollama version
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✓ Ollama installed: {result.stdout.strip()}")
        else:
            logger.error("✗ Ollama not found")
            return False
            
        # List models
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL" in result.stdout:
            logger.info("✓ DeepSeek model found")
            return True
        else:
            logger.error("✗ DeepSeek model not found")
            logger.info("Available models:")
            print(result.stdout)
            return False
            
    except Exception as e:
        logger.error(f"Error testing Ollama: {e}")
        return False

async def test_deepseek_mcp():
    """Test DeepSeek MCP server"""
    logger.info("\nTesting DeepSeek MCP server...")
    
    try:
        async with websockets.connect("ws://localhost:3008") as ws:
            # Test general reasoning
            request = {
                "jsonrpc": "2.0",
                "method": "reasoning/execute",
                "params": {
                    "task_type": "general",
                    "prompt": "What is the best precious metal to invest in today?",
                    "temperature": 0.7
                },
                "id": 1
            }
            
            await ws.send(json.dumps(request))
            response = await ws.recv()
            data = json.loads(response)
            
            if "result" in data:
                logger.info("✓ DeepSeek MCP responding")
                logger.info(f"  Confidence: {data['result'].get('confidence', 0):.2%}")
                logger.info(f"  Response time: {data['result'].get('elapsed_time', 0):.2f}s")
                return True
            else:
                logger.error(f"✗ Unexpected response: {data}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Cannot connect to DeepSeek MCP: {e}")
        logger.info("  Make sure to start the server with: python servers/deepseek_ollama_mcp_server.py")
        return False

async def test_trading_analysis():
    """Test trading-specific reasoning"""
    logger.info("\nTesting trading analysis...")
    
    try:
        async with websockets.connect("ws://localhost:3008") as ws:
            request = {
                "jsonrpc": "2.0",
                "method": "reasoning/trading",
                "params": {
                    "prompt": "Analyze gold vs silver investment opportunity",
                    "portfolio": {
                        "USD": 10000,
                        "positions": {}
                    },
                    "risk_profile": "moderate"
                },
                "id": 2
            }
            
            await ws.send(json.dumps(request))
            response = await ws.recv()
            data = json.loads(response)
            
            if "result" in data:
                result = data["result"]
                rec = result.get("trading_recommendation", {})
                
                logger.info("✓ Trading analysis complete")
                logger.info(f"  Recommended action: {rec.get('action', 'N/A')}")
                logger.info(f"  Assets: {', '.join(rec.get('assets', []))}")
                logger.info(f"  Risk assessment: {rec.get('risk_assessment', 'N/A')}")
                
                return True
            else:
                logger.error("✗ No trading recommendation received")
                return False
                
    except Exception as e:
        logger.error(f"✗ Trading analysis failed: {e}")
        return False

async def test_model_performance():
    """Test model performance with multiple queries"""
    logger.info("\nTesting model performance...")
    
    queries = [
        "What factors affect gold prices?",
        "Compare gold ETFs vs physical gold",
        "Analyze silver industrial demand"
    ]
    
    try:
        async with websockets.connect("ws://localhost:3008") as ws:
            total_time = 0
            
            for i, query in enumerate(queries):
                request = {
                    "jsonrpc": "2.0",
                    "method": "reasoning/execute",
                    "params": {
                        "task_type": "trading",
                        "prompt": query,
                        "temperature": 0.5,
                        "max_tokens": 512
                    },
                    "id": i + 10
                }
                
                await ws.send(json.dumps(request))
                response = await ws.recv()
                data = json.loads(response)
                
                if "result" in data:
                    elapsed = data["result"].get("elapsed_time", 0)
                    total_time += elapsed
                    logger.info(f"  Query {i+1}: {elapsed:.2f}s")
                    
            avg_time = total_time / len(queries)
            logger.info(f"✓ Average response time: {avg_time:.2f}s")
            
            # Get status
            status_request = {
                "jsonrpc": "2.0",
                "method": "reasoning/status",
                "id": 99
            }
            
            await ws.send(json.dumps(status_request))
            response = await ws.recv()
            data = json.loads(response)
            
            if "result" in data:
                status = data["result"]
                logger.info(f"✓ Server status: {status.get('status', 'unknown')}")
                logger.info(f"  Total requests: {status['performance'].get('total_requests', 0)}")
                logger.info(f"  Cache hits: {status['performance'].get('cache_hits', 0)}")
                logger.info(f"  Average response: {status['performance'].get('average_response_time', 0):.2f}s")
                
            return True
            
    except Exception as e:
        logger.error(f"✗ Performance test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("  DeepSeek Integration Test Suite")
    print("=" * 60)
    
    results = {
        "ollama": await test_ollama(),
        "deepseek_mcp": await test_deepseek_mcp(),
        "trading": await test_trading_analysis(),
        "performance": await test_model_performance()
    }
    
    print("\n" + "=" * 60)
    print("  Test Results")
    print("=" * 60)
    
    for test, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test:20} {status}")
        
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✨ All tests passed! DeepSeek integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the logs above.")
        
        if not results["ollama"]:
            print("\nTo fix Ollama issues:")
            print("1. Install Ollama from https://ollama.ai")
            print("2. Pull the model: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL")
            
        if not results["deepseek_mcp"]:
            print("\nTo fix DeepSeek MCP issues:")
            print("1. Start the server: python servers/deepseek_ollama_mcp_server.py")
            print("2. Or use the launcher: python launch_with_deepseek.py")

if __name__ == "__main__":
    asyncio.run(main())