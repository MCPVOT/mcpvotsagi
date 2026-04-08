#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production System Status Checker
================================
Check real status of all MCPVotsAGI services
"""

import asyncio
import aiohttp
import socket
import psutil
from datetime import datetime
from pathlib import Path
import json
import sys
import io

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class ProductionStatusChecker:
    def __init__(self):
        self.services = {
            # Core Services
            'Oracle AGI Core': {'port': 8888, 'url': 'http://localhost:8888/oracle/status'},
            'Trilogy Oracle Brain': {'port': 8887, 'url': 'http://localhost:8887/health'},
            'DGM Voltagents': {'port': 8886, 'url': 'http://localhost:8886/dgm/status'},
            'Gemini CLI': {'port': 8080, 'url': 'http://localhost:8080/health'},
            'Memory Service': {'port': 8894, 'url': 'http://localhost:8894/health'},
            'Chat API': {'port': 8890, 'url': 'http://localhost:8890/health'},
            
            # Dashboard Services  
            'Unified Dashboard': {'port': 3002, 'url': 'http://localhost:3002/api/status'},
            'Enhanced Dashboard': {'port': 3001, 'url': 'http://localhost:3001/status'},
            'Claudia Integration': {'port': 3003, 'url': 'http://localhost:3003/claudia/oracle/status'},
            
            # MCP Servers
            'GitHub MCP': {'port': 3001, 'url': None},
            'Memory MCP': {'port': 3002, 'url': None},
            'Solana MCP': {'port': 3005, 'url': None},
            'Trilogy AGI Gateway': {'port': 8000, 'url': None},
        }
        
    def check_port(self, port):
        """Check if a port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
        
    async def check_health(self, url):
        """Check health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    return resp.status == 200
        except Exception:
            return False
            
    async def check_all_services(self):
        """Check all services"""
        print("="*80)
        print(f" PRODUCTION SYSTEM STATUS CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print()
        
        # System resources
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        print(f"System Resources:")
        print(f"  CPU Usage: {cpu}%")
        print(f"  Memory Usage: {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)")
        print()
        
        # Check services
        print("Service Status:")
        print("-" * 60)
        
        online_count = 0
        total_count = len(self.services)
        
        for name, config in self.services.items():
            port = config['port']
            url = config.get('url')
            
            # Check port
            port_open = self.check_port(port)
            
            # Check health endpoint if available
            health_ok = None
            if url and port_open:
                health_ok = await self.check_health(url)
                
            # Determine status
            if port_open and (health_ok is None or health_ok):
                status = "🟢 ONLINE"
                online_count += 1
            elif port_open and health_ok is False:
                status = "🟡 DEGRADED"
            else:
                status = "🔴 OFFLINE"
                
            # Print status
            print(f"{name:<25} Port {port:<5} {status}")
            
        print("-" * 60)
        print(f"Total: {online_count}/{total_count} services online")
        print()
        
        # Check for orphaned processes
        print("Checking for orphaned processes...")
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(x in cmdline for x in ['oracle', 'trilogy', 'dgm', 'mcp', 'claudia']):
                        python_processes.append(f"  PID {proc.info['pid']}: {cmdline[:80]}...")
            except Exception:
                pass
                
        if python_processes:
            print(f"Found {len(python_processes)} related Python processes:")
            for proc in python_processes[:10]:  # Show max 10
                print(proc)
        else:
            print("  No orphaned processes found")
            
        print()
        
        # Check log files
        log_path = Path("C:/Workspace/MCPVots/logs")
        if log_path.exists():
            print("Recent log activity:")
            logs = sorted(log_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            for log in logs[:5]:
                mtime = datetime.fromtimestamp(log.stat().st_mtime)
                size = log.stat().st_size / 1024  # KB
                print(f"  {log.name:<30} {size:>8.1f} KB  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print()
        print("="*80)
        
        # Recommendations
        if online_count < total_count / 2:
            print("⚠️  WARNING: Many services are offline!")
            print("   Run START_PRODUCTION.bat to start all services")
        elif online_count < total_count:
            print("ℹ️  Some services are offline.")
            print("   Check individual service logs for errors")
        else:
            print("✅ All services are online!")
            
        return online_count, total_count

async def main():
    checker = ProductionStatusChecker()
    await checker.check_all_services()

if __name__ == "__main__":
    asyncio.run(main())