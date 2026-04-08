#!/usr/bin/env python3
"""
Claudia-Ollama DGM Integration Helper
====================================
Uses Claudia AI system and Ollama models to analyze and fix DGM integration issues
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import logging
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ClaudiaOllamaDGMHelper")

class ClaudiaOllamaHelper:
    """AI-powered DGM integration assistant"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.ollama_url = "http://localhost:11434"
        self.models = ["deepseek-coder", "codellama", "llama3.2", "qwen2.5-coder"]
        self.issues_found = []

    async def check_ollama_status(self) -> bool:
        """Check if Ollama is running and available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        available_models = [model["name"] for model in data.get("models", [])]
                        logger.info(f"✅ Ollama is running with {len(available_models)} models")

                        # Find best available model
                        for model in self.models:
                            if any(model in available for available in available_models):
                                self.best_model = model
                                logger.info(f"🎯 Using model: {model}")
                                return True

                        # Use first available model if none of preferred ones
                        if available_models:
                            self.best_model = available_models[0].split(":")[0]
                            logger.info(f"🎯 Using available model: {self.best_model}")
                            return True

                        logger.warning("⚠️ No models available in Ollama")
                        return False
                    else:
                        logger.error(f"❌ Ollama returned status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to Ollama: {e}")
            return False

    async def query_ollama(self, prompt: str, context: str = "") -> str:
        """Query Ollama model for assistance"""
        try:
            full_prompt = f"""
You are an expert Python developer specializing in AI trading systems and async web services.

Context: {context}

Task: {prompt}

Please provide a concise, practical solution focusing on:
1. Fixing import/initialization errors
2. Making services runnable with proper main() functions
3. Ensuring compatibility with aiohttp web framework
4. Using proper async/await patterns

Response should be actionable Python code or specific instructions.
"""

            payload = {
                "model": self.best_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "No response generated")
                    else:
                        return f"Error: HTTP {response.status}"

        except Exception as e:
            logger.error(f"❌ Ollama query failed: {e}")
            return f"Error querying Ollama: {str(e)}"

    async def analyze_dgm_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a DGM file for issues"""
        logger.info(f"🔍 Analyzing {file_path.name}")

        try:
            content = file_path.read_text(encoding='utf-8')

            # Analyze with Ollama
            analysis_prompt = f"""
Analyze this Python file for common issues:
1. Missing required arguments in class initialization
2. Missing main() function or entry point
3. Import errors or missing dependencies
4. Async/await compatibility issues
5. Web service integration problems

File: {file_path.name}
Content length: {len(content)} characters

Find and list specific issues with line numbers if possible.
"""

            analysis = await self.query_ollama(analysis_prompt, content[:3000])  # First 3k chars for context

            return {
                'file': str(file_path),
                'size': len(content),
                'analysis': analysis,
                'has_main': 'if __name__ == "__main__"' in content,
                'has_asyncio': 'asyncio.run(' in content,
                'has_aiohttp': 'from aiohttp import' in content
            }

        except Exception as e:
            logger.error(f"❌ Failed to analyze {file_path}: {e}")
            return {'file': str(file_path), 'error': str(e)}

    async def fix_initialization_error(self, file_path: Path, error_msg: str) -> str:
        """Fix specific initialization errors using Ollama"""
        logger.info(f"🔧 Fixing initialization error in {file_path.name}")

        content = file_path.read_text(encoding='utf-8')

        fix_prompt = f"""
Fix this Python initialization error:

Error: {error_msg}

The error suggests a class is missing required arguments.
Please provide the specific code fix to resolve this initialization issue.

Focus on:
1. Identifying the problematic class constructor
2. Providing default arguments or proper initialization
3. Ensuring the fix is minimal and maintains functionality

Provide only the corrected code section, not the entire file.
"""

        fix_suggestion = await self.query_ollama(fix_prompt, content[:2000])
        return fix_suggestion

    async def create_service_wrapper(self, file_path: Path) -> str:
        """Create a web service wrapper for a DGM module"""
        logger.info(f"🏗️ Creating service wrapper for {file_path.name}")

        content = file_path.read_text(encoding='utf-8')

        wrapper_prompt = f"""
Create a minimal aiohttp web service wrapper for this Python module.

The wrapper should:
1. Import the main classes from the module
2. Create a simple web service with health check endpoint
3. Handle initialization errors gracefully
4. Use port 8004 for dgm_trading_algorithms_v2 or 8005 for dgm_trading_algorithms
5. Include basic error handling

Module file: {file_path.name}

Provide a complete, runnable web service wrapper.
"""

        wrapper_code = await self.query_ollama(wrapper_prompt, content[:1500])
        return wrapper_code

    async def run_comprehensive_analysis(self):
        """Run comprehensive DGM integration analysis"""
        logger.info("🎯 Starting Claudia-Ollama DGM Analysis")

        # Check Ollama availability
        if not await self.check_ollama_status():
            logger.error("❌ Ollama is not available. Please start Ollama service.")
            return

        # Analyze DGM files
        dgm_files = [
            self.project_root / "dgm_evolution_connector.py",
            self.project_root / "src/trading/dgm_trading_algorithms_v2.py",
            self.project_root / "src/trading/dgm_trading_algorithms.py"
        ]

        analysis_results = []
        for file_path in dgm_files:
            if file_path.exists():
                result = await self.analyze_dgm_file(file_path)
                analysis_results.append(result)
            else:
                logger.warning(f"⚠️ File not found: {file_path}")

        # Generate fixes for identified issues
        logger.info("🔧 Generating AI-powered fixes...")

        # Fix the specific initialization error we know about
        v2_file = self.project_root / "src/trading/dgm_trading_algorithms_v2.py"
        if v2_file.exists():
            error_msg = "EnhancedDynamicGodelMachine.__init__() missing 1 required positional argument: 'initial_strategy'"
            fix = await self.fix_initialization_error(v2_file, error_msg)

            logger.info("💡 AI Suggested Fix:")
            print("=" * 60)
            print(fix)
            print("=" * 60)

        # Create report
        report = {
            'timestamp': '2025-07-07T21:00:00',
            'ollama_model': self.best_model,
            'files_analyzed': len(analysis_results),
            'analysis_results': analysis_results,
            'recommendations': [
                "Fix class initialization errors with default parameters",
                "Add proper web service entry points to all DGM modules",
                "Implement graceful error handling for missing dependencies",
                "Create unified service launcher with dependency management"
            ]
        }

        # Save report
        report_file = self.project_root / "claudia_ollama_dgm_analysis.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📄 Analysis report saved to {report_file}")
        return report

async def main():
    """Main function"""
    helper = ClaudiaOllamaHelper()

    print("🤖 Claudia-Ollama DGM Integration Helper")
    print("=" * 50)
    print("This AI assistant will help analyze and fix DGM integration issues")
    print("using Claudia intelligence and Ollama language models.\n")

    try:
        report = await helper.run_comprehensive_analysis()

        if report:
            print("\n✅ AI Analysis Complete!")
            print(f"📊 Analyzed {report['files_analyzed']} files")
            print(f"🤖 Used model: {report['ollama_model']}")
            print("\n🔧 Next steps:")
            print("1. Review the AI-generated fixes above")
            print("2. Apply the suggested code changes")
            print("3. Test the services individually")
            print("4. Re-run the DGM integration analysis")

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
