#!/bin/bash
set -e

echo "🚀 Setting up MCPVotsAGI Development Environment..."

# Update package lists
sudo apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    htop \
    tmux \
    jq \
    redis-server \
    postgresql \
    postgresql-contrib \
    ipfs \
    ffmpeg \
    libgraphviz-dev

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

# Install requirements
if [ -f requirements_complete.txt ]; then
    pip install -r requirements_complete.txt
else
    # Core dependencies
    pip install aiohttp psutil websockets numpy pandas pyyaml requests ipfshttpclient
    
    # Memory and ML
    pip install chromadb sentence-transformers networkx scikit-learn torch transformers
    
    # Trading and blockchain
    pip install finnhub-python alpaca-trade-api ccxt python-binance web3 solana
    
    # Development tools
    pip install black flake8 mypy pytest pytest-asyncio pytest-cov
    
    # Visualization
    pip install matplotlib plotly streamlit gradio
    
    # AI/LLM
    pip install ollama langchain openai anthropic
fi

# Install Node.js global packages
echo "📦 Installing Node.js MCP servers..."
npm install -g \
    @modelcontextprotocol/server-filesystem \
    @modelcontextprotocol/server-github \
    @modelcontextprotocol/server-memory \
    @modelcontextprotocol/server-sqlite \
    @modelcontextprotocol/server-postgres \
    @agentdeskai/browser-tools-mcp \
    @anthropic/mcp-server-obsidian \
    mcp-server-fetch

# Install n8n globally
echo "🔄 Installing n8n workflow automation..."
npm install -g n8n

# Setup Ollama
echo "🧠 Setting up Ollama..."
# Note: Ollama is installed via devcontainer feature, just need to configure
mkdir -p ~/.ollama
echo "OLLAMA_HOST=0.0.0.0:11434" > ~/.ollama/env

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p memory knowledge rl_models trading_data agent_swarm ipfs_data logs backups mcp_configs dashboards

# Initialize databases
echo "🗄️ Initializing databases..."
python3 -c "
import sqlite3
import os

# Create memory database
conn = sqlite3.connect('memory/ultimate_memory.db')
conn.execute('''CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    embedding BLOB,
    importance REAL DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    tags TEXT
)''')
conn.commit()
conn.close()

print('✅ Database initialized')
"

# Setup PostgreSQL if needed
echo "🐘 Setting up PostgreSQL..."
sudo service postgresql start
sudo -u postgres createuser -s codespace || true
sudo -u postgres createdb mcpvotsagi || true

# Setup Redis
echo "🔴 Setting up Redis..."
sudo service redis-server start

# Create .env file template
echo "🔐 Creating .env template..."
cat > .env.example << EOF
# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here

# Blockchain
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
PHANTOM_WALLET_ADDRESS=your_wallet_here

# Services
IPFS_GATEWAY=http://localhost:8080
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://codespace:password@localhost/mcpvotsagi

# n8n
N8N_PORT=5678
N8N_WEBHOOK_URL=http://localhost:5678/

# Ollama
OLLAMA_HOST=http://localhost:11434
DEEPSEEK_MODEL=hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
EOF

# Setup git hooks
echo "🪝 Setting up git hooks..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run linting before commit
python -m black --check src/
python -m flake8 src/
EOF
chmod +x .git/hooks/pre-commit

# Download DeepSeek model info
echo "📥 Preparing for DeepSeek-R1 model..."
cat > models/deepseek_setup.sh << 'EOF'
#!/bin/bash
# Run this after Ollama is started
ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
EOF
chmod +x models/deepseek_setup.sh

echo "✅ Post-create setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy .env.example to .env and fill in your API keys"
echo "2. Start Ollama: ollama serve"
echo "3. Pull DeepSeek model: ./models/deepseek_setup.sh"
echo "4. Start the system: python START_ULTIMATE_AGI_WITH_CLAUDIA.py"