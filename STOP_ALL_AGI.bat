@echo off
echo Stopping all AGI processes...

REM Kill Python processes running AGI
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *AGI*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *ULTIMATE_AGI*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *oracle_agi*" 2>nul

REM Kill processes on port 8888
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8888') do taskkill /F /PID %%a 2>nul

REM Kill Ollama if needed
REM taskkill /F /IM ollama.exe 2>nul

echo.
echo ✅ All AGI processes stopped
echo.
pause