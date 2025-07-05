#!/usr/bin/env python3
"""
Context7 Integration for ULTIMATE AGI SYSTEM
============================================
Provides real-time, accurate documentation context for programming assistance
"""

import asyncio
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Context7Integration:
    """Integrates Context7 MCP server for real-time documentation"""

    def __init__(self, port: int = 3000):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.mcp_process = None
        self.connected = False
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)
        self.session = None  # Persistent session to avoid unclosed warnings

        # Common libraries to detect
        self.common_libraries = {
            'react': ['react', 'jsx', 'hooks', 'component', 'useState', 'useEffect'],
            'nextjs': ['next', 'nextjs', 'getServerSideProps', 'getStaticProps', 'app router'],
            'vue': ['vue', 'vuejs', 'v-model', 'computed', 'ref', 'reactive'],
            'express': ['express', 'app.get', 'app.post', 'middleware', 'router'],
            'django': ['django', 'models.py', 'views.py', 'urls.py', 'admin.py'],
            'fastapi': ['fastapi', 'pydantic', 'async def', 'router', 'dependency'],
            'numpy': ['numpy', 'np.array', 'ndarray', 'np.', 'matrix'],
            'pandas': ['pandas', 'pd.DataFrame', 'df.', 'Series', 'read_csv'],
            'tensorflow': ['tensorflow', 'tf.', 'keras', 'model.fit', 'Dense'],
            'torch': ['torch', 'pytorch', 'tensor', 'nn.Module', 'optimizer'],
            'langchain': ['langchain', 'chain', 'llm', 'prompt', 'memory'],
            'openai': ['openai', 'gpt', 'completion', 'embedding', 'chat']
        }

        # MCP tools provided by Context7
        self.tools = {
            'get_library_docs': self._get_library_docs,
            'search_libraries': self._search_libraries,
            'resolve_library': self._resolve_library
        }

    async def _get_session(self):
        """Get or create persistent session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close the persistent session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def start_server(self) -> bool:
        """Start the Context7 MCP server"""
        try:
            # Check if already running
            if await self._check_server_health():
                logger.info("Context7 server already running")
                self.connected = True
                return True

            # Try different methods to start Context7
            commands_to_try = [
                # Try with npx.cmd on Windows
                ['npx.cmd', '-y', '@upstash/context7-mcp', '--transport', 'http', '--port', str(self.port)],
                # Try with full path to npm on Windows
                ['C:\\Program Files\\nodejs\\npx.cmd', '-y', '@upstash/context7-mcp', '--transport', 'http', '--port', str(self.port)],
                # Try with regular npx
                ['npx', '-y', '@upstash/context7-mcp', '--transport', 'http', '--port', str(self.port)]
            ]

            for cmd in commands_to_try:
                try:
                    self.mcp_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=str(Path(__file__).parent.parent.parent),
                        shell=True if cmd[0].endswith('.cmd') else False
                    )

                    # Wait for server to start
                    await asyncio.sleep(3)

                    # Check health
                    if await self._check_server_health():
                        self.connected = True
                        logger.info(f"✅ Context7 MCP server started on port {self.port}")
                        return True
                except Exception as e:
                    logger.debug(f"Failed with command {cmd[0]}: {e}")
                    if self.mcp_process:
                        try:
                            self.mcp_process.terminate()
                        except:
                            pass
                        self.mcp_process = None
                    continue

            # If all methods fail, work in offline mode
            logger.warning("⚠️ Context7 not available - documentation enrichment disabled")
            self.connected = False
            return False

        except Exception as e:
            logger.error(f"Error starting Context7 server: {e}")
            logger.warning("⚠️ Context7 not available - documentation enrichment disabled")
            return False

    async def stop_server(self):
        """Stop the Context7 MCP server"""
        # Close the session first
        await self.close_session()

        if self.mcp_process:
            self.mcp_process.terminate()
            self.mcp_process = None
        self.connected = False
        logger.info("Context7 server stopped")

    async def _check_server_health(self) -> bool:
        """Check if Context7 server is healthy"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/health") as resp:
                return resp.status == 200
        except:
            return False

    def detect_libraries(self, text: str) -> Set[str]:
        """Detect library references in text"""
        detected = set()
        text_lower = text.lower()

        for library, keywords in self.common_libraries.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.add(library)

        # Also check for explicit library mentions
        # Pattern: import X, from X import, require('X'), using X
        import_patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)\s+import',
            r'require\([\'"](\w+)[\'"]\)',
            r'using\s+(\w+)',
            r'pip install\s+(\w+)',
            r'npm install\s+(\w+)'
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            detected.update(matches)

        return detected

    async def enrich_context(self, user_query: str, max_tokens: int = 10000) -> Dict:
        """Enrich context with relevant library documentation"""
        if not self.connected:
            if not await self.start_server():
                return {
                    'error': 'Context7 server not available',
                    'enriched': False
                }

        # Detect libraries in query
        libraries = self.detect_libraries(user_query)

        if not libraries:
            return {
                'enriched': False,
                'message': 'No libraries detected in query'
            }

        enriched_context = {
            'query': user_query,
            'libraries_detected': list(libraries),
            'documentation': {},
            'total_tokens': 0,
            'timestamp': datetime.now().isoformat()
        }

        # Fetch documentation for each library
        for library in libraries:
            # Check cache first
            cache_key = f"{library}:{max_tokens}"
            if cache_key in self.cache:
                cached_data, cache_time = self.cache[cache_key]
                if datetime.now() - cache_time < self.cache_ttl:
                    enriched_context['documentation'][library] = cached_data
                    enriched_context['total_tokens'] += cached_data.get('tokens', 0)
                    continue

            # Fetch from Context7
            try:
                docs = await self._get_library_docs({
                    'library': library,
                    'maxTokens': max_tokens
                })

                if docs.get('success'):
                    enriched_context['documentation'][library] = docs['data']
                    enriched_context['total_tokens'] += docs['data'].get('tokens', 0)

                    # Cache the result
                    self.cache[cache_key] = (docs['data'], datetime.now())

            except Exception as e:
                logger.error(f"Error fetching docs for {library}: {e}")

        enriched_context['enriched'] = len(enriched_context['documentation']) > 0
        return enriched_context

    async def _get_library_docs(self, params: Dict) -> Dict:
        """Get documentation for a specific library"""
        library = params.get('library')
        max_tokens = params.get('maxTokens', 10000)
        topic = params.get('topic')

        # Call MCP endpoint
        payload = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'get-library-docs',
                'arguments': {
                    'library': library,
                    'maxTokens': max_tokens
                }
            },
            'id': 1
        }

        if topic:
            payload['params']['arguments']['topic'] = topic

        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/mcp/v1",
                json=payload
            ) as resp:
                result = await resp.json()

                if 'error' in result:
                    return {'success': False, 'error': result['error']}

                return {
                    'success': True,
                    'data': result.get('result', {})
                    }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _search_libraries(self, params: Dict) -> Dict:
        """Search for libraries matching a query"""
        query = params.get('query', '')

        payload = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'search-libraries',
                'arguments': {
                    'query': query
                }
            },
            'id': 1
        }

        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/mcp/v1",
                json=payload
                ) as resp:
                    result = await resp.json()
                    return result.get('result', {})
        except Exception as e:
            return {'error': str(e)}

    async def _resolve_library(self, params: Dict) -> Dict:
        """Resolve a library identifier to its full details"""
        library = params.get('library')

        payload = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'resolve-library',
                'arguments': {
                    'library': library
                }
            },
            'id': 1
        }

        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/mcp/v1",
                json=payload
                ) as resp:
                    result = await resp.json()
                    return result.get('result', {})
        except Exception as e:
            return {'error': str(e)}

    async def get_library_examples(self, library: str, topic: Optional[str] = None) -> Dict:
        """Get code examples for a library"""
        params = {
            'library': library,
            'maxTokens': 5000  # Smaller limit for examples
        }

        if topic:
            params['topic'] = topic

        docs = await self._get_library_docs(params)

        if docs.get('success'):
            # Extract code examples from documentation
            examples = self._extract_code_examples(docs['data'])
            return {
                'library': library,
                'topic': topic,
                'examples': examples,
                'count': len(examples)
            }

        return {'error': 'Failed to fetch examples'}

    def _extract_code_examples(self, docs_data: Dict) -> List[Dict]:
        """Extract code examples from documentation"""
        examples = []

        # This is a simplified extraction - Context7 may provide structured examples
        content = docs_data.get('content', '')

        # Find code blocks (markdown style)
        code_blocks = re.findall(r'```(?:[\w]+)?\n(.*?)\n```', content, re.DOTALL)

        for i, code in enumerate(code_blocks):
            examples.append({
                'index': i,
                'code': code.strip(),
                'language': self._detect_language(code)
            })

        return examples

    def _detect_language(self, code: str) -> str:
        """Simple language detection based on syntax"""
        if 'import React' in code or 'jsx' in code:
            return 'javascript'
        elif 'def ' in code or 'import ' in code:
            return 'python'
        elif 'function' in code or 'const ' in code:
            return 'javascript'
        elif '<template>' in code:
            return 'vue'
        else:
            return 'unknown'

    def format_enriched_context(self, enriched_data: Dict) -> str:
        """Format enriched context for display"""
        if not enriched_data.get('enriched'):
            return "No library documentation added to context."

        output = []
        output.append(f"📚 Enriched Context for Query: {enriched_data['query'][:100]}...")
        output.append(f"🔍 Libraries Detected: {', '.join(enriched_data['libraries_detected'])}")
        output.append(f"📊 Total Tokens: {enriched_data['total_tokens']}")

        for library, docs in enriched_data['documentation'].items():
            output.append(f"\n📖 {library.upper()} Documentation:")
            if 'summary' in docs:
                output.append(f"   Summary: {docs['summary']}")
            if 'version' in docs:
                output.append(f"   Version: {docs['version']}")
            if 'trustScore' in docs:
                output.append(f"   Trust Score: {docs['trustScore']}/100")

        return '\n'.join(output)


