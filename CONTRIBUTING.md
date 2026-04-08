# Contributing to MCPVotsAGI

Thank you for your interest in contributing! This guide covers everything you need to get started.

## Quick Start

```bash
# Clone and install in dev mode
git clone https://github.com/MCPVOT/mcpvotsagi.git
cd mcpvotsagi
pip install -e ".[dev]"

# Run linting
ruff check src/
ruff format src/

# Run type checking
mypy src/

# Run tests (requires Redis on localhost:6379)
pytest -v
```

## Project Structure

```
src/mcpvotsagi/
  __init__.py          # Public API + version
  client.py            # MCPVotsAGI async client
  config.py            # Configuration from env vars
  exceptions.py        # Custom exceptions
  core/
    a2a.py             # Agent-to-agent communication
    dgm.py             # Darwin Gödel Machine evolution
    memory.py          # Redis-backed persistent memory
    mcp_servers.py     # MCP server manager
    orchestrator.py    # Process orchestration
  servers/
    deepseek.py        # AI reasoning via Ollama
    opencti.py         # OpenCTI MCP server
```

## Code Style

- Python 3.11+ with modern type hints (`X | None` not `Optional[X]`, `list[X]` not `List[X]`)
- `from __future__ import annotations` at the top of every module
- Use `logging` — never `print()` in library code
- Line length: 120 characters
- All public functions must have type annotations

## Commit Messages

Use conventional commits:
- `fix: ...` — bug fixes
- `feat: ...` — new features
- `refactor: ...` — code reorganization
- `docs: ...` — documentation
- `test: ...` — test additions/changes

## Pull Requests

1. Fork the repo and create a feature branch
2. Make your changes with tests
3. Ensure `ruff check`, `mypy`, and `pytest` all pass
4. Open a PR against `main` with a clear description

## Adding New MCP Servers

Add server config to `core/mcp_servers.py` in the `mcp_config` dict. Follow the existing pattern with `port`, `command`, and `description` fields.

## Reporting Issues

Open a GitHub issue with:
- Python version (`python --version`)
- Package version (`pip show mcpvotsagi`)
- Minimal reproduction steps
