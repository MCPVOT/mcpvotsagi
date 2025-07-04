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
python oracle_agi_v5_complete.py

pause