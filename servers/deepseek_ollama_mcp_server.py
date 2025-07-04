#!/usr/bin/env python3
"""
DeepSeek Ollama MCP Server for MCPVotsAGI
========================================
Advanced reasoning engine using local DeepSeek-R1-0528-Qwen3-8B-GGUF model
Provides intelligent reasoning for trading, security, and ecosystem management
"""

import asyncio
import json
import logging
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import websockets
import aiohttp
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DeepSeekMCP")

# DeepSeek Model Configuration
DEEPSEEK_MODEL = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_CONTEXT_SIZE = 8192  # Optimized for Q4_K_XL
REASONING_TEMPERATURE = 0.7
TRADING_TEMPERATURE = 0.3  # Lower temp for trading decisions

@dataclass
class ReasoningRequest:
    """Reasoning request structure"""
    id: str
    task_type: str  # 'trading', 'security', 'ecosystem', 'general'
    prompt: str
    context: Dict[str, Any]
    temperature: float
    max_tokens: int
    system_prompt: Optional[str] = None

@dataclass
class ReasoningResponse:
    """Reasoning response structure"""
    id: str
    result: str
    confidence: float
    reasoning_steps: List[str]
    metadata: Dict[str, Any]
    elapsed_time: float

class DeepSeekReasoningEngine:
    """Core reasoning engine using Ollama"""
    
    def __init__(self):
        self.model = DEEPSEEK_MODEL
        self.ollama_host = OLLAMA_HOST
        self.context_window = MODEL_CONTEXT_SIZE
        self.session = None
        self.reasoning_cache = {}  # Cache for repeated queries
        self.performance_metrics = {
            "total_requests": 0,
            "average_response_time": 0,
            "cache_hits": 0,
            "errors": 0
        }
        
    async def initialize(self):
        """Initialize Ollama connection and verify model"""
        try:
            # Check if Ollama is running
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/version") as resp:
                    if resp.status != 200:
                        raise Exception("Ollama not running")
                    
            # Verify model is available
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            
            if self.model not in result.stdout:
                logger.error(f"Model {self.model} not found in Ollama")
                raise Exception(f"Model {self.model} not available")
                
            logger.info(f"DeepSeek reasoning engine initialized with {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize reasoning engine: {e}")
            raise
            
    async def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Execute reasoning task"""
        start_time = time.time()
        
        try:
            # Check cache for similar queries
            cache_key = self._generate_cache_key(request)
            if cache_key in self.reasoning_cache:
                self.performance_metrics["cache_hits"] += 1
                cached_response = self.reasoning_cache[cache_key]
                cached_response.elapsed_time = time.time() - start_time
                return cached_response
                
            # Build enhanced prompt based on task type
            enhanced_prompt = self._build_enhanced_prompt(request)
            
            # Call Ollama API
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": enhanced_prompt,
                    "temperature": request.temperature,
                    "num_ctx": self.context_window,
                    "stream": False,
                    "options": {
                        "num_predict": request.max_tokens,
                        "stop": ["</reasoning>", "END_REASONING"]
                    }
                }
                
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload
                ) as resp:
                    if resp.status != 200:
                        raise Exception(f"Ollama API error: {resp.status}")
                        
                    result = await resp.json()
                    
            # Parse reasoning response
            response = self._parse_reasoning_response(
                request.id,
                result["response"],
                request.task_type
            )
            response.elapsed_time = time.time() - start_time
            
            # Update metrics
            self.performance_metrics["total_requests"] += 1
            self.performance_metrics["average_response_time"] = (
                (self.performance_metrics["average_response_time"] * 
                 (self.performance_metrics["total_requests"] - 1) + 
                 response.elapsed_time) / self.performance_metrics["total_requests"]
            )
            
            # Cache response
            self.reasoning_cache[cache_key] = response
            
            return response
            
        except Exception as e:
            logger.error(f"Reasoning error: {e}")
            self.performance_metrics["errors"] += 1
            
            return ReasoningResponse(
                id=request.id,
                result=f"Error: {str(e)}",
                confidence=0.0,
                reasoning_steps=[],
                metadata={"error": str(e)},
                elapsed_time=time.time() - start_time
            )
            
    def _build_enhanced_prompt(self, request: ReasoningRequest) -> str:
        """Build task-specific enhanced prompt"""
        
        # Base system prompts for different tasks
        system_prompts = {
            "trading": """You are an expert precious metals trading AI with deep knowledge of:
