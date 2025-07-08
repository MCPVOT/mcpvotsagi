#!/usr/bin/env python3
"""
Claudia Image Analyzer
======================
Analyze images using our local Ollama models for insights and improvements
"""

import base64
import requests
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClaudiaImageAnalyzer")

class ClaudiaImageAnalyzer:
    def __init__(self):
        self.ollama_base = "http://localhost:11434"
        self.vision_models = [
            "llava:latest",
            "moondream:latest",
            "bakllava:latest"
        ]
        self.analysis_models = [
            "deepseek-r1:latest",
            "qwen2.5-coder:latest",
            "llama3.2:3b"
        ]

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return None

    async def analyze_with_vision_model(self, image_path: str, model: str = "llava:latest") -> dict:
        """Analyze image with vision model"""
        try:
            # Check if we have a vision model available
            response = requests.get(f"{self.ollama_base}/api/tags")
            if response.status_code != 200:
                logger.warning("Ollama not available for vision analysis")
                return None

            available_models = [m["name"] for m in response.json().get("models", [])]
            vision_model = None

            for vm in self.vision_models:
                if vm in available_models:
                    vision_model = vm
                    break

            if not vision_model:
                logger.warning("No vision models available, using text analysis")
                return await self.analyze_image_context(image_path)

            # Encode image
            image_b64 = self.encode_image(image_path)
            if not image_b64:
                return None

            # Analyze with vision model
            payload = {
                "model": vision_model,
                "prompt": "Analyze this image in detail. Describe what you see, identify any technical content, code, diagrams, or systems shown. Focus on understanding the context and purpose.",
                "images": [image_b64],
                "stream": False
            }

            response = requests.post(f"{self.ollama_base}/api/generate", json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return {
                    "model": vision_model,
                    "analysis": result.get("response", ""),
                    "type": "vision"
                }

        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return await self.analyze_image_context(image_path)

    async def analyze_image_context(self, image_path: str) -> dict:
        """Analyze image context using filename and available info"""
        try:
            file_path = Path(image_path)
            filename = file_path.name

            # Use our best reasoning model for context analysis
            prompt = f"""
            Analyze this context: An image file named '{filename}' is being examined.

            Based on the filename and context, this appears to be related to:
            - Screen sharing or VNC functionality (suggested by possible connection to remote systems)
            - Development or debugging processes
            - System optimization or troubleshooting

            Provide insights on:
            1. What this might be showing
            2. How it could relate to our Ultimate AGI System V3
            3. Potential improvements we could implement
            4. Technical analysis of the context
            """

            payload = {
                "model": "deepseek-r1:latest",
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(f"{self.ollama_base}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "model": "deepseek-r1:latest",
                    "analysis": result.get("response", ""),
                    "type": "context"
                }

        except Exception as e:
            logger.error(f"Context analysis error: {e}")
            return None

    async def get_improvement_suggestions(self, analysis_result: dict) -> dict:
        """Get improvement suggestions based on analysis"""
        try:
            if not analysis_result:
                return None

            prompt = f"""
            Based on this analysis: {analysis_result.get('analysis', '')}

            Our Ultimate AGI System V3 has:
            - Claudia/Ollama AI integration with 17 models
            - Jupiter DEX trading systems
            - Real-time network monitoring
            - Advanced RL trading algorithms
            - Cyberpunk-themed dashboards
            - Production-ready trading with no mock data

            Provide specific suggestions on how we can:
            1. Improve upon what was analyzed
            2. Integrate relevant features into our system
            3. Enhance user experience
            4. Optimize performance
            5. Add new capabilities

            Focus on actionable improvements.
            """

            payload = {
                "model": "qwen2.5-coder:latest",
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(f"{self.ollama_base}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "model": "qwen2.5-coder:latest",
                    "suggestions": result.get("response", ""),
                    "type": "improvements"
                }

        except Exception as e:
            logger.error(f"Improvement analysis error: {e}")
            return None

    async def generate_implementation_plan(self, improvements: dict) -> dict:
        """Generate implementation plan for improvements"""
        try:
            if not improvements:
                return None

            prompt = f"""
            Based on these improvement suggestions: {improvements.get('suggestions', '')}

            Create a concrete implementation plan for our Ultimate AGI System V3:

            1. Immediate Actions (next 1-2 hours)
            2. Short-term Goals (next 1-2 days)
            3. Medium-term Enhancements (next week)
            4. Long-term Vision (next month)

            For each item, specify:
            - File(s) to modify
            - Code changes needed
            - Dependencies required
            - Expected benefits

            Focus on practical, actionable steps.
            """

            payload = {
                "model": "deepseek-r1:latest",
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(f"{self.ollama_base}/api/generate", json=payload, timeout=45)
            if response.status_code == 200:
                result = response.json()
                return {
                    "model": "deepseek-r1:latest",
                    "plan": result.get("response", ""),
                    "type": "implementation"
                }

        except Exception as e:
            logger.error(f"Implementation planning error: {e}")
            return None

async def main():
    """Main analysis function"""
    print("🔍 CLAUDIA IMAGE ANALYZER")
    print("=" * 50)

    analyzer = ClaudiaImageAnalyzer()
    image_path = r"C:\Workspace\MCPVotsAGI\GvGSsPlXwAAVvS6.jpg"

    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return

    print(f"📸 Analyzing: {Path(image_path).name}")
    print(f"🕒 Started at: {datetime.now().strftime('%H:%M:%S')}")

    # Step 1: Initial Analysis
    print("\n🔍 Step 1: Image Analysis...")
    analysis = await analyzer.analyze_with_vision_model(image_path)

    if analysis:
        print(f"✅ Analysis completed with {analysis['model']}")
        print(f"📊 Type: {analysis['type']}")
        print(f"📝 Analysis:\n{analysis['analysis'][:500]}...")
    else:
        print("❌ Analysis failed")
        return

    # Step 2: Get Improvements
    print("\n💡 Step 2: Generating Improvements...")
    improvements = await analyzer.get_improvement_suggestions(analysis)

    if improvements:
        print(f"✅ Improvements generated with {improvements['model']}")
        print(f"📝 Suggestions:\n{improvements['suggestions'][:500]}...")

    # Step 3: Implementation Plan
    print("\n📋 Step 3: Creating Implementation Plan...")
    implementation = await analyzer.generate_implementation_plan(improvements)

    if implementation:
        print(f"✅ Implementation plan created with {implementation['model']}")
        print(f"📝 Plan:\n{implementation['plan'][:500]}...")

    # Save full results
    results = {
        "timestamp": datetime.now().isoformat(),
        "image": str(image_path),
        "analysis": analysis,
        "improvements": improvements,
        "implementation": implementation
    }

    output_file = f"claudia_image_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Full results saved to: {output_file}")
    print(f"🕒 Completed at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
