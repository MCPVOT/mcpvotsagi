#!/usr/bin/env python3
"""
Verify MCPVotsAGI System is Ready
=================================
Quick check to ensure all components are available
"""

import os
import sys
import subprocess
import requests
import socket
import time
from pathlib import Path
from datetime import datetime

class SystemVerifier:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.workspace = Path("C:/Workspace/MCPVotsAGI")
        
    def print_header(self):
        print("\n" + "="*70)
        print("MCPVotsAGI SYSTEM VERIFICATION")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def check_workspace(self):
        """Check workspace exists"""
        print("📁 Checking workspace...")
        if self.workspace.exists():
            self.passed("Workspace exists")
            
            # Check key directories
            dirs_to_check = [
                "src/core",
                "servers",
                "config",
                "TradingAgents",
                "solana-docs"
            ]
            
            for dir_name in dirs_to_check:
                dir_path = self.workspace / dir_name
                if dir_path.exists():
                    self.passed(f"  ✓ {dir_name}")
                else:
                    self.failed(f"  ✗ {dir_name} missing")
        else:
            self.failed("Workspace not found")
    
    def check_python_deps(self):
        """Check Python dependencies"""
        print("\n🐍 Checking Python dependencies...")
        
        required_packages = [
            "aiohttp",
            "psutil",
            "websockets",
            "numpy",
            "pandas",
            "yaml"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.passed(f"  ✓ {package}")
            except ImportError:
                self.failed(f"  ✗ {package} not installed")
    
    def check_ollama(self):
        """Check Ollama service"""
        print("\n🧠 Checking Ollama...")
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                self.passed("Ollama service running")
                
                # Check for models
                models = response.json().get('models', [])
                deepseek_found = False
                
                print("  Available models:")
                for model in models:
                    model_name = model.get('name', '')
                    print(f"    • {model_name}")
                    if 'DeepSeek-R1' in model_name or 'deepseek' in model_name.lower():
                        deepseek_found = True
                
                if deepseek_found:
                    self.passed("  ✓ DeepSeek-R1 model found")
                else:
                    self.failed("  ✗ DeepSeek-R1 model not found")
                    print("    💡 Pull with: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL")
            else:
                self.failed("Ollama service error")
        except Exception:
            self.failed("Ollama service not running")
            print("  💡 Start with: ollama serve")
    
    def check_ports(self):
        """Check if required ports are available"""
        print("\n🔌 Checking ports...")
        
        ports_to_check = {
            8888: "Oracle Dashboard",
            3001: "GitHub MCP",
            3002: "Memory MCP",
            3005: "Solana MCP",
            3006: "Browser MCP",
            11434: "Ollama API"
        }
        
        for port, service in ports_to_check.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                if port == 8888:
                    self.failed(f"  ✗ Port {port} ({service}) - already in use")
                else:
                    self.passed(f"  ✓ Port {port} ({service}) - in use (good)")
            else:
                if port == 8888:
                    self.passed(f"  ✓ Port {port} ({service}) - available")
                else:
                    self.failed(f"  ✗ Port {port} ({service}) - not running")
    
    def check_f_drive(self):
        """Check F: drive for RL data"""
        print("\n💾 Checking F: drive...")
        
        f_drive = Path("F:/MCPVotsAGI_Data")
        if f_drive.exists():
            self.passed("F: drive accessible")
            
            # Check subdirectories
            subdirs = ["RL", "models", "knowledge"]
            for subdir in subdirs:
                path = f_drive / subdir
                if path.exists():
                    self.passed(f"  ✓ {subdir} directory")
                else:
                    self.failed(f"  ✗ {subdir} directory missing")
        else:
            self.failed("F: drive not accessible")
            print("  ⚠️  RL data will not be available")
    
    def check_key_files(self):
        """Check key system files"""
        print("\n📄 Checking key files...")
        
        key_files = [
            "src/core/oracle_agi_v9_complete_mcp.py",
            "config/unified_system_config.yaml",
            "requirements.txt",
            "ecosystem_manager.py"
        ]
        
        for file_path in key_files:
            full_path = self.workspace / file_path
            if full_path.exists():
                self.passed(f"  ✓ {file_path}")
            else:
                self.failed(f"  ✗ {file_path} missing")
    
    def check_env_vars(self):
        """Check environment variables"""
        print("\n🔐 Checking environment variables...")
        
        env_vars = [
            "OPENAI_API_KEY",
            "FINNHUB_API_KEY",
            "GITHUB_TOKEN"
        ]
        
        for var in env_vars:
            if os.getenv(var):
                self.passed(f"  ✓ {var} set")
            else:
                self.failed(f"  ✗ {var} not set")
    
    def passed(self, message):
        """Mark check as passed"""
        print(f"✅ {message}")
        self.checks_passed += 1
    
    def failed(self, message):
        """Mark check as failed"""
        print(f"❌ {message}")
        self.checks_failed += 1
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        
        if self.checks_failed == 0:
            print("\n🎉 SYSTEM READY! All checks passed!")
            print("\n🚀 Start with:")
            print("   python src/core/start_unified_dashboard_with_ollama.py")
            print("\n   or double-click: START_AGI_CHAT.bat")
        else:
            print("\n⚠️  SYSTEM NOT READY - Please fix the issues above")
            print("\n📋 Quick fixes:")
            print("   • Install missing packages: pip install -r requirements.txt")
            print("   • Start Ollama: ollama serve")
            print("   • Pull DeepSeek model: ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL")
        
        print("="*70 + "\n")
    
    def run(self):
        """Run all verification checks"""
        self.print_header()
        
        self.check_workspace()
        self.check_python_deps()
        self.check_ollama()
        self.check_ports()
        self.check_f_drive()
        self.check_key_files()
        self.check_env_vars()
        
        self.print_summary()


if __name__ == "__main__":
    verifier = SystemVerifier()
    verifier.run()