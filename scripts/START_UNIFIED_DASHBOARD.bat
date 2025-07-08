@echo off
title Unified AGI Dashboard
echo.
echo ================================================================================
echo                          UNIFIED AGI DASHBOARD
echo ================================================================================
echo.
echo Starting the combined Jupiter Trading + Network Monitoring + AI Analysis...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Ollama is running
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama not detected - AI features may be limited
    echo You can start Ollama manually if needed
) else (
    echo SUCCESS: Ollama is running
)

echo.
echo Starting Unified AGI Dashboard...
echo.

python launch_unified_dashboard.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Unified AGI Dashboard
    echo Check the error messages above
    pause
)
