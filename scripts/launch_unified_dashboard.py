#!/usr/bin/env python3
"""
Unified AGI Dashboard Launcher
============================
Single launcher for the combined Jupiter Trading + Network Monitoring + AI Analysis
"""

import asyncio
import subprocess
import sys
import time
import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UnifiedLauncher")

def check_ollama_availability():
    """Check if Ollama is available"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return True, len(models)
    except Exception:
        pass
    return False, 0

def check_port_availability(port):
    """Check if port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except Exception:
        return False

async def main():
    """Main launcher function"""
    print("\n" + "="*80)
    print("🚀 UNIFIED AGI DASHBOARD LAUNCHER")
    print("="*80)

    # Check Ollama
    ollama_available, model_count = check_ollama_availability()
    if ollama_available:
        print(f"✅ Ollama: Available with {model_count} models")
    else:
        print("⚠️ Ollama: Not available - AI analysis will be limited")

    # Check port
    port = 8900
    if not check_port_availability(port):
        print(f"⚠️ Port {port} is in use - trying alternative...")
        port = 8901
        if not check_port_availability(port):
            print(f"❌ Ports {port-1} and {port} are both in use")
            return

    print(f"🌐 Starting on port {port}")

    try:
        # Import and run the unified dashboard
        from unified_agi_dashboard import UnifiedAGIDashboard

        dashboard = UnifiedAGIDashboard(port=port)
        runner = await dashboard.start()

        print("\n" + "="*80)
        print("🎉 UNIFIED AGI DASHBOARD READY!")
        print("="*80)
        print(f"🌐 Dashboard URL: http://localhost:{port}")
        print("📊 Features:")
        print("   • Jupiter DEX real-time trading data")
        print("   • Network monitoring and analytics")
        print("   • System performance metrics")
        print("   • Claudia AI-powered market analysis")
        print("   • Unified cyberpunk-themed interface")
        print("   • WebSocket real-time updates")
        print("="*80)
        print("Press Ctrl+C to stop...")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Unified AGI Dashboard...")
        dashboard.running = False
        await runner.cleanup()
        print("✅ Shutdown complete")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
