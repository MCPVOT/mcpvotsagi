#!/usr/bin/env python3
"""
Service Deduplication and Consolidation Manager
=============================================
Identifies and eliminates redundant Python/Node services doing the same job.
Updates MCP memory integration and ensures single-source-of-truth architecture.
"""

import asyncio
import json
import subprocess
import sys
import socket
import psutil
import sqlite3
import redis
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceDeduplicator:
    """Identifies and consolidates duplicate services"""

    def __init__(self):
        self.workspace = Path("c:/Workspace/MCPVotsAGI")
        self.services_registry = {}
        self.duplicate_services = []
        self.consolidated_config = {}

        # Define service categories and their primary implementations
        self.service_categories = {
            'dashboard': {
                'description': 'Main AGI Dashboard Interface',
                'primary': 'unified_agi_portal.py',
                'port': 8000,
                'duplicates': [
                    'oracle_agi_v5_simple.py',
                    'oracle_agi_v5_complete.py',
                    'oracle_agi_v6_realtime_dashboard.py',
                    'oracle_agi_v7_full_dashboard.py',
                    'oracle_agi_v7_ultimate.py',
                    'oracle_agi_v8_ultimate_brain.py',
                    'oracle_agi_ultimate_unified.py',
                    'oracle_agi_ultimate_unified_v2.py'
                ]
            },
            'mcp_memory': {
                'description': 'MCP Memory Service with Redis',
                'primary': 'enhanced_mcp_memory_server.py',
                'port': 3002,
                'duplicates': [
                    'knowledge_base_system.py',
                    'memory_vault_mcp.py'
                ]
            },
            'a2a_communication': {
                'description': 'Agent-to-Agent Communication',
                'primary': 'a2a_enhanced_protocol.py',
                'port': 8001,
                'duplicates': [
                    'a2a_simple_protocol.py',
                    'basic_a2a_protocol.py'
                ]
            },
            'trading_system': {
                'description': 'AI Trading Backend',
                'primary': 'deepseek_trading_agent_enhanced.py',
                'port': 8004,
                'duplicates': [
                    'deepseek_trading_agent.py',
                    'dgm_trading_algorithms.py',
                    'dgm_trading_algorithms_v2.py',
                    'finnhub_integration.py'
                ]
            },
            'ecosystem_manager': {
                'description': 'System Orchestration',
                'primary': 'ecosystem_manager_v4_clean.py',
                'port': 8002,
                'duplicates': [
                    'ecosystem_manager.py',
                    'ecosystem_manager_v3.py',
                    'launch_stable_ecosystem.py',
                    'launch_simple_ecosystem.py',
                    'launch_enhanced_ecosystem.py'
                ]
            },
            'mcp_servers': {
                'description': 'MCP Tool Servers',
                'primary': 'consolidated_mcp_servers.py',
                'port_range': (3000, 3007),
                'duplicates': [
                    'deepseek_mcp_server.py',
                    'oracle_mcp_server.py'
                ]
            }
        }

    def scan_running_processes(self) -> Dict:
        """Scan for running Python processes that might be duplicates"""
        running_services = {}

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] in ['python.exe', 'python3', 'python']:
                    cmdline = proc.info['cmdline']
                    if len(cmdline) > 1:
                        script_path = Path(cmdline[1])
                        if script_path.suffix == '.py' and 'MCPVotsAGI' in str(script_path):
                            script_name = script_path.name

                            # Check for port usage
                            ports = []
                            try:
                                for conn in proc.connections():
                                    if conn.status == 'LISTEN':
                                        ports.append(conn.laddr.port)
                            except (psutil.AccessDenied, psutil.NoSuchProcess):
                                pass

                            running_services[script_name] = {
                                'pid': proc.info['pid'],
                                'cmdline': ' '.join(cmdline),
                                'ports': ports,
                                'category': self.categorize_service(script_name)
                            }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return running_services

    def categorize_service(self, script_name: str) -> Optional[str]:
        """Categorize a service script"""
        for category, info in self.service_categories.items():
            if script_name == info['primary']:
                return f"{category}_primary"
            elif script_name in info['duplicates']:
                return f"{category}_duplicate"
        return None

    def identify_duplicates(self) -> List[Dict]:
        """Identify duplicate services and consolidation opportunities"""
        running_services = self.scan_running_processes()
        duplicates = []

        print("\n🔍 SCANNING FOR DUPLICATE SERVICES")
        print("=" * 60)

        for category, info in self.service_categories.items():
            print(f"\n📂 {category.upper()}: {info['description']}")

            # Check if primary service is running
            primary_running = None
            duplicate_running = []

            for script, details in running_services.items():
                if script == info['primary']:
                    primary_running = details
                elif script in info['duplicates']:
                    duplicate_running.append((script, details))

            if primary_running:
                print(f"   ✅ Primary: {info['primary']} (PID: {primary_running['pid']}, Ports: {primary_running['ports']})")
            else:
                print(f"   ❌ Primary: {info['primary']} (NOT RUNNING)")

            if duplicate_running:
                print(f"   ⚠️  Duplicates found ({len(duplicate_running)}):")
                for script, details in duplicate_running:
                    print(f"      - {script} (PID: {details['pid']}, Ports: {details['ports']})")
                    duplicates.append({
                        'category': category,
                        'script': script,
                        'details': details,
                        'action': 'terminate'
                    })
            else:
                print(f"   ✅ No duplicates detected")

        return duplicates

    async def create_enhanced_mcp_memory(self):
        """Create enhanced MCP memory server with Redis integration"""
        mcp_memory_content = '''#!/usr/bin/env python3
"""
Enhanced MCP Memory Server with Redis Integration
===============================================
Unified memory service for MCPVotsAGI with Redis backend
"""

import asyncio
import json
import logging
import redis.asyncio as redis
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class EnhancedMCPMemoryServer:
    """Enhanced MCP Memory server with Redis backend"""

    def __init__(self, redis_host='localhost', redis_port=6379, redis_password='MCPVotsAGI2025!'):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_client = None
        self.memory_namespace = "mcp:memory"

    async def start(self):
        """Start the memory server"""
        try:
            # Connect to Redis
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            logging.info(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")

            return True

        except Exception as e:
            logging.error(f"❌ Failed to connect to Redis: {e}")
            return False

    async def store_memory(self, key: str, value: Any, category: str = "general") -> str:
        """Store memory with metadata"""
        memory_id = str(uuid.uuid4())
        memory_data = {
            "id": memory_id,
            "key": key,
            "value": json.dumps(value) if not isinstance(value, str) else value,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }

        # Store in Redis
        redis_key = f"{self.memory_namespace}:{memory_id}"
        await self.redis_client.hset(redis_key, mapping=memory_data)

        # Add to category index
        await self.redis_client.sadd(f"{self.memory_namespace}:categories:{category}", memory_id)

        # Add to key index
        await self.redis_client.set(f"{self.memory_namespace}:keys:{key}", memory_id)

        logging.info(f"📝 Stored memory: {key} -> {memory_id}")
        return memory_id

    async def retrieve_memory(self, key: str) -> Optional[Dict]:
        """Retrieve memory by key"""
        # Get memory ID from key index
        memory_id = await self.redis_client.get(f"{self.memory_namespace}:keys:{key}")
        if not memory_id:
            return None

        # Get memory data
        redis_key = f"{self.memory_namespace}:{memory_id}"
        memory_data = await self.redis_client.hgetall(redis_key)

        if memory_data:
            # Increment access count
            await self.redis_client.hincrby(redis_key, "access_count", 1)

            # Try to parse JSON value
            try:
                memory_data["value"] = json.loads(memory_data["value"])
            except (json.JSONDecodeError, TypeError):
                pass  # Keep as string

            logging.info(f"📖 Retrieved memory: {key}")
            return memory_data

        return None

    async def search_memories(self, category: str = None, limit: int = 100) -> List[Dict]:
        """Search memories by category"""
        if category:
            memory_ids = await self.redis_client.smembers(f"{self.memory_namespace}:categories:{category}")
        else:
            # Get all memory keys
            keys = await self.redis_client.keys(f"{self.memory_namespace}:*")
            memory_ids = [key.split(":")[-1] for key in keys if len(key.split(":")) == 3]

        memories = []
        for memory_id in list(memory_ids)[:limit]:
            redis_key = f"{self.memory_namespace}:{memory_id}"
            memory_data = await self.redis_client.hgetall(redis_key)
            if memory_data:
                try:
                    memory_data["value"] = json.loads(memory_data["value"])
                except (json.JSONDecodeError, TypeError):
                    pass
                memories.append(memory_data)

        return memories

    async def delete_memory(self, key: str) -> bool:
        """Delete memory by key"""
        memory_id = await self.redis_client.get(f"{self.memory_namespace}:keys:{key}")
        if not memory_id:
            return False

        # Get memory data to find category
        redis_key = f"{self.memory_namespace}:{memory_id}"
        memory_data = await self.redis_client.hgetall(redis_key)

        if memory_data:
            category = memory_data.get("category", "general")

            # Remove from category index
            await self.redis_client.srem(f"{self.memory_namespace}:categories:{category}", memory_id)

            # Remove key index
            await self.redis_client.delete(f"{self.memory_namespace}:keys:{key}")

            # Remove memory data
            await self.redis_client.delete(redis_key)

            logging.info(f"🗑️ Deleted memory: {key}")
            return True

        return False

    async def get_stats(self) -> Dict:
        """Get memory statistics"""
        total_memories = len(await self.redis_client.keys(f"{self.memory_namespace}:*"))
        categories = await self.redis_client.keys(f"{self.memory_namespace}:categories:*")
        category_stats = {}

        for cat_key in categories:
            category = cat_key.split(":")[-1]
            count = await self.redis_client.scard(cat_key)
            category_stats[category] = count

        return {
            "total_memories": total_memories,
            "categories": category_stats,
            "redis_info": {
                "host": self.redis_host,
                "port": self.redis_port,
                "connected": self.redis_client is not None
            }
        }

async def main():
    """Main MCP memory server"""
    memory_server = EnhancedMCPMemoryServer()

    if await memory_server.start():
        print("🧠 Enhanced MCP Memory Server started successfully!")
        print(f"   Redis: {memory_server.redis_host}:{memory_server.redis_port}")
        print(f"   Namespace: {memory_server.memory_namespace}")

        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\\n🛑 Shutting down MCP Memory Server...")
    else:
        print("❌ Failed to start MCP Memory Server")

if __name__ == "__main__":
    asyncio.run(main())
'''

        # Write the enhanced MCP memory server
        mcp_memory_path = self.workspace / "core" / "enhanced_mcp_memory_server.py"
        mcp_memory_path.parent.mkdir(parents=True, exist_ok=True)

        with open(mcp_memory_path, 'w', encoding='utf-8') as f:
            f.write(mcp_memory_content)

        print(f"✅ Created enhanced MCP memory server: {mcp_memory_path}")

    async def create_consolidated_mcp_servers(self):
        """Create consolidated MCP servers manager"""
        mcp_servers_content = '''#!/usr/bin/env python3
"""
Consolidated MCP Servers Manager
==============================
Single process to manage all MCP tool servers and avoid duplicates
"""

import asyncio
import subprocess
import sys
import signal
import json
from pathlib import Path
from datetime import datetime
import logging

class ConsolidatedMCPServers:
    """Manages all MCP servers in a single process"""

    def __init__(self):
        self.servers = {}
        self.running = False

        # Define MCP servers configuration
        self.mcp_config = {
            'filesystem': {
                'port': 3000,
                'command': ['npx', '@modelcontextprotocol/server-filesystem', '/path/to/allowed/dir'],
                'description': 'File system operations'
            },
            'github': {
                'port': 3001,
                'command': ['npx', '@modelcontextprotocol/server-github'],
                'description': 'GitHub integration'
            },
            'memory': {
                'port': 3002,
                'command': [sys.executable, 'core/enhanced_mcp_memory_server.py'],
                'description': 'Enhanced memory with Redis'
            },
            'browser': {
                'port': 3003,
                'command': ['npx', '@modelcontextprotocol/server-puppeteer'],
                'description': 'Browser automation'
            },
            'search': {
                'port': 3004,
                'command': ['npx', '@modelcontextprotocol/server-brave-search'],
                'description': 'Web search via Brave'
            },
            'solana': {
                'port': 3005,
                'command': ['npx', '@modelcontextprotocol/server-solana'],
                'description': 'Solana blockchain'
            },
            'huggingface': {
                'port': 3006,
                'command': ['npx', '@modelcontextprotocol/server-huggingface'],
                'description': 'HuggingFace models'
            }
        }

    async def start_server(self, name: str, config: dict) -> bool:
        """Start individual MCP server"""
        try:
            print(f"🚀 Starting {name} MCP server on port {config['port']}...")

            process = await asyncio.create_subprocess_exec(
                *config['command'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            self.servers[name] = {
                'process': process,
                'config': config,
                'started_at': datetime.now()
            }

            print(f"✅ {name} MCP server started (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"❌ Failed to start {name} MCP server: {e}")
            return False

    async def start_all_servers(self):
        """Start all MCP servers"""
        print("🎯 Starting Consolidated MCP Servers...")
        print("=" * 50)

        success_count = 0
        for name, config in self.mcp_config.items():
            if await self.start_server(name, config):
                success_count += 1
            await asyncio.sleep(1)  # Stagger starts

        print(f"\\n📊 MCP Servers Status: {success_count}/{len(self.mcp_config)} started")
        self.running = True

        return success_count > 0

    async def stop_all_servers(self):
        """Stop all MCP servers"""
        print("\\n🛑 Stopping all MCP servers...")

        for name, server_info in self.servers.items():
            try:
                process = server_info['process']
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5)
                print(f"✅ Stopped {name} MCP server")
            except asyncio.TimeoutError:
                process.kill()
                print(f"🔥 Force killed {name} MCP server")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")

        self.running = False

    async def monitor_servers(self):
        """Monitor server health and restart if needed"""
        while self.running:
            for name, server_info in list(self.servers.items()):
                process = server_info['process']
                if process.returncode is not None:
                    print(f"⚠️ {name} MCP server died, restarting...")
                    await self.start_server(name, server_info['config'])

            await asyncio.sleep(30)  # Check every 30 seconds

    async def run(self):
        """Main run loop"""
        if await self.start_all_servers():
            print("\\n🎉 All MCP servers are running!")
            print("\\nPress Ctrl+C to stop all servers")

            # Set up signal handlers
            def signal_handler(signum, frame):
                print("\\n🛑 Received shutdown signal...")
                self.running = False

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Start monitoring
            monitor_task = asyncio.create_task(self.monitor_servers())

            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            finally:
                await self.stop_all_servers()
        else:
            print("❌ Failed to start MCP servers")

async def main():
    """Main entry point"""
    servers_manager = ConsolidatedMCPServers()
    await servers_manager.run()

if __name__ == "__main__":
    asyncio.run(main())
'''

        # Write consolidated MCP servers
        mcp_servers_path = self.workspace / "core" / "consolidated_mcp_servers.py"

        with open(mcp_servers_path, 'w', encoding='utf-8') as f:
            f.write(mcp_servers_content)

        print(f"✅ Created consolidated MCP servers: {mcp_servers_path}")

    def terminate_duplicate_services(self, duplicates: List[Dict]) -> int:
        """Terminate identified duplicate services"""
        terminated_count = 0

        if not duplicates:
            print("\n✅ No duplicate services to terminate")
            return 0

        print(f"\n🔥 TERMINATING {len(duplicates)} DUPLICATE SERVICES")
        print("=" * 60)

        for duplicate in duplicates:
            try:
                pid = duplicate['details']['pid']
                script = duplicate['script']
                category = duplicate['category']

                # Kill the process
                proc = psutil.Process(pid)
                proc.terminate()

                # Wait for termination
                try:
                    proc.wait(timeout=5)
                    print(f"✅ Terminated {script} (PID: {pid}, Category: {category})")
                    terminated_count += 1
                except psutil.TimeoutExpired:
                    proc.kill()
                    print(f"🔥 Force killed {script} (PID: {pid})")
                    terminated_count += 1

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"❌ Failed to terminate {script}: {e}")

        return terminated_count

    async def update_port_configuration(self):
        """Update port configuration to reflect consolidated services"""
        config = {
            "consolidated_services": {
                "unified_agi_portal": {"port": 8000, "status": "primary"},
                "a2a_enhanced_protocol": {"port": 8001, "status": "primary"},
                "enhanced_mcp_memory": {"port": 3002, "status": "primary"},
                "deepseek_trading_enhanced": {"port": 8004, "status": "primary"},
                "ecosystem_manager_v4": {"port": 8002, "status": "primary"},
                "consolidated_mcp_servers": {"ports": "3000-3007", "status": "primary"}
            },
            "deprecated_services": {
                "oracle_agi_v5_*": "replaced by unified_agi_portal",
                "oracle_agi_v6_*": "replaced by unified_agi_portal",
                "oracle_agi_v7_*": "replaced by unified_agi_portal",
                "oracle_agi_v8_*": "replaced by unified_agi_portal",
                "oracle_agi_ultimate_*": "replaced by unified_agi_portal",
                "knowledge_base_system": "replaced by enhanced_mcp_memory",
                "basic_a2a_protocol": "replaced by a2a_enhanced_protocol",
                "dgm_trading_algorithms": "replaced by deepseek_trading_enhanced"
            },
            "redis_integration": {
                "host": "localhost",
                "port": 6379,
                "password": "MCPVotsAGI2025!",
                "databases": {
                    "0": "a2a_communication",
                    "1": "mcp_memory",
                    "2": "system_cache"
                }
            }
        }

        config_path = self.workspace / "consolidated_services_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, indent=2, fp=f)

        print(f"✅ Updated consolidated services config: {config_path}")

    async def run_consolidation(self):
        """Run the complete service consolidation process"""
        print("🚀 MCPVOTSAGI SERVICE DEDUPLICATION & CONSOLIDATION")
        print("=" * 80)
        print(f"Workspace: {self.workspace}")
        print(f"Time: {datetime.now().isoformat()}")

        # Step 1: Identify duplicates
        duplicates = self.identify_duplicates()

        # Step 2: Create enhanced services
        print("\n🔧 CREATING ENHANCED CONSOLIDATED SERVICES")
        print("=" * 60)
        await self.create_enhanced_mcp_memory()
        await self.create_consolidated_mcp_servers()

        # Step 3: Terminate duplicates
        terminated = self.terminate_duplicate_services(duplicates)

        # Step 4: Update configuration
        await self.update_port_configuration()

        # Step 5: Summary
        print("\n📊 CONSOLIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Services terminated: {terminated}")
        print(f"✅ Enhanced MCP memory created with Redis backend")
        print(f"✅ Consolidated MCP servers manager created")
        print(f"✅ Port configuration updated")

        print("\n🎯 NEXT STEPS:")
        print("1. Start Redis: wsl -d Ubuntu sudo systemctl start redis-server")
        print("2. Start MCP Memory: python core/enhanced_mcp_memory_server.py")
        print("3. Start MCP Servers: python core/consolidated_mcp_servers.py")
        print("4. Start Unified Portal: python src/core/unified_agi_portal.py")
        print("5. Start A2A Protocol: python core/a2a_enhanced_protocol.py")

        return {
            'duplicates_found': len(duplicates),
            'services_terminated': terminated,
            'consolidation_complete': True
        }

async def main():
    """Main entry point"""
    deduplicator = ServiceDeduplicator()
    results = await deduplicator.run_consolidation()

    if results['consolidation_complete']:
        print("\n🎉 SERVICE CONSOLIDATION COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("\n❌ SERVICE CONSOLIDATION FAILED!")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
