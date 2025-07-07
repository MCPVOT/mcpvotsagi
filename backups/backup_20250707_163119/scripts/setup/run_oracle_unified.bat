@echo off
echo ================================================================================
echo ORACLE AGI V5 UNIFIED FINAL - LAUNCHER
echo The One True Dashboard with All Features Integrated
echo ================================================================================
echo.

REM Activate the virtual environment
echo Activating virtual environment...
call C:\Workspace\.venv\Scripts\activate.bat

REM Run the unified Oracle AGI
echo Starting Oracle AGI V5 Unified Final...
python C:\Workspace\MCPVotsAGI\oracle_agi_v5_unified_final.py

REM Keep window open if error
if errorlevel 1 (
    echo.
    echo ERROR: Oracle AGI failed to start!
    pause
)