# Utility class for Context7-enhanced code generation
class Context7CodeAssistant:
    """Code assistant enhanced with Context7 documentation"""

    def __init__(self, context7: Context7Integration):
        self.context7 = context7

    async def generate_code_with_docs(self, request: str) -> Dict:
        """Generate code with accurate, up-to-date documentation"""
        # Enrich context first
        enriched = await self.context7.enrich_context(request)

        if enriched.get('enriched'):
            # Add documentation to prompt
            enhanced_prompt = self._build_enhanced_prompt(request, enriched)

            # Here you would call your AI model with the enhanced prompt
            # For now, return the structure
            return {
                'original_request': request,
                'enhanced_prompt': enhanced_prompt,
                'libraries_used': enriched['libraries_detected'],
                'documentation_included': True,
                'tokens_used': enriched['total_tokens']
            }

        return {
            'original_request': request,
            'enhanced_prompt': request,
            'documentation_included': False
        }

    def _build_enhanced_prompt(self, request: str, enriched: Dict) -> str:
        """Build an enhanced prompt with documentation context"""
        prompt_parts = [
            "You have access to the following up-to-date documentation:",
            ""
        ]

        for library, docs in enriched['documentation'].items():
            prompt_parts.append(f"=== {library.upper()} Documentation ===")
            if 'content' in docs:
                # Truncate if too long
                content = docs['content']
                if len(content) > 1000:
                    content = content[:1000] + "..."
                prompt_parts.append(content)
            prompt_parts.append("")

        prompt_parts.append("User Request:")
        prompt_parts.append(request)
        prompt_parts.append("")
        prompt_parts.append("Please provide code that uses the correct, current APIs as shown in the documentation above.")

        return '\n'.join(prompt_parts)


