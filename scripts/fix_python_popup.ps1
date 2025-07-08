# Fix Windows "Choose App" Popup for Python Scripts
# This PowerShell script fixes the file association issue

Write-Host "🔧 Fixing Python File Association Issue..." -ForegroundColor Yellow
Write-Host "This will prevent 'Choose App' popups when running Python scripts" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️ This script needs to run as Administrator to fix file associations" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Use the wrapper scripts instead:" -ForegroundColor Green
    Write-Host "  .\run_python.ps1 script_name.py" -ForegroundColor Cyan
    Write-Host "  .\run_python.bat script_name.py" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

# Get Python executable path
try {
    $pythonPath = (Get-Command python).Source
    Write-Host "✅ Found Python at: $pythonPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please install Python and add it to PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Set file associations
try {
    Write-Host "🔧 Setting Python file associations..." -ForegroundColor Yellow

    # Associate .py files with Python
    cmd /c "assoc .py=Python.File"
    cmd /c "ftype Python.File=`"$pythonPath`" `"%1`" %*"

    # Associate .pyw files with Python (windowed)
    cmd /c "assoc .pyw=Python.NoConFile"
    cmd /c "ftype Python.NoConFile=`"$pythonPath`"w `"%1`" %*"

    Write-Host "✅ Python file associations set successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run Python scripts directly:" -ForegroundColor Green
    Write-Host "  python script.py" -ForegroundColor Cyan
    Write-Host "  Or double-click .py files" -ForegroundColor Cyan

} catch {
    Write-Host "❌ Failed to set file associations: $_" -ForegroundColor Red
    Write-Host "Use the wrapper scripts instead" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup complete! No more 'Choose App' popups!" -ForegroundColor Green
Read-Host "Press Enter to exit"
