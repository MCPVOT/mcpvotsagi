@echo off
cls
color 0A
title Oracle AGI V7 - Starting...

echo ================================================================================
echo                        ORACLE AGI V7 ULTIMATE
echo ================================================================================
echo.

cd /d C:\Workspace\MCPVotsAGI

REM Set UTF-8 encoding
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

REM Check if venv exists
if not exist C:\Workspace\.venv\Scripts\python.exe (
    echo ERROR: Virtual environment not found!
    echo Creating virtual environment...
    python -m venv C:\Workspace\.venv
    echo Installing requirements...
    C:\Workspace\.venv\Scripts\python.exe -m pip install aiohttp psutil pyyaml websockets numpy pandas
)

echo Starting Oracle AGI V7...
echo.

REM Try to run the V7 Ultimate first
if exist oracle_agi_v7_ultimate.py (
    echo Launching Oracle AGI V7 Ultimate...
    C:\Workspace\.venv\Scripts\python.exe oracle_agi_v7_ultimate.py
) else (
    echo Oracle V7 Ultimate not found, creating minimal version...
    
    REM Create a minimal working version
    echo import asyncio > oracle_v7_quick.py
    echo from aiohttp import web >> oracle_v7_quick.py
    echo import json >> oracle_v7_quick.py
    echo import psutil >> oracle_v7_quick.py
    echo from datetime import datetime >> oracle_v7_quick.py
    echo. >> oracle_v7_quick.py
    echo async def handle_index(request): >> oracle_v7_quick.py
    echo     html = '''>> oracle_v7_quick.py
    echo ^<!DOCTYPE html^> >> oracle_v7_quick.py
    echo ^<html^>^<head^>^<title^>Oracle AGI V7^</title^> >> oracle_v7_quick.py
    echo ^<style^>body{font-family:Arial;background:#1a1a1a;color:#fff;text-align:center;padding:40px;}>> oracle_v7_quick.py
    echo h1{color:#4CAF50;font-size:3em;}.status{background:#2a2a2a;padding:30px;border-radius:10px;display:inline-block;}>> oracle_v7_quick.py
    echo .metric{font-size:1.5em;margin:10px;}^</style^>^</head^> >> oracle_v7_quick.py
    echo ^<body^>^<h1^>Oracle AGI V7^</h1^>^<div class="status"^> >> oracle_v7_quick.py
    echo ^<div class="metric"^>Status: ^<span style="color:#4CAF50"^>RUNNING^</span^>^</div^> >> oracle_v7_quick.py
    echo ^<div class="metric"^>CPU: ^<span id="cpu"^>--^</span^>%%^</div^> >> oracle_v7_quick.py
    echo ^<div class="metric"^>Memory: ^<span id="memory"^>--^</span^>%%^</div^> >> oracle_v7_quick.py
    echo ^</div^>^<p^>API: http://localhost:8888/api/status^</p^> >> oracle_v7_quick.py
    echo ^<script^>setInterval(async()=^>{const r=await fetch('/api/status');const d=await r.json(); >> oracle_v7_quick.py
    echo document.getElementById('cpu').textContent=d.cpu.toFixed(1); >> oracle_v7_quick.py
    echo document.getElementById('memory').textContent=d.memory.toFixed(1);},2000);^</script^> >> oracle_v7_quick.py
    echo ^</body^>^</html^>''' >> oracle_v7_quick.py
    echo     return web.Response(text=html, content_type='text/html') >> oracle_v7_quick.py
    echo. >> oracle_v7_quick.py
    echo async def handle_status(request): >> oracle_v7_quick.py
    echo     return web.json_response({ >> oracle_v7_quick.py
    echo         'status': 'running', >> oracle_v7_quick.py
    echo         'version': '7.0.0', >> oracle_v7_quick.py
    echo         'cpu': psutil.cpu_percent(), >> oracle_v7_quick.py
    echo         'memory': psutil.virtual_memory().percent, >> oracle_v7_quick.py
    echo         'timestamp': datetime.utcnow().isoformat() >> oracle_v7_quick.py
    echo     }) >> oracle_v7_quick.py
    echo. >> oracle_v7_quick.py
    echo app = web.Application() >> oracle_v7_quick.py
    echo app.router.add_get('/', handle_index) >> oracle_v7_quick.py
    echo app.router.add_get('/api/status', handle_status) >> oracle_v7_quick.py
    echo. >> oracle_v7_quick.py
    echo if __name__ == '__main__': >> oracle_v7_quick.py
    echo     print('\n' + '='*60) >> oracle_v7_quick.py
    echo     print('Oracle AGI V7 - Running') >> oracle_v7_quick.py
    echo     print('='*60) >> oracle_v7_quick.py
    echo     print('Dashboard: http://localhost:8888') >> oracle_v7_quick.py
    echo     print('API: http://localhost:8888/api/status') >> oracle_v7_quick.py
    echo     print('\nPress Ctrl+C to stop') >> oracle_v7_quick.py
    echo     print('='*60 + '\n') >> oracle_v7_quick.py
    echo     web.run_app(app, host='0.0.0.0', port=8888) >> oracle_v7_quick.py
    
    REM Run the minimal version
    C:\Workspace\.venv\Scripts\python.exe oracle_v7_quick.py
)

REM If we get here, something failed
echo.
echo If you see this message, the server stopped or failed to start.
echo Check for errors above.
echo.
pause