@echo off
cls
echo ================================================
echo   ULTIMATE AGI SYSTEM V3 - Full Stack Launch
echo ================================================
echo.
echo Initializing the most advanced AGI platform...
echo.

REM Check if backend is already running
netstat -an | find "8889" >nul
if not errorlevel 1 (
    echo [INFO] Backend already running on port 8889
) else (
    echo [1/3] Starting Backend API Server...
    start "ULTIMATE AGI Backend" cmd /k "cd /d C:\Workspace\MCPVotsAGI && python src\core\ULTIMATE_AGI_SYSTEM_V3.py"
    echo      Waiting for backend to initialize...
    timeout /t 8 >nul
)

REM Check if frontend dependencies are installed
if not exist frontend\agi-dashboard\node_modules (
    echo [ERROR] Frontend not set up! Please run FULL_INTEGRATION_SETUP.bat first
    pause
    exit /b 1
)

REM Check if frontend is already running
netstat -an | find "3000" >nul
if not errorlevel 1 (
    echo [INFO] Frontend already running on port 3000
) else (
    echo.
    echo [2/3] Starting Frontend Dashboard...
    start "ULTIMATE AGI Frontend" cmd /k "cd /d C:\Workspace\MCPVotsAGI\frontend\agi-dashboard && npm run dev"
    echo      Waiting for frontend to compile...
    timeout /t 10 >nul
)

echo.
echo [3/3] System Ready!
echo.
echo ================================================
echo   Access Points:
echo ================================================
echo.
echo   🌐 Main Dashboard:    http://localhost:3000
echo   🔌 Backend API:       http://localhost:8889
echo   📊 API Status:        http://localhost:8889/api/status
echo   🗄️ Storage Stats:     http://localhost:8889/api/storage/stats
echo.
echo ================================================
echo   Features:
echo ================================================
echo.
echo   ✅ Modern React Dashboard with Animations
echo   ✅ Real-time WebSocket Updates
echo   ✅ F: Drive Storage Monitoring (853GB)
echo   ✅ Multi-Model AI Orchestration
echo   ✅ 15+ Specialized Agents
echo   ✅ Context7 Documentation Integration
echo   ✅ Professional UI/UX Design
echo.
echo ================================================
echo.
echo Press any key to open the dashboard in your browser...
pause >nul

echo.
echo Opening dashboard...
start http://localhost:3000

echo.
echo ================================================
echo System is running! Press Ctrl+C in any window to stop.
echo ================================================
echo.
pause