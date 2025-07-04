@echo off
cls
color 0A
title Oracle AGI V7 - FULL Dashboard

echo ================================================================================
echo              ORACLE AGI V7 - FULL DASHBOARD WITH ALL FEATURES
echo ================================================================================
echo.
echo Starting the complete dashboard with:
echo   - Real-time system metrics with live charts
echo   - MCP services monitoring (Memory, GitHub, DeepSeek, Solana, etc.)
echo   - AI model status (Claude, GPT-4, Gemini, DeepSeek, Llama)
echo   - Knowledge graph visualization
echo   - Trading statistics and performance
echo   - Context preservation monitoring
echo   - System event log
echo   - AI query interface
echo   - WebSocket real-time updates
echo.
echo ================================================================================
echo.

cd /d C:\Workspace\MCPVotsAGI

REM Use venv Python
C:\Workspace\.venv\Scripts\python.exe oracle_agi_v7_full_dashboard.py

pause