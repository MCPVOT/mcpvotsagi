#!/usr/bin/env python3
"""
Direct Oracle V9 Launcher
========================
Simple launcher that starts Oracle AGI V9 directly
"""

import subprocess
import sys
import os
from pathlib import Path

# Set working directory
os.chdir("C:/Workspace/MCPVotsAGI")

# Add to path
sys.path.insert(0, str(Path.cwd()))

# Import and run directly
try:
    print("🚀 Starting Oracle AGI V9 Complete...")
    print("=" * 70)
    
    # Check if Ollama is running
    import requests
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            print("✅ Ollama service is running")
        else:
            print("⚠️  Ollama service may not be running properly")
    except:
        print("❌ Ollama service not running - starting it...")
        subprocess.Popen(['ollama', 'serve'], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
        import time
        time.sleep(3)
    
    # Import and run Oracle V9
    from src.core.oracle_agi_v9_complete_mcp import OracleAGIV9CompleteMCP
    import asyncio
    
    oracle = OracleAGIV9CompleteMCP()
    asyncio.run(oracle.start())
    
except KeyboardInterrupt:
    print("\n\n✋ Shutting down Oracle AGI V9...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")