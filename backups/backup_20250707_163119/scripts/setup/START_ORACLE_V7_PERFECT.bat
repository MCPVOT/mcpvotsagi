@echo off
cls
color 0A
title Oracle AGI V7 Perfect Launch System

echo ================================================================================
echo                   ORACLE AGI V7 ULTIMATE - PERFECT LAUNCH
echo ================================================================================
echo.

cd /d C:\Workspace\MCPVotsAGI

REM Use the venv Python
set PYTHON=C:\Workspace\.venv\Scripts\python.exe

if not exist %PYTHON% (
    echo ERROR: Virtual environment not found!
    echo Please ensure venv is installed at C:\Workspace\.venv
    pause
    exit /b 1
)

echo Using Python from venv: %PYTHON%
echo.

REM Run the perfect launcher
%PYTHON% launch_oracle_perfect.py

pause