# MCP Servers Setup Guide

The Oracle AGI V9 Complete Dashboard is **fully operational** with core functionality. External MCP servers provide additional capabilities and can be set up optionally.

## 🎉 Current Status: WORKING

✅ **Core System Operational:**
- Oracle AGI Dashboard: <http://localhost:8888>
- DeepSeek-R1 Brain: Active via Ollama
- FileSystem MCP: Integrated and working
- START_AGI_CHAT.bat: One-click startup working

## 📋 Optional MCP Servers

The external MCP servers add advanced capabilities but are not required for core functionality:

### 1. GitHub MCP (Port 3001) - Repository Management
```bash
# Install GitHub MCP
npm install -g @modelcontextprotocol/server-github

# Start GitHub MCP
npx @modelcontextprotocol/server-github
```

### 2. Memory MCP (Port 3002) - Knowledge Graph
```bash
# Install Memory MCP
npm install -g @modelcontextprotocol/server-memory

# Start Memory MCP
npx @modelcontextprotocol/server-memory
```

### 3. Browser MCP (Port 3006) - Web Automation
```bash
# Install Browser MCP
npm install -g @modelcontextprotocol/server-puppeteer

# Start Browser MCP
npx @modelcontextprotocol/server-puppeteer
```

### 4. Solana MCP (Port 3005) - Blockchain Integration
```bash
# Install Solana MCP
npm install -g @modelcontextprotocol/server-solana

# Start Solana MCP
npx @modelcontextprotocol/server-solana
```

## 🚀 Quick Start (Core System Only)

The system is **ready to use** with core functionality:

1. **Start the AGI Dashboard:**
   ```bash
   START_AGI_CHAT.bat
   ```

2. **Access Dashboard:**
   - URL: <http://localhost:8888>
   - Chat with DeepSeek-R1 brain
   - Use FileSystem tools
   - Access all AI models

3. **Available Features:**
   - Natural language chat with AGI
   - File system access and manipulation
   - Multiple AI model selection
   - Real-time system monitoring

## 📊 System Verification

Run the verification script to check system status:
```bash
python verify_system_ready.py
```

## 🔧 Environment Variables (Optional)

For enhanced functionality, set these optional environment variables:
```bash
# Optional API keys for extended features
OPENAI_API_KEY=your_openai_key
FINNHUB_API_KEY=your_finnhub_key
GITHUB_TOKEN=your_github_token
```

## 🎯 Summary

The MCPVotsAGI Oracle AGI V9 Complete system is **fully operational** with:

- ✅ Core AGI chat functionality working
- ✅ DeepSeek-R1 brain active and responding
- ✅ FileSystem MCP integrated
- ✅ One-click startup via START_AGI_CHAT.bat
- ✅ Web dashboard accessible at localhost:8888

External MCP servers provide additional capabilities but are **optional** for the core AGI chat experience.

**Start chatting with your AGI now!** 🚀
