@echo off
echo.
echo ☁️  MCPVotsAGI Cloud Compute Leverager
echo =====================================
echo.
echo Select an option:
echo 1. Start Training Job in Cloud
echo 2. Spawn Agent Swarm in Cloud  
echo 3. Process Large Dataset in Cloud
echo 4. List Active Codespaces
echo 5. Stop All Codespaces
echo 6. Run Custom Task
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo Starting training job in cloud...
    python scripts\leverage_codespaces.py --task training
) else if "%choice%"=="2" (
    echo Spawning agent swarm in cloud...
    python scripts\leverage_codespaces.py --task agents
) else if "%choice%"=="3" (
    echo Processing data in cloud...
    python scripts\leverage_codespaces.py --task data
) else if "%choice%"=="4" (
    echo Listing active Codespaces...
    gh codespace list
) else if "%choice%"=="5" (
    echo Stopping all Codespaces...
    gh codespace stop --all
) else if "%choice%"=="6" (
    echo Opening cloud compute script...
    code scripts\leverage_codespaces.py
) else if "%choice%"=="7" (
    exit
)

echo.
pause