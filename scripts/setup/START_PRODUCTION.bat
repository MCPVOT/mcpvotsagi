@echo off
echo ================================================================================
echo MCPVOTSAGI PRODUCTION SYSTEM
echo Real Services Only - No Demos
echo ================================================================================
echo.

REM Set required environment variables
echo Setting environment variables...
set PYTHONUNBUFFERED=1
set ORACLE_PORT=8888

REM Check for API keys
if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY not set. Some services may not work properly.
    echo Please set it with: set GEMINI_API_KEY=your_api_key
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
if exist "C:\Workspace\.venv\Scripts\activate.bat" (
    call C:\Workspace\.venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo WARNING: No virtual environment found at C:\Workspace\.venv
    echo Using system Python
)

REM Check Python version
python --version

REM Install any missing dependencies
echo.
echo Checking dependencies...
python -m pip install aiohttp psutil

REM Run the production system
echo.
echo Starting MCPVotsAGI Production System...
echo.
python C:\Workspace\MCPVotsAGI\start_production_system.py

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo ERROR: Production system failed!
    pause
)