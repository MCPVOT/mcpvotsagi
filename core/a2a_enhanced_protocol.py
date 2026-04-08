#!/usr/bin/env python3
"""
Enhanced A2A (Agent-to-Agent) Communication System
Implements advanced A2A protocol with message queues, agent discovery, and fault tolerance
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
import redis.asyncio as redis
from aiohttp import web, WSMsgType
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """A2A Message types"""
    PING = "ping"
    PONG = "pong"
    REGISTER = "register"
    UNREGISTER = "unregister"
    DISCOVER = "discover"
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class AgentStatus(Enum):
    """Agent status states"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class AgentInfo:
    """Agent information structure"""
    agent_id: str
    name: str
    capabilities: List[str]
    endpoint: str
    status: AgentStatus
    metadata: Dict[str, Any]
    last_seen: datetime
    version: str = "1.0.0"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['last_seen'] = self.last_seen.isoformat()
        return data

@dataclass
class A2AMessage:
    """A2A Message structure"""
    message_id: str
    source_agent: str
    target_agent: Optional[str]
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    priority: int = 1
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'A2AMessage':
        """Create from dictionary"""
        return cls(
            message_id=data['message_id'],
            source_agent=data['source_agent'],
            target_agent=data.get('target_agent'),
            message_type=MessageType(data['message_type']),
            payload=data['payload'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            priority=data.get('priority', 1),
            correlation_id=data.get('correlation_id')
        )

class A2AMessageQueue:
    """Redis-based message queue for reliable A2A communication"""

    def __init__(self, redis_url: str = "redis://:os.environ.get('REDIS_PASSWORD', '')@localhost:6379/0"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.subscribers: Dict[str, Set[Callable]] = {}

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            await self.redis.ping()
            logger.info("✅ Connected to Redis message queue")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.aclose()
            logger.info("🔌 Disconnected from Redis")

    async def publish(self, channel: str, message: A2AMessage):
        """Publish message to channel"""
        if not self.redis:
            raise RuntimeError("Redis not connected")

        message_data = json.dumps(message.to_dict())
        await self.redis.publish(channel, message_data)

        # Also store in persistent queue for reliability
        queue_key = f"queue:{channel}"
        await self.redis.lpush(queue_key, message_data)

        logger.debug(f"📤 Published message {message.message_id} to {channel}")

    async def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe to agent-specific channel"""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = set()
        self.subscribers[agent_id].add(callback)

        # Start subscription task
        asyncio.create_task(self._subscription_handler(agent_id))
        logger.info(f"🔔 Subscribed agent {agent_id} to message queue")

    async def _subscription_handler(self, agent_id: str):
        """Handle subscription for agent"""
        if not self.redis:
            return

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"agent:{agent_id}")

        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    message_data = json.loads(message['data'])
                    a2a_message = A2AMessage.from_dict(message_data)

                    # Call all callbacks for this agent
                    for callback in self.subscribers.get(agent_id, set()):
                        try:
                            await callback(a2a_message)
                        except Exception as e:
                            logger.error(f"❌ Callback error for {agent_id}: {e}")

                except Exception as e:
                    logger.error(f"❌ Message processing error: {e}")

    async def get_queued_messages(self, agent_id: str, limit: int = 10) -> List[A2AMessage]:
        """Get queued messages for agent"""
        if not self.redis:
            return []

        queue_key = f"queue:agent:{agent_id}"
        messages = []

        for _ in range(limit):
            message_data = await self.redis.rpop(queue_key)
            if not message_data:
                break

            try:
                message_dict = json.loads(message_data)
                message = A2AMessage.from_dict(message_dict)

                # Check if message expired
                if message.expires_at and datetime.now() > message.expires_at:
                    continue

                messages.append(message)
            except Exception as e:
                logger.error(f"❌ Failed to parse queued message: {e}")

        return messages

class AgentRegistry:
    """Agent discovery and registry service"""

    def __init__(self, db_path: str = "agents_registry.db"):
        self.db_path = Path(db_path)
        self.agents: Dict[str, AgentInfo] = {}
        self.capabilities_index: Dict[str, Set[str]] = {}
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                version TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

        # Load agents from database
        self.load_agents_from_db()
        logger.info(f"📊 Agent registry initialized with {len(self.agents)} agents")

    def load_agents_from_db(self):
        """Load agents from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT * FROM agents')

        for row in cursor.fetchall():
            agent_info = AgentInfo(
                agent_id=row[0],
                name=row[1],
                capabilities=json.loads(row[2]),
                endpoint=row[3],
                status=AgentStatus(row[4]),
                metadata=json.loads(row[5]),
                last_seen=datetime.fromisoformat(row[6]),
                version=row[7]
            )
            self.agents[agent_info.agent_id] = agent_info

            # Update capabilities index
            for capability in agent_info.capabilities:
                if capability not in self.capabilities_index:
                    self.capabilities_index[capability] = set()
                self.capabilities_index[capability].add(agent_info.agent_id)

        conn.close()

    async def register_agent(self, agent_info: AgentInfo) -> bool:
        """Register or update agent"""
        try:
            # Update in-memory registry
            self.agents[agent_info.agent_id] = agent_info

            # Update capabilities index
            for capability in agent_info.capabilities:
                if capability not in self.capabilities_index:
                    self.capabilities_index[capability] = set()
                self.capabilities_index[capability].add(agent_info.agent_id)

            # Save to database
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT OR REPLACE INTO agents
                (agent_id, name, capabilities, endpoint, status, metadata, last_seen, version, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_info.agent_id,
                agent_info.name,
                json.dumps(agent_info.capabilities),
                agent_info.endpoint,
                agent_info.status.value,
                json.dumps(agent_info.metadata),
                agent_info.last_seen.isoformat(),
                agent_info.version,
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()

            logger.info(f"✅ Registered agent: {agent_info.name} ({agent_info.agent_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to register agent {agent_info.agent_id}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent"""
        try:
            if agent_id in self.agents:
                agent_info = self.agents[agent_id]

                # Remove from capabilities index
                for capability in agent_info.capabilities:
                    if capability in self.capabilities_index:
                        self.capabilities_index[capability].discard(agent_id)
                        if not self.capabilities_index[capability]:
                            del self.capabilities_index[capability]

                # Remove from memory
                del self.agents[agent_id]

                # Remove from database
                conn = sqlite3.connect(self.db_path)
                conn.execute('DELETE FROM agents WHERE agent_id = ?', (agent_id,))
                conn.commit()
                conn.close()

                logger.info(f"🗑️ Unregistered agent: {agent_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to unregister agent {agent_id}: {e}")
            return False

    def discover_agents(self, capability: Optional[str] = None) -> List[AgentInfo]:
        """Discover agents by capability"""
        if capability:
            agent_ids = self.capabilities_index.get(capability, set())
            return [self.agents[aid] for aid in agent_ids if aid in self.agents]
        else:
            return list(self.agents.values())

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_seen = datetime.now()

            # Update in database
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                'UPDATE agents SET status = ?, last_seen = ? WHERE agent_id = ?',
                (status.value, datetime.now().isoformat(), agent_id)
            )
            conn.commit()
            conn.close()

            return True
        return False

    async def cleanup_stale_agents(self, timeout_minutes: int = 10):
        """Remove agents that haven't been seen recently"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        stale_agents = []

        for agent_id, agent_info in self.agents.items():
            if agent_info.last_seen < cutoff_time:
                stale_agents.append(agent_id)

        for agent_id in stale_agents:
            await self.unregister_agent(agent_id)

        if stale_agents:
            logger.info(f"🧹 Cleaned up {len(stale_agents)} stale agents")

class A2AProtocolGateway:
    """Enhanced A2A protocol gateway with routing and fault tolerance"""

    def __init__(self, port: int = 8001):
        self.port = port
        self.message_queue = A2AMessageQueue()
        self.agent_registry = AgentRegistry()
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connections_active': 0,
            'errors': 0
        }

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default message handlers"""
        self.message_handlers[MessageType.PING] = self._handle_ping
        self.message_handlers[MessageType.REGISTER] = self._handle_register
        self.message_handlers[MessageType.UNREGISTER] = self._handle_unregister
        self.message_handlers[MessageType.DISCOVER] = self._handle_discover
        self.message_handlers[MessageType.REQUEST] = self._handle_request
        self.message_handlers[MessageType.HEARTBEAT] = self._handle_heartbeat

    async def start_server(self):
        """Start the A2A WebSocket server"""
        await self.message_queue.connect()

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

        # Start WebSocket server
        server = await websockets.serve(
            self._handle_connection,
            "localhost",
            self.port
        )

        logger.info(f"🚀 A2A Protocol Gateway started on ws://localhost:{self.port}")

        # Keep server running
        await server.wait_closed()

    async def _handle_connection(self, websocket, path):
        """Handle new WebSocket connections"""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        self.stats['connections_active'] += 1

        logger.info(f"🔌 New A2A connection: {connection_id}")

        try:
            async for message in websocket:
                await self._process_message(connection_id, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 A2A connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"❌ A2A connection error {connection_id}: {e}")
            self.stats['errors'] += 1
        finally:
            if connection_id in self.connections:
                del self.connections[connection_id]
            self.stats['connections_active'] -= 1

    async def _process_message(self, connection_id: str, raw_message: str):
        """Process incoming A2A message"""
        try:
            message_data = json.loads(raw_message)
            message = A2AMessage.from_dict(message_data)

            self.stats['messages_received'] += 1

            # Get handler for message type
            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(connection_id, message)
            else:
                await self._send_error(connection_id, f"Unknown message type: {message.message_type}")

        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
            await self._send_error(connection_id, f"Message processing error: {e}")
            self.stats['errors'] += 1

    async def _handle_ping(self, connection_id: str, message: A2AMessage):
        """Handle ping message"""
        pong_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=message.source_agent,
            message_type=MessageType.PONG,
            payload={"timestamp": datetime.now().isoformat()},
            timestamp=datetime.now(),
            correlation_id=message.message_id
        )
        await self._send_message(connection_id, pong_message)

    async def _handle_register(self, connection_id: str, message: A2AMessage):
        """Handle agent registration"""
        try:
            agent_data = message.payload
            agent_info = AgentInfo(
                agent_id=agent_data['agent_id'],
                name=agent_data['name'],
                capabilities=agent_data['capabilities'],
                endpoint=agent_data.get('endpoint', f"ws://{connection_id}"),
                status=AgentStatus(agent_data.get('status', 'online')),
                metadata=agent_data.get('metadata', {}),
                last_seen=datetime.now(),
                version=agent_data.get('version', '1.0.0')
            )

            success = await self.agent_registry.register_agent(agent_info)

            response = A2AMessage(
                message_id=str(uuid.uuid4()),
                source_agent="a2a_gateway",
                target_agent=message.source_agent,
                message_type=MessageType.RESPONSE,
                payload={
                    "success": success,
                    "agent_id": agent_info.agent_id,
                    "message": "Agent registered successfully" if success else "Registration failed"
                },
                timestamp=datetime.now(),
                correlation_id=message.message_id
            )

            await self._send_message(connection_id, response)

        except Exception as e:
            await self._send_error(connection_id, f"Registration error: {e}")

    async def _handle_discover(self, connection_id: str, message: A2AMessage):
        """Handle agent discovery"""
        capability = message.payload.get('capability')
        agents = self.agent_registry.discover_agents(capability)

        response = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=message.source_agent,
            message_type=MessageType.RESPONSE,
            payload={
                "agents": [agent.to_dict() for agent in agents],
                "count": len(agents),
                "capability": capability
            },
            timestamp=datetime.now(),
            correlation_id=message.message_id
        )

        await self._send_message(connection_id, response)

    async def _handle_request(self, connection_id: str, message: A2AMessage):
        """Handle agent request routing"""
        target_agent = message.target_agent

        if target_agent:
            # Route to specific agent
            await self.message_queue.publish(f"agent:{target_agent}", message)
        else:
            # Broadcast message
            await self._broadcast_message(message)

    async def _handle_heartbeat(self, connection_id: str, message: A2AMessage):
        """Handle agent heartbeat"""
        agent_id = message.source_agent
        await self.agent_registry.update_agent_status(agent_id, AgentStatus.ONLINE)

        # Send heartbeat acknowledgment
        response = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=agent_id,
            message_type=MessageType.RESPONSE,
            payload={"heartbeat_ack": True},
            timestamp=datetime.now(),
            correlation_id=message.message_id
        )

        await self._send_message(connection_id, response)

    async def _send_message(self, connection_id: str, message: A2AMessage):
        """Send message to specific connection"""
        if connection_id in self.connections:
            try:
                websocket = self.connections[connection_id]
                await websocket.send(json.dumps(message.to_dict()))
                self.stats['messages_sent'] += 1
            except Exception as e:
                logger.error(f"❌ Failed to send message to {connection_id}: {e}")

    async def _broadcast_message(self, message: A2AMessage):
        """Broadcast message to all connections"""
        message_json = json.dumps(message.to_dict())

        for connection_id, websocket in self.connections.items():
            try:
                await websocket.send(message_json)
                self.stats['messages_sent'] += 1
            except Exception as e:
                logger.error(f"❌ Broadcast failed to {connection_id}: {e}")

    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message"""
        error_msg = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=None,
            message_type=MessageType.ERROR,
            payload={"error": error_message},
            timestamp=datetime.now()
        )
        await self._send_message(connection_id, error_msg)

    async def _cleanup_task(self):
        """Periodic cleanup task"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                await self.agent_registry.cleanup_stale_agents()
            except Exception as e:
                logger.error(f"❌ Cleanup task error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        return {
            **self.stats,
            'registered_agents': len(self.agent_registry.agents),
            'capabilities': list(self.agent_registry.capabilities_index.keys()),
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }

