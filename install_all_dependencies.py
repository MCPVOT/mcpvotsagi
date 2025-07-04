#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install ALL Dependencies for MCPVotsAGI Production System
=========================================================
Ensures all required packages are installed from all requirements files
"""

import subprocess
import sys
import os
from pathlib import Path
import json
import io

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def install_dependencies():
    """Install all dependencies from all requirements files"""
    
    print("="*80)
    print(" MCPVotsAGI DEPENDENCY INSTALLER")
    print("="*80)
    print()
    
    # Set paths
    workspace = Path("C:/Workspace") if sys.platform == "win32" else Path("/mnt/c/Workspace")
    mcpvots = workspace / "MCPVots"
    mcpvots_agi = workspace / "MCPVotsAGI"
    
    # Find all requirements files
    requirements_files = [
        mcpvots / "requirements.txt",
        mcpvots / "requirements_windows.txt",
        mcpvots / "requirements_yfinance_integration.txt",
        mcpvots / "requirements_memory_system.txt",
        mcpvots / "requirements_ml_analysis.txt",
        mcpvots / "requirements-2025.txt"
    ]
    
    # Core packages that must be installed
    core_packages = [
        "aiohttp",
        "asyncio",
        "psutil",
        "requests",
        "websockets",
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "sqlite3",
        "numpy",
        "pandas",
        "torch",
        "transformers",
        "ccxt",
        "yfinance",
        "plotly",
        "networkx",
        "scikit-learn",
        "python-dotenv",
        "colorama",
        "rich",
        "typer",
        "click",
        "httpx",
        "python-multipart",
        "aiofiles",
        "cryptography",
        "pyjwt",
        "redis",
        "celery",
        "flower",
        "prometheus-client",
        "py-solana-fork",
        "base58",
        "borsh-construct",
        "construct-typing"
    ]
    
    # Upgrade pip first
    print("Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], capture_output=True)
    
    # Install core packages
    print("\nInstalling core packages...")
    failed_packages = []
    
    for package in core_packages:
        print(f"Installing {package}...", end=" ")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓")
        else:
            print("✗")
            failed_packages.append(package)
            
    # Install from requirements files
    print("\nInstalling from requirements files...")
    for req_file in requirements_files:
        if req_file.exists():
            print(f"\nProcessing {req_file.name}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ Successfully installed from {req_file.name}")
            else:
                print(f"✗ Some packages failed from {req_file.name}")
                print(f"  Error: {result.stderr[:200]}")
        else:
            print(f"⚠ File not found: {req_file}")
            
    # Special cases for Windows
    if sys.platform == "win32":
        print("\nInstalling Windows-specific packages...")
        windows_packages = ["pywin32", "windows-curses"]
        for package in windows_packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package], capture_output=True)
            
    # Install Ollama Python client if needed
    print("\nInstalling Ollama client...")
    subprocess.run([sys.executable, "-m", "pip", "install", "ollama"], capture_output=True)
    
    # Report results
    print("\n" + "="*80)
    print(" INSTALLATION SUMMARY")
    print("="*80)
    
    if failed_packages:
        print(f"\n⚠ Failed to install: {', '.join(failed_packages)}")
        print("\nThese packages may require:")
        print("  - Visual C++ Build Tools (for Windows)")
        print("  - Specific Python versions")
        print("  - Manual installation")
    else:
        print("\n✓ All core packages installed successfully!")
        
    # Check installed packages
    print("\nVerifying key packages...")
    check_packages = ["aiohttp", "fastapi", "torch", "transformers", "ccxt", "yfinance"]
    
    for package in check_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is NOT available")
            
    print("\nDependency installation complete!")
    
if __name__ == "__main__":
    install_dependencies()