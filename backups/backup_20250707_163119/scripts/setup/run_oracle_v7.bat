@echo off
cd /d C:\Workspace\MCPVotsAGI

echo Starting Oracle AGI V7...

REM Set Python to use UTF-8
set PYTHONIOENCODING=utf-8

REM Run with venv Python
C:\Workspace\.venv\Scripts\python.exe oracle_agi_v7_ultimate.py

pause