# Example A2A Client
class A2AClient:
    """Example A2A client implementation"""

    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.message_handlers: Dict[MessageType, Callable] = {}

    async def connect(self, gateway_url: str = "ws://localhost:8001"):
        """Connect to A2A gateway"""
        self.websocket = await websockets.connect(gateway_url)

        # Register with gateway
        register_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent=self.agent_id,
            target_agent=None,
            message_type=MessageType.REGISTER,
            payload={
                'agent_id': self.agent_id,
                'name': self.name,
                'capabilities': self.capabilities,
                'status': 'online'
            },
            timestamp=datetime.now()
        )

        await self.websocket.send(json.dumps(register_message.to_dict()))

        # Start message handler
        asyncio.create_task(self._message_handler())
        logger.info(f"🔌 A2A client {self.name} connected and registered")

    async def _message_handler(self):
        """Handle incoming messages"""
        async for message in self.websocket:
            try:
                message_data = json.loads(message)
                a2a_message = A2AMessage.from_dict(message_data)

                # Route to appropriate handler
                handler = self.message_handlers.get(a2a_message.message_type)
                if handler:
                    await handler(a2a_message)

            except Exception as e:
                logger.error(f"❌ Client message handler error: {e}")

    async def send_message(self, target_agent: str, payload: Dict[str, Any],
                          message_type: MessageType = MessageType.REQUEST):
        """Send message to another agent"""
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent=self.agent_id,
            target_agent=target_agent,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now()
        )

        await self.websocket.send(json.dumps(message.to_dict()))

    async def discover_agents(self, capability: Optional[str] = None) -> List[AgentInfo]:
        """Discover agents with specific capability"""
        discover_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent=self.agent_id,
            target_agent=None,
            message_type=MessageType.DISCOVER,
            payload={'capability': capability} if capability else {},
            timestamp=datetime.now()
        )

        await self.websocket.send(json.dumps(discover_message.to_dict()))

        # Wait for response (simplified implementation)
        # In production, this would use proper correlation handling
        return []

async def main():
    """Start the A2A Protocol Gateway"""
    gateway = A2AProtocolGateway(port=8001)

    logger.info("🚀 Starting Enhanced A2A Communication System...")

    try:
        await gateway.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down A2A gateway...")
    except Exception as e:
        logger.error(f"❌ A2A gateway error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
