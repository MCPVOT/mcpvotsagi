#!/usr/bin/env python3
"""
ULTIMATE AGI SYSTEM V3 LAUNCHER
===============================
🚀 Production launcher for the complete ULTIMATE AGI SYSTEM V3
🧠 Ensures all dependencies and integrations are properly configured
"""

import os
import sys
import subprocess
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check and install required dependencies"""
    logger.info("🔍 Checking dependencies...")

    required_packages = [
        'aiohttp',
        'requests',
        'websockets',
        'sqlite3',
        'pathlib'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"  ❌ {package} - missing")

    if missing_packages:
        logger.info(f"📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages, check=True)
            logger.info("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False

    return True

def check_system_requirements():
    """Check system requirements and configuration"""
    logger.info("🔧 Checking system requirements...")

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required")
        return False
    logger.info(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check current directory
    current_dir = Path.cwd()
    logger.info(f"  📁 Working directory: {current_dir}")

    # Check for required files
    required_files = [
        'src/core/ULTIMATE_AGI_SYSTEM_V3.py',
        'src/core/claudia_integration_bridge.py'
    ]

    for file_path in required_files:
        if (current_dir / file_path).exists():
            logger.info(f"  ✅ {file_path}")
        else:
            logger.warning(f"  ⚠️ {file_path} - not found")

    return True

def check_claudia_setup():
    """Check Claudia setup and configuration"""
    logger.info("🧠 Checking Claudia setup...")

    claudia_path = Path.cwd() / "claudia"
    if claudia_path.exists():
        logger.info(f"  ✅ Claudia found at: {claudia_path}")

        # Check package.json
        package_json = claudia_path / "package.json"
        if package_json.exists():
            logger.info("  ✅ package.json found")
        else:
            logger.warning("  ⚠️ package.json not found")

        # Check node_modules
        node_modules = claudia_path / "node_modules"
        if node_modules.exists():
            logger.info("  ✅ node_modules found")
        else:
            logger.warning("  ⚠️ node_modules not found - will install")

        return True
    else:
        logger.warning(f"  ⚠️ Claudia not found at: {claudia_path}")
        return False

def setup_environment():
    """Setup environment variables"""
    logger.info("🌍 Setting up environment...")

    # Set environment variables
    env_vars = {
        'AGI_PORT': '8889',
        'CLAUDIA_AGI_INTEGRATION': 'true',
        'CLAUDIA_AGI_PORT': '8889',
        'CLAUDIA_AGI_HOST': 'localhost',
        'NODE_ENV': 'development'
    }

    for key, value in env_vars.items():
        os.environ[key] = value
        logger.info(f"  ✅ {key}={value}")

    return True

async def main():
    """Main launcher function"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════════════╗
    ║                        ULTIMATE AGI SYSTEM V3 LAUNCHER                              ║
    ║                                                                                      ║
    ║  🚀 Production-Ready AGI Portal with Complete Claudia Integration                   ║
    ║  🧠 Advanced Multi-Model Orchestration & Real-Time Dashboard                        ║
    ║  📊 1M Token Context Management & Continuous Learning Engine                        ║
    ║  🎨 Cyberpunk UI/UX with WebSocket-Powered Live Updates                             ║
    ╚══════════════════════════════════════════════════════════════════════════════════════╝
    """)

    # Check system requirements
    if not check_system_requirements():
        logger.error("❌ System requirements not met")
        return

    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        return

    # Check Claudia setup
    check_claudia_setup()

    # Setup environment
    if not setup_environment():
        logger.error("❌ Environment setup failed")
        return

    # Add src directory to path
    src_path = Path.cwd() / "src"
    if src_path not in sys.path:
        sys.path.insert(0, str(src_path))

    logger.info("🚀 Starting ULTIMATE AGI SYSTEM V3...")

    try:
        # Import and run the V3 system
        from core.ULTIMATE_AGI_SYSTEM_V3 import main as v3_main
        await v3_main()
    except ImportError as e:
        logger.error(f"❌ Failed to import V3 system: {e}")
        logger.info("🔄 Trying alternative import...")

        # Try alternative import
        try:
            sys.path.insert(0, str(Path.cwd() / "src" / "core"))
            from ULTIMATE_AGI_SYSTEM_V3 import main as v3_main
            await v3_main()
        except ImportError as e:
            logger.error(f"❌ Alternative import also failed: {e}")
            logger.info("📝 Please check that ULTIMATE_AGI_SYSTEM_V3.py exists in src/core/")
    except Exception as e:
        logger.error(f"❌ V3 system error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        import traceback
        traceback.print_exc()
