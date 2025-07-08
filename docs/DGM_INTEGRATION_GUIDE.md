# DGM Integration Guide

## Overview
The Darwin Gödel Machine (DGM) is a self-improving AI system integrated into MCPVotsAGI.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install websockets aiohttp streamlit plotly pandas numpy
   ```

2. **Start Redis (Optional but recommended)**
   ```bash
   sudo apt install redis-server
   sudo service redis-server start
   ```

3. **Launch DGM System**
   ```bash
   python scripts/launch_dgm_system.py
   ```

4. **Access Dashboard**
   Open http://localhost:8501 in your browser

## Architecture

### Components
- **Unified DGM Server**: Core evolution engine (port 8013)
- **DGM Dashboard**: Monitoring and control interface (port 8501)
- **A2A Integration**: Agent-to-agent communication
- **MCP Tools**: Model Context Protocol integration

### Features
- Program evolution using genetic algorithms
- Trading strategy generation and optimization
- Self-modification capabilities
- Real-time monitoring
- Redis persistence (with in-memory fallback)

## API Reference

### WebSocket Methods

#### dgm/evolve_program
Evolve a program for a specific task.

```json
{
  "method": "dgm/evolve_program",
  "params": {
    "task": "Optimize neural network",
    "iterations": 100
  }
}
```

#### dgm/create_trading_strategy
Create an AI-optimized trading strategy.

```json
{
  "method": "dgm/create_trading_strategy",
  "params": {
    "name": "momentum_strategy",
    "risk_profile": "moderate",
    "market_conditions": {"volatility": "high"}
  }
}
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8013
# Kill process
kill -9 <PID>
```

### Redis Connection Failed
The system will automatically fall back to in-memory storage.

### Dashboard Not Loading
Ensure Streamlit is installed: `pip install streamlit`

## Advanced Usage

### Custom Evolution Algorithms
Extend the `UnifiedDGMServer` class and override `_run_evolution()`.

### A2A Integration
Register DGM as an agent in your A2A network for inter-agent collaboration.

## Performance Tuning

- Increase population size for better evolution results
- Use Redis for persistence in production
- Monitor resource usage via dashboard

## Support

For issues or questions:
- Check logs in the terminal
- Monitor dashboard metrics
- Review error messages in WebSocket responses
