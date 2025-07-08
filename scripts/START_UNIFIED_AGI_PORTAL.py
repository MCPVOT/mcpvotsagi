#!/usr/bin/env python3
"""
START UNIFIED AGI PORTAL
========================
Launch the ultimate AGI dashboard with DeepSeek-R1 + IPFS
"""

import sys
import subprocess
import os
import time
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")

    deps = [
        "aiohttp",
        "psutil",
        "numpy",
        "pandas",
        "pyyaml",
        "requests",
        "websockets",
        "ipfshttpclient"
    ]

    for dep in deps:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"  ❌ {dep} (will try alternative)")

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            deepseek_found = any("deepseek" in model.get("name", "").lower() for model in models)

            print(f"🤖 Ollama Status: ✅ Running")
            print(f"🧠 DeepSeek-R1 Model: {'✅ Available' if deepseek_found else '❌ Not Found'}")

            if not deepseek_found:
                print("💡 To install DeepSeek-R1:")
                print("   ollama pull deepseek-r1")
                print("   or")
                print("   ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL")

            return True
    except Exception as e:
        print(f"🤖 Ollama Status: ❌ Not Running")
        print("💡 Start Ollama first: ollama serve")
        return False

def check_ipfs():
    """Check if IPFS is running"""
    try:
        import requests
        response = requests.get("http://localhost:5001/api/v0/version", timeout=3)
        if response.status_code == 200:
            print(f"🌐 IPFS Status: ✅ Running")
            return True
    except Exception:
        print(f"🌐 IPFS Status: ❌ Not Running")
        print("💡 Start IPFS: ipfs daemon")
        return False

def check_node_mcp():
    """Check if Node.js and MCP servers are available"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📦 Node.js Status: ✅ Available ({result.stdout.strip()})")

            # Check if MCP packages are installed
            mcp_packages = [
                "@modelcontextprotocol/server-filesystem",
                "@modelcontextprotocol/server-github",
                "@modelcontextprotocol/server-memory",
                "@modelcontextprotocol/server-brave-search"
            ]

            for package in mcp_packages:
                try:
                    result = subprocess.run(["npm", "list", package],
                                          capture_output=True, text=True)
                    status = "✅" if result.returncode == 0 else "❌"
                    print(f"  {status} {package}")
                except:
                    print(f"  ❌ {package}")

            return True
    except FileNotFoundError:
        print(f"📦 Node.js Status: ❌ Not Available")
        return False

def main():
    """Main function"""
    print("🌟 Starting Unified AGI Portal...")
    print("=" * 50)

    # Check dependencies
    install_dependencies()

    print("\n🔍 System Check:")
    print("-" * 30)

    ollama_ok = check_ollama()
    ipfs_ok = check_ipfs()
    node_ok = check_node_mcp()

    print(f"\n📊 System Status:")
    print(f"  Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"  IPFS: {'✅' if ipfs_ok else '❌'}")
    print(f"  Node.js/MCP: {'✅' if node_ok else '❌'}")

    if not ollama_ok:
        print("\n⚠️  Warning: Ollama not running. AGI functionality will be limited.")

    if not ipfs_ok:
        print("\n⚠️  Warning: IPFS not running. Decentralized storage will be disabled.")

    print("\n🚀 Launching Unified AGI Portal...")
    print("=" * 50)

    # Set up environment
    workspace = Path(__file__).parent.parent.parent
    os.chdir(workspace)

    # Launch the portal
    try:
        from src.core.unified_agi_portal import main as portal_main
        import asyncio
        asyncio.run(portal_main())
    except ImportError:
        print("❌ Error: Could not import unified_agi_portal")
        print("   Make sure you're running from the correct directory")
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down AGI Portal...")
        print("   Thanks for using Oracle AGI Portal!")
    except Exception as e:
        print(f"\n❌ Error starting portal: {e}")
        print("   Check the logs for more details")

if __name__ == "__main__":
    main()
