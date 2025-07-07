#!/usr/bin/env python3
"""
Start the Ultimate AGI Backend System
"""

import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['PYTHONPATH'] = str(project_root)
os.environ['API_BASE_URL'] = 'http://localhost:8889'

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Ultimate AGI Backend...")
    print("=" * 60)
    
    # Check if ecosystem_core.py exists
    ecosystem_file = project_root / "ecosystem_core.py"
    if ecosystem_file.exists():
        print(f"✅ Found ecosystem_core.py at {ecosystem_file}")
        
        # Start the ecosystem core which handles everything
        cmd = [sys.executable, str(ecosystem_file)]
        print(f"📟 Running command: {' '.join(cmd)}")
        
        try:
            # Run the backend
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print("✅ Backend process started!")
            print("=" * 60)
            print("Backend logs:")
            print("-" * 60)
            
            # Stream output
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down backend...")
            process.terminate()
            process.wait()
            print("✅ Backend stopped")
            
    else:
        print(f"❌ ecosystem_core.py not found at {ecosystem_file}")
        
        # Try alternative startup scripts
        alternatives = [
            "LAUNCH_ULTIMATE_AGI_V3.py",
            "ecosystem_manager.py",
            "START_ULTIMATE_AGI.py"
        ]
        
        for alt in alternatives:
            alt_file = project_root / alt
            if alt_file.exists():
                print(f"✅ Found alternative: {alt_file}")
                cmd = [sys.executable, str(alt_file)]
                subprocess.run(cmd)
                break
        else:
            print("❌ No backend startup script found!")
            print("\nAvailable Python files:")
            for py_file in project_root.glob("*.py"):
                if "ecosystem" in py_file.name.lower() or "launch" in py_file.name.lower():
                    print(f"  - {py_file.name}")

if __name__ == "__main__":
    start_backend()