@echo off
cls
color 0A
title Oracle AGI V5 - Production System

echo ================================================================================
echo                      ORACLE AGI V5 - COMPLETE SYSTEM
echo ================================================================================
echo.
echo Starting the complete Oracle AGI ecosystem with:
echo - Oracle AGI Core (Port 8888)
echo - Trilogy Brain (Port 8887) 
echo - Trading System (Port 8889)
echo - Unified Dashboard (Port 3002)
echo - AI Models: Gemini, DeepSeek, Claude, GPT-4
echo - MCP Tools: Memory Vault, GitHub, Filesystem
echo.
echo ================================================================================

cd /d C:\Workspace\MCPVotsAGI

C:\Workspace\.venv\Scripts\python.exe oracle_agi_v5_complete.py

pause