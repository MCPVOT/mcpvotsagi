#!/usr/bin/env python3
"""
MCPVotsAGI System Configuration and Setup
=========================================
Ensures all components are properly configured for the Ultimate AGI System
"""

import os
import json
import yaml
import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPVotsAGIConfigurator:
    """Configures the entire MCPVotsAGI system"""

    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.config_dir = self.workspace_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        # DeepSeek-R1 model configuration
        self.deepseek_config = {
            "preferred_model": "unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL",
            "model_id": "2cfa2d3c7a64",
            "fallback_models": [
                "deepseek-r1",
                "deepseek-r1:latest"
            ],
            "timeout": 1200,
            "max_tokens": 4096
        }

        # MCP server configuration
        self.mcp_config = {
            "servers": [
                {
                    "name": "filesystem",
                    "port": 3000,
                    "path": "tools/mcp-filesystem",
                    "capabilities": ["read", "write", "list", "search"]
                },
                {
                    "name": "github",
                    "port": 3001,
                    "path": "tools/mcp-github",
                    "capabilities": ["repositories", "issues", "pull_requests"]
                },
                {
                    "name": "memory",
                    "port": 3002,
                    "path": "tools/mcp-memory",
                    "capabilities": ["knowledge_graph", "entities", "relations"]
                },
                {
                    "name": "browser",
                    "port": 3003,
                    "path": "tools/mcp-browser",
                    "capabilities": ["navigate", "click", "type", "screenshot"]
                },
                {
                    "name": "brave-search",
                    "port": 3004,
                    "path": "tools/mcp-brave-search",
                    "capabilities": ["web_search", "local_search"]
                }
            ]
        }

        # Context7 configuration
        self.context7_config = {
            "port": 3001,
            "path": "tools/context7",
            "capabilities": ["documentation", "library_detection", "code_context"],
            "cache_ttl": 3600
        }

        # Claudia configuration
        self.claudia_config = {
            "path": "claudia",
            "capabilities": ["agent_orchestration", "gui_automation", "workflow_management"]
        }

        # System configuration
        self.system_config = {
            "name": "Ultimate AGI System",
            "version": "2.0.0",
            "port": 8888,
            "host": "0.0.0.0",
            "database": "ultimate_agi.db",
            "log_level": "INFO",
            "components": {
                "deepseek": True,
                "mcp_tools": True,
                "context7": True,
                "claudia": True,
                "ipfs": True,
                "trading": True,
                "memory": True
            }
        }

    def create_unified_config(self):
        """Create unified system configuration"""
        try:
            unified_config = {
                "system": self.system_config,
                "deepseek": self.deepseek_config,
                "mcp": self.mcp_config,
                "context7": self.context7_config,
                "claudia": self.claudia_config,
                "features": {
                    "real_time_documentation": True,
                    "agent_orchestration": True,
                    "multi_model_support": True,
                    "1m_token_context": True,
                    "continuous_learning": True,
                    "browser_automation": True,
                    "trading_engine": True,
                    "ipfs_storage": True,
                    "knowledge_graph": True
                }
            }

            # Save as YAML
            config_file = self.config_dir / "unified_system_config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(unified_config, f, default_flow_style=False, indent=2)

            logger.info(f"✅ Created unified config: {config_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating unified config: {e}")
            return False

    def create_mcp_settings(self):
        """Create MCP server settings"""
        try:
            mcp_settings = {
                "mcpServers": {
                    "filesystem": {
                        "command": "node",
                        "args": ["dist/index.js"],
                        "cwd": str(self.workspace_root / "tools" / "mcp-filesystem"),
                        "env": {
                            "NODE_ENV": "production"
                        }
                    },
                    "github": {
                        "command": "node",
                        "args": ["dist/index.js"],
                        "cwd": str(self.workspace_root / "tools" / "mcp-github"),
                        "env": {
                            "NODE_ENV": "production",
                            "GITHUB_TOKEN": "${GITHUB_TOKEN}"
                        }
                    },
                    "memory": {
                        "command": "node",
                        "args": ["dist/index.js"],
                        "cwd": str(self.workspace_root / "tools" / "mcp-memory"),
                        "env": {
                            "NODE_ENV": "production"
                        }
                    },
                    "browser": {
                        "command": "node",
                        "args": ["dist/index.js"],
                        "cwd": str(self.workspace_root / "tools" / "mcp-browser"),
                        "env": {
                            "NODE_ENV": "production"
                        }
                    },
                    "brave-search": {
                        "command": "node",
                        "args": ["dist/index.js"],
                        "cwd": str(self.workspace_root / "tools" / "mcp-brave-search"),
                        "env": {
                            "NODE_ENV": "production",
                            "BRAVE_SEARCH_API_KEY": "${BRAVE_SEARCH_API_KEY}"
                        }
                    }
                }
            }

            # Save as JSON
            settings_file = self.config_dir / "mcp_settings.json"
            with open(settings_file, 'w') as f:
                json.dump(mcp_settings, f, indent=2)

            logger.info(f"✅ Created MCP settings: {settings_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating MCP settings: {e}")
            return False

    def create_environment_template(self):
        """Create environment variables template"""
        try:
            env_template = """# MCPVotsAGI Environment Configuration
# Copy this file to .env and fill in your API keys

# DeepSeek-R1 Model Configuration
DEEPSEEK_MODEL=unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
DEEPSEEK_MODEL_ID=2cfa2d3c7a64

# API Keys
GITHUB_TOKEN=your_github_token_here
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here
OPENAI_API_KEY=your_openai_api_key_here

# Trading Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
TRADING_MODE=paper  # paper or live
RISK_LIMIT=0.02

# System Configuration
LOG_LEVEL=INFO
DEBUG_MODE=false
ENABLE_TRADING=true
ENABLE_IPFS=true
ENABLE_CONTEXT7=true
ENABLE_CLAUDIA=true

# Database
DATABASE_URL=sqlite:///ultimate_agi.db

# Server Configuration
HOST=0.0.0.0
PORT=8888
"""

            env_file = self.workspace_root / ".env.template"
            with open(env_file, 'w') as f:
                f.write(env_template)

            logger.info(f"✅ Created environment template: {env_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating environment template: {e}")
            return False

    def create_startup_scripts(self):
        """Create platform-specific startup scripts"""
        try:
            # Windows batch script
            windows_script = """@echo off
echo 🚀 Starting Ultimate AGI System on Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Ollama is installed
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not installed
    echo Please install Ollama from https://ollama.com/
    pause
    exit /b 1
)

REM Install dependencies
echo 🔧 Installing dependencies...
pip install -r requirements.txt

REM Launch the system
echo 🚀 Launching Ultimate AGI System...
python LAUNCH_ULTIMATE_AGI_DEEPSEEK.py

pause
"""

            windows_file = self.workspace_root / "START_WINDOWS.bat"
            with open(windows_file, 'w') as f:
                f.write(windows_script)

            # Linux/Mac shell script
            unix_script = """#!/bin/bash
echo "🚀 Starting Ultimate AGI System on Unix..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo "Please install Ollama from https://ollama.com/"
    exit 1
fi

# Install dependencies
echo "🔧 Installing dependencies..."
pip3 install -r requirements.txt

# Launch the system
echo "🚀 Launching Ultimate AGI System..."
python3 LAUNCH_ULTIMATE_AGI_DEEPSEEK.py
"""

            unix_file = self.workspace_root / "START_UNIX.sh"
            with open(unix_file, 'w') as f:
                f.write(unix_script)

            # Make Unix script executable
            os.chmod(unix_file, 0o755)

            logger.info(f"✅ Created startup scripts: {windows_file}, {unix_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating startup scripts: {e}")
            return False

    def create_requirements_file(self):
        """Create comprehensive requirements.txt"""
        try:
            requirements = """# MCPVotsAGI System Requirements
# Core dependencies
aiohttp>=3.8.0
asyncio-mqtt>=0.11.0
psutil>=5.9.0
numpy>=1.24.0
pandas>=2.0.0
pyyaml>=6.0
requests>=2.28.0
websockets>=11.0.0

# AI/ML dependencies
ipfshttpclient>=0.8.0
ollama>=0.1.0

# Trading dependencies
python-binance>=1.0.0
yfinance>=0.2.0
ccxt>=4.0.0

# Web scraping and automation
selenium>=4.0.0
beautifulsoup4>=4.11.0
playwright>=1.30.0

# Database
sqlite3
sqlalchemy>=2.0.0

# Development tools
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# Optional dependencies
jupyter>=1.0.0
matplotlib>=3.6.0
plotly>=5.0.0
streamlit>=1.28.0
fastapi>=0.100.0
uvicorn>=0.20.0
"""

            req_file = self.workspace_root / "requirements.txt"
            with open(req_file, 'w') as f:
                f.write(requirements)

            logger.info(f"✅ Created requirements file: {req_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating requirements file: {e}")
            return False

    def create_documentation(self):
        """Create comprehensive documentation"""
        try:
            readme_content = """# MCPVotsAGI - Ultimate AGI System v2.0

🚀 **The ONE and ONLY consolidated AGI portal for humans and agents**

## Features

- 🧠 **DeepSeek-R1 Brain**: Advanced reasoning with `unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL`
- 🔗 **MCP Tools**: FileSystem, GitHub, Memory, Browser, Brave Search
- 📚 **Context7**: Real-time documentation enrichment
- 🎨 **Claudia**: Agent orchestration platform
- 🌐 **IPFS**: Decentralized storage
- 💹 **Trading**: Real-time market analysis and execution
- 🔍 **Memory**: Knowledge graph and semantic search
- 🤖 **Multi-Agent**: Coordinated agent swarms

## Quick Start

### Prerequisites

1. **Python 3.9+** - [Download Python](https://python.org/downloads/)
2. **Ollama** - [Install Ollama](https://ollama.com/)
3. **Node.js 18+** - [Download Node.js](https://nodejs.org/)
4. **Git** - [Install Git](https://git-scm.com/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/MCPVotsAGI.git
   cd MCPVotsAGI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

4. **Launch the system:**
   ```bash
   # Windows
   START_WINDOWS.bat

   # Linux/Mac
   ./START_UNIX.sh

   # Or directly
   python LAUNCH_ULTIMATE_AGI_DEEPSEEK.py
   ```

### Access the System

- **Web Dashboard**: http://localhost:8888
- **API Endpoints**: http://localhost:8888/api/
- **WebSocket**: ws://localhost:8888/ws

## Configuration

### DeepSeek-R1 Model

The system uses the specific model: `unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL`

This model will be automatically downloaded on first run (may take 10-20 minutes).

### MCP Servers

The system runs multiple MCP servers:

- **FileSystem** (port 3000) - File operations
- **GitHub** (port 3001) - Repository management
- **Memory** (port 3002) - Knowledge graph
- **Browser** (port 3003) - Web automation
- **Brave Search** (port 3004) - Web search

### API Keys

Configure these in your `.env` file:

- `GITHUB_TOKEN` - GitHub API access
- `BRAVE_SEARCH_API_KEY` - Web search
- `FINNHUB_API_KEY` - Financial data
- `BINANCE_API_KEY` - Trading (optional)
- `BINANCE_SECRET` - Trading (optional)

## Usage

### Chat Interface

Access the main chat interface at http://localhost:8888

The AI has access to:
- Real-time documentation via Context7
- File system operations
- GitHub repositories
- Web browsing and search
- Trading capabilities
- Memory and knowledge graph

### API Endpoints

- `GET /api/status` - System status
- `POST /api/chat` - Chat with AI
- `POST /api/agent` - Agent requests
- `GET /api/trading` - Trading status
- `POST /api/mcp` - MCP tool requests

### WebSocket

Connect to `ws://localhost:8888/ws` for real-time updates.

## Architecture

```
MCPVotsAGI/
├── src/
│   ├── core/
│   │   ├── ULTIMATE_AGI_SYSTEM.py      # Main system
│   │   ├── CONTEXT7_INTEGRATION.py     # Documentation
│   │   └── claudia_integration_bridge.py # Agents
│   ├── trading/                        # Trading engine
│   ├── memory/                         # Knowledge graph
│   └── agents/                         # Agent implementations
├── tools/
│   ├── mcp-filesystem/                 # File MCP server
│   ├── mcp-github/                     # GitHub MCP server
│   ├── mcp-memory/                     # Memory MCP server
│   ├── mcp-browser/                    # Browser MCP server
│   ├── mcp-brave-search/               # Search MCP server
│   └── context7/                       # Context7 docs
├── claudia/                            # Claudia agent platform
├── config/                             # Configuration files
├── docs/                               # Documentation
└── LAUNCH_ULTIMATE_AGI_DEEPSEEK.py    # Main launcher
```

## Troubleshooting

### Common Issues

1. **Model Download Fails**
   - Ensure stable internet connection
   - Check available disk space (model is ~5GB)
   - Try again - downloads can resume

2. **MCP Servers Not Starting**
   - Check Node.js is installed
   - Verify port availability
   - Check server logs

3. **API Keys Not Working**
   - Verify keys are correct in `.env`
   - Check API rate limits
   - Ensure proper permissions

### Support

- Check the [documentation](docs/)
- Review system logs
- Open an issue on GitHub

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- DeepSeek for the R1 model
- Ollama for local model serving
- MCP (Model Context Protocol) for tool integration
- Context7 for documentation enrichment
- Claudia for agent orchestration
"""

            readme_file = self.workspace_root / "README_COMPLETE.md"
            with open(readme_file, 'w') as f:
                f.write(readme_content)

            logger.info(f"✅ Created comprehensive documentation: {readme_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating documentation: {e}")
            return False

    def run_configuration(self):
        """Run the complete configuration setup"""
        logger.info("🔧 Configuring MCPVotsAGI System...")

        steps = [
            ("Unified Config", self.create_unified_config),
            ("MCP Settings", self.create_mcp_settings),
            ("Environment Template", self.create_environment_template),
            ("Startup Scripts", self.create_startup_scripts),
            ("Requirements File", self.create_requirements_file),
            ("Documentation", self.create_documentation)
        ]

        success_count = 0
        for step_name, step_func in steps:
            logger.info(f"🔄 {step_name}...")
            if step_func():
                success_count += 1
            else:
                logger.error(f"❌ Failed: {step_name}")

        logger.info(f"✅ Configuration complete: {success_count}/{len(steps)} steps successful")

        if success_count == len(steps):
            logger.info("🎉 MCPVotsAGI is ready to launch!")
            return True
        else:
            logger.warning("⚠️ Some configuration steps failed - system may not work properly")
            return False

def main():
    """Main entry point"""
    try:
        configurator = MCPVotsAGIConfigurator()
        configurator.run_configuration()
    except Exception as e:
        logger.error(f"💥 Configuration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
