@echo off
echo Starting MCP Chrome Server...
echo.

cd /d "%~dp0\tools\mcp-chrome"

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting MCP Chrome on port 3000...
call npm start

pause