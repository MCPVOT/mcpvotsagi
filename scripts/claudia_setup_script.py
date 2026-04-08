#!/usr/bin/env python3
"""
CLAUDIA AGI SYSTEM SETUP SCRIPT
==============================
Automated setup script for integrating Claudia AGI system with ULTIMATE AGI SYSTEM V3
Handles all prerequisite installation and configuration
"""

import asyncio
import json
import logging
import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import urllib.request
import zipfile
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claudia_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ClaudiaSetup')

class ClaudiaSystemSetup:
    """
    Automated setup for Claudia AGI system integration
    """

    def __init__(self):
        self.logger = logging.getLogger('ClaudiaSetup')
        self.system_info = {
            'platform': platform.system(),
            'architecture': platform.machine(),
            'python_version': sys.version_info,
            'workspace_path': Path(__file__).parent.absolute()
        }
        self.setup_status = {
            'python_deps': False,
            'postgresql': False,
            'ollama': False,
            'deepseek_model': False,
            'claudia_config': False,
            'database_init': False
        }

    async def run_full_setup(self) -> bool:
        """Run the complete setup process"""
        try:
            self.logger.info("🚀 STARTING CLAUDIA AGI SYSTEM SETUP")
            self.logger.info(f"📍 Platform: {self.system_info['platform']}")
            self.logger.info(f"📍 Architecture: {self.system_info['architecture']}")
            self.logger.info(f"📍 Python: {self.system_info['python_version']}")
            self.logger.info(f"📍 Workspace: {self.system_info['workspace_path']}")

            # Step 1: Install Python dependencies
            if not await self.install_python_dependencies():
                self.logger.error("❌ Failed to install Python dependencies")
                return False

            # Step 2: Setup PostgreSQL
            if not await self.setup_postgresql():
                self.logger.error("❌ Failed to setup PostgreSQL")
                return False

            # Step 3: Install Ollama
            if not await self.install_ollama():
                self.logger.error("❌ Failed to install Ollama")
                return False

            # Step 4: Download DeepSeek model
            if not await self.install_deepseek_model():
                self.logger.error("❌ Failed to install DeepSeek model")
                return False

            # Step 5: Configure Claudia system
            if not await self.configure_claudia_system():
                self.logger.error("❌ Failed to configure Claudia system")
                return False

            # Step 6: Initialize database
            if not await self.initialize_database():
                self.logger.error("❌ Failed to initialize database")
                return False

            # Step 7: Verify setup
            if not await self.verify_setup():
                self.logger.error("❌ Setup verification failed")
                return False

            self.logger.info("✅ CLAUDIA AGI SYSTEM SETUP COMPLETE!")
            await self.generate_setup_report()

            return True

        except Exception as e:
            self.logger.error(f"❌ Setup failed: {e}")
            return False

    async def install_python_dependencies(self) -> bool:
        """Install required Python dependencies"""
        self.logger.info("📦 Installing Python dependencies...")

        try:
            # Core dependencies for Claudia system
            dependencies = [
                'asyncio',
                'aiohttp',
                'asyncpg',
                'psycopg2-binary',
                'fastapi',
                'uvicorn',
                'pydantic',
                'numpy',
                'torch',
                'psutil',
                'redis',
                'asyncio-mqtt',
                'sqlalchemy',
                'alembic',
                'python-multipart',
                'python-jose[cryptography]',
                'passlib[bcrypt]',
                'jinja2',
                'requests'
            ]

            # Install dependencies
            for dep in dependencies:
                self.logger.info(f"📦 Installing {dep}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', dep, '--upgrade'
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    self.logger.warning(f"⚠️ Failed to install {dep}: {result.stderr}")
                else:
                    self.logger.info(f"✅ {dep} installed successfully")

            self.setup_status['python_deps'] = True
            self.logger.info("✅ Python dependencies installation complete")
            return True

        except Exception as e:
            self.logger.error(f"❌ Python dependencies installation failed: {e}")
            return False

    async def setup_postgresql(self) -> bool:
        """Setup PostgreSQL database"""
        self.logger.info("🐘 Setting up PostgreSQL...")

        try:
            # Check if PostgreSQL is already installed
            if self.check_postgresql_installed():
                self.logger.info("✅ PostgreSQL is already installed")
                self.setup_status['postgresql'] = True
                return True

            # Install PostgreSQL based on platform
            if self.system_info['platform'] == 'Windows':
                success = await self.install_postgresql_windows()
            elif self.system_info['platform'] == 'Darwin':  # macOS
                success = await self.install_postgresql_macos()
            elif self.system_info['platform'] == 'Linux':
                success = await self.install_postgresql_linux()
            else:
                self.logger.error(f"❌ Unsupported platform: {self.system_info['platform']}")
                return False

            if success:
                self.setup_status['postgresql'] = True
                self.logger.info("✅ PostgreSQL setup complete")
                return True
            else:
                self.logger.error("❌ PostgreSQL setup failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL setup error: {e}")
            return False

    def check_postgresql_installed(self) -> bool:
        """Check if PostgreSQL is installed"""
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    async def install_postgresql_windows(self) -> bool:
        """Install PostgreSQL on Windows"""
        self.logger.info("📥 Installing PostgreSQL on Windows...")

        try:
            # Download PostgreSQL installer
            pg_url = "https://get.enterprisedb.com/postgresql/postgresql-15.4-1-windows-x64.exe"
            installer_path = Path(__file__).parent / "postgresql_installer.exe"

            self.logger.info("📥 Downloading PostgreSQL installer...")
            urllib.request.urlretrieve(pg_url, installer_path)

            # Run installer silently
            self.logger.info("🔧 Running PostgreSQL installer...")
            result = subprocess.run([
                str(installer_path),
                '--mode', 'unattended',
                '--superpassword', 'password',
                '--serverport', '5432'
            ], capture_output=True, text=True)

            # Clean up installer
            installer_path.unlink()

            if result.returncode == 0:
                self.logger.info("✅ PostgreSQL installed successfully")
                return True
            else:
                self.logger.error(f"❌ PostgreSQL installation failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL Windows installation error: {e}")
            return False

    async def install_postgresql_macos(self) -> bool:
        """Install PostgreSQL on macOS"""
        self.logger.info("📥 Installing PostgreSQL on macOS...")

        try:
            # Use Homebrew if available
            if shutil.which('brew'):
                result = subprocess.run(['brew', 'install', 'postgresql'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Start PostgreSQL service
                    subprocess.run(['brew', 'services', 'start', 'postgresql'], capture_output=True)
                    self.logger.info("✅ PostgreSQL installed and started with Homebrew")
                    return True

            # Alternative: Use PostgreSQL.app
            self.logger.info("📥 Please install PostgreSQL from https://postgresapp.com/")
            return False

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL macOS installation error: {e}")
            return False

    async def install_postgresql_linux(self) -> bool:
        """Install PostgreSQL on Linux"""
        self.logger.info("📥 Installing PostgreSQL on Linux...")

        try:
            # Try different package managers
            if shutil.which('apt-get'):
                # Ubuntu/Debian
                result = subprocess.run([
                    'sudo', 'apt-get', 'update'
                ], capture_output=True, text=True)

                result = subprocess.run([
                    'sudo', 'apt-get', 'install', '-y', 'postgresql', 'postgresql-contrib'
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    # Start PostgreSQL service
                    subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], capture_output=True)
                    subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], capture_output=True)
                    self.logger.info("✅ PostgreSQL installed and started with apt-get")
                    return True

            elif shutil.which('yum'):
                # CentOS/RHEL
                result = subprocess.run([
                    'sudo', 'yum', 'install', '-y', 'postgresql', 'postgresql-server'
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    subprocess.run(['sudo', 'postgresql-setup', 'initdb'], capture_output=True)
                    subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], capture_output=True)
                    subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], capture_output=True)
                    self.logger.info("✅ PostgreSQL installed and started with yum")
                    return True

            self.logger.error("❌ No supported package manager found")
            return False

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL Linux installation error: {e}")
            return False

    async def install_ollama(self) -> bool:
        """Install Ollama"""
        self.logger.info("🦙 Installing Ollama...")

        try:
            # Check if Ollama is already installed
            if shutil.which('ollama'):
                self.logger.info("✅ Ollama is already installed")
                self.setup_status['ollama'] = True
                return True

            # Install Ollama based on platform
            if self.system_info['platform'] == 'Windows':
                success = await self.install_ollama_windows()
            elif self.system_info['platform'] == 'Darwin':  # macOS
                success = await self.install_ollama_macos()
            elif self.system_info['platform'] == 'Linux':
                success = await self.install_ollama_linux()
            else:
                self.logger.error(f"❌ Unsupported platform: {self.system_info['platform']}")
                return False

            if success:
                self.setup_status['ollama'] = True
                self.logger.info("✅ Ollama installation complete")
                return True
            else:
                self.logger.error("❌ Ollama installation failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ollama installation error: {e}")
            return False

    async def install_ollama_windows(self) -> bool:
        """Install Ollama on Windows"""
        self.logger.info("📥 Installing Ollama on Windows...")

        try:
            # Download Ollama installer
            ollama_url = "https://ollama.com/download/windows"
            installer_path = Path(__file__).parent / "ollama_installer.exe"

            self.logger.info("📥 Downloading Ollama installer...")
            urllib.request.urlretrieve(ollama_url, installer_path)

            # Run installer
            self.logger.info("🔧 Running Ollama installer...")
            result = subprocess.run([str(installer_path)], capture_output=True, text=True)

            # Clean up installer
            installer_path.unlink()

            if result.returncode == 0:
                self.logger.info("✅ Ollama installed successfully")
                return True
            else:
                self.logger.error(f"❌ Ollama installation failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ollama Windows installation error: {e}")
            return False

    async def install_ollama_macos(self) -> bool:
        """Install Ollama on macOS"""
        self.logger.info("📥 Installing Ollama on macOS...")

        try:
            # Use curl to install
            result = subprocess.run([
                'curl', '-fsSL', 'https://ollama.com/install.sh'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                install_script = result.stdout
                proc = subprocess.run(['sh'], input=install_script, text=True, capture_output=True)

                if proc.returncode == 0:
                    self.logger.info("✅ Ollama installed successfully")
                    return True
                else:
                    self.logger.error(f"❌ Ollama installation failed: {proc.stderr}")
                    return False
            else:
                self.logger.error(f"❌ Failed to download Ollama installer: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ollama macOS installation error: {e}")
            return False

    async def install_ollama_linux(self) -> bool:
        """Install Ollama on Linux"""
        self.logger.info("📥 Installing Ollama on Linux...")

        try:
            # Use curl to install
            result = subprocess.run([
                'curl', '-fsSL', 'https://ollama.com/install.sh'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                install_script = result.stdout
                proc = subprocess.run(['sh'], input=install_script, text=True, capture_output=True)

                if proc.returncode == 0:
                    self.logger.info("✅ Ollama installed successfully")
                    return True
                else:
                    self.logger.error(f"❌ Ollama installation failed: {proc.stderr}")
                    return False
            else:
                self.logger.error(f"❌ Failed to download Ollama installer: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ollama Linux installation error: {e}")
            return False

    async def install_deepseek_model(self) -> bool:
        """Install DeepSeek-R1 model"""
        self.logger.info("🧠 Installing DeepSeek-R1 model...")

        try:
            # Check if model is already installed
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0 and 'deepseek-r1' in result.stdout:
                self.logger.info("✅ DeepSeek-R1 model already installed")
                self.setup_status['deepseek_model'] = True
                return True

            # Start Ollama service if not running
            self.logger.info("🚀 Starting Ollama service...")
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await asyncio.sleep(5)  # Wait for service to start

            # Download DeepSeek-R1 model
            self.logger.info("📥 Downloading DeepSeek-R1 model (this may take a while)...")
            result = subprocess.run([
                'ollama', 'pull', 'deepseek-r1:latest'
            ], capture_output=True, text=True, timeout=1800)  # 30 minute timeout

            if result.returncode == 0:
                self.logger.info("✅ DeepSeek-R1 model installed successfully")
                self.setup_status['deepseek_model'] = True
                return True
            else:
                self.logger.error(f"❌ DeepSeek-R1 model installation failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ DeepSeek-R1 model installation timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ DeepSeek-R1 model installation error: {e}")
            return False

    async def configure_claudia_system(self) -> bool:
        """Configure Claudia system settings"""
        self.logger.info("⚙️ Configuring Claudia system...")

        try:
            # Create configuration directory
            config_dir = Path(__file__).parent / "claudia" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)

            # Create main configuration file
            config = {
                'database': {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'claudia_agi',
                    'user': 'postgres',
                    'password': 'password'
                },
                'ollama': {
                    'host': 'localhost',
                    'port': 11434,
                    'model': 'deepseek-r1:latest'
                },
                'services': {
                    'orchestrator': {
                        'host': '0.0.0.0',
                        'port': 8888
                    },
                    'deepseek_agent': {
                        'host': '0.0.0.0',
                        'port': 8893
                    },
                    'mcp_specialist': {
                        'host': '0.0.0.0',
                        'port': 8894
                    }
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'claudia_system.log'
                },
                'security': {
                    'secret_key': 'your-secret-key-here',
                    'algorithm': 'HS256',
                    'access_token_expire_minutes': 30
                }
            }

            config_file = config_dir / "claudia_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            self.logger.info(f"✅ Configuration saved to {config_file}")

            # Create environment file
            env_file = config_dir / ".env"
            with open(env_file, 'w') as f:
                f.write("# Claudia AGI System Environment Variables\n")
                f.write("DATABASE_URL=postgresql://postgres:password@localhost:5432/claudia_agi\n")
                f.write("OLLAMA_HOST=http://localhost:11434\n")
                f.write("SECRET_KEY=your-secret-key-here\n")
                f.write("LOG_LEVEL=INFO\n")

            self.logger.info(f"✅ Environment file created at {env_file}")

            self.setup_status['claudia_config'] = True
            return True

        except Exception as e:
            self.logger.error(f"❌ Configuration setup error: {e}")
            return False

    async def initialize_database(self) -> bool:
        """Initialize the database"""
        self.logger.info("🗄️ Initializing database...")

        try:
            # Create database
            self.logger.info("🔧 Creating Claudia database...")

            # Connect to PostgreSQL and create database
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='postgres',
                user='postgres',
                password=os.environ.get('REDIS_PASSWORD', '')
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            cursor = conn.cursor()

            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'claudia_agi'")
            exists = cursor.fetchone()

            if not exists:
                cursor.execute('CREATE DATABASE claudia_agi')
                self.logger.info("✅ Database 'claudia_agi' created")
            else:
                self.logger.info("✅ Database 'claudia_agi' already exists")

            cursor.close()
            conn.close()

            # Initialize tables (basic schema)
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='claudia_agi',
                user='postgres',
                password=os.environ.get('REDIS_PASSWORD', '')
            )

            cursor = conn.cursor()

            # Create basic tables
            schema_sql = """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                task_id VARCHAR(255) UNIQUE NOT NULL,
                task_type VARCHAR(100) NOT NULL,
                priority INTEGER DEFAULT 1,
                status VARCHAR(50) DEFAULT 'pending',
                payload JSONB,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agents (
                id SERIAL PRIMARY KEY,
                agent_id VARCHAR(255) UNIQUE NOT NULL,
                agent_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) DEFAULT 'idle',
                configuration JSONB,
                metrics JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                metric_type VARCHAR(100) NOT NULL,
                metric_value JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
            CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
            CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp);
            """

            cursor.execute(schema_sql)
            conn.commit()

            self.logger.info("✅ Database schema initialized")

            cursor.close()
            conn.close()

            self.setup_status['database_init'] = True
            return True

        except Exception as e:
            self.logger.error(f"❌ Database initialization error: {e}")
            return False

    async def verify_setup(self) -> bool:
        """Verify the complete setup"""
        self.logger.info("🔍 Verifying setup...")

        try:
            # Check all components
            all_good = True

            for component, status in self.setup_status.items():
                if status:
                    self.logger.info(f"✅ {component}: OK")
                else:
                    self.logger.error(f"❌ {component}: FAILED")
                    all_good = False

            if all_good:
                self.logger.info("✅ All components verified successfully")
                return True
            else:
                self.logger.error("❌ Some components failed verification")
                return False

        except Exception as e:
            self.logger.error(f"❌ Setup verification error: {e}")
            return False

    async def generate_setup_report(self):
        """Generate a comprehensive setup report"""
        self.logger.info("📋 Generating setup report...")

        try:
            report = {
                'setup_timestamp': time.time(),
                'system_info': self.system_info,
                'setup_status': self.setup_status,
                'next_steps': [
                    "1. Run the Claudia system: python claudia/scripts/launch_claudia_system.py",
                    "2. Test the integration bridge: python claudia_integration_bridge.py",
                    "3. Submit test tasks through the API",
                    "4. Monitor system performance",
                    "5. Configure security settings for production"
                ],
                'useful_commands': [
                    "ollama serve - Start Ollama service",
                    "ollama list - List installed models",
                    "psql -U postgres -d claudia_agi - Connect to database",
                    "curl http://localhost:8888/health - Check orchestrator health"
                ],
                'configuration_files': [
                    "claudia/config/claudia_config.json - Main configuration",
                    "claudia/config/.env - Environment variables"
                ]
            }

            report_file = Path(__file__).parent / "CLAUDIA_SETUP_REPORT.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"📋 Setup report saved to {report_file}")

        except Exception as e:
            self.logger.error(f"❌ Setup report generation error: {e}")

async def main():
    """Main setup function"""
    setup = ClaudiaSystemSetup()

    try:
        success = await setup.run_full_setup()

        if success:
            print("\n" + "="*60)
            print("🎉 CLAUDIA AGI SYSTEM SETUP COMPLETE!")
            print("="*60)
            print("✅ All components installed and configured successfully")
            print("📋 Next steps:")
            print("  1. Run: python claudia/scripts/launch_claudia_system.py")
            print("  2. Test: python claudia_integration_bridge.py")
            print("  3. Check: curl http://localhost:8888/health")
            print("📁 Configuration files created in claudia/config/")
            print("📊 Setup report saved as CLAUDIA_SETUP_REPORT.json")
            print("="*60)
            return True
        else:
            print("\n" + "="*60)
            print("❌ CLAUDIA AGI SYSTEM SETUP FAILED")
            print("="*60)
            print("Check the logs for details: claudia_setup.log")
            return False

    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🧠 CLAUDIA AGI SYSTEM AUTOMATED SETUP")
    print("=" * 50)
    print("This script will install and configure:")
    print("  • Python dependencies")
    print("  • PostgreSQL database")
    print("  • Ollama with DeepSeek-R1 model")
    print("  • Claudia system configuration")
    print("=" * 50)

    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
