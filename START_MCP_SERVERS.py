#!/usr/bin/env python3
"""
Start All MCP Servers
====================
"""

import subprocess
import time
import sys
from pathlib import Path

def start_mcp_server(command, name, port=None):
    """Start an MCP server"""
    print(f"Starting {name}...")
    try:
        if port:
            full_command = f"{command} --port {port}"
        else:
            full_command = command

        proc = subprocess.Popen(full_command, shell=True)
        print(f"   Started {name} (PID: {proc.pid})")
        return proc
    except Exception as e:
        print(f"   Failed to start {name}: {e}")
        return None

def main():
    print("Starting All MCP Servers...")
    print("=" * 40)

    servers = [
        ("npx @modelcontextprotocol/server-filesystem", "FileSystem", 3000),
        ("npx @modelcontextprotocol/server-github", "GitHub", 3001),
        ("npx @modelcontextprotocol/server-memory", "Memory", 3002),
        ("npx @modelcontextprotocol/server-brave-search", "Search", 3003),
        ("npx @agentdeskai/browser-tools-mcp", "Browser", 3006),
    ]

    processes = []
    for command, name, port in servers:
        proc = start_mcp_server(command, name, port)
        if proc:
            processes.append((proc, name))
        time.sleep(2)  # Wait between starts

    print(f"Started {len(processes)} MCP servers")
    print("Keep this window open to maintain the servers")
    print("Press Ctrl+C to stop all servers")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all MCP servers...")
        for proc, name in processes:
            try:
                proc.terminate()
                print(f"   Stopped {name}")
            except:
                pass
        print("All servers stopped.")

if __name__ == "__main__":
    main()
