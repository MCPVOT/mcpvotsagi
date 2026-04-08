#!/usr/bin/env python3
"""
Check MCPVotsAGI Ecosystem Status
"""

import socket
import json
import urllib.request
import urllib.error

def check_port(port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def check_http_endpoint(url):
    """Check if HTTP endpoint is responding"""
    try:
        response = urllib.request.urlopen(url, timeout=2)
        return response.status == 200
    except Exception:
        return False

def main():
    print("MCPVotsAGI Ecosystem Status Check")
    print("="*50)
    
    services = [
        {"name": "Oracle AGI Dashboard", "port": 3010, "url": "http://localhost:3010"},
        {"name": "Oracle AGI Core", "port": 8888, "url": "http://localhost:8888"},
        {"name": "GitHub MCP", "port": 3001, "type": "websocket"},
        {"name": "Memory MCP", "port": 3002, "type": "websocket"},
        {"name": "Trilogy AGI", "port": 8000, "type": "websocket"},
        {"name": "Ollama", "port": 11434, "url": "http://localhost:11434"},
        {"name": "Gemini CLI", "port": 8015, "type": "websocket"},
        {"name": "n8n", "port": 5678, "url": "http://localhost:5678"},
    ]
    
    online_count = 0
    
    for service in services:
        port_open = check_port(service["port"])
        
        if port_open:
            # Additional HTTP check if URL provided
            if "url" in service and service.get("type") != "websocket":
                http_ok = check_http_endpoint(service["url"])
                if http_ok:
                    status = "✅ ONLINE (HTTP OK)"
                    online_count += 1
                else:
                    status = "⚠️  ONLINE (HTTP Failed)"
            else:
                status = "✅ ONLINE"
                online_count += 1
        else:
            status = "❌ OFFLINE"
        
        print(f"{service['name']:<25} Port {service['port']:<6} {status}")
    
    print("="*50)
    print(f"Total services online: {online_count}/{len(services)}")
    
    if online_count > 0:
        print("\n🌐 Available endpoints:")
        for service in services:
            if check_port(service["port"]) and "url" in service:
                print(f"   {service['name']}: {service['url']}")

if __name__ == "__main__":
    main()