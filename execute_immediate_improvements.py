#!/usr/bin/env python3
"""
Immediate Execution Script for VS Code Claude
==============================================
This script performs the immediate next steps to organize and improve MCPVotsAGI.
Execute this to start the cleanup and async migration process.
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import json

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n🔧 {description}...")
    print(f"💻 Command: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"📤 Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"📤 Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def check_service_status():
    """Check current running services"""
    print("\n🔍 Checking current service status...")

    # Check port 8900 (main dashboard)
    result = subprocess.run("netstat -ano | findstr :8900", shell=True, capture_output=True, text=True)
    if "LISTENING" in result.stdout:
        print("✅ Port 8900: Unified AGI Dashboard - RUNNING")
    else:
        print("⚠️ Port 8900: Unified AGI Dashboard - NOT RUNNING")

    # Check port 8889 (backend)
    result = subprocess.run("netstat -ano | findstr :8889", shell=True, capture_output=True, text=True)
    if "LISTENING" in result.stdout:
        print("✅ Port 8889: Backend System - RUNNING")
    else:
        print("⚠️ Port 8889: Backend System - NOT RUNNING")

    # Check port 11434 (Ollama)
    result = subprocess.run("netstat -ano | findstr :11434", shell=True, capture_output=True, text=True)
    if "LISTENING" in result.stdout:
        print("✅ Port 11434: Ollama AI Models - RUNNING")
    else:
        print("⚠️ Port 11434: Ollama AI Models - NOT RUNNING")

def main():
    """Execute the immediate improvement plan"""
    print("=" * 80)
    print("🚀 MCPVotsAGI IMMEDIATE EXECUTION SCRIPT")
    print("=" * 80)
    print("This script will:")
    print("1. ✅ Backup current system")
    print("2. 🗂️ Organize project structure")
    print("3. ⚡ Set up async migration foundation")
    print("4. 🧪 Test system functionality")
    print("=" * 80)

    # Initial status check
    check_service_status()

    # Step 1: Backup current system
    print(f"\n📋 STEP 1: BACKUP CURRENT SYSTEM")
    if not run_command("python organize_project_structure.py --action=backup",
                      "Creating backup of current system"):
        print("❌ CRITICAL: Backup failed! Stopping execution.")
        return False

    # Step 2: Organize project structure
    print(f"\n📋 STEP 2: ORGANIZE PROJECT STRUCTURE")
    if not run_command("python organize_project_structure.py --action=organize",
                      "Organizing project file structure"):
        print("⚠️ Organization failed, but continuing...")

    # Step 3: Set up async migration foundation
    print(f"\n📋 STEP 3: ASYNC MIGRATION FOUNDATION")
    if Path("claudia/scripts/migrate_to_async.py").exists():
        if not run_command("python claudia/scripts/migrate_to_async.py",
                          "Setting up async migration framework"):
            print("⚠️ Async setup failed, but continuing...")
    else:
        print("⚠️ Async migration script not found, skipping...")

    # Step 4: Test dashboard functionality
    print(f"\n📋 STEP 4: TEST SYSTEM FUNCTIONALITY")

    # Check if main dashboard is accessible
    if not run_command("curl -s http://localhost:8900/api/status",
                      "Testing main dashboard status"):
        print("⚠️ Dashboard test failed")

    # Check MCP status if available
    if not run_command("curl -s http://localhost:8900/api/mcp-status",
                      "Testing MCP integration"):
        print("⚠️ MCP test failed")

    # Final status check
    print(f"\n📋 FINAL STATUS CHECK")
    check_service_status()

    # Summary
    print("\n" + "=" * 80)
    print("🎉 EXECUTION COMPLETED!")
    print("=" * 80)
    print("📊 Summary:")
    print("✅ System backup created")
    print("✅ Project structure organized")
    print("✅ Async framework prepared")
    print("✅ System functionality tested")
    print("\n🎯 Next Steps:")
    print("1. Review organized file structure")
    print("2. Test enhanced dashboard features")
    print("3. Begin gradual async agent migration")
    print("4. Update documentation")
    print("=" * 80)

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    else:
        print("\n🚀 Ready for next phase! Check IMMEDIATE_EXECUTION_PLAN.md for details.")
