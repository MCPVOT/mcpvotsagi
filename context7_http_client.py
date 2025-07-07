#!/usr/bin/env python3
"""
Context7 HTTP Client - Direct HTTP interface for Context7 MCP
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Context7HTTPClient:
    """Direct HTTP client for Context7 MCP server"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_id = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
        
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send JSON-RPC request to Context7"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._next_id()
        }
        
        logger.info(f"📤 Sending request: {method}")
        
        try:
            # Try HTTP transport first
            async with self.session.post(
                f"{self.base_url}/mcp",
                json=request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    logger.info(f"✅ Response received for {method}")
                    return result
                elif resp.status == 406:
                    # Server wants SSE, try with event-stream
                    return await self._send_sse_request(request)
                else:
                    logger.error(f"❌ Request failed with status {resp.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
            
    async def _send_sse_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send request with SSE transport"""
        try:
            async with self.session.post(
                f"{self.base_url}/mcp",
                data=json.dumps(request) + "\n",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache"
                }
            ) as resp:
                if resp.status == 200:
                    # Read SSE response
                    full_response = ""
                    async for data in resp.content:
                        line = data.decode('utf-8').strip()
                        if line.startswith('data: '):
                            full_response += line[6:]
                            
                    if full_response:
                        return json.loads(full_response)
                        
        except Exception as e:
            logger.error(f"SSE request error: {e}")
            
        return None
        
    async def initialize(self) -> bool:
        """Initialize MCP connection"""
        result = await self.send_request(
            "initialize",
            {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "Context7HTTPClient",
                    "version": "1.0.0"
                }
            }
        )
        
        if result and "result" in result:
            logger.info("✅ MCP initialized successfully")
            
            # Send initialized notification
            await self.send_request("notifications/initialized", {})
            return True
            
        return False
        
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        result = await self.send_request("tools/list")
        
        if result and "result" in result:
            tools = result["result"].get("tools", [])
            logger.info(f"📚 Found {len(tools)} tools")
            return tools
            
        return []
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a specific tool"""
        result = await self.send_request(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments
            }
        )
        
        if result and "result" in result:
            return result["result"]
            
        return None
        
    async def enrich_context(self, input_text: str, libraries: List[str]) -> Optional[Dict[str, Any]]:
        """Enrich context with library documentation"""
        return await self.call_tool(
            "enrich_context",
            {
                "input": input_text,
                "libraries": libraries
            }
        )


# Standalone test function
async def test_context7_http():
    """Test Context7 via HTTP"""
    logger.info("🧪 Testing Context7 HTTP interface...")
    
    async with Context7HTTPClient() as client:
        # Initialize connection
        if not await client.initialize():
            logger.error("❌ Failed to initialize MCP")
            return
            
        # List tools
        tools = await client.list_tools()
        for tool in tools:
            logger.info(f"  Tool: {tool['name']} - {tool['description']}")
            
        # Test enrichment
        test_code = """
import react from 'react';
import { useState, useEffect } from 'react';
import axios from 'axios';

const MyComponent = () => {
    const [data, setData] = useState(null);
    
    useEffect(() => {
        axios.get('/api/data').then(res => setData(res.data));
    }, []);
    
    return <div>{data}</div>;
};
"""
        
        logger.info("\n🔍 Testing code enrichment...")
        result = await client.enrich_context(
            test_code,
            ["react", "axios"]
        )
        
        if result:
            logger.info("✅ Enrichment successful!")
            logger.info(f"📖 Result: {json.dumps(result, indent=2)}")
        else:
            logger.error("❌ Enrichment failed")
            

# Direct HTTP test without client
async def test_direct_http():
    """Test direct HTTP requests to Context7"""
    logger.info("🔬 Testing direct HTTP requests...")
    
    base_url = "http://localhost:3000"
    
    async with aiohttp.ClientSession() as session:
        # Test different endpoints
        endpoints = [
            ("/", "GET"),
            ("/mcp", "GET"),
            ("/mcp", "POST"),
            ("/mcp/v1", "GET"),
            ("/health", "GET")
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    async with session.get(f"{base_url}{endpoint}") as resp:
                        logger.info(f"  {method} {endpoint}: {resp.status}")
                else:
                    # POST with JSON-RPC
                    data = {
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": 1
                    }
                    
                    # Try different content types
                    for content_type, accept in [
                        ("application/json", "application/json"),
                        ("application/json", "text/event-stream"),
                        ("text/plain", "text/event-stream")
                    ]:
                        async with session.post(
                            f"{base_url}{endpoint}",
                            json=data,
                            headers={
                                "Content-Type": content_type,
                                "Accept": accept
                            }
                        ) as resp:
                            logger.info(f"  {method} {endpoint} (Accept: {accept}): {resp.status}")
                            
                            if resp.status == 200:
                                content = await resp.text()
                                logger.info(f"    Response: {content[:100]}...")
                                
            except Exception as e:
                logger.error(f"  {method} {endpoint}: Error - {e}")
                

# Start Context7 with HTTP transport
async def start_context7_http():
    """Start Context7 with HTTP transport"""
    import subprocess
    
    logger.info("🚀 Starting Context7 with HTTP transport...")
    
    cmd = ["npx", "-y", "@upstash/context7-mcp", "--transport", "http", "--port", "3000"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for startup
    await asyncio.sleep(5)
    
    return process


async def main():
    """Main test runner"""
    # Test 1: Direct HTTP
    await test_direct_http()
    
    # Test 2: HTTP Client
    await test_context7_http()
    
    # Test 3: Start with HTTP transport
    logger.info("\n🔄 Trying HTTP transport mode...")
    process = await start_context7_http()
    
    try:
        await test_context7_http()
    finally:
        process.terminate()
        

if __name__ == "__main__":
    asyncio.run(main())