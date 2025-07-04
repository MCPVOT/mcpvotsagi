#!/usr/bin/env python3
"""
MCP Server Manager - Start and manage MCP servers for AGI Dashboard
================================================================
"""

import subprocess
import sys
import os
import time
import json
import asyncio
import signal
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manage MCP servers for AGI Dashboard"""

    def __init__(self):
        self.workspace = Path(__file__).parent
        self.processes = {}
        self.running = False

        # MCP server configurations
        self.servers = {
            "filesystem": {
                "name": "FileSystem MCP",
                "port": 3001,
                "command": ["npx", "@modelcontextprotocol/server-filesystem", str(self.workspace)],
                "env": {},
                "priority": 1
            },
            "memory": {
                "name": "Memory MCP",
                "port": 3002,
                "command": ["npx", "@modelcontextprotocol/server-memory"],
                "env": {},
                "priority": 2
            },
            "github": {
                "name": "GitHub MCP",
                "port": 3003,
                "command": ["npx", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
                },
                "priority": 3
            },
            "browser": {
                "name": "Browser MCP",
                "port": 3006,
                "command": ["npx", "@modelcontextprotocol/server-puppeteer"],
                "env": {},
                "priority": 4
            },
            "search": {
                "name": "Brave Search MCP",
                "port": 3007,
                "command": ["npx", "@modelcontextprotocol/server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")
                },
                "priority": 5
            }
        }

    def check_server_availability(self):
        """Check if MCP servers are installed and available"""
        print("=" * 70)
        print("MCP SERVER AVAILABILITY CHECK")
        print("=" * 70)

        available = 0

        for server_id, config in self.servers.items():
            try:
                # Test if server command is available
                result = subprocess.run(
                    config["command"] + ["--help"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0 or "usage" in result.stdout.lower() or "options" in result.stdout.lower():
                    status = "AVAILABLE"
                    available += 1
                else:
                    status = "NOT RESPONDING"

            except subprocess.TimeoutExpired:
                status = "TIMEOUT"
            except FileNotFoundError:
                status = "NOT INSTALLED"
            except Exception as e:
                status = f"ERROR: {str(e)[:30]}"

            print(f"{config['name']:<20} Port {config['port']:<4} {status}")

        print("-" * 70)
        print(f"Available: {available}/{len(self.servers)} servers")
        print("=" * 70)

        return available >= len(self.servers) // 2  # At least half should be available

    def start_server(self, server_id, config):
        """Start a single MCP server"""
        try:
            logger.info(f"Starting {config['name']} on port {config['port']}...")

            # Prepare environment
            env = os.environ.copy()
            env.update(config["env"])

            # Start process
            process = subprocess.Popen(
                config["command"],
                cwd=str(self.workspace),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )

            self.processes[server_id] = process

            # Give it a moment to start
            time.sleep(2)

            # Check if it's still running
            if process.poll() is None:
                logger.info(f"✓ {config['name']} started successfully")
                return True
            else:
                logger.error(f"✗ {config['name']} failed to start")
                stderr = process.stderr.read().decode('utf-8', errors='ignore')
                if stderr:
                    logger.error(f"  Error: {stderr[:200]}")
                return False

        except Exception as e:
            logger.error(f"Failed to start {config['name']}: {e}")
            return False

    def start_all_servers(self):
        """Start all MCP servers in priority order"""
        print("=" * 70)
        print("STARTING MCP SERVERS FOR AGI DASHBOARD")
        print("=" * 70)

        # Sort by priority
        sorted_servers = sorted(self.servers.items(), key=lambda x: x[1]["priority"])

        started = 0

        for server_id, config in sorted_servers:
            if self.start_server(server_id, config):
                started += 1

        print(f"\n{started}/{len(self.servers)} servers started successfully")

        if started >= len(self.servers) // 2:
            print("✓ Core MCP servers are running - AGI Dashboard ready!")
            self.running = True
            return True
        else:
            print("⚠ Not enough servers started - some features may be limited")
            return False

    def stop_all_servers(self):
        """Stop all MCP servers"""
        logger.info("Stopping all MCP servers...")

        for server_id, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    if sys.platform == "win32":
                        process.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        process.terminate()

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()

                    logger.info(f"✓ Stopped {self.servers[server_id]['name']}")
                except Exception as e:
                    logger.error(f"Error stopping {server_id}: {e}")

        self.processes.clear()
        self.running = False
        logger.info("All MCP servers stopped")

    def monitor_servers(self):
        """Monitor server health and restart if needed"""
        while self.running:
            time.sleep(30)  # Check every 30 seconds

            # Check if processes are still running
            for server_id, process in list(self.processes.items()):
                if process.poll() is not None:
                    logger.warning(f"{self.servers[server_id]['name']} stopped unexpectedly")

                    # Try to restart
                    if self.start_server(server_id, self.servers[server_id]):
                        logger.info(f"✓ Restarted {self.servers[server_id]['name']}")
                    else:
                        logger.error(f"✗ Failed to restart {self.servers[server_id]['name']}")

    def create_config_file(self):
        """Create MCP configuration file for VS Code"""
        config = {
            "mcpServers": {}
        }

        for server_id, server_config in self.servers.items():
            config["mcpServers"][server_id] = {
                "command": server_config["command"][0],
                "args": server_config["command"][1:],
                "env": server_config["env"]
            }

        config_path = self.workspace / "config" / "mcp_settings.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Created MCP configuration: {config_path}")

    def run_interactive(self):
        """Run in interactive mode"""
        print("=" * 70)
        print("MCP SERVER MANAGER - INTERACTIVE MODE")
        print("=" * 70)

        try:
            # Check availability
            if not self.check_server_availability():
                print("\n⚠ Some MCP servers are not available.")
                print("  Make sure Node.js is installed and run:")
                print("  npm install -g @modelcontextprotocol/server-filesystem")
                print("  npm install -g @modelcontextprotocol/server-memory")
                print("  npm install -g @modelcontextprotocol/server-github")
                print("  npm install -g @modelcontextprotocol/server-puppeteer")
                print("  npm install -g @modelcontextprotocol/server-brave-search")
                return False

            # Start servers
            if self.start_all_servers():
                print("\n🎉 MCP servers are running!")
                print("The AGI Dashboard can now use all MCP tools.")
                print("\nPress Ctrl+C to stop all servers...")

                # Create config file
                self.create_config_file()

                # Start monitoring
                try:
                    self.monitor_servers()
                except KeyboardInterrupt:
                    print("\nShutting down...")

            else:
                print("\n⚠ Failed to start enough servers")

        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop_all_servers()

        return True

def main():
    """Main entry point"""
    manager = MCPServerManager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "check":
            manager.check_server_availability()
        elif command == "start":
            manager.start_all_servers()
            if manager.running:
                print("Press Ctrl+C to stop servers...")
                try:
                    while manager.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                finally:
                    manager.stop_all_servers()
        elif command == "stop":
            manager.stop_all_servers()
        elif command == "config":
            manager.create_config_file()
        else:
            print("Usage: python mcp_server_manager.py [check|start|stop|config]")
            return 1
    else:
        # Interactive mode
        return 0 if manager.run_interactive() else 1

if __name__ == "__main__":
    sys.exit(main())
