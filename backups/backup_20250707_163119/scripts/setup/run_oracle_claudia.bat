@echo off
echo ================================================================================
echo ORACLE AGI + CLAUDIA UNIFIED LAUNCHER
echo ================================================================================
echo.

REM Activate virtual environment
echo Activating Python virtual environment...
call C:\Workspace\.venv\Scripts\activate.bat

REM Start Oracle + Claudia integration (which starts Oracle AGI internally)
echo Starting Oracle AGI + Claudia Integration...
start "Oracle-Claudia Integration" python C:\Workspace\MCPVotsAGI\oracle_claudia_integration.py

REM Wait a bit for the servers to start
echo Waiting for services to initialize...
timeout /t 10 /nobreak

REM Start Claudia in development mode in a new window
echo Starting Claudia UI...
cd /d C:\Workspace\MCPVotsAGI\claudia
start "Claudia UI" cmd /k "npm run tauri dev"

echo.
echo ================================================================================
echo ORACLE AGI + CLAUDIA INTEGRATION RUNNING
echo ================================================================================
echo.
echo Services:
echo - Oracle AGI Dashboard: http://localhost:3002
echo - Claudia Integration API: http://localhost:3003
echo - Claudia Desktop App: Starting in separate window
echo.
echo Oracle AGI Agents available in Claudia:
echo - Oracle Strategic Planner
echo - DeepSeek R1 Executor
echo - DGM Voltagents Analyzer
echo - II-Agent Reflector
echo - Security Scanner
echo.
echo Press Ctrl+C in each window to stop services
echo ================================================================================
pause