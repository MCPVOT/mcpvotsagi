@echo off
cls
echo ========================================
echo     ORACLE AGI V5 - RUNNING
echo ========================================
echo.
echo Dashboard is now available at:
echo.
echo     http://localhost:3002
echo.
echo ========================================
echo.
echo To access the dashboard:
echo 1. Open your web browser
echo 2. Go to: http://localhost:3002
echo.
echo API Endpoints:
echo - Status: http://localhost:3002/api/status
echo - Trading: http://localhost:3002/api/trading/signals
echo - Chat: http://localhost:3002/api/chat
echo.
echo Press Ctrl+C to stop the system
echo ========================================

cd /d C:\Workspace\MCPVotsAGI
C:\Workspace\.venv\Scripts\python.exe oracle_agi_v5_simple.py