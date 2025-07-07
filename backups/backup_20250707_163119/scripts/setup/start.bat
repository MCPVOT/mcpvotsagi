@echo off
REM MCPVotsAGI Quick Start Script for Windows

echo ====================================
echo   MCPVotsAGI Ecosystem Launcher
echo ====================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Run health check
echo Running system health check...
python launcher.py doctor

if errorlevel 1 (
    echo.
    echo Health check failed. Please fix issues before continuing.
    pause
    exit /b 1
)

REM Start ecosystem
echo.
echo Starting MCPVotsAGI Ecosystem...
echo.

REM Default to quickstart, but allow custom commands
if "%~1"=="" (
    python launcher.py quickstart
) else (
    python launcher.py %*
)

pause
