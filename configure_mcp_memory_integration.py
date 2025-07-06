#!/usr/bin/env python3
"""
Configure MCP Memory Integration for Claude Code in WSL Ubuntu
This script helps configure and test MCP memory integration between VSCode and Claude Code
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPMemoryConfigurator:
    def __init__(self):
        self.wsl_home = None
        self.config_path = None
        self.mcp_server_path = None

    def detect_wsl_environment(self):
        """Detect WSL environment and paths"""
        try:
            # Check if we're in WSL or can access WSL
            result = subprocess.run(['wsl', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ WSL detected and accessible")

                # Get WSL home directory
                wsl_home_result = subprocess.run(['wsl', 'echo', '$HOME'], capture_output=True, text=True)
                if wsl_home_result.returncode == 0:
                    self.wsl_home = wsl_home_result.stdout.strip()
                    logger.info(f"📁 WSL Home: {self.wsl_home}")

                    # Set config path
                    self.config_path = f"{self.wsl_home}/claude_desktop_config.json"
                    logger.info(f"📄 Config path: {self.config_path}")

                    return True
                else:
                    logger.error("❌ Could not get WSL home directory")
                    return False
            else:
                logger.error("❌ WSL not accessible")
                return False
        except Exception as e:
            logger.error(f"❌ Error detecting WSL: {e}")
            return False

    def find_mcp_server(self):
        """Find MCP memory server installation"""
        possible_paths = [
            f"{self.wsl_home}/.npm-global/bin/mcp-server-memory",
            f"{self.wsl_home}/.local/bin/mcp-server-memory",
            "/usr/local/bin/mcp-server-memory",
            "/usr/bin/mcp-server-memory"
        ]

        for path in possible_paths:
            try:
                # Check if file exists in WSL
                result = subprocess.run(['wsl', 'test', '-f', path], capture_output=True)
                if result.returncode == 0:
                    self.mcp_server_path = path
                    logger.info(f"✅ MCP server found at: {path}")
                    return True
            except Exception as e:
                logger.debug(f"Checking {path}: {e}")

        logger.warning("⚠️ MCP server not found in common locations")
        return False

    def install_mcp_server(self):
        """Install MCP memory server if not found"""
        logger.info("🔧 Installing MCP memory server...")

        try:
            # Install using npm in WSL
            install_cmd = [
                'wsl', 'bash', '-c',
                'npm install -g @modelcontextprotocol/server-memory || ' +
                'npm install -g mcp-server-memory || ' +
                'npm install -g @mcp/server-memory'
            ]

            result = subprocess.run(install_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("✅ MCP server installed successfully")
                return self.find_mcp_server()
            else:
                logger.error(f"❌ Failed to install MCP server: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error installing MCP server: {e}")
            return False

    def create_claude_config(self):
        """Create Claude Desktop configuration"""
        logger.info("📝 Creating Claude Desktop configuration...")

        # Configuration for Claude Code
        config = {
            "mcpServers": {
                "memory": {
                    "command": self.mcp_server_path or "/usr/local/bin/mcp-server-memory",
                    "args": [],
                    "env": {
                        "MEMORY_STORE_PATH": f"{self.wsl_home}/.mcp-memory-store",
                        "MEMORY_STORE_TYPE": "sqlite"
                    }
                }
            },
            "globalShortcut": "CommandOrControl+Shift+M"
        }

        # Write config to WSL filesystem
        try:
            config_json = json.dumps(config, indent=2)

            # Create config file in WSL
            create_cmd = [
                'wsl', 'bash', '-c',
                f'echo \'{config_json}\' > "{self.config_path}"'
            ]

            result = subprocess.run(create_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ Configuration created at: {self.config_path}")
                return True
            else:
                logger.error(f"❌ Failed to create config: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error creating config: {e}")
            return False

    def verify_config(self):
        """Verify the configuration file was created correctly"""
        try:
            # Read the config file from WSL
            result = subprocess.run(['wsl', 'cat', self.config_path], capture_output=True, text=True)

            if result.returncode == 0:
                config = json.loads(result.stdout)
                logger.info("✅ Configuration verified successfully")
                logger.info(f"📊 Config content: {json.dumps(config, indent=2)}")
                return True
            else:
                logger.error(f"❌ Could not read config: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error verifying config: {e}")
            return False

    def test_mcp_server(self):
        """Test if MCP server can be started"""
        logger.info("🧪 Testing MCP server...")

        try:
            # Test server startup
            test_cmd = [
                'wsl', 'bash', '-c',
                f'timeout 5 {self.mcp_server_path} --help || echo "Server executable found"'
            ]

            result = subprocess.run(test_cmd, capture_output=True, text=True)

            if result.returncode == 0 or "Server executable found" in result.stdout:
                logger.info("✅ MCP server is executable")
                return True
            else:
                logger.error(f"❌ MCP server test failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error testing MCP server: {e}")
            return False

    def create_memory_store(self):
        """Create memory store directory"""
        logger.info("📁 Creating memory store directory...")

        try:
            memory_store_path = f"{self.wsl_home}/.mcp-memory-store"

            # Create directory
            create_cmd = ['wsl', 'mkdir', '-p', memory_store_path]
            result = subprocess.run(create_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ Memory store created at: {memory_store_path}")
                return True
            else:
                logger.error(f"❌ Failed to create memory store: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error creating memory store: {e}")
            return False

    def generate_test_script(self):
        """Generate a test script for Claude Code"""
        logger.info("📝 Generating test script...")

        test_script = f"""#!/bin/bash
