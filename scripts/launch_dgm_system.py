#!/usr/bin/env python3
"""
DGM System Launcher - Start all DGM components
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_port(port):
    """Check if port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True if available

def start_component(name, command, port):
    """Start a component"""
    print(f"[LAUNCH] Starting {name} on port {port}...")
    
    if not check_port(port):
        print(f"[WARN] Port {port} already in use, skipping {name}")
        return None
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give it time to start
        
        if process.poll() is None:
            print(f"[OK] {name} started (PID: {process.pid})")
            return process
        else:
            print(f"[FAIL] {name} failed to start")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to start {name}: {e}")
        return None

def main():
    print("=" * 60)
    print("DGM SYSTEM LAUNCHER")
    print("=" * 60)
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    components = [
        {
            "name": "Unified DGM Server",
            "command": f"{sys.executable} core/unified_dgm_server_v2.py",
            "port": 8013
        },
        {
            "name": "DGM Dashboard",
            "command": f"{sys.executable} -m streamlit run dgm_dashboard.py --server.port 8501",
            "port": 8501
        }
    ]
    
    processes = []
    
    try:
        # Start all components
        for component in components:
            process = start_component(
                component["name"],
                component["command"],
                component["port"]
            )
            if process:
                processes.append(process)
        
        print("\n[INFO] DGM System is running. Press Ctrl+C to stop all components.")
        print("\n[URLS]")
        print("  - DGM WebSocket: ws://localhost:8013")
        print("  - DGM Dashboard: http://localhost:8501")
        
        # Wait for interrupt
        while True:
            time.sleep(1)
            # Check if processes are still running
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    print(f"\n[WARN] Component {components[i]['name']} stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n[INFO] Stopping all components...")
        for process in processes:
            if process:
                process.terminate()
                process.wait()
        print("[OK] All components stopped")

if __name__ == "__main__":
    main()
