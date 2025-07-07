@echo off
echo ================================================
echo  ULTIMATE AGI SYSTEM V3 - FIXED LAUNCHER
echo ================================================
echo.
echo [INFO] This launcher will check for valid scripts
echo [INFO] and provide proper error handling
echo.

REM Change to correct directory
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)
echo [OK] Python is available

REM Check for valid launch scripts in order of preference
echo.
echo [CHECK] Looking for valid launch scripts...

if exist "src\core\ULTIMATE_AGI_SYSTEM_V3.py" (
    echo [FOUND] Ultimate AGI System V3 - Primary launcher
    echo [LAUNCH] Starting Ultimate AGI System V3...
    python "src\core\ULTIMATE_AGI_SYSTEM_V3.py"
    goto end
)

if exist "START_UNIFIED_AGI_PORTAL.py" (
    echo [FOUND] Unified AGI Portal - Alternative launcher
    echo [LAUNCH] Starting Unified AGI Portal...
    python "START_UNIFIED_AGI_PORTAL.py"
    goto end
)

if exist "START_ULTIMATE_AGI.py" (
    echo [FOUND] Ultimate AGI - Alternative launcher
    echo [LAUNCH] Starting Ultimate AGI...
    python "START_ULTIMATE_AGI.py"
    goto end
)

if exist "LAUNCH_ULTIMATE_AGI_DEEPSEEK.py" (
    echo [FOUND] DeepSeek launcher - Alternative launcher
    echo [LAUNCH] Starting DeepSeek AGI...
    python "LAUNCH_ULTIMATE_AGI_DEEPSEEK.py"
    goto end
)

if exist "START_MCP_SERVERS.py" (
    echo [FOUND] MCP Servers - Alternative launcher
    echo [LAUNCH] Starting MCP Servers...
    python "START_MCP_SERVERS.py"
    goto end
)

REM If no Python scripts found, try PowerShell
if exist "START_COMPLETE_ECOSYSTEM.ps1" (
    echo [FOUND] PowerShell launcher - Alternative launcher
    echo [LAUNCH] Starting PowerShell ecosystem...
    powershell.exe -ExecutionPolicy Bypass -File "START_COMPLETE_ECOSYSTEM.ps1"
    goto end
)

REM No valid launcher found
echo.
echo [ERROR] No valid launcher script found!
echo.
echo [HELP] Available options:
echo   1. Use START_ECOSYSTEM.bat (recommended)
echo   2. Use START_COMPLETE_ECOSYSTEM.ps1
echo   3. Manually run: python src\core\ULTIMATE_AGI_SYSTEM_V3.py
echo.
echo [HELP] If you want to use the frontend:
echo   1. cd frontend
echo   2. npm run dev
echo.

:end
echo.
echo [DONE] Script execution completed
pause
