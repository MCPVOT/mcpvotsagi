@echo off
echo.
echo ========================================================
echo MCPVotsAGI COMPLETE SYSTEM SETUP
echo ========================================================
echo.

echo [1/5] Installing Python dependencies...
pip install aiohttp psutil websockets numpy pandas pyyaml requests ipfshttpclient
pip install chromadb sentence-transformers networkx scikit-learn
pip install finnhub-python ccxt web3 solana
pip install ollama

echo.
echo [2/5] Installing Node.js MCP servers...
call npm install -g @modelcontextprotocol/server-filesystem
call npm install -g @modelcontextprotocol/server-github  
call npm install -g @modelcontextprotocol/server-memory

echo.
echo [3/5] Checking Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama not running! Please:
    echo 1. Install Ollama from https://ollama.ai
    echo 2. Run: ollama serve
    echo 3. Run: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
) else (
    echo Ollama is installed
)

echo.
echo [4/5] Creating directories...
if not exist memory mkdir memory
if not exist knowledge mkdir knowledge
if not exist rl_models mkdir rl_models
if not exist logs mkdir logs

echo.
echo [5/5] Creating .env template...
if not exist .env (
    echo # API Keys > .env
    echo OPENAI_API_KEY=your_key_here >> .env
    echo ANTHROPIC_API_KEY=your_key_here >> .env
    echo FINNHUB_API_KEY=your_key_here >> .env
    echo GITHUB_TOKEN=your_token_here >> .env
    echo SOLANA_RPC_URL=https://api.mainnet-beta.solana.com >> .env
    echo Created .env file - please add your API keys
)

echo.
echo ========================================================
echo SETUP COMPLETE!
echo ========================================================
echo.
echo Next steps:
echo 1. Edit .env and add your API keys
echo 2. Start Ollama: ollama serve
echo 3. Pull DeepSeek: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL
echo 4. Run verification: python VERIFY_ALL_FUNCTIONAL.py
echo 5. Start system: python START_ULTIMATE_AGI_WITH_CLAUDIA.py
echo.
pause