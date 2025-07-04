# MCP Servers Setup Guide - VS Code Integration

## Overview

This guide explains how to set up and configure MCP (Model Context Protocol) servers for the MCPVotsAGI unified AGI dashboard. The system already has FileSystem MCP working, and this guide will help you add additional MCP tools.

## Current Status

✅ **FileSystem MCP**: Already working in VS Code
✅ **MCP Servers Installed**: All core servers are installed via npm
🔧 **Configuration Needed**: VS Code MCP settings need to be configured

## Quick Setup

### 1. Core MCP Servers (Already Installed)

The following MCP servers are already installed on your system:

- `@modelcontextprotocol/server-filesystem` - File system operations
- `@modelcontextprotocol/server-memory` - Knowledge graph and memory
- `@modelcontextprotocol/server-github` - GitHub integration
- `@modelcontextprotocol/server-puppeteer` - Browser automation
- `@modelcontextprotocol/server-brave-search` - Web search

### 2. VS Code MCP Configuration

To enable these MCP servers in VS Code, you need to configure them in your VS Code settings:

1. Open VS Code Settings (Ctrl+,)
2. Search for "MCP" or "Model Context Protocol"
3. Add the following configuration:

```json
{
  "mcp.servers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "C:\\Workspace\\MCPVotsAGI"],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    },
    "browser": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-puppeteer"],
      "env": {}
    },
    "search": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your_brave_api_key_here"
      }
    }
  }
}
```

### 3. Environment Variables Setup

For full functionality, set these environment variables:

**GitHub Integration:**
```bash
# Get from: https://github.com/settings/tokens
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
```

**Brave Search (Optional):**
```bash
# Get from: https://api.search.brave.com/app/keys
BRAVE_API_KEY=your_brave_api_key_here
```

## Advanced Configuration

### Custom MCP Server Settings

You can customize the MCP server behavior by modifying the configuration:

```json
{
  "mcp.servers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "C:\\Workspace\\MCPVotsAGI",
        "--allow-write",
        "--allow-read"
      ],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_BACKEND": "sqlite",
        "MEMORY_FILE": "C:\\Workspace\\MCPVotsAGI\\data\\memory.db"
      }
    }
  }
}
```

### Workspace-Specific Settings

For MCPVotsAGI workspace, create `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "${workspaceFolder}"],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_BACKEND": "sqlite",
        "MEMORY_FILE": "${workspaceFolder}/data/agi_memory.db"
      }
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

## Testing MCP Integration

### 1. Check MCP Server Status

Use the AGI dashboard to test MCP integration:

1. Open the AGI dashboard: http://localhost:8888
2. Try these commands in the chat:
   - "List files in the current directory" (FileSystem MCP)
   - "Remember this: I am testing MCP integration" (Memory MCP)
   - "Search for Python files" (FileSystem MCP)
   - "What do you remember about me?" (Memory MCP)

### 2. Manual Testing

You can also test MCP servers manually:

```bash
# Test FileSystem MCP
npx @modelcontextprotocol/server-filesystem C:\Workspace\MCPVotsAGI

# Test Memory MCP
npx @modelcontextprotocol/server-memory

# Test GitHub MCP (requires token)
npx @modelcontextprotocol/server-github
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   - Ensure Node.js is installed: `node --version`
   - Reinstall MCP servers: `npm install -g @modelcontextprotocol/server-filesystem`

2. **Permission Errors**
   - Run VS Code as administrator
   - Check file permissions in the workspace

3. **GitHub MCP Not Working**
   - Verify your GitHub token is valid
   - Check token permissions (repo, read:user)

4. **Memory MCP Issues**
   - Ensure the data directory exists
   - Check disk space availability

### Debug Mode

Enable debug mode for MCP servers:

```json
{
  "mcp.servers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "${workspaceFolder}", "--debug"],
      "env": {
        "DEBUG": "mcp:*"
      }
    }
  }
}
```

## Integration with AGI Dashboard

The Oracle AGI V9 Complete dashboard automatically detects and integrates with available MCP servers. Once configured in VS Code:

1. **FileSystem MCP**: Already working - file operations, directory listing
2. **Memory MCP**: Knowledge persistence across chat sessions
3. **GitHub MCP**: Repository management, issue tracking, code analysis
4. **Browser MCP**: Web automation, scraping, testing
5. **Search MCP**: Web search, research assistance

## Next Steps

1. **Configure Environment Variables**: Set up GitHub and Brave API keys
2. **Test Integration**: Use the AGI dashboard to test each MCP tool
3. **Custom Configuration**: Adjust settings for your specific needs
4. **Advanced Features**: Explore additional MCP servers and capabilities

## Support

For issues or questions:
- Check the AGI dashboard logs
- Review VS Code MCP extension documentation
- Test MCP servers individually
- Consult the MCPVotsAGI documentation

---

**Status**: MCP servers are installed and ready for configuration
**Last Updated**: July 3, 2025
**Version**: 1.0
