#!/usr/bin/env python3
"""
Launch MCPVotsAGI with DeepSeek Integration
==========================================
Ensures DeepSeek model is available and launches the full ecosystem
"""

import asyncio
import json
import os
import sys
import subprocess
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepSeekLauncher")

class DeepSeekLauncher:
    def __init__(self):
        self.deepseek_model = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
        self.model_id = "2cfa2d3c7a64"  # From ollama list
        
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✓ Ollama is installed and running")
                return True
            else:
                logger.error("✗ Ollama is not running properly")
                return False
        except Exception as e:
            logger.error(f"✗ Ollama not found: {e}")
            return False
            
    def check_deepseek_model(self):
        """Check if DeepSeek model is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            
            if self.deepseek_model in result.stdout or self.model_id in result.stdout:
                logger.info(f"✓ DeepSeek model {self.deepseek_model} is available")
                return True
            else:
                logger.warning(f"✗ DeepSeek model not found. Available models:")
                print(result.stdout)
                return False
        except Exception as e:
            logger.error(f"Failed to check models: {e}")
            return False
            
    def start_ollama_service(self):
        """Start Ollama service if not running"""
        try:
            # Check if already running
            result = subprocess.run(
                ["pgrep", "-f", "ollama serve"],
                capture_output=True
            )
            
            if result.returncode != 0:
                logger.info("Starting Ollama service...")
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(3)  # Wait for startup
                logger.info("✓ Ollama service started")
        except Exception as e:
            logger.error(f"Failed to start Ollama: {e}")
            
    def pull_deepseek_model(self):
        """Pull DeepSeek model if not available"""
        logger.info(f"Pulling DeepSeek model {self.deepseek_model}...")
        try:
            process = subprocess.Popen(
                ["ollama", "pull", self.deepseek_model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Show progress
            for line in process.stdout:
                if line.strip():
                    print(f"  {line.strip()}")
                    
            process.wait()
            
            if process.returncode == 0:
                logger.info("✓ DeepSeek model pulled successfully")
                return True
            else:
                logger.error("✗ Failed to pull DeepSeek model")
                return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
            
    def test_deepseek(self):
        """Test DeepSeek model with a simple query"""
        logger.info("Testing DeepSeek model...")
        try:
            result = subprocess.run(
                ["ollama", "run", self.deepseek_model, "What is 2+2?"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                logger.info("✓ DeepSeek model test successful")
                logger.info(f"  Response: {result.stdout.strip()[:100]}...")
                return True
            else:
                logger.error("✗ DeepSeek model test failed")
                return False
        except Exception as e:
            logger.error(f"Model test error: {e}")
            return False
            
    def launch_ecosystem(self):
        """Launch MCPVotsAGI ecosystem"""
        logger.info("\nLaunching MCPVotsAGI Ecosystem with DeepSeek...")
        
        # Try different launcher scripts
        launchers = [
            "launcher.py",
            "ecosystem_manager.py",
            "oracle_agi_unified_final.py"
        ]
        
        for launcher in launchers:
            launcher_path = Path(launcher)
            if launcher_path.exists():
                logger.info(f"Using launcher: {launcher}")
                
                # Set environment variables
                env = os.environ.copy()
                env["DEEPSEEK_MODEL"] = self.deepseek_model
                env["OLLAMA_HOST"] = "http://localhost:11434"
                env["ENABLE_DEEPSEEK"] = "true"
                
                # Launch with appropriate command
                if launcher == "launcher.py":
                    cmd = [sys.executable, launcher, "quickstart", "--trading", "--security"]
                else:
                    cmd = [sys.executable, launcher]
                    
                subprocess.run(cmd, env=env)
                return
                
        logger.error("No launcher script found!")
        
    def run(self):
        """Main execution flow"""
        print("=" * 60)
        print("  MCPVotsAGI DeepSeek Integration Launcher")
        print("=" * 60)
        print()
        
        # Step 1: Check Ollama
        if not self.check_ollama():
            logger.info("Attempting to start Ollama service...")
            self.start_ollama_service()
            time.sleep(3)
            
            if not self.check_ollama():
                logger.error("Please install Ollama from https://ollama.ai")
                return False
                
        # Step 2: Check DeepSeek model
        if not self.check_deepseek_model():
            if input("\nDeepSeek model not found. Pull it now? (y/n): ").lower() == 'y':
                if not self.pull_deepseek_model():
                    logger.error("Failed to pull model. Please try manually:")
                    logger.error(f"  ollama pull {self.deepseek_model}")
                    return False
            else:
                logger.warning("Proceeding without DeepSeek model")
                
        # Step 3: Test model
        if self.check_deepseek_model():
            self.test_deepseek()
            
        # Step 4: Launch ecosystem
        print("\n" + "=" * 60)
        print("All checks passed! Launching ecosystem...")
        print("=" * 60)
        print()
        
        print("The ecosystem will include:")
        print("- DeepSeek Reasoning Engine (Port 3008)")
        print("- Autonomous Trading Agent with RL/ML")
        print("- 24/7 Trading Monitoring")
        print("- Full MCPVotsAGI Integration")
        print()
        
        self.launch_ecosystem()
        return True

def main():
    launcher = DeepSeekLauncher()
    launcher.run()

if __name__ == "__main__":
    main()