#!/usr/bin/env python3
"""
A2A Enhanced Communication System Launcher
Starts the enhanced A2A system with all components
"""

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class A2ASystemLauncher:
    """Launches and manages the A2A system components"""

    def __init__(self):
        self.workspace = Path("C:/Workspace/MCPVotsAGI")
        self.services = {}

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        required_packages = [
            'websockets',
            'aiohttp',
            'redis',
            'aioredis'
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
            logger.info("📦 Install with: pip install " + " ".join(missing_packages))
            return False

        return True

    def start_redis(self) -> bool:
        """Start Redis server if not running"""
        try:
            # Check if Redis is already running
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            logger.info("✅ Redis is already running")
            return True
        except Exception:
            logger.info("🚀 Starting Redis server...")
            try:
                # Try to start Redis (Windows)
                subprocess.Popen([
                    'redis-server',
                    '--port', '6379',
                    '--save', '900', '1'
                ], shell=True)

                # Wait for Redis to start
                time.sleep(3)

                # Verify Redis is running
                import redis
                r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                r.ping()
                logger.info("✅ Redis started successfully")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to start Redis: {e}")
                logger.info("💡 Please install Redis manually:")
                logger.info("   Windows: Download from https://redis.io/download")
                logger.info("   Or use Docker: docker run -p 6379:6379 redis")
                return False

    async def start_a2a_gateway(self):
        """Start the A2A Protocol Gateway"""
        try:
            # Import and start the gateway
            sys.path.append(str(self.workspace))
            from core.a2a_enhanced_protocol import A2AProtocolGateway

            gateway = A2AProtocolGateway(port=8001)
            logger.info("🚀 Starting A2A Protocol Gateway...")

            await gateway.start_server()

        except Exception as e:
            logger.error(f"❌ Failed to start A2A gateway: {e}")
            raise

    async def start_unified_portal(self):
        """Start the Unified AGI Portal"""
        try:
            from src.core.unified_agi_portal import UnifiedAGIPortal

            portal = UnifiedAGIPortal()
            logger.info("🌟 Starting Unified AGI Portal...")

            # Start on port 8000
            await portal.run_server(port=8000)

        except Exception as e:
            logger.error(f"❌ Failed to start Unified Portal: {e}")
            # Continue with other services

    def start_ollama(self) -> bool:
        """Start Ollama if not running"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama is already running")
                return True
        except Exception:
            pass

        try:
            logger.info("🚀 Starting Ollama...")
            subprocess.Popen(['ollama', 'serve'], shell=True)
            time.sleep(5)

            # Verify Ollama is running
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Ollama started successfully")
                return True
            else:
                logger.warning("⚠️ Ollama may not be fully ready")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to start Ollama: {e}")
            logger.info("💡 Please install Ollama from https://ollama.ai")
            return False

    def run_port_verification(self) -> bool:
        """Run port verification"""
        try:
            logger.info("🔍 Running port verification...")
            result = subprocess.run([
                sys.executable,
                str(self.workspace / "verify_port_resolution.py")
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info("✅ Port verification completed successfully")
                return True
            elif result.returncode == 1:
                logger.warning("⚠️ Port verification completed with warnings")
                logger.info(result.stdout)
                return True
            else:
                logger.error("❌ Port verification failed")
                logger.error(result.stderr)
                return False

        except Exception as e:
            logger.error(f"❌ Port verification error: {e}")
            return False

    async def launch_system(self):
        """Launch the complete A2A system"""
        logger.info("🚀 Starting Enhanced A2A Communication System...")

        # 1. Check dependencies
        if not self.check_dependencies():
            logger.error("❌ Please install missing dependencies first")
            return False

        # 2. Run port verification
        if not self.run_port_verification():
            logger.warning("⚠️ Port verification issues detected - continuing anyway")

        # 3. Start Redis
        if not self.start_redis():
            logger.error("❌ Redis is required for A2A message queue")
            return False

        # 4. Start Ollama
        if not self.start_ollama():
            logger.warning("⚠️ Ollama not available - some features may be limited")

        # 5. Start services concurrently
        try:
            await asyncio.gather(
                self.start_a2a_gateway(),
                self.start_unified_portal(),
                return_exceptions=True
            )
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down A2A system...")
        except Exception as e:
            logger.error(f"❌ System launch error: {e}")
            return False

        return True

async def main():
    """Main launcher function"""
    launcher = A2ASystemLauncher()

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🤖 Enhanced A2A Communication System 🤖                   ║
║                                                                              ║
║  🔗 Agent-to-Agent Communication with Advanced Features:                    ║
║     • Redis Message Queue for Reliability                                   ║
║     • Agent Discovery and Registry                                          ║
║     • Enhanced Protocol with Fault Tolerance                               ║
║     • WebSocket-based Real-time Communication                              ║
║     • Automatic Agent Health Monitoring                                    ║
║                                                                              ║
║  🚀 Starting all services...                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        success = await launcher.launch_system()
        if success:
            logger.info("🎉 A2A Enhanced Communication System started successfully!")
        else:
            logger.error("❌ Failed to start A2A system")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 A2A system shutdown complete")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
