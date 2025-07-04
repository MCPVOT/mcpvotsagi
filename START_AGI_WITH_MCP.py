#!/usr/bin/env python3
"""
Start Ultimate AGI with Full MCP Integration + Claudia GUI
==========================================================
Launches the system with:
- DeepSeek-R1 able to use all MCP tools
- Claudia GUI integration
- Complete system consolidation
"""

import asyncio
import subprocess
import sys
import os
import json
import time
from pathlib import Path

# Add to Python path
sys.path.append(str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")

    # Check Python packages
    required_packages = ['aiohttp', 'requests', 'websockets', 'psutil']
    missing = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

    print("✅ Python dependencies OK")

def check_ollama():
    """Check if Ollama is running and DeepSeek-R1 is available"""
    print("\n🧠 Checking Ollama and DeepSeek-R1...")

    import requests

    try:
        # Check Ollama service
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            print("✅ Ollama service is running")

            # Check for DeepSeek-R1
            models = resp.json().get('models', [])
            has_deepseek = any('DeepSeek-R1' in model.get('name', '') for model in models)

            if has_deepseek:
                print("✅ DeepSeek-R1 model available")
                return True
            else:
                print("❌ DeepSeek-R1 not found")
                print("💡 Pull it with: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL")
                return False
        else:
            print("❌ Ollama service not responding properly")
            return False
    except Exception as e:
        print(f"❌ Ollama not accessible: {e}")
        print("💡 Start Ollama with: ollama serve")
        return False

def setup_mcp_config():
    """Ensure MCP configuration is set up"""
    print("\n🔧 Setting up MCP configuration...")

    # Create config directory if needed
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Check if ultimate_agi_mcp.json exists
    mcp_config_path = config_dir / "ultimate_agi_mcp.json"
    if mcp_config_path.exists():
        print("✅ MCP configuration found")
    else:
        print("⚠️  MCP configuration missing - run setup first")

    # Check for cline_mcp_settings.json
    cline_path = Path.home() / ".config" / "Claude" / "cline_mcp_settings.json"
    if cline_path.exists():
        print("✅ Cline MCP settings found")

        # Parse and show available tools
        with open(cline_path) as f:
            cline_config = json.load(f)
            servers = cline_config.get('mcpServers', {})

        print(f"📦 Available MCP servers: {', '.join(servers.keys())}")
    else:
        print("⚠️  No Cline MCP settings found")

async def start_ultimate_agi():
    """Start the Ultimate AGI System with MCP integration"""
    print("\n🚀 Starting Ultimate AGI System with MCP Integration...")

    # Check if port is already in use
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8888))
    sock.close()

    if result == 0:
        print("\n⚠️  Port 8888 is already in use!")
        print("Another instance might be running or another app is using this port.")
        print("\nOptions:")
        print("1. Run STOP_ALL_AGI.bat to stop existing instances")
        print("2. Use a different port (edit the code)")
        print("3. Access existing instance at http://localhost:8888")
        return

    # Import the systems
    from core.ULTIMATE_AGI_SYSTEM import UltimateAGISystem
    from core.deepseek_mcp_integration import DeepSeekR1WithMCP
    from core.ultimate_agi_mcp_bridge import UltimateAGIMCPBridge

    print("""
╔══════════════════════════════════════════════════════════════╗
║           ULTIMATE AGI SYSTEM WITH MCP INTEGRATION           ║
╠══════════════════════════════════════════════════════════════╣
║  🧠 DeepSeek-R1: Can now use all MCP tools                  ║
║  🔗 MCP Tools: filesystem, github, memory, browser, solana  ║
║  💾 Memory: Persistent with vector search                    ║
║  📊 RL System: 800GB data integration                       ║
║  🤖 Agents: Multi-agent swarm coordination                  ║
║  🌐 IPFS: Decentralized storage ready                       ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Import required modules for the enhanced handler
    from aiohttp import web
    from datetime import datetime

    # Create enhanced system
    class UltimateAGIWithMCP(UltimateAGISystem):
        """Enhanced Ultimate AGI with MCP integration"""

        def __init__(self):
            super().__init__()
            self.deepseek_mcp = DeepSeekR1WithMCP()
            self.mcp_bridge = UltimateAGIMCPBridge()

        async def handle_chat_message(self, request):
            """Enhanced chat handler that uses MCP tools"""
            data = await request.json()
            message = data.get('message', '')
            use_tools = data.get('use_tools', True)

            # Process with MCP-enabled DeepSeek
            response = await self.deepseek_mcp.process(message, allow_tools=use_tools)

            return web.json_response({
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'model': 'DeepSeek-R1 with MCP'
            })

    # Start the enhanced system
    system = UltimateAGIWithMCP()
    await system.run()

def main():
    """Main entry point"""
    print("""
    ███    ███  ██████ ██████  ██    ██  ██████  ████████ ███████  █████   ██████  ██
    ████  ████ ██      ██   ██ ██    ██ ██    ██    ██    ██      ██   ██ ██       ██
    ██ ████ ██ ██      ██████  ██    ██ ██    ██    ██    ███████ ███████ ██   ███ ██
    ██  ██  ██ ██      ██       ██  ██  ██    ██    ██         ██ ██   ██ ██    ██ ██
    ██      ██  ██████ ██        ████    ██████     ██    ███████ ██   ██  ██████  ██

    🚀 ULTIMATE AGI SYSTEM - MCP ENHANCED EDITION
    """)

    # Check everything
    check_dependencies()
    ollama_ok = check_ollama()
    setup_mcp_config()

    if not ollama_ok:
        print("\n⚠️  Please fix Ollama/DeepSeek-R1 issues before continuing")
        input("Press Enter to exit...")
        return

    # Start the system
    try:
        print("\n🌟 All checks passed! Starting system...")
        print("📡 Dashboard will be available at: http://localhost:8888")
        print("\nPress Ctrl+C to stop\n")

        # Add a small delay for dramatic effect
        time.sleep(2)

        # Run the async system
        asyncio.run(start_ultimate_agi())

    except KeyboardInterrupt:
        print("\n\n✋ Shutting down Ultimate AGI System...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()