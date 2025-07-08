#!/usr/bin/env python3
"""
Context7 Full Integration - Real Implementation with SSE Support
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, AsyncGenerator
import aiohttp
import asyncio_sse
from dataclasses import dataclass, asdict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Context7Tool:
    """Context7 tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class Context7Response:
    """Context7 response wrapper"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Context7Client:
    """Real Context7 MCP client with SSE support"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.tools: Dict[str, Context7Tool] = {}
        self.initialized = False
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def initialize(self):
        """Initialize Context7 client with SSE support"""
        logger.info(f"🚀 Initializing Context7 client for {self.base_url}")
        
        # Create session with SSE headers
        self.session = aiohttp.ClientSession(
            headers={
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
        # Initialize connection
        success = await self._initialize_mcp()
        if success:
            self.initialized = True
            logger.info("✅ Context7 client initialized successfully")
        else:
            logger.error("❌ Failed to initialize Context7 client")
            
    async def _initialize_mcp(self) -> bool:
        """Initialize MCP connection with SSE"""
        try:
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "MCPVotsAGI",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            response = await self._send_sse_request(init_request)
            if response and response.success:
                # Send initialized notification
                await self._send_notification("notifications/initialized", {})
                
                # List available tools
                await self._list_tools()
                return True
                
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            
        return False
        
    async def _send_sse_request(self, request: Dict[str, Any]) -> Optional[Context7Response]:
        """Send SSE request to Context7"""
        try:
            # Convert request to JSON Lines format for SSE
            request_data = json.dumps(request) + "\n"
            
            async with self.session.post(
                f"{self.base_url}/mcp",
                data=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                }
            ) as resp:
                if resp.status == 200:
                    # Read SSE stream
                    async for event in self._read_sse_stream(resp):
                        if event.get("event") == "message":
                            data = json.loads(event.get("data", "{}"))
                            if "result" in data:
                                return Context7Response(
                                    success=True,
                                    data=data["result"]
                                )
                            elif "error" in data:
                                return Context7Response(
                                    success=False,
                                    error=data["error"].get("message", "Unknown error")
                                )
                else:
                    logger.error(f"SSE request failed with status {resp.status}")
                    
        except Exception as e:
            logger.error(f"SSE request error: {e}")
            
        return None
        
    async def _read_sse_stream(self, response) -> AsyncGenerator[Dict[str, Any], None]:
        """Read Server-Sent Events stream"""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    yield {"event": "message", "data": data}
                except json.JSONDecodeError:
                    logger.warning(f"Invalid SSE data: {line}")
                    
    async def _send_notification(self, method: str, params: Dict[str, Any]):
        """Send notification (no response expected)"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        try:
            await self.session.post(
                f"{self.base_url}/mcp",
                json=notification,
                headers={"Accept": "text/event-stream"}
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")
            
    async def _list_tools(self):
        """List available Context7 tools"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        response = await self._send_sse_request(request)
        if response and response.success:
            tools_data = response.data.get("tools", [])
            for tool_data in tools_data:
                tool = Context7Tool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    inputSchema=tool_data["inputSchema"]
                )
                self.tools[tool.name] = tool
                
            logger.info(f"📚 Discovered {len(self.tools)} Context7 tools")
            
    async def enrich_context(self, input_text: str, libraries: list) -> Optional[Dict[str, Any]]:
        """Enrich context with library documentation"""
        if not self.initialized:
            logger.error("Client not initialized")
            return None
            
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "enrich_context",
                "arguments": {
                    "input": input_text,
                    "libraries": libraries
                }
            },
            "id": 3
        }
        
        response = await self._send_sse_request(request)
        if response and response.success:
            return response.data
        else:
            logger.error(f"Enrichment failed: {response.error if response else 'No response'}")
            return None
            
    async def close(self):
        """Close client session"""
        if self.session:
            await self.session.close()
            

