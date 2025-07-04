#!/usr/bin/env python3
"""
START ULTIMATE AGI WITH CLAUDIA + MCP INTEGRATION
================================================
🚀 Launch the ONE unified AGI system with:
- DeepSeek-R1 (via Ollama)
- All MCP tools
- Claudia GUI integration
- Complete system consolidation
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def check_port_available(port):
    """Check if port is available"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    except:
        return False

def check_ollama_and_deepseek():
    """Check if Ollama is running and DeepSeek-R1 is available"""
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            deepseek_available = any(
                "deepseek-r1" in model.get("name", "").lower()
                for model in models.get("models", [])
            )
            return True, deepseek_available
        return False, False
    except:
        return False, False

def start_ollama():
    """Start Ollama if not running"""
    print("🔧 Starting Ollama...")
    try:
        subprocess.Popen(["ollama", "serve"], shell=True)
        time.sleep(3)
        return True
    except:
        print("❌ Could not start Ollama. Please install Ollama first.")
        return False

def pull_deepseek_model():
    """Pull DeepSeek-R1 model if not available"""
    print("📥 Pulling DeepSeek-R1 model...")
    try:
        result = subprocess.run([
            "ollama", "pull", "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
        ], capture_output=True, text=True)
        return result.returncode == 0
    except:
        print("❌ Could not pull DeepSeek-R1 model")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    required_packages = [
        "aiohttp", "psutil", "numpy", "pandas", "pyyaml",
        "requests", "ipfshttpclient", "websockets"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"📦 Installing missing dependencies: {', '.join(missing)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", *missing
            ])
        except:
            print("❌ Could not install dependencies")
            return False

    return True

def main():
    print("""
🚀 ===================================================
   ULTIMATE AGI SYSTEM WITH CLAUDIA + MCP
🚀 ===================================================

🧠 DeepSeek-R1 + Claudia GUI + MCP Tools
🔥 The ONE and ONLY unified AGI system!
⚡ No more fragmented dashboards!
    """)

    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print(f"📁 Working directory: {os.getcwd()}")

    # Check port availability
    if not check_port_available(8888):
        print("⚠️  Port 8888 is already in use!")
        print("🔧 Options:")
        print("  1. Stop existing service: .\\STOP_ALL_AGI.bat")
        print("  2. Check what's using port: .\\CHECK_PORT.ps1")
        print("  3. Try accessing: http://localhost:8888")
        return

    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed")
        return

    # Check Ollama and DeepSeek-R1
    print("🔍 Checking Ollama and DeepSeek-R1...")
    ollama_running, deepseek_available = check_ollama_and_deepseek()

    if not ollama_running:
        if not start_ollama():
            print("❌ Could not start Ollama")
            return
        time.sleep(2)
        ollama_running, deepseek_available = check_ollama_and_deepseek()

    if not deepseek_available:
        print("📥 DeepSeek-R1 model not found, pulling...")
        if not pull_deepseek_model():
            print("❌ Could not pull DeepSeek-R1 model")
            return

    # Check MCP servers
    print("🔍 Checking MCP servers...")
    mcp_servers = [
        "servers/filesystem_server.py",
        "servers/memory_server.py",
        "servers/github_server.py",
        "servers/puppeteer_server.py"
    ]

    for server in mcp_servers:
        if not Path(server).exists():
            print(f"⚠️  MCP server not found: {server}")

    # Start the system
    print("\n🚀 Starting ULTIMATE AGI SYSTEM with Claudia + MCP...")

    try:
        # Start the ultimate AGI system
        subprocess.run([sys.executable, "src/core/ULTIMATE_AGI_SYSTEM.py"])

    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"💥 Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if all dependencies are installed")
        print("2. Verify Ollama is running with DeepSeek-R1")
        print("3. Check if port 8888 is available")
        print("4. Ensure MCP servers are properly configured")

if __name__ == "__main__":
    main()
