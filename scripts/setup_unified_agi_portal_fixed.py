#!/usr/bin/env python3
"""
Setup All MCP Servers for Unified AGI Portal (Fixed Encoding)
============================================================
Install and configure all MCP servers for the AGI portal
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"[INFO] {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   [SUCCESS] Completed")
            return True
        else:
            print(f"   [FAILED] {result.stderr}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("[SETUP] Installing Node.js MCP Servers...")

    # Check if Node.js is available
    if not run_command("node --version", "Checking Node.js"):
        print("[ERROR] Node.js not found! Please install Node.js first.")
        return False

    # Install MCP servers
    mcp_servers = [
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-github",
        "@modelcontextprotocol/server-memory",
        "@modelcontextprotocol/server-brave-search",
        "@agentdeskai/browser-tools-mcp",
        "@modelcontextprotocol/server-puppeteer"
    ]

    success_count = 0
    for server in mcp_servers:
        if run_command(f"npm install -g {server}", f"Installing {server}"):
            success_count += 1
        time.sleep(1)  # Brief pause between installs

    print(f"[STATUS] MCP Servers: {success_count}/{len(mcp_servers)} installed")
    return success_count > 0

def install_python_dependencies():
    """Install Python dependencies"""
    print("[SETUP] Installing Python Dependencies...")

    dependencies = [
        "aiohttp",
        "psutil",
        "numpy",
        "pandas",
        "pyyaml",
        "requests",
        "websockets",
        "ipfshttpclient",
        "ollama",
        "python-dotenv"
    ]

    success_count = 0
    for dep in dependencies:
        if run_command(f"pip install {dep}", f"Installing {dep}"):
            success_count += 1

    print(f"[STATUS] Python Dependencies: {success_count}/{len(dependencies)} installed")
    return success_count > 0

def setup_directories():
    """Create necessary directories"""
    print("[SETUP] Setting up directories...")

    directories = [
        "data",
        "logs",
        "static",
        "static/css",
        "static/js",
        "static/img",
        "temp",
        "backups"
    ]

    workspace = Path(__file__).parent
    for directory in directories:
        dir_path = workspace / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   [CREATED] {directory}")

    return True

def create_env_file():
    """Create environment file"""
    print("[SETUP] Creating environment configuration...")

    env_content = """# Unified AGI Portal Environment Configuration
# ================================================

# Server Configuration
AGI_PORTAL_HOST=localhost
AGI_PORTAL_PORT=8000
AGI_PORTAL_WEBSOCKET_PORT=8001

# DeepSeek-R1 Configuration
OLLAMA_ENDPOINT=http://localhost:11434
DEEPSEEK_MODEL=deepseek-r1

# IPFS Configuration
IPFS_ENDPOINT=http://localhost:5001
IPFS_GATEWAY=http://localhost:8080

# MCP Servers Configuration
MCP_FILESYSTEM_PORT=3000
MCP_GITHUB_PORT=3001
MCP_MEMORY_PORT=3002
MCP_SEARCH_PORT=3003
MCP_SOLANA_PORT=3004
MCP_HUGGINGFACE_PORT=3005
MCP_BROWSER_PORT=3006

# Database Configuration
DATABASE_PATH=data/agi_portal.db

# Security
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agi_portal.log
"""

    env_path = Path(__file__).parent / ".env"
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)

    print("   [CREATED] .env file created")
    return True

def create_startup_scripts():
    """Create additional startup scripts"""
    print("[SETUP] Creating startup scripts...")

    # Create MCP server startup script
    mcp_script = '''#!/usr/bin/env python3
"""
Start All MCP Servers
====================
"""

import subprocess
import time
import sys
from pathlib import Path

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
            except Exception:
                pass
        print("All servers stopped.")

if __name__ == "__main__":
    main()
'''

    mcp_script_path = Path(__file__).parent / "START_MCP_SERVERS.py"
    with open(mcp_script_path, "w", encoding="utf-8") as f:
        f.write(mcp_script)

    print("   [CREATED] MCP servers startup script")

    # Create Windows batch file
    batch_content = """@echo off
echo Starting MCP Servers...
python START_MCP_SERVERS.py
pause
"""

    batch_path = Path(__file__).parent / "START_MCP_SERVERS.bat"
    with open(batch_path, "w", encoding="utf-8") as f:
        f.write(batch_content)

    print("   [CREATED] Windows batch file")
    return True

def test_installations():
    """Test if everything is installed correctly"""
    print("[TEST] Testing installations...")

    # Test Node.js packages
    node_packages = [
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-github",
        "@modelcontextprotocol/server-memory"
    ]

    for package in node_packages:
        if run_command(f"npm list -g {package}", f"Testing {package}"):
            print(f"   [OK] {package} available")
        else:
            print(f"   [MISSING] {package} not found")

    # Test Python imports
    python_modules = [
        "aiohttp",
        "psutil",
        "numpy",
        "pandas",
        "yaml",
        "requests",
        "websockets"
    ]

    for module in python_modules:
        try:
            __import__(module)
            print(f"   [OK] {module} importable")
        except ImportError:
            print(f"   [MISSING] {module} not importable")

    return True

def main():
    """Main setup function"""
    print("Unified AGI Portal Setup")
    print("=" * 50)
    print("This will install and configure all components for the AGI portal")
    print()

    steps = [
        ("Setting up directories", setup_directories),
        ("Installing Python dependencies", install_python_dependencies),
        ("Installing Node.js MCP servers", install_node_dependencies),
        ("Creating environment file", create_env_file),
        ("Creating startup scripts", create_startup_scripts),
        ("Testing installations", test_installations)
    ]

    success_count = 0
    for description, func in steps:
        print(f"[STEP] {description}...")
        print("-" * 40)
        if func():
            success_count += 1
            print(f"[SUCCESS] {description} completed")
        else:
            print(f"[FAILED] {description} failed")

    print()
    print("=" * 50)
    print(f"[RESULTS] Setup: {success_count}/{len(steps)} steps completed")

    if success_count == len(steps):
        print()
        print("[SUCCESS] Setup completed successfully!")
        print()
        print("[NEXT] To start the AGI portal:")
        print("   1. Run: python START_UNIFIED_AGI_PORTAL.py")
        print("   2. Or double-click: START_UNIFIED_AGI_PORTAL.bat")
        print()
        print("[ACCESS] Portal URL: http://localhost:8000")
    else:
        print()
        print("[WARNING] Some steps failed. Please check the errors above.")
        print("You may need to install missing dependencies manually.")

    print()
    print("[DOCS] For more information, check the documentation in docs/")

if __name__ == "__main__":
    main()
