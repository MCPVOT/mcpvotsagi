@echo off
cls
color 0A
title Oracle AGI V7 Simple

cd /d C:\Workspace\MCPVotsAGI

echo ================================================================================
echo                         ORACLE AGI V7 - SIMPLE
echo ================================================================================
echo.

REM Use venv Python
C:\Workspace\.venv\Scripts\python.exe oracle_v7_simple.py

REM If that fails, try system Python
if errorlevel 1 (
    echo.
    echo Trying with system Python...
    python oracle_v7_simple.py
)

pause