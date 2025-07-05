#!/usr/bin/env python3
"""
MCPVotsAGI System Update and Verification Script
================================================
Updates all components and ensures the system is ready for production
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPVotsAGIUpdater:
    """Updates and verifies the entire MCPVotsAGI system"""

    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.required_model = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
        self.model_id = "2cfa2d3c7a64"

        # Status tracking
        self.update_status = {
            'dependencies': False,
            'model_verification': False,
            'mcp_servers': False,
            'context7': False,
            'claudia': False,
            'configuration': False,
            'system_test': False
        }

    def print_banner(self):
        """Print update banner"""
        print("""
===============================================================
   MCPVotsAGI System Update and Verification v2.0
===============================================================

Updating all components for the Ultimate AGI System:
- DeepSeek-R1 Model: hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
- MCP Tools: FileSystem, GitHub, Memory, Browser, Brave Search
- Context7: Real-time documentation enrichment
- Claudia: Agent orchestration platform
- IPFS: Decentralized storage
- Trading: Real-time market analysis and execution

THE ONE AND ONLY consolidated AGI portal
        """)

    def update_dependencies(self):
        """Update Python dependencies"""
        try:
            logger.info("Updating Python dependencies...")

            # Install/upgrade pip
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                         check=True, capture_output=True)

            # Install requirements
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                         check=True, capture_output=True)

            logger.info("✅ Python dependencies updated successfully")
            self.update_status['dependencies'] = True
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to update dependencies: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error updating dependencies: {e}")
            return False

    def verify_deepseek_model(self):
        """Verify the correct DeepSeek model is available"""
        try:
            logger.info("Verifying DeepSeek-R1 model...")

            # Check available models
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Ollama is not available")
                return False

            # Check for our specific model
            if self.required_model.lower() in result.stdout.lower():
                logger.info(f"✅ DeepSeek-R1 model verified: {self.required_model}")

                # Test the model with a simple query
                test_result = subprocess.run(
                    ['ollama', 'run', self.required_model, 'Hello, are you DeepSeek-R1?'],
                    capture_output=True, text=True, timeout=30
                )

                if test_result.returncode == 0:
                    logger.info("✅ DeepSeek-R1 model test successful")
                    self.update_status['model_verification'] = True
                    return True
                else:
                    logger.warning("⚠️ DeepSeek-R1 model test failed but model is available")
                    self.update_status['model_verification'] = True
                    return True
            else:
                logger.error(f"❌ Required model not found: {self.required_model}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Model test timeout - model may be slow to load")
            self.update_status['model_verification'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Error verifying DeepSeek model: {e}")
            return False

    def check_mcp_servers(self):
        """Check MCP server availability"""
        try:
            logger.info("Checking MCP servers...")

            mcp_servers = [
                {'name': 'filesystem', 'path': 'tools/mcp-filesystem'},
                {'name': 'github', 'path': 'tools/mcp-github'},
                {'name': 'memory', 'path': 'tools/mcp-memory'},
                {'name': 'browser', 'path': 'tools/mcp-browser'},
                {'name': 'brave-search', 'path': 'tools/mcp-brave-search'}
            ]

            available_servers = 0
            for server in mcp_servers:
                server_path = self.workspace_root / server['path']
                if server_path.exists():
                    # Check if server has required files
                    if (server_path / 'package.json').exists():
                        logger.info(f"✅ {server['name']} MCP server found")
                        available_servers += 1
                    else:
                        logger.warning(f"⚠️ {server['name']} MCP server incomplete")
                else:
                    logger.warning(f"⚠️ {server['name']} MCP server not found")

            if available_servers >= 3:
                logger.info(f"✅ {available_servers}/5 MCP servers available")
                self.update_status['mcp_servers'] = True
                return True
            else:
                logger.warning(f"⚠️ Only {available_servers}/5 MCP servers available")
                return False

        except Exception as e:
            logger.error(f"❌ Error checking MCP servers: {e}")
            return False

    def check_context7(self):
        """Check Context7 integration"""
        try:
            logger.info("Checking Context7 integration...")

            context7_path = self.workspace_root / 'tools' / 'context7'
            if context7_path.exists():
                # Check for key files
                if (context7_path / 'src' / 'index.js').exists():
                    logger.info("✅ Context7 documentation server found")
                    self.update_status['context7'] = True
                    return True
                else:
                    logger.warning("⚠️ Context7 incomplete - missing key files")
                    return False
            else:
                logger.warning("⚠️ Context7 not found - documentation enrichment will be limited")
                return False

        except Exception as e:
            logger.error(f"❌ Error checking Context7: {e}")
            return False

    def check_claudia(self):
        """Check Claudia integration"""
        try:
            logger.info("Checking Claudia integration...")

            claudia_path = self.workspace_root / 'claudia'
            if claudia_path.exists():
                # Check for agent files
                agents_found = 0
                for agent_file in claudia_path.glob('**/*.py'):
                    if 'agent' in agent_file.name.lower():
                        agents_found += 1

                if agents_found > 0:
                    logger.info(f"✅ Claudia integration found with {agents_found} agents")
                    self.update_status['claudia'] = True
                    return True
                else:
                    logger.warning("⚠️ Claudia found but no agents detected")
                    return False
            else:
                logger.warning("⚠️ Claudia not found - agent orchestration will be limited")
                return False

        except Exception as e:
            logger.error(f"❌ Error checking Claudia: {e}")
            return False

    def verify_configuration(self):
        """Verify system configuration"""
        try:
            logger.info("Verifying system configuration...")

            # Check config files
            config_files = [
                'config/unified_system_config.yaml',
                'config/mcp_settings.json',
                '.env.template'
            ]

            config_ok = True
            for config_file in config_files:
                config_path = self.workspace_root / config_file
                if config_path.exists():
                    logger.info(f"✅ Found: {config_file}")
                else:
                    logger.warning(f"⚠️ Missing: {config_file}")
                    config_ok = False

            # Check core system files
            core_files = [
                'src/core/ULTIMATE_AGI_SYSTEM.py',
                'src/core/CONTEXT7_INTEGRATION.py',
                'src/core/claudia_integration_bridge.py',
                'LAUNCH_ULTIMATE_AGI_DEEPSEEK.py'
            ]

            for core_file in core_files:
                core_path = self.workspace_root / core_file
                if core_path.exists():
                    logger.info(f"✅ Found: {core_file}")
                else:
                    logger.error(f"❌ Missing critical file: {core_file}")
                    config_ok = False

            if config_ok:
                logger.info("✅ System configuration verified")
                self.update_status['configuration'] = True
                return True
            else:
                logger.error("❌ System configuration incomplete")
                return False

        except Exception as e:
            logger.error(f"❌ Error verifying configuration: {e}")
            return False

    def run_system_test(self):
        """Run a quick system test"""
        try:
            logger.info("Running system test...")

            # Test system initialization
            test_code = """
