# PowerShell function to run Python scripts without popups
# Add this to your PowerShell profile or run manually

function Run-Python {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Script,
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )

    # Check if Python is available
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Python not found!" -ForegroundColor Red
        return
    }

    # Check if script exists
    if (-not (Test-Path $Script)) {
        Write-Host "[ERROR] Script not found: $Script" -ForegroundColor Red
        Write-Host "Available Python scripts:" -ForegroundColor Yellow
        Get-ChildItem -Name "*.py" | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
        return
    }

    # Run the script
    $fullCommand = "python `"$Script`""
    if ($Arguments) {
        $fullCommand += " " + ($Arguments -join " ")
    }

    Write-Host "[LAUNCH] $fullCommand" -ForegroundColor Green
    & python $Script @Arguments
}

# Create an alias for easier use
Set-Alias -Name py -Value Run-Python

Write-Host "✅ Python runner loaded!" -ForegroundColor Green
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  Run-Python script.py" -ForegroundColor White
Write-Host "  py script.py" -ForegroundColor White
Write-Host ""
