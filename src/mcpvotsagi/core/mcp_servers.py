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
                'command': [sys.executable, '-m', 'mcpvotsagi.core.memory'],
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
            print(f"Starting {name} MCP server on port {config['port']}...")

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

            print(f"{name} MCP server started (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"Failed to start {name} MCP server: {e}")
            return False

    async def start_all_servers(self):
        """Start all MCP servers"""
        print("Starting Consolidated MCP Servers...")
        print("=" * 50)

        success_count = 0
        for name, config in self.mcp_config.items():
            if await self.start_server(name, config):
                success_count += 1
            await asyncio.sleep(1)  # Stagger starts

        print(f"\nMCP Servers Status: {success_count}/{len(self.mcp_config)} started")
        self.running = True

        return success_count > 0

    async def stop_all_servers(self):
        """Stop all MCP servers"""
        print("\nStopping all MCP servers...")

        for name, server_info in self.servers.items():
            try:
                process = server_info['process']
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5)
                print(f"Stopped {name} MCP server")
            except asyncio.TimeoutError:
                process.kill()
                print(f"Force killed {name} MCP server")
            except Exception as e:
                print(f"Error stopping {name}: {e}")

        self.running = False

    async def monitor_servers(self):
        """Monitor server health and restart if needed"""
        while self.running:
            for name, server_info in list(self.servers.items()):
                process = server_info['process']
                if process.returncode is not None:
                    print(f"{name} MCP server died, restarting...")
                    await self.start_server(name, server_info['config'])

            await asyncio.sleep(30)  # Check every 30 seconds

    async def run(self):
        """Main run loop"""
        if await self.start_all_servers():
            print("\nAll MCP servers are running!")
            print("\nPress Ctrl+C to stop all servers")

            # Set up signal handlers
            def signal_handler(signum, frame):
                print("\nReceived shutdown signal...")
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
            print("Failed to start MCP servers")

async def main():
    """Main entry point"""
    servers_manager = ConsolidatedMCPServers()
    await servers_manager.run()

if __name__ == "__main__":
    asyncio.run(main())
