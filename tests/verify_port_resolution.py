#!/usr/bin/env python3
"""
Port Resolution Verification Script
Verifies all port assignments and resolves conflicts for A2A communication
"""

import asyncio
import socket
import logging
from typing import Optional
import json
import aiohttp
import websockets
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortManager:
    """Manages port allocation and verification"""

    def __init__(self):
        self.port_registry = {
            # Core services
            8000: "Unified AGI Portal",
            8001: "A2A WebSocket Server (Primary)",
            8002: "Memory/RL Service",
            8003: "DeepSeek MCP Server",
            8004: "Trading Backend",
            8005: "File Operations",
            8006: "GitHub Integration",
            8007: "Browser Automation",
            8008: "Blockchain/Solana",

            # Dashboard services
            8888: "Legacy Dashboard",
            8889: "Enhanced Dashboard",

            # MCP Servers
            3000: "MCP FileSystem",
            3001: "MCP GitHub",
            3002: "MCP Memory",
            3003: "MCP Browser",
            3004: "MCP Search",
            3005: "MCP Solana",
            3006: "MCP HuggingFace",
            3007: "OpenCTI MCP",

            # Specialized services
            11434: "Ollama API",
            5000: "Flask Services",

            # A2A Enhanced ports
            8100: "A2A Message Queue (Redis)",
            8101: "A2A Agent Registry",
            8102: "A2A Protocol Gateway",
            8103: "A2A Discovery Service"
        }

        self.conflicts = []
        self.available_ports = []

    def check_port(self, port: int) -> bool:
        """Check if port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # Port is available if connection fails
        except Exception:
            return True

    def verify_all_ports(self) -> dict:
        """Verify all registered ports"""
        results = {}

        for port, service in self.port_registry.items():
            is_available = self.check_port(port)
            results[port] = {
                'service': service,
                'available': is_available,
                'status': 'Available' if is_available else 'In Use'
            }

            if not is_available:
                self.conflicts.append((port, service))
            else:
                self.available_ports.append(port)

        return results

    def suggest_alternatives(self) -> dict:
        """Suggest alternative ports for conflicts"""
        alternatives = {}
        start_port = 9000

        for port, service in self.conflicts:
            # Find next available port
            while not self.check_port(start_port):
                start_port += 1
            alternatives[port] = {
                'service': service,
                'suggested_port': start_port,
                'reason': f'Original port {port} in use'
            }
            start_port += 1

        return alternatives

class A2ASystemVerifier:
    """Verifies A2A communication system status"""

    def __init__(self):
        self.endpoints = {
            'unified_portal': 'http://localhost:8000',
            'a2a_websocket': 'ws://localhost:8001',
            'memory_service': 'http://localhost:8002',
            'deepseek_mcp': 'ws://localhost:8003',
        }

    async def check_http_endpoint(self, name: str, url: str) -> dict:
        """Check HTTP endpoint health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=5) as response:
                    return {
                        'name': name,
                        'url': url,
                        'status': 'online',
                        'status_code': response.status,
                        'response_time': 0.1
                    }
        except Exception as e:
            return {
                'name': name,
                'url': url,
                'status': 'offline',
                'error': str(e)
            }

    async def check_websocket_endpoint(self, name: str, url: str) -> dict:
        """Check WebSocket endpoint health"""
        try:
            async with websockets.connect(url, timeout=5) as ws:
                await ws.send(json.dumps({'type': 'ping'}))
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                return {
                    'name': name,
                    'url': url,
                    'status': 'online',
                    'response': response
                }
        except Exception as e:
            return {
                'name': name,
                'url': url,
                'status': 'offline',
                'error': str(e)
            }

    async def verify_a2a_system(self) -> dict:
        """Verify complete A2A system"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'http_services': [],
            'websocket_services': [],
            'overall_status': 'unknown'
        }

        # Check HTTP endpoints
        for name, url in self.endpoints.items():
            if url.startswith('http'):
                result = await self.check_http_endpoint(name, url)
                results['http_services'].append(result)

        # Check WebSocket endpoints
        for name, url in self.endpoints.items():
            if url.startswith('ws'):
                result = await self.check_websocket_endpoint(name, url)
                results['websocket_services'].append(result)

        # Calculate overall status
        all_services = results['http_services'] + results['websocket_services']
        online_count = sum(1 for s in all_services if s['status'] == 'online')
        total_count = len(all_services)

        if online_count == total_count:
            results['overall_status'] = 'fully_operational'
        elif online_count > 0:
            results['overall_status'] = 'partially_operational'
        else:
            results['overall_status'] = 'offline'

        results['online_services'] = online_count
        results['total_services'] = total_count

        return results

def print_port_report(port_results: Dict, alternatives: Dict):
    """Print formatted port verification report"""
    print("\n" + "="*80)
    print("🔍 PORT VERIFICATION REPORT")
    print("="*80)

    print(f"\n📊 PORT STATUS SUMMARY:")
    available_count = sum(1 for r in port_results.values() if r['available'])
    total_count = len(port_results)
    print(f"   Available: {available_count}/{total_count} ports")
    print(f"   Conflicts: {total_count - available_count} ports")

    print(f"\n✅ AVAILABLE PORTS:")
    for port, info in port_results.items():
        if info['available']:
            print(f"   Port {port:5}: {info['service']}")

    print(f"\n❌ CONFLICTED PORTS:")
    for port, info in port_results.items():
        if not info['available']:
            print(f"   Port {port:5}: {info['service']} (IN USE)")

    if alternatives:
        print(f"\n💡 SUGGESTED ALTERNATIVES:")
        for original_port, alt_info in alternatives.items():
            print(f"   {alt_info['service']}: {original_port} → {alt_info['suggested_port']}")

async def print_a2a_report(a2a_results: Dict):
    """Print formatted A2A system report"""
    print("\n" + "="*80)
    print("🤖 A2A COMMUNICATION SYSTEM STATUS")
    print("="*80)

    status_emoji = {
        'fully_operational': '🟢',
        'partially_operational': '🟡',
        'offline': '🔴'
    }

    print(f"\n{status_emoji.get(a2a_results['overall_status'], '⚪')} OVERALL STATUS: {a2a_results['overall_status'].upper()}")
    print(f"   Online Services: {a2a_results['online_services']}/{a2a_results['total_services']}")

    print(f"\n🌐 HTTP SERVICES:")
    for service in a2a_results['http_services']:
        status_icon = '✅' if service['status'] == 'online' else '❌'
        print(f"   {status_icon} {service['name']}: {service['url']}")
        if service['status'] == 'offline':
            print(f"      Error: {service.get('error', 'Unknown')}")

    print(f"\n🔌 WEBSOCKET SERVICES:")
    for service in a2a_results['websocket_services']:
        status_icon = '✅' if service['status'] == 'online' else '❌'
        print(f"   {status_icon} {service['name']}: {service['url']}")
        if service['status'] == 'offline':
            print(f"      Error: {service.get('error', 'Unknown')}")

def generate_config_recommendations(port_results: Dict, alternatives: Dict) -> str:
    """Generate configuration recommendations"""
    config = {
        'port_assignments': {},
        'conflict_resolutions': {},
        'startup_order': [],
        'environment_variables': {}
    }

    # Assign ports based on availability
    for port, info in port_results.items():
        if info['available']:
            config['port_assignments'][info['service']] = port
        elif port in alternatives:
            alt_info = alternatives[port]
            config['conflict_resolutions'][info['service']] = {
                'original_port': port,
                'new_port': alt_info['suggested_port']
            }
            config['port_assignments'][info['service']] = alt_info['suggested_port']

    # Define startup order for dependencies
    config['startup_order'] = [
        'Ollama API',
        'A2A Message Queue (Redis)',
        'A2A Agent Registry',
        'Memory/RL Service',
        'DeepSeek MCP Server',
        'Unified AGI Portal',
        'A2A WebSocket Server (Primary)'
    ]

    # Environment variables
    config['environment_variables'] = {
        'AGI_PORTAL_PORT': config['port_assignments'].get('Unified AGI Portal', 8000),
        'A2A_WEBSOCKET_PORT': config['port_assignments'].get('A2A WebSocket Server (Primary)', 8001),
        'MEMORY_SERVICE_PORT': config['port_assignments'].get('Memory/RL Service', 8002),
        'DEEPSEEK_MCP_PORT': config['port_assignments'].get('DeepSeek MCP Server', 8003)
    }

    return json.dumps(config, indent=2)

async def main():
    """Main verification function"""
    print("🚀 Starting MCPVotsAGI Port and A2A System Verification...")

    # Initialize managers
    port_manager = PortManager()
    a2a_verifier = A2ASystemVerifier()

    # Verify ports
    print("\n🔍 Checking port availability...")
    port_results = port_manager.verify_all_ports()
    alternatives = port_manager.suggest_alternatives()

    # Verify A2A system
    print("\n🤖 Verifying A2A communication system...")
    a2a_results = await a2a_verifier.verify_a2a_system()

    # Print reports
    print_port_report(port_results, alternatives)
    await print_a2a_report(a2a_results)

    # Generate configuration
    print("\n" + "="*80)
    print("⚙️  CONFIGURATION RECOMMENDATIONS")
    print("="*80)

    config_json = generate_config_recommendations(port_results, alternatives)

    # Save configuration
    config_file = "port_resolution_config.json"
    with open(config_file, 'w') as f:
        f.write(config_json)

    print(f"\n📄 Configuration saved to: {config_file}")
    print("\n💡 NEXT STEPS:")
    print("   1. Review port conflicts and apply suggested changes")
    print("   2. Start services in recommended order")
    print("   3. Run A2A communication tests")
    print("   4. Deploy enhanced A2A protocol features")

    # Summary
    total_conflicts = len(alternatives)
    if total_conflicts == 0:
        print(f"\n🎉 SUCCESS: No port conflicts detected!")
    else:
        print(f"\n⚠️  WARNING: {total_conflicts} port conflicts need resolution")

    return {
        'port_results': port_results,
        'a2a_results': a2a_results,
        'alternatives': alternatives,
        'config': json.loads(config_json)
    }

if __name__ == "__main__":
    # Run the verification
    results = asyncio.run(main())

    # Exit with appropriate code
    conflicts = len(results['alternatives'])
    a2a_operational = results['a2a_results']['overall_status'] != 'offline'

    if conflicts == 0 and a2a_operational:
        exit(0)  # Success
    elif conflicts > 0 and a2a_operational:
        exit(1)  # Warnings
    else:
        exit(2)  # Errors
