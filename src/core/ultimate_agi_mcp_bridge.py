#!/usr/bin/env python3
"""
Ultimate AGI MCP Bridge
=======================
Allows DeepSeek-R1 to use MCP tools and exposes AGI as an MCP tool
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional
import logging
import aiohttp
import requests
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from memory.ultimate_memory_system import UltimateMemorySystem, MemoryType
except Exception:
    print("Memory system not available")
    UltimateMemorySystem = None

logger = logging.getLogger(__name__)

class MCPToolInterface:
    """Interface for MCP tools to be used by DeepSeek-R1"""

    def __init__(self, name: str, command: str, port: Optional[int] = None):
        self.name = name
        self.command = command
        self.port = port
        self.process = None
        self.is_running = False

    async def start(self):
        """Start the MCP server"""
        try:
            self.process = await asyncio.create_subprocess_shell(
                self.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.is_running = True
            logger.info(f"Started MCP tool: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start {self.name}: {e}")
            return False

    async def call(self, method: str, params: Dict = None) -> Any:
        """Call an MCP tool method"""
        if not self.is_running:
            await self.start()

        # MCP protocol communication
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": datetime.now().timestamp()
        }

        # Send to MCP server (simplified - actual implementation would use proper MCP protocol)
        return await self._send_request(request)

    async def _send_request(self, request: Dict) -> Any:
        """Send request to MCP server"""
        try:
            # Implement actual MCP protocol communication
            # This would connect to real MCP server via stdio or HTTP
            # For now, raise NotImplementedError until full MCP implementation
            raise NotImplementedError(f"MCP method {request['method']} not yet implemented for {self.name}")
        except Exception as e:
            logger.error(f"MCP request failed: {e}")
            raise

class UltimateAGIMCPBridge:
    """Bridge between Ultimate AGI System and MCP tools"""

    def __init__(self):
        self.workspace = Path("C:/Workspace/MCPVotsAGI")
        self.ollama_host = "http://localhost:11434"
        self.deepseek_model = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"

        # Initialize MCP tools that DeepSeek-R1 can use
        self.mcp_tools = {
            'filesystem': MCPToolInterface(
                'filesystem',
                'npx @modelcontextprotocol/server-filesystem'
            ),
            'github': MCPToolInterface(
                'github',
                'npx @modelcontextprotocol/server-github',
                port=3001
            ),
            'memory': MCPToolInterface(
                'memory',
                'npx @modelcontextprotocol/server-memory',
                port=3002
            ),
            'browser': MCPToolInterface(
                'browser',
                'npx @agentdeskai/browser-tools-mcp',
                port=3006
            ),
            'solana': MCPToolInterface(
                'solana',
                'python servers/solana_mcp_server.py',
                port=3005
            )
        }

        # Memory system for context
        if UltimateMemorySystem:
            self.memory = UltimateMemorySystem(self.workspace)
        else:
            self.memory = None

        logger.info("Ultimate AGI MCP Bridge initialized")

    async def process_with_deepseek(self, prompt: str, use_tools: list[str] = None) -> dict:
        """Process prompt with DeepSeek-R1 and optionally use MCP tools"""

        # 1. Enhance prompt with memory context
        context = await self._get_memory_context(prompt)
        enhanced_prompt = f"{context}\n\nUser request: {prompt}" if context else prompt

        # 2. Query DeepSeek-R1
        response = await self._query_deepseek(enhanced_prompt)

        # 3. Parse response for tool calls
        tool_calls = self._parse_tool_calls(response)

        # 4. Execute MCP tool calls if requested
        tool_results = {}
        if use_tools and tool_calls:
            for tool_call in tool_calls:
                if tool_call['tool'] in self.mcp_tools and tool_call['tool'] in use_tools:
                    result = await self.mcp_tools[tool_call['tool']].call(
                        tool_call['method'],
                        tool_call.get('params', {})
                    )
                    tool_results[tool_call['tool']] = result

        # 5. If we got tool results, ask DeepSeek to integrate them
        if tool_results:
            integration_prompt = f"""
Original request: {prompt}
Initial response: {response}

Tool results:
{json.dumps(tool_results, indent=2)}