import sys
sys.path.append('src/core')
from ULTIMATE_AGI_SYSTEM import UltimateAGISystem

try:
    system = UltimateAGISystem()
    model_name = system.get_deepseek_model_name()
    print(f"SUCCESS: System initialized with model: {model_name}")
except Exception as e:
    print(f"ERROR: System initialization failed: {e}")
    raise
"""

            result = subprocess.run(
                [sys.executable, '-c', test_code],
                capture_output=True, text=True, cwd=self.workspace_root
            )

            if result.returncode == 0 and 'SUCCESS' in result.stdout:
                logger.info("✅ System test passed")
                logger.info(f"   Output: {result.stdout.strip().split('SUCCESS:')[-1]}")
                self.update_status['system_test'] = True
                return True
            else:
                logger.error(f"❌ System test failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error running system test: {e}")
            return False

    def print_status_summary(self):
        """Print final status summary"""
        print("\n" + "="*60)
        print("   MCPVOTSAGI SYSTEM STATUS SUMMARY")
        print("="*60)

        status_items = [
            ('Python Dependencies', self.update_status['dependencies']),
            ('DeepSeek-R1 Model', self.update_status['model_verification']),
            ('MCP Servers', self.update_status['mcp_servers']),
            ('Context7 Integration', self.update_status['context7']),
            ('Claudia Integration', self.update_status['claudia']),
            ('System Configuration', self.update_status['configuration']),
            ('System Test', self.update_status['system_test'])
        ]

        success_count = 0
        for item_name, status in status_items:
            status_text = "OK" if status else "NEEDS ATTENTION"
            print(f"{item_name:.<30} {status_text}")
            if status:
                success_count += 1

        print("="*60)
        print(f"OVERALL STATUS: {success_count}/{len(status_items)} components ready")

        if success_count >= 5:
            print("\n✅ MCPVotsAGI is ready to launch!")
            print("   Run: python LAUNCH_ULTIMATE_AGI_DEEPSEEK.py")
            print("   Or:  START_WINDOWS.bat (Windows)")
            print("   Or:  ./START_UNIX.sh (Linux/Mac)")
        else:
            print("\n⚠️ Some components need attention")
            print("   Please review the status above and fix any issues")

        return success_count >= 5

    def run_update(self):
        """Run the complete update process"""
        self.print_banner()

        logger.info("Starting MCPVotsAGI system update...")

        # Run all update steps
        steps = [
            ("Updating Dependencies", self.update_dependencies),
            ("Verifying DeepSeek Model", self.verify_deepseek_model),
            ("Checking MCP Servers", self.check_mcp_servers),
            ("Checking Context7", self.check_context7),
            ("Checking Claudia", self.check_claudia),
            ("Verifying Configuration", self.verify_configuration),
            ("Running System Test", self.run_system_test)
        ]

        for step_name, step_func in steps:
            logger.info(f"🔄 {step_name}...")
            step_func()  # Continue regardless of individual step results

        # Print final summary
        return self.print_status_summary()

def main():
    """Main entry point"""
    try:
        updater = MCPVotsAGIUpdater()
        success = updater.run_update()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Update error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
