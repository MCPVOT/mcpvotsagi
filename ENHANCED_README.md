# Enhanced AGI System v2.0

🚀 **Modern UI Dashboard with Advanced Chat Interface**

## Overview

The Enhanced AGI System v2.0 is a complete redesign of the original MCPVotsAGI dashboard with:

- **Modern React-based frontend** with professional UI components
- **Real-time system monitoring** and metrics
- **Enhanced chat experience** with typing indicators and metadata
- **Responsive design** that works on all devices
- **Professional cyberpunk theme** with smooth animations
- **Advanced WebSocket communication** with better error handling

## Features

### 🎨 UI/UX Enhancements
- Modern React components with professional styling
- Cyberpunk-themed design with neon colors and gradients
- Responsive grid layout that adapts to screen size
- Enhanced chat bubbles with timestamps and metadata
- Typing indicators with animated dots
- Smooth animations and transitions

### 🔧 Technical Improvements
- Separate port (8889) to avoid conflicts with original system
- Enhanced database schema with performance metrics
- Real-time WebSocket communication with connection management
- Advanced system metrics collection (CPU, Memory, Connections)
- Improved error handling and logging
- Better message history management
- Token counting and response time tracking

### 💬 Chat Interface
- Modern chat bubbles with user/assistant differentiation
- Real-time typing indicators with animation
- Message timestamps and metadata display
- Auto-scroll to latest messages
- Textarea input with auto-resize
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Enhanced model selector with descriptions

### 📊 Dashboard Components
- Three-column responsive layout
- Real-time system metrics sidebar
- Professional header with status badges
- Advanced tools panel with MCP integrations
- Model status indicators
- Live connection count display
- CPU and Memory usage monitoring

## Quick Start

### 🚀 Launch the Enhanced System

```bash
# Using the launcher (recommended)
python LAUNCH_ENHANCED_AGI.py

# Or run directly
python src/core/ENHANCED_AGI_SYSTEM.py
```

### 🌐 Access the Dashboard

Open your browser to: **http://localhost:8889**

### 📊 View Enhancement Report

```bash
python ENHANCEMENT_REPORT.py
```

## System Requirements

- Python 3.8+
- Required packages (auto-installed):
  - aiohttp
  - psutil
  - numpy
  - pandas
  - pyyaml
  - requests
  - ipfshttpclient
- Ollama (for DeepSeek-R1 model)

## Architecture

```
Enhanced AGI System v2.0
├── Frontend (React)
│   ├── Modern UI Components
│   ├── Real-time WebSocket
│   ├── Responsive Design
│   └── Professional Styling
├── Backend (Python/aiohttp)
│   ├── Enhanced API Endpoints
│   ├── WebSocket Management
│   ├── System Metrics
│   └── Database Operations
└── Integrations
    ├── DeepSeek-R1 Model
    ├── Claudia Bridge
    ├── Context7 Documentation
    └── MCP Tools Suite
```

## Comparison with Original

| Feature | Original | Enhanced |
|---------|----------|----------|
| UI Framework | Basic HTML/CSS/JS | Modern React |
| Design System | Simple | Cyberpunk Theme |
| Responsive | Fixed Layout | Mobile-First |
| Metrics | Basic | Real-time |
| Chat UX | Simple | Advanced |
| WebSocket | Basic | Enhanced |
| Port | 8888 | 8889 |

## API Endpoints

### Chat
- `POST /api/chat` - Send chat message
- `POST /api/chat/stream` - Streaming chat (future)
- `GET /api/history` - Get chat history
- `POST /api/clear-history` - Clear chat history

### System
- `GET /api/status` - System status
- `GET /api/metrics` - Real-time metrics
- `GET /api/models` - Available models
- `POST /api/upload` - File upload

### WebSocket
- `GET /ws` - WebSocket connection
- Messages: `chat`, `metrics`, `status`

## Configuration

The system automatically loads configuration from:
- `config/unified_system_config.yaml`
- `config/unified_agi_portal.yaml`
- `config/mcp_settings.json`

## Development

### File Structure
```
src/core/
├── ENHANCED_AGI_SYSTEM.py      # Main enhanced system
├── ULTIMATE_AGI_SYSTEM.py      # Original system
├── claudia_integration_bridge.py
└── CONTEXT7_INTEGRATION.py

LAUNCH_ENHANCED_AGI.py           # Enhanced launcher
ENHANCEMENT_REPORT.py            # Comparison report
```

### Running Both Systems
Both the original (port 8888) and enhanced (port 8889) systems can run simultaneously for comparison.

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Enhanced system uses port 8889 by default
   - Original system uses port 8888
   - Both can run simultaneously

2. **Ollama Not Running**
   - Launcher automatically starts Ollama
   - Ensure Ollama is installed: `curl -fsSL https://ollama.ai/install.sh | sh`

3. **Dependencies Missing**
   - Launcher automatically installs required packages
   - Or run: `pip install -r requirements.txt`

4. **WebSocket Connection Issues**
   - Check firewall settings
   - Ensure port 8889 is accessible
   - Browser console will show connection status

## Future Enhancements

- [ ] Streaming chat responses
- [ ] Multiple model support (Gemini 2.5)
- [ ] Advanced tool integration
- [ ] File upload and processing
- [ ] Chat export functionality
- [ ] Theme customization
- [ ] Plugin system
- [ ] Mobile app companion

## License

This project is part of the MCPVotsAGI system and follows the same licensing terms.

## Support

For issues or questions about the Enhanced AGI System:
1. Check the enhancement report: `python ENHANCEMENT_REPORT.py`
2. Review the original system documentation
3. Check WebSocket connection in browser console
4. Verify Ollama is running: `ollama list`

---

🎯 **The Enhanced AGI System v2.0 - Where AI meets Modern Design**