# Integration function for ULTIMATE AGI SYSTEM
async def create_context7_integration(port: int = 3000) -> Context7Integration:
    """Create and initialize Context7 integration"""
    integration = Context7Integration(port)

    if await integration.start_server():
        logger.info("✅ Context7 integration ready")
        return integration
    else:
        logger.warning("⚠️ Context7 not available - documentation enrichment disabled")
        return None


# Test the integration
async def test_context7():
    """Test Context7 integration"""
    print("Testing Context7 Integration...")

    integration = await create_context7_integration()

    if integration:
        # Test library detection
        test_queries = [
            "How do I use React hooks?",
            "Create a FastAPI endpoint with Pydantic validation",
            "Train a neural network with PyTorch",
            "Build a Next.js app with server components"
        ]

        for query in test_queries:
            print(f"\n📝 Query: {query}")

            # Detect libraries
            libraries = integration.detect_libraries(query)
            print(f"🔍 Detected libraries: {libraries}")

            # Enrich context
            enriched = await integration.enrich_context(query, max_tokens=5000)
            formatted = integration.format_enriched_context(enriched)
            print(formatted)

        # Test code assistant
        print("\n🤖 Testing Code Assistant...")
        assistant = Context7CodeAssistant(integration)

        result = await assistant.generate_code_with_docs(
            "Create a React component with useState and useEffect"
        )
        print(f"Enhanced prompt tokens: {result.get('tokens_used', 0)}")

        await integration.stop_server()
    else:
        print("Context7 not available for testing")

    print("\n✅ Context7 Integration Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_context7())