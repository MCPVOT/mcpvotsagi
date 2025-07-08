#!/usr/bin/env python3
"""
ULTIMATE AGI SYSTEM V3 - Enhanced Launcher
==========================================
Launches the complete ULTIMATE AGI SYSTEM V3 with integrated UI components
from cloned repositories (animate-ui, next-shadcn-dashboard-starter, icons)
"""

import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path

async def main():
    """Launch ULTIMATE AGI SYSTEM V3 with enhanced UI integration"""

    print("""
    ╔══════════════════════════════════════════════════════════════════════════════════════╗
    ║                    ULTIMATE AGI SYSTEM V3 - ENHANCED LAUNCHER                       ║
    ║                                                                                      ║
    ║  🎨 Integrated UI Components from Cloned Repositories:                              ║
    ║     • animate-ui: Modern animations and effects                                     ║
    ║     • next-shadcn-dashboard-starter: Professional dashboard components              ║
    ║     • icons: Comprehensive icon library                                             ║
    ║                                                                                      ║
    ║  🚀 Enhanced Features:                                                               ║
    ║     • Real-time UI component serving                                                ║
    ║     • Dynamic component catalog                                                     ║
    ║     • Integrated frontend generation                                                ║
    ║     • Advanced dashboard with animations                                            ║
    ╚══════════════════════════════════════════════════════════════════════════════════════╝
    """)

    # Check if frontend integration is needed
    workspace_root = Path(__file__).parent
    frontend_dir = workspace_root / "frontend"

    if not frontend_dir.exists() or not (frontend_dir / "package.json").exists():
        print("🔧 Frontend not found. Creating integrated frontend...")
        try:
            subprocess.run([sys.executable, "CREATE_INTEGRATED_FRONTEND.py"], check=True)
            print("✅ Integrated frontend created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create frontend: {e}")
            print("⚠️ Continuing with backend only...")

    # Import and run the enhanced system
    try:
        from src.core.ULTIMATE_AGI_SYSTEM_V3 import main as run_agi_system

        print("🚀 Starting ULTIMATE AGI SYSTEM V3 with UI integration...")
        print("📊 Components will be served from cloned repositories")
        print("🎨 UI catalog available at: http://localhost:8889/api/v3/ui/catalog")
        print("🔗 Component API: http://localhost:8889/api/v3/ui/component/{library}/{component}")
        print("🎯 Icons API: http://localhost:8889/api/v3/ui/icons")

        await run_agi_system()

    except ImportError as e:
        print(f"❌ Failed to import ULTIMATE AGI SYSTEM V3: {e}")
        print("⚠️ Make sure the system is properly installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 ULTIMATE AGI SYSTEM V3 Enhanced Launcher Shutdown Complete!")
    except Exception as e:
        print(f"❌ Launcher Error: {e}")
        import traceback
        traceback.print_exc()
