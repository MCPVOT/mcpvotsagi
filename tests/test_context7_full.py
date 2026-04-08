#!/usr/bin/env python3
"""
Comprehensive Context7 Test - Verify full functionality
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

# Test all three integration methods
from context7_stdio_integration import Context7RealIntegration
from context7_http_client import Context7HTTPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_prerequisites():
    """Check if Context7 is available"""
    logger.info("🔍 Checking prerequisites...")
    
    # Check if npx is available
    try:
        result = subprocess.run(["npx", "--version"], capture_output=True, text=True)
        logger.info(f"  ✅ npx version: {result.stdout.strip()}")
    except Exception:
        logger.error("  ❌ npx not found - please install Node.js")
        return False
        
    # Check if Context7 package exists
    try:
        result = subprocess.run(
            ["npm", "view", "@upstash/context7-mcp", "version"],
            capture_output=True,
            text=True
        )
        logger.info(f"  ✅ Context7 MCP version: {result.stdout.strip()}")
    except Exception:
        logger.warning("  ⚠️ Cannot check Context7 version")
        
    return True


def test_stdio_integration():
    """Test stdio integration (default mode)"""
    logger.info("\n🧪 Testing STDIO Integration (Default Mode)")
    logger.info("-" * 50)
    
    integration = Context7RealIntegration()
    
    try:
        # Start integration
        if not integration.start():
            logger.error("❌ Failed to start Context7 via stdio")
            return False
            
        logger.info("✅ Context7 started successfully")
        
        # Test code enrichment
        test_code = """
import tensorflow as tf
import keras
from transformers import pipeline

# Create a simple neural network
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Use HuggingFace pipeline
classifier = pipeline("sentiment-analysis")
result = classifier("I love using Context7!")
"""
        
        logger.info("📝 Testing code enrichment...")
        result = integration.enrich_code(test_code, "python")
        
        logger.info(f"  Libraries detected: {result.get('libraries', [])}")
        logger.info(f"  Enrichment success: {result.get('success', False)}")
        
        if result.get('enrichment'):
            logger.info("  ✅ Documentation retrieved successfully!")
            return True
        else:
            logger.warning("  ⚠️ No enrichment data received")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during stdio test: {e}")
        return False
        
    finally:
        integration.stop()
        

async def test_http_integration():
    """Test HTTP/SSE integration"""
    logger.info("\n🧪 Testing HTTP/SSE Integration")
    logger.info("-" * 50)
    
    # Start Context7 with SSE transport
    process = subprocess.Popen(
        ["npx", "-y", "@upstash/context7-mcp", "--transport", "sse", "--port", "3001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    await asyncio.sleep(3)
    
    try:
        async with Context7HTTPClient("http://localhost:3001") as client:
            # Initialize
            if not await client.initialize():
                logger.error("❌ Failed to initialize HTTP client")
                return False
                
            logger.info("✅ HTTP client initialized")
            
            # List tools
            tools = await client.list_tools()
            logger.info(f"  Found {len(tools)} tools")
            
            # Test enrichment
            test_code = """
const express = require('express');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

const app = express();

// Connect to MongoDB
mongoose.connect('mongodb://localhost/myapp');

// JWT middleware
app.use((req, res, next) => {
    const token = req.headers.authorization;
    if (token) {
        jwt.verify(token, 'secret', (err, decoded) => {
            if (!err) req.user = decoded;
            next();
        });
    } else {
        next();
    }
});
"""
            
            result = await client.enrich_context(test_code, ["express", "mongoose", "jsonwebtoken"])
            
            if result:
                logger.info("  ✅ HTTP enrichment successful!")
                return True
            else:
                logger.warning("  ⚠️ HTTP enrichment failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error during HTTP test: {e}")
        return False
        
    finally:
        process.terminate()
        

def run_comprehensive_test():
    """Run comprehensive Context7 tests"""
    logger.info("🚀 CONTEXT7 COMPREHENSIVE TEST SUITE")
    logger.info("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("❌ Prerequisites check failed")
        return
        
    # Track results
    results = {
        "stdio": False,
        "http": False
    }
    
    # Test 1: STDIO (default)
    try:
        results["stdio"] = test_stdio_integration()
    except Exception as e:
        logger.error(f"STDIO test exception: {e}")
        
    # Test 2: HTTP/SSE
    try:
        results["http"] = asyncio.run(test_http_integration())
    except Exception as e:
        logger.error(f"HTTP test exception: {e}")
        
    # Summary
    logger.info("\n📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  STDIO Integration: {'✅ PASSED' if results['stdio'] else '❌ FAILED'}")
    logger.info(f"  HTTP Integration:  {'✅ PASSED' if results['http'] else '❌ FAILED'}")
    
    if all(results.values()):
        logger.info("\n🎉 ALL TESTS PASSED! Context7 is fully functional!")
    else:
        logger.info("\n⚠️ Some tests failed. Check the logs above.")
        
    return results


def create_mcp_config():
    """Create MCP configuration for Context7"""
    config = {
        "mcpServers": {
            "context7": {
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp"],
                "env": {
                    "UPSTASH_VECTOR_REST_URL": "${UPSTASH_VECTOR_REST_URL}",
                    "UPSTASH_VECTOR_REST_TOKEN": "${UPSTASH_VECTOR_REST_TOKEN}"
                }
            }
        }
    }
    
    config_path = Path("claude_desktop_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    logger.info(f"📄 Created MCP config at {config_path}")
    logger.info("  Add this to your Claude Desktop settings")
    

if __name__ == "__main__":
    # Run tests
    results = run_comprehensive_test()
    
    # Create config if tests pass
    if results.get("stdio", False):
        logger.info("\n📝 Creating MCP configuration...")
        create_mcp_config()