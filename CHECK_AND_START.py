#!/usr/bin/env python3
"""
Check ports and start ULTIMATE AGI SYSTEM with available port
"""

import os
import sys
import socket
import subprocess
import time

def check_port(port):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True if available

def find_available_port(start_port=8888):
    """Find available port starting from start_port"""
    for port in range(start_port, start_port + 100):
        if check_port(port):
            return port
    return None

def stop_process_on_port(port):
    """Stop process using port (Windows)"""
    try:
        # Find PID using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        print(f"Stopping process {pid} on port {port}")
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        time.sleep(1)
    except Exception as e:
        print(f"Error stopping process: {e}")

def main():
    print("MCPVotsAGI System Launcher")
    print("=" * 60)
    
    # Check main port
    port = 8888
    if not check_port(port):
        print(f"Port {port} is in use.")
        choice = input("Stop existing process? (y/n): ")
        if choice.lower() == 'y':
            stop_process_on_port(port)
        else:
            port = find_available_port(port + 1)
            if port:
                print(f"Using alternative port: {port}")
            else:
                print("No available ports found!")
                return
    
    # Set environment
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['AGI_PORT'] = str(port)
    
    # Set UTF-8 console
    if sys.platform == 'win32':
        subprocess.run('chcp 65001', shell=True, capture_output=True)
    
    print(f"\nStarting ULTIMATE AGI SYSTEM on port {port}...")
    print("=" * 60)
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
    
    # Import and run
    from core.ULTIMATE_AGI_SYSTEM import main as agi_main
    
    try:
        agi_main()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")