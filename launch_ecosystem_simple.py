#!/usr/bin/env python3
"""
Simple Ecosystem Launcher
========================
Launches MCPVotsAGI ecosystem without external dependencies
"""

import subprocess
import time
import os
import sys
from pathlib import Path

def is_port_open(port):
    """Check if a port is open"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def launch_service(name, command, port):
    """Launch a service"""
    print(f"Starting {name} on port {port}...")
    
    # Check if already running
    if is_port_open(port):
        print(f"  ✓ {name} already running on port {port}")
        return None
    
    try:
        # Start process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        # Wait a bit
        time.sleep(3)
        
        # Check if started
        if is_port_open(port):
            print(f"  ✓ {name} started successfully")
            return process
        else:
            print(f"  ✗ {name} failed to start")
            return None
            
    except Exception as e:
        print(f"  ✗ Error starting {name}: {e}")
        return None

def main():
    print("="*60)
    print("MCPVotsAGI Ecosystem Launcher")
    print("="*60)
    
    workspace = Path("/mnt/c/Workspace")
    mcpvots = workspace / "MCPVots"
    mcpvotsagi = workspace / "MCPVotsAGI"
    
    # Use the system Python
    python_cmd = sys.executable
    
    print(f"\nUsing Python: {python_cmd}")
    print(f"MCPVots path: {mcpvots}")
    print(f"MCPVotsAGI path: {mcpvotsagi}")
    
    # Define services to start
    services = [
        # Core dashboard - this should work without additional dependencies
        {
            "name": "Oracle AGI Dashboard",
            "command": f"{python_cmd} {mcpvotsagi}/oracle_agi_ultimate_unified.py",
            "port": 3010
        }
    ]
    
    # Try to start enhanced dashboard if modules available
    try:
        import aiohttp
        services[0]["command"] = f"{python_cmd} {mcpvotsagi}/oracle_agi_ultimate_unified_v2.py"
        print("\n✓ Enhanced dashboard available")
    except ImportError:
        print("\n! Using basic dashboard (aiohttp not installed)")
    
    # Add other services that might work
    additional_services = [
        {
            "name": "Memory MCP",
            "command": f"{python_cmd} {mcpvots}/servers/enhanced_memory_mcp_server.py",
            "port": 3002
        },
        {
            "name": "GitHub MCP",
            "command": f"{python_cmd} {mcpvots}/servers/mcp_github_server.py",
            "port": 3001
        }
    ]
    
    # Start services
    print("\nStarting services...")
    processes = []
    
    for service in services:
        process = launch_service(service["name"], service["command"], service["port"])
        if process:
            processes.append(process)
    
    # Try additional services
    print("\nAttempting additional services...")
    for service in additional_services:
        if os.path.exists(service["command"].split()[-1]):
            process = launch_service(service["name"], service["command"], service["port"])
            if process:
                processes.append(process)
        else:
            print(f"  ! {service['name']} script not found")
    
    print("\n" + "="*60)
    print("Ecosystem Launch Summary")
    print("="*60)
    
    # Check what's running
    running_services = []
    for port in [3010, 3001, 3002, 8888, 11434]:
        if is_port_open(port):
            running_services.append(port)
    
    if running_services:
        print(f"\n✓ Services running on ports: {', '.join(map(str, running_services))}")
        print(f"\n🌐 Dashboard URL: http://localhost:3010")
    else:
        print("\n✗ No services successfully started")
        print("\nTroubleshooting:")
        print("1. Check if Python modules are installed")
        print("2. Check if service scripts exist")
        print("3. Check for port conflicts")
    
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep running
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        for process in processes:
            if process:
                process.terminate()
        print("Services stopped")

if __name__ == "__main__":
    main()