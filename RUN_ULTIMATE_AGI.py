#!/usr/bin/env python3
"""
Simple launcher for ULTIMATE AGI SYSTEM
Handles encoding issues on Windows
"""

import os
import sys
import subprocess

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import and run
from core.ULTIMATE_AGI_SYSTEM import main

if __name__ == "__main__":
    try:
        # Set console to UTF-8 on Windows
        if sys.platform == 'win32':
            subprocess.run('chcp 65001', shell=True, capture_output=True)
        
        print("Starting ULTIMATE AGI SYSTEM...")
        print("=" * 60)
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")