# MCP Memory Integration Test Script
# Save this as ~/test_mcp_memory.sh and run it in WSL

echo "🧪 Testing MCP Memory Integration..."
echo "=================================="

# Check if MCP server exists
if [ -f "{self.mcp_server_path}" ]; then
    echo "✅ MCP server found at: {self.mcp_server_path}"
else
    echo "❌ MCP server not found at: {self.mcp_server_path}"
    exit 1
fi

# Check if config exists
if [ -f "{self.config_path}" ]; then
    echo "✅ Claude config found at: {self.config_path}"
    echo "📄 Config content:"
    cat "{self.config_path}"
else
    echo "❌ Claude config not found at: {self.config_path}"
    exit 1
fi

# Check if memory store exists
if [ -d "{self.wsl_home}/.mcp-memory-store" ]; then
    echo "✅ Memory store directory exists"
else
    echo "📁 Creating memory store directory..."
    mkdir -p "{self.wsl_home}/.mcp-memory-store"
fi

# Test MCP server
echo "🧪 Testing MCP server execution..."
timeout 5 {self.mcp_server_path} --help > /dev/null 2>&1
if [ $? -eq 0 ] || [ $? -eq 124 ]; then
    echo "✅ MCP server is executable"
else
    echo "❌ MCP server execution failed"
    exit 1
fi

echo ""
echo "🎉 MCP Memory Integration Test Complete!"
echo "========================================"
echo "📌 Next steps:"
echo "1. Restart Claude Code in WSL"
echo "2. Check if MCP memory tools are available"
echo "3. Try using mcp_memory_create_entities or similar tools"
echo ""
echo "💡 To restart Claude Code:"
echo "   pkill -f claude || killall claude"
echo "   # Then start Claude Code again"
"""

        try:
            # Write test script
            script_path = f"{self.wsl_home}/test_mcp_memory.sh"
            write_cmd = [
                'wsl', 'bash', '-c',
                f'echo \'{test_script}\' > "{script_path}" && chmod +x "{script_path}"'
            ]

            result = subprocess.run(write_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ Test script created at: {script_path}")
                return script_path
            else:
                logger.error(f"❌ Failed to create test script: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"❌ Error creating test script: {e}")
            return None

    def run_complete_setup(self):
        """Run the complete MCP memory setup"""
        logger.info("🚀 Starting MCP Memory Integration Setup...")
        logger.info("=" * 50)

        # Step 1: Detect WSL
        if not self.detect_wsl_environment():
            logger.error("❌ WSL setup failed")
            return False

        # Step 2: Find or install MCP server
        if not self.find_mcp_server():
            logger.info("📦 MCP server not found, attempting installation...")
            if not self.install_mcp_server():
                logger.error("❌ MCP server installation failed")
                return False

        # Step 3: Create memory store
        if not self.create_memory_store():
            logger.error("❌ Memory store creation failed")
            return False

        # Step 4: Create Claude config
        if not self.create_claude_config():
            logger.error("❌ Claude config creation failed")
            return False

        # Step 5: Verify config
        if not self.verify_config():
            logger.error("❌ Config verification failed")
            return False

        # Step 6: Test MCP server
        if not self.test_mcp_server():
            logger.error("❌ MCP server test failed")
            return False

        # Step 7: Generate test script
        test_script_path = self.generate_test_script()
        if not test_script_path:
            logger.error("❌ Test script generation failed")
            return False

        # Success summary
        logger.info("🎉 MCP Memory Integration Setup Complete!")
        logger.info("=" * 50)
        logger.info("✅ WSL environment detected")
        logger.info(f"✅ MCP server installed at: {self.mcp_server_path}")
        logger.info(f"✅ Claude config created at: {self.config_path}")
        logger.info(f"✅ Memory store created at: {self.wsl_home}/.mcp-memory-store")
        logger.info(f"✅ Test script created at: {test_script_path}")
        logger.info("")
        logger.info("📌 Next Steps:")
        logger.info("1. Restart Claude Code in WSL Ubuntu")
        logger.info("2. Run the test script: ~/test_mcp_memory.sh")
        logger.info("3. Check if MCP memory tools are available in Claude Code")
        logger.info("4. Test with: mcp_memory_create_entities or similar tools")
        logger.info("")
        logger.info("💡 To restart Claude Code in WSL:")
        logger.info("   wsl bash -c 'pkill -f claude || killall claude'")
        logger.info("   # Then start Claude Code again")

        return True

def main():
    """Main function"""
    print("🔧 MCP Memory Integration Configurator")
    print("=" * 40)

    configurator = MCPMemoryConfigurator()

    if configurator.run_complete_setup():
        print("\n✅ Setup completed successfully!")
        print("🔄 Please restart Claude Code in WSL to apply changes.")
        return 0
    else:
        print("\n❌ Setup failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
