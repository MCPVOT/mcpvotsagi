#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start ALL MCP Servers
=====================
Comprehensive MCP server management with advanced features
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path
import json
import psutil
import socket
from datetime import datetime
import logging

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("MCPManager")

class MCPServerManager:
    """Manage all MCP servers"""
    
    def __init__(self):
        self.workspace = Path("C:/Workspace") if sys.platform == "win32" else Path("/mnt/c/Workspace")
        self.mcpvots = self.workspace / "MCPVots"
        self.mcpvots_agi = self.workspace / "MCPVotsAGI"
        
        # Load MCP configuration
        self.mcp_config = self._load_mcp_config()
        
        # MCP server implementations
        self.mcp_implementations = {
            "GitHub MCP": {
                "script": "mcp_github_server.py",
                "path": self.mcpvots / "servers",
                "port": 3001
            },
            "Memory MCP": {
                "script": "enhanced_memory_mcp_server.py",
                "path": self.mcpvots / "servers",
                "port": 3002,
                "features": ["knowledge-graph", "vector-store", "embeddings"]
            },
            "HuggingFace MCP": {
                "script": "mcp_huggingface_server.py",
                "path": self.mcpvots / "servers",
                "port": 3003
            },
            "SuperMemory MCP": {
                "script": "supermemory_mcp.js",
                "path": self.mcpvots / "servers",
                "port": 3004,
                "runtime": "node"
            },
            "Solana MCP": {
                "script": "solana_mcp_deepseek_integration.py",
                "path": self.mcpvots_agi,
                "port": 3005,
                "features": ["zk-proofs", "defi-analysis", "ai-transactions"]
            },
            "Browser Tools MCP": {
                "script": "browser_tools_mcp.py",
                "path": self.mcpvots / "servers",
                "port": 3006
            },
            "Trilogy AGI Gateway": {
                "script": "trilogy_agi_gateway.py",
                "path": self.mcpvots / "servers",
                "port": 8000,
                "features": ["multi-agent", "autonomous", "advanced-reasoning"]
            },
            "OWL Framework": {
                "script": "owl_framework_mcp.py",
                "path": self.mcpvots / "servers",
                "port": 8010
            },
            "OWL Semantic Reasoning": {
                "script": "owl_semantic_reasoning_mcp.py",
                "path": self.mcpvots / "servers",
                "port": 8011,
                "features": ["sparql", "ontology", "reasoning"]
            },
            "Agent File System": {
                "script": "agent_file_system_mcp.py",
                "path": self.mcpvots / "servers",
                "port": 8012
            },
            "DGM Evolution Engine": {
                "script": "dgm_evolution_server.py",
                "path": self.mcpvots / "servers",
                "port": 8013,
                "features": ["self-improvement", "godel-machine", "evolution"]
            },
            "DeerFlow Orchestrator": {
                "script": "deerflow_orchestrator_mcp.py",
                "path": self.mcpvots / "servers",
                "port": 8014
            },
            "Gemini CLI Service": {
                "script": "gemini_cli_http_server.py",
                "path": self.mcpvots,
                "port": 8015,
                "env": {"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")}
            },
            "n8n Integration Server": {
                "script": "oracle_n8n_integration_server.py",
                "path": self.mcpvots / "servers",
                "port": 8020
            },
            "Ollama Code Review MCP": {
                "script": "ollama_code_review_mcp.py",
                "path": self.mcpvots / "servers",
                "port": 8895
            },
            "Code Review Workflow": {
                "script": "code_review_workflow_integration.py",
                "path": self.mcpvots / "servers",
                "port": 8896
            }
        }
        
        self.processes = {}
        
    def _load_mcp_config(self):
        """Load MCP configuration"""
        config_path = self.mcpvots / "mcp-config.json"
        if config_path.exists():
            return json.loads(config_path.read_text())
        return {"servers": []}
        
    def _is_port_open(self, port):
        """Check if port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
        
    async def check_status(self):
        """Check status of all MCP servers"""
        print("="*80)
        print(" MCP SERVER STATUS CHECK")
        print("="*80)
        
        online = 0
        offline = 0
        
        for server in self.mcp_config.get("servers", []):
            name = server["name"]
            if name in self.mcp_implementations:
                impl = self.mcp_implementations[name]
                port = impl["port"]
                
                if self._is_port_open(port):
                    status = "🟢 ONLINE"
                    online += 1
                else:
                    status = "🔴 OFFLINE"
                    offline += 1
                    
                features = impl.get("features", [])
                feature_str = f" [{', '.join(features)}]" if features else ""
                
                print(f"{name:<30} Port {port:<5} {status}{feature_str}")
            else:
                print(f"{name:<30} ❓ No implementation found")
                
        print("-"*80)
        print(f"Total: {online} online, {offline} offline")
        print("="*80)
        
        return online, offline
        
    async def start_server(self, name, config):
        """Start a single MCP server"""
        try:
            script_path = config["path"] / config["script"]
            
            # Check if script exists
            if not script_path.exists():
                # Try alternative paths
                alt_paths = [
                    self.mcpvots / config["script"],
                    self.mcpvots / "servers" / config["script"],
                    self.mcpvots_agi / config["script"]
                ]
                
                for alt in alt_paths:
                    if alt.exists():
                        script_path = alt
                        break
                        
            if not script_path.exists():
                logger.error(f"Script not found for {name}: {config['script']}")
                return False
                
            # Check if already running
            if self._is_port_open(config["port"]):
                logger.info(f"✓ {name} already running on port {config['port']}")
                return True
                
            # Prepare command
            runtime = config.get("runtime", "python")
            if runtime == "node":
                cmd = ["node", str(script_path)]
            else:
                if sys.platform == "win32":
                    python_exe = str(self.workspace / ".venv/Scripts/python.exe")
                    if not Path(python_exe).exists():
                        python_exe = sys.executable
                else:
                    python_exe = sys.executable
                cmd = [python_exe, str(script_path)]
                
            # Environment variables
            env = os.environ.copy()
            if "env" in config:
                env.update(config["env"])
                
            logger.info(f"Starting {name}...")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=str(script_path.parent),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes[name] = process
            
            # Wait for startup
            await asyncio.sleep(3)
            
            # Check if started
            if process.poll() is None and self._is_port_open(config["port"]):
                logger.info(f"✓ {name} started successfully on port {config['port']}")
                return True
            else:
                logger.error(f"✗ {name} failed to start")
                if process.poll() is not None:
                    stderr = process.stderr.read().decode('utf-8', errors='ignore')
                    logger.error(f"  Error: {stderr[:200]}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return False
            
    async def start_all(self):
        """Start all MCP servers"""
        print("="*80)
        print(" STARTING ALL MCP SERVERS")
        print("="*80)
        
        # Group servers by priority
        priority_groups = {
            "core": ["Memory MCP", "GitHub MCP", "Trilogy AGI Gateway"],
            "ai": ["DGM Evolution Engine", "Gemini CLI Service", "Ollama Code Review MCP"],
            "blockchain": ["Solana MCP"],
            "advanced": ["SuperMemory MCP", "OWL Framework", "OWL Semantic Reasoning"],
            "tools": ["Browser Tools MCP", "Agent File System", "DeerFlow Orchestrator"],
            "integration": ["HuggingFace MCP", "n8n Integration Server", "Code Review Workflow"]
        }
        
        for group_name, servers in priority_groups.items():
            print(f"\nStarting {group_name} servers...")
            
            for server_name in servers:
                if server_name in self.mcp_implementations:
                    await self.start_server(server_name, self.mcp_implementations[server_name])
                    
        print("\n" + "="*80)
        
        # Final status check
        await asyncio.sleep(2)
        await self.check_status()
        
    async def stop_all(self):
        """Stop all MCP servers"""
        logger.info("Stopping all MCP servers...")
        
        # Kill by process
        for name, process in self.processes.items():
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
        # Kill by port
        for name, config in self.mcp_implementations.items():
            port = config["port"]
            if self._is_port_open(port):
                if sys.platform == "win32":
                    # Find and kill process on Windows
                    result = subprocess.run(
                        f'netstat -ano | findstr :{port}',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 5 and 'LISTENING' in line:
                                pid = int(parts[-1])
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                                logger.info(f"Killed process on port {port}")
                                
        logger.info("All MCP servers stopped")
        
    def print_features(self):
        """Print advanced features of each MCP"""
        print("\n" + "="*80)
        print(" MCP ADVANCED FEATURES")
        print("="*80)
        
        features_map = {
            "Memory MCP": """
  • Knowledge Graph Integration (Neo4j compatible)
  • Vector Store with embeddings
  • Episodic, Semantic, and Procedural memory
  • FAISS indexing for similarity search
  • Memory consolidation and pruning
            """,
            "SuperMemory MCP": """
  • JavaScript-based with 2000 memory limit
  • Context-aware personalization
  • Semantic search capabilities
  • Cross-session persistence
            """,
            "DGM Evolution Engine": """
  • Gödel Machine implementation
  • Self-modification with proof verification
  • Genetic algorithm evolution
  • Meta-learning from experiences
  • 70% success rate for improvement proofs
            """,
            "Solana MCP": """
  • Zero-Knowledge proof generation
  • DeepSeek R1 integration for AI reasoning
  • DeFi opportunity analysis
  • Smart contract interaction
  • Transaction simulation
            """,
            "OWL Semantic Reasoning": """
  • SPARQL query support
  • Ontology management
  • Description Logic reasoning
  • RDF triple store
  • Knowledge inference
            """,
            "Trilogy AGI Gateway": """
  • Multi-agent orchestration
  • Autonomous task execution
  • Advanced reasoning chains
  • Cross-model consensus
  • Self-organizing agent networks
            """
        }
        
        for name, features in features_map.items():
            print(f"\n{name}:{features}")
            
        print("="*80)

async def main():
    """Main entry point"""
    manager = MCPServerManager()
    
    import argparse
    parser = argparse.ArgumentParser(description="MCP Server Manager")
    parser.add_argument("command", choices=["start", "stop", "status", "features"], 
                       help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "start":
        await manager.start_all()
    elif args.command == "stop":
        await manager.stop_all()
    elif args.command == "status":
        await manager.check_status()
    elif args.command == "features":
        manager.print_features()
        
    # Keep running if started
    if args.command == "start":
        print("\nAll MCP servers running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(60)
                # Periodic health check
                online, offline = await manager.check_status()
                if offline > 0:
                    logger.warning(f"{offline} servers offline, attempting restart...")
                    # Restart offline servers
                    for name, impl in manager.mcp_implementations.items():
                        if not manager._is_port_open(impl["port"]):
                            await manager.start_server(name, impl)
        except KeyboardInterrupt:
            await manager.stop_all()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python start_all_mcp_servers.py [start|stop|status|features]")
        sys.exit(1)
        
    asyncio.run(main())