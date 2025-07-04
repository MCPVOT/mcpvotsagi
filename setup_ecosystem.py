#!/usr/bin/env python3
"""
MCPVotsAGI Ecosystem Setup Script
================================
Properly sets up the entire ecosystem with all dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Failed!")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    return True

def setup_venv():
    """Setup virtual environment"""
    workspace = Path("C:/Workspace/MCPVotsAGI") if platform.system() == "Windows" else Path("/mnt/c/Workspace/MCPVotsAGI")
    venv_path = workspace / "venv"
    
    print("\n🐍 Setting up Python Virtual Environment...")
    
    # Check Python version
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    
    # Create venv
    if platform.system() == "Windows":
        cmd = f"{python_cmd} -m venv {venv_path}"
        activate_cmd = f"{venv_path}\\Scripts\\activate.bat"
        pip_cmd = f"{venv_path}\\Scripts\\pip.exe"
    else:
        # For WSL/Linux
        cmd = f"{python_cmd} -m venv {venv_path} --without-pip"
        activate_cmd = f"source {venv_path}/bin/activate"
        pip_cmd = f"{venv_path}/bin/pip"
        
        # First ensure pip for venv
        if not run_command(cmd, "Creating virtual environment"):
            return None, None
            
        # Get pip for the venv
        get_pip_cmd = f"curl https://bootstrap.pypa.io/get-pip.py | {venv_path}/bin/python"
        if not run_command(get_pip_cmd, "Installing pip in venv"):
            # Try alternative method
            alt_cmd = f"{venv_path}/bin/python -m ensurepip --upgrade"
            run_command(alt_cmd, "Installing pip (alternative method)")
    
    if platform.system() == "Windows" and not run_command(cmd, "Creating virtual environment"):
        return None, None
    
    return activate_cmd, pip_cmd

def install_dependencies(pip_cmd):
    """Install all dependencies"""
    workspace = Path("C:/Workspace/MCPVotsAGI") if platform.system() == "Windows" else Path("/mnt/c/Workspace/MCPVotsAGI")
    
    # First upgrade pip
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install core dependencies first (smaller packages)
    core_deps = [
        "aiohttp",
        "aiohttp-cors", 
        "websockets",
        "psutil",
        "requests",
        "aiofiles",
        "aiosqlite",
        "pyyaml",
        "python-dotenv",
        "click",
        "GitPython",
        "prometheus-client",
        "httpx"
    ]
    
    for dep in core_deps:
        run_command(f"{pip_cmd} install {dep}", f"Installing {dep}")
    
    # Install optional dependencies
    optional_deps = {
        "ipfshttpclient": "IPFS integration",
        "redis": "Redis cache support",
        "numpy": "Numerical computing"
    }
    
    for dep, desc in optional_deps.items():
        print(f"\n📦 Optional: {desc}")
        run_command(f"{pip_cmd} install {dep}", f"Installing {dep} ({desc})")
    
    # Windows-specific
    if platform.system() == "Windows":
        run_command(f"{pip_cmd} install pywin32", "Installing Windows service support")

def create_launch_scripts():
    """Create proper launch scripts"""
    workspace = Path("C:/Workspace/MCPVotsAGI") if platform.system() == "Windows" else Path("/mnt/c/Workspace/MCPVotsAGI")
    
    # Windows batch script
    if platform.system() == "Windows":
        batch_content = f'''@echo off
REM MCPVotsAGI Ecosystem Launcher with Virtual Environment

echo ===============================================
echo    MCPVotsAGI Ecosystem Launcher
echo ===============================================

REM Activate virtual environment
call "{workspace}\\venv\\Scripts\\activate.bat"

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;{workspace};C:\\Workspace\\MCPVots

REM Launch ecosystem manager
echo.
echo Starting Ecosystem Manager...
start "MCPVotsAGI Ecosystem" python "{workspace}\\ecosystem_manager.py" start

echo.
echo Ecosystem starting...
echo Dashboard will be available at: http://localhost:3010
echo.
pause
'''
        
        launch_path = workspace / "LAUNCH_WITH_VENV.bat"
        launch_path.write_text(batch_content)
        print(f"\n✅ Created: {launch_path}")
    
    # Linux/WSL script
    bash_content = f'''#!/bin/bash
# MCPVotsAGI Ecosystem Launcher with Virtual Environment

echo "==============================================="
echo "   MCPVotsAGI Ecosystem Launcher"
echo "==============================================="

# Activate virtual environment
source "{workspace}/venv/bin/activate"

# Set environment variables
export PYTHONPATH="$PYTHONPATH:{workspace}:/mnt/c/Workspace/MCPVots"

# Launch ecosystem manager
echo ""
echo "Starting Ecosystem Manager..."
python "{workspace}/ecosystem_manager.py" start
'''
    
    launch_sh = workspace / "launch_with_venv.sh"
    launch_sh.write_text(bash_content)
    launch_sh.chmod(0o755)
    print(f"✅ Created: {launch_sh}")

def main():
    print("🚀 MCPVotsAGI Ecosystem Setup")
    print("="*60)
    
    # Setup virtual environment
    activate_cmd, pip_cmd = setup_venv()
    
    if not pip_cmd:
        print("\n❌ Failed to setup virtual environment!")
        print("\nTroubleshooting:")
        if platform.system() != "Windows":
            print("1. Install python3-venv: sudo apt install python3-venv")
            print("2. Or use: python3 -m pip install --user virtualenv")
        return
    
    print(f"\n✅ Virtual environment created!")
    print(f"   Activation command: {activate_cmd}")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    install_dependencies(pip_cmd)
    
    # Create launch scripts
    print("\n📝 Creating launch scripts...")
    create_launch_scripts()
    
    # Final instructions
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    
    print("\n🚀 To launch the ecosystem:")
    
    if platform.system() == "Windows":
        print("\n   Option 1: Double-click LAUNCH_WITH_VENV.bat")
        print("\n   Option 2: From Command Prompt:")
        print("   cd C:\\Workspace\\MCPVotsAGI")
        print("   LAUNCH_WITH_VENV.bat")
    else:
        print("\n   From terminal:")
        print("   cd /mnt/c/Workspace/MCPVotsAGI")
        print("   ./launch_with_venv.sh")
    
    print("\n📊 Dashboard will be available at: http://localhost:3010")
    print("\n💡 For auto-start on boot:")
    print("   python ecosystem_manager.py install-service")

if __name__ == "__main__":
    main()