- Gold, silver, and mining stocks
- Market patterns and technical analysis
- Risk management and portfolio optimization
- Solana DeFi protocols and Jupiter aggregator
Your goal is to maximize returns while managing risk through intelligent trading decisions.
Always provide reasoning steps and confidence levels.""",
            
            "security": """You are a cybersecurity expert integrated with OpenCTI.
Analyze threats, IOCs, and security patterns. Provide actionable intelligence
for the MCPVotsAGI ecosystem. Consider MITRE ATT&CK framework in analysis.""",
            
            "ecosystem": """You are the MCPVotsAGI ecosystem architect. Optimize service
management, resource allocation, and system health. Ensure all MCP servers
work in harmony for maximum efficiency.""",
            
            "general": """You are DeepSeek, an advanced reasoning AI integrated with
MCPVotsAGI. Provide thoughtful, step-by-step analysis for complex problems."""
        }
        
        system_prompt = request.system_prompt or system_prompts.get(
            request.task_type, 
            system_prompts["general"]
        )
        
        # Build context-aware prompt
        context_str = json.dumps(request.context, indent=2) if request.context else ""
        
        enhanced_prompt = f"""<system>
{system_prompt}

Current MCPVotsAGI Context:
{context_str}
</system>

<task>
{request.prompt}
</task>

