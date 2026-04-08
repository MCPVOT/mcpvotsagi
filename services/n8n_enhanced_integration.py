#!/usr/bin/env python3
"""
Enhanced n8n Workflow Integration for Oracle AGI
==============================================
Seamless workflow automation with AI-powered decision making
"""

import asyncio
import json
import logging
import aiohttp
from pathlib import Path
from typing import Optional
import websockets
from datetime import datetime
import yaml

logger = logging.getLogger("n8n_integration")

class N8NEnhancedIntegration:
    """Enhanced n8n integration with Oracle AGI"""
    
    def __init__(self, oracle_agi):
        self.oracle = oracle_agi
        self.n8n_url = "http://localhost:5678"
        self.workflows = {}
        self.active_executions = {}
        self.workflow_templates = self._load_workflow_templates()
        
    def _load_workflow_templates(self) -> dict:
        """Load workflow templates"""
        templates_path = Path("/mnt/c/Workspace/MCPVotsAGI/n8n-workflows/workflows")
        templates = {}
        
        if templates_path.exists():
            for template_file in templates_path.glob("*.json"):
                try:
                    with open(template_file, 'r') as f:
                        workflow = json.load(f)
                        templates[workflow.get('name', template_file.stem)] = workflow
                except Exception as e:
                    logger.error(f"Failed to load template {template_file}: {e}")
        
        return templates
    
    async def initialize(self):
        """Initialize n8n integration"""
        logger.info("Initializing n8n integration...")
        
        # Check n8n availability
        if await self._check_n8n_health():
            logger.info("n8n is available")
            
            # Load existing workflows
            await self._sync_workflows()
            
            # Create AI-powered workflows
            await self._create_ai_workflows()
            
            # Start workflow monitor
            asyncio.create_task(self._workflow_monitor())
        else:
            logger.warning("n8n is not available, workflows disabled")
    
    async def _check_n8n_health(self) -> bool:
        """Check if n8n is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.n8n_url}/healthz", timeout=5) as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def _sync_workflows(self):
        """Sync workflows from n8n"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.n8n_url}/api/v1/workflows") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for workflow in data.get('data', []):
                            self.workflows[workflow['id']] = workflow
                        logger.info(f"Synced {len(self.workflows)} workflows from n8n")
        except Exception as e:
            logger.error(f"Failed to sync workflows: {e}")
    
    async def _create_ai_workflows(self):
        """Create AI-powered workflows"""
        ai_workflows = [
            {
                'name': 'AI Context Preservation',
                'description': 'Automatically preserve Oracle AGI context',
                'nodes': [
                    {
                        'name': 'Schedule',
                        'type': 'n8n-nodes-base.cron',
                        'parameters': {
                            'cronExpression': '*/5 * * * *'  # Every 5 minutes
                        }
                    },
                    {
                        'name': 'Get Oracle Context',
                        'type': 'n8n-nodes-base.httpRequest',
                        'parameters': {
                            'url': 'http://localhost:8888/api/context',
                            'method': 'GET'
                        }
                    },
                    {
                        'name': 'Store Context',
                        'type': 'n8n-nodes-base.mongoDb',
                        'parameters': {
                            'operation': 'insert',
                            'collection': 'oracle_context'
                        }
                    }
                ]
            },
            {
                'name': 'AI Model Health Monitor',
                'description': 'Monitor and alert on AI model health',
                'nodes': [
                    {
                        'name': 'Health Check',
                        'type': 'n8n-nodes-base.httpRequest',
                        'parameters': {
                            'url': 'http://localhost:8888/api/status',
                            'method': 'GET'
                        }
                    },
                    {
                        'name': 'Check Threshold',
                        'type': 'n8n-nodes-base.if',
                        'parameters': {
                            'conditions': {
                                'cpu': {'value': 80, 'operation': 'larger'},
                                'memory': {'value': 85, 'operation': 'larger'}
                            }
                        }
                    },
                    {
                        'name': 'Send Alert',
                        'type': 'n8n-nodes-base.slack',
                        'parameters': {
                            'channel': '#oracle-alerts',
                            'text': 'Oracle AGI resource alert!'
                        }
                    }
                ]
            },
            {
                'name': 'Knowledge Graph Backup',
                'description': 'Backup knowledge graph to multiple locations',
                'nodes': [
                    {
                        'name': 'Export KG',
                        'type': 'n8n-nodes-base.httpRequest',
                        'parameters': {
                            'url': 'http://localhost:8888/api/knowledge/export',
                            'method': 'GET'
                        }
                    },
                    {
                        'name': 'Store IPFS',
                        'type': 'n8n-nodes-base.httpRequest',
                        'parameters': {
                            'url': 'http://localhost:5001/api/v0/add',
                            'method': 'POST'
                        }
                    },
                    {
                        'name': 'Store S3',
                        'type': 'n8n-nodes-base.awsS3',
                        'parameters': {
                            'operation': 'upload',
                            'bucketName': 'oracle-backups'
                        }
                    }
                ]
            },
            {
                'name': 'Trading Signal Processor',
                'description': 'Process trading signals with AI validation',
                'trigger': 'webhook',
                'nodes': [
                    {
                        'name': 'Receive Signal',
                        'type': 'n8n-nodes-base.webhook',
                        'parameters': {
                            'path': 'trading-signal'
                        }
                    },
                    {
                        'name': 'AI Validation',
                        'type': 'n8n-nodes-base.httpRequest',
                        'parameters': {
                            'url': 'http://localhost:8888/api/validate-trade',
                            'method': 'POST',
                            'body': '={{$json}}'
                        }
                    },
                    {
                        'name': 'Risk Check',
                        'type': 'n8n-nodes-base.if',
                        'parameters': {
                            'conditions': {
                                'risk_score': {'value': 0.7, 'operation': 'smaller'},
                                'confidence': {'value': 0.8, 'operation': 'larger'}
                            }
                        }
                    },
                    {
                        'name': 'Execute Trade',
                        'type': 'n8n-nodes-base.httpRequest',
                        'parameters': {
                            'url': 'http://localhost:3005/api/execute-trade',
                            'method': 'POST'
                        }
                    }
                ]
            },
            {
                'name': 'GitHub Issue AI Responder',
                'description': 'Automatically respond to GitHub issues with AI',
                'nodes': [
                    {
                        'name': 'GitHub Webhook',
                        'type': 'n8n-nodes-base.githubTrigger',
                        'parameters': {
                            'events': ['issues.opened', 'issues.commented']
                        }
                    },
                    {
                        'name': 'AI Analysis',
                        'type': 'n8n-nodes-base.httpRequest',
                        'parameters': {
                            'url': 'http://localhost:8888/api/analyze-issue',
                            'method': 'POST',
                            'body': '={{$json}}'
                        }
                    },
                    {
                        'name': 'Post Response',
                        'type': 'n8n-nodes-base.github',
                        'parameters': {
                            'resource': 'issue',
                            'operation': 'createComment'
                        }
                    }
                ]
            }
        ]
        
        # Create workflows in n8n
        for workflow_def in ai_workflows:
            await self._create_workflow(workflow_def)
    
    async def _create_workflow(self, workflow_def: Dict):
        """Create a workflow in n8n"""
        try:
            # Check if workflow already exists
            existing = next(
                (w for w in self.workflows.values() if w['name'] == workflow_def['name']),
                None
            )
            
            if existing:
                logger.info(f"Workflow '{workflow_def['name']}' already exists")
                return
            
            # Create workflow
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.n8n_url}/api/v1/workflows",
                    json=workflow_def
                ) as resp:
                    if resp.status in [200, 201]:
                        data = await resp.json()
                        self.workflows[data['id']] = data
                        logger.info(f"Created workflow: {workflow_def['name']}")
                    else:
                        logger.error(f"Failed to create workflow: {resp.status}")
                        
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
    
    async def _workflow_monitor(self):
        """Monitor workflow executions"""
        while True:
            try:
                # Get active executions
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.n8n_url}/api/v1/executions",
                        params={'status': 'running'}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            for execution in data.get('data', []):
                                exec_id = execution['id']
                                
                                if exec_id not in self.active_executions:
                                    self.active_executions[exec_id] = execution
                                    
                                    # Notify Oracle AGI
                                    await self.oracle.event_stream.put({
                                        'type': 'workflow_started',
                                        'workflow': execution['workflowData']['name'],
                                        'execution_id': exec_id
                                    })
                
                # Check completed executions
                completed = []
                for exec_id, execution in self.active_executions.items():
                    status = await self._check_execution_status(exec_id)
                    
                    if status in ['success', 'error']:
                        completed.append(exec_id)
                        
                        # Notify Oracle AGI
                        await self.oracle.event_stream.put({
                            'type': 'workflow_completed',
                            'workflow': execution['workflowData']['name'],
                            'execution_id': exec_id,
                            'status': status
                        })
                
                # Remove completed
                for exec_id in completed:
                    del self.active_executions[exec_id]
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Workflow monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _check_execution_status(self, execution_id: str) -> str:
        """Check execution status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.n8n_url}/api/v1/executions/{execution_id}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('status', 'unknown')
        except Exception:
            pass
        
        return 'unknown'
    
    async def trigger_workflow(self, workflow_name: str, data: Dict) -> [str]:
        """Trigger a workflow by name"""
        workflow = next(
            (w for w in self.workflows.values() if w['name'] == workflow_name),
            None
        )
        
        if not workflow:
            logger.error(f"Workflow '{workflow_name}' not found")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                # Trigger via webhook if available
                webhook_node = next(
                    (n for n in workflow.get('nodes', []) if n['type'] == 'n8n-nodes-base.webhook'),
                    None
                )
                
                if webhook_node:
                    webhook_path = webhook_node['parameters'].get('path', workflow_name)
                    url = f"{self.n8n_url}/webhook/{webhook_path}"
                else:
                    # Use execution API
                    url = f"{self.n8n_url}/api/v1/workflows/{workflow['id']}/execute"
                
                async with session.post(url, json=data) as resp:
                    if resp.status in [200, 201]:
                        result = await resp.json()
                        execution_id = result.get('executionId')
                        logger.info(f"Triggered workflow '{workflow_name}': {execution_id}")
                        return execution_id
                    else:
                        logger.error(f"Failed to trigger workflow: {resp.status}")
                        
        except Exception as e:
            logger.error(f"Error triggering workflow: {e}")
        
        return None
    
    async def create_dynamic_workflow(self, name: str, description: str, nodes: list[Dict]) -> bool:
        """Create a dynamic workflow based on AI recommendations"""
        workflow = {
            'name': f"AI_Generated_{name}",
            'description': description,
            'nodes': nodes,
            'connections': self._generate_connections(nodes),
            'active': True,
            'settings': {
                'executionOrder': 'v1'
            }
        }
        
        await self._create_workflow(workflow)
        return True
    
    def _generate_connections(self, nodes: list[Dict]) -> dict:
        """Generate connections between nodes"""
        connections = {}
        
        for i in range(len(nodes) - 1):
            current = nodes[i]['name']
            next_node = nodes[i + 1]['name']
            
            connections[current] = {
                'main': [[{'node': next_node, 'type': 'main', 'index': 0}]]
            }
        
        return connections
    
    async def analyze_workflow_performance(self) -> dict:
        """Analyze workflow performance metrics"""
        metrics = {
            'total_workflows': len(self.workflows),
            'active_executions': len(self.active_executions),
            'workflow_stats': {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get execution statistics
                async with session.get(
                    f"{self.n8n_url}/api/v1/executions",
                    params={'limit': 100}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Analyze by workflow
                        for execution in data.get('data', []):
                            workflow_name = execution['workflowData']['name']
                            
                            if workflow_name not in metrics['workflow_stats']:
                                metrics['workflow_stats'][workflow_name] = {
                                    'total_executions': 0,
                                    'successful': 0,
                                    'failed': 0,
                                    'average_duration': 0
                                }
                            
                            stats = metrics['workflow_stats'][workflow_name]
                            stats['total_executions'] += 1
                            
                            if execution['status'] == 'success':
                                stats['successful'] += 1
                            elif execution['status'] == 'error':
                                stats['failed'] += 1
                            
                            # Calculate duration
                            if execution.get('startedAt') and execution.get('stoppedAt'):
                                start = datetime.fromisoformat(execution['startedAt'])
                                stop = datetime.fromisoformat(execution['stoppedAt'])
                                duration = (stop - start).total_seconds()
                                
                                # Update average
                                current_avg = stats['average_duration']
                                total = stats['total_executions']
                                stats['average_duration'] = (
                                    (current_avg * (total - 1) + duration) / total
                                )
        
        except Exception as e:
            logger.error(f"Error analyzing workflow performance: {e}")
        
        return metrics
    
    async def optimize_workflows(self):
        """Optimize workflows based on performance data"""
        metrics = await self.analyze_workflow_performance()
        
        for workflow_name, stats in metrics['workflow_stats'].items():
            # Check failure rate
            if stats['total_executions'] > 10:
                failure_rate = stats['failed'] / stats['total_executions']
                
                if failure_rate > 0.3:  # More than 30% failure
                    logger.warning(f"High failure rate for workflow '{workflow_name}': {failure_rate:.2%}")
                    
                    # Create optimized version
                    await self._create_optimized_workflow(workflow_name, stats)
            
            # Check performance
            if stats['average_duration'] > 300:  # More than 5 minutes
                logger.warning(f"Slow workflow '{workflow_name}': {stats['average_duration']:.1f}s")
    
    async def _create_optimized_workflow(self, workflow_name: str, stats: Dict):
        """Create an optimized version of a workflow"""
        original = next(
            (w for w in self.workflows.values() if w['name'] == workflow_name),
            None
        )
        
        if not original:
            return
        
        # Create optimized version
        optimized = {
            'name': f"{workflow_name}_Optimized",
            'description': f"AI-optimized version of {workflow_name}",
            'nodes': original['nodes'].copy(),
            'connections': original['connections'].copy(),
            'settings': {
                'executionOrder': 'v1',
                'saveDataSuccessExecution': 'all',
                'saveExecutionProgress': True,
                'executionTimeout': 300  # 5 minute timeout
            }
        }
        
        # Add error handling nodes
        error_handler = {
            'name': 'Error Handler',
            'type': 'n8n-nodes-base.errorTrigger',
            'position': [1000, 500]
        }
        
        notification = {
            'name': 'Error Notification',
            'type': 'n8n-nodes-base.httpRequest',
            'parameters': {
                'url': 'http://localhost:8888/api/workflow-error',
                'method': 'POST',
                'body': '={{$json}}'
            },
            'position': [1200, 500]
        }
        
        optimized['nodes'].extend([error_handler, notification])
        
        # Connect error handler
        optimized['connections']['Error Handler'] = {
            'main': [[{'node': 'Error Notification', 'type': 'main', 'index': 0}]]
        }
        
        await self._create_workflow(optimized)