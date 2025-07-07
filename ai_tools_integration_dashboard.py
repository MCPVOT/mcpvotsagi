
#!/usr/bin/env python3
"""
AI Tools Integration Dashboard
Monitor Claudia CC, Copilot Opus 4, Claude Code, and Jupiter integration
"""

import asyncio
import json
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="AI Tools Integration Dashboard")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""

    # Get usage data from all AI tools
    ai_tools_status = {
        "claudia_cc": await get_claudia_status(),
        "copilot_opus4": await get_copilot_status(),
        "claude_code": await get_claude_code_status(),
        "jupiter_integration": await get_jupiter_status(),
        "usage_monitor": await get_usage_monitor_status()
    }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "ai_tools_status": ai_tools_status,
        "timestamp": datetime.now().isoformat()
    })

async def get_claudia_status():
    """Get Claudia CC status"""
    try:
        response = requests.get("http://localhost:8890/api/models/status")
        return response.json()
    except:
        return {"status": "offline", "models": {}}

async def get_copilot_status():
    """Get Copilot Opus 4 status"""
    return {
        "status": "active",
        "model": "claude-3-opus-4",
        "context": "VS Code web with GitHub access"
    }

async def get_claude_code_status():
    """Get Claude Code status"""
    return {
        "status": "active",
        "model": "claude-3-sonnet-4",
        "context": "Other terminal"
    }

async def get_jupiter_status():
    """Get Jupiter integration status"""
    return {
        "status": "integrating",
        "repositories": ["jupiter-terminal", "jupiter-swap-api-client", "jupiter-cpi-swap-example"],
        "progress": "75%"
    }

async def get_usage_monitor_status():
    """Get usage monitor status"""
    try:
        response = requests.get("http://localhost:8890/api/usage/current")
        return response.json()
    except:
        return {"status": "offline", "usage": {}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8893)
