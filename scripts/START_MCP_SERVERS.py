#!/usr/bin/env python3
"""
MCP Servers Manager for MCPVotsAGI
Manages all MCP servers for the Ultimate AGI System
"""

import asyncio
import subprocess
import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manages all MCP servers for the Ultimate AGI System"""

    def __init__(self):
        self.servers = {}
        self.base_port = 3000
        self.project_root = Path(__file__).parent

        # Define all MCP servers
        self.server_configs = {
            'filesystem': {
                'port': 3000,
                'command': ['npx', '@modelcontextprotocol/server-filesystem'],
                'args': ['--port', '3000'],
                'description': 'FileSystem MCP Server'
            },
            'github': {
                'port': 3001,
                'command': ['npx', '@modelcontextprotocol/server-github'],
                'args': ['--port', '3001'],
                'description': 'GitHub MCP Server'
            },
            'memory': {
                'port': 3002,
                'command': ['npx', '@modelcontextprotocol/server-memory'],
                'args': ['--port', '3002'],
                'description': 'Memory MCP Server'
            },
            'browser': {
                'port': 3003,
                'command': ['npx', '@modelcontextprotocol/server-puppeteer'],
                'args': ['--port', '3003'],
                'description': 'Browser/Puppeteer MCP Server'
            },
            'brave-search': {
                'port': 3004,
                'command': ['npx', '@modelcontextprotocol/server-brave-search'],
                'args': ['--port', '3004'],
                'description': 'Brave Search MCP Server'
            },
            'context7': {
                'port': 3005,
                'command': ['node', str(self.project_root / 'tools' / 'context7' / 'start-windows.js')],
                'args': [],
                'description': 'Context7 Documentation Server'
            }
        }

    async def install_mcp_servers(self):
        """Install all MCP servers"""
        logger.info("[MCP] Installing MCP servers...")

        # Install global MCP servers
        mcp_packages = [
            '@modelcontextprotocol/server-filesystem',
            '@modelcontextprotocol/server-github',
            '@modelcontextprotocol/server-memory',
            '@modelcontextprotocol/server-puppeteer',
            '@modelcontextprotocol/server-brave-search'
        ]

        for package in mcp_packages:
            try:
                logger.info(f"[MCP] Installing {package}...")
                result = subprocess.run(
                    ['npm', 'install', '-g', package],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    logger.info(f"[MCP] Successfully installed {package}")
                else:
                    logger.warning(f"[MCP] Failed to install {package}: {result.stderr}")

            except Exception as e:
                logger.error(f"[MCP] Error installing {package}: {e}")

        # Build Context7 if needed
        await self.build_context7()

    async def build_context7(self):
        """Build Context7 if needed"""
        try:
            context7_dir = self.project_root / 'tools' / 'context7'
            if not context7_dir.exists():
                logger.warning("[CONTEXT7] Context7 directory not found")
                return

            # Check if build is needed
            dist_dir = context7_dir / 'dist'
            if not dist_dir.exists():
                logger.info("[CONTEXT7] Building Context7...")

                # Run Windows build script
                build_script = context7_dir / 'build-windows.bat'
                if build_script.exists():
                    result = subprocess.run(
                        [str(build_script)],
                        cwd=str(context7_dir),
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if result.returncode == 0:
                        logger.info("[CONTEXT7] Context7 build successful")
                    else:
                        logger.error(f"[CONTEXT7] Context7 build failed: {result.stderr}")
                else:
                    # Fallback to direct TypeScript compilation
                    result = subprocess.run(
                        ['npx', 'tsc'],
                        cwd=str(context7_dir),
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if result.returncode == 0:
                        logger.info("[CONTEXT7] Context7 TypeScript compilation successful")
                    else:
                        logger.error(f"[CONTEXT7] Context7 TypeScript compilation failed: {result.stderr}")

            else:
                logger.info("[CONTEXT7] Context7 already built")

        except Exception as e:
            logger.error(f"[CONTEXT7] Error building Context7: {e}")

    async def start_server(self, name: str) -> bool:
        """Start a specific MCP server"""
        if name not in self.server_configs:
            logger.error(f"[MCP] Unknown server: {name}")
            return False

        config = self.server_configs[name]

        try:
            logger.info(f"[MCP] Starting {config['description']} on port {config['port']}")

            # Start the server process
            cmd = config['command'] + config['args']
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Store the process
            self.servers[name] = {
                'process': process,
                'config': config,
                'started': time.time()
            }

            # Give it a moment to start
            await asyncio.sleep(2)

            # Check if it's still running
            if process.poll() is None:
                logger.info(f"[MCP] {config['description']} started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"[MCP] {config['description']} failed to start: {stderr}")
                return False

        except Exception as e:
            logger.error(f"[MCP] Error starting {name}: {e}")
            return False

    async def start_all_servers(self):
        """Start all MCP servers"""
        logger.info("[MCP] Starting all MCP servers...")

        started_count = 0
        for name in self.server_configs:
            if await self.start_server(name):
                started_count += 1
            else:
                logger.warning(f"[MCP] Failed to start {name}")

        logger.info(f"[MCP] Started {started_count}/{len(self.server_configs)} servers")
        return started_count

    async def stop_server(self, name: str):
        """Stop a specific MCP server"""
        if name in self.servers:
            server = self.servers[name]
            process = server['process']

            try:
                process.terminate()
                await asyncio.sleep(1)

                if process.poll() is None:
                    process.kill()

                logger.info(f"[MCP] Stopped {name}")
                del self.servers[name]

            except Exception as e:
                logger.error(f"[MCP] Error stopping {name}: {e}")

    async def stop_all_servers(self):
        """Stop all MCP servers"""
        logger.info("[MCP] Stopping all MCP servers...")

        for name in list(self.servers.keys()):
            await self.stop_server(name)

    def get_server_status(self) -> Dict:
        """Get status of all servers"""
        status = {}

        for name, config in self.server_configs.items():
            if name in self.servers:
                process = self.servers[name]['process']
                if process.poll() is None:
                    status[name] = {
                        'status': 'running',
                        'port': config['port'],
                        'uptime': time.time() - self.servers[name]['started']
                    }
                else:
                    status[name] = {
                        'status': 'stopped',
                        'port': config['port'],
                        'uptime': 0
                    }
            else:
                status[name] = {
                    'status': 'not_started',
                    'port': config['port'],
                    'uptime': 0
                }

        return status

    async def monitor_servers(self):
        """Monitor server health and restart if needed"""
        while True:
            try:
                # Check each server
                for name, server in list(self.servers.items()):
                    process = server['process']

                    if process.poll() is not None:
                        logger.warning(f"[MCP] {name} server died, restarting...")
                        del self.servers[name]
                        await self.start_server(name)

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"[MCP] Error in server monitor: {e}")
                await asyncio.sleep(5)

async def main():
    """Main function"""
    manager = MCPServerManager()

    try:
        print("[MCP] MCPVotsAGI MCP Server Manager")
        print("[MCP] ================================")

        # Install servers if needed
        await manager.install_mcp_servers()

        # Start all servers
        started_count = await manager.start_all_servers()

        if started_count > 0:
            print(f"[MCP] {started_count} servers started successfully")
            print("[MCP] Server status:")

            status = manager.get_server_status()
            for name, info in status.items():
                print(f"[MCP]   {name}: {info['status']} (port {info['port']})")

            print("[MCP] Starting server monitor...")
            print("[MCP] Press Ctrl+C to stop all servers")

            # Start monitoring
            await manager.monitor_servers()
        else:
            print("[MCP] No servers started successfully")

    except KeyboardInterrupt:
        print("\n[MCP] Shutting down...")
        await manager.stop_all_servers()
        print("[MCP] All servers stopped")

    except Exception as e:
        print(f"[MCP] Error: {e}")
        await manager.stop_all_servers()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

def start_mcp_server(command, name, port=None):
    """Start an MCP server"""
    print(f"Starting {name}...")
    try:
        if port:
            full_command = f"{command} --port {port}"
        else:
            full_command = command

        proc = subprocess.Popen(full_command, shell=True)
        print(f"   Started {name} (PID: {proc.pid})")
        return proc
    except Exception as e:
        print(f"   Failed to start {name}: {e}")
        return None

def main():
    print("Starting All MCP Servers...")
    print("=" * 40)

    servers = [
        ("npx @modelcontextprotocol/server-filesystem", "FileSystem", 3000),
        ("npx @modelcontextprotocol/server-github", "GitHub", 3001),
        ("npx @modelcontextprotocol/server-memory", "Memory", 3002),
        ("npx @modelcontextprotocol/server-brave-search", "Search", 3003),
        ("npx @agentdeskai/browser-tools-mcp", "Browser", 3006),
    ]

    processes = []
    for command, name, port in servers:
        proc = start_mcp_server(command, name, port)
        if proc:
            processes.append((proc, name))
        time.sleep(2)  # Wait between starts

    print(f"Started {len(processes)} MCP servers")
    print("Keep this window open to maintain the servers")
    print("Press Ctrl+C to stop all servers")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all MCP servers...")
        for proc, name in processes:
            try:
                proc.terminate()
                print(f"   Stopped {name}")
            except:
                pass
        print("All servers stopped.")

if __name__ == "__main__":
    main()
