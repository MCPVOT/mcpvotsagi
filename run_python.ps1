# Python Script Launcher - Prevents "Choose App" Popup
# Usage: .\run_python.ps1 script_name.py [arguments]

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptName,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "[OK] Python is available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and in PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the script exists
if (-not (Test-Path $ScriptName)) {
    Write-Host "[ERROR] Script not found: $ScriptName" -ForegroundColor Red
    Write-Host "Current directory: $PWD" -ForegroundColor Yellow
    Write-Host "Available Python scripts:" -ForegroundColor Yellow
    Get-ChildItem -Name "*.py" | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the Python script with all arguments
$fullCommand = "python `"$ScriptName`""
if ($Arguments) {
    $fullCommand += " " + ($Arguments -join " ")
}

Write-Host "[LAUNCH] Running: $fullCommand" -ForegroundColor Green
try {
    & python $ScriptName @Arguments
} catch {
    Write-Host "[ERROR] Script execution failed: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
