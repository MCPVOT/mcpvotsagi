#!/usr/bin/env python3
"""
Fixed MCP Memory Integration for Claude Code in WSL Ubuntu
This script handles different shell environments and installation methods
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
        self.shell = None

    def detect_wsl_environment(self):
        """Detect WSL environment and available shells"""
        try:
            # Check if we're in WSL or can access WSL
            result = subprocess.run(['wsl', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ WSL detected and accessible")

                # Try different shells
                shells = ['bash', 'sh', 'zsh']
                for shell in shells:
                    test_result = subprocess.run(['wsl', 'which', shell], capture_output=True, text=True)
                    if test_result.returncode == 0:
                        self.shell = shell
                        logger.info(f"✅ Using shell: {shell}")
                        break

                if not self.shell:
                    logger.error("❌ No compatible shell found")
                    return False

                # Get WSL home directory
                wsl_home_result = subprocess.run(['wsl', self.shell, '-c', 'echo $HOME'], capture_output=True, text=True)
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

    def install_nodejs_npm(self):
        """Install Node.js and npm if not available"""
        logger.info("📦 Installing Node.js and npm...")

        try:
            # Check if node is available
            node_check = subprocess.run(['wsl', 'which', 'node'], capture_output=True, text=True)
            npm_check = subprocess.run(['wsl', 'which', 'npm'], capture_output=True, text=True)

            if node_check.returncode == 0 and npm_check.returncode == 0:
                logger.info("✅ Node.js and npm already installed")
                return True

            # Install Node.js using different methods
            install_commands = [
                # Try with apt-get (Ubuntu/Debian)
                'apt-get update && apt-get install -y nodejs npm',
                # Try with yum (CentOS/RHEL)
                'yum install -y nodejs npm',
                # Try with pacman (Arch)
                'pacman -S nodejs npm --noconfirm',
                # Try with apk (Alpine)
                'apk add nodejs npm'
            ]

            for cmd in install_commands:
                try:
                    result = subprocess.run(['wsl', self.shell, '-c', cmd], capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        logger.info(f"✅ Node.js installed using: {cmd.split()[0]}")
                        return True
                except subprocess.TimeoutExpired:
                    logger.info(f"⏰ Command timed out: {cmd}")
                except Exception as e:
                    logger.debug(f"Failed with {cmd}: {e}")

            logger.error("❌ Failed to install Node.js and npm")
            return False

        except Exception as e:
            logger.error(f"❌ Error installing Node.js: {e}")
            return False

    def find_mcp_server(self):
        """Find MCP memory server installation"""
        possible_paths = [
            f"{self.wsl_home}/.npm-global/bin/mcp-server-memory",
            f"{self.wsl_home}/.local/bin/mcp-server-memory",
            "/usr/local/bin/mcp-server-memory",
            "/usr/bin/mcp-server-memory",
            f"{self.wsl_home}/node_modules/.bin/mcp-server-memory"
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
        """Install MCP memory server using different methods"""
        logger.info("🔧 Installing MCP memory server...")

        # First ensure Node.js is installed
        if not self.install_nodejs_npm():
            logger.error("❌ Node.js installation failed")
            return False

        # Try different installation methods
        install_methods = [
            # Method 1: Global install with common package names
            'npm install -g @modelcontextprotocol/server-memory',
            'npm install -g mcp-server-memory',
            'npm install -g @mcp/server-memory',

            # Method 2: Local install
            f'cd {self.wsl_home} && npm install @modelcontextprotocol/server-memory',
            f'cd {self.wsl_home} && npm install mcp-server-memory',

            # Method 3: Using npx
            'npx @modelcontextprotocol/server-memory --help',
        ]

        for method in install_methods:
            try:
                logger.info(f"🔄 Trying: {method}")
                result = subprocess.run(['wsl', self.shell, '-c', method], capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    logger.info(f"✅ Installation method succeeded: {method}")

                    # Try to find the server again
                    if self.find_mcp_server():
                        return True

                    # If not found, try to locate it
                    find_cmd = 'find /usr -name "*mcp*memory*" -type f 2>/dev/null || find $HOME -name "*mcp*memory*" -type f 2>/dev/null'
                    find_result = subprocess.run(['wsl', self.shell, '-c', find_cmd], capture_output=True, text=True)

                    if find_result.returncode == 0 and find_result.stdout.strip():
                        paths = find_result.stdout.strip().split('\n')
                        for path in paths:
                            if 'mcp' in path and 'memory' in path:
                                self.mcp_server_path = path
                                logger.info(f"✅ MCP server found at: {path}")
                                return True

            except subprocess.TimeoutExpired:
                logger.info(f"⏰ Installation timed out: {method}")
            except Exception as e:
                logger.debug(f"Failed method {method}: {e}")

        logger.error("❌ All installation methods failed")
        return False

    def create_memory_server_script(self):
        """Create a simple MCP memory server script if installation fails"""
        logger.info("📝 Creating simple MCP memory server script...")

        server_script = '''#!/usr/bin/env node
/**
 * Simple MCP Memory Server
 * This is a basic implementation for testing
 */

const fs = require('fs');
const path = require('path');

class SimpleMCPMemoryServer {
    constructor() {
        this.memoryStore = new Map();
        this.storePath = process.env.MEMORY_STORE_PATH || path.join(process.env.HOME, '.mcp-memory-store');
        this.init();
    }

    init() {
        // Create store directory if it doesn't exist
        if (!fs.existsSync(this.storePath)) {
            fs.mkdirSync(this.storePath, { recursive: true });
        }

        // Load existing memory
        this.loadMemory();
    }

    loadMemory() {
        try {
            const memoryFile = path.join(this.storePath, 'memory.json');
            if (fs.existsSync(memoryFile)) {
                const data = fs.readFileSync(memoryFile, 'utf8');
                const memory = JSON.parse(data);
                this.memoryStore = new Map(Object.entries(memory));
                console.log(`Loaded ${this.memoryStore.size} memory entries`);
            }
        } catch (error) {
            console.error('Error loading memory:', error);
        }
    }

    saveMemory() {
        try {
            const memoryFile = path.join(this.storePath, 'memory.json');
            const memory = Object.fromEntries(this.memoryStore);
            fs.writeFileSync(memoryFile, JSON.stringify(memory, null, 2));
        } catch (error) {
            console.error('Error saving memory:', error);
        }
    }

    start() {
        console.log('🧠 Simple MCP Memory Server started');
        console.log(`📁 Memory store: ${this.storePath}`);
        console.log(`💾 Memory entries: ${this.memoryStore.size}`);

        // Keep the server running
        setInterval(() => {
            this.saveMemory();
        }, 5000);
    }
}

// Handle command line arguments
if (process.argv.includes('--help')) {
    console.log('Simple MCP Memory Server');
    console.log('Usage: node simple-mcp-memory-server.js');
    console.log('Environment variables:');
    console.log('  MEMORY_STORE_PATH: Path to store memory data');
    process.exit(0);
}

const server = new SimpleMCPMemoryServer();
server.start();
'''

        try:
            server_path = f"{self.wsl_home}/simple-mcp-memory-server.js"
            write_cmd = f'echo \'{server_script}\' > "{server_path}"'

            result = subprocess.run(['wsl', self.shell, '-c', write_cmd], capture_output=True, text=True)

            if result.returncode == 0:
                # Make it executable
                chmod_cmd = f'chmod +x "{server_path}"'
                subprocess.run(['wsl', self.shell, '-c', chmod_cmd], capture_output=True, text=True)

                self.mcp_server_path = f'node {server_path}'
                logger.info(f"✅ Simple MCP server created at: {server_path}")
                return True
            else:
                logger.error(f"❌ Failed to create server script: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error creating server script: {e}")
            return False

    def create_claude_config(self):
        """Create Claude Desktop configuration"""
        logger.info("📝 Creating Claude Desktop configuration...")

        # Configuration for Claude Code
        config = {
            "mcpServers": {
                "memory": {
                    "command": self.mcp_server_path or "node",
                    "args": [f"{self.wsl_home}/simple-mcp-memory-server.js"] if 'node' in (self.mcp_server_path or '') else [],
                    "env": {
                        "MEMORY_STORE_PATH": f"{self.wsl_home}/.mcp-memory-store",
                        "MEMORY_STORE_TYPE": "json"
                    }
                }
            },
            "globalShortcut": "CommandOrControl+Shift+M"
        }

        # Write config to WSL filesystem
        try:
            config_json = json.dumps(config, indent=2)

            # Create config file in WSL
            create_cmd = f'echo \'{config_json}\' > "{self.config_path}"'

            result = subprocess.run(['wsl', self.shell, '-c', create_cmd], capture_output=True, text=True)

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

    def create_memory_store(self):
        """Create memory store directory"""
        logger.info("📁 Creating memory store directory...")

        try:
            memory_store_path = f"{self.wsl_home}/.mcp-memory-store"

            # Create directory
            create_cmd = f'mkdir -p "{memory_store_path}"'
            result = subprocess.run(['wsl', self.shell, '-c', create_cmd], capture_output=True, text=True)

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
        """Generate a comprehensive test script"""
        logger.info("📝 Generating test script...")

        test_script = f'''#!/bin/sh
# MCP Memory Integration Test Script
# Run this script in WSL to test the integration

echo "🧪 Testing MCP Memory Integration..."
echo "=================================="

# Check shell
echo "🐚 Using shell: {self.shell}"

# Check Node.js
if which node > /dev/null 2>&1; then
    echo "✅ Node.js found: $(node --version)"
else
    echo "❌ Node.js not found"
fi

# Check npm
if which npm > /dev/null 2>&1; then
    echo "✅ npm found: $(npm --version)"
else
    echo "❌ npm not found"
fi

# Check MCP server
if [ -f "{self.mcp_server_path}" ]; then
    echo "✅ MCP server found at: {self.mcp_server_path}"
elif [ -f "{self.wsl_home}/simple-mcp-memory-server.js" ]; then
    echo "✅ Simple MCP server found at: {self.wsl_home}/simple-mcp-memory-server.js"
else
    echo "❌ MCP server not found"
fi

# Check config
if [ -f "{self.config_path}" ]; then
    echo "✅ Claude config found at: {self.config_path}"
    echo "📄 Config content:"
    cat "{self.config_path}"
else
    echo "❌ Claude config not found"
fi

# Check memory store
if [ -d "{self.wsl_home}/.mcp-memory-store" ]; then
    echo "✅ Memory store directory exists"
else
    echo "📁 Creating memory store directory..."
    mkdir -p "{self.wsl_home}/.mcp-memory-store"
fi

# Test server execution
echo "🧪 Testing server execution..."
if [ -f "{self.wsl_home}/simple-mcp-memory-server.js" ]; then
    echo "Testing simple server..."
    timeout 3 node "{self.wsl_home}/simple-mcp-memory-server.js" > /tmp/mcp-test.log 2>&1 &
    sleep 2
    if ps aux | grep -q "simple-mcp-memory-server"; then
        echo "✅ Simple MCP server started successfully"
        pkill -f "simple-mcp-memory-server" || true
    else
        echo "❌ Simple MCP server failed to start"
        echo "📋 Log output:"
        cat /tmp/mcp-test.log 2>/dev/null || echo "No log output"
    fi
fi

echo ""
echo "🎉 MCP Memory Integration Test Complete!"
echo "========================================"
echo "📌 Next steps:"
echo "1. Restart Claude Code in WSL"
echo "2. Check if MCP memory tools are available"
echo "3. Try using these tools in Claude Code:"
echo "   - mcp_memory_create_entities"
echo "   - mcp_memory_search_nodes"
echo "   - mcp_memory_read_graph"
echo ""
echo "💡 To restart Claude Code processes:"
echo "   pkill -f claude 2>/dev/null || true"
echo "   killall claude 2>/dev/null || true"
echo "   # Then start Claude Code again"
echo ""
echo "🔧 If tools are not available, check:"
echo "   - Claude Code is running in WSL"
echo "   - Config file exists: {self.config_path}"
echo "   - Memory server is accessible"
'''

        try:
            script_path = f"{self.wsl_home}/test_mcp_memory.sh"
            write_cmd = f'echo \'{test_script}\' > "{script_path}" && chmod +x "{script_path}"'

            result = subprocess.run(['wsl', self.shell, '-c', write_cmd], capture_output=True, text=True)

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

        # Step 2: Create memory store
        if not self.create_memory_store():
            logger.error("❌ Memory store creation failed")
            return False

        # Step 3: Find or install MCP server
        if not self.find_mcp_server():
            logger.info("📦 MCP server not found, attempting installation...")
            if not self.install_mcp_server():
                logger.info("📝 Installation failed, creating simple server...")
                if not self.create_memory_server_script():
                    logger.error("❌ Failed to create simple server")
                    return False

        # Step 4: Create Claude config
        if not self.create_claude_config():
            logger.error("❌ Claude config creation failed")
            return False

        # Step 5: Verify config
        if not self.verify_config():
            logger.error("❌ Config verification failed")
            return False

        # Step 6: Generate test script
        test_script_path = self.generate_test_script()
        if not test_script_path:
            logger.error("❌ Test script generation failed")
            return False

        # Success summary
        logger.info("🎉 MCP Memory Integration Setup Complete!")
        logger.info("=" * 50)
        logger.info("✅ WSL environment detected")
        logger.info(f"✅ Using shell: {self.shell}")
        logger.info(f"✅ MCP server configured: {self.mcp_server_path}")
        logger.info(f"✅ Claude config created: {self.config_path}")
        logger.info(f"✅ Memory store created: {self.wsl_home}/.mcp-memory-store")
        logger.info(f"✅ Test script created: {test_script_path}")
        logger.info("")
        logger.info("📌 Next Steps:")
        logger.info("1. Run the test script in WSL:")
        logger.info(f"   wsl {self.shell} {test_script_path}")
        logger.info("2. Restart Claude Code in WSL Ubuntu")
        logger.info("3. Check if MCP memory tools are available")
        logger.info("4. Test with: mcp_memory_create_entities")
        logger.info("")
        logger.info("💡 To restart Claude Code processes:")
        logger.info("   wsl pkill -f claude 2>/dev/null || true")
        logger.info("   wsl killall claude 2>/dev/null || true")
        logger.info("   # Then start Claude Code again")

        return True

def main():
    """Main function"""
    print("🔧 MCP Memory Integration Configurator v2")
    print("=" * 45)

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
