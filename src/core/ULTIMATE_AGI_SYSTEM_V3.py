#!/usr/bin/env python3
"""
ULTIMATE AGI SYSTEM V3 - Enhanced with Context7 Documentation
============================================================
🚀 Now with real-time, accurate library documentation for better code generation
"""

import asyncio
import json
import os
import sys
import time
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import V2 base system
try:
    from ULTIMATE_AGI_SYSTEM_V2 import UltimateAGISystemV2
    HAS_V2 = True
except ImportError:
    logger.error("V2 system not found - creating from scratch")
    HAS_V2 = False

# Import Context7 integration
try:
    from CONTEXT7_INTEGRATION import (
        Context7Integration, 
        Context7CodeAssistant,
        create_context7_integration
    )
    HAS_CONTEXT7 = True
except ImportError:
    Context7Integration = None
    HAS_CONTEXT7 = False
    logger.warning("Context7 integration not available")


class UltimateAGISystemV3(UltimateAGISystemV2 if HAS_V2 else object):
    """Enhanced ULTIMATE AGI system with Context7 documentation"""
    
    def __init__(self):
        """Initialize V3 system with Context7"""
        if HAS_V2:
            super().__init__()
            self.version = "ULTIMATE-V3.0"
        else:
            # Minimal initialization if V2 not available
            self.version = "ULTIMATE-V3.0"
            self.port = int(os.environ.get('AGI_PORT', 8888))
            self.start_time = time.time()
            
        # Context7 components
        self.context7 = None
        self.code_assistant = None
        
        # Enhanced features
        self.documentation_cache = {}
        self.library_usage_stats = {}
        
        logger.info(f"🚀 ULTIMATE AGI SYSTEM V3 initialized - Now with Context7!")
    
    async def initialize_all_systems(self):
        """Initialize all systems including Context7"""
        # Initialize V2 systems first
        if HAS_V2:
            await super().initialize_all_systems()
        
        # Initialize Context7
        if HAS_CONTEXT7:
            await self._init_context7()
        
        logger.info("✅ All V3 systems initialized")
    
    async def _init_context7(self):
        """Initialize Context7 documentation system"""
        logger.info("Initializing Context7 documentation system...")
        
        try:
            self.context7 = await create_context7_integration()
            
            if self.context7:
                self.code_assistant = Context7CodeAssistant(self.context7)
                logger.info("✅ Context7 documentation system ready")
                
                # Pre-cache popular libraries
                await self._precache_popular_libraries()
            else:
                logger.warning("⚠️ Context7 server not available")
                
        except Exception as e:
            logger.error(f"Context7 initialization error: {e}")
    
    async def _precache_popular_libraries(self):
        """Pre-cache documentation for popular libraries"""
        popular_libs = ['react', 'nextjs', 'fastapi', 'langchain', 'openai']
        
        logger.info("Pre-caching popular library documentation...")
        
        for lib in popular_libs:
            try:
                await self.context7.enrich_context(f"import {lib}", max_tokens=5000)
                logger.info(f"  ✓ Cached {lib}")
            except Exception as e:
                logger.warning(f"  ✗ Failed to cache {lib}: {e}")
    
    async def handle_chat(self, request):
        """Enhanced chat handler with Context7 documentation"""
        data = await request.json()
        message = data.get('message', '')
        
        # Track library usage
        self._track_library_usage(message)
        
        # Check if this is a coding request
        if self._is_coding_request(message):
            # Enrich with documentation
            enriched_response = await self._handle_coding_with_docs(message)
            return enriched_response
        
        # Fall back to V2 handler for non-coding requests
        if HAS_V2:
            return await super().handle_chat(request)
        else:
            # Simple response if V2 not available
            from aiohttp import web
            return web.json_response({
                'response': f"Processing: {message}",
                'timestamp': datetime.now().isoformat()
            })
    
    async def _handle_coding_with_docs(self, message: str) -> Any:
        """Handle coding requests with accurate documentation"""
        from aiohttp import web
        
        response_data = {
            'query': message,
            'timestamp': datetime.now().isoformat(),
            'documentation_enriched': False
        }
        
        if self.context7:
            # Enrich context with documentation
            enriched = await self.context7.enrich_context(message)
            
            if enriched.get('enriched'):
                response_data['documentation_enriched'] = True
                response_data['libraries_detected'] = enriched['libraries_detected']
                response_data['documentation_tokens'] = enriched['total_tokens']
                
                # Generate enhanced response
                enhanced_result = await self.code_assistant.generate_code_with_docs(message)
                
                # Here you would call your AI model with enhanced context
                # For now, we'll create a structured response
                response_data['response'] = self._create_documented_response(
                    message, 
                    enriched,
                    enhanced_result
                )
            else:
                response_data['response'] = await self._get_ai_response(message)
        else:
            response_data['response'] = await self._get_ai_response(message)
        
        return web.json_response(response_data)
    
    def _is_coding_request(self, message: str) -> bool:
        """Detect if message is a coding/programming request"""
        coding_indicators = [
            'code', 'function', 'class', 'implement', 'create',
            'build', 'write', 'program', 'script', 'api',
            'component', 'module', 'library', 'package',
            'debug', 'fix', 'error', 'bug', 'issue'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in coding_indicators)
    
    def _track_library_usage(self, message: str):
        """Track which libraries are being asked about"""
        if self.context7:
            libraries = self.context7.detect_libraries(message)
            for lib in libraries:
                self.library_usage_stats[lib] = self.library_usage_stats.get(lib, 0) + 1
    
    def _create_documented_response(self, query: str, enriched: Dict, enhanced: Dict) -> str:
        """Create a response with documentation context"""
        response_parts = []
        
        # Header
        response_parts.append("📚 **Code Assistant Response** (with up-to-date documentation)\n")
        
        # Libraries detected
        if enriched['libraries_detected']:
            response_parts.append(f"🔍 **Libraries detected**: {', '.join(enriched['libraries_detected'])}")
            response_parts.append(f"📊 **Documentation tokens**: {enriched['total_tokens']}\n")
        
        # Main response (this would come from your AI model)
        response_parts.append("**Solution**:")
        response_parts.append("```python")
        response_parts.append("# Your code here with accurate, current APIs")
        response_parts.append("# Based on official documentation")
        response_parts.append("```")
        
        # Add relevant examples if available
        if enriched.get('documentation'):
            response_parts.append("\n**Reference Documentation**:")
            for lib, docs in enriched['documentation'].items():
                if 'version' in docs:
                    response_parts.append(f"- {lib} v{docs['version']}")
        
        return '\n'.join(response_parts)
    
    async def _get_ai_response(self, message: str) -> str:
        """Get AI response (fallback without documentation)"""
        # This would call your actual AI model
        # For now, return a placeholder
        return f"Processing your request: {message}"
    
    async def handle_documentation_request(self, request):
        """Handle direct documentation requests"""
        from aiohttp import web
        
        data = await request.json()
        library = data.get('library')
        topic = data.get('topic')
        
        if not self.context7:
            return web.json_response({
                'error': 'Context7 not available'
            })
        
        # Get documentation
        docs = await self.context7._get_library_docs({
            'library': library,
            'topic': topic,
            'maxTokens': data.get('maxTokens', 10000)
        })
        
        return web.json_response(docs)
    
    async def handle_code_examples_request(self, request):
        """Get code examples for a library"""
        from aiohttp import web
        
        data = await request.json()
        library = data.get('library')
        topic = data.get('topic')
        
        if not self.context7:
            return web.json_response({
                'error': 'Context7 not available'
            })
        
        examples = await self.context7.get_library_examples(library, topic)
        return web.json_response(examples)
    
    def setup_routes(self):
        """Setup routes including Context7 endpoints"""
        # Call parent setup if available
        if HAS_V2:
            super().setup_routes()
        
        # Add Context7-specific routes
        if hasattr(self, 'app'):
            self.app.router.add_post('/api/documentation', self.handle_documentation_request)
            self.app.router.add_post('/api/examples', self.handle_code_examples_request)
            self.app.router.add_get('/api/library-stats', self.get_library_stats)
    
    async def get_library_stats(self, request):
        """Get library usage statistics"""
        from aiohttp import web
        
        stats = {
            'most_requested': sorted(
                self.library_usage_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'total_requests': sum(self.library_usage_stats.values()),
            'unique_libraries': len(self.library_usage_stats),
            'context7_available': self.context7 is not None
        }
        
        return web.json_response(stats)
    
    async def get_system_status(self, request):
        """Enhanced status with Context7 info"""
        if HAS_V2:
            # Get V2 status
            base_status = await super().get_system_status(request)
            status_data = json.loads(base_status.text)
        else:
            status_data = {
                'status': 'online',
                'version': self.version,
                'uptime': int(time.time() - self.start_time)
            }
        
        # Add Context7 status
        status_data['context7_status'] = 'online' if self.context7 and self.context7.connected else 'offline'
        status_data['documentation_cache_size'] = len(self.documentation_cache)
        status_data['libraries_tracked'] = len(self.library_usage_stats)
        
        from aiohttp import web
        return web.json_response(status_data)
    
    async def cleanup(self):
        """Cleanup resources on shutdown"""
        if self.context7:
            await self.context7.stop_server()
        
        # Call parent cleanup if available
        if HAS_V2 and hasattr(super(), 'cleanup'):
            await super().cleanup()


async def main():
    """Main entry point for V3"""
    # Fix encoding for Windows
    if sys.platform == 'win32':
        subprocess.run('chcp 65001', shell=True, capture_output=True)
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                  ULTIMATE AGI SYSTEM V3.0                        ║
    ║                                                                  ║
    ║  🚀 Now with Context7: Real-time, accurate documentation        ║
    ║  📚 No more hallucinated APIs - always current                  ║
    ║  🔍 Automatic library detection and documentation               ║
    ║  💡 Better code generation with verified examples               ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    system = UltimateAGISystemV3()
    
    # Create minimal web app if V2 not available
    if not HAS_V2:
        from aiohttp import web
        system.app = web.Application()
        system.setup_routes()
    
    await system.initialize_all_systems()
    
    # Start web server
    from aiohttp import web
    runner = web.AppRunner(system.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', system.port)
    await site.start()
    
    print(f"\n✅ System running at: http://localhost:{system.port}")
    print(f"✅ Context7 documentation: {'enabled' if system.context7 else 'disabled'}")
    print(f"✅ Code assistant: {'ready' if system.code_assistant else 'not available'}")
    
    print("\n📝 Try these enhanced features:")
    print("  - Ask about any programming library for accurate docs")
    print("  - Request code examples with current APIs")
    print("  - Get version-specific documentation")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\nShutting down...")
        await system.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()