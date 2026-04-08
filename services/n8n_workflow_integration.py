#!/usr/bin/env python3
"""
n8n Workflow Integration Backend
================================
Integrates n8n automation workflows with the trading system
"""

import asyncio
import json
import logging
from typing import List, Optional
from datetime import datetime, timedelta
import aiohttp
from aiohttp import web
from dataclasses import dataclass
import yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("n8nIntegration")


@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration"""
    name: str
    type: str  # webhook, schedule, event
    conditions: dict[str, Any]
    workflow_id: str
    enabled: bool = True


class N8NIntegrationServer:
    """n8n integration server for trading workflows"""
    
    def __init__(self, config_path: str = "n8n_config.yaml"):
        self.config = self._load_config(config_path)
        self.n8n_url = self.config.get("n8n_url", "http://localhost:5678")
        self.webhook_url = self.config.get("webhook_url", "http://localhost:8020")
        
        # Workflow triggers
        self.triggers = self._init_triggers()
        
        # Event queue
        self.event_queue = asyncio.Queue()
        
        # Web app
        self.app = web.Application()
        self._setup_routes()
        
    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load n8n configuration"""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            "n8n_url": "http://localhost:5678",
            "webhook_url": "http://localhost:8020",
            "api_key": "",
            "workflows": {
                "trading_signal": "1",
                "risk_alert": "2",
                "portfolio_rebalance": "3",
                "market_analysis": "4",
                "daily_report": "5"
            }
        }
        
    def _init_triggers(self) -> list[WorkflowTrigger]:
        """Initialize workflow triggers"""
        return [
            WorkflowTrigger(
                name="High Confidence Trade",
                type="event",
                conditions={"confidence": {"gt": 0.8}},
                workflow_id=self.config["workflows"]["trading_signal"]
            ),
            WorkflowTrigger(
                name="Risk Alert",
                type="event",
                conditions={"risk_score": {"gt": 0.7}},
                workflow_id=self.config["workflows"]["risk_alert"]
            ),
            WorkflowTrigger(
                name="Portfolio Rebalance",
                type="schedule",
                conditions={"cron": "0 0 * * *"},  # Daily
                workflow_id=self.config["workflows"]["portfolio_rebalance"]
            ),
            WorkflowTrigger(
                name="Market Analysis",
                type="schedule",
                conditions={"cron": "0 */4 * * *"},  # Every 4 hours
                workflow_id=self.config["workflows"]["market_analysis"]
            ),
            WorkflowTrigger(
                name="Daily Report",
                type="schedule",
                conditions={"cron": "0 9 * * *"},  # 9 AM daily
                workflow_id=self.config["workflows"]["daily_report"]
            )
        ]
        
    def _setup_routes(self):
        """Setup web routes"""
        # Webhook endpoints
        self.app.router.add_post('/webhook/trading', self.handle_trading_webhook)
        self.app.router.add_post('/webhook/alert', self.handle_alert_webhook)
        self.app.router.add_post('/webhook/n8n', self.handle_n8n_webhook)
        
        # API endpoints
        self.app.router.add_get('/api/triggers', self.get_triggers)
        self.app.router.add_post('/api/trigger', self.manual_trigger)
        self.app.router.add_get('/api/workflows', self.get_workflows)
        self.app.router.add_get('/api/status', self.get_status)
        
    async def start(self, port: int = 8020):
        """Start the integration server"""
        # Start event processor
        asyncio.create_task(self._process_events())
        
        # Start scheduled workflows
        asyncio.create_task(self._schedule_processor())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        
        logger.info(f"n8n Integration Server running on http://localhost:{port}")
        
    async def trigger_workflow(self, 
                             workflow_id: str,
                             data: dict[str, Any],
                             webhook_suffix: str = "webhook") -> dict[str, Any]:
        """Trigger an n8n workflow"""
        
        url = f"{self.n8n_url}/webhook/{webhook_suffix}/{workflow_id}"
        
        headers = {}
        if self.config.get("api_key"):
            headers["X-N8N-API-KEY"] = self.config["api_key"]
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=data,
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        logger.info(f"Triggered workflow {workflow_id}")
                        return {"success": True, "result": result}
                    else:
                        error = await resp.text()
                        logger.error(f"Workflow trigger failed: {error}")
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Failed to trigger workflow: {e}")
            return {"success": False, "error": str(e)}
            
    async def process_trading_event(self, event: dict[str, Any]):
        """Process trading events and trigger appropriate workflows"""
        
        # Check all triggers
        for trigger in self.triggers:
            if trigger.type == "event" and trigger.enabled:
                if self._check_conditions(event, trigger.conditions):
                    # Trigger workflow
                    await self.trigger_workflow(
                        trigger.workflow_id,
                        {
                            "event": event,
                            "trigger": trigger.name,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
    def _check_conditions(self, data: dict[str, Any], conditions: dict[str, Any]) -> bool:
        """Check if data meets trigger conditions"""
        
        for field, condition in conditions.items():
            if field not in data:
                return False
                
            value = data[field]
            
            if isinstance(condition, dict):
                # Complex condition
                if "gt" in condition and value <= condition["gt"]:
                    return False
                if "lt" in condition and value >= condition["lt"]:
                    return False
                if "eq" in condition and value != condition["eq"]:
                    return False
                if "in" in condition and value not in condition["in"]:
                    return False
            else:
                # Simple equality
                if value != condition:
                    return False
                    
        return True
        
    async def _process_events(self):
        """Process event queue"""
        while True:
            try:
                event = await self.event_queue.get()
                await self.process_trading_event(event)
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                
    async def _schedule_processor(self):
        """Process scheduled workflows"""
        
        while True:
            current_time = datetime.now()
            
            for trigger in self.triggers:
                if trigger.type == "schedule" and trigger.enabled:
                    # Check if should run (simplified cron)
                    cron = trigger.conditions.get("cron", "")
                    
                    # Simple daily check
                    if "0 0 * * *" in cron and current_time.hour == 0 and current_time.minute == 0:
                        await self.trigger_workflow(
                            trigger.workflow_id,
                            {
                                "trigger": trigger.name,
                                "scheduled_time": current_time.isoformat()
                            }
                        )
                        
            # Sleep for 1 minute
            await asyncio.sleep(60)
            
    # Web handlers
    async def handle_trading_webhook(self, request):
        """Handle incoming trading webhooks"""
        try:
            data = await request.json()
            
            # Add to event queue
            await self.event_queue.put(data)
            
            return web.json_response({"status": "queued"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
            
    async def handle_alert_webhook(self, request):
        """Handle alert webhooks"""
        try:
            data = await request.json()
            
            # Trigger alert workflow immediately
            result = await self.trigger_workflow(
                self.config["workflows"]["risk_alert"],
                data
            )
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
            
    async def handle_n8n_webhook(self, request):
        """Handle callbacks from n8n workflows"""
        try:
            data = await request.json()
            
            logger.info(f"Received n8n callback: {data}")
            
            # Process based on workflow type
            workflow_id = data.get("workflow_id")
            
            if workflow_id == self.config["workflows"]["trading_signal"]:
                # Handle trading signal result
                logger.info("Processing trading signal result from n8n")
                
            return web.json_response({"status": "processed"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
            
    async def get_triggers(self, request):
        """Get all configured triggers"""
        triggers_data = [
            {
                "name": t.name,
                "type": t.type,
                "conditions": t.conditions,
                "workflow_id": t.workflow_id,
                "enabled": t.enabled
            }
            for t in self.triggers
        ]
        
        return web.json_response(triggers_data)
        
    async def manual_trigger(self, request):
        """Manually trigger a workflow"""
        try:
            data = await request.json()
            workflow_id = data.get("workflow_id")
            payload = data.get("payload", {})
            
            result = await self.trigger_workflow(workflow_id, payload)
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
            
    async def get_workflows(self, request):
        """Get configured workflows"""
        return web.json_response(self.config["workflows"])
        
    async def get_status(self, request):
        """Get integration status"""
        return web.json_response({
            "status": "online",
            "n8n_url": self.n8n_url,
            "triggers": len(self.triggers),
            "enabled_triggers": sum(1 for t in self.triggers if t.enabled),
            "queue_size": self.event_queue.qsize()
        })


class N8NWorkflowBuilder:
    """Helper to build n8n workflow configurations"""
    
    @staticmethod
    def create_trading_workflow() -> dict[str, Any]:
        """Create a trading signal workflow"""
        return {
            "name": "Trading Signal Processor",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "trading-signal"
                    }
                },
                {
                    "name": "Analyze Signal",
                    "type": "n8n-nodes-base.function",
                    "position": [450, 300],
                    "parameters": {
                        "functionCode": """
                        const signal = items[0].json;
                        
                        // Extract key information
                        const action = signal.action;
                        const confidence = signal.confidence;
                        const token = signal.token;
                        
                        // Add analysis
                        signal.analysis = {
                            risk_level: confidence < 0.6 ? 'high' : 'medium',
                            suggested_size: confidence * 0.1,
                            alert_required: confidence > 0.9
                        };
                        
                        return [{json: signal}];
                        """
                    }
                },
                {
                    "name": "Notify",
                    "type": "n8n-nodes-base.telegram",
                    "position": [650, 300],
                    "parameters": {
                        "text": "Trading Signal: {{$json.action}} {{$json.token}} ({{$json.confidence}}% confidence)",
                        "chatId": "{{$env.TELEGRAM_CHAT_ID}}"
                    }
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [[{"node": "Analyze Signal", "type": "main", "index": 0}]]
                },
                "Analyze Signal": {
                    "main": [[{"node": "Notify", "type": "main", "index": 0}]]
                }
            }
        }
        
    @staticmethod
    def create_risk_alert_workflow() -> dict[str, Any]:
        """Create a risk alert workflow"""
        return {
            "name": "Risk Alert Handler",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300]
                },
                {
                    "name": "Check Severity",
                    "type": "n8n-nodes-base.if",
                    "position": [450, 300],
                    "parameters": {
                        "conditions": {
                            "number": [
                                {
                                    "value1": "={{$json.risk_score}}",
                                    "operation": "larger",
                                    "value2": 0.8
                                }
                            ]
                        }
                    }
                },
                {
                    "name": "High Risk Alert",
                    "type": "n8n-nodes-base.emailSend",
                    "position": [650, 200],
                    "parameters": {
                        "subject": "⚠️ HIGH RISK ALERT",
                        "text": "High risk detected: {{$json.message}}"
                    }
                },
                {
                    "name": "Log Alert",
                    "type": "n8n-nodes-base.writeBinaryFile",
                    "position": [650, 400],
                    "parameters": {
                        "fileName": "risk_alerts.log",
                        "options": {"append": true}
                    }
                }
            ]
        }
        
    @staticmethod 
    def export_workflow(workflow: dict[str, Any], filename: str):
        """Export workflow to file"""
        with open(filename, 'w') as f:
            json.dump(workflow, f, indent=2)
            
        logger.info(f"Exported workflow to {filename}")


