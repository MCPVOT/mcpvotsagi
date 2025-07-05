#!/bin/bash
set -e

echo "🎯 Starting MCPVotsAGI services..."

# Start Redis
echo "🔴 Starting Redis..."
sudo service redis-server start

# Start PostgreSQL
echo "🐘 Starting PostgreSQL..."
sudo service postgresql start

# Start IPFS daemon in background
echo "🌐 Starting IPFS daemon..."
ipfs init --profile server 2>/dev/null || true
nohup ipfs daemon > logs/ipfs.log 2>&1 &

# Start Ollama service
echo "🧠 Starting Ollama service..."
nohup ollama serve > logs/ollama.log 2>&1 &

# Wait for Ollama to be ready
sleep 5

# Check if DeepSeek model exists
echo "🔍 Checking for DeepSeek-R1 model..."
if ! ollama list | grep -q "DeepSeek-R1"; then
    echo "📥 DeepSeek-R1 not found. Pull it with:"
    echo "   ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
fi

# Start MCP servers
echo "🔗 Starting MCP servers..."

# FileSystem MCP
nohup npx @modelcontextprotocol/server-filesystem > logs/mcp_filesystem.log 2>&1 &

# Memory MCP (port 3002)
nohup npx @modelcontextprotocol/server-memory --port 3002 > logs/mcp_memory.log 2>&1 &

# Start n8n workflow automation
echo "🔄 Starting n8n..."
nohup n8n start --port 5678 > logs/n8n.log 2>&1 &

# Show status
echo ""
echo "✅ Services started!"
echo ""
echo "📊 Service Status:"
echo "  - Redis: $(sudo service redis-server status | grep -o 'running' || echo 'stopped')"
echo "  - PostgreSQL: $(sudo service postgresql status | grep -o 'running' || echo 'stopped')"
echo "  - IPFS: Check http://localhost:5001/webui"
echo "  - Ollama: Check http://localhost:11434"
echo "  - n8n: Check http://localhost:5678"
echo ""
echo "🚀 Ready to start MCPVotsAGI!"
echo "   Run: python START_ULTIMATE_AGI_WITH_CLAUDIA.py"