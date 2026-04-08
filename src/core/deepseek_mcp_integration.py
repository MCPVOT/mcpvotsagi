#!/usr/bin/env python3
"""
DeepSeek-R1 MCP Integration
============================
Enables DeepSeek-R1 to use all MCP tools seamlessly
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
import subprocess
import sys

logger = logging.getLogger(__name__)

class DeepSeekMCPOrchestrator:
    """Orchestrates MCP tool usage for DeepSeek-R1"""
    
    def __init__(self):
        self.mcp_configs = self._load_mcp_configs()
        self.active_servers = {}
        self.tool_capabilities = self._parse_capabilities()
        
    def _load_mcp_configs(self) -> dict:
        """Load MCP configurations"""
        configs = {}
        
        # Load from cline_mcp_settings.json
        cline_path = Path.home() / ".config" / "Claude" / "cline_mcp_settings.json"
        if cline_path.exists():
            with open(cline_path) as f:
                cline_config = json.load(f)
                configs.update(cline_config.get('mcpServers', {}))
        
        # Load from our config
        our_config = Path("C:/Workspace/MCPVotsAGI/config/ultimate_agi_mcp.json")
        if our_config.exists():
            with open(our_config) as f:
                our_mcp = json.load(f)
                configs.update(our_mcp.get('mcpServers', {}))
        
        return configs
    
    def _parse_capabilities(self) -> dict:
        """Parse all available MCP tool capabilities"""
        capabilities = {}
        
        for server_name, config in self.mcp_configs.items():
            if 'capabilities' in config:
                for method, details in config['capabilities'].items():
                    capabilities[f"{server_name}.{method}"] = {
                        'server': server_name,
                        'method': method,
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', {})
                    }
        
        return capabilities
    
    async def start_mcp_server(self, server_name: str) -> bool:
        """Start an MCP server"""
        if server_name in self.active_servers:
            return True
        
        config = self.mcp_configs.get(server_name)
        if not config:
            logger.error(f"No configuration for server: {server_name}")
            return False
        
        try:
            # Build command
            command = config.get('command', '')
            args = config.get('args', [])
            
            # Start server
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **config.get('environment', {})}
            )
            
            self.active_servers[server_name] = {
                'process': process,
                'port': config.get('port'),
                'config': config
            }
            
            logger.info(f"Started MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {server_name}: {e}")
            return False
    
    async def call_mcp_tool(self, tool_path: str, params: Dict = None) -> Any:
        """Call an MCP tool method"""
        # Parse tool path (e.g., "filesystem.read")
        if '.' not in tool_path:
            return {"error": f"Invalid tool path: {tool_path}"}
        
        server_name, method = tool_path.split('.', 1)
        
        # Ensure server is running
        if server_name not in self.active_servers:
            success = await self.start_mcp_server(server_name)
            if not success:
                return {"error": f"Failed to start server: {server_name}"}
        
        # Call the method
        return await self._send_mcp_request(server_name, method, params or {})
    
    async def _send_mcp_request(self, server: str, method: str, params: Dict) -> Any:
        """Send request to MCP server"""
        # This is a simplified version - actual implementation would use
        # proper MCP protocol over stdio/http/websocket
        
        server_info = self.active_servers.get(server)
        if not server_info:
            return {"error": f"Server not running: {server}"}
        
        # For demonstration - actual implementation would communicate with server
        return {
            "result": f"Called {method} on {server}",
            "params": params
        }
    
    def get_tool_prompt(self) -> str:
        """Generate prompt explaining available tools to DeepSeek"""
        prompt_parts = [
            "You have access to the following MCP tools:",
            ""
        ]
        
        for tool_path, info in self.tool_capabilities.items():
            prompt_parts.append(f"- {tool_path}: {info['description']}")
            if info['parameters']:
                prompt_parts.append(f"  Parameters: {json.dumps(info['parameters'], indent=4)}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "To use a tool, respond with:",
            "[MCP_TOOL:tool_name.method:{\"param1\": \"value1\", \"param2\": \"value2\"}]",
            "",
            "You can use multiple tools in one response.",
            "Example: [MCP_TOOL:filesystem.read:{\"path\": \"/config/settings.json\"}]"
        ])
        
        return "\n".join(prompt_parts)

class DeepSeekR1WithMCP:
    """Enhanced DeepSeek-R1 with full MCP capabilities"""
    
    def __init__(self):
        self.orchestrator = DeepSeekMCPOrchestrator()
        self.ollama_host = "http://localhost:11434"
        self.model = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
        
    async def process(self, user_prompt: str, allow_tools: bool = True) -> str:
        """Process user prompt with optional MCP tool usage"""
        
        # Build enhanced prompt
        if allow_tools:
            tool_prompt = self.orchestrator.get_tool_prompt()
            full_prompt = f"{tool_prompt}\n\nUser request: {user_prompt}"
        else:
            full_prompt = user_prompt
        
        # Get response from DeepSeek
        response = await self._query_deepseek(full_prompt)
        
        # Parse and execute tool calls
        if allow_tools:
            tool_results = await self._execute_tool_calls(response)
            
            if tool_results:
                # Ask DeepSeek to integrate results
                integration_prompt = f"""
Original request: {user_prompt}
Your response: {response}

Tool execution results:
{json.dumps(tool_results, indent=2)}

Please provide a final response integrating these results.
"""
                final_response = await self._query_deepseek(integration_prompt)
                return final_response
        
        return response
    
    async def _query_deepseek(self, prompt: str) -> str:
        """Query DeepSeek-R1 via Ollama"""
        import requests
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error querying DeepSeek: {e}"
    
    async def _execute_tool_calls(self, response: str) -> dict:
        """Parse and execute MCP tool calls from response"""
        import re
        
        results = {}
        
        # Find all tool calls
        pattern = r'\[MCP_TOOL:([^:]+):(.*?)\]'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for tool_path, params_str in matches:
            try:
                params = json.loads(params_str) if params_str else {}
                result = await self.orchestrator.call_mcp_tool(tool_path, params)
                results[tool_path] = result
            except Exception as e:
                results[tool_path] = {"error": str(e)}
        
        return results

# Example usage
async def demonstrate():
    """Demonstrate DeepSeek-R1 using MCP tools"""
    deepseek = DeepSeekR1WithMCP()
    
    examples = [
        "List all Python files in the src directory",
        "Check the current system memory usage and suggest optimizations",
        "Read the README.md file and summarize the project",
        "Search my memory for information about trading algorithms"
    ]
    
    for example in examples:
        print(f"\n{'='*60}")
        print(f"Prompt: {example}")
        print(f"{'='*60}")
        
        response = await deepseek.process(example)
        print(f"Response: {response}")

def create_mcp_enabled_deepseek():
    """Factory function to create MCP-enabled DeepSeek instance"""
    return DeepSeekR1WithMCP()

if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate())