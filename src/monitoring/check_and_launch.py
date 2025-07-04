#!/usr/bin/env python3
"""
Check status and launch dashboard on available port
"""

import socket
import subprocess
import sys

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True if available

def find_available_port(start=3010):
    """Find an available port starting from the given port"""
    for port in range(start, start + 100):
        if check_port(port):
            return port
    return None

def main():
    print("MCPVotsAGI Dashboard Launcher")
    print("="*40)
    
    # Check default port
    default_port = 3010
    if check_port(default_port):
        print(f"✅ Port {default_port} is available")
        port = default_port
    else:
        print(f"⚠️  Port {default_port} is in use")
        port = find_available_port(default_port + 1)
        if port:
            print(f"✅ Found available port: {port}")
        else:
            print("❌ No available ports found!")
            return
    
    # Update the dashboard to use the available port
    dashboard_path = "/mnt/c/Workspace/MCPVotsAGI/oracle_agi_ultimate_unified_v2.py"
    
    # Create a temporary launcher that uses the available port
    launcher_content = f'''
import sys
sys.path.insert(0, "/mnt/c/Workspace/MCPVotsAGI")
from oracle_agi_ultimate_unified_v2 import OracleAGIUnifiedDashboard

dashboard = OracleAGIUnifiedDashboard()
dashboard.run(port={port})
'''
    
    launcher_path = "/mnt/c/Workspace/MCPVotsAGI/temp_launcher.py"
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    print(f"\n🚀 Launching dashboard on port {port}...")
    print(f"🌐 Dashboard URL: http://localhost:{port}")
    print("\nPress Ctrl+C to stop\n")
    
    # Launch with virtual environment
    cmd = [
        "/mnt/c/Workspace/MCPVotsAGI/venv/bin/python",
        launcher_path
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")

if __name__ == "__main__":
    main()