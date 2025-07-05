#!/usr/bin/env python3
"""
Test ULTIMATE AGI SYSTEM V3
"""

import requests
import json
import sys

def test_system():
    """Test the system endpoints"""
    base_url = "http://localhost:8889"
    
    print("🧪 Testing ULTIMATE AGI SYSTEM V3...")
    print(f"   Base URL: {base_url}")
    print()
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Please make sure the server is running on port 8889")
        return False
    
    # Test 2: Check status endpoint
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ Status endpoint working")
            print(f"   Version: {status.get('version', 'Unknown')}")
            print(f"   Uptime: {status.get('uptime', 0)}s")
            
            # Check V3 features
            v3_features = status.get('v3_features', {})
            print(f"   Context7: {v3_features.get('context7_status', 'Unknown')}")
            print(f"   Claudia: {v3_features.get('claudia_status', 'Unknown')}")
            print(f"   Agents: {v3_features.get('agents_count', 0)}")
        else:
            print(f"❌ Status endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test 3: Test chat endpoint
    print("\n📝 Testing chat endpoint...")
    try:
        # Basic chat test
        chat_data = {
            "message": "Hello, are you working?"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Basic chat working")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
        else:
            print(f"❌ Chat returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
    
    # Test 4: Test agent execution
    print("\n🤖 Testing agent execution...")
    try:
        agent_data = {
            "message": "Create a simple React component",
            "use_claudia": True,
            "agent": "ultimate-agi-orchestrator"
        }
        response = requests.post(f"{base_url}/api/chat", json=agent_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Agent execution working")
            print(f"   System info: {result.get('system_info', {})}")
        else:
            print(f"❌ Agent execution returned {response.status_code}")
    except Exception as e:
        print(f"❌ Agent execution error: {e}")
    
    # Test 5: Check V3 dashboard
    print("\n📊 Testing V3 dashboard...")
    try:
        response = requests.get(f"{base_url}/api/v3/dashboard", timeout=5)
        if response.status_code == 200:
            dashboard = response.json()
            print("✅ V3 dashboard working")
            print(f"   Active models: {len(dashboard.get('active_models', {}))}")
            print(f"   Real-time metrics: {dashboard.get('real_time_metrics', {}).get('system_health', 'Unknown')}")
        else:
            print(f"❌ V3 dashboard returned {response.status_code}")
    except Exception as e:
        print(f"❌ V3 dashboard error: {e}")
    
    print("\n✨ Testing complete!")
    return True

if __name__ == "__main__":
    test_system()