Please provide a final response integrating these tool results.
"""
            final_response = await self._query_deepseek(integration_prompt)
        else:
            final_response = response

        # 6. Store in memory
        if self.memory:
            await self.memory.save_conversation(
                session_id=f"mcp_bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                role="user",
                content=prompt
            )
            await self.memory.save_conversation(
                session_id=f"mcp_bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                role="assistant",
                content=final_response
            )

        return {
            "response": final_response,
            "tool_results": tool_results,
            "model": self.deepseek_model
        }

    async def _get_memory_context(self, prompt: str) -> str:
        """Get relevant context from memory system"""
        if not self.memory:
            return ""

        try:
            # Search for relevant memories
            memories = await self.memory.recall_memory(prompt, top_k=3)

            # Search knowledge graph
            knowledge = await self.memory.query_knowledge(prompt)

            # Build context
            context_parts = []

            if memories:
                context_parts.append("Relevant memories:")
                for mem in memories:
                    context_parts.append(f"- {mem['content']}")

            if knowledge:
                context_parts.append("\nRelevant knowledge:")
                for k in knowledge[:3]:
                    context_parts.append(f"- {k['subject']} {k['predicate']} {k['object']}")

            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error getting memory context: {e}")
            return ""

    async def _query_deepseek(self, prompt: str) -> str:
        """Query DeepSeek-R1 via Ollama"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            if response.status_code != 200:
                return "Error: Ollama service not running"

            # Generate response
            generate_url = f"{self.ollama_host}/api/generate"
            data = {
                "model": self.deepseek_model,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(generate_url, json=data, timeout=30)
            if response.status_code == 200:
                return response.json().get('response', 'No response generated')
            else:
                return f"Error generating response: {response.status_code}"

        except Exception as e:
            logger.error(f"Error querying DeepSeek: {e}")
            return f"Error: {str(e)}"

    def _parse_tool_calls(self, response: str) -> list[Dict]:
        """Parse response for MCP tool calls"""
        tool_calls = []

        # Simple parsing - look for tool call patterns
        # In production, this would use more sophisticated parsing

        # Pattern: [TOOL:filesystem:read:{"path": "/some/path"}]
        import re
        pattern = r'\[TOOL:(\w+):(\w+):(.*?)\]'
        matches = re.findall(pattern, response)

        for match in matches:
            tool, method, params_str = match
            try:
                params = json.loads(params_str) if params_str else {}
            except Exception:
                params = {}

            tool_calls.append({
                'tool': tool,
                'method': method,
                'params': params
            })

        return tool_calls

    async def expose_as_mcp_server(self, port: int = 3333):
        """Expose Ultimate AGI as an MCP server"""
        from aiohttp import web

        async def handle_mcp_request(request):
            """Handle incoming MCP requests"""
            try:
                data = await request.json()
                method = data.get('method')
                params = data.get('params', {})

                # Route methods
                if method == 'chat':
                    result = await self.process_with_deepseek(
                        params.get('prompt', ''),
                        params.get('use_tools', [])
                    )
                elif method == 'memory_search':
                    if self.memory:
                        result = await self.memory.recall_memory(
                            params.get('query', ''),
                            params.get('top_k', 5)
                        )
                    else:
                        result = {"error": "Memory system not available"}
                elif method == 'knowledge_query':
                    if self.memory:
                        result = await self.memory.query_knowledge(
                            params.get('query', '')
                        )
                    else:
                        result = {"error": "Memory system not available"}
                else:
                    result = {"error": f"Unknown method: {method}"}

                return web.json_response({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": data.get('id')
                })

            except Exception as e:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": data.get('id', None)
                })

        app = web.Application()
        app.router.add_post('/mcp', handle_mcp_request)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()

        logger.info(f"Ultimate AGI MCP Server running on port {port}")

        # Keep running
        await asyncio.Future()

# MCP Server Configuration for Ultimate AGI
MCP_SERVER_CONFIG = {
    "name": "ultimate-agi",
    "version": "1.0.0",
    "description": "Ultimate AGI System with DeepSeek-R1 brain and full MCP integration",
    "methods": {
        "chat": {
            "description": "Chat with DeepSeek-R1 AGI",
            "params": {
                "prompt": {"type": "string", "required": True},
                "use_tools": {"type": "array", "items": {"type": "string"}}
            }
        },
        "memory_search": {
            "description": "Search the AGI memory system",
            "params": {
                "query": {"type": "string", "required": True},
                "top_k": {"type": "integer", "default": 5}
            }
        },
        "knowledge_query": {
            "description": "Query the knowledge graph",
            "params": {
                "query": {"type": "string", "required": True}
            }
        }
    }
}

async def main():
    """Main entry point"""
    bridge = UltimateAGIMCPBridge()

    # Example: Process with DeepSeek using MCP tools
    print("🔗 Testing Ultimate AGI MCP Bridge...")

    result = await bridge.process_with_deepseek(
        "What files are in the src directory?",
        use_tools=['filesystem']
    )

    print(f"\nResponse: {result['response']}")
    print(f"Tool results: {result['tool_results']}")

    # Start as MCP server
    print("\n🚀 Starting Ultimate AGI as MCP Server on port 3333...")
    await bridge.expose_as_mcp_server(port=3333)

if __name__ == "__main__":
    asyncio.run(main())