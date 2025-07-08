@echo off
echo.
echo ===============================================
echo    🌟 Oracle AGI Portal - Ultimate Dashboard
echo ===============================================
echo.
echo Starting the Unified AGI Portal...
echo This will launch the ultimate AGI dashboard with:
echo   - DeepSeek-R1 Integration
echo   - IPFS Decentralized Storage
echo   - MCP Agents (FileSystem, GitHub, Memory, etc.)
echo   - WebSocket Real-time Communication
echo   - Human and Agent Interface
echo.

cd /d "%~dp0"

echo Checking Python...
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 🚀 Launching Unified AGI Portal...
echo.
echo Once started, access the portal at:
echo   Web Interface: http://localhost:8000
echo   WebSocket: ws://localhost:8001
echo.
echo Press Ctrl+C to stop the portal
echo.

python START_UNIFIED_AGI_PORTAL.py

echo.
echo Portal has been stopped.
pause
