@echo off
REM Oracle AGI Quick Run Script for Windows
REM ======================================

echo ============================================
echo   Oracle AGI Unified Dashboard Launcher
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/3] Checking Python version...
python --version

echo.
echo [2/3] Installing dependencies...
python -m pip install --quiet aiohttp websockets aiohttp-cors psutil aiosqlite

echo.
echo [3/3] Starting Oracle AGI Dashboard...
echo.
echo The dashboard will:
echo - Auto-detect available port
echo - Start required MCP tools
echo - Provide unified interface
echo.
echo Available at: http://localhost:3011 (or next available port)
echo.

REM Try to run the fix script first
if exist "fix_and_run.py" (
    python fix_and_run.py
) else (
    REM Try direct run
    if exist "run_oracle_agi.py" (
        python run_oracle_agi.py
    ) else (
        REM Last resort - run main script
        if exist "oracle_agi_unified_final.py" (
            python oracle_agi_unified_final.py
        ) else (
            echo ERROR: Cannot find Oracle AGI scripts!
            echo Please ensure you are in the MCPVotsAGI directory
        )
    )
)

pause