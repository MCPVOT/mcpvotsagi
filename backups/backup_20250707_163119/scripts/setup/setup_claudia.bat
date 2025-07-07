@echo off
echo ================================================================================
echo CLAUDIA SETUP FOR ORACLE AGI INTEGRATION
echo ================================================================================
echo.

cd /d C:\Workspace\MCPVotsAGI\claudia

echo Installing dependencies...

REM Check if bun is installed
where bun >nul 2>nul
if %errorlevel% neq 0 (
    echo Bun not found, using npm instead...
    call npm install
) else (
    echo Using bun to install dependencies...
    call bun install
)

echo.
echo Building Claudia...

REM Build the Tauri app
if exist "node_modules" (
    if exist "package.json" (
        call npm run tauri build
    )
) else (
    echo ERROR: Dependencies not installed properly!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Claudia setup complete!
echo.
echo To run Claudia in development mode:
echo   cd C:\Workspace\MCPVotsAGI\claudia
echo   npm run tauri dev
echo.
echo To run the Oracle + Claudia integration:
echo   cd C:\Workspace\MCPVotsAGI
echo   python oracle_claudia_integration.py
echo ================================================================================
pause