# ⚡ MCPVotsAGI Quick Reference

## 🚀 Quick Start Commands

```bash
# Start everything
START_ULTIMATE_AGI.bat                    # Windows
python src/core/ULTIMATE_AGI_SYSTEM.py    # Direct

# Start Ollama
ollama serve

# Pull DeepSeek-R1
ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL

# Access Dashboard
http://localhost:8888
```

## 🧠 DeepSeek-R1 Commands

```bash
# Check if model exists
ollama list

# Run model directly
ollama run hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL

# Model info
ollama show hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
```

## 📁 Key File Locations

```
C:/Workspace/MCPVotsAGI/
├── src/core/ULTIMATE_AGI_SYSTEM.py      # Main system
├── src/memory/ultimate_memory_system.py  # Memory system
├── src/rl/rl_integration.py             # RL integration
├── config/deepseek_ecosystem.json       # DeepSeek config
├── memory/ultimate_memory.db            # Memory database
└── F:/MCPVotsAGI_Data/                  # 800GB RL data
```

## 🔧 Common Operations

### Test Memory System
```python
python test_memory_system.py
```

### Verify System
```python
python VERIFY_AND_INTEGRATE_RL.py
```

### Install Dependencies
```bash
pip install -r requirements_complete.txt
```

### Start MCP Servers
```bash
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory
```

## 💬 Chat Commands

```
# In the AGI Chat interface:
/help              - Show available commands
/memory search X   - Search memories for X
/agents status     - Show agent swarm status
/rl models         - List available RL models
/tools list        - Show MCP tools
/system health     - System health check
```

## 🛠️ Troubleshooting

### Ollama Issues
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart
pkill ollama && ollama serve
```

### Port Conflicts
```python
# Change in ULTIMATE_AGI_SYSTEM.py
self.port = 8889  # Different port
```

### Memory Issues
```sql
-- Clean up database
VACUUM;
ANALYZE;
```

### F: Drive Not Found
```bash
# WSL: Mount F: drive
sudo mkdir -p /mnt/f
sudo mount -t drvfs F: /mnt/f
```

## 📊 System Monitoring

### Check Status
```bash
# System health endpoint
curl http://localhost:8888/api/health

# WebSocket status
wscat -c ws://localhost:8888/ws
```

### View Logs
```bash
# Real-time logs
tail -f logs/ultimate_agi.log

# Error logs
grep ERROR logs/ultimate_agi.log
```

### Memory Stats
```python
# In Python
from memory.ultimate_memory_system import UltimateMemorySystem
memory = UltimateMemorySystem(Path("C:/Workspace/MCPVotsAGI"))
stats = await memory.get_memory_stats()
print(stats)
```

## 🔑 Environment Variables

```env
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
FINNHUB_API_KEY=...
GITHUB_TOKEN=ghp_...
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
IPFS_GATEWAY=http://localhost:8080
```

## 🌐 API Endpoints

### REST API
```
GET  /api/health          - System health
GET  /api/status          - Detailed status
POST /api/chat            - Send chat message
GET  /api/memory/search   - Search memories
GET  /api/agents          - Agent status
GET  /api/tools           - MCP tools list
```

### WebSocket
```
ws://localhost:8888/ws
- Event: 'chat' - Chat messages
- Event: 'status' - System updates
- Event: 'metrics' - Performance data
```

## 🤖 Agent Commands

```python
# Control agents programmatically
{
    "action": "spawn_agent",
    "type": "volta",
    "task": "analyze_market"
}

{
    "action": "coordinate_swarm",
    "agents": ["volta_1", "dgm_2"],
    "objective": "trading_decision"
}
```

## 📈 Trading Operations

```python
# Execute trade
{
    "action": "trade",
    "symbol": "SOL/USDC",
    "side": "buy",
    "amount": 10,
    "strategy": "dgm_momentum"
}

# Check positions
{
    "action": "get_positions"
}
```

## 🔒 Security Commands

```bash
# Generate API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check audit logs
grep SECURITY logs/audit.log

# Verify signatures
python scripts/verify_integrity.py
```

## 🚀 Performance Tuning

```python
# Reduce memory usage
MEMORY_CACHE_SIZE = 500  # Instead of 1000

# Faster model loading
OLLAMA_KEEP_ALIVE = 3600  # Keep model in memory

# Optimize database
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
```

## 📱 Mobile Access

```bash
# Expose to network (be careful!)
python src/core/ULTIMATE_AGI_SYSTEM.py --host 0.0.0.0

# Access from mobile
http://YOUR_IP:8888
```

## 🆘 Emergency Commands

```bash
# Stop everything
pkill -f ULTIMATE_AGI_SYSTEM
pkill ollama

# Clear all data (CAUTION!)
rm -rf memory/*.db logs/*

# Reset to defaults
git checkout -- config/

# Backup critical data
cp -r memory/ memory_backup_$(date +%Y%m%d)
```

---

**Keep this reference handy for quick access to MCPVotsAGI commands!** ⚡