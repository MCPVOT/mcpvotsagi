@echo off
echo ===============================================================
echo    MCPVotsAGI - Ultimate AGI System v2.0 - Windows Launcher
echo ===============================================================
echo.
echo DeepSeek-R1 Model: unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
echo MCP Tools: FileSystem, GitHub, Memory, Browser, Brave Search
echo Context7: Real-time documentation enrichment
echo Claudia: Agent orchestration platform
echo IPFS: Decentralized storage
echo Trading: Real-time market analysis and execution
echo.
echo THE ONE AND ONLY consolidated AGI portal
echo.

REM Check if Python is installed
echo [CHECK] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python is installed

REM Check if Ollama is installed
echo [CHECK] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is not installed
    echo Please install Ollama from https://ollama.com/
    pause
    exit /b 1
)
echo [OK] Ollama is installed

REM Check if Node.js is installed
echo [CHECK] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js is installed

REM Install Python dependencies
echo [DEPS] Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies may have failed to install
)

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found
    echo [SETUP] Copying template...
    copy .env.template .env >nul 2>&1
    echo.
    echo [NOTE] Please edit .env file with your API keys before continuing
    echo Press any key to continue anyway...
    pause >nul
)

REM Launch the system
echo.
echo ===============================================================
echo    LAUNCHING ULTIMATE AGI SYSTEM
echo ===============================================================
echo.
echo [WEB] Dashboard will be available at: http://localhost:8888
echo [STOP] Press Ctrl+C to stop the system
echo.

REM Check if launch script exists
if exist "LAUNCH_ULTIMATE_AGI_DEEPSEEK.py" (
    echo [LAUNCH] Starting Ultimate AGI System...
    python "LAUNCH_ULTIMATE_AGI_DEEPSEEK.py"
) else (
    echo [ERROR] Launch script not found: LAUNCH_ULTIMATE_AGI_DEEPSEEK.py
    echo [FALLBACK] Starting alternative launcher...
    if exist "src\core\ULTIMATE_AGI_SYSTEM_V3.py" (
        python "src\core\ULTIMATE_AGI_SYSTEM_V3.py"
    ) else (
        echo [ERROR] No launch script found!
        echo Available options:
        echo   1. Use START_COMPLETE_ECOSYSTEM.ps1
        echo   2. Use START_ECOSYSTEM.bat
        echo   3. Run: python src\core\ULTIMATE_AGI_SYSTEM_V3.py
        pause
        exit /b 1
    )
)

echo.
echo [STOP] Ultimate AGI System stopped
pause