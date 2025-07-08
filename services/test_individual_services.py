#!/usr/bin/env python3
"""
Individual Service Tester
=========================
Test individual services to see which ones work
"""

import subprocess
import time
import requests
import socket
from pathlib import Path

def check_port(port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_service(script_name, port, timeout=10):
    """Test if a service script can start successfully"""
    print(f"\n🔄 Testing {script_name}...")

    # Check if script exists
    script_path = Path(script_name)
    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return False

    # Check if port is available
    if check_port(port):
        print(f"⚠️ Port {port} already in use")
        return False

    try:
        # Start the service
        process = subprocess.Popen([
            'python', script_name
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for startup
        print(f"⏳ Waiting {timeout} seconds for startup...")
        for i in range(timeout):
            if check_port(port):
                print(f"✅ {script_name} started successfully on port {port}")

                # Try HTTP request if it looks like a web service
                try:
                    response = requests.get(f"http://localhost:{port}", timeout=2)
                    print(f"📡 HTTP Status: {response.status_code}")
                except Exception as e:
                    print(f"📡 HTTP Test: {e}")

                # Cleanup
                process.terminate()
                process.wait(timeout=5)
                return True
            time.sleep(1)

        # Service didn't start properly
        print(f"❌ {script_name} failed to start on port {port}")

        # Get error output
        stdout, stderr = process.communicate(timeout=2)
        if stderr:
            print(f"🔍 Error output: {stderr.decode()[:200]}...")

        process.terminate()
        return False

    except Exception as e:
        print(f"❌ Error testing {script_name}: {e}")
        return False

def main():
    print("🧪 TESTING INDIVIDUAL SERVICES")
    print("=" * 50)

    # Services to test
    services = [
        ("ultimate_trading_system_v3.py", 8892),
        ("jupiter_rl_integration.py", 8895),
        ("deepseek_r1_trading_agent_enhanced.py", 8896),
        ("watchyourlan_cyberpunk_ultimate_integration.py", 8893),
        ("cyberpunk_dashboard.py", 8894),
        ("claudia_enhanced_trading_system.py", 8897),
    ]

    working_services = []

    for script, port in services:
        if test_service(script, port):
            working_services.append((script, port))

    print(f"\n📊 RESULTS")
    print("=" * 30)
    print(f"✅ Working services: {len(working_services)}")
    print(f"❌ Failed services: {len(services) - len(working_services)}")

    if working_services:
        print(f"\n✅ WORKING SERVICES:")
        for script, port in working_services:
            print(f"   {script} (Port: {port})")

    print(f"\n💡 Recommendation: Use the working services in your launcher")

if __name__ == "__main__":
    main()
