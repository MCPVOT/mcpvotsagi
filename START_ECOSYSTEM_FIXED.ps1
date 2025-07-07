# Ultimate AGI System V3 - Complete Ecosystem Launcher
# ===================================================

Write-Host "Ultimate AGI System V3 - Complete Ecosystem" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if we're in virtual environment
$pythonPath = python -c "import sys; print(sys.executable)" 2>$null
if ($pythonPath -like "*venv*") {
    Write-Host "Virtual environment active: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Check Python and Node.js availability
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
$nodeVersion = node --version 2>$null

if ($pythonVersion) {
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python not found!" -ForegroundColor Red
    exit 1
}

if ($nodeVersion) {
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js not found!" -ForegroundColor Red
    exit 1
}

# Install Python dependencies if needed
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -q fastapi uvicorn aiohttp psutil numpy pandas pyyaml requests websockets python-dotenv

# Start the backend system
Write-Host "Starting Ultimate AGI System V3 Backend..." -ForegroundColor Cyan
Start-Job -Name "AGI_Backend" -ScriptBlock {
    Set-Location "C:\Workspace\MCPVotsAGI"
    & ".\venv\Scripts\Activate.ps1"
    python "src\core\ULTIMATE_AGI_SYSTEM_V3.py"
}

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start the frontend
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Set-Location "frontend"

# Install npm dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
}

# Set environment variables
$env:NEXT_PUBLIC_SENTRY_DISABLED = "true"
$env:NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = "pk_test_demo_key_for_development"
$env:CLERK_SECRET_KEY = "sk_test_demo_key_for_development"

# Start Next.js development server
Write-Host "Frontend will be available at:" -ForegroundColor Green
Write-Host "  Local:   http://localhost:3002" -ForegroundColor White
Write-Host "  Network: http://172.27.176.1:3002" -ForegroundColor White
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

npx next dev -p 3002