<reasoning>
Step-by-step reasoning:
"""
        
        return enhanced_prompt
        
    def _parse_reasoning_response(self, request_id: str, response: str, task_type: str) -> ReasoningResponse:
        """Parse and structure reasoning response"""
        
        # Extract reasoning steps
        reasoning_steps = []
        lines = response.strip().split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('<'):
                reasoning_steps.append(line.strip())
                
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, task_type)
        
        # Extract metadata
        metadata = {
            "task_type": task_type,
            "model": self.model,
            "response_length": len(response),
            "reasoning_steps_count": len(reasoning_steps)
        }
        
        # For trading tasks, extract specific signals
        if task_type == "trading":
            metadata.update(self._extract_trading_signals(response))
            
        return ReasoningResponse(
            id=request_id,
            result=response,
            confidence=confidence,
            reasoning_steps=reasoning_steps,
            metadata=metadata,
            elapsed_time=0  # Will be set by caller
        )
        
    def _calculate_confidence(self, response: str, task_type: str) -> float:
        """Calculate confidence score for response"""
        
        # Base confidence factors
        confidence = 0.5
        
        # Check for reasoning indicators
        if "therefore" in response.lower() or "thus" in response.lower():
            confidence += 0.1
        if "step" in response.lower() and ":" in response:
            confidence += 0.1
        if len(response) > 200:  # Detailed response
            confidence += 0.1
            
        # Task-specific adjustments
        if task_type == "trading":
            if any(word in response.lower() for word in ["buy", "sell", "hold"]):
                confidence += 0.1
            if "risk" in response.lower():
                confidence += 0.1
                
        return min(confidence, 0.95)  # Cap at 95%
        
    def _extract_trading_signals(self, response: str) -> Dict[str, Any]:
        """Extract trading signals from response"""
        
        signals = {
            "action": None,
            "assets": [],
            "risk_level": "medium"
        }
        
        # Simple extraction logic (can be enhanced)
        response_lower = response.lower()
        
        if "buy" in response_lower:
            signals["action"] = "buy"
        elif "sell" in response_lower:
            signals["action"] = "sell"
        else:
            signals["action"] = "hold"
            
        # Extract mentioned assets
        assets = ["gold", "silver", "gdx", "slv", "gld"]
        for asset in assets:
            if asset in response_lower:
                signals["assets"].append(asset.upper())
                
        return {"trading_signals": signals}
        
    def _generate_cache_key(self, request: ReasoningRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.task_type}:{request.prompt}:{json.dumps(request.context, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

class DeepSeekMCPServer:
    """MCP Server for DeepSeek reasoning"""
    
    def __init__(self, port: int = 3008):
        self.port = port
        self.reasoning_engine = DeepSeekReasoningEngine()
        self.clients = set()
        self.active_tasks = {}
        
        # Integration with other MCP servers
        self.mcp_connections = {
            "memory": "ws://localhost:3002",
            "trading": "ws://localhost:3005",
            "security": "ws://localhost:3007"
        }
        
    async def start(self):
        """Start the MCP server"""
        await self.reasoning_engine.initialize()
        
        server = await websockets.serve(
            self.handle_client,
            "localhost",
            self.port
        )
        
        logger.info(f"DeepSeek MCP Server started on ws://localhost:{self.port}")
        
        # Start background tasks
        asyncio.create_task(self.health_monitor())
        asyncio.create_task(self.sync_with_ecosystem())
        
        await server.wait_closed()
        
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            self.clients.remove(websocket)
            
    async def process_message(self, websocket, message):
        """Process incoming JSON-RPC messages"""
        try:
            data = json.loads(message)
            method = data.get("method", "")
            params = data.get("params", {})
            msg_id = data.get("id")
            
            # Route to appropriate handler
            if method == "reasoning/execute":
                await self.handle_reasoning_request(websocket, params, msg_id)
            elif method == "reasoning/trading":
                await self.handle_trading_reasoning(websocket, params, msg_id)
            elif method == "reasoning/security":
                await self.handle_security_reasoning(websocket, params, msg_id)
            elif method == "reasoning/ecosystem":
                await self.handle_ecosystem_reasoning(websocket, params, msg_id)
            elif method == "reasoning/status":
                await self.handle_status_request(websocket, msg_id)
            elif method == "ping":
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "result": "pong",
                    "id": msg_id
                }))
            else:
                await self.send_error(websocket, msg_id, f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await self.send_error(websocket, msg_id, str(e))
            
    async def handle_reasoning_request(self, websocket, params, msg_id):
        """Handle general reasoning request"""
        request = ReasoningRequest(
            id=msg_id,
            task_type=params.get("task_type", "general"),
            prompt=params.get("prompt", ""),
            context=params.get("context", {}),
            temperature=params.get("temperature", REASONING_TEMPERATURE),
            max_tokens=params.get("max_tokens", 2048)
        )
        
        response = await self.reasoning_engine.reason(request)
        
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "result": asdict(response),
            "id": msg_id
        }))
        
    async def handle_trading_reasoning(self, websocket, params, msg_id):
        """Handle trading-specific reasoning"""
        
        # Get current market context from trading MCP
        market_context = await self.get_market_context()
        
        request = ReasoningRequest(
            id=msg_id,
            task_type="trading",
            prompt=params.get("prompt", "Analyze current precious metals market"),
            context={
                "market_data": market_context,
                "portfolio": params.get("portfolio", {}),
                "risk_profile": params.get("risk_profile", "moderate")
            },
            temperature=TRADING_TEMPERATURE,
            max_tokens=params.get("max_tokens", 2048)
        )
        
        response = await self.reasoning_engine.reason(request)
        
        # Send response
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "result": {
                **asdict(response),
                "trading_recommendation": self.parse_trading_recommendation(response)
            },
            "id": msg_id
        }))
        
    async def handle_security_reasoning(self, websocket, params, msg_id):
        """Handle security analysis reasoning"""
        
        request = ReasoningRequest(
            id=msg_id,
            task_type="security",
            prompt=params.get("prompt", "Analyze security threats"),
            context={
                "threats": params.get("threats", []),
                "iocs": params.get("iocs", []),
                "system_state": params.get("system_state", {})
            },
            temperature=0.3,  # Low temperature for security analysis
            max_tokens=params.get("max_tokens", 2048)
        )
        
        response = await self.reasoning_engine.reason(request)
        
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "result": asdict(response),
            "id": msg_id
        }))
        
    async def handle_ecosystem_reasoning(self, websocket, params, msg_id):
        """Handle ecosystem optimization reasoning"""
        
        request = ReasoningRequest(
            id=msg_id,
            task_type="ecosystem",
            prompt=params.get("prompt", "Optimize ecosystem performance"),
            context={
                "services": params.get("services", {}),
                "resources": params.get("resources", {}),
                "performance": params.get("performance", {})
            },
            temperature=0.5,
            max_tokens=params.get("max_tokens", 2048)
        )
        
        response = await self.reasoning_engine.reason(request)
        
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "result": asdict(response),
            "id": msg_id
        }))
        
    async def handle_status_request(self, websocket, msg_id):
        """Handle status request"""
        status = {
            "status": "online",
            "model": DEEPSEEK_MODEL,
            "performance": self.reasoning_engine.performance_metrics,
            "connected_clients": len(self.clients),
            "cache_size": len(self.reasoning_engine.reasoning_cache)
        }
        
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "result": status,
            "id": msg_id
        }))
        
    async def get_market_context(self) -> Dict[str, Any]:
        """Get current market context from trading MCP"""
        try:
            # Connect to trading MCP server
            async with websockets.connect(self.mcp_connections["trading"]) as ws:
                await ws.send(json.dumps({
                    "jsonrpc": "2.0",
                    "method": "market/status",
                    "id": "market_context"
                }))
                
                response = await ws.recv()
                data = json.loads(response)
                return data.get("result", {})
                
        except Exception as e:
            logger.error(f"Failed to get market context: {e}")
            return {}
            
    def parse_trading_recommendation(self, response: ReasoningResponse) -> Dict[str, Any]:
        """Parse trading recommendation from reasoning response"""
        
        metadata = response.metadata.get("trading_signals", {})
        
        return {
            "action": metadata.get("action", "hold"),
            "assets": metadata.get("assets", []),
            "confidence": response.confidence,
            "risk_assessment": metadata.get("risk_level", "medium"),
            "reasoning_summary": response.reasoning_steps[:3] if response.reasoning_steps else []
        }
        
    async def send_error(self, websocket, msg_id, error_message):
        """Send error response"""
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": error_message
            },
            "id": msg_id
        }))
        
    async def health_monitor(self):
        """Monitor server health"""
        while True:
            try:
                # Log performance metrics
                metrics = self.reasoning_engine.performance_metrics
                logger.info(f"DeepSeek Performance: {metrics}")
                
                # Clear old cache entries
                if len(self.reasoning_engine.reasoning_cache) > 1000:
                    self.reasoning_engine.reasoning_cache.clear()
                    logger.info("Cleared reasoning cache")
                    
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                
    async def sync_with_ecosystem(self):
        """Sync with other MCP servers"""
        while True:
            try:
                # Announce presence to ecosystem
                for service, endpoint in self.mcp_connections.items():
                    try:
                        async with websockets.connect(endpoint) as ws:
                            await ws.send(json.dumps({
                                "jsonrpc": "2.0",
                                "method": "ecosystem/announce",
                                "params": {
                                    "service": "deepseek",
                                    "capabilities": ["reasoning", "trading", "security", "optimization"]
                                },
                                "id": f"announce_{service}"
                            }))
                    except:
                        pass  # Service might not be running
                        
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                logger.error(f"Ecosystem sync error: {e}")

async def main():
    """Main entry point"""
    server = DeepSeekMCPServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())