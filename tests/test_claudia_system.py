#!/usr/bin/env python3
"""
Simple Claudia/Ollama Verification Script
========================================
Quick test to verify Ollama is working with your models
"""

import requests
import json

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("🔍 Testing Ollama Connection...")
    print("=" * 50)

    try:
        # Test API connection
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama API connected successfully")
            print(f"📊 Found {len(models)} models:")

            # Show available models
            for i, model in enumerate(models):
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                size_gb = size / (1024**3) if size > 0 else 0
                print(f"  {i+1}. {name} ({size_gb:.1f}GB)")

            # Test with the fastest model
            if models:
                test_model = "llama3.2:3b"  # Your fastest model
                print(f"\n🧠 Testing {test_model}...")

                payload = {
                    'model': test_model,
                    'prompt': 'Respond with: "Claudia AI system operational and ready for Ultimate AGI System V3"',
                    'stream': False,
                    'options': {
                        'num_predict': 50,
                        'temperature': 0.1
                    }
                }

                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get('response', 'No response')
                    print(f"✅ Model test successful!")
                    print(f"🤖 AI Response: {ai_response}")
                    print(f"\n🚀 CLAUDIA/OLLAMA SYSTEM: OPERATIONAL")
                    return True
                else:
                    print(f"❌ Model test failed: HTTP {response.status_code}")
                    return False
            else:
                print("❌ No models available")
                return False

        else:
            print(f"❌ Ollama API connection failed: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama (Connection refused)")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_system_status():
    """Show system status"""
    print("\n" + "=" * 50)
    print("🎯 ULTIMATE AGI SYSTEM V3 - CLAUDIA STATUS")
    print("=" * 50)

    if test_ollama_connection():
        print("✅ Status: READY FOR ENHANCED TRADING & ANALYSIS")
        print("🎯 Next: Run enhanced ecosystem launcher")
        print("📝 Command: python launch_claudia_enhanced_ecosystem.py")
    else:
        print("⚠️ Status: CLAUDIA/OLLAMA NOT READY")
        print("🔧 Action Required: Start Ollama server")
        print("📝 Command: ollama serve")

if __name__ == "__main__":
    show_system_status()
