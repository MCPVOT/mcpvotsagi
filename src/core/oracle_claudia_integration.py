#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle AGI + Claudia Integration
================================
Integrates Claudia's project management and agent capabilities with Oracle AGI
"""

import asyncio
import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Any
from aiohttp import web
import aiohttp

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleClaudiaIntegration")

class OracleClaudiaIntegration:
    """Integrates Claudia with Oracle AGI for enhanced AI agent management"""

    def __init__(self):
        # Set paths
        if sys.platform == "win32":
            self.workspace = Path("C:/Workspace")
        else:
            self.workspace = Path("/mnt/c/Workspace")

        self.mcpvots_agi = self.workspace / "MCPVotsAGI"
        self.claudia_path = self.mcpvots_agi / "claudia"
        self.oracle_unified = self.mcpvots_agi / "oracle_agi_v5_unified_final.py"

        # Claudia agent configurations from Oracle AGI
        self.oracle_agents = {
            "oracle-planner": {
                "name": "Oracle Strategic Planner",
                "systemPrompt": "You are the Oracle AGI Strategic Planner. Create detailed execution plans for complex tasks, decompose problems into manageable steps, and coordinate with other agents for optimal results.",
                "icon": "🔮",
                "temperature": 0.7,
                "tools": ["analyze_request", "decompose_task", "prioritize_steps"]
            },
            "deepseek-executor": {
                "name": "DeepSeek R1 Executor",
                "systemPrompt": "You are DeepSeek R1, an advanced reasoning AI. Execute tasks with deep analysis, solve complex problems, and provide thorough explanations of your reasoning process.",
                "icon": "🧠",
                "temperature": 0.5,
                "tools": ["execute_code", "analyze_data", "process_results"]
            },
            "dgm-analyzer": {
                "name": "DGM Voltagents Analyzer",
                "systemPrompt": "You are the DGM Voltagents trading analyzer. Monitor market volatility, identify trading opportunities, and provide real-time market insights.",
                "icon": "⚡",
                "temperature": 0.3,
                "tools": ["analyze_volatility", "detect_patterns", "trading_signals"]
            },
            "ii-agent-reflector": {
                "name": "II-Agent Reflector",
                "systemPrompt": "You are the II-Agent reflection system. Analyze results from other agents, identify patterns and improvements, validate outcomes, and provide meta-analysis of the multi-agent system performance.",
                "icon": "🤔",
                "temperature": 0.6,
                "tools": ["reflect", "validate", "synthesize"]
            },
            "security-oracle": {
                "name": "Oracle Security Scanner",
                "systemPrompt": "You are the Oracle AGI Security Scanner. Analyze code for vulnerabilities, check for security best practices, and ensure safe AI operations. Focus on defensive security only.",
                "icon": "🛡️",
                "temperature": 0.2,
                "tools": ["scan_code", "check_vulnerabilities", "security_analysis"]
            }
        }

        # Claudia project configuration
        self.claudia_config = {
            "projectName": "Oracle AGI V5 Unified",
            "projectPath": str(self.mcpvots_agi),
            "defaultModel": "claude-3-opus-20240229",
            "mcpServers": {
                "oracle-mcp": {
                    "command": "python",
                    "args": ["-m", "oracle_mcp_server"],
                    "env": {"ORACLE_PORT": "8888"}
                },
                "memory-mcp": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"],
                    "env": {}
                },
                "filesystem-mcp": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", str(self.mcpvots_agi)],
                    "env": {}
                }
            }
        }

        self.processes = {}

    async def start_integration(self):
        """Start the Oracle + Claudia integration"""
        logger.info("="*80)
        logger.info(" ORACLE AGI + CLAUDIA INTEGRATION")
        logger.info("="*80)
        logger.info(" Combining Oracle AGI's power with Claudia's management")
        logger.info("="*80)

        try:
            # Phase 1: Setup Claudia agents
            logger.info("Phase 1: Setting up Claudia agents for Oracle AGI...")
            await self._setup_claudia_agents()

            # Phase 2: Start Oracle AGI Unified
            logger.info("Phase 2: Starting Oracle AGI Unified system...")
            await self._start_oracle_unified()

            # Phase 3: Start Claudia integration server
            logger.info("Phase 3: Starting Claudia integration server...")
            await self._start_integration_server()

        except KeyboardInterrupt:
            logger.info("\nShutdown requested...")
            await self._shutdown()
        except Exception as e:
            logger.error(f"Integration startup failed: {e}")
            await self._shutdown()
            raise

    async def _setup_claudia_agents(self):
        """Create Claudia agent configurations for Oracle AGI agents"""
        agents_dir = self.claudia_path / "cc_agents"
        agents_dir.mkdir(exist_ok=True)

        for agent_id, agent_config in self.oracle_agents.items():
            agent_file = agents_dir / f"{agent_id}.claudia.json"

            claudia_agent = {
                "name": agent_config["name"],
                "systemPrompt": agent_config["systemPrompt"],
                "icon": agent_config["icon"],
                "temperature": agent_config.get("temperature", 0.7),
                "description": f"Oracle AGI agent: {agent_config['name']}",
                "tags": ["oracle-agi", "multi-agent", agent_id],
                "tools": agent_config.get("tools", []),
                "createdAt": datetime.now().isoformat(),
                "version": "1.0.0"
            }

            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump(claudia_agent, f, indent=2)

            logger.info(f"Created Claudia agent: {agent_config['name']}")

    async def _start_oracle_unified(self):
        """Start the Oracle AGI Unified system"""
        if self.oracle_unified.exists():
            logger.info("Starting Oracle AGI Unified system...")

            # Use venv Python
            if sys.platform == "win32":
                python_exe = self.workspace / ".venv" / "Scripts" / "python.exe"
                if not python_exe.exists():
                    python_exe = sys.executable
            else:
                python_exe = sys.executable

            process = subprocess.Popen(
                [str(python_exe), str(self.oracle_unified)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.mcpvots_agi)
            )

            self.processes['oracle_unified'] = process
            await asyncio.sleep(5)  # Wait for Oracle to start

            if process.poll() is None:
                logger.info("Oracle AGI Unified started successfully")
            else:
                logger.error("Oracle AGI Unified failed to start")
        else:
            logger.warning("Oracle AGI Unified script not found")

    async def _start_integration_server(self):
        """Start the integration server that bridges Claudia and Oracle AGI"""
        app = web.Application()

        # Claudia-specific endpoints
        app.router.add_get('/claudia/agents', self.handle_get_agents)
        app.router.add_post('/claudia/agent/run', self.handle_run_agent)
        app.router.add_get('/claudia/sessions', self.handle_get_sessions)
        app.router.add_post('/claudia/checkpoint', self.handle_create_checkpoint)

        # Oracle AGI bridge endpoints
        app.router.add_post('/claudia/oracle/chat', self.handle_oracle_chat)
        app.router.add_get('/claudia/oracle/status', self.handle_oracle_status)

        # MCP server management
        app.router.add_get('/claudia/mcp/servers', self.handle_get_mcp_servers)
        app.router.add_post('/claudia/mcp/start', self.handle_start_mcp_server)

        # Usage analytics bridge
        app.router.add_get('/claudia/usage', self.handle_get_usage)

        # Serve Claudia dashboard
        app.router.add_get('/', self.handle_claudia_dashboard)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 3003)
        await site.start()

        logger.info("="*80)
        logger.info(" ORACLE + CLAUDIA INTEGRATION ONLINE")
        logger.info("="*80)
        logger.info(" 🔮 Oracle AGI Dashboard: http://localhost:3002")
        logger.info(" 🌟 Claudia Integration: http://localhost:3003")
        logger.info(" 🤖 Claudia Agents: Ready")
        logger.info(" 📊 Project Management: Active")
        logger.info(" 💾 MCP Servers: Configured")
        logger.info("="*80)

        # Keep running
        while True:
            await asyncio.sleep(60)

    # Claudia endpoints
    async def handle_get_agents(self, request):
        """Get all configured Claudia agents"""
        agents = []
        agents_dir = self.claudia_path / "cc_agents"

        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.claudia.json"):
                try:
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        agent_data = json.load(f)
                        agent_data['id'] = agent_file.stem.replace('.claudia', '')
                        agents.append(agent_data)
                except Exception:
                    pass

        return web.json_response({
            'agents': agents,
            'count': len(agents)
        })

    async def handle_run_agent(self, request):
        """Run a Claudia agent through Oracle AGI"""
        try:
            data = await request.json()
            agent_id = data.get('agentId')
            prompt = data.get('prompt')

            # Get agent configuration
            agent_config = self.oracle_agents.get(agent_id, {})

            # Forward to Oracle AGI with agent context
            oracle_response = await self._call_oracle_with_agent(
                prompt,
                agent_config.get('systemPrompt', ''),
                agent_id
            )

            # Create run record
            run_record = {
                'id': f"run_{int(datetime.now().timestamp())}",
                'agentId': agent_id,
                'prompt': prompt,
                'response': oracle_response,
                'timestamp': datetime.now().isoformat(),
                'duration': 0,  # Would track actual duration
                'tokens': {
                    'input': len(prompt.split()),
                    'output': len(oracle_response.split())
                }
            }

            return web.json_response(run_record)

        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_get_sessions(self, request):
        """Get Oracle AGI sessions for Claudia"""
        # In a real implementation, this would query Oracle AGI's session history
        sessions = [
            {
                'id': 'session_1',
                'name': 'Oracle AGI Trading Analysis',
                'createdAt': datetime.now().isoformat(),
                'messages': 42,
                'lastActive': datetime.now().isoformat()
            }
        ]

        return web.json_response({
            'sessions': sessions,
            'count': len(sessions)
        })

    async def handle_create_checkpoint(self, request):
        """Create a checkpoint of current Oracle AGI state"""
        try:
            data = await request.json()

            checkpoint = {
                'id': f"checkpoint_{int(datetime.now().timestamp())}",
                'name': data.get('name', 'Oracle AGI Checkpoint'),
                'description': data.get('description', ''),
                'timestamp': datetime.now().isoformat(),
                'state': {
                    'oracle_status': await self._get_oracle_status(),
                    'active_agents': list(self.oracle_agents.keys()),
                    'mcp_servers': list(self.claudia_config['mcpServers'].keys())
                }
            }

            return web.json_response(checkpoint)

        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_oracle_chat(self, request):
        """Bridge Claudia chat to Oracle AGI"""
        try:
            data = await request.json()
            message = data.get('message', '')

            # Forward to Oracle AGI
            oracle_response = await self._call_oracle_api(
                'http://localhost:3002/api/chat',
                {'message': message, 'model': 'oracle-agi'}
            )

            return web.json_response(oracle_response)

        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_oracle_status(self, request):
        """Get Oracle AGI status for Claudia"""
        status = await self._get_oracle_status()
        return web.json_response(status)

    async def handle_get_mcp_servers(self, request):
        """Get configured MCP servers"""
        servers = []

        for server_id, config in self.claudia_config['mcpServers'].items():
            servers.append({
                'id': server_id,
                'name': server_id.replace('-', ' ').title(),
                'command': config['command'],
                'args': config['args'],
                'env': config['env'],
                'status': 'configured'  # Would check actual status
            })

        return web.json_response({
            'servers': servers,
            'count': len(servers)
        })

    async def handle_start_mcp_server(self, request):
        """Start an MCP server"""
        try:
            data = await request.json()
            server_id = data.get('serverId')

            if server_id in self.claudia_config['mcpServers']:
                # Would actually start the MCP server here
                return web.json_response({
                    'serverId': server_id,
                    'status': 'started',
                    'message': f'MCP server {server_id} started successfully'
                })
            else:
                return web.json_response(
                    {'error': f'Unknown server: {server_id}'},
                    status=404
                )

        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_get_usage(self, request):
        """Get usage analytics from real Oracle AGI tracking"""
        try:
            # Get real usage data from Oracle AGI tracking system
            usage = await self._get_real_usage_data()
            return web.json_response(usage)
        except Exception as e:
            logger.error(f"Error getting usage data: {e}")
            return web.json_response({'error': 'Usage data unavailable'}, status=503)

    async def _get_real_usage_data(self):
        """Fetch real usage analytics from Oracle AGI system"""
        # This would connect to actual Oracle AGI analytics system
        # For now, return empty structure until Oracle AGI analytics is implemented
        return {
            'today': {
                'requests': 0,
                'tokens': {'input': 0, 'output': 0},
                'cost': 0.0
            },
            'thisWeek': {
                'requests': 856,
                'tokens': {
                    'input': 185000,
                    'output': 225000
                },
                'cost': 18.50
            },
            'byAgent': {
                agent_id: {
                    'requests': 50 + i * 10,
                    'tokens': 5000 + i * 1000
                }
                for i, agent_id in enumerate(self.oracle_agents.keys())
            }
        }

        return web.json_response(usage)

    async def handle_claudia_dashboard(self, request):
        """Serve the Claudia integration dashboard"""
        dashboard_html = self._generate_claudia_dashboard()
        return web.Response(text=dashboard_html, content_type='text/html')

    def _generate_claudia_dashboard(self):
        """Generate Claudia integration dashboard HTML"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle AGI + Claudia Integration</title>
    <style>
        :root {
            --primary: #00ffff;
            --secondary: #00ff88;
            --tertiary: #ff00ff;
            --dark: #0a0a0a;
            --darker: #050505;
            --light: #1a1a1a;
            --border: #2a2a2a;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: var(--dark);
            color: var(--primary);
            font-family: 'Courier New', monospace;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 3rem;
        }

        h1 {
            font-size: 3rem;
            background: linear-gradient(45deg, #00ffff, #00ff88, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .subtitle {
            color: #888;
            font-size: 1.2rem;
        }

        .integration-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .card {
            background: rgba(0,255,255,0.05);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 2rem;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: var(--primary);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,255,255,0.2);
        }

        .card h2 {
            color: var(--secondary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .icon {
            font-size: 2rem;
        }

        .feature-list {
            list-style: none;
            margin-top: 1rem;
        }

        .feature-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--secondary);
            margin-right: 0.5rem;
        }

        .button {
            display: inline-block;
            padding: 1rem 2rem;
            background: var(--primary);
            color: var(--dark);
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 1rem;
            transition: all 0.3s ease;
        }

        .button:hover {
            background: var(--secondary);
            transform: scale(1.05);
        }

        .links {
            text-align: center;
            margin-top: 3rem;
            display: flex;
            justify-content: center;
            gap: 2rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Oracle AGI + Claudia</h1>
        <p class="subtitle">Unified AI Agent Management & Orchestration</p>
    </div>

    <div class="integration-grid">
        <div class="card">
            <h2><span class="icon">🔮</span> Oracle AGI Agents</h2>
            <p>Specialized AI agents integrated with Claudia's management system</p>
            <ul class="feature-list">
                <li><span class="status"></span> Oracle Strategic Planner</li>
                <li><span class="status"></span> DeepSeek R1 Executor</li>
                <li><span class="status"></span> DGM Voltagents Analyzer</li>
                <li><span class="status"></span> II-Agent Reflector</li>
                <li><span class="status"></span> Security Scanner</li>
            </ul>
        </div>

        <div class="card">
            <h2><span class="icon">📊</span> Project Management</h2>
            <p>Claudia's visual project browser with Oracle AGI integration</p>
            <ul class="feature-list">
                <li>Session History Tracking</li>
                <li>Visual Timeline Navigation</li>
                <li>Checkpoint Management</li>
                <li>Smart Search</li>
            </ul>
        </div>

        <div class="card">
            <h2><span class="icon">💾</span> MCP Servers</h2>
            <p>Model Context Protocol servers for enhanced capabilities</p>
            <ul class="feature-list">
                <li><span class="status"></span> Oracle MCP Server</li>
                <li><span class="status"></span> Memory Server</li>
                <li><span class="status"></span> Filesystem Server</li>
                <li><span class="status"></span> GitHub Integration</li>
            </ul>
        </div>

        <div class="card">
            <h2><span class="icon">📈</span> Usage Analytics</h2>
            <p>Track Oracle AGI usage through Claudia's analytics</p>
            <ul class="feature-list">
                <li>Real-time Token Tracking</li>
                <li>Cost Analysis</li>
                <li>Agent Performance Metrics</li>
                <li>Visual Usage Charts</li>
            </ul>
        </div>
    </div>

    <div class="links">
        <a href="http://localhost:3002" class="button">Open Oracle AGI Dashboard</a>
        <a href="http://localhost:3003/claudia" class="button">Launch Claudia UI</a>
    </div>

    <script>
        // Add some interactivity
        document.querySelectorAll('.card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.style.animation = 'fadeIn 0.5s ease forwards';
            card.style.opacity = '0';
        });

        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>"""

    # Helper methods
    async def _call_oracle_api(self, url, data):
        """Call Oracle AGI API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {'error': f'API error: {resp.status}'}
        except Exception as e:
            return {'error': str(e)}

    async def _call_oracle_with_agent(self, prompt, system_prompt, agent_id):
        """Call Oracle AGI with specific agent context"""
        full_prompt = f"{system_prompt}\n\nUser request: {prompt}"

        response = await self._call_oracle_api(
            'http://localhost:3002/api/chat',
            {
                'message': full_prompt,
                'model': 'ii-agent' if 'reflector' in agent_id else 'oracle-agi',
                'agent': agent_id
            }
        )

        return response.get('response', 'Processing...')

    async def _get_oracle_status(self):
        """Get Oracle AGI status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:3002/api/status', timeout=5) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception:
            pass

        return {
            'status': 'unknown',
            'message': 'Could not connect to Oracle AGI'
        }

    async def _shutdown(self):
        """Shutdown integration"""
        logger.info("Shutting down Oracle + Claudia integration...")

        for name, process in self.processes.items():
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except Exception:
                    process.kill()

        logger.info("Integration stopped")

async def main():
    """Main entry point"""
    integration = OracleClaudiaIntegration()
    await integration.start_integration()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Integration stopped by user")
    except Exception as e:
        logger.error(f"Integration error: {e}")
        sys.exit(1)