#!/usr/bin/env python3
"""
Stable Claudia-Enhanced Ecosystem Launcher
==========================================
Focuses on stable, working components only
Uses top 3 models: DeepSeek-R1, Qwen2.5-Coder, Llama3.2:3b
"""

import asyncio
import logging
import time
import subprocess
import sys
import os
import signal
from pathlib import Path
import requests
import json
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StableEcosystemLauncher")

class StableEcosystemLauncher:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = {}
        self.running = True

        # Core stable services only
        self.core_services = [
            {
                "name": "Jupiter Ultimate Dashboard V4",
                "script": "jupiter_ultimate_dashboard_v4.py",
                "port": 8891,
                "essential": True
            },
            {
                "name": "Ultimate Trading System V3",
                "script": "ultimate_trading_system_v3.py",
                "port": 8892,
                "essential": True
            },
            {
                "name": "WatchYourLAN Integration",
                "script": "watchyourlan_cyberpunk_ultimate_integration.py",
                "port": 8893,
                "essential": False
            }
        ]

        # Top 3 Claudia models
        self.claudia_models = {
            "reasoning": "deepseek-r1:latest",
            "coding": "qwen2.5-coder:latest",
            "quick": "llama3.2:3b"
        }

    def check_claudia_availability(self) -> bool:
        """Check if Claudia/Ollama is available"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"✅ Claudia/Ollama available with {len(models)} models")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Claudia/Ollama not available: {e}")
        return False

    def test_claudia_model(self, model: str, task: str) -> Optional[str]:
        """Test a specific Claudia model"""
        try:
            payload = {
                'model': model,
                'prompt': f'Test {task} response: What is your status?',
                'stream': False
            }
            response = requests.post('http://localhost:11434/api/generate',
                                   json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response')[:100]
        except Exception as e:
            logger.error(f"❌ Model {model} test failed: {e}")
        return None

    def start_service(self, service: Dict) -> bool:
        """Start a single service"""
        script_path = self.base_path / service["script"]
        if not script_path.exists():
            logger.warning(f"⚠️ Script not found: {service['script']}")
            return False

        try:
            # Check if port is already in use
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', service.get('port', 8000)))
            sock.close()

            if result == 0:
                logger.warning(f"⚠️ Port {service.get('port')} already in use for {service['name']}")
                return True  # Consider it running

            # Start the service
            logger.info(f"🔄 Starting {service['name']}...")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )

            # Give it time to start
            time.sleep(3)

            if process.poll() is None:
                self.processes[service['name']] = process
                logger.info(f"✅ {service['name']} started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {service['name']} failed to start")
                if stderr:
                    logger.error(f"Error: {stderr.decode()[:200]}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start {service['name']}: {e}")
            return False

    def get_service_status(self) -> Dict:
        """Get status of all services"""
        status = {
            "running": 0,
            "total": len(self.core_services),
            "services": {}
        }

        for service in self.core_services:
            name = service['name']
            process = self.processes.get(name)

            if process and process.poll() is None:
                status["services"][name] = "✅ RUNNING"
                status["running"] += 1
            else:
                status["services"][name] = "❌ STOPPED"

        return status

    def display_status(self):
        """Display current ecosystem status"""
        claudia_available = self.check_claudia_availability()
        status = self.get_service_status()

        print("\n" + "="*80)
        print("🚀 STABLE CLAUDIA-ENHANCED ECOSYSTEM STATUS")
        print("="*80)
        print(f"🤖 Claudia AI Integration: {'✅ ENABLED' if claudia_available else '❌ DISABLED'}")
        print(f"🔧 Services Running: {status['running']}/{status['total']}")

        print("\n📋 SERVICE STATUS:")
        for service_name, service_status in status["services"].items():
            service_info = next((s for s in self.core_services if s['name'] == service_name), {})
            port_info = f" (Port: {service_info.get('port', 'N/A')})" if service_info.get('port') else ""
            print(f"   {service_name}: {service_status}{port_info}")

        if claudia_available:
            print("\n🧠 CLAUDIA MODELS:")
            for task, model in self.claudia_models.items():
                print(f"   {task.title()}: {model}")

        print("\n🌐 ACCESS URLS:")
        for service in self.core_services:
            if service.get('port') and service['name'] in status["services"]:
                if "RUNNING" in status["services"][service['name']]:
                    print(f"   {service['name']}: http://localhost:{service['port']}")

        print("\n✨ Stable ecosystem running. Press Ctrl+C to exit.")
        print("="*80)

    async def run(self):
        """Main run loop"""
        logger.info("🚀 Starting Stable Claudia-Enhanced Ecosystem...")

        print("\n" + "="*80)
        print("🤖 STABLE CLAUDIA-ENHANCED ULTIMATE AGI SYSTEM V3")
        print("="*80)

        # Check Claudia availability
        claudia_available = self.check_claudia_availability()

        if claudia_available:
            logger.info("🧠 Testing Claudia models...")
            for task, model in self.claudia_models.items():
                response = self.test_claudia_model(model, task)
                if response:
                    logger.info(f"✅ {task.title()} model ({model}): Working")
                else:
                    logger.warning(f"⚠️ {task.title()} model ({model}): Failed")

        # Start core services
        started_services = 0
        for service in self.core_services:
            if self.start_service(service):
                started_services += 1
            time.sleep(2)  # Stagger startup

        logger.info(f"✅ Started {started_services}/{len(self.core_services)} services")

        # Display status and wait
        self.display_status()

        try:
            while self.running:
                await asyncio.sleep(30)  # Check every 30 seconds instead of 10

                # Simple health check - don't restart automatically
                status = self.get_service_status()
                if status["running"] < len([s for s in self.core_services if s.get('essential', True)]):
                    logger.warning(f"⚠️ Some essential services stopped. Running: {status['running']}/{status['total']}")

        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested...")
            self.running = False

            # Clean shutdown
            for name, process in self.processes.items():
                try:
                    logger.info(f"🔄 Stopping {name}...")
                    if os.name == 'nt':
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()

                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")

            logger.info("✅ Ecosystem shutdown complete")

def main():
    """Main entry point"""
    launcher = StableEcosystemLauncher()
    try:
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\n🛑 Ecosystem stopped by user")
    except Exception as e:
        logger.error(f"❌ Ecosystem error: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
