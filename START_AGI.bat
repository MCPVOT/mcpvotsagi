@echo off
echo.
echo ========================================================
echo MCPVotsAGI ULTIMATE SYSTEM LAUNCHER
echo ========================================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

REM Check Ollama
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama not running!
    echo Starting Ollama might be required...
) else (
    echo [OK] Ollama is running
)

REM Menu
echo.
echo Choose an option:
echo 1. Test Core Systems
echo 2. Start ULTIMATE AGI (auto port)
echo 3. Stop all AGI processes
echo 4. Install dependencies
echo 5. Exit
echo.
choice /c 12345 /n /m "Select option: "

if %errorlevel%==1 goto test
if %errorlevel%==2 goto start
if %errorlevel%==3 goto stop
if %errorlevel%==4 goto install
if %errorlevel%==5 goto end

:test
echo.
echo Running Core Systems Test...
if exist "TEST_CORE_SYSTEMS.py" (
    python "TEST_CORE_SYSTEMS.py"
) else (
    echo [ERROR] TEST_CORE_SYSTEMS.py not found!
    echo [FALLBACK] Running basic system check...
    python -c "import sys; print(f'Python {sys.version}'); print('System OK')"
)
goto menu

:start
echo.
echo Starting ULTIMATE AGI SYSTEM...
if exist "CHECK_AND_START.py" (
    python "CHECK_AND_START.py"
) else if exist "src\core\ULTIMATE_AGI_SYSTEM_V3.py" (
    echo [FALLBACK] Starting Ultimate AGI System V3...
    python "src\core\ULTIMATE_AGI_SYSTEM_V3.py"
) else (
    echo [ERROR] No valid launcher found!
    echo [HELP] Please use START_ECOSYSTEM.bat or START_SAFE_LAUNCHER.bat
)
goto menu

:stop
echo.
echo Stopping all AGI processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *AGI*" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8888') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8889') do taskkill /F /PID %%a >nul 2>&1
echo Processes stopped.
pause
goto menu

:install
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
pause
goto menu

:menu
echo.
goto end

:end
echo.
echo Goodbye!
pause