# Integration with main trading system
class TradingSystemN8NAdapter:
    """Adapter to connect trading system with n8n"""
    
    def __init__(self, n8n_server: N8NIntegrationServer):
        self.n8n = n8n_server
        
    async def on_trading_signal(self, signal: dict[str, Any]):
        """Handle trading signal from main system"""
        
        # Add to n8n event queue
        await self.n8n.event_queue.put({
            "type": "trading_signal",
            "signal": signal,
            "timestamp": datetime.now().isoformat()
        })
        
    async def on_risk_alert(self, alert: dict[str, Any]):
        """Handle risk alert"""
        
        # Trigger risk workflow immediately
        await self.n8n.trigger_workflow(
            self.n8n.config["workflows"]["risk_alert"],
            alert
        )
        
    async def on_portfolio_update(self, portfolio: dict[str, Any]):
        """Handle portfolio updates"""
        
        # Check if rebalancing needed
        if self._needs_rebalancing(portfolio):
            await self.n8n.trigger_workflow(
                self.n8n.config["workflows"]["portfolio_rebalance"],
                portfolio
            )
            
    def _needs_rebalancing(self, portfolio: dict[str, Any]) -> bool:
        """Check if portfolio needs rebalancing"""
        
        # Simple check - if any position > 20% of portfolio
        total_value = portfolio.get("total_value", 0)
        if total_value == 0:
            return False
            
        for position in portfolio.get("positions", []):
            if position["value"] / total_value > 0.2:
                return True
                
        return False


async def main():
    """Test n8n integration"""
    
    # Create n8n server
    server = N8NIntegrationServer()
    
    # Start server
    await server.start()
    
    # Test workflow trigger
    result = await server.trigger_workflow(
        "test",
        {"message": "Test from Python"}
    )
    
    logger.info(f"Test result: {result}")
    
    # Create sample workflows
    trading_workflow = N8NWorkflowBuilder.create_trading_workflow()
    N8NWorkflowBuilder.export_workflow(trading_workflow, "trading_workflow.json")
    
    risk_workflow = N8NWorkflowBuilder.create_risk_alert_workflow()
    N8NWorkflowBuilder.export_workflow(risk_workflow, "risk_workflow.json")
    
    logger.info("n8n integration ready")
    
    # Keep running
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())