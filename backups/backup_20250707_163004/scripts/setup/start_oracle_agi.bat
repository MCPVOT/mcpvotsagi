@echo off
cls
echo ================================================================================
echo                         ORACLE AGI V5 - PRODUCTION SYSTEM
echo ================================================================================
echo.

cd /d C:\Workspace\MCPVotsAGI

echo [1/3] Activating virtual environment...
call C:\Workspace\.venv\Scripts\activate

echo [2/3] System check...
python --version
echo.

echo [3/3] Starting Oracle AGI V5 Complete System...
echo --------------------------------------------------------------------------------
python oracle_agi_v5_complete.py

pause