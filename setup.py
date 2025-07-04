#!/usr/bin/env python3
"""
MCPVotsAgi Setup Script
Professional installation and configuration utility
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('setup.log')
    ]
)
logger = logging.getLogger(__name__)

class MCPVotsAgiSetup:
    """Professional setup manager for MCPVotsAgi"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.requirements_files = [
            'requirements.txt',
            'requirements_real_data.txt'
        ]

    def print_banner(self):
        """Print professional setup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    MCPVotsAgi Setup                          ║
║              Professional AGI Ecosystem                      ║
║                                                              ║
║  🚀 Autonomous Trading • 🧠 Multi-AI • 🔐 Blockchain       ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def check_system_requirements(self) -> bool:
        """Check system requirements"""
        logger.info("🔍 Checking system requirements...")

        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("❌ Python 3.8+ is required")
            return False
        logger.info(f"✅ Python {self.python_version} detected")

        # Check essential commands
        required_commands = ['git', 'node', 'npm']
        for cmd in required_commands:
            if not shutil.which(cmd):
                logger.warning(f"⚠️  {cmd} not found - some features may be limited")
            else:
                logger.info(f"✅ {cmd} available")

        # Check available memory
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 8:
                logger.warning(f"⚠️  Low memory detected ({memory_gb:.1f}GB) - 8GB+ recommended")
            else:
                logger.info(f"✅ Memory: {memory_gb:.1f}GB")
        except ImportError:
            logger.info("💡 Install psutil for memory checking")

        return True

    def setup_virtual_environment(self) -> bool:
        """Set up Python virtual environment"""
        logger.info("🐍 Setting up virtual environment...")

        venv_path = self.project_root / "venv"

        if venv_path.exists():
            logger.info("✅ Virtual environment already exists")
            return True

        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True)
            logger.info("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to create virtual environment")
            return False

    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("📦 Installing Python dependencies...")

        venv_path = self.project_root / "venv"
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"

        if not pip_path.exists():
            logger.error("❌ Virtual environment not properly set up")
            return False

        # Upgrade pip
        try:
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            logger.info("✅ Pip upgraded")
        except subprocess.CalledProcessError:
            logger.warning("⚠️  Could not upgrade pip")

        # Install requirements
        for req_file in self.requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    subprocess.run([
                        str(pip_path), "install", "-r", str(req_path)
                    ], check=True)
                    logger.info(f"✅ Installed {req_file}")
                except subprocess.CalledProcessError:
                    logger.error(f"❌ Failed to install {req_file}")
                    return False
            else:
                logger.warning(f"⚠️  {req_file} not found")

        return True

    def install_node_dependencies(self) -> bool:
        """Install Node.js dependencies"""
        logger.info("📦 Installing Node.js dependencies...")

        package_json = self.project_root / "package.json"
        if not package_json.exists():
            logger.info("💡 No package.json found - skipping Node.js setup")
            return True

        try:
            subprocess.run(["npm", "install"],
                         cwd=str(self.project_root), check=True)
            logger.info("✅ Node.js dependencies installed")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to install Node.js dependencies")
            return False

    def setup_configuration(self) -> bool:
        """Set up configuration files"""
        logger.info("⚙️  Setting up configuration...")

        # Copy .env.example to .env if not exists
        env_example = self.project_root / ".env.example"
        env_file = self.project_root / ".env"

        if env_example.exists() and not env_file.exists():
            shutil.copy(env_example, env_file)
            logger.info("✅ .env file created from template")

        # Create necessary directories
        directories = [
            'data', 'logs', 'temp', 'static/uploads',
            'config/development', 'config/production', 'config/testing'
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")

        return True

    def setup_database(self) -> bool:
        """Set up database"""
        logger.info("🗄️  Setting up database...")

        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)

        # Create empty database files
        db_files = [
            'mcpvots.db', 'ecosystem_knowledge.db',
            'oracle_agi_v5.db', 'dashboard_metrics.db'
        ]

        for db_file in db_files:
            db_path = data_dir / db_file
            if not db_path.exists():
                db_path.touch()
                logger.info(f"✅ Created database: {db_file}")

        return True

    def setup_git_hooks(self) -> bool:
        """Set up Git hooks"""
        logger.info("🪝 Setting up Git hooks...")

        hooks_dir = self.project_root / ".git" / "hooks"
        if not hooks_dir.exists():
            logger.info("💡 Not a Git repository - skipping hooks setup")
            return True

        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/sh
# MCPVotsAgi pre-commit hook
echo "Running pre-commit checks..."

# Check Python syntax
python -m py_compile src/**/*.py
if [ $? -ne 0 ]; then
    echo "❌ Python syntax errors found"
    exit 1
fi

# Check for secrets (basic)
if grep -r "sk-" --include="*.py" --include="*.js" --include="*.json" .; then
    echo "❌ Potential secrets found in code"
    exit 1
fi

echo "✅ Pre-commit checks passed"
"""

        try:
            with open(pre_commit_hook, 'w') as f:
                f.write(pre_commit_content)
            os.chmod(pre_commit_hook, 0o755)
            logger.info("✅ Git pre-commit hook installed")
        except Exception as e:
            logger.warning(f"⚠️  Could not install Git hooks: {e}")

        return True

    def run_initial_tests(self) -> bool:
        """Run initial system tests"""
        logger.info("🧪 Running initial tests...")

        # Test Python imports
        test_imports = [
            'asyncio', 'aiohttp', 'sqlite3', 'json', 'logging'
        ]

        for module in test_imports:
            try:
                __import__(module)
                logger.info(f"✅ {module} import successful")
            except ImportError:
                logger.warning(f"⚠️  {module} import failed")

        # Test file permissions
        test_files = [
            'src/core/launcher.py',
            'scripts/setup/install_all_dependencies.py'
        ]

        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                if os.access(full_path, os.R_OK):
                    logger.info(f"✅ {file_path} readable")
                else:
                    logger.warning(f"⚠️  {file_path} not readable")

        return True

    def print_next_steps(self):
        """Print next steps for user"""
        next_steps = """
╔══════════════════════════════════════════════════════════════╗
║                        SETUP COMPLETE! 🎉                    ║
╚══════════════════════════════════════════════════════════════╝

🚀 Next Steps:

1. Configure your environment:
   📝 Edit .env file with your API keys and settings

2. Start the system:
   🖥️  python src/core/launcher.py

3. Access the dashboard:
   🌐 http://localhost:8090

4. View documentation:
   📚 Open docs/README.md

5. Run tests:
   🧪 python -m pytest src/tests/

6. Monitor logs:
   📊 tail -f logs/mcpvots.log

📖 Documentation: https://github.com/kabrony/mcpvotsagi
💬 Support: Create an issue on GitHub
🔐 Security: Review SECURITY.md for guidelines

Happy trading! 🚀
        """
        print(next_steps)

    def run_setup(self, skip_deps: bool = False) -> bool:
        """Run complete setup process"""
        self.print_banner()

        steps = [
            ("System Requirements", self.check_system_requirements),
            ("Virtual Environment", self.setup_virtual_environment),
            ("Configuration", self.setup_configuration),
            ("Database", self.setup_database),
            ("Git Hooks", self.setup_git_hooks),
            ("Initial Tests", self.run_initial_tests),
        ]

        if not skip_deps:
            steps.insert(2, ("Python Dependencies", self.install_python_dependencies))
            steps.insert(3, ("Node Dependencies", self.install_node_dependencies))

        for step_name, step_func in steps:
            logger.info(f"📋 Step: {step_name}")
            try:
                if not step_func():
                    logger.error(f"❌ Setup failed at: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"❌ Error in {step_name}: {e}")
                return False

        self.print_next_steps()
        return True

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description='MCPVotsAgi Setup Script')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip dependency installation')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    setup = MCPVotsAgiSetup()

    try:
        success = setup.run_setup(skip_deps=args.skip_deps)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
