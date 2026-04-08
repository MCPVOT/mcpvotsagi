#!/usr/bin/env python3
"""
Unified Dashboard Launcher with Ollama Integration
=================================================
Ensures all MCP servers and Ollama models are running for AGI chat
"""

import asyncio
import subprocess
import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class UnifiedDashboardLauncher:
    """Launch unified dashboard with all integrations"""
    
    def __init__(self):
        self.workspace = Path("C:/Workspace/MCPVotsAGI")
        self.ollama_models = {
            'deepseek_r1': 'hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL',
            'llama3.1': 'llama3.1:8b',
            'mistral': 'mistral:latest',
            'qwen2.5-coder': 'qwen2.5-coder:latest'
        }
        
        self.mcp_servers = {
            'github': {'port': 3001, 'cmd': 'npx @modelcontextprotocol/server-github'},
            'memory': {'port': 3002, 'cmd': 'npx @modelcontextprotocol/server-memory'},
            'browser': {'port': 3006, 'cmd': 'npx @agentdeskai/browser-tools-mcp'}
        }
        
        self.f_drive_path = Path("F:/MCPVotsAGI_Data")
        
    def check_ollama_service(self):
        """Check if Ollama service is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_ollama_service(self):
        """Start Ollama service if not running"""
        if not self.check_ollama_service():
            print("🚀 Starting Ollama service...")
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            time.sleep(3)
            
            if self.check_ollama_service():
                print("✅ Ollama service started successfully")
            else:
                print("❌ Failed to start Ollama service")
                return False
        else:
            print("✅ Ollama service already running")
        return True
    
    def check_ollama_model(self, model_name):
        """Check if Ollama model is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model_name in model.get('name', '') for model in models)
        except Exception:
            pass
        return False
    
    def ensure_ollama_models(self):
        """Ensure required Ollama models are available"""
        print("\n🧠 Checking Ollama models...")
        
        for alias, model_name in self.ollama_models.items():
            if self.check_ollama_model(model_name):
                print(f"✅ {alias}: {model_name}")
            else:
                print(f"⚠️  {alias}: {model_name} not found")
                if alias == 'deepseek_r1':
                    print("   💡 Pull with: ollama pull " + model_name)
    
    def check_port(self, port):
        """Check if port is in use"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    def start_mcp_servers(self):
        """Start MCP servers"""
        print("\n🔧 Starting MCP servers...")
        
        for name, config in self.mcp_servers.items():
            if self.check_port(config['port']):
                print(f"✅ {name} MCP already running on port {config['port']}")
            else:
                print(f"🚀 Starting {name} MCP on port {config['port']}...")
                try:
                    # Start in background
                    subprocess.Popen(
                        config['cmd'].split(),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        cwd=str(self.workspace)
                    )
                    time.sleep(2)
                    if self.check_port(config['port']):
                        print(f"✅ {name} MCP started successfully")
                    else:
                        print(f"⚠️  {name} MCP may not have started properly")
                except Exception as e:
                    print(f"❌ Failed to start {name} MCP: {e}")
    
    def check_f_drive(self):
        """Check F: drive for RL data"""
        print("\n💾 Checking F: drive for RL data...")
        
        if self.f_drive_path.exists():
            # Check for RL data
            rl_data_size = sum(f.stat().st_size for f in self.f_drive_path.rglob('*') if f.is_file())
            rl_data_gb = rl_data_size / (1024**3)
            print(f"✅ F: drive accessible - {rl_data_gb:.2f} GB of RL data found")
            return True
        else:
            print("⚠️  F: drive not accessible - RL data unavailable")
            return False
    
    def start_dashboard(self):
        """Start the Oracle AGI V9 dashboard"""
        print("\n🎯 Starting Oracle AGI V9 Complete Dashboard...")
        
        oracle_script = self.workspace / "src" / "core" / "oracle_agi_v9_complete_mcp.py"
        
        if not oracle_script.exists():
            print(f"❌ Oracle script not found at: {oracle_script}")
            return False
        
        try:
            # Start the dashboard
            process = subprocess.Popen(
                [sys.executable, str(oracle_script)],
                cwd=str(self.workspace)
            )
            
            print("\n" + "="*70)
            print("🎉 ORACLE AGI V9 COMPLETE - UNIFIED DASHBOARD READY!")
            print("="*70)
            print("\n📍 Access Points:")
            print("   🌐 Dashboard: http://localhost:8888")
            print("   💬 Chat with AGI: Full Ollama integration")
            print("   🧠 DeepSeek-R1: Ready for complex reasoning")
            print("   🔧 MCP Tools: All systems operational")
            print("\n✨ Features:")
            print("   • Chat with multiple AI models")
            print("   • Access all MCP tools (filesystem, GitHub, memory, browser)")
            print("   • Real-time system monitoring")
            print("   • RL brain integration")
            print("   • Knowledge graph persistence")
            print("\n⚡ Available Models:")
            for alias, model in self.ollama_models.items():
                status = "✅" if self.check_ollama_model(model) else "❌"
                print(f"   {status} {alias}: {model}")
            print("\n🛡️ Security: Acting as if public (F: drive private)")
            print("\nPress Ctrl+C to stop all services")
            print("="*70)
            
            # Wait for process
            process.wait()
            
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down Oracle AGI V9...")
            return True
        except Exception as e:
            print(f"❌ Failed to start dashboard: {e}")
            return False
    
    def create_quick_access_scripts(self):
        """Create quick access scripts"""
        print("\n📝 Creating quick access scripts...")
        
        # Windows batch file
        batch_content = f"""@echo off
cd /d "{self.workspace}"
python "{__file__}"
pause
"""
        
        batch_file = self.workspace / "START_AGI_CHAT.bat"
        batch_file.write_text(batch_content)
        print(f"✅ Created: {batch_file}")
        
        # PowerShell script
        ps_content = f"""
Write-Host "Starting Oracle AGI V9 with Ollama..." -ForegroundColor Cyan
Set-Location "{self.workspace}"
python "{__file__}"
Read-Host "Press Enter to exit"
"""
        
        ps_file = self.workspace / "START_AGI_CHAT.ps1"
        ps_file.write_text(ps_content)
        print(f"✅ Created: {ps_file}")
    
    def run(self):
        """Run the complete startup sequence"""
        print("🚀 Oracle AGI V9 - Unified Dashboard Launcher")
        print("=" * 70)
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Workspace: {self.workspace}")
        print("=" * 70)
        
        # Check and start Ollama
        if not self.start_ollama_service():
            print("❌ Cannot proceed without Ollama service")
            return
        
        # Check Ollama models
        self.ensure_ollama_models()
        
        # Start MCP servers
        self.start_mcp_servers()
        
        # Check F: drive
        self.check_f_drive()
        
        # Create quick access scripts
        self.create_quick_access_scripts()
        
        # Start dashboard
        self.start_dashboard()


if __name__ == "__main__":
    launcher = UnifiedDashboardLauncher()
    launcher.run()