# Check what's using port 8888
Write-Host "Checking what's using port 8888..." -ForegroundColor Cyan

$process = Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue

if ($process) {
    $pid = $process.OwningProcess
    $processInfo = Get-Process -Id $pid
    
    Write-Host "`nFound process using port 8888:" -ForegroundColor Yellow
    Write-Host "Process Name: $($processInfo.ProcessName)" -ForegroundColor Green
    Write-Host "Process ID: $pid" -ForegroundColor Green
    Write-Host "Process Path: $($processInfo.Path)" -ForegroundColor Green
    
    Write-Host "`nYou can:" -ForegroundColor Cyan
    Write-Host "1. Access the existing dashboard at http://localhost:8888"
    Write-Host "2. Stop it with: Stop-Process -Id $pid -Force"
    Write-Host "3. Or run: .\STOP_ALL_AGI.bat"
} else {
    Write-Host "Port 8888 is free!" -ForegroundColor Green
}