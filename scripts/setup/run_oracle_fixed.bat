@echo off
echo ================================================================================
echo ORACLE AGI V5 FIXED - LAUNCHER
echo Using existing advanced dashboard HTML files
echo ================================================================================
echo.

REM Activate the virtual environment
echo Activating virtual environment...
call C:\Workspace\.venv\Scripts\activate.bat

REM Run the fixed Oracle AGI
echo Starting Oracle AGI V5 Fixed...
python C:\Workspace\MCPVotsAGI\oracle_agi_v5_fixed.py

REM Keep window open if error
if errorlevel 1 (
    echo.
    echo ERROR: Oracle AGI failed to start!
    pause
)