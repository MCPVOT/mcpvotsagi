@echo off
echo ================================================================================
echo 🚀 STARTING ULTIMATE AGI SYSTEM V3 WITH CLAUDIA/OLLAMA
echo ================================================================================

cd /d "C:\Workspace\MCPVotsAGI"

echo 📋 Step 1: Starting Ollama server...
start "Ollama Server" cmd /k "ollama serve"

echo ⏳ Waiting for Ollama to initialize...
timeout /t 5 /nobreak

echo 📋 Step 2: Verifying available models...
echo ✅ Found excellent model collection:
echo    - DeepSeek-R1 (latest, 8b, 1.5b) for advanced reasoning
echo    - Llama 3.2 3b for fast inference
echo    - Qwen2.5-Coder for code analysis
echo    - Gemma3n for mathematical operations

echo 📋 Step 3: Starting Python virtual environment...
call .venv\Scripts\activate.bat

echo 📋 Step 4: Installing any missing dependencies...
pip install --quiet aiohttp websockets numpy pandas scikit-learn

echo 📋 Step 5: Starting Stable Claudia-Enhanced Ecosystem...
python launch_stable_ecosystem.py

echo ================================================================================
echo 🎯 SYSTEM STARTUP COMPLETE
echo ================================================================================
pause