class Context7Server:
    """Context7 server manager"""
    
    def __init__(self, port: int = 3000):
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        
    async def start(self) -> bool:
        """Start Context7 MCP server with SSE transport"""
        try:
            # Kill any existing process on the port
            await self._kill_existing_process()
            
            # Start Context7 with SSE transport
            cmd = [
                "npx", "-y", "@upstash/context7-mcp",
                "--transport", "sse",
                "--port", str(self.port)
            ]
            
            logger.info(f"🚀 Starting Context7 server: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Verify server is running
            if await self._check_server_health():
                logger.info(f"✅ Context7 server started on port {self.port}")
                return True
            else:
                logger.error("❌ Context7 server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Context7 server: {e}")
            return False
            
    async def _kill_existing_process(self):
        """Kill any existing process on the port"""
        try:
            if sys.platform == "win32":
                # Windows: Find and kill process
                result = subprocess.run(
                    ["netstat", "-ano"],
                    capture_output=True,
                    text=True
                )
                
                for line in result.stdout.splitlines():
                    if f":{self.port}" in line and "LISTENING" in line:
                        parts = line.split()
                        pid = parts[-1]
                        subprocess.run(["taskkill", "/F", "/PID", pid])
                        logger.info(f"Killed existing process on port {self.port}")
                        await asyncio.sleep(1)
                        break
            else:
                # Unix-like: Use lsof
                subprocess.run(["lsof", "-ti", f":{self.port}", "|", "xargs", "kill", "-9"])
                
        except Exception as e:
            logger.debug(f"No existing process to kill: {e}")
            
    async def _check_server_health(self) -> bool:
        """Check if server is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://localhost:{self.port}/mcp",
                    headers={"Accept": "text/event-stream"}
                ) as resp:
                    # SSE endpoint should return 200 or 406 if headers are wrong
                    return resp.status in [200, 406]
        except:
            return False
            
    def stop(self):
        """Stop Context7 server"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info("🛑 Context7 server stopped")
            

class Context7Integration:
    """Full Context7 integration for MCPVotsAGI"""
    
    def __init__(self):
        self.server = Context7Server()
        self.client: Optional[Context7Client] = None
        
    async def setup(self) -> bool:
        """Setup Context7 integration"""
        logger.info("🔧 Setting up Context7 integration...")
        
        # Start server
        if not await self.server.start():
            return False
            
        # Initialize client
        self.client = Context7Client()
        await self.client.initialize()
        
        return self.client.initialized
        
    async def enrich_code_with_docs(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Enrich code with library documentation"""
        if not self.client:
            logger.error("Context7 not initialized")
            return {"error": "Not initialized"}
            
        # Detect libraries in code
        libraries = self._detect_libraries(code, language)
        logger.info(f"📚 Detected libraries: {libraries}")
        
        # Enrich with Context7
        result = await self.client.enrich_context(code, list(libraries))
        
        if result:
            return {
                "enriched": True,
                "libraries": list(libraries),
                "documentation": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "enriched": False,
                "libraries": list(libraries),
                "error": "Enrichment failed"
            }
            
    def _detect_libraries(self, code: str, language: str) -> set:
        """Detect libraries used in code"""
        libraries = set()
        
        if language == "python":
            # Python imports
            import_lines = [line for line in code.splitlines() if line.strip().startswith(('import ', 'from '))]
            for line in import_lines:
                parts = line.split()
                if parts[0] == 'import':
                    lib = parts[1].split('.')[0]
                    libraries.add(lib)
                elif parts[0] == 'from':
                    lib = parts[1].split('.')[0]
                    libraries.add(lib)
                    
        elif language == "javascript":
            # JavaScript imports
            import_lines = [line for line in code.splitlines() if 'import' in line or 'require(' in line]
            for line in import_lines:
                if 'from' in line:
                    # ES6 imports
                    parts = line.split('from')
                    if len(parts) > 1:
                        lib = parts[1].strip().strip(';').strip('"').strip("'")
                        libraries.add(lib)
                elif 'require(' in line:
                    # CommonJS
                    import re
                    matches = re.findall(r'require\([\'"]([^\'\"]+)[\'\"]', line)
                    libraries.update(matches)
                    
        return libraries
        
    async def test_integration(self) -> Dict[str, Any]:
        """Test Context7 integration"""
        logger.info("🧪 Testing Context7 integration...")
        
        test_results = {
            "server_started": False,
            "client_initialized": False,
            "tools_discovered": 0,
            "enrichment_works": False,
            "errors": []
        }
        
        try:
            # Test server start
            test_results["server_started"] = await self.server._check_server_health()
            
            # Test client initialization
            if self.client:
                test_results["client_initialized"] = self.client.initialized
                test_results["tools_discovered"] = len(self.client.tools)
                
                # Test enrichment
                test_code = """
import numpy as np
import pandas as pd

def process_data(df):
    return df.mean()
"""
                
                result = await self.enrich_code_with_docs(test_code)
                test_results["enrichment_works"] = result.get("enriched", False)
                
        except Exception as e:
            test_results["errors"].append(str(e))
            
        return test_results
        
    async def cleanup(self):
        """Cleanup Context7 integration"""
        if self.client:
            await self.client.close()
        self.server.stop()
        

# Real integration test
async def main():
    """Run real Context7 integration test"""
    integration = Context7Integration()
    
    try:
        # Setup
        success = await integration.setup()
        if not success:
            logger.error("❌ Context7 setup failed")
            return
            
        # Run tests
        test_results = await integration.test_integration()
        
        logger.info("📊 Test Results:")
        logger.info(f"  Server Started: {test_results['server_started']}")
        logger.info(f"  Client Initialized: {test_results['client_initialized']}")
        logger.info(f"  Tools Discovered: {test_results['tools_discovered']}")
        logger.info(f"  Enrichment Works: {test_results['enrichment_works']}")
        
        if test_results["errors"]:
            logger.error(f"  Errors: {test_results['errors']}")
            
        # Test real enrichment
        if test_results["enrichment_works"]:
            test_code = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
async def create_item(item: Item):
    await asyncio.sleep(1)
    return {"status": "created", "item": item}
"""
            
            logger.info("\n🔍 Testing real code enrichment...")
            result = await integration.enrich_code_with_docs(test_code, "python")
            
            if result.get("enriched"):
                logger.info("✅ Code successfully enriched with documentation!")
                logger.info(f"📚 Libraries detected: {result['libraries']}")
            else:
                logger.error("❌ Enrichment failed")
                
    finally:
        await integration.cleanup()
        

if __name__ == "__main__":
    asyncio.run(main())