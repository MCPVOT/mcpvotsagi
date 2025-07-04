#!/bin/bash
# Install all dependencies for MCPVotsAGI

echo "📦 Installing MCPVotsAGI dependencies..."

# Core dependencies
pip3 install aiohttp psutil websockets numpy pandas pyyaml requests

# Memory and ML
pip3 install chromadb sentence-transformers networkx scikit-learn

# Trading
pip3 install finnhub-python

# Ollama
pip3 install ollama

# IPFS
pip3 install ipfshttpclient

echo "✅ Dependencies installed!"
echo "💡 Don't forget to:"
echo "   1. Start Ollama: ollama serve"
echo "   2. Pull DeepSeek-R1: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"