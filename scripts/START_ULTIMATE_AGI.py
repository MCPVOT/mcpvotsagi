#!/usr/bin/env python3
"""
START THE ULTIMATE AGI SYSTEM
=============================
🚀 Launch the ONE and ONLY consolidated AGI portal
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("""
🚀 ===================================================
   LAUNCHING ULTIMATE AGI SYSTEM
🚀 ===================================================

🔥 Consolidating ALL systems into ONE portal...
🧠 No more fragmented dashboards!
⚡ This is THE unified AGI system!
    """)

    # Change to the correct directory
    script_dir = Path(__file__).parent
    mcpvots_dir = script_dir  # We're already in MCPVotsAGI
    os.chdir(mcpvots_dir)

    print(f"📁 Working directory: {os.getcwd()}")

    try:
        # Run the ultimate AGI system
        print("\n🚀 Starting ULTIMATE AGI SYSTEM...")
        subprocess.run([sys.executable, "src/core/ULTIMATE_AGI_SYSTEM.py"])

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"💥 Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in the MCPVotsAGI directory")
        print("2. Check if Python dependencies are installed")
        print("3. Verify Ollama is running with DeepSeek-R1 model")

if __name__ == "__main__":
    main()
