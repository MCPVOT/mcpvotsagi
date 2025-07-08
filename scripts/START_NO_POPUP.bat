@echo off
echo ================================================
echo  ULTIMATE AGI SYSTEM V3 - WORKING LAUNCHER
echo ================================================
echo.
echo [INFO] This is a guaranteed working launcher
echo [INFO] It will NOT cause "choose app" popups
echo.

REM Change to correct directory
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ and add to PATH
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Show Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% is available

REM Check for virtual environment
python -c "import sys; print('Virtual environment active' if sys.prefix != sys.base_prefix else 'System Python')"

echo.
echo [MENU] Choose startup option:
echo   1. Start Ultimate AGI System V3 (Recommended)
echo   2. Start Frontend Only
echo   3. Start with PowerShell Ecosystem
echo   4. Check System Status
echo   5. Exit
echo.
choice /c 12345 /n /m "Select option (1-5): "

if %errorlevel%==1 goto start_backend
if %errorlevel%==2 goto start_frontend
if %errorlevel%==3 goto start_powershell
if %errorlevel%==4 goto check_status
if %errorlevel%==5 goto exit

:start_backend
echo.
echo [LAUNCH] Starting Ultimate AGI System V3...
if exist "src\core\ULTIMATE_AGI_SYSTEM_V3.py" (
    echo [OK] Found Ultimate AGI System V3
    python "src\core\ULTIMATE_AGI_SYSTEM_V3.py"
) else (
    echo [ERROR] Ultimate AGI System V3 not found!
    echo [HELP] Please ensure src\core\ULTIMATE_AGI_SYSTEM_V3.py exists
)
goto exit

:start_frontend
echo.
echo [LAUNCH] Starting Frontend Only...
if exist "frontend\package.json" (
    echo [OK] Found frontend directory
    cd frontend
    echo [INFO] Installing dependencies if needed...
    npm install --silent
    echo [INFO] Starting Next.js development server...
    echo [INFO] Frontend will be available at http://localhost:3002
    npm run dev
) else (
    echo [ERROR] Frontend not found!
    echo [HELP] Please ensure frontend directory exists
)
goto exit

:start_powershell
echo.
echo [LAUNCH] Starting PowerShell Ecosystem...
if exist "START_COMPLETE_ECOSYSTEM.ps1" (
    echo [OK] Found PowerShell ecosystem launcher
    powershell.exe -ExecutionPolicy Bypass -File "START_COMPLETE_ECOSYSTEM.ps1"
) else (
    echo [ERROR] PowerShell ecosystem not found!
    echo [HELP] Please ensure START_COMPLETE_ECOSYSTEM.ps1 exists
)
goto exit

:check_status
echo.
echo [STATUS] System Status Check...
echo.
echo Python:
python --version
echo.
echo Node.js:
node --version 2>nul || echo Not installed
echo.
echo Available launch scripts:
if exist "src\core\ULTIMATE_AGI_SYSTEM_V3.py" echo   ✓ Ultimate AGI System V3
if exist "START_COMPLETE_ECOSYSTEM.ps1" echo   ✓ PowerShell Ecosystem
if exist "frontend\package.json" echo   ✓ Frontend
echo.
echo F: Drive Storage:
if exist "F:\ULTIMATE_AGI_DATA" (
    echo   ✓ F: Drive configured
    dir "F:\ULTIMATE_AGI_DATA" /b 2>nul | find /c /v "" && echo directories found || echo Empty
) else (
    echo   ✗ F: Drive not configured
)
echo.
pause
goto exit

:exit
echo.
echo [DONE] Thank you for using Ultimate AGI System V3
pause
