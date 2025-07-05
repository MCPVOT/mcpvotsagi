#!/usr/bin/env python3
"""
Enhanced AGI System Launcher
============================
🚀 Launch the enhanced AGI system with modern UI
"""

import os
import sys
import subprocess
import time
import requests
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    required_packages = [
        'aiohttp',
        'psutil',
        'numpy',
        'pandas',
        'pyyaml',
        'requests',
        'ipfshttpclient'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"🔧 Installing missing dependencies: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("✅ Dependencies installed successfully")

def check_ollama():
    """Check if Ollama is running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def start_ollama():
    """Start Ollama if not running"""
    if not check_ollama():
        print("🔄 Starting Ollama...")
        try:
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            if check_ollama():
                print("✅ Ollama started successfully")
            else:
                print("⚠️ Ollama may not be properly installed")
        except Exception as e:
            print(f"⚠️ Could not start Ollama: {e}")
    else:
        print("✅ Ollama is already running")

def wait_for_server(port=8889, timeout=30):
    """Wait for the server to start"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://localhost:{port}', timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    """Main launcher function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 🚀 Enhanced AGI System v2.0                  ║
║                    Modern UI Dashboard                       ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Change to MCPVotsAGI directory
    os.chdir(Path(__file__).parent)

    # Check dependencies
    print("🔍 Checking dependencies...")
    check_dependencies()

    # Check and start Ollama
    print("🔍 Checking Ollama...")
    start_ollama()

    # Start the enhanced AGI system
    print("🚀 Starting Enhanced AGI System...")
    enhanced_system_path = Path("src/core/ENHANCED_AGI_SYSTEM.py")

    if not enhanced_system_path.exists():
        print("❌ Enhanced AGI System not found!")
        sys.exit(1)

    # Start the system
    process = subprocess.Popen([sys.executable, str(enhanced_system_path)])

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    if wait_for_server(8889):
        print("✅ Enhanced AGI System is running!")
        print("🌐 Dashboard: http://localhost:8889")

        # Open browser
        try:
            webbrowser.open('http://localhost:8889')
            print("🎉 Browser opened automatically")
        except:
            print("🔗 Please open http://localhost:8889 in your browser")

        print("""
╔══════════════════════════════════════════════════════════════╗
║                    🎯 System Ready!                          ║
║                                                              ║
║  • Enhanced Chat Interface with Modern UI                   ║
║  • Real-time System Metrics                                 ║
║  • Advanced DeepSeek-R1 Integration                         ║
║  • MCP Tools Suite                                          ║
║  • Context7 Documentation Bridge                            ║
║                                                              ║
║  Press Ctrl+C to stop the system                            ║
╚══════════════════════════════════════════════════════════════╝
""")

        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n👋 Shutting down Enhanced AGI System...")
            process.terminate()
            process.wait()
            print("✅ System shutdown complete")
    else:
        print("❌ Server failed to start within timeout")
        process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
