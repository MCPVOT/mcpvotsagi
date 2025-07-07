#!/usr/bin/env python3
"""
Ultimate Cyberpunk System Launcher
Launches all system components with Jupiter DEX integration
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil

class CyberpunkSystemLauncher:
    """Ultimate system launcher with cyberpunk theme"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=8)

        # System components
        self.components = {
            "watchyourlan_integration": {
                "script": "watchyourlan_cyberpunk_ultimate_integration.py",
                "description": "🔥 CYBERPUNK NETWORK MONITOR",
                "port": None,
                "health_check": None
            },
            "cyberpunk_dashboard": {
                "script": "cyberpunk_dashboard.py",
                "description": "🔥 CYBERPUNK DASHBOARD",
                "port": 8891,
                "health_check": "http://localhost:8891"
            },
            "ultimate_trading_system": {
                "script": "ultimate_trading_system_v3.py",
                "description": "💰 ULTIMATE TRADING SYSTEM",
                "port": 8889,
                "health_check": "http://localhost:8889"
            },
            "jupiter_dashboard": {
                "script": "jupiter_ultimate_dashboard_v4.py",
                "description": "🚀 JUPITER DEX DASHBOARD",
                "port": 8892,
                "health_check": "http://localhost:8892"
            }
        }

        self.logger.info("🔥 CYBERPUNK SYSTEM LAUNCHER INITIALIZED 🔥")

    def _setup_logger(self) -> logging.Logger:
        """Setup cyberpunk logger"""
        logger = logging.getLogger("CyberpunkLauncher")
        logger.setLevel(logging.INFO)

        # Create console handler with custom formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Custom formatter with colors
        class CyberpunkFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
                'RESET': '\033[0m'      # Reset
            }

            def format(self, record):
                color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
                record.levelname = f"{color}[{record.levelname}]{self.COLORS['RESET']}"
                record.msg = f"{color}{record.msg}{self.COLORS['RESET']}"
                return super().format(record)

        formatter = CyberpunkFormatter('%(asctime)s - 🔥 %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        required_packages = [
            "aiohttp",
            "jinja2",
            "sqlite3",
            "psutil",
            "asyncio"
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
            return False

        self.logger.info("✅ All dependencies are installed")
        return True

    def check_system_resources(self) -> bool:
        """Check system resources"""
        try:
            # Check memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.logger.warning(f"⚠️ High memory usage: {memory.percent}%")

            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                self.logger.warning(f"⚠️ High CPU usage: {cpu_percent}%")

            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                self.logger.warning(f"⚠️ High disk usage: {disk.percent}%")

            self.logger.info(f"📊 System resources: CPU {cpu_percent}%, Memory {memory.percent}%, Disk {disk.percent}%")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error checking system resources: {e}")
            return False

    def create_directories(self):
        """Create necessary directories"""
        directories = [
            "data",
            "logs",
            "config",
            "templates",
            "static",
            "data/reports"
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        self.logger.info("📁 Created necessary directories")

    def start_component(self, name: str, component: Dict[str, Any]) -> bool:
        """Start a single component"""
        try:
            script_path = Path(component["script"])
            if not script_path.exists():
                self.logger.error(f"❌ Script not found: {script_path}")
                return False

            # Start the process
            self.logger.info(f"🚀 Starting {component['description']}")

            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes[name] = process
            self.logger.info(f"✅ Started {component['description']} (PID: {process.pid})")

            # Wait a moment for the process to start
            time.sleep(2)

            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.logger.error(f"❌ {component['description']} failed to start:")
                self.logger.error(f"STDOUT: {stdout}")
                self.logger.error(f"STDERR: {stderr}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Error starting {component['description']}: {e}")
            return False

    def check_component_health(self, name: str, component: Dict[str, Any]) -> bool:
        """Check if a component is healthy"""
        try:
            if name not in self.processes:
                return False

            process = self.processes[name]
            if process.poll() is not None:
                return False

            # If there's a health check URL, we could test it here
            # For now, just check if process is running
            return True

        except Exception as e:
            self.logger.error(f"❌ Error checking health of {component['description']}: {e}")
            return False

    def stop_component(self, name: str):
        """Stop a component"""
        try:
            if name in self.processes:
                process = self.processes[name]
                process.terminate()

                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                del self.processes[name]
                self.logger.info(f"🛑 Stopped {self.components[name]['description']}")

        except Exception as e:
            self.logger.error(f"❌ Error stopping {name}: {e}")

    def monitor_components(self):
        """Monitor running components"""
        while self.running:
            try:
                for name, component in self.components.items():
                    if name in self.processes:
                        if not self.check_component_health(name, component):
                            self.logger.warning(f"⚠️ {component['description']} is not healthy")
                            # Optionally restart the component
                            # self.restart_component(name, component)

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"❌ Error monitoring components: {e}")
                time.sleep(5)

    def restart_component(self, name: str, component: Dict[str, Any]):
        """Restart a component"""
        self.logger.info(f"🔄 Restarting {component['description']}")
        self.stop_component(name)
        time.sleep(2)
        self.start_component(name, component)

    def display_status(self):
        """Display system status"""
        print("\n" + "="*60)
        print("🔥 CYBERPUNK SYSTEM STATUS 🔥")
        print("="*60)

        for name, component in self.components.items():
            if name in self.processes:
                process = self.processes[name]
                if process.poll() is None:
                    status = "✅ RUNNING"
                    pid = f"(PID: {process.pid})"
                else:
                    status = "❌ STOPPED"
                    pid = ""
            else:
                status = "❌ NOT STARTED"
                pid = ""

            print(f"{component['description']}: {status} {pid}")
            if component.get('port'):
                print(f"   URL: http://localhost:{component['port']}")

        print("="*60)
        print(f"Total running processes: {len([p for p in self.processes.values() if p.poll() is None])}")
        print("="*60)

    def start_all(self):
        """Start all components"""
        self.logger.info("🔥 STARTING CYBERPUNK SYSTEM 🔥")

        # Check prerequisites
        if not self.check_dependencies():
            self.logger.error("❌ Prerequisites not met")
            return False

        if not self.check_system_resources():
            self.logger.warning("⚠️ System resource warning")

        # Create directories
        self.create_directories()

        # Start components
        started_components = 0
        for name, component in self.components.items():
            if self.start_component(name, component):
                started_components += 1
            else:
                self.logger.error(f"❌ Failed to start {component['description']}")

        self.logger.info(f"🚀 Started {started_components}/{len(self.components)} components")

        # Start monitoring
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_components)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Display status
        self.display_status()

        return started_components > 0

    def stop_all(self):
        """Stop all components"""
        self.logger.info("🛑 STOPPING CYBERPUNK SYSTEM 🛑")
        self.running = False

        for name in list(self.processes.keys()):
            self.stop_component(name)

        self.logger.info("🔥 CYBERPUNK SYSTEM STOPPED 🔥")

    def run_interactive(self):
        """Run interactive mode"""
        self.start_all()

        try:
            while True:
                print("\n🔥 CYBERPUNK SYSTEM CONTROL 🔥")
                print("1. Display Status")
                print("2. Restart Component")
                print("3. Stop Component")
                print("4. Start Component")
                print("5. Stop All")
                print("6. Exit")

                choice = input("\nEnter choice (1-6): ").strip()

                if choice == "1":
                    self.display_status()
                elif choice == "2":
                    self._restart_component_interactive()
                elif choice == "3":
                    self._stop_component_interactive()
                elif choice == "4":
                    self._start_component_interactive()
                elif choice == "5":
                    self.stop_all()
                    break
                elif choice == "6":
                    break
                else:
                    print("Invalid choice")

        except KeyboardInterrupt:
            self.logger.info("🔥 Interrupted by user 🔥")
        finally:
            self.stop_all()

    def _restart_component_interactive(self):
        """Interactive component restart"""
        print("\nAvailable components:")
        for i, (name, component) in enumerate(self.components.items(), 1):
            print(f"{i}. {component['description']}")

        try:
            choice = int(input("Enter component number: ")) - 1
            name = list(self.components.keys())[choice]
            component = self.components[name]
            self.restart_component(name, component)
        except (ValueError, IndexError):
            print("Invalid choice")

    def _stop_component_interactive(self):
        """Interactive component stop"""
        print("\nRunning components:")
        running_components = [(name, comp) for name, comp in self.components.items() if name in self.processes]

        for i, (name, component) in enumerate(running_components, 1):
            print(f"{i}. {component['description']}")

        try:
            choice = int(input("Enter component number: ")) - 1
            name = running_components[choice][0]
            self.stop_component(name)
        except (ValueError, IndexError):
            print("Invalid choice")

    def _start_component_interactive(self):
        """Interactive component start"""
        print("\nStopped components:")
        stopped_components = [(name, comp) for name, comp in self.components.items() if name not in self.processes]

        for i, (name, component) in enumerate(stopped_components, 1):
            print(f"{i}. {component['description']}")

        try:
            choice = int(input("Enter component number: ")) - 1
            name, component = stopped_components[choice]
            self.start_component(name, component)
        except (ValueError, IndexError):
            print("Invalid choice")

def main():
    """Main function"""
    launcher = CyberpunkSystemLauncher()

    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            launcher.start_all()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                launcher.stop_all()
        elif sys.argv[1] == "stop":
            launcher.stop_all()
        elif sys.argv[1] == "status":
            launcher.display_status()
        else:
            print("Usage: python cyberpunk_launcher.py [start|stop|status]")
    else:
        launcher.run_interactive()

if __name__ == "__main__":
    main()
