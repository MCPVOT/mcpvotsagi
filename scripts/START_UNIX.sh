#!/bin/bash
echo "🚀 ==============================================================="
echo "   MCPVotsAGI - Ultimate AGI System v2.0 - Unix Launcher"
echo "🚀 ==============================================================="
echo ""
echo "🧠 DeepSeek-R1 Model: unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
echo "🔗 MCP Tools: FileSystem, GitHub, Memory, Browser, Brave Search"
echo "📚 Context7: Real-time documentation enrichment"
echo "🎨 Claudia: Agent orchestration platform"
echo "🌐 IPFS: Decentralized storage"
echo "💹 Trading: Real-time market analysis and execution"
echo ""
echo "🎯 THE ONE AND ONLY consolidated AGI portal"
echo ""

# Check if Python is installed
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    echo "Please install Python 3.9+ from https://python.org/downloads/"
    exit 1
fi
echo "✅ Python3 is installed"

# Check if Ollama is installed
echo "🔍 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo "Please install Ollama from https://ollama.com/"
    exit 1
fi
echo "✅ Ollama is installed"

# Check if Node.js is installed
echo "🔍 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js is installed"

# Configure the system
echo "🔧 Configuring system..."
python3 CONFIGURE_SYSTEM.py
if [ $? -ne 0 ]; then
    echo "❌ System configuration failed"
    exit 1
fi

# Install Python dependencies
echo "🔧 Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️ .env file not found"
    echo "Copying template..."
    cp .env.template .env
    echo ""
    echo "📝 Please edit .env file with your API keys before continuing"
    echo "Press Enter to continue anyway..."
    read
fi

# Launch the system
echo ""
echo "🚀 ==============================================================="
echo "   LAUNCHING ULTIMATE AGI SYSTEM"
echo "🚀 ==============================================================="
echo ""
echo "🌐 Dashboard will be available at: http://localhost:8888"
echo "🛑 Press Ctrl+C to stop the system"
echo ""

python3 LAUNCH_ULTIMATE_AGI_DEEPSEEK.py

echo ""
echo "👋 Ultimate AGI System stopped"
