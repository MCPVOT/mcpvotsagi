@echo off
cls
color 0A
title Oracle AGI V7 Ultimate - Complete System

echo ================================================================================
echo                      ORACLE AGI V7 ULTIMATE
echo           The Most Advanced Self-Improving AI System
echo ================================================================================
echo.
echo Starting complete ecosystem with:
echo - Oracle AGI V7 Core (Port 8888)
echo - All MCP Servers (Memory, GitHub, DeepSeek, Solana, etc.)
echo - AI Models: DeepSeek-R1, Gemini 2.5, Claude, GPT-4, Llama
echo - Knowledge Graph with Vector Store
echo - Self-Healing & Context Preservation
echo - n8n Workflow Automation
echo - Real-time Dashboard
echo.
echo ================================================================================

cd /d C:\Workspace\MCPVotsAGI

REM Check Python environment
if exist C:\Workspace\.venv\Scripts\python.exe (
    set PYTHON=C:\Workspace\.venv\Scripts\python.exe
) else (
    echo Creating virtual environment...
    python -m venv C:\Workspace\.venv
    set PYTHON=C:\Workspace\.venv\Scripts\python.exe
    
    echo Installing requirements...
    %PYTHON% -m pip install --upgrade pip
    %PYTHON% -m pip install -r requirements.txt
)

REM Start Redis for distributed state
echo Starting Redis...
start /B redis-server

REM Start IPFS for distributed storage
echo Starting IPFS...
start /B ipfs daemon

REM Start Ollama for local AI models
echo Starting Ollama...
start /B ollama serve

REM Wait for services to start
timeout /t 5 /nobreak

REM Pull required models if not present
echo Checking AI models...
ollama list | findstr "deepseek-r1" >nul || (
    echo Pulling DeepSeek-R1 model...
    ollama pull deepseek-r1:latest
)

ollama list | findstr "llama3.3" >nul || (
    echo Pulling Llama 3.3 model...
    ollama pull llama3.3:latest
)

REM Start n8n if not running
echo Starting n8n workflow engine...
start /B npx n8n

REM Start Oracle AGI V7 Ultimate
echo.
echo Starting Oracle AGI V7 Ultimate System...
echo.

%PYTHON% oracle_agi_v7_ultimate.py

pause