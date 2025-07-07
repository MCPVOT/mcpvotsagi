@echo off
REM ============================================================
REM MCPVotsAGI DeepSeek Ecosystem Launcher with F:\ Storage
REM ============================================================

echo ============================================================
echo   MCPVotsAGI DEEPSEEK ECOSYSTEM LAUNCHER
echo   With 853 GB F:\ Drive Storage Integration
echo ============================================================
echo.

REM Check if F:\ drive exists
if not exist "F:\" (
    echo ERROR: F:\ drive not found!
    echo Please ensure F:\ drive is mounted and accessible.
    pause
    exit /b 1
)

REM Set environment variables for F:\ storage
echo [1/6] Setting up F:\ drive storage paths...
set MCPVOTSAGI_DATA_ROOT=F:\MCPVotsAGI_Data
set MCPVOTSAGI_RL_DATA=F:\MCPVotsAGI_Data\rl_training
set MCPVOTSAGI_MARKET_DATA=F:\MCPVotsAGI_Data\market_data
set MCPVOTSAGI_MODEL_PATH=F:\MCPVotsAGI_Data\models
set MCPVOTSAGI_MEMORY_PATH=F:\MCPVotsAGI_Data\memory
set MCPVOTSAGI_TRADING_LOGS=F:\MCPVotsAGI_Data\trading
set MCPVOTSAGI_BACKUP_PATH=F:\MCPVotsAGI_Data\backups

REM Performance settings for large storage
set MCPVOTSAGI_CACHE_SIZE=10GB
set MCPVOTSAGI_BUFFER_SIZE=1GB
set MCPVOTSAGI_MAX_MEMORY=32GB

REM DeepSeek configuration
set DEEPSEEK_MODEL=hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
set OLLAMA_HOST=http://localhost:11434
set ENABLE_DEEPSEEK=true

echo ✓ Environment variables configured
echo.

REM Configure F:\ drive storage if not already done
echo [2/6] Checking F:\ drive storage configuration...
if not exist "%MCPVOTSAGI_DATA_ROOT%" (
    echo Creating MCPVotsAGI data infrastructure on F:\ drive...
    python configure_f_drive_storage.py
    if errorlevel 1 (
        echo ERROR: Failed to configure F:\ drive storage
        pause
        exit /b 1
    )
) else (
    echo ✓ F:\ drive storage already configured
)
echo.

REM Check Python version
echo [3/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
python --version
echo.

REM Check and start Ollama
echo [4/6] Checking Ollama service...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama not installed. Please install from https://ollama.ai
    pause
    exit /b 1
)

REM Check if Ollama is running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama">NUL
if "%ERRORLEVEL%"=="1" (
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)
echo ✓ Ollama service running
echo.

REM Check DeepSeek model
echo [5/6] Checking DeepSeek model...
ollama list | findstr /C:"hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL" >nul
if errorlevel 1 (
    echo DeepSeek model not found. Pulling model...
    echo This may take several minutes depending on your connection...
    ollama pull %DEEPSEEK_MODEL%
    if errorlevel 1 (
        echo ERROR: Failed to pull DeepSeek model
        pause
        exit /b 1
    )
) else (
    echo ✓ DeepSeek model available
)
echo.

REM Install/Update dependencies
echo [6/6] Checking Python dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q h5py psutil

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "models" mkdir models
if not exist "data" mkdir data

echo.
echo ============================================================
echo   LAUNCHING MCPVOTSAGI ECOSYSTEM
echo ============================================================
echo.

REM Display system info
echo System Configuration:
echo - F:\ Drive Storage: 853 GB allocated
echo - DeepSeek Model: %DEEPSEEK_MODEL%
echo - RL Buffer Size: 50 million experiences
echo - Market Data: 5 years historical
echo - Trading Mode: 24/7 Autonomous
echo.

REM Launch options menu
echo Select launch mode:
echo [1] Full Ecosystem with DeepSeek Trading (Recommended)
echo [2] DeepSeek MCP Server Only
echo [3] Trading Agent Only
echo [4] Test DeepSeek Integration
echo [5] Manage F:\ Drive Storage
echo [6] Standard Ecosystem (without DeepSeek)
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto full_ecosystem
if "%choice%"=="2" goto deepseek_server
if "%choice%"=="3" goto trading_agent
if "%choice%"=="4" goto test_deepseek
if "%choice%"=="5" goto manage_storage
if "%choice%"=="6" goto standard_ecosystem

echo Invalid choice. Defaulting to full ecosystem...
goto full_ecosystem

:full_ecosystem
echo.
echo Starting Full Ecosystem with DeepSeek Trading...
echo.

REM Start DeepSeek MCP server in new window
start "DeepSeek MCP Server" cmd /k "cd /d C:\Workspace\MCPVotsAGI && python servers\deepseek_ollama_mcp_server.py"

REM Wait for DeepSeek to start
timeout /t 5 /nobreak >nul

REM Start enhanced trading agent in new window
start "DeepSeek Trading Agent" cmd /k "cd /d C:\Workspace\MCPVotsAGI && python src\ai\deepseek_trading_agent_enhanced.py"

REM Wait for services
timeout /t 3 /nobreak >nul

REM Launch main ecosystem
python launcher.py quickstart --trading --security
goto end

:deepseek_server
echo.
echo Starting DeepSeek MCP Server only...
python servers\deepseek_ollama_mcp_server.py
goto end

:trading_agent
echo.
echo Starting Enhanced Trading Agent...
python deepseek_trading_agent_enhanced.py
goto end

:test_deepseek
echo.
echo Running DeepSeek Integration Tests...
python test_deepseek.py
echo.
pause
goto end

:manage_storage
echo.
echo F:\ Drive Storage Management
echo.
python manage_f_drive_data.py usage
echo.
echo Options:
echo [1] Check storage usage
echo [2] Clean old data (30 days)
echo [3] Optimize storage
echo [4] Back to main menu
echo.
set /p storage_choice="Enter choice (1-4): "

if "%storage_choice%"=="1" python manage_f_drive_data.py usage
if "%storage_choice%"=="2" python manage_f_drive_data.py cleanup 30
if "%storage_choice%"=="3" python manage_f_drive_data.py optimize
if "%storage_choice%"=="4" goto end

pause
goto end

:standard_ecosystem
echo.
echo Starting Standard Ecosystem...
python launcher.py quickstart
goto end

:end
echo.
echo ============================================================
echo   MCPVotsAGI Ecosystem Running
echo ============================================================
echo.
echo Dashboard: http://localhost:3011
echo DeepSeek MCP: ws://localhost:3008
echo Trading Agent: Active (check logs)
echo F:\ Storage: %MCPVOTSAGI_DATA_ROOT%
echo.
echo Press any key to exit...
pause >nul