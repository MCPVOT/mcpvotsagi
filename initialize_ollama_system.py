#!/usr/bin/env python3
"""
Claudia/Ollama System Initializer
================================
Ensures Ollama is running and models are available before starting the ecosystem
"""

import subprocess
import time
import requests
import logging
import sys
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OllamaInitializer")

class OllamaSystemInitializer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.required_models = [
            "llama3.2:3b",
            "deepseek-r1:1.5b",
            "qwen2.5:3b",
            "llama3.2:1b"
        ]

    def check_ollama_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def start_ollama_server(self):
        """Start Ollama server"""
        logger.info("🚀 Starting Ollama server...")
        try:
            # Start Ollama in background
            if sys.platform == "win32":
                subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"])

            # Wait for server to start
            for i in range(30):  # Wait up to 30 seconds
                if self.check_ollama_running():
                    logger.info("✅ Ollama server is running")
                    return True
                time.sleep(1)

            logger.error("❌ Failed to start Ollama server")
            return False
        except Exception as e:
            logger.error(f"❌ Error starting Ollama: {e}")
            return False

    def get_available_models(self) -> list:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error getting models: {e}")
        return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a specific model"""
        logger.info(f"📥 Pulling model: {model_name}")
        try:
            result = subprocess.run(["ollama", "pull", model_name],
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ Successfully pulled {model_name}")
                return True
            else:
                logger.error(f"❌ Failed to pull {model_name}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout pulling {model_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error pulling {model_name}: {e}")
            return False

    def ensure_models_available(self):
        """Ensure all required models are available"""
        available_models = self.get_available_models()
        logger.info(f"📋 Available models: {available_models}")

        for model in self.required_models:
            if model not in available_models:
                logger.info(f"📥 Model {model} not found, pulling...")
                if not self.pull_model(model):
                    logger.warning(f"⚠️ Failed to pull {model}, continuing anyway...")
            else:
                logger.info(f"✅ Model {model} already available")

    def test_model_inference(self, model_name: str = "llama3.2:3b") -> bool:
        """Test model inference"""
        try:
            logger.info(f"🧪 Testing inference with {model_name}...")
            data = {
                "model": model_name,
                "prompt": "Hello! Respond with just 'OK' if you can understand this.",
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 5}
            }

            response = requests.post(f"{self.ollama_url}/api/generate", json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Model inference successful: {result.get('response', '')[:50]}")
                return True
            else:
                logger.error(f"❌ Model inference failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error testing model: {e}")
            return False

    async def initialize_system(self) -> bool:
        """Initialize the complete Ollama system"""
        logger.info("🔧 Initializing Ollama system...")

        # Check if Ollama is running
        if not self.check_ollama_running():
            logger.info("📋 Ollama not running, starting server...")
            if not self.start_ollama_server():
                return False
        else:
            logger.info("✅ Ollama server already running")

        # Ensure models are available
        self.ensure_models_available()

        # Test inference
        if self.test_model_inference():
            logger.info("🎉 Ollama system initialization complete!")
            return True
        else:
            logger.error("❌ Ollama system initialization failed")
            return False

async def main():
    """Main initialization function"""
    initializer = OllamaSystemInitializer()

    print("=" * 80)
    print("🤖 OLLAMA SYSTEM INITIALIZER")
    print("=" * 80)

    success = await initializer.initialize_system()

    if success:
        print("\n🚀 Starting Claudia-Enhanced Ecosystem...")
        # Import and run the enhanced ecosystem
        try:
            from launch_claudia_enhanced_ecosystem import ClaudiaEcosystemLauncher
            launcher = ClaudiaEcosystemLauncher()
            await launcher.start()
        except Exception as e:
            logger.error(f"Error starting ecosystem: {e}")
            print("\n⚠️ You can now manually run: python launch_claudia_enhanced_ecosystem.py")
    else:
        print("\n❌ System initialization failed")
        print("💡 Try running: ollama serve")
        print("💡 Then run: python launch_claudia_enhanced_ecosystem.py")

if __name__ == "__main__":
    asyncio.run(main())
