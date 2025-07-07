@echo off
cls
color 0A
title Oracle AGI V8 ULTIMATE - DeepSeek Brain

echo ================================================================================
echo                    ORACLE AGI V8 ULTIMATE
echo              Powered by DeepSeek-R1-Qwen3-8B (5.1 GB)
echo ================================================================================
echo.
echo Primary Brain: hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
echo Integrated: Claude Code (Opus 4) + All Ollama Models
echo.
echo Features:
echo   - Advanced Chat Interface with ALL models
echo   - Real-time Trading System
echo   - Knowledge Graph Learning
echo   - Multi-Model Consensus
echo   - Continuous Self-Improvement
echo   - Voice & Vision (Coming Soon)
echo.
echo ================================================================================
echo.

cd /d C:\Workspace\MCPVotsAGI

REM Make sure Ollama is running
echo Checking Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo Starting Ollama...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)

REM Pull the primary brain model if needed
echo.
echo Checking DeepSeek-R1 Brain model...
ollama list | findstr "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL" >nul || (
    echo Pulling DeepSeek-R1 Brain... This may take a while...
    ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
)

echo.
echo Starting Oracle AGI V8 ULTIMATE...
echo.

REM Use venv Python
C:\Workspace\.venv\Scripts\python.exe oracle_agi_v8_ultimate_brain.py

pause