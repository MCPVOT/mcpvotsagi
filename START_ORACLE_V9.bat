@echo off
cd /d "C:\Workspace\MCPVotsAGI"
echo Starting Oracle V9...
if exist "start_oracle_v9.py" (
    python "start_oracle_v9.py"
) else (
    echo [ERROR] Script not found: start_oracle_v9.py
    echo [FALLBACK] Starting Ultimate AGI System V3...
    if exist "src\core\ULTIMATE_AGI_SYSTEM_V3.py" (
        python "src\core\ULTIMATE_AGI_SYSTEM_V3.py"
    ) else (
        echo [ERROR] No valid launch script found!
        echo Please use START_ECOSYSTEM.bat instead
        pause
        exit /b 1
    )
)
pause