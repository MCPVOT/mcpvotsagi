#!/usr/bin/env python3
"""
Simple launcher for Oracle AGI Unified Dashboard
Ensures all dependencies are available and starts the system
"""

import subprocess
import sys
import os
import time
import socket
from pathlib import Path

def check_port(port):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def find_python():
    """Find Python executable"""
    for cmd in ['python3', 'python', sys.executable]:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return cmd
        except:
            continue
    return 'python'

def install_dependencies():
    """Install required dependencies"""
    python = find_python()
    requirements = [
        'aiohttp>=3.9.0',
        'websockets>=12.0',
        'aiohttp-cors>=0.7.0',
        'psutil>=5.9.0',
        'aiosqlite>=0.19.0'
    ]
    
    print("Installing core dependencies...")
    for req in requirements:
        subprocess.run([python, '-m', 'pip', 'install', req], capture_output=True)

def main():
    print("=" * 60)
    print("  Oracle AGI Unified Dashboard Launcher")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 7):
        print(f"❌ Python 3.7+ required (found {python_version.major}.{python_version.minor})")
        sys.exit(1)
    
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Install dependencies
    try:
        import aiohttp
        import websockets
        import aiohttp_cors
        import psutil
        print("✓ Dependencies already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        install_dependencies()
        print("✓ Dependencies installed")
    
    # Find available port
    ports = [3011, 3010, 3012, 8080, 8081, 8082]
    available_port = None
    
    for port in ports:
        if check_port(port):
            available_port = port
            break
    
    if not available_port:
        print("❌ No available ports found")
        sys.exit(1)
    
    print(f"✓ Using port {available_port}")
    
    # Start the dashboard
    python = find_python()
    oracle_agi_path = Path(__file__).parent / "oracle_agi_unified_final.py"
    
    if not oracle_agi_path.exists():
        print(f"❌ oracle_agi_unified_final.py not found at {oracle_agi_path}")
        sys.exit(1)
    
    print(f"\n🚀 Starting Oracle AGI Dashboard on http://localhost:{available_port}")
    print("\nPress Ctrl+C to stop\n")
    
    # Set environment variables
    env = os.environ.copy()
    env['ORACLE_AGI_PORT'] = str(available_port)
    
    try:
        # Run the dashboard
        process = subprocess.Popen(
            [python, str(oracle_agi_path)],
            env=env,
            cwd=Path(__file__).parent
        )
        
        # Wait a moment for startup
        time.sleep(2)
        
        print(f"\n✨ Dashboard should now be available at http://localhost:{available_port}")
        print("\nThe dashboard will:")
        print("- Auto-start required MCP tools")
        print("- Manage all connections")
        print("- Provide unified interface for all tools")
        print("\nMCP Tools available:")
        print("- Memory MCP (Knowledge Graph)")
        print("- GitHub MCP (Repository Management)")
        print("- Solana MCP (Trading)")
        print("- Browser MCP (Web Automation)")
        print("- OpenCTI MCP (Security)")
        
        # Keep running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down Oracle AGI Dashboard...")
        process.terminate()
        time.sleep(1)
        print("✓ Dashboard stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()