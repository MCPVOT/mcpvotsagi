
Write-Host "Starting Oracle AGI V9 with Ollama..." -ForegroundColor Cyan
Set-Location "C:\Workspace\MCPVotsAGI"
python "C:\Workspace\MCPVotsAGI\src\core\start_unified_dashboard_with_ollama.py"
Read-Host "Press Enter to exit"
