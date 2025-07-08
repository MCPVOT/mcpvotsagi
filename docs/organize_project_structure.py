#!/usr/bin/env python3
"""
MCPVotsAGI Project Organizer
============================
Organizes the cluttered MCPVotsAGI project into a clean, maintainable structure.
Moves files to appropriate directories and archives redundant code.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPVotsAGIOrganizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_organization"
        self.organization_log = []

    def analyze_current_structure(self):
        """Analyze current file structure"""
        logger.info("[SEARCH] Analyzing current project structure...")

        python_files = list(self.project_root.glob("*.py"))
        md_files = list(self.project_root.glob("*.md"))

        analysis = {
            "total_python_files": len(python_files),
            "total_md_files": len(md_files),
            "python_files": [f.name for f in python_files],
            "md_files": [f.name for f in md_files]
        }

        logger.info(f"📊 Found {len(python_files)} Python files and {len(md_files)} Markdown files")
        return analysis

    def create_directory_structure(self):
        """Create the new organized directory structure"""
        logger.info("[FOLDER] Creating organized directory structure...")

        directories = [
            "core",
            "claudia/scripts",
            "claudia/docs",
            "claudia/config",
            "tools/MCPVots",
            "tools/integrations",
            "dashboards/jupiter",
            "dashboards/monitoring",
            "archive/legacy_scripts",
            "archive/old_dashboards",
            "docs",
            "scripts/setup",
            "scripts/migration",
            "scripts/testing",
            "config"
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            # Create __init__.py for Python packages
            if any(part in directory for part in ["core", "claudia", "tools"]):
                (dir_path / "__init__.py").touch()

        logger.info("[OK] Directory structure created")

    def categorize_files(self):
        """Categorize files for organization"""

        # Core production files (keep in core/)
        core_files = [
            "unified_agi_dashboard.py",
            "claudia_mcp_integration.py",
            "ecosystem_manager_v4_clean.py",
            "ecosystem_core.py"
        ]

        # Claudia AI system files
        claudia_files = [
            "claudia_dashboard_enhancer.py",
            "claudia_deepseek_dashboard_enhancer.py",
            "claudia_advanced_model_upgrade.py",
            "claudia_orchestrator_v2.py"
        ]

        # Archive candidates (redundant/old versions)
        archive_files = [
            "cyberpunk_dashboard.py",
            "jupiter_ultimate_dashboard_v4.py",
            "oracle_agi_v*.py",
            "ultimate_mcp_resource_manager_v4.py",
            "*_launcher*.py",
            "*_temp*.py",
            "*_test*.py"
        ]

        # Documentation files
        doc_files = [
            "README*.md",
            "ARCHITECTURE*.md",
            "COMPLETE_SYSTEM_OVERVIEW.md",
            "*_DOCUMENTATION.md",
            "*_REPORT.md"
        ]

        # Setup/utility scripts
        script_files = [
            "install_*.py",
            "setup_*.py",
            "check_*.py",
            "configure_*.py",
            "launch_*.py"
        ]

        return {
            "core": core_files,
            "claudia": claudia_files,
            "archive": archive_files,
            "docs": doc_files,
            "scripts": script_files
        }

    def create_backup(self):
        """Create backup of current state"""
        logger.info("💾 Creating backup of current state...")

        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        self.backup_dir.mkdir()

        # Backup all Python and Markdown files
        for pattern in ["*.py", "*.md", "*.json", "*.yaml", "*.yml"]:
            for file in self.project_root.glob(pattern):
                if file.is_file() and not str(file).startswith(str(self.backup_dir)):
                    shutil.copy2(file, self.backup_dir / file.name)

        logger.info(f"[OK] Backup created at {self.backup_dir}")

    def move_files_to_organization(self):
        """Move files to their organized locations"""
        logger.info("[PACKAGE] Moving files to organized structure...")

        categories = self.categorize_files()

        # Move core files
        for file_pattern in categories["core"]:
            for file_path in self.project_root.glob(file_pattern):
                if file_path.is_file():
                    dest = self.project_root / "core" / file_path.name
                    shutil.move(str(file_path), str(dest))
                    self.organization_log.append(f"Moved {file_path.name} to core/")

        # Move Claudia files
        for file_pattern in categories["claudia"]:
            for file_path in self.project_root.glob(file_pattern):
                if file_path.is_file():
                    dest = self.project_root / "claudia" / "scripts" / file_path.name
                    shutil.move(str(file_path), str(dest))
                    self.organization_log.append(f"Moved {file_path.name} to claudia/scripts/")

        # Archive old files
        for file_pattern in categories["archive"]:
            for file_path in self.project_root.glob(file_pattern):
                if file_path.is_file():
                    dest = self.project_root / "archive" / "legacy_scripts" / file_path.name
                    shutil.move(str(file_path), str(dest))
                    self.organization_log.append(f"Archived {file_path.name}")

        # Move documentation
        for file_pattern in categories["docs"]:
            for file_path in self.project_root.glob(file_pattern):
                if file_path.is_file():
                    dest = self.project_root / "docs" / file_path.name
                    shutil.move(str(file_path), str(dest))
                    self.organization_log.append(f"Moved {file_path.name} to docs/")

        # Move scripts
        for file_pattern in categories["scripts"]:
            for file_path in self.project_root.glob(file_pattern):
                if file_path.is_file():
                    dest = self.project_root / "scripts" / "setup" / file_path.name
                    shutil.move(str(file_path), str(dest))
                    self.organization_log.append(f"Moved {file_path.name} to scripts/setup/")

    def create_new_main_readme(self):
        """Create a consolidated main README"""
        logger.info("[MEMO] Creating new main README...")

        readme_content = '''# MCPVotsAGI - Advanced AI Dashboard System

## [ROCKET] Overview

MCPVotsAGI is a production-ready AI dashboard system that combines:
- **Unified AGI Dashboard** with real-time monitoring
- **Claudia AI** with MCP (Model Context Protocol) integration
- **Jupiter DEX** trading integration
- **Knowledge Graph** and memory systems
- **Reinforcement Learning** capabilities

## 🏗️ Architecture

```
MCPVotsAGI/
├── [FOLDER] core/                    # Production core systems
├── [FOLDER] claudia/                 # AI agent system
├── [FOLDER] tools/                   # MCP and external tools
├── [FOLDER] dashboards/              # Specialized dashboards
├── [FOLDER] docs/                    # Documentation
├── [FOLDER] scripts/                 # Utility scripts
└── [FOLDER] config/                  # Configuration files
```

## 🚦 Quick Start

### Prerequisites
- Python 3.9+
- Ollama with DeepSeek-R1 model
- Node.js (for some components)

### Installation
```bash
# Clone and setup
git clone <repository>
cd MCPVotsAGI

# Install dependencies
pip install -r requirements.txt

# Run the unified dashboard
python core/unified_agi_dashboard.py
```

### Access Points
- **Main Dashboard**: http://localhost:8900
- **API Backend**: http://localhost:8889
- **Ollama AI**: http://localhost:11434

## 🧠 Claudia AI System

Claudia is the AI agent system with:
- **MCP Integration**: Memory, GitHub, FileSystem, Browser, Search
- **Multi-Model Support**: DeepSeek-R1, Qwen2.5-Coder, Llama3.2
- **Context-Aware Analysis**: Uses knowledge graph for insights
- **Async Architecture**: High-performance concurrent processing

## 📊 Features

### Real-Time Dashboard
- Jupiter DEX trading monitoring
- System performance metrics
- Network monitoring
- AI-powered analysis and recommendations

### MCP Tools Integration
- **Memory**: Knowledge graph and context storage
- **GitHub**: Repository management and code analysis
- **FileSystem**: Workspace analysis and operations
- **Browser**: Web automation and research
- **Search**: Real-time information gathering

### Trading Integration
- Jupiter DEX API integration
- Real-time price monitoring
- AI-powered trading insights
- Risk assessment

## [WRENCH] Configuration

### Environment Setup
```bash
# Ollama models
ollama pull deepseek-r1:latest
ollama pull qwen2.5-coder:latest
ollama pull llama3.2:3b
```

### Configuration Files
- `config/production.yaml` - Production settings
- `config/development.yaml` - Development settings
- `claudia/config/async_config.yaml` - AI agent configuration

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Setup Guide](docs/SETUP.md)
- [Claudia AI System](claudia/docs/)

## [ROCKET] Deployment

### Production
```bash
# Start all services
python core/unified_agi_dashboard.py
```

### Development
```bash
# Run in development mode
python scripts/setup/dev_setup.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## [MEMO] License

MIT License - see LICENSE file for details

## 🆘 Support

- Create an issue for bugs
- Join discussions for questions
- Check docs/ for detailed information

---

**Built with ❤️ for advanced AI integration**
'''

        readme_path = self.project_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        logger.info("[OK] New README.md created")

    def create_organization_report(self):
        """Create a report of the organization process"""
        logger.info("[CLIPBOARD] Creating organization report...")

        report = {
            "organization_date": datetime.now().isoformat(),
            "files_moved": len(self.organization_log),
            "changes": self.organization_log,
            "new_structure": {
                "core_files": len(list((self.project_root / "core").glob("*.py"))),
                "claudia_files": len(list((self.project_root / "claudia" / "scripts").glob("*.py"))),
                "archived_files": len(list((self.project_root / "archive").rglob("*.py"))),
                "doc_files": len(list((self.project_root / "docs").glob("*.md")))
            }
        }

        with open(self.project_root / "ORGANIZATION_REPORT.json", 'w') as f:
            json.dump(report, f, indent=2)

        logger.info("[OK] Organization report created")
        return report

    def organize_project(self):
        """Main organization workflow"""
        logger.info("🎯 Starting MCPVotsAGI project organization...")

        # Step 1: Analyze current structure
        analysis = self.analyze_current_structure()

        # Step 2: Create backup
        self.create_backup()

        # Step 3: Create new directory structure
        self.create_directory_structure()

        # Step 4: Move files to organized structure
        self.move_files_to_organization()

        # Step 5: Create new README
        self.create_new_main_readme()

        # Step 6: Create organization report
        report = self.create_organization_report()

        logger.info("🎉 Project organization completed!")
        logger.info(f"📊 Moved {report['files_moved']} files")
        logger.info(f"💾 Backup available at: {self.backup_dir}")

        return report

def main():
    """Main execution function"""
    print("[ROCKET] MCPVotsAGI Project Organizer")
    print("="*50)

    organizer = MCPVotsAGIOrganizer()

    # Confirm before proceeding
    response = input("[WARN]  This will reorganize your project structure. Continue? (y/N): ")
    if response.lower() != 'y':
        print("[FAIL] Organization cancelled")
        return

    try:
        report = organizer.organize_project()

        print("\n[OK] Organization completed successfully!")
        print(f"📊 Files moved: {report['files_moved']}")
        print(f"💾 Backup created: backup_before_organization/")
        print(f"[CLIPBOARD] Report saved: ORGANIZATION_REPORT.json")
        print("\n🎯 Next steps:")
        print("1. Test the reorganized system")
        print("2. Update any import paths if needed")
        print("3. Commit changes to git")

    except Exception as e:
        logger.error(f"[FAIL] Organization failed: {e}")
        print(f"\n💾 Backup available at: backup_before_organization/")
        raise

if __name__ == "__main__":
    main()
