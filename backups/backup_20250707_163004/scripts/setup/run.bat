@echo off
echo ========================================
echo Oracle AGI V5 - PRODUCTION SYSTEM
echo ========================================

cd /d C:\Workspace\MCPVotsAGI

echo Activating virtual environment...
call C:\Workspace\.venv\Scripts\activate

echo Installing dependencies...
pip install aiohttp websockets psutil requests aiofiles

echo Starting Oracle AGI V5...
REM Check if the script exists
if exist "oracle_agi_v5_complete.py" (
    python "oracle_agi_v5_complete.py"
) else (
    echo [ERROR] Script not found: oracle_agi_v5_complete.py
    echo [FALLBACK] Checking for alternative scripts...
    if exist "..\..\src\core\ULTIMATE_AGI_SYSTEM_V3.py" (
        echo [LAUNCH] Starting Ultimate AGI System V3...
        python "..\..\src\core\ULTIMATE_AGI_SYSTEM_V3.py"
    ) else (
        echo [ERROR] No valid script found!
        echo Please run from the main directory: START_ECOSYSTEM.bat
        pause
        exit /b 1
    )
)

pause