#!/usr/bin/env python3
"""
DGM Integration Analysis Script
Converted from Jupyter notebook for easy execution
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path.cwd()
sys.path.append(str(project_root))

# Import and run notebook cells
async def run_dgm_analysis():
    print("🚀 Running DGM Integration Analysis...")
    print("=" * 80)
    
    # Cell 1: Import dependencies
    print("\n📦 Loading dependencies...")
    exec(open('dgm_analysis_imports.py').read()) if Path('dgm_analysis_imports.py').exists() else None
    
    # For this script, we'll run the key analysis functions
    print("\n🔍 Starting DGM Integration Analysis...")
    
    # Mock configuration for testing
    components = [
        {
            "name": "dgm_evolution_connector",
            "description": "DGM Evolution Learning System",
            "port": 8013,
            "status": "unknown"
        },
        {
            "name": "dgm_trading_algorithms",
            "description": "DGM Trading Algorithms",
            "port": 8014,
            "status": "unknown"
        },
        {
            "name": "a2a_protocol",
            "description": "Agent-to-Agent Communication",
            "port": 8001,
            "status": "unknown"
        }
    ]
    
    # Health checks
    print("\n🏥 Running Health Checks...")
    import socket
    health_results = []
    
    for component in components:
        print(f"\nChecking {component['name']}...")
        
        # Check port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', component['port']))
        sock.close()
        
        if result == 0:
            component['status'] = 'running'
            print(f"  ✅ Port {component['port']} is open")
        else:
            component['status'] = 'offline'
            print(f"  ❌ Port {component['port']} is closed")
        
        health_results.append(component)
    
    # A2A Testing
    print("\n🤖 Testing A2A Communication...")
    a2a_results = {
        'redis': {'success': False, 'error': 'Not tested'},
        'websocket': {'success': False, 'error': 'Not tested'},
        'overall': False
    }
    
    # Test Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, password='mcpvotsagi2025', socket_connect_timeout=2)
        r.ping()
        a2a_results['redis'] = {'success': True, 'message': 'Redis connected'}
        print("  ✅ Redis connectivity verified")
    except Exception as e:
        a2a_results['redis'] = {'success': False, 'error': str(e)}
        print(f"  ❌ Redis connection failed: {e}")
    
    # Generate Report
    print("\n📊 Generating Integration Report...")
    
    # Calculate scores
    healthy_components = sum(1 for c in health_results if c['status'] == 'running')
    health_score = (healthy_components / len(health_results)) * 100 if health_results else 0
    
    a2a_tests_passed = sum(1 for test in a2a_results.values() 
                          if isinstance(test, dict) and test.get('success', False))
    a2a_score = (a2a_tests_passed / 2) * 100  # 2 main tests
    
    overall_score = (health_score + a2a_score) / 2
    
    # Display results
    print("\n" + "=" * 80)
    print("🎯 DGM INTEGRATION ANALYSIS - RESULTS")
    print("=" * 80)
    
    print(f"\n📈 SCORES:")
    print(f"  Health Score: {health_score:.1f}%")
    print(f"  A2A Score: {a2a_score:.1f}%")
    print(f"  Overall Score: {overall_score:.1f}%")
    
    print(f"\n🔧 COMPONENT STATUS:")
    for component in health_results:
        status_icon = '✅' if component['status'] == 'running' else '❌'
        print(f"  {status_icon} {component['name']}: {component['status'].upper()}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if health_score < 50:
        print("  🔧 Start DGM services: python production_launcher_v2.py")
    if not a2a_results['redis']['success']:
        print("  📦 Ensure Redis is running: sudo service redis-server start")
    if overall_score >= 80:
        print("  ✅ System is ready for production use!")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'scores': {
            'health': health_score,
            'a2a': a2a_score,
            'overall': overall_score
        },
        'components': health_results,
        'a2a_results': a2a_results
    }
    
    report_file = f"DGM_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_file}")
    print("✅ Analysis complete!")

if __name__ == "__main__":
    asyncio.run(run_dgm_analysis())