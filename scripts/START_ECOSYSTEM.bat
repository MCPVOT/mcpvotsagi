@echo off
echo ================================================
echo  Ultimate AGI System V3 - Complete Ecosystem
echo ================================================
echo.
echo Starting PowerShell script...
echo.

REM Change to the correct directory
cd /d "%~dp0"

REM Run PowerShell script with execution policy bypass
powershell.exe -ExecutionPolicy Bypass -File "START_COMPLETE_ECOSYSTEM.ps1"

echo.
echo Script completed. Press any key to exit...
pause > nul
