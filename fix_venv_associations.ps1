# Fix Python file associations for virtual environment
# This script sets up file associations to work with the current venv

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  FIXING PYTHON FILE ASSOCIATIONS FOR VENV" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a virtual environment
$isVenv = python -c "import sys; print('venv' if sys.prefix != sys.base_prefix else 'system')"
Write-Host "Environment type: $isVenv" -ForegroundColor Yellow

# Get the current Python executable path
$pythonExe = python -c "import sys; print(sys.executable)"
Write-Host "Current Python executable: $pythonExe" -ForegroundColor Green

# Set file associations for the current user only (doesn't require admin)
Write-Host "Setting file associations for current user..." -ForegroundColor Yellow

try {
    # Create registry entries for current user
    New-Item -Path "HKCU:\Software\Classes\.py" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\.py" -Name "(Default)" -Value "Python.File"

    New-Item -Path "HKCU:\Software\Classes\Python.File\shell\open\command" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\Python.File\shell\open\command" -Name "(Default)" -Value "`"$pythonExe`" `"%1`" %*"

    # Also set for .pyw files
    New-Item -Path "HKCU:\Software\Classes\.pyw" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\.pyw" -Name "(Default)" -Value "Python.NoConFile"

    New-Item -Path "HKCU:\Software\Classes\Python.NoConFile\shell\open\command" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\Python.NoConFile\shell\open\command" -Name "(Default)" -Value "`"$pythonExe`"w `"%1`" %*"

    Write-Host ""
    Write-Host "✅ File associations updated successfully!" -ForegroundColor Green
    Write-Host "Python scripts will now run with: $pythonExe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test by running: python test_script.py" -ForegroundColor Yellow

} catch {
    Write-Host "❌ Error setting file associations: $_" -ForegroundColor Red
    Write-Host "Try running as administrator or use the wrapper scripts" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to continue"
