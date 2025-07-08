@echo off
echo ==========================================
echo  MCP SERVERS SETUP FOR VSCODE
echo ==========================================
echo.

echo Checking prerequisites...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm not found. Please install Node.js first.
    pause
    exit /b 1
)

echo ✓ Node.js and npm are available
echo.

echo Installing/updating MCP servers...
echo.

echo Installing FileSystem MCP...
call npm install -g @modelcontextprotocol/server-filesystem
if %errorlevel% neq 0 (
    echo WARNING: FileSystem MCP installation had issues
)

echo Installing Memory MCP...
call npm install -g @modelcontextprotocol/server-memory
if %errorlevel% neq 0 (
    echo WARNING: Memory MCP installation had issues
)

echo Installing GitHub MCP...
call npm install -g @modelcontextprotocol/server-github
if %errorlevel% neq 0 (
    echo WARNING: GitHub MCP installation had issues
)

echo Installing Browser MCP...
call npm install -g @modelcontextprotocol/server-puppeteer
if %errorlevel% neq 0 (
    echo WARNING: Browser MCP installation had issues
)

echo Installing Brave Search MCP...
call npm install -g @modelcontextprotocol/server-brave-search
if %errorlevel% neq 0 (
    echo WARNING: Brave Search MCP installation had issues
)

echo.
echo ==========================================
echo  MCP SERVERS INSTALLATION COMPLETE
echo ==========================================
echo.
echo Next steps:
echo 1. Open VS Code
echo 2. Go to Settings (Ctrl+,)
echo 3. Search for "MCP" or "Model Context Protocol"
echo 4. Add the MCP server configuration
echo 5. Set environment variables for GitHub and Brave (optional)
echo.
echo For detailed setup instructions, see:
echo docs\MCP_SETUP_GUIDE_VSCODE.md
echo.
echo The AGI dashboard at http://localhost:8888 will automatically
echo detect and use the configured MCP servers.
echo.
pause
