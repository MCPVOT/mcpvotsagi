#!/usr/bin/env python3
"""
Simple Service Launcher - Focus on Working Components
====================================================
Launch only the services that actually work
"""

import asyncio
import subprocess
import sys
import time
import logging
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SimpleServiceLauncher")

class SimpleServiceLauncher:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.services = []

    def check_claudia_availability(self):
        """Check if Claudia/Ollama is available"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"✅ Claudia/Ollama available with {len(models)} models")
                return True
            else:
                logger.warning("⚠️ Claudia/Ollama not responding")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Claudia/Ollama not available: {e}")
            return False

    def start_service(self, script_name, port, service_name):
        """Start a single service"""
        try:
            logger.info(f"🔄 Starting {service_name}...")

            # Use Python from virtual environment if available
            python_cmd = sys.executable
            if (self.base_path / '.venv' / 'Scripts' / 'python.exe').exists():
                python_cmd = str(self.base_path / '.venv' / 'Scripts' / 'python.exe')

            script_path = self.base_path / script_name
            if not script_path.exists():
                logger.error(f"❌ Script not found: {script_path}")
                return None

            # Start the service
            process = subprocess.Popen(
                [python_cmd, str(script_path)],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Give it time to start
            time.sleep(3)

            # Check if it's still running
            if process.poll() is None:
                logger.info(f"✅ {service_name} started successfully (PID: {process.pid})")
                self.services.append({
                    'name': service_name,
                    'process': process,
                    'port': port,
                    'script': script_name
                })
                return process
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {service_name} failed to start")
                if stderr:
                    logger.error(f"Error: {stderr[:200]}...")
                return None

        except Exception as e:
            logger.error(f"❌ Error starting {service_name}: {e}")
            return None

    def check_port(self, port):
        """Check if a port is in use"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def run(self):
        """Run the simple service launcher"""
        logger.info("🚀 Starting Simple Service Launcher...")

        print("=" * 80)
        print("🤖 SIMPLE CLAUDIA-ENHANCED ECOSYSTEM")
        print("=" * 80)

        # Check Claudia availability
        claudia_available = self.check_claudia_availability()

        # Define services to start (only the working ones)
        services_to_start = [
            {
                'script': 'jupiter_ultimate_dashboard_v4.py',
                'port': 8891,
                'name': 'Jupiter Ultimate Dashboard V4'
            }
        ]

        # Start services
        started_services = 0
        for service_config in services_to_start:
            port = service_config['port']

            # Check if port is already in use
            if self.check_port(port):
                logger.warning(f"⚠️ Port {port} already in use for {service_config['name']}")
                started_services += 1
                continue

            # Try to start the service
            process = self.start_service(
                service_config['script'],
                port,
                service_config['name']
            )

            if process:
                started_services += 1

        # Display status
        print(f"\n✅ Started {started_services}/{len(services_to_start)} services")
        print("\n📋 SERVICE STATUS:")

        for service_config in services_to_start:
            port = service_config['port']
            name = service_config['name']

            if self.check_port(port):
                print(f"   {name}: ✅ RUNNING (Port: {port})")
                print(f"   URL: http://localhost:{port}")
            else:
                print(f"   {name}: ❌ STOPPED (Port: {port})")

        print(f"\n🤖 Claudia AI Integration: {'✅ ENABLED' if claudia_available else '❌ DISABLED'}")

        if claudia_available:
            print("🧠 Available Models:")
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                models = response.json().get('models', [])[:3]  # Top 3
                for model in models:
                    print(f"   - {model.get('name', 'Unknown')}")
            except:
                pass

        print("\n" + "=" * 80)
        print("✨ Simple ecosystem ready. Services are running independently.")
        print("Press Ctrl+C to show status (services will continue running)")
        print("=" * 80)

        try:
            while True:
                time.sleep(30)
                # Periodic status check
                running_count = sum(1 for config in services_to_start if self.check_port(config['port']))
                logger.info(f"📊 Status: {running_count}/{len(services_to_start)} services running")
        except KeyboardInterrupt:
            print("\n🔍 Final Status Check:")
            for service_config in services_to_start:
                port = service_config['port']
                name = service_config['name']
                status = "✅ RUNNING" if self.check_port(port) else "❌ STOPPED"
                print(f"   {name}: {status} (Port: {port})")
            print("\n✨ Services continue running independently.")

if __name__ == "__main__":
    launcher = SimpleServiceLauncher()
    launcher.run()
