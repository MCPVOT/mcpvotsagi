#!/usr/bin/env python3
"""
Setup Core MCP Servers for AGI Dashboard
========================================
This script sets up the essential MCP servers needed for the AGI dashboard.
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoreMCPSetup:
    """Setup core MCP servers for AGI dashboard"""

    def __init__(self):
        self.workspace = Path(__file__).parent
        self.mcp_config_path = self.workspace / "config" / "mcp_settings.json"

    def create_mcp_config(self):
        """Create MCP configuration file"""
        config = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", str(self.workspace)],
                    "env": {}
                },
                "memory": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "env": {}
                },
                "github": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
                    }
                },
                "browser": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-puppeteer"],
                    "env": {}
                },
                "brave-search": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-brave-search"],
                    "env": {
                        "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")
                    }
                }
            }
        }

        # Ensure config directory exists
        self.mcp_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config
        with open(self.mcp_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Created MCP configuration at {self.mcp_config_path}")

    def install_mcp_servers(self):
        """Install essential MCP servers"""
        servers = [
            "@modelcontextprotocol/server-filesystem",
            "@modelcontextprotocol/server-memory",
            "@modelcontextprotocol/server-github",
            "@modelcontextprotocol/server-puppeteer",
            "@modelcontextprotocol/server-brave-search"
        ]

        logger.info("Installing MCP servers...")

        for server in servers:
            try:
                logger.info(f"Installing {server}...")
                result = subprocess.run(
                    ["npm", "install", "-g", server],
                    capture_output=True,
                    text=True,
                    cwd=str(self.workspace),
                    shell=True
                )

                if result.returncode == 0:
                    logger.info(f"✓ {server} installed successfully")
                else:
                    logger.warning(f"⚠ {server} installation had warnings: {result.stderr}")

            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to install {server}: {e}")
            except FileNotFoundError:
                logger.error("npm not found. Please install Node.js first.")
                return False

        return True

    def check_mcp_servers(self):
        """Check if MCP servers are available"""
        logger.info("Checking MCP server availability...")

        servers = [
            "@modelcontextprotocol/server-filesystem",
            "@modelcontextprotocol/server-memory",
            "@modelcontextprotocol/server-github",
            "@modelcontextprotocol/server-puppeteer",
            "@modelcontextprotocol/server-brave-search"
        ]

        available = []

        for server in servers:
            try:
                result = subprocess.run(
                    ["npx", server, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True
                )

                if result.returncode == 0 or "usage" in result.stdout.lower() or "options" in result.stdout.lower():
                    available.append(server)
                    logger.info(f"✓ {server} is available")
                else:
                    logger.warning(f"⚠ {server} not responding correctly")

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning(f"⚠ {server} not available")

        logger.info(f"Available MCP servers: {len(available)}/{len(servers)}")
        return available

    def create_launch_script(self):
        """Create launch script for MCP servers"""
        script_content = '''@echo off
echo Starting Core MCP Servers for AGI Dashboard...
echo.

REM Check if Node.js is available
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is available
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm not found. Please install Node.js first.
    pause
    exit /b 1
)

echo Node.js and npm are available.
echo.

REM Install MCP servers if not already installed
echo Installing/updating MCP servers...
call npm install -g @modelcontextprotocol/server-filesystem
call npm install -g @modelcontextprotocol/server-memory
call npm install -g @modelcontextprotocol/server-github
call npm install -g @modelcontextprotocol/server-puppeteer
call npm install -g @modelcontextprotocol/server-brave-search

echo.
echo MCP servers are ready!
echo.
echo To use these servers, make sure to:
echo 1. Set GITHUB_PERSONAL_ACCESS_TOKEN for GitHub integration
echo 2. Set BRAVE_API_KEY for web search capabilities
echo 3. Configure them in your MCP client
echo.
pause
'''

        script_path = self.workspace / "START_MCP_SERVERS.bat"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"Created launch script at {script_path}")

    def create_status_check_script(self):
        """Create status check script"""
        script_content = '''#!/usr/bin/env python3
"""Check MCP Server Status"""

import subprocess
import sys

def check_mcp_status():
    """Check if MCP servers are available"""
    servers = [
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-memory",
        "@modelcontextprotocol/server-github",
        "@modelcontextprotocol/server-puppeteer",
        "@modelcontextprotocol/server-brave-search"
    ]

    print("="*60)
    print("MCP SERVER STATUS CHECK")
    print("="*60)

    available = 0

    for server in servers:
        try:
            result = subprocess.run(
                ["npx", server, "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 or "usage" in result.stdout.lower():
                print(f"✓ {server:<40} AVAILABLE")
                available += 1
            else:
                print(f"✗ {server:<40} NOT RESPONDING")

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            print(f"✗ {server:<40} NOT AVAILABLE")

    print("-"*60)
    print(f"Status: {available}/{len(servers)} servers available")
    print("="*60)

    if available == len(servers):
        print("🎉 All MCP servers are ready!")
        return True
    else:
        print("⚠ Some MCP servers need to be installed/configured")
        return False

if __name__ == "__main__":
    check_mcp_status()
'''

        script_path = self.workspace / "check_mcp_status.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"Created status check script at {script_path}")

    def run_setup(self):
        """Run the complete setup"""
        logger.info("Setting up Core MCP Servers for AGI Dashboard...")

        # Create MCP configuration
        self.create_mcp_config()

        # Install MCP servers
        if self.install_mcp_servers():
            logger.info("✓ MCP servers installation completed")
        else:
            logger.warning("⚠ MCP servers installation had issues")

        # Check availability
        available = self.check_mcp_servers()

        # Create launch scripts
        self.create_launch_script()
        self.create_status_check_script()

        # Final status
        print("\n" + "="*60)
        print("CORE MCP SETUP COMPLETE")
        print("="*60)
        print(f"Available servers: {len(available)}")
        print(f"Configuration: {self.mcp_config_path}")
        print(f"Launch script: START_MCP_SERVERS.bat")
        print(f"Status check: check_mcp_status.py")
        print("="*60)

        if len(available) >= 3:
            print("🎉 MCP servers are ready for use!")
        else:
            print("⚠ Some MCP servers need manual setup")

        return len(available) >= 3

def main():
    """Main entry point"""
    setup = CoreMCPSetup()
    success = setup.run_setup()

    if success:
        print("\n✓ Setup completed successfully!")
        print("You can now use the AGI dashboard with MCP integration.")
    else:
        print("\n⚠ Setup completed with warnings.")
        print("Some MCP servers may need manual configuration.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
