# MCPVotsAGI SDK

MCP integration SDK with agent orchestration, persistent memory, AI reasoning, and Darwin Gödel Machine evolution.

## Install

```bash
pip install mcpvotsagi
```

With optional features:

```bash
pip install mcpvotsagi[trading]   # Solana trading support
pip install mcpvotsagi[ai]        # OpenAI integration
pip install mcpvotsagi[all]       # Everything
```

## Quick Start

```python
import asyncio
from mcpvotsagi import MCPVotsAGI, MCPVotsAGIConfig

async def main():
    config = MCPVotsAGIConfig(
        redis_host="localhost",
        redis_password="your-password",
    )

    async with MCPVotsAGI(config) as agi:
        # Store and retrieve memories
        await agi.memory.store("trade_1", {"action": "buy", "asset": "SOL", "price": 185.50})
        memory = await agi.memory.retrieve("trade_1")
        print(memory)

        # Search memories by category
        trades = await agi.memory.search_memories(category="trading")

        # AI reasoning
        result = await agi.reason("Should I buy SOL at current price?", task_type="trading")
        print(result)

        # System status
        status = await agi.status()
        print(status)

asyncio.run(main())
```

## Configuration

All settings can be passed via `MCPVotsAGIConfig` or environment variables:

| Env Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | localhost | Redis host |
| `REDIS_PORT` | 6379 | Redis port |
| `REDIS_PASSWORD` | (empty) | Redis password |
| `A2A_PORT` | 8001 | A2A gateway port |
| `DEEPSEEK_PORT` | 3003 | DeepSeek MCP server port |
| `OLLAMA_HOST` | http://localhost:11434 | Ollama API host |
| `LOG_LEVEL` | INFO | Logging level |

## API Reference

### `MCPVotsAGI`

Main SDK client. Use as async context manager.

```python
async with MCPVotsAGI() as agi:
    agi.memory    # EnhancedMCPMemoryServer
    agi.a2a       # A2AProtocolGateway
    agi.dgm       # UnifiedDGMServer
```

**Methods:**
- `await agi.start()` — Initialize all services
- `await agi.stop()` — Shut down all services
- `await agi.reason(prompt, task_type="general")` — AI reasoning
- `await agi.status()` — System health check

### `EnhancedMCPMemoryServer`

Persistent key-value memory with Redis backend.

```python
# Store
memory_id = await agi.memory.store("key", {"data": "value"}, category="trades")

# Retrieve
entry = await agi.memory.retrieve("key")

# Search by category
results = await agi.memory.search_memories(category="trades", limit=50)

# Delete
await agi.memory.delete("key")

# Stats
stats = await agi.memory.get_stats()
```

### `A2AProtocolGateway`

Agent-to-agent communication via WebSocket.

```python
gateway = agi.a2a
await gateway.start()

# Register an agent
await gateway.agent_registry.register_agent(AgentInfo(...))

# Discover agents
agents = await gateway.agent_registry.discover_agents(capability="trading")
```

### `UnifiedDGMServer`

Darwin Gödel Machine evolution engine for self-improving programs.

```python
dgm = agi.dgm
result = await dgm.evolve_program(program_id="strategy_1")
```

## Architecture

```
┌──────────────────────────────────┐
│         MCPVotsAGI Client        │
├──────────┬──────────┬────────────┤
│  Memory  │   A2A    │    DGM     │
│ (Redis)  │ (WS:8001)│ (Evolution)│
├──────────┴──────────┴────────────┤
│          MCP Servers              │
│  ┌──────────┐  ┌───────────────┐ │
│  │ DeepSeek │  │   OpenCTI     │ │
│  │ (Ollama) │  │ (Threat Intel)│ │
│  └──────────┘  └───────────────┘ │
└──────────────────────────────────┘
```

## Development

```bash
git clone https://github.com/MCPVOT/mcpvotsagi.git
cd mcpvotsagi
pip install -e ".[dev]"

# Lint
ruff check src/mcpvotsagi/

# Test
pytest

# Type check
mypy src/mcpvotsagi/
```

## License

MIT
