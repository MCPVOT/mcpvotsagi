@echo off
REM Python Script Launcher - Prevents "Choose App" Popup
REM Usage: run_python.bat script_name.py [arguments]

if "%1"=="" (
    echo Usage: run_python.bat script_name.py [arguments]
    echo This prevents Windows "choose app" popups
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please ensure Python is installed and in PATH
    pause
    exit /b 1
)

REM Check if the script exists
if not exist "%1" (
    echo [ERROR] Script not found: %1
    echo Current directory: %CD%
    dir *.py /b 2>nul
    pause
    exit /b 1
)

REM Run the Python script with all arguments
echo [LAUNCH] Running: python %*
python %*
