#!/usr/bin/env python3
"""
Setup and Run Oracle AGI V5
===========================
Handles dependencies and starts the system
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a package using the appropriate method"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except:
        try:
            # Try with apt-get for WSL/Linux
            subprocess.check_call(["sudo", "apt-get", "install", "-y", f"python3-{package}"])
            return True
        except:
            return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    print("🔍 Checking dependencies...")
    
    required_packages = {
        'aiohttp': 'aiohttp',
        'websockets': 'websockets',
        'psutil': 'psutil',
        'requests': 'requests',
        'aiofiles': 'aiofiles'
    }
    
    missing_packages = []
    
    for package_name, install_name in required_packages.items():
        try:
            __import__(package_name)
            print(f"✓ {package_name} installed")
        except ImportError:
            print(f"✗ {package_name} missing")
            missing_packages.append(install_name)
    
    if missing_packages:
        print("\n📦 Installing missing packages...")
        
        # First try to ensure pip is installed
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip"])
        except:
            print("⚠️  Could not ensure pip is installed")
        
        for package in missing_packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✓ {package} installed successfully")
            else:
                print(f"✗ Failed to install {package}")
                print(f"Please install manually: pip install {package}")
                return False
    
    return True

def start_oracle_agi():
    """Start the Oracle AGI V5 system"""
    print("\n🚀 Starting Oracle AGI V5...")
    
    oracle_script = Path(__file__).parent / "oracle_agi_v5_complete.py"
    
    if not oracle_script.exists():
        print("❌ oracle_agi_v5_complete.py not found!")
        return
    
    try:
        subprocess.run([sys.executable, str(oracle_script)])
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("🔮 Oracle AGI V5 - Setup and Run")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version}")
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("\n❌ Failed to install dependencies")
        print("Please install manually:")
        print("  pip install aiohttp websockets psutil requests aiofiles")
        sys.exit(1)
    
    # Start the system
    start_oracle_agi()

if __name__ == "__main__":
    main()