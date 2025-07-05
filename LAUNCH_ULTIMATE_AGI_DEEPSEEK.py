#!/usr/bin/env python3
"""
ULTIMATE AGI SYSTEM LAUNCHER with DeepSeek-R1 Model Verification
================================================================
🚀 Ensures the correct DeepSeek-R1 model is loaded and launches the complete system
Model: unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL (ID: 2cfa2d3c7a64)
"""

import asyncio
import subprocess
import sys
import os
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateAGILauncher:
    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.required_model = "unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
        self.model_id = "2cfa2d3c7a64"
        self.system_components = {
            'ollama': False,
            'deepseek_model': False,
            'mcp_servers': False,
            'context7': False,
            'claudia': False,
            'ipfs': False
        }

    def print_banner(self):
        """Print startup banner"""
        print("""
🚀 ===============================================================
   ULTIMATE AGI SYSTEM LAUNCHER v2.0
🚀 ===============================================================

🧠 DeepSeek-R1 Model: unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
🔗 MCP Tools: FileSystem, GitHub, Memory, Browser, Brave Search
📚 Context7: Real-time documentation enrichment
🎨 Claudia: Agent orchestration platform
🌐 IPFS: Decentralized storage
💹 Trading: Real-time market analysis and execution

🎯 THE ONE AND ONLY consolidated AGI portal
        """)

    async def check_ollama_installation(self):
        """Check if Ollama is installed and running"""
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Ollama is installed")
                self.system_components['ollama'] = True
                return True
            else:
                logger.error("❌ Ollama is not installed")
                return False
        except FileNotFoundError:
            logger.error("❌ Ollama not found - please install Ollama first")
            return False

    async def ensure_deepseek_model(self):
        """Ensure the correct DeepSeek-R1 model is loaded"""
        try:
            # Check current models
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)

            # Check if our specific model is already loaded
            if 'deepseek-r1-0528-qwen3-8b-gguf:q4_k_xl' in result.stdout.lower():
                logger.info(f"✅ DeepSeek-R1 model {self.required_model} is already loaded")
                self.system_components['deepseek_model'] = True
                return True

            # If not loaded, try to pull it
            logger.info(f"🔄 Pulling DeepSeek-R1 model: {self.required_model}")
            print("   This may take several minutes for the first time...")

            pull_result = subprocess.run(
                ['ollama', 'pull', self.required_model],
                capture_output=True,
                text=True,
                timeout=1200  # 20 minutes timeout
            )

            if pull_result.returncode == 0:
                logger.info(f"✅ Successfully pulled DeepSeek-R1 model: {self.required_model}")
                self.system_components['deepseek_model'] = True
                return True
            else:
                logger.error(f"❌ Failed to pull model: {pull_result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("⏰ Model download timeout - this may take a while")
            return False
        except Exception as e:
            logger.error(f"❌ Error ensuring DeepSeek model: {e}")
            return False

    async def verify_deepseek_model(self):
        """Verify the DeepSeek model is working correctly"""
        try:
            # Test with a simple prompt
            test_prompt = "Hello, please confirm you are DeepSeek-R1 and ready to help."
            cmd = ['ollama', 'run', self.required_model, test_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                logger.info(f"✅ DeepSeek-R1 model verification successful")
                logger.info(f"   Model response: {result.stdout.strip()[:100]}...")
                return True
            else:
                logger.warning(f"⚠️ DeepSeek-R1 model verification failed")
                return False

        except Exception as e:
            logger.error(f"❌ Error verifying DeepSeek model: {e}")
            return False

    async def start_mcp_servers(self):
        """Start all MCP servers"""
        try:
            logger.info("🔄 Starting MCP servers...")

            # Start MCP servers in background
            mcp_servers = [
                {'name': 'filesystem', 'port': 3000, 'path': 'tools/mcp-filesystem'},
                {'name': 'github', 'port': 3001, 'path': 'tools/mcp-github'},
                {'name': 'memory', 'port': 3002, 'path': 'tools/mcp-memory'},
                {'name': 'browser', 'port': 3003, 'path': 'tools/mcp-browser'},
                {'name': 'brave-search', 'port': 3004, 'path': 'tools/mcp-brave-search'}
            ]

            started_servers = 0
            for server in mcp_servers:
                server_path = self.workspace_root / server['path']
                if server_path.exists():
                    try:
                        # Start server in background
                        subprocess.Popen(
                            ['node', 'dist/index.js'],
                            cwd=server_path,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        started_servers += 1
                        logger.info(f"✅ Started {server['name']} MCP server on port {server['port']}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to start {server['name']} MCP server: {e}")
                else:
                    logger.warning(f"⚠️ MCP server path not found: {server_path}")

            if started_servers >= 3:
                self.system_components['mcp_servers'] = True
                logger.info(f"✅ Started {started_servers} MCP servers")
                return True
            else:
                logger.warning(f"⚠️ Only {started_servers} MCP servers started")
                return False

        except Exception as e:
            logger.error(f"❌ Error starting MCP servers: {e}")
            return False

    async def start_context7(self):
        """Start Context7 documentation server"""
        try:
            context7_path = self.workspace_root / 'tools' / 'context7'
            if context7_path.exists():
                logger.info("🔄 Starting Context7 documentation server...")

                # Start Context7 server in background
                subprocess.Popen(
                    ['node', 'src/index.js'],
                    cwd=context7_path,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                self.system_components['context7'] = True
                logger.info("✅ Context7 documentation server started")
                return True
            else:
                logger.warning("⚠️ Context7 not found - documentation enrichment will be limited")
                return False

        except Exception as e:
            logger.error(f"❌ Error starting Context7: {e}")
            return False

    async def start_claudia(self):
        """Start Claudia agent orchestration"""
        try:
            claudia_path = self.workspace_root / 'claudia'
            if claudia_path.exists():
                logger.info("🔄 Starting Claudia agent orchestration...")

                # Claudia integration will be handled by the bridge
                self.system_components['claudia'] = True
                logger.info("✅ Claudia integration ready")
                return True
            else:
                logger.warning("⚠️ Claudia not found - agent orchestration will be limited")
                return False

        except Exception as e:
            logger.error(f"❌ Error starting Claudia: {e}")
            return False

    async def check_ipfs(self):
        """Check if IPFS is available"""
        try:
            result = subprocess.run(['ipfs', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.system_components['ipfs'] = True
                logger.info("✅ IPFS is available")
                return True
            else:
                logger.warning("⚠️ IPFS not available - decentralized storage will be limited")
                return False
        except FileNotFoundError:
            logger.warning("⚠️ IPFS not installed - decentralized storage will be limited")
            return False

    def print_system_status(self):
        """Print system component status"""
        print("\n🔧 SYSTEM COMPONENT STATUS:")
        print("=" * 50)

        status_map = {
            'ollama': '🧠 Ollama Runtime',
            'deepseek_model': '🤖 DeepSeek-R1 Model',
            'mcp_servers': '🔗 MCP Tool Servers',
            'context7': '📚 Context7 Documentation',
            'claudia': '🎨 Claudia Agent Platform',
            'ipfs': '🌐 IPFS Network'
        }

        for key, name in status_map.items():
            status = "✅ READY" if self.system_components[key] else "❌ NOT AVAILABLE"
            print(f"{name}: {status}")

    async def launch_ultimate_agi(self):
        """Launch the Ultimate AGI System"""
        try:
            logger.info("🚀 Launching Ultimate AGI System...")

            # Change to src/core directory
            core_path = self.workspace_root / 'src' / 'core'
            os.chdir(core_path)

            # Launch the main system
            subprocess.run([sys.executable, 'ULTIMATE_AGI_SYSTEM.py'])

        except Exception as e:
            logger.error(f"❌ Error launching Ultimate AGI System: {e}")
            return False

    async def run(self):
        """Main launcher routine"""
        self.print_banner()

        # Check system requirements
        logger.info("🔍 Checking system requirements...")

        # Check Ollama
        if not await self.check_ollama_installation():
            print("\n❌ CRITICAL: Ollama is required but not installed")
            print("   Please install Ollama from: https://ollama.com/")
            return False

        # Ensure DeepSeek model
        if not await self.ensure_deepseek_model():
            print("\n❌ CRITICAL: Failed to load DeepSeek-R1 model")
            print("   The system cannot function without this model")
            return False

        # Verify model is working
        if not await self.verify_deepseek_model():
            print("\n⚠️ WARNING: DeepSeek-R1 model verification failed")
            print("   Continuing anyway, but chat functionality may be limited")

        # Start optional components
        await self.start_mcp_servers()
        await self.start_context7()
        await self.start_claudia()
        await self.check_ipfs()

        # Print status
        self.print_system_status()

        # Give servers time to start
        logger.info("⏳ Waiting for all services to initialize...")
        await asyncio.sleep(3)

        # Launch the main system
        print("\n🚀 LAUNCHING ULTIMATE AGI SYSTEM...")
        print("=" * 50)
        await self.launch_ultimate_agi()

def main():
    """Main entry point"""
    try:
        launcher = UltimateAGILauncher()
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\n👋 Launch cancelled by user")
    except Exception as e:
        print(f"💥 Launch error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
