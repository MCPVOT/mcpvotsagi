```python
import asyncio
from datetime import datetime
import logging
from aiohttp.web import web
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SystemInfo:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_speed: float

class DataCollector:
    async def get_system_info(self):
        """Return system metrics for the dashboard"""
        # Implement actual data collection logic here
        return SystemInfo(cpu_usage=50.0, memory_usage=30.0, disk_usage=20.0, network_speed=100.0)

class ClaudiaAI:
    async def analyze_market_data(self):
        return {"analysis": "Deep analysis pending implementation"}

class UnifiedAGIDashboard:
    class ServiceStatus(Enum):
        ONLINE = 1
        OFFLINE = 2

    def __init__(self, port: int=8900):
        self.port = port
        self.app = web.Application()
        
        # Dependency injection and service container
        self.data_collector = DataCollector()
        self.claudia_ai = ClaudiaAI()
        self.websockets = []
        self.running = True

    async def handle_request(self, request: web.Request):
        """Handle incoming HTTP requests"""
        data_type = request.match_info.get('type', None)
        
        if data_type is not None:
            try:
                # Collect data based on the requested type
                update_data = await getattr(self.data_collector, f"get_{data_type}")(self.data_collector)

                # Send targeted update to the client
                return web.json_response(update_data)
                
            except Exception as e:
                logger.error(f"Error handling {data_type}: {e}")
                return web.Response(status=500, text="Internal Server Error")
        
        else:
            return web.Response(status=404, text="Not Found")

    async def send_update(self, websocket: web.WebSocketResponse, data_type):
        """Send targeted update to a specific websocket"""
        try:
            await websocket.send_str(json.dumps(data_type))
        except Exception as e:
            logger.error(f"Error sending update to WebSocket: {e}")

    async def broadcast_updates(self):
        while self.running:
            try:
                # Collect all current data from the services
                system_info = await self.data_collector.get_system_info()

                # Get AI analysis if we have market data available
                ai_analysis = await self.claudia_ai.analyze_market_data()

                # Combine into update object with appropriate structure
                updates = {
                    'system': asdict(system_info),
                    'ai_analysis': ai_analysis,
                    'timestamp': datetime.now().isoformat()
                }

                # Send updates to all connected websockets
                for ws in self.websockets:
                    await self.send_update(ws, updates)

            except Exception as e:
                logger.error(f"Error sending update: {e}")
                continue

    async def handle_websocket(self, request):
        """Handle incoming WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Add to the list of connected clients
        self.websockets.append(ws)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    response_text = f"Echo: {msg.data}"
                    await ws.send_str(response_text)
                    
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
        
        finally:
            # Remove from the list of connected clients
            self.websockets.remove(ws)
            
        return ws

    async def on_shutdown(self):
        """Cleanup before shutting down"""
        self.running = False
        for ws in self.websockets:
            await ws.close()

# Create the dashboard app
app = web.Application()
dashboard = UnifiedAGIDashboard(port=8080)

# Add routes and middleware
app.router.add_get('/data/{type}', dashboard.handle_request)
app.router.add_route('GET', '/ws', dashboard.handle_websocket)
app.on_shutdown.append(dashboard.on_shutdown)

# Run the server
web.run_app(app, port=dashboard.port)
```

This code provides a more structured and modular version of the unified AGI dashboard with improved architecture and functionality. It includes:

1. Dependency injection for services
2. Proper error handling in HTTP requests and WebSocket connections
3. Real-time update broadcasting mechanism
4. Configuration management (port number is configurable)
5. Basic logging

This code can be further extended with additional features as per the requirements.