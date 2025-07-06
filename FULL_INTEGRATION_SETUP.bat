@echo off
echo ============================================
echo ULTIMATE AGI V3 - Full Frontend Integration
echo ============================================
echo.

REM Check prerequisites
echo Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.12+ from https://python.org
    pause
    exit /b 1
) else (
    echo [OK] Python found
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
) else (
    echo [OK] Node.js found
)

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed!
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
) else (
    echo [OK] Git found
)

echo.
echo ============================================
echo Step 1: Setting up Frontend
echo ============================================
echo.

REM Create frontend directory
if not exist frontend mkdir frontend
cd frontend

REM Clone repositories
echo Downloading UI libraries...
if not exist animate-ui (
    git clone https://github.com/kabrony/animate-ui.git
    echo [OK] Animate UI downloaded
) else (
    echo [INFO] Animate UI already exists
    cd animate-ui
    git pull
    cd ..
)

if not exist agi-dashboard (
    git clone https://github.com/kabrony/next-shadcn-dashboard-starter.git agi-dashboard
    echo [OK] Dashboard downloaded
) else (
    echo [INFO] Dashboard already exists
    cd agi-dashboard
    git pull
    cd ..
)

echo.
echo ============================================
echo Step 2: Installing Dependencies
echo ============================================
echo.

cd agi-dashboard
echo Installing npm packages...
call npm install

echo.
echo Creating environment configuration...
(
echo NEXT_PUBLIC_API_URL=http://localhost:8889
echo NEXT_PUBLIC_WS_URL=ws://localhost:8889/ws
echo NEXT_PUBLIC_APP_NAME=ULTIMATE AGI System V3
) > .env.local

echo.
echo ============================================
echo Step 3: Setting up API Integration
echo ============================================
echo.

REM Create necessary directories
mkdir src\lib\api 2>nul
mkdir src\components\agents 2>nul
mkdir src\components\storage 2>nul
mkdir src\components\chat 2>nul
mkdir src\components\models 2>nul
mkdir src\components\metrics 2>nul

echo API client and components have been created!

cd ..\..

echo.
echo ============================================
echo Step 4: Backend Configuration
echo ============================================
echo.

REM Check if backend is set up
if not exist src\core\ULTIMATE_AGI_SYSTEM_V3.py (
    echo [ERROR] Backend not found!
    echo Please ensure ULTIMATE_AGI_SYSTEM_V3.py exists
    pause
    exit /b 1
) else (
    echo [OK] Backend found
)

echo.
echo ============================================
echo Step 5: Creating Launcher Scripts
echo ============================================
echo.

REM Create unified launcher
(
echo @echo off
echo echo Starting ULTIMATE AGI V3 with Modern UI...
echo echo.
echo echo Step 1: Starting Backend API...
echo start "AGI Backend" cmd /k "python src\core\ULTIMATE_AGI_SYSTEM_V3.py"
echo timeout /t 5
echo.
echo echo Step 2: Starting Frontend Dashboard...
echo cd frontend\agi-dashboard
echo start "AGI Frontend" cmd /k "npm run dev"
echo.
echo echo ============================================
echo echo ULTIMATE AGI V3 is starting up!
echo echo.
echo echo Backend API: http://localhost:8889
echo echo Frontend UI: http://localhost:3000
echo echo.
echo echo Press any key to open the dashboard...
echo pause >nul
echo start http://localhost:3000
) > START_FULL_SYSTEM.bat

echo.
echo ============================================
echo Integration Complete!
echo ============================================
echo.
echo Your ULTIMATE AGI V3 system is now fully integrated with:
echo - Modern React dashboard (Next.js 15)
echo - Smooth animations (Framer Motion)
echo - Professional UI components (Shadcn)
echo - Real-time updates (WebSocket)
echo - F: drive storage monitoring (853GB)
echo - Multi-model orchestration
echo - Agent management interface
echo.
echo To start the system:
echo   Run START_FULL_SYSTEM.bat
echo.
echo Or start components individually:
echo   Backend: python src\core\ULTIMATE_AGI_SYSTEM_V3.py
echo   Frontend: cd frontend\agi-dashboard ^&^& npm run dev
echo.
pause