@echo off
REM ========================================
REM MCPVotsAGI Ecosystem Auto-Start Script
REM ========================================

echo ===============================================
echo    MCPVotsAGI Ecosystem Startup
echo    Full Auto-Start with Self-Healing
echo ===============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Not running as administrator
    echo Some features may not work properly
    echo.
)

REM Set working directory
cd /d "C:\Workspace\MCPVotsAGI"

REM Check prerequisites
echo Checking prerequisites...
python ecosystem_manager.py check
if errorlevel 1 (
    echo.
    echo Prerequisites check failed!
    echo Please resolve the issues above before continuing.
    pause
    exit /b 1
)

echo.
echo ===============================================
echo Starting MCPVotsAGI Ecosystem...
echo ===============================================
echo.

REM Start ecosystem manager with monitoring
start "MCPVotsAGI Ecosystem Manager" /min python ecosystem_manager.py start

REM Wait for services to initialize
echo Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Start the ultimate dashboard
echo.
echo Starting Oracle AGI Ultimate Dashboard V2...
start "Oracle AGI Dashboard" python oracle_agi_ultimate_unified_v2.py

echo.
echo ===============================================
echo    Ecosystem Started Successfully!
echo ===============================================
echo.
echo Dashboard URL: http://localhost:3010
echo.
echo To stop all services, press Ctrl+C in the Ecosystem Manager window
echo or run: python ecosystem_manager.py stop
echo.
echo To install as Windows service for auto-start on boot:
echo Run as Administrator: python ecosystem_manager.py install-service
echo.
pause