#!/usr/bin/env python3
"""
MCP Chrome Integration for ULTIMATE AGI SYSTEM
==============================================
Browser automation and web intelligence capabilities
"""

import asyncio
import json
import logging
from typing import Optional
from pathlib import Path
import aiohttp
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPChromeIntegration:
    """Advanced browser automation using MCP Chrome"""
    
    def __init__(self, port: int = 3000):
        self.base_url = f"http://localhost:{port}"
        self.mcp_url = f"{self.base_url}/mcp/v1"
        self.connected = False
        self.session = None
        
        # Available MCP Chrome tools
        self.tools = {
            'navigate': self._navigate,
            'screenshot': self._screenshot,
            'extract_content': self._extract_content,
            'fill_form': self._fill_form,
            'click': self._click,
            'search_tabs': self._search_tabs,
            'monitor_network': self._monitor_network,
            'execute_script': self._execute_script,
            'get_cookies': self._get_cookies,
            'wait_for_element': self._wait_for_element
        }
    
    async def connect(self) -> bool:
        """Connect to MCP Chrome server"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Check health endpoint
            async with self.session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.connected = True
                    logger.info(f"✅ Connected to MCP Chrome: {data}")
                    return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP Chrome: {e}")
            if self.session:
                await self.session.close()
            self.connected = False
        
        return False
    
    async def disconnect(self):
        """Disconnect from MCP Chrome"""
        if self.session:
            await self.session.close()
        self.connected = False
    
    async def execute_tool(self, tool_name: str, params: Dict) -> dict:
        """Execute an MCP Chrome tool"""
        if not self.connected:
            return {'error': 'Not connected to MCP Chrome'}
        
        if tool_name not in self.tools:
            return {'error': f'Unknown tool: {tool_name}'}
        
        try:
            return await self.tools[tool_name](params)
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {'error': str(e)}
    
    async def _call_mcp(self, method: str, params: Dict) -> dict:
        """Call MCP Chrome API"""
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': 1
        }
        
        async with self.session.post(
            self.mcp_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        ) as resp:
            result = await resp.json()
            
            if 'error' in result:
                raise Exception(result['error'])
            
            return result.get('result', {})
    
    async def _navigate(self, params: Dict) -> dict:
        """Navigate to a URL"""
        url = params.get('url')
        if not url:
            return {'error': 'URL required'}
        
        result = await self._call_mcp('navigation.navigate', {
            'url': url,
            'wait_until': params.get('wait_until', 'load')
        })
        
        return {
            'status': 'success',
            'url': url,
            'title': result.get('title'),
            'loaded': result.get('loaded', True)
        }
    
    async def _screenshot(self, params: Dict) -> dict:
        """Take a screenshot"""
        result = await self._call_mcp('page.screenshot', {
            'full_page': params.get('full_page', False),
            'format': params.get('format', 'png')
        })
        
        # Decode base64 image if needed
        image_data = result.get('data', '')
        
        # Optionally save to file
        if params.get('save_to'):
            save_path = Path(params['save_to'])
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
            
            return {
                'status': 'success',
                'saved_to': str(save_path),
                'size': len(base64.b64decode(image_data))
            }
        
        return {
            'status': 'success',
            'data': image_data,
            'format': params.get('format', 'png')
        }
    
    async def _extract_content(self, params: Dict) -> dict:
        """Extract content from current page"""
        selector = params.get('selector', 'body')
        
        result = await self._call_mcp('content.extract', {
            'selector': selector,
            'include_text': params.get('include_text', True),
            'include_html': params.get('include_html', False),
            'include_attributes': params.get('include_attributes', False)
        })
        
        return {
            'status': 'success',
            'content': result.get('content', ''),
            'elements_found': result.get('count', 0)
        }
    
    async def _fill_form(self, params: Dict) -> dict:
        """Fill form fields"""
        fields = params.get('fields', {})
        
        results = []
        for selector, value in fields.items():
            result = await self._call_mcp('input.fill', {
                'selector': selector,
                'value': value
            })
            results.append({
                'selector': selector,
                'filled': result.get('success', False)
            })
        
        return {
            'status': 'success',
            'filled_fields': results
        }
    
    async def _click(self, params: Dict) -> dict:
        """Click an element"""
        selector = params.get('selector')
        if not selector:
            return {'error': 'Selector required'}
        
        result = await self._call_mcp('input.click', {
            'selector': selector,
            'wait_for_navigation': params.get('wait_for_navigation', False)
        })
        
        return {
            'status': 'success',
            'clicked': result.get('success', False),
            'new_url': result.get('new_url')
        }
    
    async def _search_tabs(self, params: Dict) -> dict:
        """Search across browser tabs using AI"""
        query = params.get('query')
        if not query:
            return {'error': 'Query required'}
        
        result = await self._call_mcp('search.semantic', {
            'query': query,
            'max_results': params.get('max_results', 10),
            'include_content': params.get('include_content', True)
        })
        
        return {
            'status': 'success',
            'query': query,
            'results': result.get('results', []),
            'total_tabs': result.get('total_tabs', 0)
        }
    
    async def _monitor_network(self, params: Dict) -> dict:
        """Monitor network requests"""
        duration = params.get('duration', 5000)  # milliseconds
        filter_pattern = params.get('filter', '*')
        
        result = await self._call_mcp('network.monitor', {
            'duration': duration,
            'filter': filter_pattern,
            'include_headers': params.get('include_headers', False),
            'include_body': params.get('include_body', False)
        })
        
        return {
            'status': 'success',
            'requests': result.get('requests', []),
            'total_requests': len(result.get('requests', [])),
            'total_size': result.get('total_size', 0)
        }
    
    async def _execute_script(self, params: Dict) -> dict:
        """Execute JavaScript in the browser"""
        script = params.get('script')
        if not script:
            return {'error': 'Script required'}
        
        result = await self._call_mcp('page.evaluate', {
            'expression': script,
            'await_promise': params.get('await_promise', False)
        })
        
        return {
            'status': 'success',
            'result': result.get('value'),
            'type': result.get('type')
        }
    
    async def _get_cookies(self, params: Dict) -> dict:
        """Get browser cookies"""
        result = await self._call_mcp('storage.getCookies', {
            'url': params.get('url'),
            'name': params.get('name')
        })
        
        return {
            'status': 'success',
            'cookies': result.get('cookies', []),
            'count': len(result.get('cookies', []))
        }
    
    async def _wait_for_element(self, params: Dict) -> dict:
        """Wait for element to appear"""
        selector = params.get('selector')
        if not selector:
            return {'error': 'Selector required'}
        
        result = await self._call_mcp('page.waitForSelector', {
            'selector': selector,
            'timeout': params.get('timeout', 30000),
            'visible': params.get('visible', True)
        })
        
        return {
            'status': 'success',
            'found': result.get('found', False),
            'elapsed': result.get('elapsed_ms', 0)
        }
    
    async def research_topic(self, topic: str, depth: int = 3) -> dict:
        """Perform comprehensive web research on a topic"""
        research_results = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'sources': [],
            'key_findings': [],
            'summary': ''
        }
        
        # Search for the topic
        await self.execute_tool('navigate', {
            'url': f'https://www.google.com/search?q={topic}'
        })
        
        # Extract search results
        search_results = await self.execute_tool('extract_content', {
            'selector': 'h3',
            'include_text': True
        })
        
        # Visit top results
        for i in range(min(depth, 5)):
            # Click on result
            await self.execute_tool('click', {
                'selector': f'h3:nth-of-type({i+1})',
                'wait_for_navigation': True
            })
            
            # Extract content
            content = await self.execute_tool('extract_content', {
                'selector': 'main, article, .content',
                'include_text': True
            })
            
            # Take screenshot
            screenshot = await self.execute_tool('screenshot', {
                'full_page': False
            })
            
            research_results['sources'].append({
                'index': i,
                'content': content.get('content', ''),
                'screenshot': screenshot.get('data', '')[:100] + '...'  # Truncated
            })
            
            # Go back
            await self.execute_tool('execute_script', {
                'script': 'window.history.back()'
            })
        
        # Search tabs for additional context
        tab_search = await self.execute_tool('search_tabs', {
            'query': topic,
            'max_results': 10
        })
        
        research_results['tab_results'] = tab_search.get('results', [])
        research_results['summary'] = f"Researched {topic} across {depth} sources"
        
        return research_results


# Utility class for web automation workflows
class WebAutomationWorkflow:
    """High-level web automation workflows"""
    
    def __init__(self, chrome_integration: MCPChromeIntegration):
        self.chrome = chrome_integration
    
    async def login_to_service(self, service_url: str, username: str, password: str) -> dict:
        """Automated login workflow"""
        # Navigate to service
        await self.chrome.execute_tool('navigate', {'url': service_url})
        
        # Fill login form
        await self.chrome.execute_tool('fill_form', {
            'fields': {
                'input[type="email"], input[name="username"], #username': username,
                'input[type="password"], #password': password
            }
        })
        
        # Click login button
        await self.chrome.execute_tool('click', {
            'selector': 'button[type="submit"], .login-button, #login',
            'wait_for_navigation': True
        })
        
        # Check if logged in
        cookies = await self.chrome.execute_tool('get_cookies', {})
        
        return {
            'status': 'success',
            'logged_in': len(cookies.get('cookies', [])) > 0
        }
    
    async def scrape_data(self, url: str, selectors: dict[str, str]) -> dict:
        """Scrape structured data from a webpage"""
        # Navigate to page
        await self.chrome.execute_tool('navigate', {'url': url})
        
        # Wait for content
        await self.chrome.execute_tool('wait_for_element', {
            'selector': list(selectors.values())[0]
        })
        
        # Extract data
        scraped_data = {}
        for field, selector in selectors.items():
            result = await self.chrome.execute_tool('extract_content', {
                'selector': selector,
                'include_text': True
            })
            scraped_data[field] = result.get('content', '')
        
        return {
            'status': 'success',
            'url': url,
            'data': scraped_data,
            'timestamp': datetime.now().isoformat()
        }
    
    async def monitor_site_changes(self, url: str, check_interval: int = 60) -> dict:
        """Monitor a website for changes"""
        # Initial snapshot
        await self.chrome.execute_tool('navigate', {'url': url})
        
        initial_content = await self.chrome.execute_tool('extract_content', {
            'selector': 'body',
            'include_text': True
        })
        
        # Monitor network for dynamic content
        network_data = await self.chrome.execute_tool('monitor_network', {
            'duration': 5000,
            'filter': '*api*'
        })
        
        return {
            'status': 'monitoring',
            'url': url,
            'baseline_content': initial_content.get('content', '')[:500],
            'api_endpoints': [req['url'] for req in network_data.get('requests', [])]
        }


# Integration function for ULTIMATE AGI SYSTEM
async def create_mcp_chrome_integration(port: int = 3000) -> [MCPChromeIntegration]:
    """Create and initialize MCP Chrome integration"""
    integration = MCPChromeIntegration(port)
    
    if await integration.connect():
        logger.info("✅ MCP Chrome integration ready")
        return integration
    else:
        logger.warning("⚠️ MCP Chrome not available")
        return None


# Test the integration
async def test_mcp_chrome():
    """Test MCP Chrome integration"""
    print("Testing MCP Chrome Integration...")
    
    integration = await create_mcp_chrome_integration()
    
    if integration:
        # Test navigation
        result = await integration.execute_tool('navigate', {
            'url': 'https://example.com'
        })
        print(f"Navigation test: {result}")
        
        # Test content extraction
        result = await integration.execute_tool('extract_content', {
            'selector': 'h1'
        })
        print(f"Content extraction: {result}")
        
        # Test research workflow
        research = await integration.research_topic('AI agents', depth=2)
        print(f"Research results: {len(research['sources'])} sources found")
        
        await integration.disconnect()
    else:
        print("MCP Chrome not available for testing")
    
    print("\n✅ MCP Chrome Integration Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_mcp_chrome())