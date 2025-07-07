@echo off
echo ================================================
echo  Ultimate AGI System V3 - Frontend Launcher
echo ================================================
echo.
echo Starting Next.js Development Server...
echo.
echo Frontend will be available at:
echo   Local:   http://localhost:3002
echo   Network: http://172.27.176.1:3002
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
npx next dev -p 3002

pause
